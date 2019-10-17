# Internet of Things  
#### Programs created for the connection of a Raspberry Pi to AWS, using the AWS SDK  
_____________________________________________________________________________________  
The AWS_SDK folder contains to python files, one for publishing to the AWS IoT core and the other for subscribing to it. The end_device python program is used to publish an update to a device shadow which will cause a connected device to take a picture. The raspberry_pi_device file is designed to be run on a raspberry pi with a connected camera. It will wait for updates to the device shadow, and when one is detected it will take a photo and upload it to an S3 bucket.
