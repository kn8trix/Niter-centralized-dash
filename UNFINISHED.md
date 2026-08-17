# UNFINISHED.md — Session Progress, Pending Tasks & Continuation Points

> **Purpose:** Track what was completed in the recent development sessions, the
> exact current state of every in-flight system, and precisely where to resume
> work so the next session picks up without re-discovering context.
>
> **Last updated:** 17 August 2026 · Branch `main` · Working tree: clean
> (Steps 1–6 of the roadmap completed this session; Step 7 final commit
> pending).

---

## 1. COMPLETED WORK SUMMARY

### 1.1 Most recent commits (this project's changelog §118–§122)

| § | Commit | What shipped |
|---|--------|--------------|
| 122 | `25789af`, `9478115`, `cbe17b4` | **Student Edition Android app** (`mobile-webview/`): branded splash + launcher icons (all mipmap densities), persistent sessions, direct dashboard landing, native permissions, FCM push with picture banners, native emergency siren + "Turn Off Siren" control; Gradle wrapper jar/scripts committed so terminal builds work. |
| 121 | `29688ff` | **Public pharmacy storefront** — guest browsing/cart on `/pharmacy/`, hero pharmacy button contrast fix, auto-seeded BD medicine catalog. |
| 120 | `5c90964` | **Club dashboard sub-routes** + event banner upload + event visibility sync to student portals. |
| 119 | `a164e8a` | **Visual builder empty-canvas fix** — default block HTML backfill, preview-mode canvas, template-cache flush on save/publish. |
| 118 | `6e5430b` | **Pharmacy layout + catalog + checkout** — BD medicine catalog, product detail modal, payment-gateway checkout, out-of-stock stock requests, modal CSS fix. |

### 1.2 Backend / database (all committed)

- **`MedicineRequest` model** exists in `core/models.py` (~line 1785): FK to
  `MedicineItem` + `User`, `quantity`, `urgency_note`, `phone`, `status`
  (`pending` / `fulfilled` / `rejected`), `admin_note`, `created_at`,
  `updated_at`, ordered newest-first.
- **`api_pharmacy_stock_request`** (`core/views.py` ~line 1095,
  `@login_required`) persists requests from the storefront "Request Stock"
  modal; staff see them on the Pharmacy Admin dashboard **Medicine Requests
  tab** (`templates/pharmacy/admin.html`, `tab-requests` pane,
  `pending_requests_count` badge) and mark them fulfilled/rejected via
  `api_pharmacy_request_status`.
- **`pharmacy_store`** view (`core/views.py` ~line 738) is **public** — no
  `@login_required`; guests browse/search/build carts. Login is enforced only
  on the API endpoints (checkout / stock request / prescription upload).
- **Session persistence** (`config/settings.py` ~line 397–400):
  `SESSION_EXPIRE_AT_BROWSER_CLOSE = False`,
  `SESSION_COOKIE_AGE = 31536000` (365 days).
- **Club dashboard sub-routes** live in `core/urls.py`:
  `/dashboard/club/`, `/dashboard/club/google-sheet/`, `members/`, `roles/`,
  `events/`, `transactions/` → dedicated views + templates under
  `templates/dashboard/club/` (`overview.html`, `sheet.html`, `members.html`,
  `roles.html`, `events.html`, `transactions.html`).
- **Visual builder** (`templates/builder/edit_page.html`) renders a block
  manager + section canvas/preview tabs; default block HTML backfill and
  template-cache flush shipped in §119.

### 1.3 Android wrapper (`mobile-webview/`)

- `AndroidManifest.xml` already declares `INTERNET`, `ACCESS_NETWORK_STATE`,
  `CAMERA`, `READ_MEDIA_IMAGES`, `READ_EXTERNAL_STORAGE`,
  `WRITE_EXTERNAL_STORAGE`, `POST_NOTIFICATIONS`, `VIBRATE`, `WAKE_LOCK`.
- `MainActivity.kt` blocks staff/admin/builder URLs inside the WebView
  (`/builder/`, `/admin/`, `/django-admin/`, `/dashboard/admin/`,
  `/medical/admin/`, club management) and shows a restricted-area fallback;
  file-chooser bridge, JS/domStorage enabled, payment-scheme intents
  (`bkash://`, `nagad://`, `intent://`, `upay://`), session persistence.
- `NotificationHelper.kt` renders **BigPictureStyle picture banners** and
  loops the siren on `STREAM_ALARM`; `EmergencyMessagingService.kt` handles
  `play_siren` / `type=resolved` push payloads and exposes
  `stopSiren(context)`; `MainActivity` stops the siren on resume.
- **Gradle sync + compile — DONE (verified `./gradlew assembleDebug`
  passes, APK produced).** The full story: `settings.gradle.kts` gained
  `jitpack.io` (committed `4253795`); `local.properties` points at
  `sdk.dir=/home/kn8/Android/Sdk` (gitignored); two Kotlin compile errors
  surfaced by firebase-messaging 24.1.0 were fixed:
  - `EmergencyMessagingService.kt` — `onStartCommand` is **final** on
    `EnhancedIntentService`, so the override was removed; the notification's
    "Stop Siren" action now routes through a new **`SirenControlReceiver`**
    (BroadcastReceiver, registered in the manifest).
  - `NotificationHelper.kt` — `bannerUrl?.trim().takeIf { … }` called
    `.takeIf` on a nullable receiver; now `bannerUrl?.trim()?.takeIf { … }`.
  - The 4 files listed below are **uncommitted** (see §2.1).

