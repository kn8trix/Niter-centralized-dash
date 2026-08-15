// Root build file — declares plugin versions only; the :app module applies them.
plugins {
    id("com.android.application") version "8.10.1" apply false
    id("org.jetbrains.kotlin.android") version "2.0.21" apply false
    // Firebase (FCM push). Applied conditionally in :app — only when the
    // project's google-services.json is present — so the build never breaks
    // for a checkout that hasn't wired up a Firebase project yet.
    id("com.google.gms.google-services") version "4.4.2" apply false
}
