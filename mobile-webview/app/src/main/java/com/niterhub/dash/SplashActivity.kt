package com.niterhub.dash

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.appcompat.app.AppCompatActivity

/**
 * Launcher splash — a clean charcoal screen with the campus hub logo and
 * "NITER Campus Hub — Student Edition", then a hand-off to the WebView shell.
 *
 * Kept deliberately dependency-free: the charcoal theme (``Theme.NiterDash.Splash``)
 * draws instantly, the layout renders the logo + titles, and a short handler
 * starts [MainActivity] (which restores the persisted session and lands
 * straight on the student dashboard).
 */
class SplashActivity : AppCompatActivity() {

    private companion object {
        const val SPLASH_MILLIS = 1400L
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        Handler(Looper.getMainLooper()).postDelayed({
            if (isFinishing || isDestroyed) return@postDelayed
            startActivity(Intent(this, MainActivity::class.java))
            finish()
        }, SPLASH_MILLIS)
    }
}