### 1.4 UI / UX already shipped

- Checkout modal `display:none` bug fixed: `.modal-backdrop[hidden] { display: none; }`
  in `static/css/pharmacy.css` (modals no longer render on page load).
- Hero "Online Pharmacy" button restyled with `#0284c7` background.
- Pharmacy pages carry the standard `width=device-width, initial-scale=1.0`
  viewport meta; pharmacy CSS has a `@media (max-width: 768px)` responsive
  block.

---

## 2. CURRENT SYSTEM STATE & PENDING ISSUES

### 2.1 Android App & Gradle Sync — ✅ BUILD PASSES + FIXES COMMITTED

**State:**
- `mobile-webview/settings.gradle.kts` — `jitpack.io` added under
  `dependencyResolutionManagement.repositories`; **committed** (`4253795`).
- Compile fixes **committed** (`41c2c87`): `SirenControlReceiver` (new) +
  manifest registration, `EmergencyMessagingService.kt` override removed
  (`onStartCommand` is final on `EnhancedIntentService` in firebase-messaging
  24.1.0), `NotificationHelper.kt` safe-call fix.
- `mobile-webview/local.properties` — `sdk.dir=/home/kn8/Android/Sdk`;
  **gitignored** (never commit — machine-specific path).
- Root `build.gradle.kts` declares AGP `8.10.1`, Kotlin `2.0.21`,
  google-services `4.4.2` (applied only when `google-services.json` exists).
  `settings.gradle.kts` has `google()`, `mavenCentral()`, `gradlePluginPortal()`
  (pluginManagement) and `google()`, `mavenCentral()`, `jitpack.io`
  (dependencyResolutionManagement, `FAIL_ON_PROJECT_REPOS`).
- **`./gradlew assembleDebug` PASSES** — `app-debug.apk` (4.4 MB) at
  `mobile-webview/app/build/outputs/apk/debug/`. Only 3 harmless deprecation
  warnings remain (`WebSettings.databaseEnabled` / `allowFileAccessFromFileURLs`
  / `allowUniversalAccessFromFileURLs` in `MainActivity.kt`).

**Pending:**
- Verify FCM push with picture banners + emergency siren end-to-end on a
  device (code compiles; runtime path needs a Firebase
  `google-services.json` drop-in to activate).
- Optional: build the release APK (`./gradlew assembleRelease`).

### 2.2 Online Pharmacy (`/pharmacy/`) — ✅ COMPLETE (17 Aug 2026)

1. **Product image URLs / fallbacks — DONE.** Local self-hosted photos in
   `static/images/pharmacy/` for all 8 seeded medicines + `default_medicine.png`
   universal fallback; `onerror` swap in `cardImage()` / `openProduct()`;
   seed command backfills old placehold.co URLs.
2. **Button & card text contrast — DONE.** Solid cyan `#0284c7` for Add /
   Cart pill / Upload Prescription, dark red `#b91c1c` for out-of-stock
   Request, dark grey `#374151` / `#f3f4f6` for Details; `.med-img` / `.pd-img`
   placeholders are dark slate `#1f2937` with `#f3f4f6` icons.
3. **Standalone public access — DONE** (`pharmacy_store` is public; login
   required only at checkout / stock request / Rx upload).
4. **"Request any medicine" — DONE.** Standalone `/pharmacy/request/` page
   (free-text fields incl. urgency normal/urgent) backed by the extended
   `MedicineRequest` model (migration `0046`, nullable FKs + name/ID/urgency
   fields); storefront toolbar links to it; admin tab renders both request
   kinds (catalog + free-text).

### 2.3 Global Navigation — ✅ DONE (17 Aug 2026)

- **Pharmacy pill removed** from `templates/partials/topbar.html` (desktop
  nav pills + mobile profile-popover links). The dedicated "Online Pharmacy"
  action button inside `/medical/` (`templates/medical/booking.html` →
  `.med-pharmacy-btn`) is kept.

### 2.4 Visual Website Builder — MOSTLY DONE (§119)

- Empty-canvas bug fixed: default block HTML backfill, preview-mode canvas,
  template-cache flush on save/publish (committed `a164e8a`).
- `edit_page.html` has canvas/preview tabs + live inspector sync.
- **Verify/remaining:** confirm the fallback path renders template partials
  (e.g. `templates/partials/_hero.html`) when a block's `content` is empty
  (vs. the old "This page has no content yet" state) — the §119 commit covers
  default backfill; a quick browser check of a freshly created page is the
  final confirmation.

### 2.5 Club Dashboard — DONE (§120)

- Sub-routes implemented (`overview`, `google-sheet`, `members`, `roles`,
  `events`, `transactions`) with dedicated views + templates under
  `templates/dashboard/club/`; `ClubEvent.banner` + `is_published` +
  student-portal visibility shipped in `5c90964`.
