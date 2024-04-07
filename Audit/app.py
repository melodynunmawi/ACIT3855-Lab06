from pykafka import KafkaClient
import connexion
import yaml
import json
from threading import Thread

# Load configurations
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# Kafka setup
client = KafkaClient(hosts=f"{app_config['kafka']['hostname']}:{app_config['kafka']['port']}")
topic = client.topics[str.encode(app_config['kafka']['topic'])]
consumer = topic.get_simple_consumer()

# Events lists
thermostat_events = []
lighting_events = []

def consume_events():
    for message in consumer:
        if message is not None:
            event = json.loads(message.value.decode('utf-8'))
            if event['type'] == 'thermostat':
                thermostat_events.append(event)
            elif event['type'] == 'lighting':
                lighting_events.append(event)

# Start consuming in a separate thread
Thread(target=consume_events).start()

# API endpoints
def get_thermostat_event(index):
    try:
        return thermostat_events[index], 200
    except IndexError:
        return {"message": "Not Found"}, 404

def get_lighting_event(index):
    try:
        return lighting_events[index], 200
    except IndexError:
        return {"message": "Not Found"}, 404

# Flask application setup
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('openapi.yml')
app.run(port=8110)
