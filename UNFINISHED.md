# UNFINISHED.md — Session Progress, Pending Tasks & Continuation Points

> **Purpose:** Track what was completed in the recent development sessions, the
> exact current state of every in-flight system, and precisely where to resume
> work so the next session picks up without re-discovering context.
>
> **Last updated:** 17 August 2026 · Branch `main` · Working tree: 1 modified
> file (`mobile-webview/settings.gradle.kts`) + 1 gitignored file
> (`mobile-webview/local.properties`).

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
- **Gradle sync fix (IN PROGRESS — see §2.1):** `settings.gradle.kts` edited
  to add `jitpack.io` (uncommitted); `local.properties` created with
  `sdk.dir=/home/kn8/Android/Sdk` (gitignored). Build previously failed with
  `SDK location not found` — the fix resolves that, but the build has **not**
  been re-verified end-to-end.

### 1.4 UI / UX already shipped

- Checkout modal `display:none` bug fixed: `.modal-backdrop[hidden] { display: none; }`
  in `static/css/pharmacy.css` (modals no longer render on page load).
- Hero "Online Pharmacy" button restyled with `#0284c7` background.
- Pharmacy pages carry the standard `width=device-width, initial-scale=1.0`
  viewport meta; pharmacy CSS has a `@media (max-width: 768px)` responsive
  block.

---

## 2. CURRENT SYSTEM STATE & PENDING ISSUES

### 2.1 Android App & Gradle Sync — ⚠️ IN PROGRESS

**State:**
- `mobile-webview/settings.gradle.kts` **modified, NOT committed**: added
  `maven { url = uri("https://jitpack.io") }` under
  `dependencyResolutionManagement.repositories`.
- `mobile-webview/local.properties` **created, gitignored**:
  `sdk.dir=/home/kn8/Android/Sdk`.
- Root `build.gradle.kts` declares AGP `8.10.1`, Kotlin `2.0.21`,
  google-services `4.4.2` (applied only when `google-services.json` exists).
  `settings.gradle.kts` has `google()`, `mavenCentral()`, `gradlePluginPortal()`
  (pluginManagement) and `google()`, `mavenCentral()`, `jitpack.io`
  (dependencyResolutionManagement, `FAIL_ON_PROJECT_REPOS`).

**Pending:**
- Re-run `cd mobile-webview && ./gradlew assembleDebug` to confirm the sync +
  build now succeed with the SDK path + jitpack.io in place.
- Commit `settings.gradle.kts` (the jitpack.io repository change).
- Verify FCM push with picture banners + emergency siren end-to-end on a
  device (code is present; runtime path needs a Firebase
  `google-services.json` drop-in to activate).

### 2.2 Online Pharmacy (`/pharmacy/`) — ⚠️ MULTIPLE PENDING ITEMS

1. **Product image URLs / fallbacks — NOT DONE.**
   - `core/management/commands/seed_pharmacy_catalog.py` still seeds
     `image_url` with placehold.co placeholders
     (`https://placehold.co/400x300/EADCC9/2B2927?text=…`).
   - No `static/images/pharmacy/default_medicine.png` fallback asset exists
     (directory does not exist).
   - `store.html` `cardImage()` uses an icon fallback (`.no-img` class +
     `.med-img-fallback`), **not** the requested
     `onerror="this.onerror=null; this.src='/static/images/pharmacy/default_medicine.png'"`
     pattern.
2. **Button & card text contrast — NOT DONE.**
   - `.btn-primary` in `static/css/pharmacy.css` is still generic dark grey
     (`var(--accent-dark, #27272a)`); the requested solid **cyan `#0284c7`**
     for "+ Add", solid **dark red `#b91c1c`** for out-of-stock "Request", and
     solid **dark grey `#374151` / text `#f3f4f6`** for "Details" are NOT
     implemented.
   - `.med-img` / `.pd-img` placeholder backgrounds are still light
     (`var(--bg-subtle, #f7f4ef)`); the requested dark slate `#1f2937` /
     `#111827` container (or dark charcoal `#111827` text) is NOT implemented.
   - Header "Cart" pill (`.pharm-cart-btn`) and "Upload Prescription"
     (`.pharm-rx-btn`) do not have the requested explicit `#0284c7` /
     `#ffffff` styling (cart pill uses dark grey; Rx button is dashed outline).
