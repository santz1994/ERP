package com.qutykarunia.erp

import android.app.Application
import dagger.hilt.android.HiltAndroidApp
import timber.log.Timber

@HiltAndroidApp
class ERPApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        initLogging()
        initializeApp()
    }

    private fun initLogging() {
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }
    }

    private fun initializeApp() {
        Timber.d("ERP Application initialized")
    }
}
