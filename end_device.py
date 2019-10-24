import ssl
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import json
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont
import boto3
from time import sleep


def assign_certificates():
	# assign the certificates for the connection to AWS IoT.
	client = AWSIoTMQTTClient("client id")
	client.configureEndpoint("your endpoint", 8883)
	client.configureCredentials("rootCA.pem", "private key", "certificate")
	return client

def assign_shadow_certificates():
	# assign the certificates for the connection to the device shadow on the IoT core.
	shadowclient = AWSIoTMQTTShadowClient("client id")
	shadowclient.configureEndpoint("your endpoint", 8883)
	shadowclient.configureCredentials("rootCA.pem", "private key", "certificate")
	return shadowclient

def get_keys():
	key_file = open('keys.txt', 'r')
	keys = key_file.readlines()
	access_key = keys[0]
	secret_key = keys[1]
	access_key.strip()
	
	return access_key, secret_key

def get_image():
	# get the image stored on the S3 bucket, and save it to a local file.
	connection = S3Connection()
	bucket = connection.get_bucket('S3 bucket name')
	key = Key(bucket)
	key.key = ('test')
	key.get_contents_to_filename('filename')
	
def update_shadow():
	# send an update to the device shadow to get the other device to take the picture.
	shadow_client = assign_shadow_certificates()

	shadow_state = {}
	shadow_state = {"state": {"reported": {"take_photo": "True"}}}
	shadow_payload = json.dumps(shadow_state)

	shadow_client = shadow_client.getMQTTConnection()
	shadow_client.connect()
	shadow_client.publish("$aws/things/thing_name/shadow/update", shadow_payload, 1)
	shadow_client.disconnect()

def detect_label(bucket, photo):
	# using the rekognition service to perform label detection on the stored image.
	rekognition = boto3.client('rekognition', region_name = 'region')
	response = rekognition.detect_labels(Image={'S3Object':{'Bucket': bucket, 'Name': photo}}, MaxLabels = 10)
	
	# call to get image.
	get_image()
	
	# open the image using PIL so that bounding boxes can be drawn to it.
	image = Image.open('filename')
	img_width, img_height = image.size
	draw = ImageDraw.Draw(image)

	print ""
	print "Detected labels for " + photo
	print ""
	
	# print the results of the labels that have been detected in the image.
	for label in response['Labels']:
		print 'label: ' + label['Name']
		print 'confidence: ' + str(label['Confidence'])
		
		# draw the bounding boxes.
		if 'Instances' in label:
			for instance in label['Instances']:
				
				box = instance['BoundingBox']
				left = img_width * box['Left']
				top = img_height * box['Top']
				width = img_width * box['Width']
				height = img_height * box['Height']

				points = ((left, top), (left + width, top), (left + width, top + height), (left, top + height), (left, top))
				draw.line(points, fill = '#00d400', width = 2)
				draw.text((left, top), label['Name'], (255, 255, 255))

	image.show()

def user_function():
	user_input = raw_input("take_photo?  ")
	if user_input == 'y':
		update_shadow()
		sleep(10)
		detect_label('bucket name','key')

def main():
	user_function()

if __name__ == '__main__':
	main()
