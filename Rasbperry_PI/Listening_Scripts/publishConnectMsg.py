#this scripts path is: /home/pi/Desktop/testayal
import boto3
from time import sleep
client = boto3.client('iot-data', region_name='us-east-1',
                      aws_access_key_id='',
                      aws_secret_access_key='')


response = client.publish(
    topic='CameraConnected',
    payload='Security Camera is connected!!!'
)
response = client.publish(
    topic='StopJanus',
    payload='Restarting Janus!!!'
)
sleep(10)
response = client.publish(
    topic='StartJanus',
    payload='Restarting Janus!!!'
)

