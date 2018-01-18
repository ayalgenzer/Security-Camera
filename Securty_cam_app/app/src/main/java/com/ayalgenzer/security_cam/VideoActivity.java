package com.ayalgenzer.security_cam;


import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.support.v7.app.AppCompatActivity;
import android.net.http.SslError;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.Display;
import android.view.Surface;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.webkit.PermissionRequest;
import android.webkit.SslErrorHandler;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.ImageButton;
import android.widget.Switch;
import android.widget.TextView;

import com.amazonaws.mobileconnectors.iot.AWSIotMqttNewMessageCallback;
import com.amazonaws.mobileconnectors.iot.AWSIotMqttQos;

import java.io.UnsupportedEncodingException;
import java.util.Timer;
import java.util.TimerTask;

import name.cpr.VideoEnabledWebChromeClient;
import name.cpr.VideoEnabledWebView;
import static java.lang.Math.abs;

/**
 * Created by ayalgenzer on 14/12/17.
 */

public class VideoActivity extends AppCompatActivity implements SensorEventListener {

    private VideoEnabledWebView webView;
    private VideoEnabledWebChromeClient webChromeClient;


    // buttons

    Button btnVideo;
    ImageButton btnrecord;
    ImageButton btnstop;
    ImageButton btndown;
    ImageButton btnup;
    ImageButton btnright;
    ImageButton btnleft;


    TextView LastMessage;
    TextView mode_msg;
    TextView rectime;
    Switch mode;
    boolean initialize = true;

    private boolean downpress = false;
    private boolean dreleas = true;

    //constants
    private static boolean gyro = false;
    private final String move_topic = "MovePiCam";
    private final String record_topic = "StartRecord";
    private final String stop_topic = "StopRecord";
    private final String upload_topic = "UploadSuccess";


    Timer T;
    int count = 0;
    String time;

    //gyro fields:
    // System sensor manager instance.
    private SensorManager mSensorManager;

    // Accelerometer and magnetometer sensors, as retrieved from the
    // sensor manager.
    private Sensor mSensorAccelerometer;
    private Sensor mSensorMagnetometer;

    // Current data from accelerometer & magnetometer.  The arrays hold values
    // for X, Y, and Z.
    private float[] mAccelerometerData = new float[3];
    private float[] mMagnetometerData = new float[3];

    // System display. Need this for determining rotation.
    private Display mDisplay;

    // Very small values for the accelerometer (on all three axes) should
    // be interpreted as 0. This value is the amount of acceptable
    // non-zero drift.
    private static final float VALUE_DRIFT = 0.05f;
    float pitch = (float) 45.0;
    float roll = (float) 45.0;
    float first_pitch = (float) 45.0;
    float first_roll = (float) 45.0;
    float limit1 = (float) 45.0;
    float limit2 = (float) 45.0;
    boolean first = true;
    float lastpitch = (float)45.0;
    float lastroll =(float)45.0;
    long curr_time = System.currentTimeMillis() ;
    long btn_currtime;
    long btn_lasttime = System.currentTimeMillis() ;;

    Mqtt mqtt = new Mqttvideo();

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(com.ayalgenzer.security_cam.R.layout.activity_video);
        getWindow().getDecorView().setBackgroundColor(Color.BLACK);


        // Save the web view
        webView = (VideoEnabledWebView)findViewById(cpr.name.videoenabledwebview.R.id.webView);

        mqtt.connect();


        btnVideo = (Button) findViewById(R.id.btnvideos);
        btnVideo.setOnClickListener(videos);
        btnVideo.setEnabled(true);

        btnrecord = (ImageButton) findViewById(R.id.btnrecord);
        btnrecord.setOnClickListener(record);
        btnrecord.setEnabled(true);

        btnstop = (ImageButton) findViewById(R.id.btnstop);
        btnstop.setOnClickListener(stop);
        btnstop.setEnabled(false);

        btnup = (ImageButton) findViewById(R.id.btnup);
        btnup.setOnClickListener(up);
        btnup.setEnabled(true);