3. **Standalone public access — DONE** (`pharmacy_store` is public; login
   required only at checkout / stock request / Rx upload).
4. **"Request Medicine" out-of-stock feature — PARTIALLY DONE.**
   - Model + API + admin tab exist and work for **out-of-stock catalog items**
     via the storefront modal.
   - **NOT DONE:** a standalone **"Request any medicine" fill-out form page**
     (free-text medicine name — not limited to catalog items). The requested
     model shape (`student_name`, `student_id`, `medicine_name`,
     `generic_name`, `urgency` normal/urgent) differs from the shipped model
     (FKs + `urgency_note`). Decide whether to extend the existing model or
     add the free-text page on top of it (recommended: extend — the admin tab
     + API already key off `MedicineRequest`).

### 2.3 Global Navigation — NOT DONE

- `templates/partials/topbar.html` still contains the **Pharmacy pill** in
  both the desktop nav pills (~line 81) and the mobile profile-popover links
  (~line 127):
  `<a href="{% url 'pharmacy_store' %}" …><i class="fa-solid fa-prescription-bottle-medical"></i> Pharmacy</a>`.
- Requested: remove both so the global top bar no longer advertises
  Pharmacy; keep the dedicated "Online Pharmacy" action button inside
  `/medical/` (`templates/medical/booking.html` → `.med-pharmacy-btn`).

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

### 2.6 Mobile WebView Responsiveness — PARTIALLY DONE

- Viewport meta is present but **not** the requested full form:
  `width=device-width, initial-scale=1.0` — missing `maximum-scale=1.0,
  user-scalable=no`.
- Touch targets: 44px exists in `clubs.css` / `club_dashboard.css` only;
  not applied consistently across pharmacy/other service pages.
- Header nav pill bars: horizontal `overflow-x: auto; white-space: nowrap;`
  treatment NOT verified/added.
- `@media (max-width: 640px)` modal sizing (`width: 95vw; max-height: 90vh;
  overflow-y: auto;`) NOT added to `pharmacy.css`.
- Data tables wrapped in `.table-responsive` (`overflow-x: auto;`) — NOT
  present in pharmacy templates.

---

## 3. RESUMPTION ROADMAP & EXACT STARTING POINT

**Start here next session — in this order:**

### Step 1 — Close out the Android Gradle sync (5 min)
1. `cd mobile-webview && ./gradlew assembleDebug`
2. If it passes, commit the wrapper fix:
   `git add mobile-webview/settings.gradle.kts && git commit -m "Add jitpack.io repository to fix Android Gradle sync"`
   (do NOT commit `local.properties` — it is gitignored on purpose).
3. If it still fails, read the stack trace — the most likely next cause is a
   missing SDK component or plugin download; fix the specific error.

### Step 2 — Pharmacy contrast + image fallbacks (the biggest open chunk)
Files: `static/css/pharmacy.css`, `templates/pharmacy/store.html`,
`core/management/commands/seed_pharmacy_catalog.py`.
1. `static/css/pharmacy.css`:
   - `.med-img` / `.pd-img` placeholder → `background: #1f2937;` and make the
     fallback icon/text `#f3f4f6` (crisp on dark).
   - Add scoped rules for `.med-add` → `background: #0284c7; color: #fff;
     border: none; font-weight: 600;` (and hover `#0369a1`), `.med-request` /
     `.pd-request` → `background: #b91c1c; color: #fff;`, `.med-detail` →
     `background: #374151; color: #f3f4f6; border: 1px solid #4b5563;`.
   - `.pharm-cart-btn` → explicit `background: #0284c7; color: #ffffff;`;
     give `.pharm-rx-btn` the same solid treatment (or a dark outline with
     `#f3f4f6` text per the spec).
