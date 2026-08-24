package com.niterhub.dash

import android.Manifest
import android.annotation.SuppressLint
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.MediaStore
import android.view.View
import android.webkit.CookieManager
import android.webkit.ValueCallback
import android.webkit.PermissionRequest
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.ProgressBar
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat

/**
 * WebView shell for the Niter Campus Hub — Student Edition.
 *
 * - Renders [startUrl] full-screen (no ActionBar / status bar — the dashboard
 *   IS the interface). A logged-in student lands straight on the dashboard:
 *   the root URL redirects authenticated sessions to ``/dashboard/student/``
 *   and the persistent 1-year session cookie survives app restarts.
 * - Advertises a standard mobile Chrome User-Agent so Google OAuth does not
 *   reject the embedded browser with "disallowed_useragent".
 * - **Student-only shell**: staff/admin URLs (builder, Django admin, medical
 *   admin, club management) are blocked inside the wrapper and bounced to the
 *   student dashboard — defense in depth on top of the server-side RBAC.
 * - Keeps Google auth redirects (accounts.google.com, drive callbacks) and the
 *   app itself inside the WebView; hands non-http(s) schemes (mailto:/tel:/
 *   intent:/whatsapp://…) to external apps.
 * - Registers for Firebase Cloud Messaging (emergency + campus pushes) and
 *   requests the POST_NOTIFICATIONS permission on Android 13+ — all guarded,
 *   so the app works untouched until ``google-services.json`` is added.
 * - Hardware BACK walks the WebView history before exiting the app.
 * - Supports file uploads (Notes Engine, Reports attachments, profile photos)
 *   through [android.webkit.WebChromeClient.onShowFileChooser].
 */
class MainActivity : AppCompatActivity() {

    /** Point the app at a different deployment by changing this constant. */
    private val startUrl = "https://niter-centralized-dash.onrender.com"

    private val studentDashboardUrl = "$startUrl/dashboard/student/"

    /**
     * Staff/admin areas hidden from the student wrapper. Path prefixes are
     * matched so deep links and server redirects into these areas are bounced
     * back to the student dashboard.
     */
    private val staffAreaPrefixes = listOf(
        "/builder/",
        "/admin/",
        "/django-admin/",
        "/dashboard/admin/",
        "/dashboard/club/",
        "/dashboard/medical/",
        "/medical/admin/",
        "/host/",
    )

    private lateinit var webView: WebView
    private lateinit var progressBar: ProgressBar

    /** Pending JS callback for the native QR scanner (set before launch, cleared on result). */
    private var qrScanCallback: String? = null

    /** Held while the system file picker is open; cleared when the result lands. */
    private var pendingFileCallback: ValueCallback<Array<Uri>>? = null

    /** The picker intent waiting on a runtime-permission grant (camera). */
    private var pendingFileIntent: Intent? = null

