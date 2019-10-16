# Raspberry Pi MQTT publisher using AWS
import ssl
from matplotlib import pyplot as plt
import numpy as np
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import json

def cert_assignment():
    MQTTclient = AWSIoTMQTTClient("rasp_pi")
    Shadowclient = AWSIoTMQTTShadowClient("rasp_pi_shadow")
    MQTTclient.configureEndpoint("endpoint", 8883)
    Shadowclient.configureEndpoint("endpoint", 8883)
    MQTTclient.configureCredentials("rootCA.pem", "private key", "certificate")
    Shadowclient.configureCredentials("rootCA.pem", "private key", "certificate")
    return MQTTclient, Shadowclient

def update_shadow(client):
    shadow_state = {}
    shadow_state = {"state": {"reported": {"color": "green"}}}
    shadow_js = json.dumps(shadow_state)
    client = client.getMQTTConnection()
    client.connect()
    client.publish("shadow update topic", shadow_js, 1)
    client.disconnect()

def connect(MQTTclient, topic, payload):
    MQTTclient.connect()
    MQTTclient.publish(topic, payload, 0)
    MQTTclient.disconnect()

def main():
    print 'MQTT Publisher'
    client, shadowclient = cert_assignment()

    topic = "test_pi"
    payload = {}
    payload['Allomancy'] = []
    payload['Allomancy'].append({'Iron': 'Pull', 'Steel': 'Push', 'Copper': 'Pull'})

    js = json.dumps(payload)

    with open('data.json', 'w') as outfile:
        json.dump(payload, outfile, indent = 4)

    connect(client, topic, js)
    #update_shadow(shadowclient)


if __name__ == '__main__':
    main()
