# Niter Dash — Android WebView Wrapper

A lightweight Android app that renders **Niter Centralized Dash** in a full-screen
`WebView`, giving students a native launcher for the campus dashboard
(`https://niter-centralized-dash.onrender.com`).

## Features

| Requirement | Implementation |
|---|---|
| Full-screen web experience | `Theme.AppCompat.NoActionBar` + `android:windowFullscreen` + `WindowInsetsControllerCompat` hides the ActionBar, status bar and navigation bar |
| JavaScript + storage | `setJavaScriptEnabled(true)`, `setDomStorageEnabled(true)`, `setDatabaseEnabled(true)`, `setAllowFileAccess(true)` (see `configureWebView()` in `MainActivity.kt`) |
| Google OAuth works | `chromeLikeUserAgent()` strips the `Version/4.0` marker and normalises the Chrome token, so Google's "disallowed_useragent" block never triggers; allauth + Drive callbacks stay in the WebView |
| External links | `shouldOverrideUrlLoading` keeps all `http`/`https` (Google auth, payments) inside the WebView and hands `mailto:`/`tel:`/`intent:`/`whatsapp://` to external apps |
| Hardware BACK | `OnBackPressedCallback` walks `WebView` history first, exits only at the root page |
| File uploads | `WebChromeClient.onShowFileChooser` → system picker (via `ActivityResultContracts.StartActivityForResult`), used by the Notes Engine and the Reports & Feedback attachments |
| HTTPS enforced | `network_security_config.xml` forbids cleartext everywhere except loopback hosts for local dev |

## Project layout

```
mobile-webview/
├── settings.gradle.kts          # repo config (Google + Maven Central)
├── build.gradle.kts             # AGP 8.10.1, Kotlin 2.0.21
├── gradle.properties
├── gradle/wrapper/gradle-wrapper.properties
└── app/
    ├── build.gradle.kts         # namespace com.niterhub.dash, minSdk 26, targetSdk 36
    └── src/main/
        ├── AndroidManifest.xml
        ├── java/com/niterhub/dash/MainActivity.kt
        └── res/                 # layout, theme, strings, adaptive icon, xml/network_security_config
```

## Requirements

- **Android Studio** — Meerkat (2024.3.1) or newer recommended (it bundles
  JDK 17+ and will auto-provision the Gradle wrapper).
- **Android SDK** — `platforms;android-36` and `build-tools;35.0.0` (Android
  Studio's SDK Manager installs these automatically on first sync).
- Internet access on first build (Gradle downloads AGP/Kotlin/AndroidX).

## Open & build the APK (Android Studio)

1. **Open the project**
   - Android Studio → **File → Open…** → select the `mobile-webview` folder
     (the one containing `settings.gradle.kts`) → **OK**.
   - If asked whether to trust the project, choose **Trust Project**.
2. **Let Gradle sync** — Android Studio downloads the Gradle 8.11.1 wrapper and
   all dependencies automatically. If the wrapper JAR is missing from
   `gradle/wrapper/`, Android Studio restores it during sync (or run
   `gradle wrapper` in a terminal inside `mobile-webview/`).
   - If the SDK isn't found, set the SDK path via
     **File → Project Structure → SDK Location**.
3. **Build a debug APK**
   - **Build → Build App Bundle(s) / APK(s) → Build APK(s)**.
   - The APK lands in `app/build/outputs/apk/debug/app-debug.apk` — copy it to
     a phone and install (enable "Install unknown apps" on the device), or plug
     a phone in and press **Run ▶** to install & launch directly.
4. **Release APK (optional)**
   - **Build → Generate Signed Bundle / APK… → APK** and follow the wizard to
     create a keystore, then choose `release`. The signed APK is written to
     `app/build/outputs/apk/release/app-release.apk`.

## Changing the target URL

Edit the `startUrl` constant at the top of `MainActivity.kt`:

```kotlin
private val startUrl = "https://niter-centralized-dash.onrender.com"
```

Rebuild and reinstall — no other changes are needed.

## Troubleshooting

- **Google login says "This browser or app may not be secure"** — the UA
  override handles this; ensure you rebuilt after editing `MainActivity.kt`.
  If the dashboard itself is opened in a plain browser it can also show this —
  the WebView wrapper is the supported path.
- **File picker opens but the upload never completes** — the page must be
  served over HTTPS (it is), and the `accept` attributes on the input are
  forwarded automatically by `onShowFileChooser`.
- **App shows a blank screen** — check the device has an internet connection
  and that `https://niter-centralized-dash.onrender.com` is reachable; try
  `adb logcat | grep chromium` for WebView errors.
- **Cleartext blocked when testing against a LAN dev server** — the network
  security config only whitelists loopback hosts; if you point `startUrl` at a
  machine on your LAN (e.g. `http://192.168.x.x:8000`) from a physical device,
  add that IP as a `<domain>` in
  `app/src/main/res/xml/network_security_config.xml`.

## Security notes

- `allowFileAccess(true)` is enabled per requirements; `allowFileAccessFromFileURLs`
  and `allowUniversalAccessFromFileURLs` are explicitly `false` so untrusted
  `file://` content cannot reach the network or other origins.
- The WebView keeps session cookies, so students stay logged in between app
  launches (Django session cookie persists until it expires).
