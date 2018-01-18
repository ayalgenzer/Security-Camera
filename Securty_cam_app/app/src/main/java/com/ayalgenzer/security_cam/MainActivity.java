package com.ayalgenzer.security_cam;

import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.support.v7.app.AppCompatActivity;

import com.amazonaws.youruserpools.CognitoMainActivity;


public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        getWindow().getDecorView().setBackgroundColor(Color.BLACK);
        Handler mHandler = new Handler();
        mHandler.postDelayed(new Runnable() {

            @Override
            public void run() {
                Intent intent = new Intent(com.ayalgenzer.security_cam.MainActivity.this, CognitoMainActivity.class);
                startActivity(intent);
            }

        }, 3500L);


    }

}


