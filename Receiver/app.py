import connexion
from connexion import NoContent
import datetime
import json
import logging
import logging.config
import pykafka
from pykafka import KafkaClient
import requests
import uuid
import yaml 

def process_event(event, endpoint):
    # trace_id = str(uuid.uuid4())
    # event['trace_id'] = trace_id

    # logging.debug(f'Received event {endpoint} with trace id: {trace_id}')
    # # TODO: call logger.debug and pass in message "Received event <type> with trace id <trace_id>"

    # headers = { 'Content-Type': 'application/json' }
    
    # url = app_config[endpoint]['url']
    # res = requests.post(url, headers=headers, data=json.dumps(event))
    # # TODO: update requests.post to use app_config property instead of hard-coded URL
    
    # logger.debug(f'Received response with trace id: {trace_id}, status code: {res.status_code}')
    # # TODO: call logger.debug and pass in message "Received response with trace id <trace_id>, status code <status_code>"

    # # pass
    # return res.text, res.status_code
    trace_id = str(uuid.uuid4())
    event['trace_id'] = trace_id

    logger.debug(f'Received {endpoint} event with trace id {trace_id}')

    # TODO: create KafkaClient object assigning hostname and port from app_config to named parameter "hosts"
    # and store it in a variable named 'client'
    hosts = receiver_app_config["events"]["hostname"] + ':' + str(receiver_app_config["events"]["port"])
    client = KafkaClient(hosts=hosts)

    # TODO: index into the client.topics array using topic from app_config
    # and store it in a variable named topic
    topic = client.topics[receiver_app_config["events"]["topic"]]

    # TODO: call get_sync_producer() on your topic variable
    # and store the return value in variable named producer
    producer = topic.get_sync_producer()  # create a Kafka producer using the topic

    # TODO: create a dictionary with three properties:
    # type (equal to the event type, i.e. endpoint param)
    # datetime (equal to the current time, formatted as per our usual format)
    # payload (equal to the entire event passed into the function)
    event_dict = {
        "type": endpoint,
        "datetime": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "payload": event
    }

    # TODO: convert the dictionary to a json string
    event_json = json.dumps(event_dict)

    # TODO: call the produce() method of your producer variable and pass in your json string
    # note: encode the json string as utf-8
    producer.produce(event_json.encode("utf-8"))
    
    # TODO: log "PRODUCER::producing x event" where x is the actual event type
    # TODO: log the json string
    logger.debug(f'PRODUCER::producing x {endpoint}')
    logger.debug(f"{event_json}")
    return NoContent, 201


# Endpoints
def buy(body):
    process_event(body, 'buy')
    return NoContent, 201

def sell(body):
    process_event(body, 'sell')
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read()) #use yaml library to read the configuration file

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

with open('receiver-app_conf.yml', 'r') as f:
    receiver_app_config = yaml.safe_load(f.read())

logger = logging.getLogger('basic') 
# we mostly deal with the objects of the Logger class, which are instantiated using
# the module-level function loggin.getLogger(name), "name" is a custom logger 
# unlike root logger, it cannot be configured using basicConfig(), have to use Handlers and Formatters

if __name__ == "__main__":
    app.run(port=8080)