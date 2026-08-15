package com.niterhub.dash

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.drawable.BitmapDrawable
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.net.Uri
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.Executors

/**
 * Native notification plumbing for the Niter Campus Hub wrapper.
 *
 * Two channels:
 *  - ``emergency_alerts`` — IMPORTANCE_HIGH, plays the bundled siren
 *    (``res/raw/emergency_siren.wav``) and vibrates, so campus emergencies
 *    break through silent mode / DND.
 *  - ``general_alerts`` — normal campus + pharmacy notifications.
 *
 * Emergency alerts render as **picture banners** (BigPictureStyle): the push's
 * ``banner`` URL is fetched when present, otherwise the bundled
 * ``drawable/emergency_banner.png`` is used. A **Stop Siren** action hands
 * control back to [EmergencyMessagingService], which stops the looping siren
 * and clears the alert.
 *
 * Every entry point is guarded so the app works identically when Firebase is
 * not configured (no ``google-services.json`` yet) — only push delivery is
 * inert in that case.
 */
object NotificationHelper {

    const val CHANNEL_EMERGENCY = "emergency_alerts"
    const val CHANNEL_GENERAL = "general_alerts"

    private const val EMERGENCY_NOTIFICATION_ID = 1001

    private val sirenExecutor = Executors.newSingleThreadExecutor()
    private val bannerExecutor = Executors.newSingleThreadExecutor()
    private var sirenPlayer: MediaPlayer? = null

    // ------------------------------------------------------------------
    // Channels
    // ------------------------------------------------------------------

    /** Create both notification channels (idempotent; safe to call every launch). */
    fun ensureChannels(context: Context) {
        val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        val sirenUri = Uri.parse(
            "android.resource://${context.packageName}/${R.raw.emergency_siren}"
        )
        val emergency = NotificationChannel(
            CHANNEL_EMERGENCY,
            context.getString(R.string.channel_emergency),
            NotificationManager.IMPORTANCE_HIGH,
        ).apply {
            description = context.getString(R.string.channel_emergency_desc)
            enableVibration(true)
            vibrationPattern = longArrayOf(0, 500, 300, 500, 300, 900)
            setSound(sirenUri, AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_ALARM)
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .build())
            lockscreenVisibility = Notification.VISIBILITY_PUBLIC
        }
        manager.createNotificationChannel(emergency)