2. `templates/pharmacy/store.html` `cardImage()` — add the onerror fallback
   img: `onerror="this.onerror=null; this.src='/static/images/pharmacy/default_medicine.png'"`.
   Same for the `.pd-img` in `openProduct()`.
3. Create the fallback asset: `static/images/pharmacy/default_medicine.png`
   (simple pill/capsule graphic on a `#1f2937` square, 400×300).
4. `seed_pharmacy_catalog.py` — replace the placehold.co URL with working
   high-res product image URLs for the 8 seeded medicines (Napa Extra, Seclo,
   Sergel, Ace Plus, Entacyd, Savlon, Ceevit, Monas). Run
   `python manage.py seed_pharmacy_catalog` (idempotent) and verify `/pharmacy/`.

### Step 3 — Restrict hero auto-redirect to the native app
File: `core/views.py` → `public_home` (~line 155).
- Change the authenticated-user redirect so it fires ONLY for the native app
  wrapper:
  ```python
  user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
  is_mobile_app = 'niterapp' in user_agent or request.META.get('HTTP_X_NATIVE_APP') == 'true'
  if request.user.is_authenticated and is_mobile_app and request.path == '/':
      return redirect(role_home_path(get_user_role(request.user)))
  ```
- Result: desktop/mobile **browsers can view the public hero page even when
  logged in**; only the WebView wrapper auto-bounces to the dashboard.

### Step 4 — Remove the Pharmacy pill from the global top bar
File: `templates/partials/topbar.html` — delete the Pharmacy link at ~line 81
(desktop nav pills) and ~line 127 (mobile popover). Keep the
`.med-pharmacy-btn` in `templates/medical/booking.html`.

### Step 5 — Standalone "Request any medicine" page (user feature request)
- Build a fill-out form page (e.g. `/pharmacy/request/`, new view +
  template) with free-text fields: medicine name, generic name, quantity,
  urgency (normal / urgent emergency), contact number, notes.
- POST to a new (or extended) `MedicineRequest`-backed endpoint; reuse the
  existing admin "Medicine Requests" tab for review, so staff see requests
  from both the out-of-stock modal and the new form in one queue.
- If the model needs the `student_name`/`student_id`/`urgency` fields, add a
  migration (`core/migrations/00XX_…`) — keep `medicine`/`user` nullable so
  free-text requests work without a catalog match.

### Step 6 — Mobile WebView responsiveness pass
- Add `maximum-scale=1.0, user-scalable=no` to the pharmacy viewport meta.
- Add `@media (max-width: 640px)` modal sizing to `pharmacy.css`
  (`.modal-card { width: 95vw; max-height: 90vh; overflow-y: auto; }`).
- Wrap pharmacy admin tables in `.table-responsive`; add 44px min-height to
  buttons/inputs across the pharmacy + medical pages.

### Step 7 — Verify & commit
- `python manage.py check` + `python manage.py test` (suite is large —
  run the pharmacy + navigation tests: `core.tests.PharmacyPageTest`,
  `core.tests.UnifiedHeaderTest` if present).
- Browser-check `/`, `/pharmacy/`, `/medical/` at 390px and 1280px.
- Update `docs/HANDOVER.md` changelog + this file, then commit.

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
| Android wrapper | `mobile-webview/settings.gradle.kts`, `app/build.gradle.kts`, `app/src/main/AndroidManifest.xml`, `app/src/main/java/com/niterhub/dash/MainActivity.kt`, `NotificationHelper.kt`, `EmergencyMessagingService.kt` |
| Sessions | `config/settings.py` (SESSION_EXPIRE_AT_BROWSER_CLOSE / SESSION_COOKIE_AGE) |
