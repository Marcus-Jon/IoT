import ssl
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import json
from time import sleep
import PIL as image
from picamera import PiCamera as pc
from boto.s3.connection import S3Connection
from boto.s3.key import Key

def customCallback(client, userdata, message):
	print message.topic
	print message.payload

	callback_state = message.payload[36:40]
	pi = rasp_pi()
	print 'state: ', callback_state
	if callback_state == 'True':
		global state
		state = callback_state

class rasp_pi:
	def __init__(self):
		pass

	def assign_certificates(self):
		client = AWSIoTMQTTClient("client id")
		client.configureEndpoint("your endpoint", 8883)
		client.configureCredentials("rootCA.pem", "private key", "certificate")
		client.configureOfflinePublishQueueing(-1)
		return client

	def assign_shadow_certificates(self):
		shadow_client = AWSIoTMQTTShadowClient("client id")
		shadow_client.configureEndpoint("your endpoint", 8883)
		shadow_client.configureCredentials("rootCA.pem", "private key", "certificate")
		return shadow_client

	def send_image(self, client):
		# Connect to MQTT broker to publish current status.
		topic = "topic name"
		client.connect()

		# upload file to the s3 bucket.
		# get keys from file
		key_file = open('keys.txt', 'r')
		keys = key_file.readlines()
		access_key = keys[0]
		secret_key = keys[1]
		access_key = access_key.strip()
	
		# connect to S3 bucket.
		connection = S3Connection(access_key, secret_key)
		bucket = connection.get_bucket('bucket name')
		key = Key(bucket)
		key.key = ('key name')
		key.set_contents_from_filename('filename')
	
		# payload for notification.
		payload = {}
		payload = {"state":{"file": "uploaded"}}
		payload = json.dumps(payload)

		client.publish(topic, payload, 1)
		client.disconnect()

	def take_image(self):
		# take image with raspberry pi camera.
		camera = pc()
		camera.resolution = (1024, 768)
		camera.start_preview()

		sleep(2)
		camera.capture('filename')

		client = self.assign_certificates()
		self.send_image(client)

	def check_update(self, shadow_client):
		running = True
		global state
		
		payload = {}
		payload = {"state": {"reported": {"take_photo":"idle"}}}
		shadow_payload = json.dumps(payload)
	
		shadow_client = shadow_client.getMQTTConnection()
		shadow_client.configureOfflinePublishQueueing(-1)
		shadow_client.connect()
		
		while running == True:
			shadow_client.publish("$aws/things/thing name/shadow/get", "", 1)
			shadow_client.subscribe("$aws/things/thing name/shadow/get/accepted", 1, customCallback)
			shadow_state = state
			if shadow_state == "True":
				shadow_client.publish("$aws/things/thing name/shadow/update", shadow_payload, 1)
				print 'state has been changed to idle'
				state = "idle"
				self.take_image()
				running = False

		shadow_client.disconnect()

def main():
	pi = rasp_pi()
	global state
	state = "idle"
	shadow_client = pi.assign_shadow_certificates()
	pi.check_update(shadow_client)

if __name__ == '__main__':
	main()
