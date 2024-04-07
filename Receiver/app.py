import connexion
from connexion import NoContent
import yaml
import logging.config
import uuid
from pykafka import KafkaClient
import json
from datetime import datetime

# Load application configuration
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# Load logging configuration
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')

# Setup Kafka client from app configuration
kafka_config = app_config['kafka']
client = KafkaClient(hosts=f"{kafka_config['hostname']}:{kafka_config['port']}")
topic = client.topics[str.encode(kafka_config['topic'])]
producer = topic.get_sync_producer()

def submit_thermostat_event(body):
    """
    Function to submit a thermostat event to Kafka.
    """
    trace_id = str(uuid.uuid4())  # Generate unique trace_id
    logger.info(f"Received event thermostat request with a trace id of {trace_id}")
  
    body["trace_id"] = trace_id
    msg = {
        "type": "thermostat",
        "datetime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Returned event thermostat response (Id: {trace_id}) with status 201")
    return NoContent, 201

def submit_lighting_event(body):
    """
    Function to submit a lighting event to Kafka.
    """
    trace_id = str(uuid.uuid4())  # Generate unique trace_id
    logger.info(f"Received event lighting request with a trace id of {trace_id}")

    body["trace_id"] = trace_id
    msg = {
        "type": "lighting",
        "datetime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Returned event lighting response (Id: {trace_id}) with status 201")
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True, swagger_ui=False)

if __name__ == "__main__":
    app.run(port=8080)
