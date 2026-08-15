plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

// FCM push: the google-services plugin generates Firebase resources from
// google-services.json. It is applied ONLY when that file exists in the app
// module, so a checkout without a Firebase project keeps building/running
// unchanged (the FCM service is inert until the file is dropped in).
if (file("google-services.json").exists()) {
    apply(plugin = "com.google.gms.google-services")
}

android {
    namespace = "com.niterhub.dash"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.niterhub.dash"
        minSdk = 26
        targetSdk = 36
        versionCode = 2
        versionName = "2.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("androidx.activity:activity-ktx:1.9.3")

    // Firebase Cloud Messaging — emergency + campus push notifications.
    // Inert without google-services.json; everything FCM-related is guarded.
    implementation("com.google.firebase:firebase-messaging:24.1.0")
}
