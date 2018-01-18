package com.ayalgenzer.security_cam;

/**
 * Created by ayalgenzer on 02/01/18.
 */
import android.app.Application;
import android.content.Context;


public class MyApplication extends Application {

    private static Context mContext;

    @Override
    public void onCreate() {
        super.onCreate();
        mContext = getApplicationContext();
    }

    public static Context getContext() {
        return mContext;
    }
}