- No pending work unless a specific sub-page needs styling/testing.

### 2.6 Mobile WebView Responsiveness — ✅ PHARMACY DONE, REST OPEN

- Pharmacy pages (store / orders / admin / request) now ship the full
  viewport: `width=device-width, initial-scale=1.0, maximum-scale=1.0,
  user-scalable=no`.
- New `@media (max-width: 640px)` block in `pharmacy.css`: modals
  `width:95vw; max-height:90vh; overflow-y:auto`, 44px min-height touch
  targets on buttons/inputs, `.navlinks` horizontal scroll.
- Admin tables already use `.admin-table-wrap` (overflow-x auto).
- **Still open:** same treatment for medical + other service pages (44px
  touch targets, horizontal pill bars, table wrappers).

---

## 3. RESUMPTION ROADMAP & EXACT STARTING POINT

**Roadmap status — Steps 1–6 DONE this session (17 Aug 2026):**

| Step | Task | Status |
|------|------|--------|
| 1 | Commit Android compile fixes (SirenControlReceiver + nullable bannerUrl) | ✅ `41c2c87` |
| 2 | Pharmacy contrast (cyan/red/grey buttons, dark-slate image placeholders) | ✅ |
| 2 | `onerror` fallback to `default_medicine.png` in `cardImage()` / `openProduct()` | ✅ |
| 2 | `static/images/pharmacy/default_medicine.png` + 8 branded product photos | ✅ |
| 2 | Seed command → local static image URLs + placehold.co backfill | ✅ (re-seeded) |
| 3 | Hero auto-redirect gated to `niterapp` UA / `X-Native-App` header | ✅ (tests rewritten) |
| 4 | Pharmacy pill removed from topbar (desktop + mobile) | ✅ |
| 5 | Standalone `/pharmacy/request/` form + `MedicineRequest` free-text fields (migration `0046`) + admin tab for both kinds | ✅ (5 new tests) |
| 6 | Mobile WebView: full viewport meta, `@media (max-width: 640px)` modals + 44px touch targets + horizontal navlinks | ✅ |
| 7 | `manage.py check` + 64 pharmacy tests + 21 targeted tests | ✅ passing |

**Next session — pick up here:**

### Step 7 (finish) — Final docs + commit + push
1. `docs/HANDOVER.md` §123 already written (changelog row + full section).
2. `UNFINISHED.md` — mark the table above as committed once pushed.
3. Commit everything in one pass:
   ```bash
   git add -A && git commit -m "Pharmacy contrast + product images, native-app-only hero redirect, request-any-medicine page, topbar cleanup, Android compile fixes, mobile WebView polish"
   git push origin main
   ```
4. Optional follow-ups (not required):
   - `cd mobile-webview && ./gradlew assembleRelease` for the release APK.
   - Browser-check `/`, `/pharmacy/`, `/pharmacy/request/` at 390px + 1280px.
   - Device E2E of FCM picture banners + emergency siren (needs
     `google-services.json` drop-in — code compiles, runtime path is inert
     without Firebase).

### Still open (lower priority, not in the original roadmap)
- **Visual builder fallback check (§2.4)** — the §119 default-HTML backfill
  is committed; a browser check of a freshly created page confirms the
  template-partial fallback path renders (vs. "This page has no content yet").
- **Mobile WebView pass beyond pharmacy** — 44px touch targets / horizontal
  pill bars / `table-responsive` wrappers were applied to pharmacy pages;
  medical + other service pages can get the same treatment.
- **FCM end-to-end on device** — requires the Firebase project + rebuilt APK.

---

## 4. QUICK REFERENCE — KEY FILES

| Area | File(s) |
|------|---------|
| Pharmacy catalog seed | `core/management/commands/seed_pharmacy_catalog.py` |
| Pharmacy storefront | `templates/pharmacy/store.html` + `static/css/pharmacy.css` |
| Pharmacy admin (requests tab) | `templates/pharmacy/admin.html`, `core/views.py` (`medical_pharmacy`, `api_pharmacy_stock_request`, `api_pharmacy_request_status`) |
| Pharmacy models | `core/models.py` (`MedicineItem` ~1539, `MedicineRequest` ~1785) |
| Hero redirect | `core/views.py` → `public_home` (~155) + `core/roles.py` (`get_user_role`, `role_home_path`) |
| Global nav | `templates/partials/topbar.html` |
| Club dashboard | `core/urls.py` (lines 17–24), `templates/dashboard/club/` |
| Visual builder | `templates/builder/edit_page.html`, `core/views.py` (`editable_page_view`), `core/templatetags/builder_tags.py` |
| Android wrapper | `mobile-webview/settings.gradle.kts`, `app/build.gradle.kts`, `app/src/main/AndroidManifest.xml`, `app/src/main/java/com/niterhub/dash/MainActivity.kt`, `NotificationHelper.kt`, `EmergencyMessagingService.kt`, `SirenControlReceiver.kt` |
| Sessions | `config/settings.py` (SESSION_EXPIRE_AT_BROWSER_CLOSE / SESSION_COOKIE_AGE) |
