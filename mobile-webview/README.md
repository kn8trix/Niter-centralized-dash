# Niter Campus Hub — Student Edition (Android)

A full-fledged, **student-only** native Android app for **Niter Centralized
Dash**. It renders the campus portal (`https://niter-centralized-dash.onrender.com`)
in a full-screen `WebView` and adds native polish on top: a branded splash +
launcher icon, persistent login, direct dashboard landing, native permissions,
Firebase Cloud Messaging push with **picture banners**, and an **emergency
siren** that breaks through silent mode.

## Features

| Requirement | Implementation |
|---|---|
| Branded splash | `SplashActivity` — charcoal screen with the campus-hub logo + "NITER Campus Hub — Student Edition", then a hand-off to the WebView shell |
| Custom app icon | PNG `ic_launcher` / `ic_launcher_round` at every mipmap density (mdpi→xxxhdpi) — charcoal rounded square/circle with a beige "N" monogram (regenerate with `scripts/generate_assets.py`) |
| Persistent login | The 1-year Django session cookie (`SESSION_COOKIE_AGE = 31536000`) is stored by `CookieManager`, so students stay signed in between launches until they tap **Log Out** |
| Direct dashboard landing | The app's UA carries a `NiterApp/<version>` marker; the server (`public_home`) bounces **native-app-only** authenticated sessions straight to the role dashboard, while desktop/mobile browsers keep the public hero page |
| Student-only shell | Staff/admin URLs (`/builder/`, `/admin/`, `/dashboard/admin/`, `/dashboard/club/`, `/dashboard/medical/`, `/medical/admin/`, `/host/`) are blocked inside the wrapper and bounced to the student dashboard — defense in depth on top of the server-side RBAC |
| Native permissions | INTERNET, ACCESS_NETWORK_STATE, CAMERA, READ_MEDIA_IMAGES, READ/WRITE_EXTERNAL_STORAGE (legacy caps), POST_NOTIFICATIONS (runtime-requested on Android 13+), VIBRATE, WAKE_LOCK |
| FCM push w/ picture banners | `EmergencyMessagingService` subscribes to the `emergency_alerts` topic; pushes render as BigPicture notifications (push `banner` URL, or the bundled `emergency_banner.png`) |
| Emergency siren controls | High-importance `emergency_alerts` channel plays `res/raw/emergency_siren.wav` + vibrates; `play_alarm_sound` data loops the siren until dismissed via the **Stop Siren** notification action or by opening the app |
| Full-screen web experience | `Theme.AppCompat.NoActionBar` + `android:windowFullscreen` + `WindowInsetsControllerCompat` hides the ActionBar, status bar and navigation bar |
| JavaScript + storage | `setJavaScriptEnabled(true)`, `setDomStorageEnabled(true)`, `setDatabaseEnabled(true)`, `setAllowFileAccess(true)` (see `configureWebView()`) |
| Google OAuth works | `chromeLikeUserAgent()` strips the `Version/4.0` marker, normalises the Chrome token (so Google's "disallowed_useragent" block never triggers) and appends `NiterApp/<version>` so the server can detect the native wrapper |
| External links | `shouldOverrideUrlLoading` keeps `http`/`https` inside the WebView and hands `mailto:`/`tel:`/`intent:`/`whatsapp://` to external apps |
| Hardware BACK | `OnBackPressedCallback` walks `WebView` history first, exits only at the root page |
| File uploads | `WebChromeClient.onShowFileChooser` → system picker (Notes Engine, Reports attachments, profile photos) |
| HTTPS enforced | `network_security_config.xml` forbids cleartext everywhere except loopback hosts for local dev |

## Project layout

```
mobile-webview/
├── settings.gradle.kts          # repo config (Google + Maven Central)
├── build.gradle.kts             # AGP 8.10.1, Kotlin 2.0.21, google-services 4.4.2
├── gradle.properties
├── gradle/wrapper/gradle-wrapper.properties
├── scripts/
│   └── generate_assets.py       # regenerates launcher icons + siren WAV + banner (Pillow)
└── app/
    ├── build.gradle.kts         # com.niterhub.dash, minSdk 26, targetSdk 36, firebase-messaging
    └── src/main/
        ├── AndroidManifest.xml  # permissions, splash launcher, FCM service
        ├── java/com/niterhub/dash/
        │   ├── SplashActivity.kt            # branded splash → WebView shell
        │   ├── MainActivity.kt              # WebView shell + student-only guard + FCM subscribe
        │   ├── EmergencyMessagingService.kt # FCM: emergency/general pushes, siren control
        │   └── NotificationHelper.kt        # channels, BigPicture banners, siren loop
        └── res/
            ├── drawable/        # adaptive foreground, alert small-icon, emergency banner
            ├── mipmap-*/        # ic_launcher + ic_launcher_round PNGs (all densities)
            ├── raw/             # emergency_siren.wav (bundled siren)
            ├── layout/          # WebView + progress bar + splash screen
            └── values/ xml/     # strings, theme (incl. splash), colors, network security config
```

## Firebase Cloud Messaging (push notifications)

Push is **plumbed but Firebase-optional**: the app builds and runs perfectly
without a Firebase project — the FCM service is simply never invoked. To turn
push on:

1. **Create a Firebase project** at <https://console.firebase.google.com> and
   add an **Android app** with package name `com.niterhub.dash`.
2. **Download `google-services.json`** from Firebase console → Project settings
   → Your apps → `com.niterhub.dash`, and place it in
   `mobile-webview/app/google-services.json`. The Gradle plugin auto-activates
   on the next sync (the build script applies it only when the file exists).
3. **Server side**: set `FIREBASE_CREDENTIALS` (Firebase service-account JSON,
   inline or path) in the Django environment. The backend
   (`services/emergency_push.py`) broadcasts Emergency Alerts to the
   `emergency_alerts` **topic** — the app subscribes on first launch, so no
   per-device token management is needed.
4. Rebuild the APK. Emergency broadcasts now push with a picture banner, siren
   sound, and vibration.

## Requirements

- **Android Studio** — Meerkat (2024.3.1) or newer recommended (it bundles
  JDK 17+ and will auto-provision the Gradle wrapper).
- **Android SDK** — `platforms;android-36` and `build-tools;35.0.0` (Android
  Studio's SDK Manager installs these automatically on first sync).
- Internet access on first build (Gradle downloads AGP/Kotlin/AndroidX/Firebase).

## Open & build the APK (Android Studio)

1. **Open the project**
   - Android Studio → **File → Open…** → select the `mobile-webview` folder
     (the one containing `settings.gradle.kts`) → **OK**.
   - If asked whether to trust the project, choose **Trust Project**.
2. **Let Gradle sync** — Android Studio downloads the Gradle 8.11.1 wrapper and
   all dependencies automatically (the wrapper JAR and `gradlew` scripts are
   committed, so this works out of the box).
   - If the SDK isn't found, set the SDK path via
     **File → Project Structure → SDK Location**.

**Command-line build** (JDK 17+ required):

```bash
cd mobile-webview
./gradlew assembleDebug          # Windows: gradlew.bat assembleDebug
# APK → app/build/outputs/apk/debug/app-debug.apk
```
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

Rebuild and reinstall — no other changes are needed. The student-dashboard
bounce URL is derived from it (`$startUrl/dashboard/student/`).

## Regenerating assets

Launcher icons, the emergency banner and the siren WAV are generated (Pillow,
pure-Python WAV):

```bash
python3 mobile-webview/scripts/generate_assets.py
```

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
- **No push notifications arrive** — confirm `google-services.json` is in
  `mobile-webview/app/`, the APK was rebuilt after adding it, and the server
  has `FIREBASE_CREDENTIALS` set. On Android 13+ the notification permission
  must be granted (the app asks on first launch; enable it in Settings if
  denied).
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
  launches (1-year Django session cookie). Logging out in the app clears the
  session server-side.
- The wrapper blocks staff/admin areas at the navigation layer (student-only
  edition); the server enforces the same RBAC independently.