        btndown = (ImageButton) findViewById(R.id.btndown);
        btndown.setOnClickListener(down);
        //btndown.setOnLongClickListener((View.OnLongClickListener) downlong);
        //btndown.setOnTouchListener((OnTouchListener) downtouch);
        btndown.setEnabled(true);

        btnleft = (ImageButton) findViewById(R.id.btnleft);
        btnleft.setOnClickListener(left);
        btnleft.setEnabled(true);

        btnright = (ImageButton) findViewById(R.id.btnright);
        btnright.setOnClickListener(right);
        btnright.setEnabled(true);


        LastMessage = (TextView) findViewById(R.id.message);
        rectime = (TextView) findViewById(R.id.rectime);
        mode_msg = (TextView) findViewById(R.id.modestr);
        mode = (Switch) findViewById(R.id.btnmode);
        mode.setChecked(false);
        mode.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (isChecked){
                    mode_msg.setText("GYRO");
                    first = true;
                    mqtt.publish(move_topic , "45 45");
                    gyro = true;
                    btndown.setEnabled(false);
                    btnup.setEnabled(false);
                    btnleft.setEnabled(false);
                    btnright.setEnabled(false);

                }
                else {
                    mode_msg.setText("ARROWS");
                    gyro = false;
                    btndown.setEnabled(true);
                    btnup.setEnabled(true);
                    btnleft.setEnabled(true);
                    btnright.setEnabled(true);
                }
            }
        });


        // Initialize the VideoEnabledWebChromeClient and set event handlers
        View nonVideoLayout = findViewById(cpr.name.videoenabledwebview.R.id.nonVideoLayout); // Your own view, read class comments
        ViewGroup videoLayout = (ViewGroup)findViewById(cpr.name.videoenabledwebview.R.id.videoLayout); // Your own view, read class comments
        //noinspection all
        View loadingView = getLayoutInflater().inflate(cpr.name.videoenabledwebview.R.layout.view_loading_video, null); // Your own view, read class comments


        // gyro integration starts here

        // Get accelerometer and magnetometer sensors from the sensor manager.
        // The getDefaultSensor() method returns null if the sensor
        // is not available on the device.
        mSensorManager = (SensorManager) getSystemService(
                Context.SENSOR_SERVICE);
        mSensorAccelerometer = mSensorManager.getDefaultSensor(
                Sensor.TYPE_ACCELEROMETER);
        mSensorMagnetometer = mSensorManager.getDefaultSensor(
                Sensor.TYPE_MAGNETIC_FIELD);

        // Get the display from the window manager (for rotation).
        WindowManager wm = (WindowManager) getSystemService(WINDOW_SERVICE);
        mDisplay = wm.getDefaultDisplay();
        //mqtt.publish(move_topic , "45 45");


        webChromeClient = new VideoEnabledWebChromeClient(nonVideoLayout, videoLayout, loadingView, webView) // See all available constructors...
        {
            // Subscribe to standard events, such as onProgressChanged()...
            @Override
            public void onProgressChanged(WebView view, int progress)
            {
                // Your code...
            }
        };


        webChromeClient.setOnToggledFullscreen(new VideoEnabledWebChromeClient.ToggledFullscreenCallback()
        {
            @Override
            public void toggledFullscreen(boolean fullscreen)
            {
                // Your code to handle the full-screen change, for example showing and hiding the title bar. Example:
                if (fullscreen)
                {
                    WindowManager.LayoutParams attrs = getWindow().getAttributes();
                    attrs.flags |= WindowManager.LayoutParams.FLAG_FULLSCREEN;
                    attrs.flags |= WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON;
                    getWindow().setAttributes(attrs);
                    if (android.os.Build.VERSION.SDK_INT >= 14)
                    {
                        //noinspection all
                        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LOW_PROFILE);
                    }
                }
                else
                {
                    WindowManager.LayoutParams attrs = getWindow().getAttributes();
                    attrs.flags &= ~WindowManager.LayoutParams.FLAG_FULLSCREEN;
                    attrs.flags &= ~WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON;
                    getWindow().setAttributes(attrs);
                    if (android.os.Build.VERSION.SDK_INT >= 14)
                    {
                        //noinspection all
                        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_VISIBLE);
                    }
                }

            }
        });
        webView.setWebChromeClient(new VideoEnabledWebChromeClient(){
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    request.grant(request.getResources());
                }
            }
        });
        // Call private class InsideWebViewClient
        webView.setWebViewClient(new InsideWebViewClient());

        // Navigate anywhere you want, but consider that this classes have only been tested on YouTube's mobile site
        webView.loadUrl("https://52.87.156.146/SecCam.html");
        // webView.loadUrl("https://sport5.co.il");


    }

    /**
     * Listeners for the sensors are registered in this callback so that
     * they can be unregistered in onStop().
     */
    @Override
    protected void onStart() {
        super.onStart();

        // Listeners for the sensors are registered in this callback and
        // can be unregistered in onStop().
        //
        // Check to ensure sensors are available before registering listeners.
        // Both listeners are registered with a "normal" amount of delay
        // (SENSOR_DELAY_NORMAL).
        if (mSensorAccelerometer != null) {
            mSensorManager.registerListener(this, mSensorAccelerometer,
                    SensorManager.SENSOR_DELAY_NORMAL);
        }
        if (mSensorMagnetometer != null) {
            mSensorManager.registerListener(this, mSensorMagnetometer,
                    SensorManager.SENSOR_DELAY_NORMAL);
        }

    }

    @Override
    protected void onStop() {
        super.onStop();

        // Unregister all sensor listeners in this callback so they don't
        // continue to use resources when the app is stopped.
        mSensorManager.unregisterListener(this);
    }

    @Override
    public void onSensorChanged(SensorEvent sensorEvent) {

        if (gyro) {
            // The sensor type (as defined in the Sensor class).
            int sensorType = sensorEvent.sensor.getType();

            // The sensorEvent object is reused across calls to onSensorChanged().
            // clone() gets a copy so the data doesn't change out from under us
            switch (sensorType) {
                case Sensor.TYPE_ACCELEROMETER:
                    mAccelerometerData = sensorEvent.values.clone();
                    break;
                case Sensor.TYPE_MAGNETIC_FIELD:
                    mMagnetometerData = sensorEvent.values.clone();
                    break;
                default:
                    return;
            }
            // Compute the rotation matrix: merges and translates the data
            // from the accelerometer and magnetometer, in the device coordinate
            // system, into a matrix in the world's coordinate system.
            //
            // The second argument is an inclination matrix, which isn't
            // used in this example.
            float[] rotationMatrix = new float[9];
            boolean rotationOK = SensorManager.getRotationMatrix(rotationMatrix,
                    null, mAccelerometerData, mMagnetometerData);

            // Remap the matrix based on current device/activity rotation.
            float[] rotationMatrixAdjusted = new float[9];
            switch (mDisplay.getRotation()) {
                case Surface.ROTATION_0:
                    rotationMatrixAdjusted = rotationMatrix.clone();
                    break;
                case Surface.ROTATION_90:
                    SensorManager.remapCoordinateSystem(rotationMatrix,
                            SensorManager.AXIS_Y, SensorManager.AXIS_MINUS_X,
                            rotationMatrixAdjusted);
                    break;
                case Surface.ROTATION_180:
                    SensorManager.remapCoordinateSystem(rotationMatrix,
                            SensorManager.AXIS_MINUS_X, SensorManager.AXIS_MINUS_Y,
                            rotationMatrixAdjusted);
                    break;
                case Surface.ROTATION_270:
                    SensorManager.remapCoordinateSystem(rotationMatrix,
                            SensorManager.AXIS_MINUS_Y, SensorManager.AXIS_X,
                            rotationMatrixAdjusted);
                    break;
            }

            // Get the orientation of the device (azimuth, pitch, roll) based
            // on the rotation matrix. Output units are radians.
            float orientationValues[] = new float[3];
            if (rotationOK) {
                SensorManager.getOrientation(rotationMatrixAdjusted,
                        orientationValues);
            }
            if (true == first) {
                first_pitch = (float) (orientationValues[1] * 57.295779513);
                if (first_pitch < 0) first_pitch = first_pitch * -1;
                else first_pitch = 360 - first_pitch;

                first_roll = (float) (orientationValues[2] * 57.295779513);
                limit1 = (float) first_roll + 180 + 45;
                if (limit1 < 0) limit1 = limit1 + 360;
                if (limit1 > 360) limit1 = limit1 % 360;
                limit2 = (float) first_roll + 180 - 45;
                if (limit2 < 0) limit2 = limit2 + 360;
                if (limit2 > 360) limit2 = limit2 % 360;

                if (first_roll > 90) first_roll = 180 - first_roll;
                if (first_roll < -90) first_roll = -(180 + first_roll);

                if (first_roll < 0) first_roll = first_roll * -1;
                else first_roll = 360 - first_roll;
                lastpitch = first_pitch;
                pitch = first_pitch;
                lastroll = first_roll;
                roll = first_roll;
                if ((first_roll > 0) && (first_roll < 360)) first = false;
            }
            float tmplastpitch = pitch;
            float tmplastroll = roll;

            float min, max = 0;
            if (limit1 > limit2) {
                max = limit1;
                min = limit2;
            } else {
                max = limit2;
                min = limit1;
            }


            // Pull out the individual values from the array.
            float azimuth = (float) (orientationValues[0] * 57.295779513);

            pitch = (float) (orientationValues[1] * 57.295779513);
            float orig_pitch = pitch - first_pitch;
            if (pitch < 0) pitch = pitch * -1;
            else pitch = 360 - pitch;
            pitch = pitch - first_pitch + 45;
            if (pitch < 0) pitch = pitch + 360;
            if (pitch > 360) pitch = pitch % 360;

            roll = (float) (orientationValues[2] * 57.295779513);

            float limitcurr = roll + 180;
            if (limitcurr < 0) limitcurr = limitcurr + 360;
            if (limitcurr > 360) limitcurr = limitcurr % 360;

            //if ((limitcurr < max) && (limitcurr > min))
            //    lastroll = tmplastroll;

            if (roll > 90) roll = 180 - roll;
            if (roll < -90) roll = -(180 + roll);

            if (roll < 0) roll = roll * -1;
            else roll = 360 - roll;
            float orig_roll = roll - first_roll;
            roll = roll - first_roll + 45;
            if (roll < 0) roll = roll + 360;
            if (roll > 360) roll = roll % 360;

            if (((abs(orig_pitch) < 45)) || ((abs(orig_roll) < 90) || (abs(orig_roll) > 270))) {
                String s = null;
                if ((limitcurr < max) && (limitcurr > min))
                    s = Float.toString((90 - roll));
                else if (limitcurr > max) s = "90";
                else s = "0";
                if ((pitch >= 0) && (pitch <= 90)) s = s + " " + Float.toString(pitch);
                else if ((pitch > 90) && (pitch < 180)) s = s + " 90";
                else s = s + " 0";
                //s = /*Float.toString((90 - roll)) +*/ "45 " +Float.toString(pitch);
                long last_time = curr_time;
                long curr_time = System.currentTimeMillis();
                if (curr_time - last_time > 200)
                    if ((abs(pitch - lastpitch) > 4.0) || (abs(roll - lastroll) > 6.0)) {
                        mqtt.publish(move_topic, s);
                        lastpitch = tmplastpitch;
                        lastroll = tmplastroll;
                    }
            }

            // Pitch and roll values that are close to but not 0 cause the
            // animation to flash a lot. Adjust pitch and roll to 0 for very
            // small values (as defined by VALUE_DRIFT).
            if (abs(pitch) < VALUE_DRIFT) {
                pitch = 0;
            }
            if (abs(roll) < VALUE_DRIFT) {
                roll = 0;
            }
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {

    }


    private class InsideWebViewClient extends WebViewClient {
        @Override
        // Force links to be opened inside WebView and not in Default Browser
        // Thanks http://stackoverflow.com/a/33681975/1815624
        public boolean shouldOverrideUrlLoading(WebView view, String url) {
            view.loadUrl(url);
            return true;
        }

        @Override
        public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
            handler.proceed(); // Ignore SSL certificate errors
        }


    }

    @Override
    public void onBackPressed()
    {
        // Notify the VideoEnabledWebChromeClient, and handle it ourselves if it doesn't handle it
        if (!webChromeClient.onBackPressed())
        {
            if (webView.canGoBack())
            {
                webView.goBack();
            }
            else
            {
                // Standard back button implementation (for example this could close the app)
                super.onBackPressed();
            }
        }
    }

    View.OnClickListener videos = new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            if (initialize) {
                init();
                initialize = false;
            }
            Intent intent;
            intent = new Intent(VideoActivity.this, com.amazonaws.demo.s3transferutility.S3_MainActivity.class);
            startActivity(intent);
        }
    };

    View.OnClickListener record = new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            if (initialize) {
                init();
                initialize = false;
            }
            count = 0;
            //mqtt.publish(record_topic, "recording...");
            mqtt.publish(record_topic, "record");
            btnrecord.setEnabled(false);
            btnstop.setEnabled(true);
            T = new Timer();
            T.scheduleAtFixedRate(new TimerTask() {
                @Override
                public void run() {
                    runOnUiThread(new Runnable()
                    {
                        @Override
                        public void run()
                        {
                            time = String.format("%02d:%02d", count / 100, count % 100);
                            rectime.setText("recording... " + time);
                            count++;
                        }
                    });
                }
            }, 1000, 1000);
        }
    };

    View.OnClickListener stop = new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            if (initialize) {
                init();
                initialize = false;
            }
            mqtt.publish(stop_topic, "stop");
            btnstop.setEnabled(false);
            rectime.setText("recorded: " + time);
            T.cancel();
        }
    };

    View.OnClickListener down = new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            if (initialize) {
                init();
                initialize = false;
            }
            mqtt.publish(move_topic, "Down");
        }
    };


    View.OnClickListener up = new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            if (initialize) {
                init();
                initialize = false;
            }
            mqtt.publish(move_topic, "Up");
        }
    };

    View.OnClickListener left = new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            if (initialize) {
                init();
                initialize = false;
            }
            mqtt.publish(move_topic, "Left");
        }
    };

    View.OnClickListener right = new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            if (initialize) {
                init();
                initialize = false;
            }
            mqtt.publish(move_topic, "Right");
        }
    };

    public void init(){
        mqtt.publish(move_topic , "45 45");
        mqtt.subscribe(move_topic);
        mqtt.subscribe(stop_topic);
        mqtt.subscribe(record_topic);
        mqtt.subscribe(upload_topic);
    }





    public  class Mqttvideo extends Mqtt{

        @Override
        public void subscribe(String top){
            final String topic = top;

            Log.d(LOG_TAG, "topic = " + topic);
            try {
                mqttManager.subscribeToTopic(topic, AWSIotMqttQos.QOS0,
                        new AWSIotMqttNewMessageCallback() {
                            @Override
                            public void onMessageArrived(final String topic, final byte[] data) {
                                runOnUiThread(new Runnable() {
                                    String message;
                                    @Override
                                    public void run() {
                                        try {
                                            message = new String(data, "UTF-8");
                                            Log.d(LOG_TAG, "Message arrived:");
                                            Log.d(LOG_TAG, "   Topic: " + topic);
                                            Log.d(LOG_TAG, " Message: " + message);
                                            if (message.equals("Video uploaded")){
                                                btnrecord.setEnabled(true);
                                                rectime.setText("");

                                            }
                                            LastMessage.setText(message);
                                        } catch (UnsupportedEncodingException e) {
                                            Log.e(LOG_TAG, "Message encoding error.", e);
                                        }
                                    }
                                });
                            }
                        });
            } catch (Exception e) {
                Log.e(LOG_TAG, "Subscription error.", e);
            }

        }
    }

}
