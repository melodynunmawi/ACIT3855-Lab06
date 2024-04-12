import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
import datetime
from stats import Stats  # Ensure this is updated to handle new event types
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine, desc  # Added 'desc' here
from sqlalchemy.orm import sessionmaker
from pytz import utc

# Load configuration
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

# Set up database connection
DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def fetch_new_events(url, last_updated):
    """Fetch new thermostat and lighting events."""
    response = requests.get(url, params={"end_timestamp": last_updated})
    if response.status_code == 200:
        return response.json()
    else:
        logger.error("Failed to fetch events")
        return []

def populate_stats():
    logger.info("Periodic processing has started.")
    
    session = DB_SESSION()
    
    latest_stats = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    last_updated_time = datetime.datetime(2000, 1, 1) if latest_stats is None else latest_stats.last_updated
    last_updated_time_str = last_updated_time.strftime("%Y-%m-%d %H:%M:%S.%f")

    thermostat_url = f"{app_config['eventstore']['url']}/thermostat-events?start_timestamp={last_updated_time_str}"
    lighting_url = f"{app_config['eventstore']['url']}/lighting-events?start_timestamp={last_updated_time_str}"

    thermostat_events = fetch_new_events(thermostat_url, last_updated_time_str)
    lighting_events = fetch_new_events(lighting_url, last_updated_time_str)

    if thermostat_events:
        number_of_thermostat_events = len(thermostat_events)
        average_temperature = sum(event['temperature'] for event in thermostat_events) / number_of_thermostat_events
    else:
        number_of_thermostat_events = 0
        average_temperature = 0

    if lighting_events:
        number_of_lighting_events = len(lighting_events)
        average_light_intensity = sum(event['intensity'] for event in lighting_events) / number_of_lighting_events
    else:
        number_of_lighting_events = 0
        average_light_intensity = 0

    new_stats = Stats(
        number_of_thermostat_events=number_of_thermostat_events,
        number_of_lighting_events=number_of_lighting_events,
        average_temperature=average_temperature,
        average_light_intensity=average_light_intensity,
        #last_updated=datetime.datetime.now()
    )

    session.add(new_stats)
    session.commit()

    logger.info("Periodic processing has ended.")
    session.close()



def get_stats():
    logger.info("Request for statistics started.")

    session = DB_SESSION()
    latest_stats = session.query(Stats).order_by(desc(Stats.last_updated)).first()
    
    if latest_stats:
        stats_dict = latest_stats.to_dict()
        logger.info("Statistics fetched successfully.")
        session.close()
        return stats_dict, 200
    else:
        logger.error("No statistics found.")
        session.close()
        return NoContent, 404



def init_scheduler():
    sched = BackgroundScheduler(daemon=True, timezone=utc)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


if __name__ == "__main__":
    init_scheduler()
    app = connexion.FlaskApp(__name__, specification_dir="")
    app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)  # Ensure the API spec is correctly named
    app.run(port=8100)

