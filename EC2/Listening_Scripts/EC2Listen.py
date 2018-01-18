#-------------------------------Ayal & Guy's Security Camera - 2018 ------------------------------------
#Listening Script from EC2 - Handles MQTT messages and Mannaging SecCam

#-----------------Imports----------------------
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import sys
import logging
import time
import argparse
from time import sleep
import subprocess
import boto3
from time import gmtime, strftime, localtime
import os
import signal

#------------------------Constants--------------------
UPDATE_TIME = 30 #The frequency Segment is updated [sec]
SEGMENT_LEN = 60*30 #The length of a single segment [sec]
SEG_LIFE = (60*60*24) # The length of a single segment lifetime (after that - it will be deleted) [sec]

#------------------------CALLBACKS----------------------------
# Custom MQTT message callback

def thisIsStart():
	global start_time
	start_time = time.time()
	global n_time
	n_time = start_time + 0.001
	global current_time
	current_time = time.time() + 0.002
	global ifstart
	ifstart = True
	global last_rec
       	last_rec = True
	global filename
	global if_first
	if_first = True
	filename = strftime("Cam1-%d-%m-%Y-%H:%M:%S.webm", localtime())
	print("Janus started!")

def customCallback(client, userdata, message):
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")
	if (message.topic == "StartJanus"):
		#Start Janus - (and delete old videos)
		for file in os.listdir('/home/ubuntu/Rec/'):
			bashCommand = "sudo rm /home/ubuntu/Rec/"+file
               		process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
		bashCommand = "sudo /home/ubuntu/janus-gateway/janus -F /opt/janus/etc/janus -1 *EC2's IP*&"
		process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)             
		thisIsStart()
	if (message.topic == "StopJanus"):
		#Stop Janus
		global ifstart
		if (ifstart == True):
	                global last_rec
			last_rec = True
		bashCommand = "sudo pkill janus"
                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
		process.wait()
		ifstart = False
	if (message.topic == "StartRecord"):
		#Saves the record's start time - turn on flags and edit file's name
		global is_rec
		if (is_rec == False):
			global start_record
			start_record = time.time()
			if (start_record < 0):
				start_record = 0
			is_rec = True
			global is_record_stop
			is_record_stop = False
			print ("---------Got start Rec -----------")
			print (start_record-start_time)
			global record_name 
			record_name = strftime("Cam1-%d-%m-%Y-%H:%M:%S.webm", localtime())
	if (message.topic == "StopRecord"):
		#Saves the record's end time - edit flags
		if (is_rec == True):
			global stop_record
        	        stop_record = time.time()
			if (stop_record < 0):
				stop_record = 5
                	is_record_stop = True
			print ("---------Got stop Rec -----------")
			print(stop_record-start_time)


#------------------------CALLBACKS DONE----------------------------
        



#------------------------PARSER----------------------------
# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub", help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="OpenPiCam", help="Targeted topic")

args = parser.parse_args()
host = "*AWS CERT KEY*"
rootCAPath = "*AWS CERT KEY*"
certificatePath = "*AWS CERT KEY*"
privateKeyPath = "*AWS CERT KEY*"
useWebsocket = args.useWebsocket
clientId = args.clientId
#------------------------PARSER DONE----------------------------

#------------------------INIT----------------------------
start_time = time.time() #Start Janus session time
n_time = start_time #Start segment time
start_record = time.time() #Start Record time
stop_record = time.time() #Stop record time
is_rec = False # If recording
current_time = time.time()
os.environ["TZ"]="UTC-2" #Adjust system clock
time.tzset() #Set system clock
record_name = strftime("Cam1-%d-%m-%Y-%H:%M:%S.webm", localtime()) #Record's name
global is_record_stop
is_record_stop = True #Flag for stop recording
global ifstart
ifstart = False #Flag to indicate streaming session start
filename = strftime("Cam1-%d-%m-%Y-%H:%M:%S.webm", localtime()) #Segment's name
last_rec = False #Flag for saving videos after shut down
if_first = False #First iteration
#------------------------INIT DONE----------------------------


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

#------------------------LISTENING---------------------------
def handler(signum, frame): #handle signal
    print '!!!!!!!!!!!Shutting down...'
    sys.exit(0)


