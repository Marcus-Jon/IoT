import ssl
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import json
from time import sleep
import PIL as image
from picamera import PiCamera as pc
from boto.s3.connection import S3Connection
from boto.s3.key import Key


def assign_certificates():
	client = AWSIoTMQTTClient("client id")
	client.configureEndpoint("endpoint", 8883)
	client.configureCredentials("rootCA", "private key", "certificate")
	client.configureOfflinePublishQueueing(-1)
	return client

def assign_shadow_certificates():
	shadow_client = AWSIoTMQTTShadowClient("client id")
	shadow_client.configureEndpoint(endpoint", 8883)
	shadow_client.configureCredentials("rootCA", "private key", "certificate")
	return shadow_client

def send_image(client):
	# Connect to MQTT broker to publish current status.
	topic = "pi_image"
	client.connect()

	# upload file to the s3 bucket.
	# get keys from file
	key_file = open('key file', 'r')
	keys = key_file.readlines()
	access_key = keys[0]
	secret_key = keys[1]
	access_key = access_key.strip()
	
	# connect to S3 bucket.
	connection = S3Connection(access_key, secret_key)
	bucket = connection.get_bucket('s3 bucket')
	key = Key(bucket)
	key.key = ('test')
	key.set_contents_from_filename('file name')
	
	# payload for notification.
	payload = {}
	payload = {"state":{"file": "uploaded"}}
	payload = json.dumps(payload)

	client.publish(topic, payload, 1)
	client.disconnect()

def take_image():
	# take image with raspberry pi camera.
	camera = pc()
	camera.resolution = (1024, 768)
	camera.start_preview()

	sleep(2)
	camera.capture('file name')

	client = assign_certificates()
	send_image(client)

def update_shadow():
	shadow_client = assign_shadow_certificates()

	# update the device shadow.
	payload = {}
	payload = {"state": {"reported": {"take_photo":"idle"}}}
	shadow_payload = json.dumps(payload)

	shadow_client = shadow_client.getMQTTConnection()
	shadow_client.configureOfflinePublishQueueing(-1)
	shadow_client.connect()
	shadow_client.publish("shadow update topic", shadow_payload, 1)
	shadow_client.disconnect()

def customCallback(client, userdata, message):
	print message.topic
	print message.payload
	
	# check the state of the device shadow payload
	state = message.payload[36:40]
	if state == 'True':
		take_image()
		update_shadow()

def check_update(shadow_client):
	# establish connection to MQTT broker on AWS.
	shadow_client = shadow_client.getMQTTConnection()
	shadow_client.configureOfflinePublishQueueing(-1)
	shadow_client.connect()

	# wait for update to the device shadow for the raspberry pi.
	while True:
		shadow_client.subscribe("shadow update accepted topic", 1, customCallback)
	shadow_client.disconnect()

def main():
	shadow_client = assign_shadow_certificates()

	check_update(shadow_client)

if __name__ == '__main__':
	main()
