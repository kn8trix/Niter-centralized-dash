package com.niterhub.dash

import android.content.Context
import android.webkit.CookieManager
import androidx.work.Constraints
import androidx.work.ExistingWorkPolicy
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.Worker
import androidx.work.WorkerParameters
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.TimeUnit

/**
 * Background emergency watcher — the Firebase-free delivery path.
 *
 * The native push channel (FCM) only works once ``google-services.json`` is
 * added, so this worker polls the backend's public emergency endpoint
 * (``/api/emergency/active/``) using the session cookie the WebView already
 * stored, and turns the live state into native behaviour:
 *
 *  - a NEW active alert → high-priority BigPicture notification + the looping
 *    alarm-channel siren (``NotificationHelper.notifyEmergency``), so the
 *    phone rings even in silent mode and even when the app is backgrounded;
 *  - the alert resolved (``alert: null``) → siren stopped + notification
 *    cleared;
 *  - network / auth failure → state untouched (a transient error must never
 *    silence an active emergency).
 *
 * Each run re-schedules the next poll (~30s) as one-time work, so the loop
 * survives process death. The notification's **Stop Siren** action calls
 * [EmergencyPollWorker.silenceCurrent] so the same alert is not re-triggered
 * on the next tick; a brand-new alert id re-arms automatically.
 */
class EmergencyPollWorker(context: Context, params: WorkerParameters) : Worker(context, params) {

    companion object {
        private const val TAG = "emergency-poll"

        /** Keep in sync with [MainActivity.startUrl]. */
        private const val BASE_URL = "https://niter-centralized-dash.onrender.com"
        private const val ACTIVE_URL = "$BASE_URL/api/emergency/active/"

        private const val PREFS = "emergency_poll"
        private const val KEY_LAST_ALERT_ID = "last_alert_id"
        private const val KEY_SILENCED_ALERT_ID = "silenced_alert_id"

        private const val POLL_SECONDS = 30L

        /** (Re)start the polling loop — idempotent, cheap, safe to call on launch. */
        fun schedule(context: Context) {
            val request = OneTimeWorkRequestBuilder<EmergencyPollWorker>()
                .setInitialDelay(15, TimeUnit.SECONDS)
                .setConstraints(
                    Constraints.Builder()
                        .setRequiredNetworkType(NetworkType.CONNECTED)
                        .build()
                )
                .addTag(TAG)
                .build()
            WorkManager.getInstance(context)
                .enqueueUniqueWork(TAG, ExistingWorkPolicy.REPLACE, request)
        }

        /** Remember "the user silenced the current alert" so polls don't re-trigger it. */
        fun silenceCurrent(context: Context) {
            val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            val last = prefs.getString(KEY_LAST_ALERT_ID, null)
            if (last != null) {
                prefs.edit().putString(KEY_SILENCED_ALERT_ID, last).apply()
            }
        }
    }

    /** Result of one poll — distinguishes "explicitly no alert" from "couldn't tell". */
    private sealed class PollResult {
        data class Success(val alert: JSONObject?) : PollResult()
        object Unavailable : PollResult()
    }

    override fun doWork(): Result {
        NotificationHelper.ensureChannels(applicationContext)
        val prefs = applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

        when (val result = fetchActiveAlert()) {
            is PollResult.Success -> {
                val alert = result.alert
                if (alert == null) {
                    // Explicitly resolved — clear everything, re-arm for the next alert.
                    NotificationHelper.stopSiren(applicationContext)
                    prefs.edit()
                        .remove(KEY_LAST_ALERT_ID)
                        .remove(KEY_SILENCED_ALERT_ID)
                        .apply()
                } else {
                    handleActiveAlert(alert, prefs)
                }
            }
            is PollResult.Unavailable -> {
                // Network blip or logged-out session — leave the current state
                // untouched so an active emergency is never silenced by a
                // transient failure.
            }
        }

        // Keep watching.
        schedule(applicationContext)
        return Result.success()
    }

    private fun handleActiveAlert(alert: JSONObject, prefs: android.content.SharedPreferences) {
        val id = alert.optLong("id", -1L)
        val idKey = id.toString()
        val silencedId = prefs.getString(KEY_SILENCED_ALERT_ID, null)
        val lastNotifiedId = prefs.getString(KEY_LAST_ALERT_ID, null)

        if (idKey == silencedId) {
            // The user hit "Stop Siren" on this exact alert — do not re-trigger.
            return
        }
        if (idKey == lastNotifiedId) {
            // Already alerted on this alert id — never re-notify or re-siren.
            return
        }

        prefs.edit()
            .putString(KEY_LAST_ALERT_ID, idKey)
            .remove(KEY_SILENCED_ALERT_ID)
            .apply()

        val title = alert.optString("title").takeIf { it.isNotBlank() }
            ?: "EMERGENCY ALERT"
        val body = alert.optString("message").takeIf { it.isNotBlank() }
            ?: "A campus emergency has been declared."
        val playAlarm = alert.optBoolean("play_alarm_sound", false)

        NotificationHelper.notifyEmergency(
            applicationContext,
            "\uD83D\uDEA8 $title",
            body,
            null, // banner: the backend serializes no image URL — bundled banner is used.
            playAlarm,
        )
    }

    /** GET /api/emergency/active/ with the WebView's session cookie (same-origin). */
    private fun fetchActiveAlert(): PollResult {
        val cookie = try {
            CookieManager.getInstance().getCookie(ACTIVE_URL)
        } catch (_: Exception) {
            null
        }
        if (cookie.isNullOrEmpty()) return PollResult.Unavailable

        return try {
            val connection = (URL(ACTIVE_URL).openConnection() as HttpURLConnection).apply {
                connectTimeout = 10_000
                readTimeout = 10_000
                requestMethod = "GET"
                setRequestProperty("Cookie", cookie)
                setRequestProperty("Accept", "application/json")
            }
            try {
                if (connection.responseCode != HttpURLConnection.HTTP_OK) {
                    // Redirect to login (logged out) or server error — can't tell state.
                    return PollResult.Unavailable
                }
                val body = connection.inputStream.bufferedReader().use { it.readText() }
                val json = JSONObject(body)
                if (json.optString("status") != "success") return PollResult.Unavailable
                PollResult.Success(json.optJSONObject("alert"))
            } finally {
                connection.disconnect()
            }
        } catch (_: Exception) {
            PollResult.Unavailable
        }
    }
}
