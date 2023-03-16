from threading import Event
from typing import Optional, Any
from time import sleep
import json

import paho.mqtt.client as mqtt
import requests # The REST Client library

mqtt_client: Optional[mqtt.Client] = None

mqtt_connection_event = Event()
Message_callbackEvent = Event() # Wait for message to be received

continue_loop = True 
secret = -1
# --------------------------------------------------------------------------- #
# Write the secret number to the REST server as POST /secret_number as JSON
# and check the whether value sent was correct
# --------------------------------------------------------------------------- #
def send_secret_rest(secret_value: int):
    global continue_loop

    foo = {'value': secret_value}
    json_data = json.dumps(foo)
    session = requests.Session()
    r_post = session.post(url = 'http://server:80/secret_number', data = json_data)
    print("Post attempt successful ? : " + r_post.text)
    if r_post.text == 'OK':
        continue_loop = False # Terminate script after at least a value is sent
    r_get = session.get(url = 'http://server:80/secret_correct')
    print("Was the value correct ? : " + r_get.text)
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

def on_mqtt_connect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    mqtt_connection_event.set()

# --------------------------------------------------------------------------- #
# Receive and parse through JSON with secret number
# --------------------------------------------------------------------------- #
def on_mqtt_message(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):

    coded_message = str(msg.payload.decode("utf-8"))
    message = json.loads(coded_message)
    global secret
    secret = message['value']
    Message_callbackEvent.set()

# Note: It is generally not a good idea to do any advanced data processing such as 
# HTTP requests inside a callback function like on_message as that can create issues
# as more and more messages queue up



def connect_mqtt() -> mqtt.Client:
    client = mqtt.Client(
        clean_session=True,
        protocol=mqtt.MQTTv311
    )
    client.on_connect = on_mqtt_connect
    client.on_message = on_mqtt_message
    client.loop_start()
    client.connect('mqtt-broker', 1883)
    return client

# --------------------------------------------------------------------------- #
# Try Get request to server and wait while it  until server is ready
# --------------------------------------------------------------------------- #
def wait_for_server_ready():

    x = True
    while True:
        sleep(5)
        try:
            r = requests.get(url = 'http://server:80/ready') 
        except: 
            if x:
                print("Waiting for server ...")
                x=False
            continue
        else:   
            break
 
    

def main():
    global mqtt_client
    
    wait_for_server_ready()

    mqtt_client = connect_mqtt()
    mqtt_connection_event.wait()

    mqtt_client.subscribe('secret/number') # Subscribe to the MQTT topic: secret/number

    while continue_loop:

        Message_callbackEvent.wait() # Terminate script after at least a value is sent
        send_secret_rest(secret)

    try:
        mqtt_client.disconnect()
    except Exception:
        pass
    try:
        mqtt_client.loop_stop()
    except Exception:
        pass


if __name__ == '__main__':
    main()