    /**
     * Native QR scanner launcher — opens [ScannerActivity] and injects the
     * decoded QR value into the WebView page that requested it.
     */
    private val qrScannerLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val jsCallback = qrScanCallback
        qrScanCallback = null
        if (result.resultCode == RESULT_OK) {
            val qrValue = result.data?.getStringExtra(ScannerActivity.EXTRA_QR_RESULT) ?: ""
            // Escape for safe JS injection — single-quote and backslash.
            val escaped = qrValue.replace("\\", "\\\\").replace("'", "\\'")
            webView.post {
                webView.evaluateJavascript(
                    "if(window.__qrScanCallback){window.__qrScanCallback('$escaped');}"
                ) { /* no-op */ }
            }
        } else {
            // Scanner cancelled — notify the page so it can reset UI.
            webView.post {
                webView.evaluateJavascript(
                    "if(window.__qrScanCallback){window.__qrScanCallback(null);}"
                ) { /* no-op */ }
            }
        }
    }

    private val notificationPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { /* Result is non-blocking — the OS shows the channel settings. */ }

    /**
     * CAMERA runtime permission (Android 6+): the WebView's file chooser may
     * ask for a camera capture (an image input with the capture attribute in
     * the pharmacy / profile upload pages), and launching ACTION_IMAGE_CAPTURE
     * without the CAMERA permission makes the camera app fail with "permission
     * denied". When granted we re-launch the pending picker; when denied we
     * resolve the callback with null so the page's file input doesn't hang.
     */
    private val cameraPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        val intent = pendingFileIntent
        pendingFileIntent = null
        if (granted && intent != null) {
            launchFilePicker(intent)
        } else {
            pendingFileCallback?.onReceiveValue(null)
            pendingFileCallback = null
        }
    }

    private val filePicker = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val uris = if (result.resultCode == RESULT_OK && result.data != null) {
            val clip = result.data!!.clipData
            if (clip != null && clip.itemCount > 0) {
                Array(clip.itemCount) { i -> clip.getItemAt(i).uri }
            } else {
                // Some pickers return RESULT_OK with a data Uri but no clipData;
                // guard against the rare null-data case so we never crash.
                result.data?.data?.let { arrayOf(it) } ?: emptyArray()
            }
        } else {
            emptyArray()
        }
        pendingFileCallback?.onReceiveValue(uris)
        pendingFileCallback = null
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)
        progressBar = findViewById(R.id.progressBar)

        configureWebView()

        // Full-screen: hide the status and navigation bars (edge-to-edge).
        val insets = WindowInsetsControllerCompat(window, window.decorView)
        insets.hide(WindowInsetsCompat.Type.systemBars())
        insets.systemBarsBehavior =
            WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE

        // Hardware BACK: navigate in-page history first, exit only at the root.
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) {
                    webView.goBack()
                } else {
                    finish()
                }
            }
        })

        // Native push: channels + topic subscription + notification permission.
        // The emergency poll worker is the Firebase-free fallback that turns
        // the backend's live emergency state into native notifications + the
        // alarm-channel siren even when the app is backgrounded.
        NotificationHelper.ensureChannels(this)
        EmergencyMessagingService.subscribe(this)
        EmergencyPollWorker.schedule(this)
        requestNotificationPermissionIfNeeded()

        if (savedInstanceState == null) {
            webView.loadUrl(startUrl)
        } else {
            webView.restoreState(savedInstanceState)
        }
    }

    /** Ask for POST_NOTIFICATIONS on Android 13+ (the manifest declares it). */
    private fun requestNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT >= 33) {
            val granted = ContextCompat.checkSelfPermission(
                this, Manifest.permission.POST_NOTIFICATIONS,
            ) == PackageManager.PERMISSION_GRANTED
            if (!granted) {
                notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun configureWebView() {
        val settings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.databaseEnabled = true
        settings.allowFileAccess = true
        settings.allowContentAccess = true
        settings.javaScriptCanOpenWindowsAutomatically = true
        settings.loadWithOverviewMode = true
        settings.useWideViewPort = true
        // Inline media (e.g. embedded YouTube lectures) plays without a tap.
        settings.mediaPlaybackRequiresUserGesture = false
        // The site is served entirely over HTTPS — never allow http subresources.
        settings.mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
        // Defense in depth: file:// pages must never reach other origins/APIs.
        settings.allowFileAccessFromFileURLs = false
        settings.allowUniversalAccessFromFileURLs = false

        // Persistent login: the 1-year Django session cookie is kept on disk,
        // so students stay signed in between app launches until they tap
        // "Log Out". Third-party cookies are kept for the Google OAuth flow.
        CookieManager.getInstance().setAcceptCookie(true)
        CookieManager.getInstance().setAcceptThirdPartyCookies(webView, true)

        // Google OAuth blocks embedded WebViews that advertise "Version/4.0".
        // Rebuild the UA into a standard mobile-Chrome-looking string instead.
        settings.userAgentString = chromeLikeUserAgent(settings.userAgentString)

        // Native siren bridge: the dashboard's emergency banner calls
        // NiterHub.playSiren()/stopSiren() so the alarm plays on the STREAM
        // ALARM channel — it rings even in silent mode and keeps sounding
        // when the screen is off (browser Audio cannot do either).
        webView.addJavascriptInterface(EmergencyBridge(), "NiterHub")

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(
                view: WebView?,
                request: WebResourceRequest?
            ): Boolean {
                val url = request?.url ?: return false
                return handleNavigation(url)
            }

            @Suppress("DEPRECATION")
            @Deprecated("Deprecated in API 24")
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                val uri = Uri.parse(url ?: return false)
                return handleNavigation(uri)
            }

            // Catch server-side redirects (e.g. role home routing after a
            // fresh login) that land in a staff area and bounce them back.
            override fun onPageStarted(view: WebView?, url: String?, favicon: android.graphics.Bitmap?) {
                super.onPageStarted(view, url, favicon)
                val uri = url?.let { Uri.parse(it) }
                if (uri != null && isStaffArea(uri) && webView.url != studentDashboardUrl) {
                    webView.stopLoading()
                    webView.loadUrl(studentDashboardUrl)
                }
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                if (newProgress < 100) {
                    progressBar.visibility = View.VISIBLE
                    progressBar.progress = newProgress
                } else {
                    progressBar.visibility = View.GONE
                }
            }

            // Enable HTML5/WebRTC camera access (e.g. attendance QR scanner).
            // The page's getUserMedia() call triggers this; we grant all
            // requested resources (camera, microphone) so the stream works.
            override fun onPermissionRequest(request: PermissionRequest?) {
                runOnUiThread {
                    request?.grant(request.resources)
                }
            }

            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                // Cancel any stale callback from a previous, abandoned picker.
                pendingFileCallback?.onReceiveValue(null)
                pendingFileCallback = filePathCallback

                val intent = fileChooserParams?.createIntent()
                    ?: Intent(Intent.ACTION_GET_CONTENT).apply {
                        addCategory(Intent.CATEGORY_OPENABLE)
                        type = "*/*"
                    }

                // Camera capture (e.g. pharmacy prescription photo) needs the
                // CAMERA runtime permission on Android 6+. Ask first and only
                // open the picker once the user grants it.
                val wantsCamera = intent.action == MediaStore.ACTION_IMAGE_CAPTURE
                    || intent.action == MediaStore.ACTION_VIDEO_CAPTURE
                    || fileChooserParams?.isCaptureEnabled == true
                if (wantsCamera && ContextCompat.checkSelfPermission(
                        this@MainActivity, Manifest.permission.CAMERA,
                    ) != PackageManager.PERMISSION_GRANTED
                ) {
                    pendingFileIntent = intent
                    cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
                    return true
                }

                return launchFilePicker(intent)
            }
        }
    }

    /** Launch the system picker, resolving the pending callback on failure. */
    private fun launchFilePicker(intent: Intent): Boolean {
        return try {
            filePicker.launch(intent)
            true
        } catch (e: Exception) {
            // No picker app available — resolve with null so the page's
            // file input doesn't stay stuck "picking" forever.
            pendingFileCallback?.onReceiveValue(null)
            pendingFileCallback = null
            true
        }
    }

    /**
     * Bridge the dashboard's emergency banner to the native alarm siren.
     *
     * The WebView page calls ``NiterHub.playSiren()`` when an emergency with
     * ``play_alarm_sound`` renders and ``NiterHub.stopSiren()`` when it is
     * silenced / resolved. Using the native MediaPlayer (STREAM_ALARM) means
     * the siren breaks through silent mode / DND and keeps ringing even when
     * the screen is off — something the in-browser Audio element cannot do.
     */
    private inner class EmergencyBridge {
        @android.webkit.JavascriptInterface
        fun playSiren() {
            NotificationHelper.startSirenLoop(this@MainActivity)
        }

        @android.webkit.JavascriptInterface
        fun stopSiren() {
            NotificationHelper.stopSiren(this@MainActivity)
        }

        /**
         * Launch the native QR scanner. The page must set
         * ``window.__qrScanCallback`` before calling this — the callback
         * receives the decoded string on success or ``null`` on cancel.
         */
        @android.webkit.JavascriptInterface
        fun scanQR() {
            runOnUiThread {
                qrScanCallback = "pending"
                val intent = Intent(this@MainActivity, ScannerActivity::class.java)
                qrScannerLauncher.launch(intent)
            }
        }
    }

    /** True when the URL points into a staff/admin area the student app hides. */
    private fun isStaffArea(uri: Uri): Boolean {
        val path = uri.path ?: return false
        return staffAreaPrefixes.any { prefix ->
            path == prefix.trimEnd('/') || path.startsWith(prefix)
        }
    }

    /**
     * Rewrites the embedded-WebView User-Agent into a normal mobile-Chrome UA
     * tagged with the app's own marker.
     *
     * Google's OAuth consent page refuses sign-in from WebViews whose UA
     * contains the "Version/4.0" token. We strip that token and normalise the
     * Chrome token so the request looks like stock Chrome for Android — the
     * device-specific OS/model tokens from the original UA are preserved.
     *
     * The trailing ``NiterApp/<version>`` token is how the server recognises
     * this request as coming from the native wrapper (``public_home`` bounces
     * authenticated native-app requests straight to the role dashboard, while
     * ordinary browsers keep the public hero page).
     */
    private fun chromeLikeUserAgent(defaultUa: String): String {
        var ua = defaultUa.replace("Version/4.0 ", "").replace("Version/4.0", "")
        ua = if (Regex("Chrome/\\d+\\.\\d+\\.\\d+\\.\\d+").containsMatchIn(ua)) {
            ua.replace(Regex("Chrome/\\d+\\.\\d+\\.\\d+\\.\\d+"), "Chrome/125.0.0.0")
        } else if (Regex("Chrome/\\d+").containsMatchIn(ua)) {
            ua.replace(Regex("Chrome/\\d+"), "Chrome/125.0.0.0")
        } else {
            "$ua Chrome/125.0.0.0 Mobile Safari/537.36"
        }
        return "$ua NiterApp/$APP_VERSION"
    }

    /** App version used to tag the User-Agent for server-side native-app detection. */
    private val APP_VERSION: String
        get() = runCatching { packageManager.getPackageInfo(packageName, 0).versionName }
            .getOrNull() ?: "2.0"

    /**
     * Decides where a navigation goes.
     *
     * @return `true` if the WebView should NOT load the URL (we handled it by
     *         bouncing it or handing it to an external app), `false` to load
     *         it in the WebView.
     */
    private fun handleNavigation(url: Uri): Boolean {
        // Student-only shell: never open staff/admin areas inside the app.
        if (isStaffArea(url)) {
            webView.loadUrl(studentDashboardUrl)
            return true
        }
        return when (url.scheme?.lowercase()) {
            // http/https — including Google OAuth (accounts.google.com), the
            // allauth callback and payment pages — stay inside the WebView.
            "http", "https" -> false
            // Everything else (mailto:, tel:, intent:, whatsapp://, geo:, …)
            // goes to the appropriate external app.
            else -> runCatching { startActivity(Intent(Intent.ACTION_VIEW, url)) }.isSuccess
        }
    }

    override fun onResume() {
        super.onResume()
        webView.onResume()
        // The app is open — hand the siren over to the in-app banner so the
        // native loop and the WebView siren never play at the same time.
        EmergencyMessagingService.stopSiren(this)
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        webView.saveState(outState)
    }

    override fun onPause() {
        super.onPause()
        webView.onPause()
    }

    override fun onDestroy() {
        pendingFileCallback?.onReceiveValue(null)
        pendingFileCallback = null
        webView.destroy()
        super.onDestroy()
    }
}
