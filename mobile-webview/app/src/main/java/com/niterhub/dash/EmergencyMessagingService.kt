package com.niterhub.dash

import android.content.Context
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage

/**
 * Firebase Cloud Messaging service for the Niter Campus Hub wrapper.
 *
 * The backend (``services/emergency_push.py``) broadcasts campus emergencies
 * to the ``emergency_alerts`` topic; this service:
 *
 *  - subscribes every install to that topic on first launch (token refresh),
 *  - turns ``EMERGENCY_ALERT`` data messages into high-priority native
 *    notifications with a picture banner + looping siren,
 *  - renders any other push as a normal campus notification,
 *  - stops the siren / clears the alert via the notification's **Stop Siren**
 *    action (``ACTION_STOP_SIREN``) or when the user opens the app.
 *
 * The whole class is Firebase-optional: without ``google-services.json`` the
 * service is simply never invoked and every FCM call is guarded, so the app
 * builds and runs exactly as before until the Firebase project is wired up
 * (see ``mobile-webview/README.md``).
 */
class EmergencyMessagingService : FirebaseMessagingService() {

    companion object {
        private const val TOPIC_EMERGENCY = "emergency_alerts"

        const val DATA_TYPE = "type"
        const val TYPE_EMERGENCY = "EMERGENCY_ALERT"
        const val TYPE_RESOLVED = "EMERGENCY_RESOLVED"
        const val DATA_SEVERITY = "severity"
        const val DATA_PLAY_SIREN = "play_alarm_sound"
        const val DATA_BANNER = "banner"

        const val ACTION_STOP_SIREN = "com.niterhub.dash.action.STOP_SIREN"

        /** Subscribe this install to emergency broadcasts (idempotent). */
        fun subscribe(context: Context) {
            try {
                com.google.firebase.messaging.FirebaseMessaging.getInstance()
                    .subscribeToTopic(TOPIC_EMERGENCY)
            } catch (_: IllegalStateException) {
                // Firebase not configured (no google-services.json) — skip.
            }
        }

        /** Stop the looping siren + clear the alert (called when the app opens). */
        fun stopSiren(context: Context) {
            NotificationHelper.stopSiren(context)
        }
    }

    override fun onNewToken(token: String) {
        super.onNewToken(token)
        subscribe(this)
    }

    override fun onMessageReceived(message: RemoteMessage) {
        val data = message.data
        val type = data[DATA_TYPE]

        when (type) {
            TYPE_EMERGENCY -> {
                val title = message.notification?.title
                    ?: data["title"]
                    ?: getString(R.string.channel_emergency)
                val body = message.notification?.body
                    ?: data["body"]
                    ?: getString(R.string.channel_emergency_desc)
                val playSiren = data[DATA_PLAY_SIREN]?.toBoolean() ?: false
                NotificationHelper.ensureChannels(this)
                NotificationHelper.notifyEmergency(
                    this,
                    title,
                    body,
                    data[DATA_BANNER],
                    playSiren,
                )
            }

            TYPE_RESOLVED -> NotificationHelper.stopSiren(this)

            else -> {
                // General campus / pharmacy push — render as a normal
                // notification when the app is not in the foreground.
                val title = message.notification?.title
                    ?: data["title"]
                    ?: getString(R.string.app_name)
                val body = message.notification?.body
                    ?: data["body"]
                    ?: getString(R.string.channel_general_desc)
                NotificationHelper.ensureChannels(this)
                NotificationHelper.notifyGeneral(this, title, body)
            }
        }
    }

    // NOTE: ``onStartCommand`` is NOT overridden here — firebase-messaging
    // 24.x makes it final on ``EnhancedIntentService``. The notification's
    // Stop Siren action routes through ``SirenControlReceiver`` instead.
}
