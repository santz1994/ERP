"""
build.gradle.kts (Project Root)
Gradle configuration for Android ERP App
Min SDK: 25 (Android 7.1.2)
Target SDK: 34 (Android 14)
"""

plugins {
    id("com.android.application") version "8.2.0" apply false
    id("com.android.library") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.10" apply false
    id("com.google.dagger.hilt.android") version "2.46.1" apply false
    id("com.google.gms.google-services") version "4.4.0" apply false
}

tasks.register<Delete>("clean") {
    delete(rootProject.buildDir)
}
