import ssl
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import json
from time import sleep
import PIL as image
#from picamera import PiCamera as pc
from boto.s3.connection import S3Connection
from boto.s3.key import Key


def assign_certificates():
	client = AWSIoTMQTTClient("client ID")
	client.configureEndpoint("endpoint", 8883)
	client.configureCredentials("rootCA", "private key", "certificate")
	client.configureOfflinePublishQueueing(-1)
	return client

def assign_shadow_certificates():
	shadow_client = AWSIoTMQTTShadowClient("client shadow ID")
	shadow_client.configureEndpoint("endpoint", 8883)
	shadow_client.configureCredentials("rootCA", "private", "certificate")
	return shadow_client

def send_image(client):
	topic = "topic name"
	payload = {}
	payload = {"state":{"image": "taken"}}
	payload = json.dumps(payload)

	client.connect()
	client.publish(topic, payload, 1)

	# upload file to the s3 bucket
	key_file = open('keys.txt', 'r')
	keys = key_file.readlines()
	access_key = keys[0]
	secret_key = keys[1]
	access_key = access_key.strip()

	connection = S3Connection(access_key, secret_key)
	bucket = connection.get_bucket('s3_bucket_name')
	key = Key(bucket)
	key.key = ('test')
	key.set_contents_from_string('test.jpg')

	payload = {}
	payload = {"state":{"file": "uploaded"}}
	payload = json.dumps(payload)

	client.publish(topic, payload, 1)
	client.disconnect()

def take_image():
	# take image with raspberry pi camera.
	'''camera = pc()
	camera.resolution = (1024, 768)
	camera.start_preview()

	sleep(2)
	camera.capture('test.jpg')
'''
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

	state = message.payload[36:40]
	if state == 'True':
		update_shadow()
		take_image()

def check_update(shadow_client):
	# wait for update to the device shadow for the raspberry pi.
	shadow_client = shadow_client.getMQTTConnection()
	shadow_client.configureOfflinePublishQueueing(-1)
	shadow_client.connect()

	while True:
		shadow_client.subscribe("shadow update accepted topic", 1, customCallback)
	shadow_client.disconnect()

def main():
	shadow_client = assign_shadow_certificates()

	check_update(shadow_client)

if __name__ == '__main__':
	main()
