# Security-Camera
Streaming live video from rasbperry pi camera to an Android app and controlling movement with servo engines.

This repo contains an android app, AWS-EC2 scripts, rasbperry pi scripts and 3d camera pan tilt mount printing.

The pi streams live video from its camera to an EC2 instance which streams the video to a web page.

The app contains AWS-cognito identety, after logging the "video_activity" is launched.

The "video_activity" contains a WEB VIEW of the web pages with the video streaming and a GUI with arrows/gyro mode to move the camera
by publishing mqtt messages to different topics, these meassages are delivered to the pi and the pi sends signals to the GPIO connectet to the servo motors.

Another feature is to record a video and upload/download it to the AWS-S3 storage service.

The app is based on an open source AWS code samples & GitHub repositories.

credits:

for enabling video web view-
https://github.com/cprcrack/VideoEnabledWebView

parsing hardware sensors for gyro movement:
https://github.com/google-developer-training/android-advanced/tree/master/TiltSpot

AWS-Android-mobile-sdk:
https://github.com/awslabs/aws-sdk-android-samples

S3-
https://github.com/awslabs/aws-sdk-android-samples/tree/master/S3TransferUtilitySample

pubsub-mqtt
https://github.com/awslabs/aws-sdk-android-samples/tree/master/AndroidPubSub

cognito-
https://github.com/awslabs/aws-sdk-android-samples/tree/master/AmazonCognitoYourUserPoolsDemo




