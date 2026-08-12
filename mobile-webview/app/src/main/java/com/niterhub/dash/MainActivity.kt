package com.niterhub.dash

import android.annotation.SuppressLint
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.ProgressBar
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat

/**
 * Lightweight WebView wrapper for the Niter Centralized Dash web app.
 *
 * - Renders [startUrl] full-screen (no ActionBar / status bar — the dashboard
 *   IS the interface).
 * - Advertises a standard mobile Chrome User-Agent so Google OAuth does not
 *   reject the embedded browser with "disallowed_useragent".
 * - Keeps Google auth redirects (accounts.google.com, drive callbacks) and the
 *   app itself inside the WebView; hands non-http(s) schemes (mailto:/tel:/
 *   intent:/whatsapp://…) to external apps.
 * - Hardware BACK walks the WebView history before exiting the app.
 * - Supports file uploads (Notes Engine, Reports attachments, profile photos)
 *   through [android.webkit.WebChromeClient.onShowFileChooser].
 */
class MainActivity : AppCompatActivity() {

    /** Point the app at a different deployment by changing this constant. */
    private val startUrl = "https://niter-centralized-dash.onrender.com"

    private lateinit var webView: WebView
    private lateinit var progressBar: ProgressBar

    /** Held while the system file picker is open; cleared when the result lands. */
    private var pendingFileCallback: ValueCallback<Array<Uri>>? = null

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

        if (savedInstanceState == null) {
            webView.loadUrl(startUrl)
        } else {
            webView.restoreState(savedInstanceState)
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
        // The site is served entirely over HTTPS — never allow http subresources.
        settings.mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
        // Defense in depth: file:// pages must never reach other origins/APIs.
        settings.allowFileAccessFromFileURLs = false
        settings.allowUniversalAccessFromFileURLs = false

        // Google OAuth blocks embedded WebViews that advertise "Version/4.0".
        // Rebuild the UA into a standard mobile-Chrome-looking string instead.
        settings.userAgentString = chromeLikeUserAgent(settings.userAgentString)

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
        }
    }

    /**
     * Rewrites the embedded-WebView User-Agent into a normal mobile-Chrome UA.
     *
     * Google's OAuth consent page refuses sign-in from WebViews whose UA
     * contains the "Version/4.0" token. We strip that token and normalise the
     * Chrome token so the request looks like stock Chrome for Android — the
     * device-specific OS/model tokens from the original UA are preserved.
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
        return ua
    }

    /**
     * Decides where a navigation goes.
     *
     * @return `true` if the WebView should NOT load the URL (we handled it by
     *         handing it to an external app), `false` to load it in the WebView.
     */
    private fun handleNavigation(url: Uri): Boolean {
        return when (url.scheme?.lowercase()) {
            // http/https — including Google OAuth (accounts.google.com), the
            // allauth callback and payment pages — stay inside the WebView.
            "http", "https" -> false
            // Everything else (mailto:, tel:, intent:, whatsapp://, geo:, …)
            // goes to the appropriate external app.
            else -> runCatching { startActivity(Intent(Intent.ACTION_VIEW, url)) }.isSuccess
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        webView.saveState(outState)
    }

    override fun onPause() {
        super.onPause()
        webView.onPause()
    }

    override fun onResume() {
        super.onResume()
        webView.onResume()
    }

    override fun onDestroy() {
        pendingFileCallback?.onReceiveValue(null)
        pendingFileCallback = null
        webView.destroy()
        super.onDestroy()
    }
}
