# Raspberry Pi MQTT subscriber using AWS
import ssl
from matplotlib import pyplot as plt
import numpy as np
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import json

def customCallback(client, userdata, message):
    print "new message received"
    print message.payload

def cert_assignment():
    MQTTclient = AWSIoTMQTTClient("rasp_pi_sub")
    MQTTclient.configureEndpoint("endpoint", 8883)
    MQTTclient.configureCredentials("rootCA.pem", "private key", "certificate")
    return MQTTclient

def connect(client):
    client.connect()
    while True:
        client.subscribe("test_pi", 1, customCallback)
    client.disconnect()

def main():
    print "MQTT subscriber"
    client = cert_assignment()
    connect(client)

if __name__ == '__main__':
    main()
