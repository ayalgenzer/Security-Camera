/*
 * Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */

package com.amazonaws.demo.s3transferutility;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import com.amazonaws.demo.s3transferutility.R;

/*
 * This is the beginning screen that lets the user select if they want to upload or download
 */
public class S3_MainActivity extends Activity {

    private Button btnDownload;
    private Button btnUpload;
    private Button btnDownload_2;
    private Button btnUpload_2;

    public static  String bucket_name ;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_s3_main);
        getWindow().getDecorView().setBackgroundColor(Color.BLACK);
        initUI();
    }

    private void initUI() {
        btnDownload = (Button) findViewById(R.id.buttonDownloadMain);
        btnUpload = (Button) findViewById(R.id.buttonUploadMain);
        btnDownload_2 = (Button) findViewById(R.id.buttonDownloadMain_2);
        btnUpload_2 = (Button) findViewById(R.id.buttonUploadMain_2);

        btnDownload.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View arg0) {
                bucket_name = "ayalgenzer";
                Intent intent = new Intent(S3_MainActivity.this, DownloadActivity.class);
                startActivity(intent);
            }
        });

        btnUpload.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View arg0) {
                bucket_name = "ayalgenzer";
                Intent intent = new Intent(S3_MainActivity.this, UploadActivity.class);
                startActivity(intent);
            }
        });

        btnDownload_2.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View arg0) {
                bucket_name = "savedvids";
                Intent intent = new Intent(S3_MainActivity.this, DownloadActivity.class);
                startActivity(intent);
            }
        });

        btnUpload_2.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View arg0) {
                bucket_name = "savedvids";
                Intent intent = new Intent(S3_MainActivity.this, UploadActivity.class);
                startActivity(intent);
            }
        });
    }
}