print("Connection succeeded: Listening...")
# Connect and subscribe to AWS IoT -TOPPPICCCCC - OPENPICAM
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe("StartJanus", 1, customCallback)
myAWSIoTMQTTClient.subscribe("StopJanus", 1, customCallback)
myAWSIoTMQTTClient.subscribe("StartRecord", 1, customCallback)
myAWSIoTMQTTClient.subscribe("StopRecord", 1, customCallback)
myAWSIoTMQTTClient.subscribe("UploadVideo", 1, customCallback)
signal.signal(signal.SIGINT, handler)
time.sleep(2)

#------------------------LISTENING DONE---------------------------
while (True):
	time.sleep(1)
	if (ifstart == True):
		                # Connect Amazon S3
                s3 = boto3.resource('s3',
                        aws_access_key_id='"*AWS CERT KEY*"',
                        aws_secret_access_key='"*AWS CERT KEY*"',)
		if ((time.time() - current_time) > UPDATE_TIME):
			#Handle segment update - every UPDATE_TIME - remove temp files and re-create them
			print("----------------------- Segment Update -------------------")
			current_time = time.time()
                        bashCommand = "sudo rm /home/ubuntu/tmp.webm"
                        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
                        process.wait()
                        print("tmp.webm deleted!")
                        bashCommand = "sudo rm /home/ubuntu/X1.webm"
                        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
                        process.wait()
                        print("X1.webm deleted!")                	
			bashCommand = "ls -s /home/ubuntu/Rec | sort -n | tail -1 | cut -d ' ' -f 2"
           	     	process = subprocess.Popen(bashCommand , shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
               	 	out, err = process.communicate()
                	process.wait()
                	bashCommand = "sudo /home/ubuntu/janus-gateway/janus-pp-rec /home/ubuntu/Rec/" + out + " tmp.webm"
                	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                	process.wait()
			print("tmp.webm created!")
			#calculate video time
			tmp_time = (n_time - 10)-start_time
			if (tmp_time < 0):
				tmp_time = 0
			m, s = divmod(tmp_time, 60)
			h, m = divmod(m, 60)
			sn_time = "%02d:%02d:%02d" % (h, m, s)
			m, s = divmod(current_time-n_time+15, 60)
                        h, m = divmod(m, 60)
                        s_curr_time = "%02d:%02d:%02d" % (h, m, s)			
			bashCommand = "ffmpeg -i tmp.webm -ss "+sn_time+" -t "+s_curr_time+" -c copy X1.webm"
			process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        process.wait()
			m, s = divmod(n_time - start_time, 60)
                        h, m = divmod(m, 60)
			print_time = "%02d:%02d:%02d" % (h, m, s)
                        print("tmp.webm cut! from "+print_time+", Duration[sec]: "+str(UPDATE_TIME))
			if ((out != "") and (ifstart == True)):
                        	data = open('X1.webm', 'rb')
                        	s3.Object('ayalgenzer',filename).delete()
				time.sleep(1)
                        	s3.Bucket('ayalgenzer').put_object(Key=filename, Body=data)
				print("Uploading to AWS...")
				time.sleep(2)
  	                	print("Upload to last 24H succeeded: "+filename)
			current_time= time.time()
			if ((is_rec == True) and (is_record_stop == True)):
		                print("----------------------- Recording Saved Segment -------------------")
                		#Start of recording after start of segment
                                bashCommand = "sudo rm /home/ubuntu/X2.webm"
                                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
                                process.wait()
                                print("X2.webm deleted!")
                                bashCommand = "sudo rm /home/ubuntu/tmp2.webm"
                                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
                                process.wait()
                                print("tmp2.webm deleted!")				
			        bashCommand = "ls -s /home/ubuntu/Rec | sort -n | tail -1 | cut -d ' ' -f 2"
                        	process = subprocess.Popen(bashCommand , shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
                        	out, err = process.communicate()
                        	process.wait()
                        	bashCommand = "sudo /home/ubuntu/janus-gateway/janus-pp-rec /home/ubuntu/Rec/" + out + " tmp2.webm"
                        	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        	process.wait()
				print("tmp2.webm created!")
				tmp_time = (start_record-15)-start_time
				if (tmp_time < 0):
                                	tmp_time = 0
                       		m, s = divmod(tmp_time, 60)
                		h, m = divmod(m, 60)
                		sn_time = "%02d:%02d:%02d" % (h, m, s)
				is_rec = False
				print("----------------------- Stop Recording Segment -------------------")
				m, s = divmod(12+stop_record-start_record, 60)
                                h, m = divmod(m, 60)
                                s_curr_time = "%02d:%02d:%02d" % (h, m, s)
                		bashCommand = "ffmpeg -i tmp2.webm -ss "+sn_time+" -t "+s_curr_time+" -c copy X2.webm"
                		process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                		process.wait() 
               	 		m, s = divmod((start_record-6.5)-start_time, 60)
				h, m = divmod(m, 60)
				print_time = "%02d:%02d:%02d" % (h, m, s)
				print("tmp2.webm cut! from "+print_time+", Duration[sec]: "+s_curr_time)
                		data = open('X2.webm', 'rb')
				s3.Object('savedvids',record_name).delete()
                		time.sleep(1)
				s3.Bucket('savedvids').put_object(Key=record_name, Body=data)
				print("Uploading to AWS...")
				time.sleep(2)
                		current_time= time.time()
				try:
					if(1 == myAWSIoTMQTTClient.publish("UploadSuccess", "Video uploaded", 1)):
	        				print("MQTT Publish for UploadSuccess succeeded!")
					else:
       						print("MQTT Publish for UploadSuccess Failed!")
				except:
					print("MQTT Publish for UploadSuccess Failed!")
				print("Upload to Saved Videos succeeded! File closed: "+record_name) 
		if ((time.time() - n_time) > SEGMENT_LEN):
			#Handle segment Close - every SEGMENT_LEN
			print("----------------------- Segment Close -------------------")
			old_n_time = n_time
			current_time= time.time()
			n_time = time.time()
                        bashCommand = "sudo rm /home/ubuntu/tmp.webm"
                        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
                        process.wait()
                        print("tmp.webm deleted!")
                        bashCommand = "sudo rm /home/ubuntu/X1.webm"
                        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
                        process.wait()
                        print("X1.webm deleted!")
			bashCommand = "ls -s /home/ubuntu/Rec | sort -n | tail -1 | cut -d ' ' -f 2"
                	process = subprocess.Popen(bashCommand , shell = True, stdout=subprocess.PIPE) 
                	out, err = process.communicate()
                	process.wait()
                	bashCommand = "sudo /home/ubuntu/janus-gateway/janus-pp-rec /home/ubuntu/Rec/" + out + " tmp.webm"
                	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                	process.wait()
			print("tmp.webm created!")
			tmp_time = (old_n_time-10)-start_time
	                if (tmp_time < 0):
                                tmp_time = 0
                        m, s = divmod(tmp_time, 60)
                        h, m = divmod(m, 60)
                        sn_time = "%02d:%02d:%02d" % (h, m, s)
                        m, s = divmod(current_time-old_n_time+15, 60)
                        h, m = divmod(m, 60)
                        s_curr_time = "%02d:%02d:%02d" % (h, m, s)
			bashCommand = "ffmpeg -i tmp.webm -ss "+sn_time+" -t "+s_curr_time+" -c copy X1.webm" 
                        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        process.wait() 
                        m, s = divmod(old_n_time-start_time, 60)
                        h, m = divmod(m, 60)
			print_time = "%02d:%02d:%02d" % (h, m, s)
			print("tmp.webm cut! from "+print_time+" , Duration[sec]: "+str(SEGMENT_LEN))
			data = open('X1.webm', 'rb')
			s3.Object('ayalgenzer',filename).delete()
			time.sleep(1)
                	s3.Bucket('ayalgenzer').put_object(Key=filename, Body=data)
			print("Uploading to AWS...")
			time.sleep(2)
			current_time= time.time()
			print("Upload to last 24H succeeded! file closed: "+filename)
                	filename = strftime("Cam1-%d-%m-%Y-%H:%M:%S.webm", localtime())
	        	#Record
			if ((is_rec == True) and (is_record_stop == True)):
                                print("----------------------- Recording Saved Segment -------------------")
                                #Start of recording after start of segment
                                bashCommand = "sudo rm /home/ubuntu/X2.webm"
                                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
                                process.wait()
                                print("X2.webm deleted!")
                                bashCommand = "sudo rm /home/ubuntu/tmp2.webm"
                                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
                                process.wait()
                                print("tmp2.webm deleted!")
                                bashCommand = "ls -s /home/ubuntu/Rec | sort -n | tail -1 | cut -d ' ' -f 2"
                                process = subprocess.Popen(bashCommand , shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
                                out, err = process.communicate()
                                process.wait()
                                bashCommand = "sudo /home/ubuntu/janus-gateway/janus-pp-rec /home/ubuntu/Rec/" + out + " tmp2.webm"
                                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                process.wait()
                                print("tmp2.webm created!")
                                tmp_time = (start_record-15)-start_time
                                if (tmp_time < 0):
                                        tmp_time = 0
                                m, s = divmod(tmp_time, 60)
                                h, m = divmod(m, 60)
                                sn_time = "%02d:%02d:%02d" % (h, m, s)
                                is_rec = False
                                print("----------------------- Stop Recording Segment -------------------")
                                m, s = divmod(12+stop_record-start_record, 60)
                                h, m = divmod(m, 60)
                                s_curr_time = "%02d:%02d:%02d" % (h, m, s)
                                bashCommand = "ffmpeg -i tmp2.webm -ss "+sn_time+" -t "+s_curr_time+" -c copy X2.webm"
                                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                process.wait() 
                                m, s = divmod((start_record-6.5)-start_time, 60)
                                h, m = divmod(m, 60)
                                print_time = "%02d:%02d:%02d" % (h, m, s)
                                print("tmp2.webm cut! from "+print_time+", Duration[sec]: "+s_curr_time)
                                data = open('X2.webm', 'rb')
                                s3.Object('savedvids',record_name).delete()
                                time.sleep(1)
                                s3.Bucket('savedvids').put_object(Key=record_name, Body=data)
                                print("Uploading to AWS...")
                                time.sleep(2)
                                current_time= time.time()
                                try:
                                        if(1 == myAWSIoTMQTTClient.publish("UploadSuccess", "Video uploaded", 1)):
                                                print("MQTT Publish for UploadSuccess succeeded!")
                                        else:
                                                print("MQTT Publish for UploadSuccess Failed!")
                                except:
                                        print("MQTT Publish for UploadSuccess Failed!")

				print("Upload to Saved Videos succeeded! File closed: "+record_name)
			#Record
			if ((time.time() - start_time) > SEG_LIFE):
                       		 #Handle Segment drop - Saves SEG_LIFE back
                        	print("----------------------- Segment Drop -------------------")
				bucket = s3.Bucket(name='ayalgenzer')
				res = bucket.objects.filter(Prefix='Cam1')
				first = False
				for obj in res:
     					if (first == False):
             					first = True
             					nkey = obj.key
             					ndate = obj.last_modified
     				else:
             				if (obj.last_modified < ndate):
                     				ndate = obj.last_modified
                     				nkey = obj.key
				if ((first == True) and (obj != None)):
		                        s3.Object('ayalgenzer',nkey).delete()
		                        print("Old segment removed! file: "+nkey)
	else:
		if (last_rec == True):
			#Handle Closing and uploading last segment after streaming is over
			last_rec = False
                        print("----------------------- Segment Close -------------------")
                        old_n_time = n_time
                        current_time= time.time()
                        n_time = time.time()
                        bashCommand = "sudo rm /home/ubuntu/tmp.webm"
                        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
                        process.wait()
                        print("tmp.webm deleted!")
                        bashCommand = "sudo rm /home/ubuntu/X1.webm"
                        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
                        process.wait()
                        print("X1.webm deleted!")
                        bashCommand = "ls -s /home/ubuntu/Rec | sort -n | tail -1 | cut -d ' ' -f 2"
                        process = subprocess.Popen(bashCommand , shell = True, stdout=subprocess.PIPE) 
                        out, err = process.communicate()
                        process.wait()
                        bashCommand = "sudo /home/ubuntu/janus-gateway/janus-pp-rec /home/ubuntu/Rec/" + out + " -c copy tmp.webm"
                        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        process.wait()
                        print("tmp.webm created!")
                        tmp_time = (old_n_time-6.5)-start_time
                        if (tmp_time < 0):
                                tmp_time = 0
                        m, s = divmod(tmp_time, 60)
                        h, m = divmod(m, 60)
                        sn_time = "%02d:%02d:%02d" % (h, m, s)
                        m, s = divmod(current_time-old_n_time+5, 60)
                        h, m = divmod(m, 60)
                        s_curr_time = "%02d:%02d:%02d" % (h, m, s)
                        bashCommand = "ffmpeg -i tmp.webm -ss "+sn_time+" -t "+s_curr_time+" X1.webm" 
                        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        process.wait() 
			m, s = divmod((old_n_time-6.5)-start_time, 60)
                        h, m = divmod(m, 60)
                        print_time = "%02d:%02d:%02d" % (h, m, s)
                        print("tmp.webm cut! from "+print_time+" , Duration[sec]: "+s_curr_time)
                        data = open('X1.webm', 'rb')
                        s3.Object('ayalgenzer',filename).delete()
                        time.sleep(1)
                        s3.Bucket('ayalgenzer').put_object(Key=filename, Body=data)
                        print("Uploading to AWS...")
			time.sleep(2)
                        current_time= time.time()
                        print("Upload to last 24H succeeded! file closed: "+filename)
                        if (is_rec == True):
                                print("----------------------- Recording Saved Segment -------------------")
                                #Handle Closing record after streaming is over
                                bashCommand = "sudo rm /home/ubuntu/X2.webm"
                                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
                                process.wait()
                                print("X2.webm deleted!")
                                bashCommand = "sudo rm /home/ubuntu/tmp2.webm"
                                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
                                process.wait()
                                print("tmp2.webm deleted!")
                                bashCommand = "ls -s /home/ubuntu/Rec | sort -n | tail -1 | cut -d ' ' -f 2"
                                process = subprocess.Popen(bashCommand , shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
                                out, err = process.communicate()
                                process.wait()
                                bashCommand = "sudo /home/ubuntu/janus-gateway/janus-pp-rec /home/ubuntu/Rec/" + out + " tmp2.webm"
                                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                process.wait()
                                print("tmp2.webm created!")
                                tmp_time = (start_record-15)-start_time
                                if (tmp_time < 0):
                                        tmp_time = 0
                                m, s = divmod(tmp_time, 60)
                                h, m = divmod(m, 60)
                                sn_time = "%02d:%02d:%02d" % (h, m, s)
                                is_rec = False
                                print("----------------------- Stop Recording Segment -------------------")
                                m, s = divmod(12+current_time-start_record, 60)
                                h, m = divmod(m, 60)
                                s_curr_time = "%02d:%02d:%02d" % (h, m, s)
                                bashCommand = "ffmpeg -i tmp2.webm -ss "+sn_time+" -t "+s_curr_time+" -c copy X2.webm"
                                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                process.wait() 
                                m, s = divmod((start_record-6.5)-start_time, 60)
                                h, m = divmod(m, 60)
                                print_time = "%02d:%02d:%02d" % (h, m, s)
				print("tmp2.webm cut! from "+print_time+", Duration[sec]: "+s_curr_time)
                                data = open('X2.webm', 'rb')
                                s3.Object('savedvids',record_name).delete()
                                time.sleep(1)
                                s3.Bucket('savedvids').put_object(Key=record_name, Body=data)
                                print("Uploading to AWS...")
                                time.sleep(2)
                                current_time= time.time()
                                try:
                                        if(1 == myAWSIoTMQTTClient.publish("UploadSuccess", "Video uploaded", 1)):
                                                print("MQTT Publish for UploadSuccess succeeded!")
                                        else:
                                                print("MQTT Publish for UploadSuccess Failed!")
                                except:
                                        print("MQTT Publish for UploadSuccess Failed!")

                                print("Upload to Saved Videos succeeded! File closed: "+record_name) 
			print("Removing temporary files...")
			time.sleep(3)
	                bashCommand = "sudo rm /home/ubuntu/X1.webm"
	                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
        	        process.wait()
                	bashCommand = "sudo rm /home/ubuntu/tmp.webm"
                	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
                	process.wait()
                	bashCommand = "sudo rm /home/ubuntu/X2.webm"
                	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
                	process.wait()
                	bashCommand = "sudo rm /home/ubuntu/tmp2.webm"
                	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 
                	process.wait()
			print("Session Closed!")
