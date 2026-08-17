package com.niterhub.dash

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

/**
 * Handles the emergency notification's **Stop Siren** action.
 *
 * The Firebase Messaging base class (`EnhancedIntentService` in firebase-
 * messaging 24.x) marks `onStartCommand` as final, so the emergency service
 * can no longer intercept explicit intents. Notification actions therefore
 * route here via `PendingIntent.getBroadcast` — the receiver just stops the
 * looping siren and clears the alert.
 */
class SirenControlReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == EmergencyMessagingService.ACTION_STOP_SIREN) {
            NotificationHelper.stopSiren(context)
        }
    }
}
