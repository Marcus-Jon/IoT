# Raspberry Pi MQTT subscriber using AWS
import ssl
from matplotlib import pyplot as plt
import numpy as np
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import json

def customCallback(client, userdata, message):
    print "new message received"
    print message.topic
    print message.payload

def cert_assignment():
    MQTTclient = AWSIoTMQTTClient("rasp_pi_sub")
    Shadowclient = AWSIoTMQTTShadowClient("rasp_pi_sub_shadow")
    MQTTclient.configureEndpoint("endpoint", 8883)
    Shadowclient.configureEndpoint("endpoint", 8883)
    MQTTclient.configureCredentials("rootCA.pem", "private key", "certificate")
    Shadowclient.configureCredentials("rootCA.pem", "private key", "certificate")
    return MQTTclient, Shadowclient

def sub_MQTT(client, topic):
    client.connect()
    while True:
        client.subscribe(topic, 1, customCallback)
    client.disconnect()

def sub_shadow(shadow_client):
    shadowclient = shadow_client.getMQTTConnection()
    shadowclient.connect()
    while True:
        shadowclient.subscribe("shadow update accepted topic", 1, customCallback)
    shadowclient.disconnect()

def main():
    print "MQTT subscriber"
    topic = "test_pi"
    client, shadow_client = cert_assignment()
    sub_shadow(shadow_client)
    #sub_MQTT(client, topic)

if __name__ == '__main__':
    main()
