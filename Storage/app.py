import connexion
from connexion import NoContent
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from base import Base
import yaml
import logging
import logging.config
import datetime
from event_models import ThermostatEvent, LightingEvent
import os
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread


# Load logging configuration
log_conf_path = os.path.join(os.path.dirname(__file__), 'log_conf.yml')
with open(log_conf_path, 'r') as f:
    log_config = yaml.safe_load(f)
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')

# Load database configuration
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f)

# Log the database connection details
logger.info(f"Connecting to MySQL database at {app_config['db']['hostname']} on port {app_config['db']['port']}")

# Database engine creation
# DB_ENGINE = create_engine('mysql+pymysql://root:Passw0rd@127.0.0.1:3306/smart_home')
DB_ENGINE= create_engine(f"mysql+pymysql://{app_config['db']['user']}:{app_config['db']['password']}@{app_config['db']['hostname']}:{app_config['db']['port']}/{app_config['db']['db']}")
# Create a Session Factory
DB_SESSION = sessionmaker(bind=DB_ENGINE)

# Create all tables by issuing CREATE TABLE commands to the DB for all models
Base.metadata.create_all(DB_ENGINE)

def process_messages():
    """Process event messages."""
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)
    
    for msg in consumer:
        if msg is not None:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            logger.info(f"Message: {msg}")
            payload = msg["payload"]
            
            if msg["type"] == "thermostat_event":
                getThermostatEvents(payload)
            elif msg["type"] == "lighting_event":
                getLightingEvents(payload)
            
            consumer.commit_offsets()

def getThermostatEvents(start_timestamp, end_timestamp):
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')

    results = session.query(ThermostatEvent).filter(
        and_(ThermostatEvent.timestamp >= start_timestamp_datetime, ThermostatEvent.timestamp < end_timestamp_datetime))

    results_list = []
    for event in results:
        results_list.append(event.to_dict())

    session.close()

    logger.info(f"Query for Thermostat events after {start_timestamp} returns {len(results_list)} results")

    return results_list, 200

def getLightingEvents(start_timestamp, end_timestamp):
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')

    results = session.query(LightingEvent).filter(
        and_(LightingEvent.timestamp >= start_timestamp_datetime, LightingEvent.timestamp < end_timestamp_datetime))

    results_list = []
    for event in results:
        results_list.append(event.to_dict())

    session.close()

    logger.info(f"Query for Lighting events after {start_timestamp} returns {len(results_list)} results")

    return results_list, 200


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    # Kafka Consumer Thread
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    
    app.run(port=8090)

