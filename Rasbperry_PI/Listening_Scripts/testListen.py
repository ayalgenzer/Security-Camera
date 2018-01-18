#this scripts path is: /home/pi/Desktop/testayal
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import sys
import logging
import time
import argparse
from picamera import PiCamera
from time import sleep
from time import gmtime, strftime
import boto3
import pigpio
import sys
import os
import signal
import subprocess
#------------------------CALLBACKS----------------------------
# Custom MQTT message callback
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")
	if (message.topic == "OpenPiCam"):
                try:
                    camera.start_preview()
                    camera.rotation = 180
                    sleep(10)
                finally:
                    camera.stop_preview()
                    camera.close()
        if (message.topic == "StartJanus"):
                bashCommand = "curl --insecure -s 'http://127.0.0.1:8080/janus?gateway_url=http://*PI's_IP*&gateway_root=/janus&room=*ROOMNUM*&room_pin=&username=&token=&publish=1&subscribe=0&hw_vcodec=0&vformat=60&reconnect=1&proxy_host=&proxy_port=80&proxy_password=&proxy_bypass=&reconnect=1&action=Start&' > /dev/null"
                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)    
		process.wait()
		bashCommand = "curl --insecure -s 'http://127.0.0.1:8080/panel?width=640&height=480&format=842093913&9963776=50&9963777=0&9963778=0&9963790=100&9963791=100&9963803=0&9963810=0&134217728=0&134217729=1&134217730=0&134217739=85&134217741=30&9963796=0&9963797=1&134217734=0&134217736=0&134217737=1&134217738=0&134217740=0&134217731=0&134217732=1&134217733=0&134217735=3&apply_changed=1' > /dev/null"
		process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)           
	if (message.topic == "StopJanus"):
                bashCommand = "curl --insecure -s 'http://127.0.0.1:8080/panel?width=640&height=480&format=842093913&9963776=50&9963777=0&9963778=0&9963790=100&9963791=100&9963803=0&9963810=0&134217728=0&134217729=1&134217730=0&134217739=85&134217741=30&9963796=1&9963797=1&134217734=0&134217736=0&134217737=1&134217738=0&134217740=0&134217731=0&134217732=1&134217733=0&134217735=3&apply_changed=1' > /dev/null"
		process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
		process.wait()
	if (message.topic == "MovePiCam"):
                duty_cycle_UD = pi.get_servo_pulsewidth(servo_pin_UD)
                duty_cycle_RL = pi.get_servo_pulsewidth(servo_pin_RL)
                if (message.payload == "Right"):
                        duty_cycle_RL = duty_cycle_RL - 30
                if (message.payload == "Left"):
                        duty_cycle_RL = duty_cycle_RL + 30
                if (message.payload == "Up"):
                        duty_cycle_UD = duty_cycle_UD + 30
                if (message.payload == "Down"):
                        duty_cycle_UD = duty_cycle_UD - 30
                if (len(message.payload.split()) == 2):
                        try:
                                angle_x = float(message.payload.split()[0])#Range 0 - 90 deg
                                angle_y = float(message.payload.split()[1])#Range 0 - 90  deg
                                duty_cycle_RL = MIN_DUTY+((1300 * angle_x) / 90)
                                duty_cycle_UD = MIN_DUTY+((1300 * angle_y) / 90)
                        except:
                                print("ERROR: angles are not floats!")
                                
                #---STAY IN LIMITS---        
                if (duty_cycle_UD < MIN_DUTY):
                        duty_cycle_UD = MIN_DUTY
                if (duty_cycle_UD > MAX_DUTY):
                        duty_cycle_UD = MAX_DUTY
                if (duty_cycle_RL < MIN_DUTY):
                        duty_cycle_RL = MIN_DUTY
                if (duty_cycle_RL > MAX_DUTY):
                        duty_cycle_RL = MAX_DUTY
                #---SET SERVO---
               	print("Tilt axis: [Up/Down] ")
		print(duty_cycle_UD)
		print("Pan axis: [Right/Left]: ")
		print(duty_cycle_RL)
		pi.set_servo_pulsewidth(servo_pin_UD ,duty_cycle_UD)
                pi.set_servo_pulsewidth(servo_pin_RL ,duty_cycle_RL)

#------------------------CALLBACKS DONE----------------------------
        



#------------------------PARSER----------------------------
# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="tmp1", help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="OpenPiCam", help="Targeted topic")

args = parser.parse_args()
host = "ak1xob3uf7qvf.iot.us-east-1.amazonaws.com"
rootCAPath = "*aws_CERT_KEY*"
certificatePath = "*aws_CERT_KEY*"
privateKeyPath = ""*aws_CERT_KEY*""
useWebsocket = args.useWebsocket
clientId = args.clientId

#------------------------PARSER DONE----------------------------


#------------------------CONNECT TO AWS----------------------------
if args.useWebsocket and certificatePath and privateKeyPath:
	parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
	exit(2)

if not args.useWebsocket and (not certificatePath or not privateKeyPath):
	parser.error("Missing credentials for authentication.")
	exit(2)

# Configure logging
#logger = logging.getLogger("AWSIoTPythonSDK.core")
#logger.setLevel(logging.DEBUG)
#streamHandler = logging.StreamHandler()
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#streamHandler.setFormatter(formatter)
#logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
	myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
	myAWSIoTMQTTClient.configureEndpoint(host, 443)
	myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
	myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
	myAWSIoTMQTTClient.configureEndpoint(host, 8883)
	myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
#------------------------CONNECT TO AWS DONE----------------------------

#------------------------SERVO Init----------------------------
pi = pigpio.pi() # Connect to local Pi.

#Constants
MIN_DUTY = 1000
MAX_DUTY = 2400
CENTRE = (((MAX_DUTY - MIN_DUTY) / 2) + MIN_DUTY)


duty_cycle = CENTRE     # Should be the center for a SG90

# Configure the Pi to use pin names 
servo_pin_UD = 13
servo_pin_RL = 5

# Create PWM channel on the servo pin with a frequency of CENTRE
duty_cycle_UD = CENTRE
duty_cycle_RL = CENTRE
print("init Tilt axis [Up/Down]: ")
print(duty_cycle_UD)
print("init Pan axis [Right/Left]: ")
print(duty_cycle_RL)
pi.set_servo_pulsewidth(servo_pin_UD , duty_cycle_UD)
pi.set_servo_pulsewidth(servo_pin_RL , duty_cycle_RL)

#------------------------SERVO Init DONE----------------------------


#------------------------LISTENING---------------------------
def handler(signum, frame):
    print("Cleaning up GPIO...")
    tmp=pi.set_servo_pulsewidth(servo_pin_UD , CENTRE)
    tmp=pi.set_servo_pulsewidth(servo_pin_RL , CENTRE)
    time.sleep(0.5)
    tmp=pi.set_servo_pulsewidth(servo_pin_UD , 0)
    tmp=pi.set_servo_pulsewidth(servo_pin_RL , 0)
    time.sleep(0.5)
    pi.stop()
    print '!!!!!!!!!!!Shutting down...'
    sys.exit(0)


print("Connection succeeded: Listening...")
# Connect and subscribe to AWS IoT -TOPIC
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe("OpenPiCam", 1, customCallback)
myAWSIoTMQTTClient.subscribe("MovePiCam", 1, customCallback)
myAWSIoTMQTTClient.subscribe("StartJanus", 1, customCallback)
myAWSIoTMQTTClient.subscribe("StopJanus", 1, customCallback)
signal.signal(signal.SIGINT, handler)
time.sleep(2)
#------------------------LISTENING DONE---------------------------
while (True):
	time.sleep(1)



