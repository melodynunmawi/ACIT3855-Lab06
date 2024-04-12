from connexion import NoContent, FlaskApp
import requests
import yaml
import logging
import logging.config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from datetime import datetime, timezone
from stats import Stats
from apscheduler.schedulers.background import BackgroundScheduler
from dateutil import parser
from urllib.parse import unquote
from pytz import utc

# Load configuration
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

# Correct the connection string for SQLite
connection_string = f"sqlite:///{app_config['database']['connection_string']}"
DB_ENGINE = create_engine(connection_string)
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def get_stats():
    """Retrieve the latest aggregated statistics for thermostat and lighting events."""
    session = DB_SESSION()
    latest_stats = session.query(Stats).order_by(Stats.last_updated.desc()).first()

    if latest_stats is not None:
        # Convert the SQLAlchemy model instance to a dictionary
        stats_response = {
            'number_of_thermostat_events': latest_stats.number_of_thermostat_events,
            'number_of_lighting_events': latest_stats.number_of_lighting_events,
            'average_temperature': latest_stats.average_temperature,
            'average_light_intensity': latest_stats.average_light_intensity,
            'last_updated': latest_stats.last_updated.strftime("%Y-%m-%d %H:%M:%S")  # Format datetime as string
        }
        return stats_response, 200
    else:
        # No statistics found, you can decide to return an empty object or a 404 error
        return NoContent, 404

def fetch_new_events(url, start_timestamp, end_timestamp):
    """Fetch new thermostat and lighting events."""
    full_url = f"{url}?start_timestamp={start_timestamp}&end_timestamp={end_timestamp}"
    logger.info(f"Fetching events from URL: {full_url}")
    try:
        response = requests.get(full_url)
        response.raise_for_status()
        events = response.json()
        logger.info(f"Fetched {len(events)} events: {events}")
        return events
    except requests.HTTPError as e:
        logger.error(f"HTTP error occurred while fetching events: {e.response.status_code} - {e.response.reason}")
    except requests.RequestException as e:
        logger.error(f"Request exception while fetching events: {e}")
    except ValueError as e:
        logger.error(f"Value error decoding JSON response: {e}")
    return []

def populate_stats():
    """Function to fetch new events and populate statistics."""
    logger.info("Periodic processing has started.")
    session = DB_SESSION()

    try:
        latest_stats = session.query(Stats).order_by(Stats.last_updated.desc()).first()
        last_updated_time = latest_stats.last_updated if latest_stats else datetime(2000, 1, 1, tzinfo=timezone.utc)
        current_time = datetime.now(timezone.utc)

        last_updated_time_str = last_updated_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        current_time_str = current_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        thermostat_url = app_config['eventstore']['url'] + '/thermostat-events'
        lighting_url = app_config['eventstore']['url'] + '/lighting-events'
        thermostat_events = fetch_new_events(thermostat_url, last_updated_time_str, current_time_str)
        lighting_events = fetch_new_events(lighting_url, last_updated_time_str, current_time_str)

        if thermostat_events:
            new_average_temperature = sum(event['temperature'] for event in thermostat_events) / len(thermostat_events)
        else:
            new_average_temperature = 0
        if lighting_events:
            new_average_light_intensity = sum(event['intensity'] for event in lighting_events) / len(lighting_events)
        else:
            new_average_light_intensity = 0
        new_number_of_thermostat_events = len(thermostat_events)
        new_number_of_lighting_events = len(lighting_events)

        if latest_stats:
            latest_stats.average_temperature = (latest_stats.average_temperature * latest_stats.number_of_thermostat_events + new_average_temperature * new_number_of_thermostat_events) / (latest_stats.number_of_thermostat_events + new_number_of_thermostat_events)
            latest_stats.average_light_intensity = (latest_stats.average_light_intensity * latest_stats.number_of_lighting_events + new_average_light_intensity * new_number_of_lighting_events) / (latest_stats.number_of_lighting_events + new_number_of_lighting_events)
            latest_stats.number_of_thermostat_events += new_number_of_thermostat_events
            latest_stats.number_of_lighting_events += new_number_of_lighting_events
            latest_stats.last_updated = current_time
        else:
            new_stats = Stats(
                number_of_thermostat_events=new_number_of_thermostat_events,
                number_of_lighting_events=new_number_of_lighting_events,
                average_temperature=new_average_temperature,  
                average_light_intensity=new_average_light_intensity,  
                last_updated=current_time
            )
            session.add(new_stats)

        session.commit()
    except Exception as e:
        logger.error(f"An error occurred during stats population: {e}")
        session.rollback()
    finally:
        session.close()
        logger.info("Periodic processing has finished.")

def init_scheduler():
    """Initialize the scheduler."""
    sched = BackgroundScheduler(daemon=True, timezone=utc)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

if __name__ == "__main__":
    init_scheduler()
    app = FlaskApp(__name__, specification_dir='')
    app.add_api('openapi.yaml', strict_validation=True, validate_responses=True)
    app.run(port=8100)
