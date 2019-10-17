import ssl
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import json


def assign_shadow_certificates():
	shadowclient = AWSIoTMQTTShadowClient("client ID")
	shadowclient.configureEndpoint("endpoint", 8883)
	shadowclient.configureCredentials("rootCA", "private key", "certificate")
	return shadowclient

def update_shadow():
	shadow_client = assign_shadow_certificates()

	shadow_state = {}
	shadow_state = {"state": {"reported": {"take_photo": "True"}}}
	shadow_payload = json.dumps(shadow_state)

	shadow_client = shadow_client.getMQTTConnection()
	shadow_client.connect()
	shadow_client.publish("shadow update topic", shadow_payload, 1)
	shadow_client.disconnect()

def function():
	function = raw_input("take_photo?  ")
	if function == 'y':
		update_shadow()

def main():
	function()

if __name__ == '__main__':
	main()