        val general = NotificationChannel(
            CHANNEL_GENERAL,
            context.getString(R.string.channel_general),
            NotificationManager.IMPORTANCE_DEFAULT,
        ).apply {
            description = context.getString(R.string.channel_general_desc)
        }
        manager.createNotificationChannel(general)
    }

    // ------------------------------------------------------------------
    // Emergency alert (siren + picture banner)
    // ------------------------------------------------------------------

    /**
     * Show the emergency alert notification.
     *
     * @param bannerUrl optional picture URL from the push ``banner`` field;
     *        falls back to the bundled emergency banner when absent.
     * @param playSiren loop the siren while the notification is active.
     */
    fun notifyEmergency(
        context: Context,
        title: String,
        body: String,
        bannerUrl: String?,
        playSiren: Boolean,
    ) {
        if (playSiren) startSirenLoop(context)

        val contentIntent = PendingIntent.getActivity(
            context, 0,
            Intent(context, MainActivity::class.java)
                .addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val stopSirenIntent = PendingIntent.getService(
            context, 1,
            Intent(context, EmergencyMessagingService::class.java)
                .setAction(EmergencyMessagingService.ACTION_STOP_SIREN),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )

        val builder = NotificationCompat.Builder(context, CHANNEL_EMERGENCY)
            .setSmallIcon(R.drawable.ic_stat_alert)
            .setContentTitle(title)
            .setContentText(body)
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setAutoCancel(true)
            .setContentIntent(contentIntent)
            .addAction(
                R.drawable.ic_stat_alert,
                context.getString(R.string.notif_stop_siren),
                stopSirenIntent,
            )

        val fallback = (context.getDrawable(R.drawable.emergency_banner) as? BitmapDrawable)?.bitmap
        val url = bannerUrl?.trim().takeIf { it.isNotEmpty() }

        val notify: (Bitmap?) -> Unit = { picture ->
            builder.setStyle(
                NotificationCompat.BigPictureStyle()
                    .bigPicture(picture)
                    .setBigContentTitle(title)
                    .setSummaryText(body)
            )
            try {
                NotificationManagerCompat.from(context).notify(
                    EMERGENCY_NOTIFICATION_ID, builder.build(),
                )
            } catch (_: SecurityException) {
                // POST_NOTIFICATIONS not granted — the alert still reaches the
                // app shell (banner + siren) when the WebView is open.
            }
        }

        if (url != null) {
            bannerExecutor.execute {
                val picture = fetchBitmap(url) ?: fallback
                android.os.Handler(context.mainLooper).post { notify(picture) }
            }
        } else {
            notify(fallback)
        }
    }

    // ------------------------------------------------------------------
    // General notification (non-emergency push)
    // ------------------------------------------------------------------

    fun notifyGeneral(context: Context, title: String, body: String) {
        val contentIntent = PendingIntent.getActivity(
            context, 0,
            Intent(context, MainActivity::class.java)
                .addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val notification = NotificationCompat.Builder(context, CHANNEL_GENERAL)
            .setSmallIcon(R.drawable.ic_stat_alert)
            .setContentTitle(title)
            .setContentText(body)
            .setStyle(NotificationCompat.BigTextStyle().bigText(body))
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setAutoCancel(true)
            .setContentIntent(contentIntent)
            .build()
        try {
            NotificationManagerCompat.from(context).notify(
                (System.currentTimeMillis() % 10000).toInt() + 2000, notification,
            )
        } catch (_: SecurityException) {
            // Notification permission not granted — skip silently.
        }
    }

    fun cancelEmergency(context: Context) {
        NotificationManagerCompat.from(context).cancel(EMERGENCY_NOTIFICATION_ID)
    }

    // ------------------------------------------------------------------
    // Siren loop
    // ------------------------------------------------------------------

    /** Start looping the bundled siren (replaces any active loop). */
    fun startSirenLoop(context: Context) {
        sirenExecutor.execute {
            try {
                stopSirenPlayer()
                val player = MediaPlayer().apply {
                    setAudioAttributes(
                        AudioAttributes.Builder()
                            .setUsage(AudioAttributes.USAGE_ALARM)
                            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                            .build(),
                    )
                    setDataSource(
                        context,
                        Uri.parse(
                            "android.resource://${context.packageName}/${R.raw.emergency_siren}"
                        ),
                    )
                    isLooping = true
                    prepare()
                    start()
                }
                sirenPlayer = player
            } catch (_: Exception) {
                sirenPlayer = null
            }
        }
    }

    /** Stop the looping siren, if one is playing. */
    fun stopSiren(context: Context) {
        sirenExecutor.execute {
            stopSirenPlayer()
            cancelEmergency(context)
        }
    }

    private fun stopSirenPlayer() {
        try {
            sirenPlayer?.stop()
        } catch (_: Exception) {
            // Already stopped.
        }
        try {
            sirenPlayer?.release()
        } catch (_: Exception) {
            // Nothing to release.
        }
        sirenPlayer = null
    }

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------

    private fun fetchBitmap(url: String): Bitmap? {
        return try {
            val connection = (URL(url).openConnection() as HttpURLConnection).apply {
                connectTimeout = 8000
                readTimeout = 8000
                requestMethod = "GET"
            }
            try {
                if (connection.responseCode == HttpURLConnection.HTTP_OK) {
                    BitmapFactory.decodeStream(connection.inputStream)
                } else {
                    null
                }
            } finally {
                connection.disconnect()
            }
        } catch (_: Exception) {
            null
        }
    }
}
