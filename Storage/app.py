from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import yaml
import logging.config
import json
import connexion
from base import Base  # Your SQLAlchemy base
from event_models import ThermostatEvent, LightingEvent  # Your event models
from datetime import datetime

# Load application configuration
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# Load logging configuration
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')

# Setup Database connection
engine = create_engine(f"mysql+pymysql://{app_config['db']['user']}:{app_config['db']['password']}@{app_config['db']['hostname']}:{app_config['db']['port']}/{app_config['db']['db']}")
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

def process_messages():
    """Process event messages from Kafka."""
    kafka_config = app_config['kafka']
    client = KafkaClient(hosts=f"{kafka_config['hostname']}:{kafka_config['port']}")
    topic = client.topics[str.encode(kafka_config['topic'])]
    consumer = topic.get_simple_consumer(consumer_group=b"storage_group", reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)
    
    for message in consumer:
        if message is not None:
            msg_str = message.value.decode('utf-8')
            msg = json.loads(msg_str)
            logger.info(f"Consumed message: {msg_str}")
            
            if msg['type'] == 'thermostat':
                store_thermostat_event(msg['payload'])
            elif msg['type'] == 'lighting':
                store_lighting_event(msg['payload'])
            
            consumer.commit_offsets()

def store_thermostat_event(event):
    """Store the thermostat event to the DB."""
    session = DBSession()
    te = ThermostatEvent(
        trace_id=event['trace_id'],
        temperature=event['temperature'],
        status=event['status'],
        timestamp=datetime.strptime(event['timestamp'], "%Y-%m-%dT%H:%M:%S")
    )
    session.add(te)
    session.commit()
    session.close()
    logger.debug(f"Stored thermostat event with trace id {event['trace_id']}")

def store_lighting_event(event):
    """Store the lighting event to the DB."""
    session = DBSession()
    le = LightingEvent(
        trace_id=event['trace_id'],
        intensity=event['intensity'],
        status=event['status'],
        timestamp=datetime.strptime(event['timestamp'], "%Y-%m-%dT%H:%M:%S")
    )
    session.add(le)
    session.commit()
    session.close()
    logger.debug(f"Stored lighting event with trace id {event['trace_id']}")

def get_thermostat_events(start_timestamp, end_timestamp):
    """Retrieve thermostat events from the DB between two timestamps."""
    session = DBSession()
    start = datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    end = datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    events = session.query(ThermostatEvent).filter(
        ThermostatEvent.timestamp >= start, 
        ThermostatEvent.timestamp <= end
    ).all()
    # Convert SQLAlchemy objects to a serializable format
    results = [event.to_dict() for event in events]
    session.close()
    return results, 200

def get_lighting_events(start_timestamp, end_timestamp):
    """Retrieve lighting events from the DB between two timestamps."""
    session = DBSession()

    start = datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    end = datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    events = session.query(LightingEvent).filter(
        LightingEvent.timestamp >= start, 
        LightingEvent.timestamp <= end
    ).all()
    # Convert SQLAlchemy objects to a serializable format
    results = [event.to_dict() for event in events]
    session.close()
    return results, 200


# Flask application setup
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    # Start Kafka message processing in a separate thread
    t1 = Thread(target=process_messages)
    t1.daemon = True
    t1.start()

    # Start the Flask application
    app.run(port=8090)
