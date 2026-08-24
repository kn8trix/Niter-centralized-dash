# Niter Centralized Dash - Handover Document

## Changelog — Recent Work (Aug 2026)

| § | Title | Commit(s) |
|---|---|---|
| 143 | Visual builder extended to all 11 navbar routes — SYSTEM_PAGES expanded to 13, @xframe_options_sameorigin on all views, cms/system_zone.html added to 8 templates | *(see §143)* |
| 142 | News visual builder fix — editor iframe loads real /news/ route, CMS content_json binding for editable text, preview mode shows hidden blocks | *(see §142)* |
| 141 | CMS WYSIWYG integration tests — end-to-end `CmsWysiwygIntegrationTest` (system page existence, AJAX save, student-facing rendering) | *(see §141)* |
| 140 | CMS dynamic navigation — `nav_order`/`nav_icon` fields on EditablePage, per-page icon in topbar Pages dropdown, builder toolbar inputs, admin table columns | *(see §140)* |
| 139 | Pharmacy product detail modal & card image fixes — pill placeholder fallback, `object-fit:contain` modal image, `.pd-head` padding, `max-height:85vh` scrollable modal | *(see §139)* |
| 138 | Pharmacy product image display fix — catalog serializer uses `item.image.url` (ImageField) with `image_url` fallback, media serving verified | *(see §138)* |
| 137 | E-Commerce pharmacy inventory management — CRUD views (list/add/edit/delete/toggle/adjust), image upload, stock badges, sidebar logout + Pharmacy Inventory nav link | *(see §137)* |
| 136 | Attendance page mobile layout — card overflow fix, video proportional scaling, `flex:1 1 45%` button wrap, full-width input/button on mobile | *(see §136)* |
| 135 | WebView zoom & layout settings — `setSupportZoom(false)`, `builtInZoomControls=false`, `displayZoomControls=false`, `TEXT_AUTOSIZING` layout algorithm | *(see §135)* |
| 134 | Mobile viewport optimization — `maximum-scale=1.0, user-scalable=no` on all 31 templates, global 44×44 px touch-target minimum, attendance/dashboard mobile touch-friendly CSS | *(see §134)* |
| 133 | Native QR Scanner — CameraX + ML Kit barcode detection bypasses WebView `getUserMedia`; `NiterHub.scanQR()` JS bridge; attendance page auto-selects native scanner in-app | *(see §133)* |
| 132 | Study Corner PDF-preview overlap fix (`[hidden]` display guard) + case-insensitive Student/Staff ID login (`StudentIdAuthenticationForm` on `RoleAwareLoginView`) | *(see §132)* |
| 131 | Meals remaining-count fix + news response caching; Study Corner PDF preview box, Google Drive removal, direct local/DB uploads; embedded ChromaDB vector store + RAG retrieval wired into Study Corner & Research AI | *(see §131)* |
| 130 | Navbar underline fix, modal button contrast (Rx Upload / Checkout), mobile WebView responsiveness for /news/ /attendance/ /pharmacy/ | *(see §130)* |
| 129 | NCC club-manager demo account — `NCC`/`ncc@gmail.com` linked to the NITER Computer Club (active ClubAccount, full manager capabilities) + README/handover updates | *(see §129)* |
| 128 | README solution section — official project description (modular hub + mobile app, sub-dashboards, Website Builder, Emergency Siren & Broadcast) | *(see §128)* |
| 127 | App notifications + sound without Firebase — EmergencyPollWorker (30s poll of `/api/emergency/active/`), native siren JS bridge in the dashboard banner, silence persistence | *(see §127)* |
| 126 | Repo branding & README — banner asset, feature/comprehensive README from the hackathon doc | *(see §126)* |
| 125 | Android Studio Gradle sync fix — remove open-app-as-root artifacts, align root project name, README troubleshooting | *(see §125)* |
| 124 | Dedicated Medical Staff role & portal — separate medical dashboards, medical/medical123 account, medical links removed from admin sidebar | *(see §124)* |
| 123 | Pharmacy contrast + product images, native-app-only hero redirect, "Request any medicine" page, topbar Pharmacy pill removal, Android compile fixes, mobile WebView polish | *(see §123)* |
| 122 | Student Edition Android app — branded splash + launcher icons, persistent sessions, direct dashboard landing, native permissions, FCM push with picture banners, emergency siren (+ Gradle wrapper jar/scripts) | `25789af`, `9478115` |
| 121 | Public pharmacy storefront — guest browsing/cart, hero button contrast fix, auto-seeded BD catalog | `29688ff` |
| 120 | Club dashboard sub-routes + event banner upload + event visibility sync to student portals | `5c90964` |
| 119 | Fix visual builder empty canvas — default block HTML backfill, preview-mode canvas, template-cache flush on save/publish | `a164e8a` |
| 118 | Online Pharmacy polish — BD medicine catalog seed, product detail modal, Buy Now checkout, stock requests, nav buttons, modal CSS fix | `6e5430b` |
| 117 | Website Builder overhaul — system page registration, feature blocks, live editing, UI redesign | `1908512` |
| 116 | Fix 500 on /study-corner/ — guard fileless CourseMaterial rows | `3fa4aa1` |
| 115 | Signup — show/hide password toggle | `e4d6a25` |
| 114 | Online Pharmacy module — Rx verification, checkout, order tracking, batch/expiry alerts, generic substitutes | `ddbc86a` |
| 113 | Study Corner — Academic Notes + YouTube lectures + AI Study Assistant | `76a9d50` |
| 112 | Global News — dedicated Video News section (YouTube Data API v3) | `965064e` |
| 111 | Remove email OTP verification from signup — direct registration | `1447f87` |
| 110 | Global News nav tab + /news/ page; emergency resolve verified; student-page mobile pass | `0e37bd6` |
| 109 | Visual builder — inline canvas editing + active-block sidebar sync + publish flow | `ce61dba` |
| 108 | Builder routes locked to Admin Console layout — no student nav on admin pages | `ace3441` |
| 107 | Builder edit page — auto-opening Delete Section modal fix ([hidden] vs display:grid) | `acd73c0` |
| 106 | Builder iframe fix — public pages frameable same-origin (X-Frame-Options SAMEORIGIN) | `f007cbf` |
| 105 | `seed_demo_data` command — realistic NITER demo dataset (+ MealMenu model) | `39f3488` |
| 104 | Global News & Search widget (NewsAPI service + student/admin dashboards + search API) | `991c4f8` |
| 103 | Emergency alarm persistent-silence fix + WYSIWYG student-view editor overlay | `991c4f8` |
| 102 | dash-data CI failure root cause — ALLOWED_HOSTS vs localhost host fix | `a7b0243` |
| 101 | dash-data dashboard JSON embedding — verified present, calendar grid guards green | `8905493` |
| 100 | CI hardening — pytest-proof channel layer + dash-data/Huey regression guards | `0a90ad5` |
| 99 | Test-suite Redis isolation — in-memory channel layer under the test runner | `0c38e45` |
| 98 | Emergency Alert modal — auto-open / unclosable state fix (admin dashboard) | `4a3e9ea` |
| 97 | Emergency Announcement System — banner + siren + mobile push | `ba82093` |
| 96 | Teacher Management + QR email dispatch + attendance report emails | `52735a4` |
| 95 | Medical API payload alignment — booking keys + consultation lookup | `d2bf152` |
| 94 | Mobile responsiveness (calendar / clock / attendance) + Transport payment gateway modal | `e8f3332` |
| 93 | Attendance page dark-mode theming (shared CSS tokens) | `85589ca` |
| 90 | Dynamic user names on all passes + cleaned-up profile dropdown | `71ed77b` |
| 91 | QR Attendance System + Academic Calendar grid fix | `f832515` |
| 92 | Two-step signup verification (Django Gmail SMTP) | `46585c0` |
| 89 | Meal Ticket System — monthly subscription + QR passes + 9 PM cancel rule | `a73e4a5` |
| 88 | Google OAuth — 401/Invalid-Credentials hardening + upload session guard | `62ba895` |
| 87 | Medical Booking — form state binding + AJAX submission fix | `bf1a05e` |
| 86 | Final Integration Status — Module Matrix, OAuth Refresh & Health Check | `fc74649` |
| 85 | Android WebView Wrapper (`/mobile-webview`) | `83b1d80`, `fc74649` |
| 84 | System Audit + Reports Module Upgrade (severity / attachments / envelope) | `b5fdb0e` |
| 83 | Google OAuth / Drive — Recurring "Google Access Required" Popup Fix | `c983640` |

See the end of this document for full sections. Older feature history follows
in §1–§82.

---

## 1. Project Overview
The **Niter Centralized Dash** is a student-centric dashboard designed to provide a unified interface for academic management, official notices, and campus services. It follows a "Warm Minimal Notion-style" aesthetic, focusing on readability, clean layouts, and subtle interactions.

## 2. Design System

### 2.1 Color Palette
The theme is built around a warm, paper-like background with neutral accents.

| Token | Hex Code | Usage |
| :--- | :--- | :--- |
| **Base (Background)** | `#FBF9F5` | Primary background color for the app. |
| **Card** | `#FFFFFF` | Background for content cards and sidebar. |
| **Border** | `#EBE6DF` | Subtle separators between sections. |
| **Main (Text)** | `#2B2927` | Primary text color for high readability. |
| **Accent** | `#EADCC9` | Used for active states, buttons, and highlights. |
| **Accent Hover** | `#D8CAB4` | Slightly darker accent for hover interactions. |

### 2.2 Typography
- **Font Family:** Inter (Google Fonts)
- **Weights:** 300 (Light), 400 (Regular), 500 (Medium), 600 (Semi-bold), 700 (Bold).
- **Style:** Antialiased for a crisp, modern look.

## 3. Layout & Structure

### 3.1 Sidebar
- **Width:** Fixed at `256px` (w-64).
- **Behavior:** Fixed to the left, scrolls independently if content exceeds height.
- **Navigation Items:**
    - **Dashboard:** Main landing view.
    - **Academic & Notes:** Course materials and personal notes.
    - **Official Notices:** Institutional announcements.
    - **Transport Tickets:** Bus routes, seat booking, QR boarding pass (`/transport/`).
    - **Meal System:** Meal slot ratio, claim, supply stats (`/meals/`).
    - **Medical Booking:** Appointment scheduling.
    - **Clubs & Events:** Club discovery + events (`/clubs/`). *Note:* the
      executive workspace is **not** in the public sidebar — it moved behind the
      role-protected `/dashboard/club/` (and legacy `/clubs/manage/`) routes,
      see §77 and §86.
- **Footer:** User profile section with avatar and logout option (posts to `/logout/` when signed in).

### 3.2 Main Content Area
- **Margin:** Offset by `256px` on desktop (`lg:ml-64`); full-width on mobile (`ml-0`) so content reflows when the drawer is hidden.
- **Header:** Sticky top bar with page title, global search, and notification bell. On mobile the hamburger sits inline next to the title and the search bar wraps to its own row.
- **Grid System:** Responsive grid using Tailwind CSS utility classes.

## 4. Implemented Templates

### 4.1 Dashboard Home (`templates/dashboard/home.html`)
A comprehensive student dashboard (redesigned — see §73 for the full
overhaul) with:
- **Live Bangladesh Clock Card:** real-time Asia/Dhaka time (UTC+6) with a
  next-class countdown and NOW / NEXT UP highlighting on today's routine.
- **Today's Class Routine Panel:** the signed-in user's weekly schedule
  (per-user `Routine` JSON, set via Settings → Routine or the AI extractor),
  with the current/upcoming class auto-highlighted against the live clock.
- **Interactive Academic Calendar:** monthly grid (Saturday-first) fed by
  `AcademicEvent` rows — exams, holidays, assignments — with prev/next month
  navigation via `GET /api/calendar/events/?month=YYYY-MM`.
- **Recent Activity:** the user's latest notes / transport / medical / meals /
  clubs actions merged into one reverse-chronological feed.
- **Quick Campus Info:** latest published notice + shortcut tiles to the
  standalone service pages.
- **Bottom Split Section:** Recent Official Notices + Academic Notes shortcuts
  (compact, linking to `/notices/` and `/academic-notes/`).

### 4.2 Ticketing System (`templates/ticketing/tickets.html`)
Bus and meal ticket management with:
- **Online Meal Ticket Counter:**
    - Live status badge (140/200 remaining with pulsing indicator).
    - Meal type selector (Breakfast/Lunch/Dinner) with icons.
    - "Claim Meal Ticket" button with CSRF protection.
- **Transport Ticket Booking:**
    - Table with columns: Route, Departure Time, Seats Available, Action.
    - Color-coded seat availability badges (Green/Orange/Red).
    - "Book Ticket (QR)" buttons with disabled state for full routes.

### 4.3 Medical Booking (`templates/medical/booking.html`)
Appointment scheduling interface with:
- **Appointment Form:**
    - Doctor selection dropdown (General Physician, Pediatrician, etc.).
    - Date picker with clean styling.
    - Time slot grid (6 slots from 09:00 AM to 05:00 PM).
    - Reason for Visit textarea.
    - "Confirm Appointment" submit button.
- **Upcoming Appointments Card:**
    - Sticky sidebar showing the signed-in student's **live** appointment rows
      (no mock markup) with status badges (Confirmed/Pending), date and time.
    - Booking is **AJAX**: the form submits via `fetch()` to
      `/book-appointment/` (`data.success === true` → success toast, the new
      appointment is prepended to the list, the form resets — no page
      reload). Field errors clear as soon as the visitor picks a doctor / date
      / slot. Full details in §87.

### 4.4 Academic Notes (`templates/academic/notes.html`)
Academic materials and course management:
- **Header Section:** Welcome message with "Upload Notes" button.
- **Course Cards Grid:**
    - CS101 - Introduction to AI
    - MATH201 - Linear Algebra
    - PHY101 - Physics Lab
    - CS201 - Data Structures
    - Each with progress bars and file counts.
- **Recent Assignments Table:**
    - Assignment name, course, due date, and status badges.
    - Statuses: In Progress, Not Started, Submitted, Urgent.

### 4.5 Official Notices (`templates/notices/notices.html`)
Institutional announcements and events:
- **Header Section:** Category filter dropdown.
- **Notices List:**
    - Color-coded border accents (Red=Urgent, Blue=Academic, Purple=Event, Green=Workshop).
    - Each notice includes: title, description, source, date, and view count.
    - Sample notices: Exam Schedule Update, Library Hours, Tech Fest, Holiday Schedule, Career Workshop.

### 4.6 Notes Engine (`templates/notes/notes_engine.html`)
Markdown notebook-style interface with:
- **Left Sidebar (File Browser):**
    - Search bar filtering folders, PDFs, and notes by text.
    - Upload button for new documents (Google Drive).
    - Folder tree — **live** `Department`/`Course` rows: one folder per department with a course count; clicking one filters the PDF list (§43).
    - Recent PDF list — **live** `CourseMaterial` rows (course code, size, upload date) linking to the real file (§43).
    - My Notes — the signed-in user's `UserNote` rows; clicking one loads its content via `GET /api/notes/<id>/` instead of embedding it in the HTML.
- **Main Pane (Markdown Editor):**
    - Title input field.
    - Action buttons: "Save Note", "Generate AI Summary", "Extract Keywords", "Export as PDF" — all server-backed.
    - Monospace textarea for note-taking.
- **Bottom Preview Box:**
    - AI summary display with formatted content.
    - Keywords extraction preview.
    - Status indicator showing summary readiness.

### 4.7 Host Portal Base (`templates/host/host_base.html`)
Host-side layout extending the student base template with a dedicated host sidebar:
- **Host Sidebar:** Host logo, host menu (Medical Admin Dashboard, Medical Dashboard, Appointments, Today's Queue, Reports, Settings), and a staff profile footer.
- **Reuses** `base.html` via `{% block sidebar %}` so the host sidebar replaces the student navigation while keeping the same header and content shell.

### 4.8 Medical Host Dashboard (`templates/host/medical/dashboard.html`)
Staff view of medical appointments with:
- **Summary Cards:** Total, Pending, Confirmed, Completed, Cancelled, and Today's Queue counts.
- **Search & Filter Bar:** Search by student name/ID plus status filter (All, Today, Pending, Confirmed, Completed, Cancelled).
- **Appointments Table:** Student details, doctor, date/time, reason, status badge, and inline actions (View, Edit, Assign, Confirm, Return, Cancel, Mark Completed).
- **Real appointment data + status actions** — queries live `MedicalAppointment` rows (see section 36): Confirm / Cancel / Mark Completed POST to `/api/medical/appointments/<id>/status/`, which persists the state change and pushes a real-time `Notification` to the student.

### 4.9 Medical Admin Dashboard (`templates/host/medical/admin_dashboard.html`)
Admin-only medical management interface at `/medical/admin/` with:
- **Summary Cards:** Total, Pending, Confirmed, and Cancelled appointment counts.
- **Appointment Management (real):** Multi-field filter form (keyword, student name, student ID, date, status, department, doctor) querying live `MedicalAppointment` rows; table with Confirm / Cancel / View Details actions wired to the persistent status endpoint.
- **Appointment Details Panel:** Full student and appointment info (contact, reason, doctor, booking time).
- **Medical Chat Management:** Mock chat threads with statuses (Active, Waiting, Resolved) — **backend pending**.
- **Doctor Schedule (real, §63):** Doctor list rendered from the persisted `Doctor` catalog with today's `DoctorSchedule` — daily **availability toggles** and **slot-cap inputs** POST to `/api/medical/doctor-availability/`; the booking flow enforces both (unavailable doctor or full daily cap → 409).
- **Medical Content Management:** Mock content sections (Health Tips, Disease Awareness, First Aid, Medical Facilities, Emergency Contacts, Medical News) — **backend pending**.
- **Home Page Medical Information:** Mock editable sections for the medical center's public pages — **backend pending**.

### 4.10 Clubs & Events (`templates/clubs.html`)
Frontend-only Club & Event **student view** at `/clubs/` — a standalone page (own `clubs.css`, exact warm palette `#faf9f6` / `#ffffff` / `#f0ebe1` / `#e8e2d8`) driven entirely by mock JavaScript data (no backend/database). The **executive workspace is now real**: `/clubs/manage/` (`club_admin.html`) syncs registrations/members from the linked Google Sheet and verifies bKash/Nagad TrxIDs against the sheet with real-time notifications (see section 36).
- **Student View:**
    - Featured clubs showcase (Computer Club, Electronics Club, Cultural Society, Sports Club) rendered from JS with active status badges and member counts.
    - Upcoming events grid (date, time, location, description, fee tags "Free" / "৳200 BDT") with a "Register Now" button that opens a mock registration modal (Student Name, Student ID, Payment Method bKash/Nagad, Trx ID).
- **Club Executive Workspace:**
    - Stat summary cards: Total Members, Active Registrations, Event Revenue, Pending Approvals.
    - Mock registrations & payment tracking table (student name/ID, event, bKash/Nagad + TrxID chips, amount, Verified / Pending Review badges) rendered from JS.
    - Announcement Publisher form (title, target audience dropdown, details) with mock confirmation toast.
- The view (`clubs_dashboard`) is a pure stub rendering `clubs.html`; toggle + modal + toast are client-side vanilla JS with mock data arrays in the template.

### 4.11 Transport Online Ticket System (`templates/transport.html`)
Transport booking dashboard at `/transport/` (`static/css/transport.css`) — **booking is backend-wired** (see section 35): the seat form POSTs to `/book-transport/` and renders the real QR boarding pass; the route catalog / live bus status tracker remain mock JS data.
- **Live Status Tracker** — pulsing status badges per route ("On Time" green, "In Transit" blue, "Arriving in 10 mins" amber).
- **Bus Routes & Schedules** — route cards (Route 1: Campus → Town Center, etc.) with driver info, departure times, and color-coded live seats badges ("12 / 40 seats left").
- **Seat Selector / Booking Form** — route dropdown, trip-time chips, passenger name, and a clickable 40-seat grid (booked seats disabled); "Book Seat" validates and generates the pass, then live-updates seats-left on the route cards.
- **Digital Boarding Pass** — visual QR ticket (deterministic SVG QR placeholder) showing passenger, route, assigned seat, departure time, and token.

### 4.12 Online Meal Ticket System (`templates/meals.html`)
Meal ticket dashboard at `/meals/` (`static/css/meals.css`) — **claiming is backend-wired** (see section 35): "Claim Meal Ticket" POSTs to `/claim-meal/` and renders the backend-issued `#MEAL-XXXX` pass; the supply stat cards / progress ring seed values remain mock JS data.
- **Live Meal Ratio Counter** — animated SVG progress ring (142 / 200 slots claimed, 58 remaining).
- **Meal Booking & Claim Card** — Lunch/Dinner selector chips, date picker, and a "Claim Meal Ticket" button that issues a pass and live-updates the ring + supply stats.
- **Active Digital Meal Pass** — coupon-style card (perforated edges) with token (`#MEAL-8921`), student name, meal type, date, and a "Mark as Redeemed" toggle (Unused → Redeemed).
- **Cafeteria Supply Overview** — stat cards for meals prepared, tickets claimed, remaining supply, and slots remaining.

## 5. Template Usage

### 5.1 Base Template
All templates extend `templates/base.html` which provides:
- Fixed sidebar with navigation (off-canvas drawer on mobile, toggled by the inline hamburger in the sticky header).
- Sticky header with search and notifications.
- Consistent styling and theme colors.
- Responsive design: mobile drawer with dark backdrop overlay (tap-away or tapping any nav link closes it), `overflow-x-hidden` on the body to prevent horizontal scroll.

### 5.2 Creating New Pages
To create a new page, extend the base template:

```html
{% extends "base.html" %}

{% block title %}Page Name - Niter Hub{% endblock %}

{% block header %}Page Header{% endblock %}

{% block content %}
    <!-- Add your modular components here -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Component 1 -->
        <div class="bg-card rounded-xl border border-border p-6">
            ...
        </div>
    </div>
{% endblock %}
```

### 5.3 Form Guidelines
- Always include `{% csrf_token %}` in Django forms.
- Use clean HTML form tags with proper `name` attributes.
- Follow the color scheme: `bg-base` for inputs, `border-border` for borders.
- Use `focus:ring-2 focus:ring-accent` for focus states.

## 6. Technical Stack
- **Backend:** Django 4.2 (`requirements.txt` pins `django>=4.2,<5.0`)
- **Config:** `django-environ` — all secrets/settings from environment / `.env`
- **Real-time:** Django Channels 4 + Daphne (ASGI — WebSockets for live notifications); `channels-redis` in production with in-memory fallback. channels/daphne implicit deps (`asgiref`, `autobahn`, `twisted[tls]`) are pinned explicitly in `requirements.txt` (see §42)
- **Static:** WhiteNoise (`CompressedStaticFilesStorage`) — production static serving + `collectstatic`
- **Auth:** django-allauth (Google OAuth) + Django sessions; Google ID-token verification via `PyJWT[crypto]` (allauth's `socialaccount` extra — pinned in `requirements.txt`, see §42)
- **Google APIs:** `google-api-python-client`, `gspread` (Drive notes upload, club sheets)
- **Research AI / LLM (OpenRouter):** `requests`-based chat-completions client in `services/openrouter.py`. Zero-cost models — default `OPENROUTER_DEFAULT_MODEL=nvidia/nemotron-3.5-lightning:free` (NVIDIA Nemotron 3.5 Lightning, free tier, §67) with automatic single retry on HTTP 429/503 via `OPENROUTER_FALLBACK_MODEL=openrouter/free` (auto free router). `OPENROUTER_BASE_URL=https://openrouter.ai/api/v1/chat/completions`, `OPENROUTER_ENABLED = bool(OPENROUTER_API_KEY)`; page falls back to the deterministic offline engine when the key is unset. Reference PDF/DOCX text extracted server-side by `services/parser.py` (`pypdf` + `python-docx`). The student dashboard's AI routine extractor (§73) adds `OPENROUTER_VISION_MODEL` (default `meta-llama/llama-3.2-11b-vision-instruct:free`) for image scans and reuses the text models for PDF/DOCX.
- **Frontend Styling:** Tailwind CSS (via CDN for rapid development)
- **Icons:** Heroicons (SVG) for a consistent, clean look.
- **Fonts:** Inter (Google Fonts)
- **JavaScript:** Vanilla JS for mobile sidebar toggle and basic interactions.

## 7. Getting Started (Local Development)

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Setup Instructions

```bash
# 1. Clone the repository
git clone https://github.com/kn8trix/Niter-centralized-dash.git
cd Niter-centralized-dash

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# OR on Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure the environment
cp .env.example .env   # then set SECRET_KEY / DEBUG=True for local dev

# 5. Apply migrations (fresh DBs get seed data for departments/clubs)
python manage.py migrate

# 6. Run the development server (daphne serves HTTP + WebSockets)
python manage.py runserver 0.0.0.0:8000

# 7. Open your browser
# Navigate to: http://127.0.0.1:8000/

# For production, also run:
python manage.py collectstatic --noinput
python manage.py check --deploy
```

### Available Pages
| Page | URL | Description |
| :--- | :--- | :--- |
| **Public Homepage** | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) | Warm light landing page (public nodes, NITER content) |
| **Dashboard** | [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/) | Main student dashboard (moved from `/`) |
| **Academic & Notes** | [http://127.0.0.1:8000/academic-notes/](http://127.0.0.1:8000/academic-notes/) | Courses & assignments |
| **Official Notices** | [http://127.0.0.1:8000/notices/](http://127.0.0.1:8000/notices/) | Announcements & events |
| **Tickets** | [http://127.0.0.1:8000/tickets/](http://127.0.0.1:8000/tickets/) | Meal & transport tickets |
| **Medical** | [http://127.0.0.1:8000/medical/](http://127.0.0.1:8000/medical/) | Appointment booking |
| **Notes Engine** | [http://127.0.0.1:8000/notes/](http://127.0.0.1:8000/notes/) | Notes engine |
| **Medical Admin** | [http://127.0.0.1:8000/medical/admin/](http://127.0.0.1:8000/medical/admin/) | Medical admin dashboard |
| **Medical Host** | [http://127.0.0.1:8000/host/medical/](http://127.0.0.1:8000/host/medical/) | Medical host dashboard (`/host/` redirects here) |
| **Clubs & Events** | [http://127.0.0.1:8000/clubs/](http://127.0.0.1:8000/clubs/) | Club discovery + executive workspace |
| **Transport Tickets** | [http://127.0.0.1:8000/transport/](http://127.0.0.1:8000/transport/) | Bus routes, seat booking, QR pass |
| **Meal System** | [http://127.0.0.1:8000/meals/](http://127.0.0.1:8000/meals/) | Meal slot ratio, claim, supply stats |
| **Login** | [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/) | Student/staff sign-in page |
| **Logout** | [http://127.0.0.1:8000/logout/](http://127.0.0.1:8000/logout/) | Sign out (POST) |
| **Settings** | [http://127.0.0.1:8000/settings/](http://127.0.0.1:8000/settings/) | Tabbed settings dashboard: notifications, account/Google OAuth, display (theme + timezone) |
| **Sign Up** | [http://127.0.0.1:8000/signup/](http://127.0.0.1:8000/signup/) | Student sign-up (creates account + profile) |
| **Profile** | [http://127.0.0.1:8000/profile/](http://127.0.0.1:8000/profile/) | Virtual student ID card + booking history |
| **System Admin** | [http://127.0.0.1:8000/admin-dashboard/](http://127.0.0.1:8000/admin-dashboard/) | Staff-only dashboard (users, notices, transport, security) |
| **Cafeteria Admin** | [http://127.0.0.1:8000/cafeteria/admin/](http://127.0.0.1:8000/cafeteria/admin/) | Staff-only meal slots, inventory, QR redemption |
| **Club Management** | [http://127.0.0.1:8000/clubs/manage/](http://127.0.0.1:8000/clubs/manage/) | Staff-only club executive workspace |
| **Checkout** | [http://127.0.0.1:8000/checkout/](http://127.0.0.1:8000/checkout/) | Payment gateway (bKash/Nagad/Rocket) for events, transport, meals |
| **Research AI** | [http://127.0.0.1:8000/research-ai/](http://127.0.0.1:8000/research-ai/) | Academic research & thesis assistant — OpenRouter-backed chat, persisted threads, PDF/DOCX reference parsing (server-driven; §65–§67) |
| **Departments** | [http://127.0.0.1:8000/departments/](http://127.0.0.1:8000/departments/) | Department directory & hub (`/departments/<slug>/`) |
| **Builder** | [http://127.0.0.1:8000/builder/](http://127.0.0.1:8000/builder/) | Website Builder dashboard (super-admin) + `/builder/edit/<slug>/` editor |
| **Builder Pages** | [http://127.0.0.1:8000/page/<slug>/](http://127.0.0.1:8000/page/<slug>/) | Public render of builder-authored pages (e.g. `/page/research-ai/`) |
| **Student Reports** | [http://127.0.0.1:8000/dashboard/student/reports/](http://127.0.0.1:8000/dashboard/student/reports/) | Reports & Feedback — submit + personal history (login required) |
| **Report Inbox (Admin)** | [http://127.0.0.1:8000/dashboard/admin/reports/](http://127.0.0.1:8000/dashboard/admin/reports/) | Staff inbox — triage all student reports (staff only) |

### Troubleshooting
- **Port already in use:** Use `python manage.py runserver 8080` to run on a different port.
- **ModuleNotFoundError:** Ensure virtual environment is activated (`source venv/bin/activate`).
- **`ModuleNotFoundError: No module named 'jwt'` (allauth Google provider):** stale venv or pre-§42 `requirements.txt` — the Google provider needs `PyJWT[crypto]`. Re-run `pip install -r requirements.txt` (adds the pin; see §42).
- **Template errors:** Check that all templates are in the `templates/` directory.

## 8. File Structure
```
Niter-centralized-dash/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── venv/                        # Virtual environment (not in git)
├── config/
│   ├── __init__.py
│   ├── settings.py              # Django settings (channels, allauth, ASGI, CHANNEL_LAYERS)
│   ├── urls.py                  # Main URL configuration
│   ├── wsgi.py                  # WSGI application
│   └── asgi.py                  # ASGI application (HTTP + WebSockets via Channels)
├── core/
│   ├── __init__.py
│   ├── models.py                # StudentProfile, PageTemplate/EditablePage/ContentBlock,
│   │                            # GoogleUserToken, Notification, Notice, Course/CourseMaterial,
│   │                            # MealSubscription/MealTicket, TransportBooking, MedicalAppointment,
│   │                            # Department/FacultyMember/ClassRoutine, Club/ClubEvent/ClubRegistration,
│   │                            # PaymentTransaction, UserNotificationPreference, UserNote
│   ├── views.py                 # View functions (incl. claim_meal/book_transport/book_appointment)
│   │                            # + staff endpoints: redeem_meal_ticket, update_appointment_status,
│   │                            #   verify_club_transaction_view, update_user_role, create_notice,
│   │                            #   join_club, _process_checkout, notes actions, research_query
│   ├── urls.py                  # App URL routes
│   ├── consumers.py             # NotificationConsumer (WebSocket, user_<id> groups) + notify_user
│   ├── routing.py               # WebSocket URL routing (ws/notifications/)
│   ├── admin.py                 # Admin registrations (builder + Google + notifications + services)
│   ├── decorators.py            # superuser_required etc.
│   ├── google_service.py        # Google Drive/Sheets service layer (incl. verify_club_transaction)
│   ├── context_processors.py    # Centralized ENDPOINTS registry
│   ├── templatetags/
│   │   └── builder_tags.py      # render_block template tag
│   └── migrations/
│       ├── 0001_initial.py      # StudentProfile
│       ├── 0002_*.py            # PageTemplate/EditablePage/ContentBlock
│       ├── 0003_googleusertoken.py
│       ├── 0004_notification.py
│       ├── 0005_*.py            # MealSubscription/MealTicket/TransportBooking/MedicalAppointment
│       ├── 0006_*.py            # MealTicket.redeemed_at + Notification 'club' category
│       ├── 0007_*.py            # Notice + Course/CourseMaterial
│       ├── 0008_*.py            # Department/FacultyMember/ClassRoutine/Club/ClubEvent/ClubRegistration
│       ├── 0009_seed_*.py       # Seed data (5 departments, faculty, routines, clubs, events)
│       ├── 0010_*.py            # PaymentTransaction/UserNotificationPreference/UserNote
│       └── 0011_*.py            # Database indexes (db_index + composite)
├── host/
│   ├── __init__.py
│   ├── views.py                 # Host portal views (medical host + admin dashboards)
│   ├── urls.py                  # Host app URL routes
│   └── tests.py                 # Host app tests
├── services/                   # Third-party service adapters (§65)
│   ├── __init__.py
│   ├── openrouter.py            # OpenRouter chat-completions client (headers,
│   │                            #   system prompt, typed error hierarchy, 30s cap)
│   └── parser.py                # PDF/DOCX → plain-text extraction for references
├── static/
│   └── css/
│       ├── theme.css            # Global design tokens (:root variables)
│       ├── main.css             # Public homepage warm light styles
│       ├── auth.css             # Login page styles
│       ├── clubs.css            # Clubs & Events page styles
│       ├── transport.css        # Transport ticket page styles
│       ├── meals.css            # Meal ticket page styles
│       ├── topbar.css           # Shared topbar/nav pills/profile popover/intro/toast
│       ├── dashboard.css        # Student dashboard styles
│       ├── medical.css          # Medical booking page styles
│       ├── notices.css          # Notices page styles
│       ├── notes.css            # Academic notes drive styles
│       ├── admin.css            # Shared System Admin / Cafeteria / Club admin styles
│       ├── signup.css           # Sign up page styles
│       ├── settings.css         # Account settings page styles
│       └── profile.css          # Virtual student ID card styles
├── templates/
│   ├── index.html               # Public homepage (warm light hero, about/medical nodes)
│   ├── login.html               # Standalone sign-in page
│   ├── clubs.html               # Clubs & Events (frontend-only, mock JS data)
│   ├── transport.html           # Transport Online Ticket System (mock JS data)
│   ├── meals.html               # Online Meal Ticket System (mock JS data)
│   ├── signup.html              # Student sign-up (creates User + StudentProfile)
│   ├── settings.html            # Account settings (password, toggles, theme)
│   ├── profile.html             # Virtual student ID card + booking history
│   ├── sys_admin.html           # System Admin dashboard (4 tabs, staff-only)
│   ├── cafeteria_admin.html     # Cafeteria admin (slots, inventory, QR redemption)
│   ├── club_admin.html          # Club executive admin (/clubs/manage/)
│   ├── partials/
│   │   └── topbar.html          # Shared top navigation (brand, nav pills, profile popover)
│   ├── base.html                # Base template with sidebar & header
│   ├── dashboard/
│   │   └── home.html            # Student dashboard
│   ├── academic/
│   │   └── notes.html           # Academic materials & courses
│   ├── notices/
│   │   └── notices.html         # Official announcements
│   ├── ticketing/
│   │   └── tickets.html         # Legacy meal & transport tickets page
│   ├── medical/
│   │   └── booking.html         # Medical appointments
│   ├── host/
│   │   ├── host_base.html       # Host portal base (host sidebar)
│   │   └── medical/
│   │       ├── dashboard.html       # Medical host dashboard
│   │       └── admin_dashboard.html # Medical admin dashboard
│   └── notes/
│       └── notes_engine.html    # Notes engine
└── docs/
    └── HANDOVER.md              # This documentation
```

## 9. Django Configuration

### Key Settings (`config/settings.py`)
- **Environment-driven (django-environ):** `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DATABASE_URL`, `REDIS_URL` read from the environment / `.env` (see `.env.example`). `DEBUG` **defaults to False**; `SECRET_KEY` **fails closed** when `DEBUG=False` and unset.
- **DEBUG / ALLOWED_HOSTS:** no longer hardcoded — from `.env` (dev: `DEBUG=True`, `ALLOWED_HOSTS=localhost,127.0.0.1`).
- **INSTALLED_APPS:** `daphne` (first, so `runserver` serves ASGI), `django.contrib.admin/auth/contenttypes/sessions/messages/staticfiles/sites`, `channels`, allauth (`allauth`, `allauth.account`, `allauth.socialaccount` + Google provider), `core`
- **MIDDLEWARE:** Security, **WhiteNoise**, Session, Common, Csrf, Auth, `allauth.account.middleware.AccountMiddleware`, Messages, **XFrameOptions** (clickjacking)
- **TEMPLATES DIRS:** `[BASE_DIR / 'templates']` — context processors include `request`, `auth`, `messages`, and `core.context_processors.endpoints`
- **DATABASES:** SQLite by default (`sqlite:///db.sqlite3`); set `DATABASE_URL` (e.g. Postgres) for production
- **AUTH SETTINGS:** `LOGIN_URL='/login/'`, `LOGIN_REDIRECT_URL='/dashboard/'`, `LOGOUT_REDIRECT_URL='/'`
- **REAL-TIME:** `ASGI_APPLICATION = 'config.asgi.application'`; `CHANNEL_LAYERS` uses **`channels_redis`** when a reachable `REDIS_URL` is configured, otherwise falls back to `InMemoryChannelLayer` (startup ping probe; `notify_user` never raises on a runtime outage). Under the **test runner the layer is always in-memory** (`_running_tests()` — `'test' in sys.argv` or the `TESTING` env var), so a flaky local/CI Redis can never fail the WebSocket/consumer tests (§99)
- **GOOGLE OAUTH:** `SITE_ID = 1`; `SOCIALACCOUNT_PROVIDERS['google']` scopes profile/email + Drive (app-data) + Sheets with offline/consent auth params (refresh tokens persisted in `GoogleUserToken`)
- **STATIC:** `STATICFILES_DIRS = [BASE_DIR / 'static']`, `STATIC_ROOT = staticfiles/`, WhiteNoise `CompressedStaticFilesStorage`; run `collectstatic` for production
- **SECURITY (DEBUG=False only):** `SECURE_SSL_REDIRECT`, `SECURE_PROXY_SSL_HEADER`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, HSTS (+subdomains/preload), `SECURE_REFERRER_POLICY` — `manage.py check --deploy` is clean

### Run the ASGI/dev server
Because `daphne` is first in `INSTALLED_APPS`, `python manage.py runserver` serves both HTTP and WebSockets — no extra `--asgi` flag needed.

### Environment Variables (Required — see `.env.example`)
Copy `.env.example` to `.env` and fill in values. Real environment variables (set by your process manager / hosting platform) always take precedence over `.env`.

```env
# Required
SECRET_KEY=your-long-random-secret      # fails startup when DEBUG=False and unset
DEBUG=False                            # MUST be False in production
ALLOWED_HOSTS=niter.edu.bd,www.niter.edu.bd

# Optional
DATABASE_URL=postgres://user:pass@localhost:5432/niter_db   # unset → SQLite
REDIS_URL=redis://127.0.0.1:6379/0     # unset/unreachable → in-memory channel layer (tests always in-memory — §99)
CSRF_TRUSTED_ORIGINS=https://niter.edu.bd
SECURE_SSL_REDIRECT=True               # production-only flags (DEBUG=False)
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## 10. Git Repository
- **Repository:** [https://github.com/kn8trix/Niter-centralized-dash](https://github.com/kn8trix/Niter-centralized-dash)
- **Branch:** `main` (work-in-progress lives on `taj` and gets merged into `main`)
- **Git Ignore:** `venv/`, `.venv/`, `__pycache__/`, `*.pyc`, `.env`, `db.sqlite3`

## 11. API Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | `/claim-meal/` | Claim a meal ticket (`claim_meal`, `@login_required`, atomic — validates subscription, daily capacity, generates `#MEAL-XXXX`, pushes notification) |
| POST | `/book-transport/` | Book a transport seat (`book_transport`, `@login_required`, atomic — seat conflicts → 409, QR token, notification) |
| POST | `/book-appointment/` | Schedule a medical appointment (`book_appointment`, `@login_required`, atomic — slot double-booking → 409, notification) |
| GET | `/api/notifications/` | Fetch unread count + 10 most recent notifications (`fetch_notifications`, `@login_required`) |
| POST | `/api/notifications/<id>/read/` | Mark one of the user's notifications as read (`mark_notification_read`, `@login_required`) |
| WS | `ws/notifications/` | Real-time notification stream (`NotificationConsumer`, joins `user_<id>` group) |
| GET | `/api/notes/upload/` | Upload a note to the user's Google Drive (`@login_required`) |
| GET | `/clubs/dashboard/sheets/` | Fetch club Google Sheet records (staff only) |
| POST | `/clubs/dashboard/sheets/append/` | Append a row to the club Google Sheet (staff only) |
| GET | `/api/builder/create-page/` | Super-admin: create a builder page |
| POST | `/api/builder/save-block/` | Super-admin: save a ContentBlock |
| POST | `/api/builder/save-css/` | Super-admin: save page custom CSS |
| POST | `/api/cafeteria/redeem/` | Staff: validate a `#MEAL-XXXX` token, mark `is_redeemed=True` + `redeemed_at` (`redeem_meal_ticket`) |
| POST | `/api/cafeteria/batch-redeem/` | Staff: bulk-redeem meal coupons — `tokens` list or `all_today=true`; per-token results (`batch_redeem_meal_tickets`, §63) |
| POST | `/api/medical/doctor-availability/` | Staff: upsert a `DoctorSchedule` row (daily availability toggle + slot cap, §63) |
| POST | `/api/medical/appointments/<id>/status/` | Staff: persist appointment status changes + notify the student (`update_appointment_status`) |
| POST | `/api/clubs/verify-transaction/` | Staff: mark a TrxID **Verified** in the club Google Sheet + notify the student (`verify_club_transaction_view`) |
| POST | `/api/admin/update-role/` | Superuser: toggle `is_staff` / `is_superuser` with self-demotion + last-superuser guards (`update_user_role`) |
| POST | `/api/notices/create/` | Staff: persist a `Notice` (published/draft); publishing broadcasts a real-time notification to every active user (`create_notice`) |
| POST | `/api/clubs/join/` | Student: create a pending `ClubRegistration` (duplicate → 409, club lead notified) (`join_club`) |
| POST | `/checkout/` | Student: validate wallet payment, persist a `PaymentTransaction` with a unique `NTR-` id; meal purpose activates the `MealSubscription` (`_process_checkout`) |
| GET | `/api/notes/<id>/` | Student: fetch one `UserNote` to load into the editor (owner-scoped 404) |
| POST | `/api/notes/save/` | Student: create/update a `UserNote` (owner-scoped; `note_id` updates instead of duplicating) |
| POST | `/api/settings/google-unlink/` | Student: disconnect Google account (deletes `SocialAccount` + `GoogleUserToken`) |
| POST | `/api/notes/summarize/` | Student: server-side extractive TF summarization of note content |
| POST | `/api/notes/keywords/` | Student: TF keyword ranking for note content |
| POST/GET | `/api/notes/export/` | Student: export a `UserNote` as `.txt` or a dependency-free generated PDF |
| POST | `/research-ai/api/query/` | Student: OpenRouter-backed research chat — `message` + `citation_style` + optional PDF/DOCX `file` → `{status, response, thread_id, engine}`; offline engine fallback when `OPENROUTER_API_KEY` is unset; friendly 429/504/502 error payloads (§65) |
| GET | `/research-ai/api/threads/` | Student: list the signed-in user's research threads (title, citation style, updated-at) (§65) |
| GET/DELETE | `/research-ai/api/threads/<id>/` | Student: fetch a thread's full message history / delete the thread (owner-scoped 404) (§65) |
| POST | `/api/research/query/` | Legacy alias of the query endpoint (kept so old clients/tests keep working) |
| GET | `/notices/` | Published `Notice` feed with optional `?category=` filter (server-rendered) |
| GET | `/academic-notes/` | Live `Course`/`CourseMaterial` drive (server-rendered) |
| GET | `/departments/` + `/departments/<slug>/` | Live department directory + detail hubs (server-rendered) |
| GET | `/` | Public homepage (glassmorphism landing page) |
| GET | `/dashboard/` | Student dashboard (moved from `/`) |
| GET | `/clubs/` | Clubs & Events (frontend-only student view) |
| GET | `/transport/` | Transport ticket system (booking backend-wired, section 35) |
| GET | `/meals/` | Meal ticket system (claiming backend-wired, section 35) |
| GET | `/medical/admin/` | Medical admin dashboard (real appointments, section 36) |
| GET | `/host/medical/` | Medical host dashboard (real appointments, section 36) |
| GET | `/host/` | Host portal index (redirects to medical host dashboard) |
| POST | `/login/` | Sign in (Django `LoginView`, redirects to `/dashboard/`) |
| POST | `/logout/` | Sign out (Django `LogoutView`, redirects to `/`) |
| GET | `/settings/` | Account settings (password change, toggles, theme) |
| GET | `/signup/` | Student sign-up (creates account + profile) |
| GET | `/profile/` | Virtual student ID card + booking history |
| GET | `/admin-dashboard/` | System Admin dashboard (staff-only, 4 tabs) |
| GET | `/cafeteria/admin/` | Cafeteria admin (staff-only) |
| GET | `/clubs/manage/` | Club admin / executive workspace (staff-only) |
| GET/POST | `/api/reports/` | Student: list own reports / submit one (`@login_required`, JSON or form body) |
| GET | `/api/admin/reports/` | Staff: all reports with student details, `?status=` / `?category=` filters |
| PATCH | `/api/admin/reports/<id>/` | Staff: update status + admin_notes; notifies the student in real time |
| GET | `/dashboard/student/reports/` | Student Reports & Feedback page (login required) |
| GET | `/dashboard/admin/reports/` | Staff report inbox (staff only) |

## 12. Next Steps

### Backend Status Summary

**Backend live (as of section 37):** everything below is implemented, tested (320 tests), and verified end-to-end:
- auth + accounts (login/signup/settings/profile) — `/settings/` tabbed dashboard (preferences, account/Google, display) with per-category notification toggles, Google OAuth connection status, and timezone — §44
- campus-service models & handlers (meal/transport/medical, sections 34–35) + real-time notification engine (section 33)
- Website Builder backend (section 30+), Google Drive/Sheets layer, staff/admin/host dashboards (section 36)
- **Profile booking & activity history** — real per-user `MealTicket`/`TransportBooking`/`MedicalAppointment` rows (section 37 pass 1)
- **Official Notices** — `Notice` model, `/notices/` feed, staff `POST /api/notices/create/` publisher with real-time student broadcasts
- **Academic Notes / Course Materials** — `Course` + `CourseMaterial` models drive `/academic-notes/` (no mock folders)
- **Department Directory & Detail Hubs** — `Department`/`FacultyMember`/`ClassRoutine` models + seed migration; `/departments/<slug>/` hubs render live data
- **Club student view** — `Club`/`ClubEvent`/`ClubRegistration` models; `POST /api/clubs/join/` (pending membership, duplicate → 409, lead notified)
- **Checkout / payments** — `PaymentTransaction` model + server-backed `POST /checkout/` (unique `NTR-` ids, meal purpose activates `MealSubscription`)
- **Research AI** — OpenRouter-backed `/research-ai/api/query/` chat with persisted `ResearchThread`/`ResearchMessage` rows, server-side PDF/DOCX reference extraction, and graceful offline-engine fallback when no `OPENROUTER_API_KEY` is configured (§65)
- **Dashboard live widgets** — meal ratio, transport seats, medical availability + feeds computed from the database
- **Notes Engine AI actions + live sidebar** — server-side save / summarize / keywords / export (.txt + PDF); the sidebar reads the live academic catalog (`Department` folders, `CourseMaterial` PDFs, owner-scoped `UserNote` fetch via `/api/notes/<id>/`) — §43
- **Deployment** — env-driven settings (django-environ), `DEBUG=False` + `ALLOWED_HOSTS` from env, WhiteNoise static, `channels_redis` with offline fallback, `check --deploy` clean
- **Render Blueprint (§38)** — `render.yaml` one-click PaaS deploy (web + Postgres + Redis), `build.sh`, auto `ALLOWED_HOSTS`/CSRF for `.onrender.com`
- **CI/CD (§39)** — GitHub Actions: full test suite on PRs to `main`, SSH auto-deploy on push to `main`
- **DB transport catalog (§39)** — `Driver`/`TransportRoute`/`BusSchedule` models + seed; transport page/widget/booking read the DB
- **Medical chat + live queue (§39)** — persistent `MedicalChatThread`/`MedicalChatMessage` with a WebSocket consumer; FIFO staff queue API with real-time pushes

### Remaining (LOW priority)

1. **~~LOW — Transport live status / route catalog~~ — DONE in §39**: `TRANSPORT_ROUTES` is replaced by DB models (`TransportRoute`/`BusSchedule`/`Driver`); the transport page, dashboard widget, and booking handler read live seat counts and driver details from the database.
2. **LOW — Cafeteria kitchen inventory + System Admin driver/scan tables**: still mock forms — needs inventory/scan models + staff CRUD (drivers themselves now live in the DB via `Driver`).
3. **~~LOW — Medical admin chat~~ — DONE in §39**: persistent patient–doctor consultation threads (models + REST + WebSockets). The doctor-schedule panel is now **real** (§63 — DB `Doctor`/`DoctorSchedule` + availability toggles + slot caps enforced at booking); only the content-management and home-page-information panels remain mock.
4. **~~LOW — Research AI persisted threads & real LLM~~ — DONE in §65/§66**: `/research-ai/api/query/` now calls OpenRouter (`services/openrouter.py`, zero-cost free models with automatic 429/503 fallback) when `OPENROUTER_API_KEY` is set and persists `ResearchThread`/`ResearchMessage` history; uploaded PDF/DOCX reference text is extracted server-side (`services/parser.py`) and injected into the LLM system prompt.
5. **LOW — Media at scale**: media is served by Django — swap to django-storages/CDN if uploads grow (noted in `.env.example`).

## 13. Update by Tajkia Tasnim

**Date:** 07 August 2026  
**Branch:** taj

### Overview

Completed UI architecture refactoring and improved the dashboard structure while preserving the existing design and functionality.

### Completed Work

- Refactored shared layout into reusable partial templates.
- Created reusable UI components for better code organization.
- Added shared CSS and JavaScript resources.
- Improved accessibility and responsiveness.
- Implemented interactive mock confirmation flows for:
  - Meal Ticket
  - Transport Booking
  - Medical Appointment

### Files Modified

- `templates/base.html`
- `templates/dashboard/home.html`
- `templates/ticketing/tickets.html`
- `templates/medical/booking.html`
- `core/views.py`

### Testing

- `python manage.py check` ✔
- Tested successfully on localhost.

---

## 14. Update by Tajkia Tasnim

**Date:** 08 August 2026  
**Branch:** taj

### Overview

Added a medical admin dashboard and a host portal to the project, built on top of the refactored layout from the previous update.

### Completed Work

- Created a new `host/` Django app with:
  - **Medical host dashboard** (`/host/medical/`) - staff view of appointments with search, filters, and mock status actions.
  - **Medical admin dashboard** (`/medical/admin/`) - admin-only management UI with appointment confirm/cancel/view, chat management, doctor schedules, and medical content sections.
- Added `host_base.html` - a host-specific sidebar that replaces the student sidebar via `{% block sidebar %}` in `base.html`.
- Wired new routes in `config/urls.py` (`/medical/admin/`, `/host/`).
- Wrapped the sidebar in `base.html` with `{% block sidebar %}` and improved the mobile toggle so content reflows (`ml-64` <-> `ml-0`).
- Added `.venv/` to `.gitignore`.
- Added unit tests for the admin dashboard and verified the student booking page still works.

### Files Added / Modified

- `host/` (new app: `views.py`, `urls.py`, `tests.py`, `__init__.py`)
- `config/urls.py`
- `templates/host/host_base.html`
- `templates/host/medical/dashboard.html`
- `templates/host/medical/admin_dashboard.html`
- `templates/base.html`
- `.gitignore`

### URLs

| URL | View | Description |
| :--- | :--- | :--- |
| `/medical/admin/` | `medical_admin_dashboard` | Medical admin dashboard |
| `/host/` | `host:index` | Redirects to medical host dashboard |
| `/host/medical/` | `host:medical_host_dashboard` | Medical host dashboard |

### Testing

- `python manage.py check` ✔
- `python manage.py test` ✔ (2 tests pass)

---

## 15. Visual Builder Compatibility Refactor

**Date:** 08 August 2026  
**Branch:** main

### Overview

Refactored the full codebase to be compatible with a standalone Visual WYSIWYG Builder App. Applied standard CSS variables, data attribute tags, and decoupled endpoint mappings without breaking any page layouts, functionality, or responsiveness.

### Completed Work

1. **CSS & Theme Variable Migration**
   - Created `static/css/theme.css` with a global `:root` block containing all design tokens (colors, fonts, radii, layout).
   - Colors stored as space-separated RGB triplets so Tailwind opacity modifiers (e.g. `bg-base/80`) keep working via the `rgb(var(--color-x) / <alpha-value>)` pattern.
   - Replaced all hardcoded hex values (body, scrollbar, sidebar-link hover/active in `base.html` and the `bg-[#F0EBE1]` icon chips across 5 templates) with `var()` references + fallbacks.
   - Replaced `bg-[#F0EBE1]` with a new `chip` color token (`bg-chip`).

2. **Data Attribute Tags**
   - Added `data-component`, `data-widget`, `data-region`, `data-route`, `data-endpoint`, and `data-category` attributes across all templates so the Visual Builder can target components.
   - `base.html`: `data-app="campusdash"` on `<body>`, `data-region` on sidebar/nav/main/header/content, `data-component` on brand/profile/search/notifications.
   - Cards tagged `data-widget="meal-ratio"`, `"transport"`, `"medical-center"`, `"notice"`, `"course-card"`, `"appointment-form"`, etc.

3. **Decoupled Endpoint Mappings**
   - Created `core/context_processors.py` exposing a single `ENDPOINTS` dict (logical name -> resolved URL) to every template.
   - Replaced hardcoded `{% url %}` references in forms and sidebar links with `{{ ENDPOINTS.<name> }}`.
   - `base.html` emits the endpoint map as machine-readable JSON for the builder via `{{ ENDPOINTS|json_script:"app-endpoints" }}`.

### Files Added / Modified

- `static/css/theme.css` (new)
- `core/context_processors.py` (new)
- `config/settings.py` (added `core.context_processors.endpoints`, `STATICFILES_DIRS`)
- `templates/base.html`
- `templates/dashboard/home.html`
- `templates/ticketing/tickets.html`
- `templates/medical/booking.html`
- `templates/academic/notes.html`
- `templates/notices/notices.html`
- `templates/notes/notes_engine.html`
- `templates/host/host_base.html`
- `templates/host/medical/dashboard.html`
- `templates/host/medical/admin_dashboard.html`

### Design Tokens (`static/css/theme.css`)

| Token | Value | Usage |
| :--- | :--- | :--- |
| `--color-base` | `251 249 245` (#FBF9F5) | App background |
| `--color-card` | `255 255 255` (#FFFFFF) | Cards & sidebar |
| `--color-border` | `235 230 223` (#EBE6DF) | Separators |
| `--color-main` | `43 41 39` (#2B2927) | Primary text |
| `--color-accent` | `234 220 201` (#EADCC9) | Active states / buttons |
| `--color-accent-hover` | `216 202 180` (#D8CAB4) | Accent hover |
| `--color-chip` | `240 235 225` (#F0EBE1) | Icon chips / soft badges |
| `--font-main` | `'Inter', system-ui, sans-serif` | Primary font |

### Testing

- `python manage.py check` ✔
- `python manage.py test` ✔ (2 tests pass)
- Verified in browser: all pages render with correct theme, data attributes present, no console errors.

---

## 16. Mobile Responsiveness Pass

**Date:** 08 August 2026  
**Branch:** main (working tree, uncommitted)

### Overview

Completed the mobile responsiveness pass that was in progress (cut off by a session limit). The app is now fully usable on viewports from 360px–414px up to desktop, with no horizontal page overflow anywhere.

### Completed Work

1. **Mobile Navigation (`templates/base.html`)**
   - Moved the hamburger button **inside the sticky header**, inline next to the page title (previously it was a floating fixed button that overlapped the title on mobile).
   - Sidebar now slides in as an off-canvas drawer on mobile (`-translate-x-full lg:translate-x-0`) with `z-40 lg:z-auto` so it renders **above** the sticky header when open.
   - Added a dark **backdrop overlay** (`#sidebar-backdrop`) that appears with the drawer; tapping it closes the menu, and tapping any sidebar link also closes it. `aria-expanded` is synced on the toggle button.
   - Added `overflow-x-hidden` to the body to prevent horizontal scrolling.
   - Header search bar wraps to its own row on mobile; content padding is `p-4 md:p-8`.

2. **Host Sidebar (`templates/host/host_base.html`)**
   - Same `z-40 lg:z-auto` drawer treatment so the host portal menu behaves identically on mobile.

3. **Dashboard (`templates/dashboard/home.html`)**
   - Welcome banner stacks vertically on mobile (`flex-col sm:flex-row`) so the "Quick Action" button never squeezes the greeting.

4. **Tickets (`templates/ticketing/tickets.html`)**
   - Meal type selector (Breakfast/Lunch/Dinner) stacks to a single column on mobile (`grid-cols-1 sm:grid-cols-3`) instead of cramming three cards into 360px.

5. **Notes Engine (`templates/notes/notes_engine.html`)**
   - Workspace becomes a vertical stack on mobile (`flex-col lg:flex-row`, `h-auto lg:h-[calc(100vh-160px)]`).
   - File browser is full-width with a capped height (`max-h-[45vh]`) and internal scroll instead of a fixed 288px side column.
   - Editor action buttons wrap (`flex-wrap`); the flex spacer is hidden on mobile.
   - Textarea gets `min-h-[320px]` on mobile (prevents collapse in an auto-height parent) with an internal scroll.

6. **Medical Host Dashboard (`templates/host/medical/dashboard.html`)**
   - Search + filter form stacks vertically on mobile (`flex-col md:flex-row`); appointments table scrolls inside its `overflow-x-auto` container.

7. **Medical Admin Dashboard (`templates/host/medical/admin_dashboard.html`)**
   - Chat rows stack on mobile (`flex-col sm:flex-row`). Other sections were already responsive (summary cards, filter grid, tables wrapped in `overflow-x-auto`).

### Verification

- `python manage.py check` ✔ (no issues)
- `python manage.py test` ✔ (4 tests pass)
- **Headless Chrome @ 390×844 viewport** (all 8 pages: `/`, `/notes/`, `/tickets/`, `/host/medical/`, `/medical/admin/`, `/medical/`, `/academic-notes/`, `/notices/`):
  - No horizontal overflow on any page (`scrollWidth == clientWidth`).
  - Hamburger visible on every page, header title never overlapped.
  - Drawer opens with backdrop (opacity 1) and closes on backdrop tap (`sidebar` returns off-screen).
  - Only console noise: `/favicon.ico` 404 (no favicon defined — harmless).

### Files Modified (this pass)

- `templates/base.html`
- `templates/host/host_base.html`
- `templates/dashboard/home.html`
- `templates/ticketing/tickets.html`
- `templates/notes/notes_engine.html`
- `templates/host/medical/dashboard.html`
- `templates/host/medical/admin_dashboard.html`

### Notes for the Visual Builder

- All new/modified elements keep the existing `data-component`, `data-widget`, `data-region` tags (e.g. `data-component="sidebar-toggle"`, `data-component="sidebar-backdrop"`) so the WYSIWYG editor can target them unchanged.
- The mobile drawer state is pure CSS transforms + a tiny vanilla JS helper (`setSidebar`), so the builder can style/relocate the sidebar without touching the toggle logic.

---

## 17. Dynamic Public Homepage (Glassmorphism Landing Page)

**Date:** 08 August 2026  
**Branch:** main (working tree, uncommitted)

### Overview

Built the public-facing homepage (`templates/index.html`) with a full-screen dynamic hero and glassmorphism UI, and its stylesheet `static/css/main.css`. The homepage became the new root URL — the student dashboard moved from `/` to `/dashboard/` (URL name `dashboard` kept, so existing tests and `ENDPOINTS.dashboard` keep working).

### Routing Change
- `core/urls.py`: `'' → views.public_home` (`name='home'`), `'dashboard/' → views.dashboard` (`name='dashboard'`).
- `core/views.py`: added `public_home` view (renders `templates/index.html`).
- `core/context_processors.py`: added `'home'` to the `ENDPOINTS` registry.

### Homepage Sections (`templates/index.html`)
- **Navbar (`.navbar.glass-panel`)** — floating glass pill with `nav-logo-icon` / `nav-brand-name` tags; links to About University, Faculty & Teachers, Departments, Medical System, and a red `.btn-emergency`; hamburger + stacked glass dropdown on mobile.
- **Hero (`.hero-viewport`)** — full-screen animated background layer (`.hero-bg-slider`, Unsplash campus photo + gradient fallback, `zoomEffect` 20s), dark overlay (`.hero-overlay`), center `hero-title` / `hero-subtitle` / `hero-btn-primary` / `hero-btn-secondary`, and a 3-card floating glass deck (`.hero-card-deck`): emergency hotline with pulsing badge, medical center overview (Dr. Alex Mercer), and the 5 department quick-selector tags (CSE, TEX, IPE, FD, EEE).
- **About University (`#about-university`)** — `badge-public` header, Varsity Overview card, Emergency Contact & Address card, Faculty & Teachers 2-card grid, and a 5-card departments grid (FontAwesome icons).
- **Medical Info System (`#medical-system`)** — `badge-public` header, About Medical In-Charge, Contact Information, Medical Facilities checklist, Emergency Contacts (`.card-emergency`), and Health Tips — mirroring the sections managed from the Medical Admin dashboard's "Home Page Medical Information" mock.
- **Footer** — `footer-text` tag + dashboard link.

### Visual Builder Readiness
- The homepage is the first page fully tagged with the builder's canonical attributes: **77 `data-widget-id`** and **51 `data-editable-field`** elements after the NITER content pass (all required per spec: `nav-logo-icon`, `nav-brand-name`, `hero-bg`, `hero-title`, `hero-subtitle`, `hero-btn-primary`, `hero-btn-secondary`, `footer-text`, `niter-*` content fields, plus cards and text nodes).

### Styling (`static/css/main.css`)
- Glassmorphism primitives (`.glass-panel` with `backdrop-filter: blur(16px)`), full-screen hero classes, grid helpers `.grid-2` / `.grid-3` / `.grid-5` (collapse to `1fr` below 768px), `.badge-public`, pulse/zoom/fadeUp animations, `prefers-reduced-motion` support.
- Colors/fonts/radii fall back to `theme.css` tokens; landing-specific tokens (dark navy base, glass fills) live at the top of `main.css`.

### Verification
- `python manage.py check` ✔, `python manage.py test` ✔ (4 tests pass).
- Headless Chrome @1280px: hero fills the viewport, 18 glass panels, 3-card deck, 5 department cards, all sections present, **no horizontal overflow**, zero JS errors (favicon 404 only).
- Headless Chrome @390px: **no horizontal overflow** (before/after nav open), hamburger opens the stacked menu, card deck collapses to 1 column, zero console errors.
- `/` serves the homepage; `/dashboard/` still serves the student dashboard with its sidebar.

### Files Added / Modified
- `templates/index.html` (new)
- `static/css/main.css` (new)
- `core/views.py`, `core/urls.py`, `core/context_processors.py`
- `docs/HANDOVER.md`

---

## 18. Real-World NITER Content (About University Section)

**Date:** 08 August 2026  
**Branch:** main (working tree, uncommitted)

### Overview

Replaced the placeholder "About University" content on the public homepage with accurate NITER (National Institute of Textile Engineering and Research) information, and added an affiliation/governance highlight band.

### Updated Content (`templates/index.html`)
- **Varsity Overview → "About NITER"** — `niter-overview-title` / `niter-overview-text`: NITER is a constituent institute of the University of Dhaka, run under the Bangladesh Textile Mills Association (BTMA) under the Ministry of Textiles and Jute.
- **Address & Emergency Contact → "NITER Campus & Contact"** — `niter-address-title`, `niter-address-text` (Nayarhat, Savar, Dhaka-1350), `niter-phone-text` (+880 2-7791888 / +880 1711-000000), `niter-email-text` (info@niter.edu.bd).
- **Affiliation & Management Highlights** — new `highlight-card` band (`niter-highlights`) with two pill items: `niter-affiliation-text` (Constituent Institute of the University of Dhaka) and `niter-governance-text` (Managed by BTMA).
- **Department cards** — `dept-*-desc` fields now state full B.Sc. programs: CSE (Computer Science & Engineering), TEX (Textile Engineering), IPE (Industrial & Production Engineering), FD (Fashion Design & Technology), EEE (Electrical & Electronic Engineering).

### Styling (`static/css/main.css`)
- Added `.highlight-card`, `.highlight-item`, `.highlight-icon`, `.highlight-label`, `.highlight-text` (wrapable pill band, responsive).

### Verification
- `python manage.py check` ✔, `python manage.py test` ✔ (4 tests pass).
- Headless Chrome: all new widget texts render exactly as specified, highlight band shows 2 items, all 5 department descriptions updated, **no horizontal overflow** at 1280px or 390px (favicon 404 only).

---

## 19. Session Finalization & Release to main

**Date:** 08 August 2026  
**Branch:** main (committed & pushed)

### Overview

Final release pass: full error check, mobile-viewport audit, and push of the accumulated work (mobile responsiveness, public homepage + route change, NITER content) to `main`.

### Final Verification (before push)
- `python manage.py check` ✔ (no issues), `python manage.py test` ✔ (4 tests pass — including `home` route coverage).
- **Mobile @390px (9 pages):** `/`, `/dashboard/`, `/notes/`, `/tickets/`, `/host/medical/`, `/medical/admin/`, `/medical/`, `/academic-notes/`, `/notices/` — zero horizontal overflow; hamburger drawer opens/closes via backdrop and nav-link tap on the moved `/dashboard/` (backdrop opacity 1 → 0, sidebar returns to `-256`).
- **Homepage @1280px/390px:** hero full-screen, 19 glass panels, 3-col deck on desktop / 1-col on mobile, all sections present, NITER content exact, **77 widget ids / 51 editable fields**, no overflow, no console errors (favicon 404 only).
- **Desktop:** sticky header, fixed sidebar, hamburger hidden on lg+.

### Committed
- 12 modified files + 2 new files (`templates/index.html`, `static/css/main.css`).
- Pushed to `origin/main`.

---

## 20. Login Page & Authentication Wiring

**Date:** 09 August 2026

### Overview

Added a warm light-themed login page (`templates/login.html`) and wired Django's built-in authentication so the public homepage, login page, and student dashboard connect seamlessly.

### Completed Work

1. **Login Template (`templates/login.html`) + `static/css/auth.css`**
   - Standalone page matching the warm beige design system (`#faf9f6` bg, `#ffffff` card, `#f0ebe1` borders, `#e8e2d8` primary button).
   - Heading "Niter Hub" with subtext "Sign in to access your portal & dashboard"; Student/Staff ID + Password fields, CSRF token, error alert container, "Sign In" submit, and a "Skip login & view Dashboard demo →" fallback link.

2. **Auth Routes (`config/urls.py`)**
   - `/login/` → `LoginView.as_view(template_name='login.html', redirect_authenticated_user=True)`
   - `/logout/` → `LogoutView.as_view()` (POST-only)
   - Added `login` / `logout` to the `ENDPOINTS` registry (`core/context_processors.py`).

3. **Settings (`config/settings.py`)**
   - Added `django.contrib.auth` / `contenttypes` / `sessions` apps + Session/Common/Csrf/Auth middleware.
   - `LOGIN_URL = '/login/'`, `LOGIN_REDIRECT_URL = '/dashboard/'`, `LOGOUT_REDIRECT_URL = '/'`.
   - Configured SQLite (`db.sqlite3`) so authentication works end-to-end locally.

4. **Homepage Navigation (`templates/index.html`, `static/css/main.css`)**
   - Navbar: added "Sign In" link and a warm beige "Dashboard" pill button (`.btn-dashboard`); navbar collapses to the hamburger below 1120px so the extra items never crowd the pill.
   - Hero primary CTA now reads "Login to Dashboard →" and links to `/login/`.

5. **Dashboard (`templates/base.html`)**
   - Sidebar profile shows the real logged-in user (`user.get_full_name|default:user.username`); logout icon wrapped in a CSRF-protected POST form, hidden for anonymous users.

6. **Demo Users (SQLite, dev only — `db.sqlite3` is gitignored)**
   - `admin` / `admin123` (superuser)
   - `student` / `student123` (regular user)
   - Fresh clones must run `venv/bin/python manage.py migrate` and `venv/bin/python manage.py seed_demo_users` before real logins work.

### Testing

- `python manage.py check` ✔
- `python manage.py test` ✔ (9 tests — added `LoginFlowTests` in `core/tests.py` covering page render, valid login redirect, invalid-login error alert, authenticated redirect, and logout redirect).
- Verified end-to-end via HTTP: valid login → 302 to `/dashboard/`, bad credentials re-render with the error alert, logout → 302 to `/`.

### Next Steps

- Add `@login_required` / role-based access (student / host / admin) now that auth is in place.

---

## 21. Transport & Meal Ticket Dashboards

**Date:** 09 August 2026

### Overview

Added two frontend-only standalone dashboards following the clubs pattern: **Transport Online Ticket System** (`/transport/`, `templates/transport.html` + `static/css/transport.css`) and **Online Meal Ticket System** (`/meals/`, `templates/meals.html` + `static/css/meals.css`). Both use mock JavaScript data, the exact warm palette (#faf9f6 / #ffffff / #f0ebe1 / #e8e2d8, hover #dfd7cb), and stub views.

### Completed Work

1. **Routes & Views** — `path('transport/', views.transport_dashboard, name='transport_dashboard')` and `path('meals/', views.meal_dashboard, name='meal_dashboard')` in `core/urls.py`; stub views in `core/views.py`; entries added to the `ENDPOINTS` registry.
2. **Transport** — live status tracker, 3 route cards with driver/departure/live seats badges, seat selector (40-seat grid, route dropdown, trip-time chips), and a digital boarding pass with a deterministic SVG QR placeholder. Booking live-updates seats-left and regenerates the QR.
3. **Meals** — animated SVG ratio ring (142/200), Lunch/Dinner chips + date picker claim card, perforated coupon-style meal pass with token + Redeemed toggle, and 4 cafeteria supply stat cards that live-update on claim.
4. **Navigation** — replaced the single "Bus & Meal Tickets" sidebar link with "Transport Tickets" and "Meal System" (icons included); the legacy `/tickets/` route and page remain functional.
5. **Tests** — `transport_dashboard` / `meal_dashboard` added to the smoke-test PAGES list and endpoint-registry coverage.

### Testing

- `python manage.py check` ✔
- `python manage.py test` ✔

---

## 23. Public Homepage Light Theme Refactor

**Date:** 09 August 2026

### Overview

Converted the public landing page from the original dark-navy glassmorphism theme to the **warm light design system** (`#faf9f6` bg, `#ffffff` cards, `#f0ebe1` borders, `#e8e2d8` accents, `#1f2937` text) so `/` transitions seamlessly into `/dashboard/`.

### Completed Work (`static/css/main.css`, `templates/index.html`)

- **Tokens** — landing palette (`--bg-main`, `--bg-card`, `--border-color`, `--text-primary`, `--text-muted`, `--accent-primary`, `--accent-dark`) defined in `main.css` `:root` with hex fallbacks.
- **Navbar** — semi-transparent white pill (`#ffffffcc`), light `#f0ebe1` border, charcoal Emergency button; collapses to the hamburger below 1120px.
- **Hero** — light warm gradient overlay (`rgba(250,249,246,.85)` → `.95`) over the campus photo; headline `#1f2937`, tagline `#6b7280`.
- **CTAs** — "Login to Dashboard" beige button (`#e8e2d8`); white "Medical Services" button with light border.
- **Cards/badges** — white cards with `#f0ebe1` borders, beige icon chips, soft-green status chips (`#dcfce7` / `#166534`), `#f7f4ef` alt section band.
- Comments-only HTML updates — all `data-widget-id` / `data-editable-field` tags preserved.

### Testing

- `python manage.py check` ✔, `python manage.py test` ✔ (9 tests).
- Headless Chrome: computed styles match the palette exactly; no overflow at 1280px / 1024px / 360px; zero console errors.

---

## 22. Clubs & Events Module (Frontend-only Rebuild)

**Date:** 09 August 2026

### Overview

Rebuilt the Club & Event dashboard at `/clubs/` as a **frontend-only standalone page** (`templates/clubs.html` + `static/css/clubs.css`) driven by mock JavaScript data — no backend or database code. Supersedes the earlier `templates/clubs/clubs.html` (view-context data) implementation, which was removed.

### Completed Work

1. **Route & View** — route `path('clubs/', views.clubs_dashboard, name='clubs_dashboard')` unchanged; `clubs_dashboard` is now a pure stub rendering `clubs.html`. `clubs_dashboard` stays in the `ENDPOINTS` registry and the student sidebar.
2. **Template (`templates/clubs.html`)** — standalone page (theme.css + clubs.css, FontAwesome, Inter) with all mock data in JS arrays (`CLUBS`, `EVENTS`, `STATS`, `REGISTRATIONS`) rendered client-side:
   - Student View: club showcase cards with member counts + pulsing Active badges; events grid with fee tags ("Free" / "৳200 BDT") and "Register Now" triggers.
   - Registration modal: Student Name, Student ID, Payment Method (bKash/Nagad), Trx ID — mock submit with toast confirmation; closes via backdrop, ✕, or Esc.
   - Executive Workspace: 4 stat cards, registrations & payment tracking table (method + TrxID chips, amounts, Verified/Pending Review badges), announcement publisher form with mock publish toast.
3. **Styling** — `static/css/clubs.css` scoped to `body.clubs` with the exact warm palette (`#faf9f6`, `#ffffff`, `#f0ebe1`, `#e8e2d8`, `#1f2937`, `#6b7280`); responsive grids (4→2→1 columns), scrollable table, accessible modal.
4. **Tests** — `clubs_dashboard` smoke test + endpoint-registry coverage unchanged (page renders 200).

### Testing

- `python manage.py check` ✔
- `python manage.py test` ✔

---

## 24. Unified Top Navigation & Standalone Page Refactor

**Date:** 09 August 2026  
**Branch:** main

### Overview

Standardized the entire student front end on **one shared top navigation header**. Every standalone page (`/dashboard/`, `/transport/`, `/meals/`, `/clubs/`, `/medical/`, `/notices/`, `/academic-notes/`) now uses the exact same top bar, pill navigation, and profile popover — one source of truth, no per-page duplication.

### Completed Work

1. **Shared header partial (`templates/partials/topbar.html`)**
   - Top-left brand **"CampusDash"** (links to `{% url 'dashboard' %}` per spec).
   - Desktop nav pills: Dashboard, Academic Notes, Notices, Transport, Meals, Medical, Clubs — the current page's pill is highlighted `#e8e2d8` (`active` class), the rest stay white.
   - Circular profile avatar + popover (user name/email, page links, account actions).
   - Included via `{% include 'partials/topbar.html' with active='<page>' %}`.
2. **Shared styles (`static/css/topbar.css`)**
   - Single source of truth for `.topbar`, `.brand`, `.navlinks` (+ `.active`), `.profile`/`.avatar-btn`/`.profile-popover`, the centered `.intro` hero, and the `.toast`.
   - Responsive: `.navlinks` hidden below 768px; profile popover content switches per viewport (see section 26).
   - Duplicated header CSS removed from `transport.css`, `meals.css`, `clubs.css`.
3. **Pages converted to standalone** (no longer extend `base.html`)
   - `/dashboard/`, `/medical/`, `/notices/`, `/academic-notes/`. `base.html` (sidebar layout) remains only for `/tickets/`, `/notes/` (Notes Engine) and the host portal.
   - New page stylesheets: `dashboard.css`, `medical.css`, `notices.css`, `notes.css` (warm beige palette `#faf9f6` / `#ffffff` / `#f0ebe1` / `#e8e2d8`).
4. **Auth context processor** — added `django.contrib.auth.context_processors.auth` to `config/settings.py` so `{{ user }}` resolves on every page (also fixed the `base.html` sidebar profile).

### Files Added / Modified

- **New:** `templates/partials/topbar.html`, `static/css/topbar.css`, `static/css/dashboard.css`, `static/css/medical.css`, `static/css/notices.css`, `static/css/notes.css`
- **Modified:** `templates/dashboard/home.html`, `templates/medical/booking.html`, `templates/notices/notices.html`, `templates/academic/notes.html`, `templates/transport.html`, `templates/meals.html`, `templates/clubs.html`, `static/css/transport.css`, `static/css/meals.css`, `static/css/clubs.css`, `config/settings.py`, `core/tests.py`

### Testing

- `python manage.py check` ✔
- `python manage.py test` ✔ (**13 tests** — added `UnifiedHeaderTest` covering the shared header + active pill on all 7 pages, and `ProfilePopoverAuthTest` for the popover's authenticated/anonymous states).
- Headless Chrome @390px / @1280px on all pages: zero console errors, zero horizontal overflow; nav pills hidden on mobile, visible on desktop.

---

## 25. Student Dashboard Refactor (`/dashboard/`)

**Date:** 09 August 2026  
**Branch:** main

### Completed Work

- `/dashboard/` is now a standalone page (sidebar removed, shared top navigation with the Dashboard pill active).
- **Centered hero:** "Welcome back, {active user name}!" + subtitle *"Here is your central campus overview — quick access to meals, transport, medical bookings, and updates."* (resolves the real logged-in user via the auth context processor; falls back to "Guest").
- **Row 1 — Quick Summary Widgets** (cards link to the real pages, replacing old dead `#` links):
  - Meal Ratio Counter (140/200 + progress bar) → `/meals/`
  - Transport Service route preview ("Reserve Seat") → `/transport/`
  - Medical Center doctor availability ("Book Slot") → `/medical/`
- **Row 2 — Feeds & Activity:** Official Notices feed (Urgent/General/Event badges) → `/notices/`, Recent Academic Notes shortcuts → `/academic-notes/`.
- Styling in `static/css/dashboard.css`; `data-widget` / `data-component` tags preserved for the Visual Builder.

---

## 26. Responsive Profile Dropdown

**Date:** 09 August 2026  
**Branch:** main

The shared profile popover now adjusts its menu contents by screen size (pure CSS, no JS):

- **Desktop (≥768px):** header (name + email) + **account actions only** — Settings → `/settings/`, Sign Up / Switch Account → `/signup/`, Sign Out → POST `/logout/`. Page links are hidden (`@media (min-width: 768px)` → `.profile-links { display: none }`) since the top bar already shows them.
- **Mobile (<768px):** header + all 7 page navigation links + a `#f0ebe1` divider + the account actions section (the `.profile-actions` top border serves as the divider).
- Guests see **"Sign Up"** → `/signup/` and **"Sign In"** → `/login/`; logged-in users see **"Switch Account"** → `/signup/` and a real **Sign Out** POST form.
- Click-outside-to-close, Escape, and the smooth toggle animation are unchanged.

---

## 27. Settings & Sign Up Placeholder Pages

**Date:** 09 August 2026  
**Branch:** main

- New routes **`/settings/`** and **`/signup/`** (names `settings`, `signup`) → `views.placeholder` rendering `templates/placeholder.html` (styled by `static/css/placeholder.css`): warm-beige "Coming soon" pages so the profile popover links resolve.
- Both routes registered in the `ENDPOINTS` registry (`core/context_processors.py`) and added to the smoke-test `PAGES` list in `core/tests.py`.
- Swap in real pages later by replacing the `views.placeholder` entries.

### Testing

- `python manage.py check` ✔
- `python manage.py test` ✔ (13 tests — including smoke renders + endpoint-registry coverage for `settings`/`signup`).

---

## 28. Payment Gateway & Checkout (`/checkout/`)

**Date:** 09 August 2026  
**Branch:** main

### Overview

Added a **frontend-only payment gateway** (`templates/checkout.html` + `static/css/checkout.css`) for local mobile wallets (bKash / Nagad / Rocket / Card). All three purchase flows now route through it — **club event registration**, **transport seat booking**, and **monthly meal subscription** — and land back on their origin page with the pass/ticket already generated.

### Completed Work

1. **Route & View** — `path('checkout/', views.checkout_page, name='checkout')` in `core/urls.py`; stub view in `core/views.py`; `checkout` added to the `ENDPOINTS` registry (`core/context_processors.py`) and to the smoke-test `PAGES` list.
2. **Checkout page (`templates/checkout.html`)** — standalone page (theme.css + topbar.css + checkout.css) reading order data from query params (`type` = `event` | `transport` | `meal`, `item`, `issuer`, `fee`, `meta`):
   - Payment method selector (bKash / Nagad / Rocket-Card radio cards, brand-colored logos, per-channel merchant numbers that update the banner).
   - Payment details form: merchant account banner, wallet number + TrxID fields with client-side validation (`01XXXXXXXXX`, `[A-Za-z0-9-]{6,}`).
   - Order summary sidebar (item, issuer, meta line, subtotal/total) + Student Verification badge (real `user` via auth context processor, fallback mock).
   - "Confirm & Pay" simulates gateway processing (1.4s), then shows a success modal with a receipt (item, method, amount, TrxID, generated `NTR-…` reference with copy button) and a context-aware CTA.
   - Context-aware back link + success CTA: transport → `/transport/?booked=1&…`, meal → `/meals/?claimed=1&…`, event → dashboard.
3. **Clubs wiring (`templates/clubs.html`)** — "Register Now" buttons on paid events are now links to `/checkout/?type=event&item=…&issuer=…&fee=…` (fee parsed from the event's `fee_label`); the old in-page registration modal was removed. Free events still register via toast mock.
4. **Transport wiring (`templates/transport.html`)** — "Book Seat & Pay" validates seat/route/time, then routes to `/checkout/?type=transport&…` with route/seat/time/name; returning via the success CTA (`?booked=1`) resumes the page, marks the seat booked, and regenerates the boarding pass automatically. Button label updated to "Book Seat & Pay".
5. **Meals wiring (`templates/meals.html`)** — meals are **paid monthly**: a subscription status banner sits in the claim card. While inactive, "Pay Monthly Fee & Claim" routes to `/checkout/?type=meal&…` (fee `MEAL_MONTHLY_FEE = 2000` ৳/mo mock, adjustable constant); returning via the success CTA (`?claimed=1&meal=…&date=…`) marks the subscription active for the session (`sessionStorage`), claims the chosen meal, and regenerates the meal pass. Subscribed students claim directly.

### Testing

- `python manage.py check` ✔
- `python manage.py test` ✔ (16 tests — added `CheckoutPageTest`: checkout page renders core sections, clubs/transport/meals pages all link to `/checkout/`, meals page shows the monthly subscription banner).

---

## 29. Academic Research & Thesis Assistant (`/research-ai/`)

**Date:** 09 August 2026  
**Branch:** main

### Overview

Added a **frontend-only AI research chat console** (`templates/research_ai.html` + `static/css/research_ai.css`) — "Research AI" — matching the unified top-header navigation and warm beige aesthetic. All assistant responses are canned mock JS (no backend/AI calls).

### Completed Work

1. **Route & View** — `path('research-ai/', views.research_ai_page, name='research_ai')` in `core/urls.py`; stub view in `core/views.py`; `research_ai` added to the `ENDPOINTS` registry and to the smoke-test `PAGES` list.
2. **Navigation** — "Research AI" pill added to the shared topbar partial (`templates/partials/topbar.html`, desktop nav + mobile popover, robot icon) so every standalone page links to it; active pill `#e8e2d8` via `active='research'`.
3. **Centered hero** — title "Academic Research & Thesis Assistant" + subtitle about literature reviews, methodology, IEEE-style citations, and draft editing.
4. **Split layout (sidebar workbench + chat console)** — `grid-template-columns: 320px 1fr`, stacks to one column below 1100px:
   - **Sidebar:** drag-and-drop upload dropzone (PDF/DOCX, sets the "Current Reference" indicator), Recent Research Threads list (Superposition Circuit Analysis / Textile IoT Automation Models / NLP for Bangla Text Mining — click to resume with a mock context message), Citation Style selector (IEEE / APA 7 / Harvard / Chicago with live sample preview), and Quick Prompt Starters (Draft Literature Review / Methodology Breakdown / Check Citation Formatting).
   - **Chat console:** header with pulsing status badge ("Ready for Query" ↔ "Analyzing…" while typing) and active-document indicator; scrollable message feed with right-aligned `#e8e2d8` user bubbles and left-aligned white AI bubbles (`#f0ebe1` border); structured markdown-lite rendering (## / ### headings, bullets, inline code, **bold**) plus LaTeX/fenced code blocks with **Copy** buttons; animated typing indicator; multi-line auto-growing textarea with attach clip button, prompt-template dropdown (bolt icon), and a prominent "Send" button (Enter to send, Shift+Enter for newline).
   - Mock assistant routes prompts by keyword (literature / methodology / citation / summarize / superposition / IoT) with canned structured responses; fallback help message otherwise.

### Testing

- `python manage.py check` ✔
- `python manage.py test` ✔ (21 tests — `research_ai` added to smoke + unified-header + active-pill coverage; new `ResearchAIPageTest` asserts hero, dropzone, threads, citation styles, prompt starters, chat header, and input placeholder).

---

## 30. Department Directory & Detail Hub (`/departments/`)

**Date:** 09 August 2026  
**Branch:** main

### Overview

Added the **Department Directory** (`/departments/`) and **Department Detail Hub** (`/departments/<dept_slug>/`) as frontend-only standalone pages driven by mock JS data, matching the unified top navigation and warm beige palette. A new **Departments** pill was synced into the shared topbar (desktop nav + mobile popover).

### Completed Work

1. **Routes & Views** — `path('departments/', views.departments_directory, name='departments')` and `path('departments/<slug:dept_slug>/', views.department_detail, name='department_detail')` in `core/urls.py`; stub views in `core/views.py` (the detail view passes `dept_slug` to the template). Both added to the `ENDPOINTS` registry (`core/context_processors.py`; `department_detail` registered with a representative `fde` slug).
2. **Navigation** — "Departments" pill (`fa-building-columns`) added to `templates/partials/topbar.html` in both the desktop nav pills and the mobile profile-popover page links (account-actions-on-desktop / full-nav-on-mobile behavior unchanged).
3. **Department Directory (`templates/departments.html`)** — hero "Academic Departments & Faculties" with a live search bar (clear button hidden until typing) and quick-jump pills (All / FDAE / CSE / TE / EEE / IPE) that filter + scroll to the matching card; 5 showcase cards (FDAE, CSE, TE, EEE, IPE) each with HOD name, student count, and note-resource count, plus "Explore Department" (→ detail hub) and "Department Notes" (→ `/#tab-notes` deep link) buttons; mock-JS `DEPARTMENTS` array rendered client-side; empty state for no matches.
4. **Department Detail Hub (`templates/department_detail.html`)** — centered header (dept icon, "Department of …", code chip, Established / Students / HOD / Notes stats) and **4 client-side tabs** (hash deep-linking, `#tab-overview|faculty|schedule|notes`):
   - **Overview & Announcements** — HOD welcome card + announcement cards (Lab Update / Workshop / Circular badges).
   - **Faculty Directory** — faculty cards with initials avatar, designation, research focus, contact email, office hours, and an "Office hours open" badge.
   - **Class & Lab Schedule** — Sun–Thu routine cards with course codes, room numbers, timings, and Lecture/Lab icons.
   - **Department Notes & PDF Drive** — semester filter chips, note cards (type badges, file size, mock Download), and an "Upload New Notes" button (mock toast).
   - Unknown slugs render a graceful "Department not found" fallback card with a back link.
5. **Styling** — `static/css/departments.css` scoped to `body.departments` / `body.dept-detail` with the exact warm palette (`#faf9f6` / `#ffffff` / `#f0ebe1` / `#e8e2d8`, hover `#dfd7cb`, text `#1f2937`, muted `#6b7280`); responsive grids (cards 1→2→3+ columns, tabs wrap, note toolbar stacks on mobile), `prefers-reduced-motion` support, keyboard focus rings.
6. **Tests** — `departments` added to the smoke-test `PAGES` list, `UnifiedHeaderTest` pages + `NAV_LINKS` (now includes Departments) + active-pill mapping; new `DepartmentsPageTest` covers directory hero/search/quick-jump, all 5 slugs rendering the detail hub with all 4 tabs, mock content presence, shared header + active pill, and the unknown-slug fallback.

### Files Added / Modified

- **New:** `templates/departments.html`, `templates/department_detail.html`, `static/css/departments.css`
- **Modified:** `templates/partials/topbar.html`, `core/urls.py`, `core/views.py`, `core/context_processors.py`, `core/tests.py`, `docs/HANDOVER.md`

### Testing

- `python manage.py check` ✔
- `python manage.py test` ✔ (27 tests — added `DepartmentsPageTest`; smoke + unified-header + active-pill coverage extended to `departments`).

---

## 31. Account Pages, Staff/Admin Dashboards & Nav Fixes

**Date:** 09 August 2026  
**Branch:** main (working tree)

### Overview

Replaced the placeholder `/settings/` and `/signup/` pages with real account surfaces, added three staff/admin dashboards (System Admin consolidates Transport Management), introduced the first database model, and fixed stale navigation links. This is the largest single pass since section 30.

### Completed Work

1. **StudentProfile model (`core/models.py` + migration `core/0001_initial`)** — one-to-one with Django `User` (`related_name='student_profile'`): `student_id` (unique) + `department` (choices CSE / TEX / IPE / FDAE / EEE) + `get_department_display_name()`.
2. **System Admin Dashboard (`/admin-dashboard/`, `system_admin_view`)** — `@staff_member_required(login_url=settings.LOGIN_URL)` rendering `templates/sys_admin.html` (shared `static/css/admin.css`). Clean HTML/JS 4-tab interface:
   - **Tab 1 — Users & Roles:** student + staff tables and a role & permission matrix.
   - **Tab 2 — Notices & Material Drive:** university notices and a material drive table.
   - **Tab 3 — Transport Management (consolidated):** live bus status stat cards, driver updates table, and boarding-scan (QR) table. *(Seat Allocations lived here until section 32.)*
   - **Tab 4 — Local AI Vector DB & System Security Logs:** vector stats, recent queries, security logs.
3. **Cafeteria Admin (`/cafeteria/admin/`, `cafeteria_admin_view`)** — staff-only: daily meal slot capacity counters, kitchen inventory table (stock/unit/status), and a QR token / meal coupon redemption form (mock validation).
4. **Club Admin (`/clubs/manage/`, `club_admin_view`)** — staff-only executive workspace: member approval list, role assignment selects, event post creator, and bKash/Nagad/Rocket transaction verifier fields.
5. **Sign Up (`/signup/`, `signup_view`)** — replaced the placeholder: form (Student ID, Full Name, Department dropdown, Email, Password) creates a `User` (username = student ID) **plus** `StudentProfile`, logs the student in, and redirects to `/dashboard/`. Duplicate student ID / username is rejected with an inline error.
6. **Settings (`/settings/`, `settings_view`)** — replaced the placeholder: working Django `PasswordChangeForm` (saved with `update_session_auth_hash` so the session survives), notification preference toggles, and a Warm Light / Dark theme picker persisted in `localStorage` (CSS token overrides — affects var()-based pages only).
7. **Profile (`/profile/`, `profile_view`, `@login_required`)** — virtual student ID card (photo placeholder, dept + student ID, deterministic SVG QR — same technique as the transport pass) with a **Booking & Activity History** tab showing mock medical appointments, transport tickets, and meal coupons.
8. **Navigation fixes (`templates/partials/topbar.html`)** — the Academic Notes pill (desktop + mobile dropdown) now points cleanly to `/notes/`; an unlinked **Tickets** item was added to the profile dropdown.
9. **Cleanup** — removed `templates/placeholder.html`, `static/css/placeholder.css`, and the `views.placeholder` view (all dead references gone).

### Files Added / Modified

- **New:** `core/models.py`, `core/migrations/0001_initial.py`, `templates/sys_admin.html`, `templates/cafeteria_admin.html`, `templates/club_admin.html`, `templates/signup.html`, `templates/settings.html`, `templates/profile.html`, `static/css/admin.css`, `static/css/signup.css`, `static/css/settings.css`, `static/css/profile.css`
- **Modified:** `core/views.py`, `core/urls.py`, `core/context_processors.py`, `templates/partials/topbar.html`, `core/tests.py`
- **Removed:** `templates/placeholder.html`, `static/css/placeholder.css`

### URLs

| URL | View | Access |
| :--- | :--- | :--- |
| `/admin-dashboard/` | `system_admin_view` | staff only |
| `/cafeteria/admin/` | `cafeteria_admin_view` | staff only |
| `/clubs/manage/` | `club_admin_view` | staff only |
| `/signup/` | `signup_view` | public |
| `/settings/` | `settings_view` | logged in |
| `/profile/` | `profile_view` | logged in |

### Testing

- `python manage.py check` ✔
- `python manage.py test` ✔ (**40 tests**, up from 27): new coverage for all six routes (smoke + endpoint registry), auth redirects (`/profile/` + `/settings/` → login when anonymous; admin pages → login for non-staff), signup creating user + profile, duplicate-ID rejection, the password-change flow, and staff gating.
- Verified live in the browser: all four System Admin tabs switch correctly; student login sees their real profile; admin pages 403/redirect correctly for non-staff.

### Notes

- `@staff_member_required` defaults to redirecting to `admin:index`, which doesn't exist here, so it is bound to `settings.LOGIN_URL` (`/login/`).
- Demo users recreated locally (`db.sqlite3` is gitignored): `admin` / `admin123` (staff) and `student` / `student123`. Run `venv/bin/python manage.py seed_demo_users` (idempotent) to recreate them — see README for options.
- The settings page's Dark toggle is a bonus foundation only — the project theme remains warm-light (section 23).

---

## 32. Transport Seat Allocations Removal

**Date:** 09 August 2026

### Overview

Removed the **"Seat Allocations"** card from the System Admin dashboard's Transport Management tab together with its mock data. Live Bus Status, Driver Updates, and Boarding Scans remain completely intact.

### Completed Work

1. `templates/sys_admin.html` — deleted the Seat Allocations card (title, "Assigned seats per route" subtitle, the ROUTE / SEAT / PASSENGER / STATUS table, and its `{% for seat in seat_allocations %}` rows). The remaining transport cards are stacked blocks, so the layout simply closes up with no grid breakage.
2. `core/views.py` — removed the `seat_allocations` mock list and its `'seat_allocations': seat_allocations` context entry from `system_admin_view`. `buses`, `driver_updates`, and `boarding_scans` are untouched.
3. `core/tests.py` — dropped `'Seat Allocations'` from the admin tab-rendering test's expected needles.

### Testing

- `python manage.py check` ✔
- `python manage.py test` ✔ (40 tests)
- Verified live: logged-in fetch of `/admin-dashboard/` contains **0** "seat allocation" mentions while "Live Bus Status", "Driver Updates", and "Boarding Scans" each render once.

### Scope note

- The student `/profile/` page's Booking & Activity History still shows transport tickets with seat numbers (`transport_tickets` in `profile_view`) — that is the student's own booking history, a separate feature from the admin Seat Allocations table, and was intentionally left intact.
- Verified over HTTP: `/departments/` and all 5 `/departments/<slug>/` pages return 200; unknown slug renders the fallback; all inline scripts pass `node --check`.

---

## 33. Google OAuth Expiry Fix + Real-Time Notification & System Alert Engine

**Date:** 10 August 2026

### Overview

Two backend milestones landed together: (1) finalized the **Google OAuth token expiry fix** (the last failing test from the previous session) and (2) built the **Real-Time Notification & System Alert Engine** — a persisted `Notification` model, JSON APIs, and a Django Channels WebSocket consumer that pushes alerts to `user_<id>` groups in real time.

### Google OAuth Token Expiry Fix (`core/google_service.py`)

- `get_google_credentials` previously called `timezone.localtime(creds.expiry)` unconditionally, which raised `ValueError: localtime() cannot be applied to a naive datetime` whenever google-auth handed back a naive expiry (the project runs `USE_TZ=False`, so `timezone.now()` is naive local time).
- **Fix:** branch on `timezone.is_aware(creds.expiry)` — aware UTC expiries are normalized with `localtime()`; naive values are stored untouched (they are already in the project's local-time convention). `GoogleUserToken.is_expired` keeps comparing like with like.
- All 117 existing tests (incl. the previously failing `test_get_google_credentials_refreshes_expired_token_and_persists`) pass after the fix.

### Notification Model (`core/models.py` → migration `0004_notification`)

- **`Notification`** — `user` (FK, `related_name='notifications'`), `title`, `message`, `category` (`urgent` / `academic` / `meal` / `transport` / `medical`), `is_read` (default `False`), `created_at` (`auto_now_add`). Ordered newest-first (`['-created_at', '-id']`).
- Registered in `core/admin.py` (`NotificationAdmin`).

### Notification APIs (`core/views.py`, `core/urls.py`)

| Method | Endpoint | View | Description |
| :--- | :--- | :--- | :--- |
| GET | `/api/notifications/` | `fetch_notifications` | `@login_required` — returns `unread_count` + the 10 most recent notifications for `request.user` |
| POST | `/api/notifications/<id>/read/` | `mark_notification_read` | `@login_required` — marks the user's own notification read (others' IDs 404); returns `{'status': 'success'}` |

### WebSocket / Real-Time Layer (Django Channels)

- **`core/consumers.py`** — `NotificationConsumer` (`AsyncJsonWebsocketConsumer`) joins group `user_<user_id>` on connect (anonymous sockets rejected), leaves on disconnect, and relays `{'type': 'notification', 'payload': {...}}` messages. Also exposes a sync `notify_user(user_id, payload)` helper for views/commands.
- **`core/routing.py`** — `ws/notifications/` WebSocket route.
- **`config/asgi.py`** (new) — `ProtocolTypeRouter` (HTTP via Django ASGI + WebSockets through `AuthMiddlewareStack`/`URLRouter`).
- **`config/settings.py`** — `daphne` (first) + `channels` in `INSTALLED_APPS`, `ASGI_APPLICATION = 'config.asgi.application'`, `CHANNEL_LAYERS` = in-memory (swap for `channels_redis` in multi-process production).
- **`requirements.txt`** — added `channels>=4.0,<5.0` and `daphne>=4.0,<5.0`.

### Tests

- Added `NotificationModelTest`, `NotificationApiTest`, and `NotificationConsumerTest` (async consumer tests share one event loop; `notify_user` tested with an `AsyncMock`).
- `python manage.py check` ✔ · `python manage.py test` ✔ (**139 tests**).

---

## 34. Production Campus-Service Models, Atomic Handlers & APIs

**Date:** 10 August 2026

### Overview

Turned the three placeholder booking stubs (`claim_meal_ticket`, `book_transport_ticket`, `book_appointment`) into **production backend handlers**: real models, `transaction.atomic()` actions with `IntegrityError` handling, real-time notifications on every successful booking, and a full test suite (meal capacity, transport seat conflicts, medical slot double-booking).

### Models (`core/models.py` → migration `0005_*`)

| Model | Key fields | Constraints |
| :--- | :--- | :--- |
| `MealSubscription` | `user` (OneToOne, `meal_subscription`), `is_active`, `expires_at`, `created_at`; `is_expired` property | — |
| `MealTicket` | `user` (FK, `meal_tickets`), `meal_type` (`breakfast`/`lunch`/`dinner`), `ticket_token` (`#MEAL-XXXX`), `is_redeemed`, `claimed_at` | `ticket_token` unique |
| `TransportBooking` | `user` (FK, `transport_bookings`), `route_name`, `departure_time`, `seat_number` (1–40), `qr_token`, `booked_at` | `qr_token` unique; `unique_together (route_name, departure_time, seat_number)` — the DB is the seat-availability arbiter |
| `MedicalAppointment` | `user` (FK, `medical_appointments`), `doctor_name`, `appointment_date`, `time_slot`, `reason`, `status` (default `pending`), `created_at` | `unique_together (doctor_name, appointment_date, time_slot)` — prevents doctor double-booking |

All four registered in `core/admin.py`.

### Views (`core/views.py`)

- **`claim_meal`** — POST + `@login_required`. Validates `meal_type`, verifies an active, non-expired `MealSubscription` (403 otherwise), enforces the **one ticket per user per meal per day** rule (409), checks **remaining daily capacity** (`DAILY_MEAL_CAPACITY`, 429 when full), generates a unique `#MEAL-XXXX` token, and atomically creates the `MealTicket` + a `meal` `Notification`. Broadcasts over WebSocket after commit.
- **`book_transport`** — POST + `@login_required`. Resolves `route_id` via the `TRANSPORT_ROUTES` catalog (or explicit `route_name`/`departure_time`), validates `seat_number` (1–40), then creates the `TransportBooking` inside `transaction.atomic()`. A concurrent/taken seat raises `IntegrityError` → **409 "already taken"** (no partial write, no notification).
- **`book_appointment`** — POST + `@login_required`. Resolves `doctor` id via the `DOCTORS` catalog (or explicit `doctor_name`), validates the `YYYY-MM-DD` date, and atomically creates a `pending` `MedicalAppointment`. A double-booked slot raises `IntegrityError` → **409 "already booked"**.
- Shared helpers: `_generate_meal_token`, `_generate_qr_token` (e.g. `TR-4F2A1C`), `_broadcast_notification` (calls `notify_user` only after the atomic block commits).
- View functions renamed (`claim_meal_ticket` → `claim_meal`, `book_transport_ticket` → `book_transport`); **URL names are unchanged** (`claim_meal_ticket`, `book_transport_ticket`, `book_appointment`) so templates, `ENDPOINTS`, and existing tests keep working.

### URLs (`core/urls.py`)

- `/claim-meal/`, `/book-transport/`, `/book-appointment/` — same paths/names, now backed by the production handlers. The existing frontend forms (meal `meal_type`, transport `route_id`, medical `doctor`/`appointment_date`/`time_slot`/`reason`) submit directly to these endpoints.

### Tests

- New suites: `MealSubscriptionModelTest`, `ClaimMealApiTest` (subscription guards, capacity, token uniqueness), `TransportBookingModelTest` + `BookTransportApiTest` (seat race / duplicate blocking → 409), `MedicalAppointmentModelTest` + `BookAppointmentApiTest` (slot double-booking → 409).

---

## 35. Student Frontend → Backend Wiring + Real-Time Notification Bell

**Date:** 10 August 2026  
**Branch:** main (working tree)

### Overview

Connected the student frontend dashboards to the production campus-service APIs (section 34) and wired the real-time notification bell into the shared topbar. The mock-JS seat/pass UI flows now issue real async POSTs with CSRF and render backend responses.

### Transport (`templates/transport.html`)
- Seat-selection form now POSTs `route_id`, `seat_number`, `departure_time` to `/book-transport/` with `X-CSRFToken`.
- **200:** renders the real backend `qr_token` + boarding pass details; marks the chosen seat booked in the 40-seat grid.
- **409:** error toast "Seat already taken by another passenger…" and refreshes seat availability.

### Meals (`templates/meals.html`)
- Meal chips use backend keys (breakfast/lunch/dinner); "Claim Meal Ticket" POSTs to `/claim-meal/`.
- **200:** active digital meal pass updates with the backend `#MEAL-XXXX` token; the slot counter + progress ring decrement.
- **403/409/429:** inline alerts (403 includes a "pay now" checkout link for missing subscriptions).

### Medical (`templates/medical/booking.html`)
- Form POSTs `doctor`, `appointment_date`, `time_slot`, `reason` to `/book-appointment/`.
- **200:** appointment prepended to "Upcoming Appointments" with a Pending badge + success alert.
- **409:** inline error alert for already-booked doctor slots.

### Real-Time Notification Bell (`templates/partials/topbar.html` + `static/css/topbar.css`)
- Initial `GET /api/notifications/` on page load sets the unread badge + populates the dropdown.
- WebSocket client to `ws/notifications/` (authenticated only): each payload increments the badge and slides in a top-right toast (title + message); reconnect capped to avoid infinite loops.
- Click-to-mark-read via `POST /api/notifications/<id>/read/`; bell toggle mirrors the profile popover.
- A `{% csrf_token %}` renders for logged-in users so the CSRF cookie exists on pages without forms (required by all the new AJAX calls).

### Testing
- `python manage.py check` ✔ · `python manage.py test` ✔ (**187 tests**).
- Verified end-to-end against the running server (authenticated curl): transport 200 (`TR-…`) + 409 on re-book; meal 200 (`#MEAL-…`) + 409 on re-claim; appointment 200 (pending) + 409 on re-book; `/api/notifications/` returns `unread_count` with all alert types. Bell markup renders for logged-in users, absent for guests.

---

## 36. Staff / Admin / Host Dashboards → Real Models & Persistent Endpoints

**Date:** 10 August 2026  
**Branch:** main (working tree)

### Overview

Connected all four staff/admin/host dashboards to real database models and persistent service endpoints. Added `MealTicket.redeemed_at`, a `club` Notification category, the `verify_club_transaction` Sheets helper, and 4 new API routes.

### Models (`core/models.py` → migration `0006_*`)
- `MealTicket.redeemed_at` (DateTimeField, null) — set when a ticket is redeemed.
- `Notification.category` gains a **`club`** choice (club payment/verification alerts).

### Cafeteria Admin (`/cafeteria/admin/`)
- `cafeteria_admin_view` now queries live `MealSubscription` counts, today's `MealTicket` claims per meal against capacity caps (Breakfast 80 / Lunch 200 / Dinner 160).
- New **`POST /api/cafeteria/redeem/`** (`redeem_meal_ticket`): validates `#MEAL-XXXX` tokens, sets `is_redeemed=True` + `redeemed_at`, returns ticket details; 409 on double redemption; the redeem JS auto-refreshes the supply counters. Redemptions table shows real tickets with an empty state.

### Medical Admin & Host (`/medical/admin/`, `/host/medical/`)
- Both views serve real `MedicalAppointment` rows (`select_related('user')`) with filters for student name/ID, status, department, doctor, date — protected by `staff_member_required`.
- New **`POST /api/medical/appointments/<id>/status/`** (`update_appointment_status`): persists status transitions (pending → confirmed/completed/cancelled), creates a `Notification`, and pushes it via `notify_user` (JSON for AJAX, redirect-with-message for form POSTs). Old mock `?action=` links are now real POST forms.

### Club Executive (`/clubs/manage/`)
- `club_admin_view` syncs pending registrations, member rosters, and transactions from the linked Google Sheet via the `gspread` layer when `?sheet_url=` is present (friendly error if Google isn't connected); "Connect" redirects to the synced URL.
- New **`POST /api/clubs/verify-transaction/`** (`verify_club_transaction_view`): marks the matching TrxID row **Verified** in the sheet (find-based lookup — robust to blank rows) and pushes a `club`-category real-time `Notification` to the student.

### System Admin (`/admin-dashboard/`)
- Live `User`/`StudentProfile` counts + stat cards, real `TransportBooking` route aggregates & boarding scans, and a security log synthesized from recent meal/transport/medical activity.
- New **`POST /api/admin/update-role/`** (`update_user_role`, superuser-only): toggles `is_staff` / `is_superuser` with guards (no self-demotion, last superuser never demoted); per-staff role forms wired to it.

### Service layer (`core/google_service.py`)
- New `verify_club_transaction(sheet_url, user, trx_id)` — find-based row lookup, marks the transaction cell **Verified**, returns student email for the notification.

### Templates
- `cafeteria_admin.html` — real redemption fetch + live subscription/supply stats.
- `sys_admin.html` — stat cards + role forms wired to `/api/admin/update-role/`.
- `club_admin.html` — verify-transaction fetch + sheet-error display + post-connect roster sync.
- `host/medical/admin_dashboard.html` + `host/medical/dashboard.html` — status action POST forms.
- `templates/partials/topbar.html` — `club` category icon for the bell.

### Testing
- `python manage.py check` ✔ · `python manage.py test` ✔ (**215 tests**).
- New `StaffAdminBackendTest` (permissions, redemption, status transitions + notifications, sheet verification, role updates) and rewritten `host/tests.py` with staff-gated access tests.
- Verified end-to-end against the running server: all five dashboards 200 for staff; redeem/status/verify/role flows round-trip with notifications; wrong-role access blocked.
- `python manage.py check` ✔ · `python manage.py makemigrations --check` (no drift) ✔ · `python manage.py test` ✔ (**187 tests**).

---

## 37. Backend Finalization: Profile/Notices/Courses, Departments/Clubs/Dashboard, Checkout/Settings/Notes-AI, Deployment Prep

**Date:** 10 August 2026  
**Branch:** main (working tree → committed & pushed)

### Overview

Four consecutive passes that closed out the remaining backend gaps and prepared the project for production:

1. **Profile Activity History, Official Notices Engine, Course Materials API** (migrations `0007`)
2. **Department Hubs, Club Management System, Dynamic Dashboard Widgets** (migrations `0008` + `0009` seed)
3. **Checkout/Payments, Settings Persistence, Server-Side Notes & Research AI** (migration `0010`)
4. **Deployment Preparation, Performance Optimization, Security Hardening** (migration `0011`)

Full suite: **320 tests pass**; `manage.py check` and `check --deploy` clean; all verification data removed after live E2E runs.

---

### Pass 1 — Profile History, Notices Engine, Course Materials (`0007`)

**Models** (`core/models.py`, all admin-registered):
- `Notice` — `title`, `content`, `category` (urgent/academic/event/general), `is_published`, `author` FK, `created_at`/`updated_at`. Published rows drive the `/notices/` feed.
- `Course` (`code` unique, `title`, `department`, `semester`) and `CourseMaterial` (`course` FK, `title`, `file` upload, `file_type`, `uploaded_at`, `display_type`/`size_display` helpers).

**Views:**
- `profile_view` — the "Booking & Activity History" now renders real per-user `MealTicket`, `TransportBooking`, and `MedicalAppointment` rows (no mock lists).
- `notices_view` — filters published `Notice` rows by `?category=`; `academic_notes` — live `Course`/`CourseMaterial` folders grouped by department.
- New **`POST /api/notices/create/`** (`create_notice`, staff-only): persists the notice and, when published, creates a `Notification` for every active user and pushes it over WebSocket.

---

### Pass 2 — Departments, Clubs, Dashboard Widgets (`0008` + `0009`)

**Models** (admin-registered): `Department` (name/code/slug/HOD/description/office), `FacultyMember` (dept FK), `ClassRoutine` (dept FK, day/semester/subject/time/room), `Club` (name/slug/lead_user/banner), `ClubEvent` (club FK, date/capacity/location), `ClubRegistration` (student+club unique, pending/active).

**Seed migration `0009`:** 5 departments, 15 faculty, 20 routine periods, 4 clubs, 4 upcoming events — pages work out of the box on a fresh DB.

**Views:**
- `/departments/` — live DB rows with student/material counts (2 grouped queries, no N+1); search + quick-jump filter server-rendered cards.
- `/departments/<slug>/` — full hub: HOD/office header, faculty cards, routine grouped by weekday, notes drive grouped by semester, published academic notices; unknown slug → 404.
- `/clubs/` — live clubs (annotated active-member counts) + upcoming events; new **`POST /api/clubs/join/`** (`join_club`) creates a pending registration (duplicate → 409), notifying the club lead.
- `dashboard` — three live widgets: meal ratio (tickets claimed today / capacity), transport (seats left per catalog route), medical (on-duty doctors + slots open today); notices feed + course quick-tiles are live DB data.

---

### Pass 3 — Checkout, Settings, Notes & Research AI (`0010`)

**Models** (admin-registered): `PaymentTransaction` (user, amount, method bKash/Nagad/Card/Rocket, unique `transaction_id`, purpose Meal/Tuition/Event/Transport, status pending/completed/failed, `wallet_trx`), `UserNotificationPreference` (email/sms/push/dark_mode; auto-created for every new user via a `post_save` signal), `UserNote` (user, title, content).

**Views / endpoints (all `@login_required`, CSRF-protected):**
- `checkout_view` POST → `_process_checkout`: validates wallet number/TrxID/amount (guards NaN/Infinity/negative/oversized), generates a unique `NTR-XXXXXX` id, persists the payment, notifies the user, and **a meal payment activates/extends the `MealSubscription`**. The checkout page's simulated `setTimeout` was replaced with a real POST; the receipt shows the server reference.
- `/settings/` — GET loads saved prefs; POST (form or JSON) persists them to the DB (localStorage toggles removed); dark theme applied from `prefs.dark_mode`.
- Notes Engine actions: `POST /api/notes/save/`, `POST /api/notes/summarize/` (extractive TF summarization), `POST /api/notes/keywords/` (TF keyword ranking), `POST|GET /api/notes/export/` → `.txt` or a **dependency-free PDF writer** (structure-validated; `file` reports "PDF document, version 1.4"). The page has working Save/Summary/Keywords/Export buttons + a "My Notes" sidebar.
- `POST /api/research/query/` — structured responses (`topic`, `response_markdown`, style-aware `references` for IEEE/APA 7/Harvard/Chicago); the research page POSTs to it with a local offline fallback.

---

### Pass 4 — Deployment Preparation, Performance, Security (`0011`)

**Production configuration (`config/settings.py`):**
- Environment-driven via **django-environ**: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DATABASE_URL`, `REDIS_URL` (real env vars beat `.env`). `DEBUG` hard-defaults to **False** and `SECRET_KEY` **fails closed** (`ImproperlyConfigured` when `DEBUG=False` without a secret).
- `.env` (gitignored, dev) + documented `.env.example`; `requirements.txt` adds `django-environ`, `whitenoise`, `channels-redis`.
- **WhiteNoise** (`CompressedStaticFilesStorage`, middleware) serves collected static; `STATIC_ROOT = staticfiles/` (gitignored); media stays served via `config/urls.py` (`static()` helper, gate removed so it works in production).
- Production security block (only when `DEBUG=False`): `SECURE_SSL_REDIRECT`, `SECURE_PROXY_SSL_HEADER`, `SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE`, HSTS (+subdomains/preload), `SECURE_REFERRER_POLICY`, clickjacking middleware — **`check --deploy` clean**.
- **Channel layers:** `channels_redis` when a reachable `REDIS_URL` is configured; a startup ping probe falls back to the in-memory layer when unset **or offline**. `notify_user` (`core/consumers.py`) swallows channel-layer failures so a runtime Redis outage degrades to poll-only delivery instead of 500ing the request (new `NotificationPushResilienceTest`).

**Performance (`0011`):**
- `db_index` on status flags/timestamps + composite indexes for the hot paths: `Notification(user, is_read)` & `(user, -created_at)`, `Notice(is_published, -created_at)`, `PaymentTransaction(user, status)`, `UserNote(user, -updated_at)`, plus `MealTicket`/`MedicalAppointment`/`TransportBooking`/`ClubEvent` fields.
- `dashboard` transport widget collapsed from a per-route COUNT loop to **one grouped query**; the medical widget uses a single `values_list` for both the booked count and on-duty doctor set. `profile`/`departments`/`clubs` were already N+1-free (`select_related`/`prefetch_related`/grouped aggregates).

**Verification:** `collectstatic` (147 files), `manage.py check` + `check --deploy` clean, **320 tests pass**. Live E2E confirmed: pages/static/media 200 in dev; HTTP→HTTPS 301 in production mode; Redis fallback; fail-closed `SECRET_KEY`; join-club + checkout + notes + research flows round-trip over real HTTP (all verification data cleaned up, server stopped).

---

## 38. Production Deployment — Render (render.yaml Blueprint)

**Date:** 10 August 2026  
**Branch:** main  

### Overview

The app is packaged for one-click deployment on **Render** via a Blueprint (`render.yaml`). Render provisions the web service, a managed PostgreSQL database, and a managed Redis (Key Value) instance — everything is wired together with environment variables, so no separate nginx/systemd/certbot setup is needed (Render terminates TLS automatically at `https://<service>.onrender.com`).

### Files Added / Modified

| File | Purpose |
| :--- | :--- |
| `render.yaml` | Blueprint: web service (Python/Daphne), managed Postgres, managed Redis |
| `build.sh` | Render build command (executable): pip install → collectstatic → migrate → seed_demo_users |
| `config/settings.py` | Render auto-config: `ALLOWED_HOSTS` + `CSRF_TRUSTED_ORIGINS` when `RENDER=true` |
| `requirements.txt` | Added `psycopg2-binary>=2.9.9` (Postgres driver for `DATABASE_URL`) |

### `render.yaml` Blueprint

- **Web Service** (`type: web`, `runtime: python` — the modern replacement for the deprecated `env: python` field):
  - `buildCommand: ./build.sh`  
  - `startCommand: daphne -b 0.0.0.0 -p $PORT config.asgi:application` — Daphne serves both HTTP and WebSockets (`ws/notifications/`) on Render's injected `$PORT` (default `10000`).
  - `healthCheckPath: /` (homepage renders without DB reads — a safe liveness probe).
  - `domains: [niter.edu.bd]` — the production custom domain is attached in the Blueprint (Render auto-provisions Let's Encrypt TLS and the `www` redirect; point the domain's DNS at Render before launching).
  - Env vars: `PYTHON_VERSION: 3.12.3`, `DEBUG: false`, `SECRET_KEY` (`generateValue: true` — Render stores a random secret), `DATABASE_URL` (`fromDatabase`), `REDIS_URL` (`fromService`, type `redis`). `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` are intentionally **not** set — the settings auto-config below fills in `.onrender.com` **and** `niter.edu.bd` (keeping Blueprint syncs from clobbering dashboard-set values).
- **PostgreSQL** (`databases:`): `niter-centralized-dash-db`, plan `free` (`databaseName: niter`, `user: niter`).
- **Redis** (`type: redis` — the documented alias for Render's `keyvalue` service): `niter-centralized-dash-redis`, plan `free`, `maxmemoryPolicy: noeviction`, `ipAllowList: []` (no public access — the web service uses Render's private network, so `connectionString` resolves to the internal `redis://` URL; TLS cert issues are avoided entirely).

### `build.sh`

```bash
#!/usr/bin/env bash
set -o errexit
set -o pipefail

# Render's build image provides `python`; a local checkout may only expose
# `python3` or a venv — prefer an existing venv so ./build.sh also runs locally.
if [ -x "venv/bin/python" ]; then PYTHON="venv/bin/python"
elif command -v python >/dev/null 2>&1; then PYTHON="python"
else PYTHON="python3"; fi

"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install -r requirements.txt
RENDER_BUILD=true "$PYTHON" manage.py collectstatic --noinput
RENDER_BUILD=true "$PYTHON" manage.py migrate --noinput
RENDER_BUILD=true "$PYTHON" manage.py seed_demo_users
```

**Hardening** (`chmod +x build.sh`): `errexit` + `pipefail` abort the build on
any failing step; `RENDER_BUILD=true` tells settings.py this is the **build
phase**, so `collectstatic`/`migrate`/`seed_demo_users` succeed even before
Render injects the service's generated `SECRET_KEY` (see below). Verified
locally: `bash -n build.sh` OK; `manage.py seed_demo_users` runs idempotently
(§69, §76).

### Settings Changes (`config/settings.py`)

Render injects `RENDER=true` for every service. When present, the app **appends** the platform host `.onrender.com`, the production custom domain `niter.edu.bd` (+ `www.`), and `localhost`/`127.0.0.1` to `ALLOWED_HOSTS`; `CSRF_TRUSTED_ORIGINS` gets `https://*.onrender.com` plus `https://niter.edu.bd` / `https://www.niter.edu.bd`. The block only ever **appends** — env-provided hosts still pass through untouched. Non-Render environments (local dev/tests) are unaffected. Verified: `RENDER=true` → `ALLOWED_HOSTS=['.onrender.com','niter.edu.bd','www.niter.edu.bd','localhost','127.0.0.1']`, `CSRF_TRUSTED_ORIGINS=['https://*.onrender.com','https://niter.edu.bd','https://www.niter.edu.bd']`; without `RENDER` → unchanged.

**Build-time SECRET_KEY fallback.** `SECRET_KEY` still **fails closed** at
runtime (`ImproperlyConfigured` when `DEBUG=false` and no secret), but when
`RENDER_BUILD=true` (set only by `build.sh`, never by the start command) a
throwaway placeholder key is used so the build's `collectstatic`/`migrate`/
`seed_demo_users` run cleanly even if the env var hasn't loaded yet. Probes (`.env` moved aside):
`DEBUG=false RENDER_BUILD=true` → check OK; `DEBUG=false` alone →
`ImproperlyConfigured`; `DEBUG=true` → dev fallback key. This is defense-in-depth
— Render's `generateValue` secret is normally injected before the build runs.

WhiteNoise (`CompressedStaticFilesStorage`, middleware) already serves collected static in production — no changes needed; `build.sh` runs `collectstatic` so `staticfiles/` is fresh on every deploy.

### Deploying (First Launch)

1. Commit and push `render.yaml` + `build.sh` (plus the settings/requirements changes) to the GitHub repo (`kn8trix/Niter-centralized-dash`).
2. In the Render dashboard: **New + → Blueprint → select the repo** → Render validates the Blueprint and creates all three resources.
3. First deploy runs `build.sh`: pip install → collectstatic → migrate (seeded departments/clubs come via migration `0009`) → `seed_demo_users` (demo accounts, §69).
4. Open `https://niter-centralized-dash.onrender.com`. The build seeds the demo accounts `admin`/`admin123` and `student`/`student123` automatically (§76) — use `python manage.py createsuperuser` (Render **Shell** tab) only for additional accounts.

### Custom Domain (`niter.edu.bd`)

- Already attached via `domains: [niter.edu.bd]` in `render.yaml` — Render provisions Let's Encrypt TLS automatically (no certbot), and `www.niter.edu.bd` redirects to the root.
- Before the Blueprint launches, point the domain's DNS at Render: `CNAME niter.edu.bd → niter-centralized-dash.onrender.com` (or `A/AAAA` records to Render's IPs).
- Hosts + CSRF origins are handled by the settings auto-config — no env vars needed. To add *further* domains later, extend `domains:` in `render.yaml` AND add them to the `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` env vars in the same file so Blueprint syncs keep them in sync.

### Free-Tier Caveats (plan: free)

- Web services **spin down after 15 min of inactivity** (next request takes ~1 min to cold-start). Use `starter`/`standard` for always-on.
- Free Postgres **expires 30 days after creation** (1 GB cap, one per workspace) — upgrade before then or migrate data off.
- Free web services share 750 instance hours/month per workspace.
- WebSockets are supported on the free plan, but connections drop when the instance spins down — the notification JS should reconnect (the current UI polls `/api/notifications/` as a fallback).

### Verification (local, before deploy)

- `python manage.py check` — no issues  
- `python manage.py check --deploy` — clean under a production env (only the expected warnings from a throwaway test `SECRET_KEY` / empty hosts)  
- `python manage.py test` — **349 tests, OK** (includes the channel-layer fallback resilience tests)  
- `python manage.py collectstatic --noinput` — 147 files post-processed (WhiteNoise compression)  
- `RENDER=true` settings probe — auto-host/CSRF config confirmed working

---

## 39. Production Systems Round-Up: DB Transport Catalog, Medical Chat & Live Queue, CI/CD

**Date:** 10 August 2026  
**Branch:** main  

### 1. Dynamic Transport Catalog & Driver Management

Replaced the hardcoded `TRANSPORT_ROUTES` catalog with real database models (migrations `0012` schema + `0013` seed + `0014` ordering fix):

- **`Driver`** — name, phone, license number, active flag.
- **`TransportRoute`** — name (unique), origin/destination, **per-route capacity**, fare, driver FK, active flag.
- **`BusSchedule`** — one departure time per route (a route runs several trips/day; unique per route; **no string ordering** — alphabetical sorting would put `01:00 PM` before `08:00 AM`, the catalog iterates by insertion id instead).
- Seed (`0013`) mirrors the legacy catalog exactly (`Route 1/2/3`, 40 seats, `08:00/09:30/10:00 AM` primaries, Abdul Karim/Rashed Mia/Faruk Hossain) so existing bookings, the dashboard widget, and legacy `route_id` booking forms keep resolving identically.
- **`_transport_catalog()`** (`core/views.py`) — active DB routes + schedules + driver details keyed by route id, with a legacy-constant fallback for pre-seed databases.
- `transport_dashboard` now renders the live catalog as JSON (`transport-data`); the page's JS renders routes/schedules/driver cards, live booked counts, and a derived status (Full / Few seats left / On Time).
- `book_transport` resolves `route_id` through the catalog and bounds seats by **`route.capacity`** (a capacity-5 route rejects seat 6).
- Admin: `Driver`/`TransportRoute` (with `BusScheduleInline`) registrations.

### 2. Medical Admin & Consultation Chat Engine

**Persistent patient ↔ doctor threads** (`MedicalChatThread` one-per-appointment + `MedicalChatMessage`):

- **REST APIs** (`core/urls.py`): `GET /api/medical/chat/threads/` (staff sees all, students only their own, viewer-scoped unread counts), `POST /api/medical/chat/start/` (idempotent get-or-create; patient may open their own appointment, staff any), `GET|POST /api/medical/chat/<id>/messages/` (history marks the other side's messages read; POST is the non-WS fallback).
- **WebSockets** — `MedicalChatConsumer` on `ws/medical-chat/<thread_id>/` (`core/routing.py` + `core/consumers.py`): membership enforced on connect (thread patient or any staff), messages persisted and broadcast to the `medical_chat_<id>` group; `send_chat_push()` mirrors `notify_user` resilience.
- **Staff UI** (`host/medical/admin_dashboard.html`) — the mock chat panel is replaced with real threads (patient, last message, unread badge, status) + an inline live chat window (WS send/receive, close/fallback to POST).
- **Patient UI** (`templates/medical/booking.html`) — new "My Consultations" section: start a thread from a booked appointment, list open threads, and chat live.

**Real-time doctor queue management**: `GET /api/medical/queue/` (staff-only) returns today's pending→confirmed FIFO queue with positions and counts; the host dashboard (`templates/host/medical/dashboard.html`) renders it and polls every 15s; every `update_appointment_status` call now also creates + pushes a `Notification` to **all active staff** so queue widgets update without a reload.

### 3. CI/CD Deployment Automation

- **`.github/workflows/ci.yml`** — on PRs to `main` and pushes to `main`: checkout → Python 3.12 → `pip install -r requirements.txt` → `manage.py check` → full `manage.py test` suite (SQLite + in-memory channel layer).
- **`.github/workflows/deploy.yml`** — on push to `main`: SSH into the production server (`DEPLOY_HOST`/`DEPLOY_USER`/`DEPLOY_KEY`/`DEPLOY_PORT`/`DEPLOY_PATH` secrets), `git pull --ff-only`, then run the versioned `scripts/deploy.sh` — pip install → `migrate --noinput` → `collectstatic --noinput` → `systemctl reload` the gunicorn/daphne unit. The job is a no-op until `DEPLOY_HOST` is configured; the workflow comments document the matching systemd unit.
- **`scripts/deploy.sh`** — idempotent remote deploy (APP_DIR/VENV_DIR/SERVICE_NAME overridable). Note: if the live target is Render (§38), Render already auto-deploys from the repo on push — this workflow is for a self-hosted gunicorn/daphne server.

### Verification

- `python manage.py check` — no issues · `makemigrations --check` — no changes detected  
- **`python manage.py test` — 349 tests, OK** (29 new: transport catalog models/views + legacy fallback, chat API + WebSocket consumer, queue API, host dashboards)  
- Local `migrate` applied `0012`–`0014` (reverse tested); catalog probe confirms `08:00 AM` / `09:30 AM` / `10:00 AM` primaries

---

## 40. Work Session Summary — Render Deployment, Production Systems & CI/CD

**Date:** 10 August 2026  
**Branch:** main  

### Overview

One work session covering: the **Render Blueprint production deployment** (with the `niter.edu.bd` custom domain), the remaining **low-priority systems** (DB-backed transport catalog, medical consultation chat, live doctor queue), and **CI/CD automation**. Full details in §38 (Render) and §39 (systems + CI/CD).

### Completed

1. **Render Blueprint deployment** — `render.yaml` (web service + managed PostgreSQL + managed Redis, `domains: [niter.edu.bd]`), executable `build.sh` (pip install → collectstatic → migrate → seed_demo_users), `RENDER=true` auto-config in `config/settings.py` (appends `.onrender.com` + `niter.edu.bd`/`www` to `ALLOWED_HOSTS` and CSRF origins), `psycopg2-binary` Postgres driver. → §38
2. **DB transport catalog** — `Driver` / `TransportRoute` / `BusSchedule` models + seed migration (0013); the transport page, dashboard widget, and `book_transport` read live routes/drivers/seats with per-route capacity; legacy-constant fallback for pre-seed databases. → §39.1
3. **Medical consultation chat + live queue** — persistent `MedicalChatThread` / `MedicalChatMessage`; REST APIs + WebSocket consumer (`ws/medical-chat/<id>/`); staff admin chat UI and patient "My Consultations" UI; staff-only FIFO queue API (`/api/medical/queue/`) with real-time staff pushes on status changes. → §39.2
4. **CI/CD** — `.github/workflows/ci.yml` (check + full test suite on PRs to main and pushes), `.github/workflows/deploy.yml` (SSH deploy on push to main, secrets-guarded), `scripts/deploy.sh` (versioned, idempotent remote deploy). → §39.3

### Verification

- `python manage.py check` — no issues · `makemigrations --check` — no changes detected  
- **`python manage.py test` — 349 tests, OK** (29 new)  
- `RENDER=true` probe: `ALLOWED_HOSTS = ['.onrender.com', 'niter.edu.bd', 'www.niter.edu.bd', 'localhost', '127.0.0.1']`, `CSRF_TRUSTED_ORIGINS` includes `https://*.onrender.com` + `https://niter.edu.bd`  
- `render.yaml` validated (no duplicate keys; correct commands/domains/datastores)
---

## 41. Website Builder — Structured Block Component Library

Expanded the Website Builder from raw-HTML ``ContentBlock``s into a structured
component library. The ``render_block`` template tag and the public page
renderer now dispatch on a new ``ContentBlock.block_type`` field.

### 41.1 Block types & JSON schemas

``ContentBlock.block_type`` (default ``html``, migration **0015**) selects the
rendering strategy. Structured types keep their data in ``content_json`` — the
canonical schemas are documented in ``ContentBlock.BLOCK_SCHEMAS``:

| type | partial | ``content_json`` shape |
|------|---------|------------------------|
| ``html`` | — (raw ``content_html``) | — |
| ``faq`` | ``builder/blocks/faq_accordion.html`` | ``{title?, subtitle?, items: [{question, answer}]}`` |
| ``stats`` | ``builder/blocks/stats_grid.html`` | ``{title?, subtitle?, items: [{value, label, icon?, highlight?}]}`` |
| ``testimonials`` | ``builder/blocks/testimonial_slider.html`` | ``{title?, items: [{quote, author, title?, avatar?}]}`` |
| ``cta`` | ``builder/blocks/cta_section.html`` | ``{headline?, subtext?, primary_label?, primary_url?, secondary_label?, secondary_url?}`` |

### 41.2 Rendering & fallback behavior

- ``core/templatetags/builder_tags.py`` — ``render_block`` now loads the
  partial for the block's type via ``render_block_html`` (shared with
  ``core/views.editable_page_view`` so the tag and the live page never
  diverge). Fallbacks, in order: partial render failure / missing partial →
  ``content_html`` → ``default_text``. A broken block never 500s a page.
- Structured blocks with **empty** ``content_json`` render the default/empty
  state; ``data.items`` is normalized so a missing ``items`` key safely hits
  the ``{% empty %}`` branch instead of resolving to the dict's bound method.
- ``editable_page.html`` renders ``block.rendered_html`` (partial output for
  structured types, raw HTML otherwise); the visual editor gains a
  ``block-type-badge`` in the inspector and shows ``block_type``/``content_json``
  in its block payloads.
- ``save_content_block`` accepts optional ``block_type`` / ``content_json``
  (invalid types are coerced to ``html``); a plain HTML save preserves an
  existing structured block's type and data.
- ``safe_url`` template filter guards CTA ``href`` values (only http(s)/
  mailto/tel/ftp, relative and ``#`` links pass; ``javascript:`` is neutralized)
  so ``content_json`` URLs get the same scheme allow-list as the HTML sanitizer.
- ``render_block_html`` treats a non-dict ``content_json`` (hand-edited in the
  admin) as malformed and falls back — a broken block never 500s a page.

### 41.3 Client-side behaviour (dependency-free)

- FAQ accordion — native ``<details>/<summary>``, no JS required, CSS chevron
  rotation on ``[open]``.
- Stats grid — ``IntersectionObserver`` count-up animation for the leading
  digits of each value (suffixes like ``+``/``%`` preserved); ``highlight``
  cards use the dark accent.
- Testimonial slider — vanilla-JS track slider: prev/next arrows, dot
  navigation, 7s auto-advance, hover pause, touch swipe. Static list without JS.
- CTA section — gradient banner with primary + secondary pill buttons; each
  button renders only when both its label and URL are set.

All component styles live in ``static/css/editable_page.css`` (§7), matching
 the warm-light theme tokens. A local demo page (``/page/component-demo/``)
 exercises all four components.

### 41.4 Verification

- `python manage.py check` — no issues · `makemigrations --check` — no changes
- Builder tests: `python manage.py test core.tests.BuilderBlockLibraryTest`
  (18 tests: model defaults, partial dispatch, fallbacks incl. non-dict JSON,
  ``safe_url`` filter, save-API structured fields, live-page rendering, editor
  badge). Note: the spec's literal `core.tests.test_builder` label does not
  resolve — builder tests live in `core/tests.py`.
- **`python manage.py test` — 367 tests, OK** (18 new, 349 prior)
- Browser smoke test of ``/page/component-demo/`` — all four components render,
  no console errors.

---

## 43. Notes Engine — Live Academic Catalog Wiring (`/notes/`)

**Date:** 10 August 2026  
**Branch:** main (working tree, uncommitted)

### Overview

The Notes Engine sidebar previously rendered hardcoded mock rows (two static
folders, three fake PDFs). It now reads the same live academic catalog as
`/academic-notes/` and the editor's file-selection flow uses a real API:

- **Folders** — built from the real `Department` model: one folder per
department that owns at least one `Course`, named from the hub row (falling
back to `StudentProfile.DEPARTMENT_CHOICES` for codes without a hub),
annotated with the course count. Clicking a folder filters the Recent PDFs
list to that department (client-side, keyboard-accessible).
- **Recent PDFs** — the newest `CourseMaterial` rows (`select_related` course),
each linking to the real `file.url` with course code, size, and upload date.
- **My Notes** — the signed-in user's `UserNote` rows (already live); note
clicks now fetch the full content over `GET /api/notes/<id>/` (owner-scoped
404) instead of embedding it in `data-*` attributes, and the editor tracks
the loaded note id so **Save Note** updates the existing row rather than
creating a duplicate.
- The sidebar search input now actually filters folders / PDFs / notes.

### Files

- `core/views.py` — `notes` view context now queries `Course` / `Department` /
  `CourseMaterial` (folders + materials + user notes); new `get_note`
  endpoint (`GET /api/notes/<id>/`, `@login_required`, owner-scoped 404).
- `core/urls.py` — `api/notes/<int:note_id>/` route.
- `templates/notes/notes_engine.html` — dynamic folders/PDFs loops, fetch-
  backed note loading, `note_id`-aware save, sidebar search + folder filter.
- `core/tests.py` — `NotesEnginePageTest` (live folders/materials/empty
  states) + `get_note` API tests (owner fetch, cross-user 404, login gate).

### Verification

- `python manage.py check` — no issues
- `python manage.py test core.tests.AcademicNotesPageTest core.tests.NotesEnginePageTest core.tests.NotesEngineApiTest` — OK
  (note: the literal `core.tests.test_academic_notes` label does not resolve —
  the tests live in `core/tests.py`, same as §41's `test_builder` note)
- Full suite — 373 tests, OK (6 new)

---

## 42. Dependency Hardening — PyJWT / Cryptography for allauth Google OAuth

**Date:** 10 August 2026  
**Branch:** main (working tree, uncommitted)

### Overview

`django-allauth` only declares its Google/OIDC JWT requirements
(`pyjwt[crypto]>=1.7`, `requests`) under the optional **`socialaccount`** extra,
so a plain `pip install -r requirements.txt` never installed them. On a fresh
environment (CI, Render build, new local clone) Django crashed during startup
when the Google provider module loaded:

```
File ".../allauth/socialaccount/providers/google/provider.py", line 7, in <module>
    from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
File ".../allauth/socialaccount/providers/google/views.py", line 13, in <module>
    from allauth.socialaccount.internal import jwtkit
File ".../allauth/socialaccount/internal/jwtkit.py", line 3, in <module>
    import jwt
ModuleNotFoundError: No module named 'jwt'
```

**Verified end-to-end:** installing the previous `requirements.txt` into a
clean venv and running `manage.py check` reproduced exactly that traceback
(and showed `cryptography` already arriving transitively via
`twisted[tls]`→pyOpenSSL while `PyJWT` was missing). The system-wide Python
happened to have PyJWT installed, which masked the problem locally.

### Changes (`requirements.txt`)

- **Added `PyJWT[crypto]>=2.8,<3.0`** — the `[crypto]` extra installs
  `cryptography` for the RS256 key handling. Without it the Google provider's
  `jwtkit` import fails at startup with `ModuleNotFoundError: No module named
  'jwt'`.
- **Pinned channels/daphne implicit dependencies explicitly** so fresh
  installs never rely on transitive resolution order:
  - `asgiref>=3.9,<4.0` — required by channels (>=3.9.0) and daphne (>=3.5.2)
  - `autobahn>=22.4.2,<27` — daphne's WebSocket protocol library
  - `twisted[tls]>=22.4,<27` — daphne's ASGI server engine (TLS extra pulls
    pyOpenSSL + service-identity + cryptography)
- `requests` / `requests-oauthlib` are the remaining `socialaccount` extra
  requirements — `requests` was already pinned; `requests-oauthlib` is now
  explicit too (previously only arriving transitively via `google-auth-oauthlib`).

No `config/settings.py` change was needed — the Google provider was already
correctly in `INSTALLED_APPS`; the failure was purely a missing install-time
dependency. CI (`ci.yml`) installs from `requirements.txt`, so the fix flows
through automatically.

### Verification

- **Repro:** clean venv + old `requirements.txt` → `python manage.py check`
  fails with `ModuleNotFoundError: No module named 'jwt'`.
- **Fix:** clean venv + updated `requirements.txt` → `pip install` resolves
  cleanly (`PyJWT` 2.x + `cryptography` present) → `python manage.py check` —
  no issues.
- **Full test suite:** `python manage.py test` — 367 tests, OK.

---

## 44. Settings Overhaul — Tabbed Dashboard, Google OAuth Integration, Topbar Fix

**Date:** 10 August 2026  
**Branch:** main (working tree, uncommitted)

### Overview

The settings page was redesigned from a single-column layout into a **tabbed
dashboard** with three tabs (Notifications, Account & Google, Display). The
topbar gained a **Settings gear icon** next to the CampusDash brand so the
settings link is always one click away regardless of which page the user is
on. On the backend, the `UserNotificationPreference` model was extended with
per-category notification toggles and a timezone selector, and a new API
endpoint lets students disconnect their Google account.

### Changes

**Topbar (`templates/partials/topbar.html` + `static/css/topbar.css`):**
- Added a `.settings-link` gear icon (``<i class="fa-solid fa-gear"></i>``)
  right after the brand, linking to `/settings/`. Always visible, keyboard-
  focusable, styled consistently (hover rotates + lifts).

**Settings page (`templates/settings.html`):**
- Tabbed navigation with three panels (client-side switch, no page reload):
  - **Notifications** — per-category toggles (Meals, Transport, Medical,
    Notices) and channel-level toggles (Email, SMS, Push), all persisted
    to the database via JSON POST.
  - **Account & Google** — password change form (Django `PasswordChangeForm`)
    + Google integration card showing connection status (connected email,
    Drive/Sheets scope summary) with an "Unlink" button.
  - **Display** — Warm Light / Dark theme picker + timezone selector
    (Asia/Dhaka, UTC, US Eastern, Europe/London, etc.).

**View (`core/views.py`):**
- `settings_view` now passes `google_social` (allauth `SocialAccount`),
  `has_google_token`, and `active_tab` (from `?tab=` query param).
- `_save_settings_prefs` persists the new `notify_*` fields and `timezone`;
  only fields explicitly present in the payload are updated (partial toggle
  saves no longer reset other preferences to defaults).
- New `google_unlink` endpoint (`POST /api/settings/google-unlink/`) deletes
  the user's allauth `SocialAccount` and `GoogleUserToken` rows.

**Model (`core/models.py`):**
- `UserNotificationPreference` — five new fields:
  - `notify_meals`, `notify_transport`, `notify_medical`, `notify_notices`
    (BooleanField, default `True`)
  - `timezone` (CharField, choices from `TIMEZONE_CHOICES`, default
    `'Asia/Dhaka'`)

**Migration:** `core/migrations/0016_…` (applied).

**URLs (`core/urls.py`):**
- `api/settings/google-unlink/` → `google_unlink`.

**Tests (`core/tests.py`):**
- `SettingsPreferencesTest` — updated for new fields + `force_login`;
  new test for JSON update of category/timezone fields.
- `test_google_unlink_removes_token` — HTTP 200 + token deletion.
- `test_google_unlink_requires_login` — HTTP 401 for unauthenticated users.

### Verification

- `python manage.py check` — no issues
- `python manage.py test core.tests.SettingsPreferencesTest` — 9 tests, OK
- Full suite — **376 tests, OK** (3 new)

---

## 45. Notes Engine Converted to CampusDash Top-Pill Layout (sidebar refactor reverted)

**Date:** 10 August 2026  
**Branch:** main (committed & pushed)

### Overview

The left-sidebar "Niter Hub" refactor from an earlier session was **reverted**
and the app is back on the standalone **CampusDash top-pill** layout for every
student page. The Notes Engine — the last page still rendering inside the
left-sidebar shell — was converted to the shared top-pill layout so it matches
`dashboard.html` / `notices.html`.

### Reverts

- `71df21b` — reverted a HANDOVER doc-tweak commit (`641acaf`).
- `e117180` — reverted `b2404c3` (the left-sidebar refactor): the 9 student
templates are standalone again, `core/tests.py` is a single test module once
more, and `core/tests/test_navigation.py` was removed.

### Notes Engine (`templates/notes/notes_engine.html`, `/notes/`)

- **Removed the left vertical sidebar** — the template no longer extends
  `base.html` (no `Niter Hub` sidebar column, no mobile drawer).
- **Includes `partials/topbar.html`** (`active='notes'`) at the top of the
  standard `.shell` container, exactly like `dashboard.html` / `notices.html`.
- Added the shared `.intro` header (styled by `topbar.css`).
- The workspace (folder list, markdown editor, AI summary preview) renders
  unchanged inside the shell; the Tailwind CDN + theme-token config from the
  sidebar version were kept so the `bg-card` / `border-border` / `bg-accent`
  classes still work, alongside `notes.css` for `body.notes` + `.shell`.
- Workspace desktop height retuned to `lg:h-[calc(100vh-200px)]` to fit below
  the topbar + intro chrome.

### Tests (`core/tests.py`)

- `NotesEnginePageTest.test_uses_campusdash_top_pill_header` — asserts the
  topbar partial (`data-component="topbar"`), the `CampusDash` brand, the
  profile `avatar-btn`, and **no** `data-region="sidebar"` on `/notes/`.

### Verification

- `python manage.py check` — no issues
- `python manage.py test core.tests.NotesEnginePageTest` — 4 tests, OK
- `python manage.py test core.tests.UnifiedHeaderTest` — 2 tests, OK
- Full suite — **377 tests, OK** (376 + the new topbar assertion)
- Live check of `/notes/`: topbar renders, sidebar absent, workspace present.

---

## 46. Settings View & Top-Left Gear Icon (Top-Pill Layout)

**Date:** 10 August 2026  
**Branch:** main (committed & pushed)

### Overview

Verified the Settings feature inside the CampusDash top-pill layout. The
tabbed settings page and the always-visible top-left gear icon shipped in the
Settings Overhaul (section 44 / `91992cb`) and survive the sidebar-refactor
reverts unchanged — no code changes were needed; this section records their
presence in the current top-pill architecture and confirms the checks pass.

### Topbar (`templates/partials/topbar.html` + `static/css/topbar.css`)

- Gear icon (`.settings-link`, `<i class="fa-solid fa-gear"></i>`) sits
  top-left next to the "CampusDash" brand on every top-pill page and links to
  `/settings/`; styled as a 32px circular button with hover lift.

### Settings page (`templates/settings.html`)

- Renders inside the top-pill shell (`{% include 'partials/topbar.html' %}`)
  with the `.intro` header — no left sidebar required.
- Three tabs (client-side switch, `?tab=` deep link):
  1. **Notification Preferences** — category toggles (Meals, Transport,
     Medical, Notices) + channel toggles (Email, SMS, Push), persisted via
     JSON POST to `/settings/`.
  2. **Account & Google** — password change form + Google OAuth status card
     (connected email / not connected) with **Unlink** (`POST
     /api/settings/google-unlink/`) and Connect buttons.
  3. **Display** — Warm Light / Dark theme toggle + timezone selector.

### Backend (`core/views.py`, `core/urls.py`)

- `settings_view` (login-gated), `_save_settings_prefs` (form + JSON, partial
  updates only), `google_unlink` (deletes `SocialAccount` + `GoogleUserToken`).
- Routes: `/settings/`, `api/settings/google-unlink/`.

### Verification

- `python manage.py check` — no issues
- `python manage.py test core.tests.SettingsPreferencesTest
  core.tests.AccountAndAdminPagesTest` — 22 tests, OK

## 47. Header Layout Fix — Profile Menu Moved Top-Left, Gear Icon Removed

Replaces the standalone settings gear icon with a cleaner top-left header
group. The profile avatar is now anchored directly beside the **CampusDash**
brand, and the desktop nav pills sit on a second row beneath the header.

### Topbar structure (`templates/partials/topbar.html`)

- **Row 1 (`div.topbar-row`)** — brand + profile avatar grouped in
  `div.topbar-left` on the left; the notification bell stays on the right
  (authenticated users only).
- **Row 2 (`nav.navlinks`)** — the horizontal top-pill navigation bar
  (Dashboard, Academic Notes, Departments, Research AI, Notices, Transport,
  Meals, Medical, Clubs) aligned beneath the header row.
- **Standalone gear removed** — no more `a.settings-link` next to the brand;
  Settings is reachable from the profile menu's *Settings* item (gear icon
  inside the popover) at `/settings/`.
- **Profile popover** — clicking the avatar still opens the menu with user
  info, page links (mobile), and account actions: a new *Notifications* item
  (opens the bell dropdown, authenticated only), *Settings*, *Switch
  Account*, and *Sign Out*.
- Popover now anchors with `left: 0` since the avatar sits at the far left.

### CSS (`static/css/topbar.css`)

- `.topbar` switched to a column flex (two rows) with `gap: 1rem`.
- Added `.topbar-row` / `.topbar-left`; removed the `.settings-link` rules
  and its `:focus-visible` entry; `.profile-popover` re-anchored to `left`.
- Mobile (`<768px`): the popover re-anchors to the header group
  (`.profile { position: static }` + `.topbar-left { position: relative }`)
  so the full-page menu opens from the viewport edge and never overflows
  narrow screens.

### Tests (`core/tests.py`)

- `UnifiedHeaderTest` asserts the `topbar-row`/`topbar-left` group exists on
  every public page and that the standalone `class="settings-link"` is **gone**.
- `ProfilePopoverAuthTest` asserts the *Notifications* entry
  (`id="profile-notif-link"`) renders for authenticated users and is
  **not** rendered for guests.

### Verification

- `python manage.py check` — no issues
- `python manage.py test core.tests.UnifiedHeaderTest
  core.tests.ProfilePopoverAuthTest` — 4 tests, OK
- Full suite — **377 tests, OK**
- Live checks on `/dashboard/`, `/transport/`, `/medical/`, `/clubs/`,
  `/notes/` all serve the two-row header (`topbar-row` + `topbar-left`
  present, `settings-link` count 0, `avatar-btn` present).

## 48. User Registration & Authentication Flow (Sign-Up Form)

Self-registration already existed; this pass extracted the inline view
validation into a clean, reusable form and added the missing cross-links.

### `core/forms.py` (new)

- `SignUpForm` — fields: `student_id` (max 30), `full_name`, `department`
  (from `StudentProfile.DEPARTMENT_CHOICES`), `email`, `password`
  (`min_length=8`), `confirm_password`.
- Validation: duplicate **Student ID** (checks `User.username` and
  `StudentProfile.student_id`) and duplicate **email** (case-insensitive),
  password/confirm match (`Passwords do not match.`), short password
  (`Ensure this value has at least 8 characters.`), invalid department.
- `save()` — `User.objects.create_user(...)` (pbkdf2-hashed password) +
  `StudentProfile`, splitting full name into first/last.

### `core/views.py` — `signup_view` refactored

- POST → `SignUpForm(request.POST)`; on valid, `form.save()` then
  `auth_login(request, user)` and `redirect('dashboard')` (auto-login).
- Form errors are flattened into the simple list `signup.html` renders.
- GET renders the empty form; template contract (`errors`, `departments`,
  `form_data`) unchanged.

### Login (`config/urls.py`)

- `/login/` uses Django's built-in `auth_views.LoginView` (which authenticates
  against stored users via `authenticate()` + `login()`), `template_name='login.html'`,
  `redirect_authenticated_user=True`. `/logout/` uses `LogoutView`.
- `templates/login.html` gained a **"New to Niter Hub? Create an account"**
  link to `/signup/` (styled `.auth-switch` in `auth.css`).

### Tests (`core/tests.py`)

- New `SignUpFormTest` (6 tests): valid save + hashed password + profile,
  duplicate ID / duplicate email, password mismatch, short password, invalid
  department. Existing `LoginFlowTests` + `AccountAndAdminPagesTest` cover the
  view flow (redirect to dashboard, auto-login, `authenticate()` login).

### Verification

- `python manage.py check` — no issues
- `python manage.py test core.tests.LoginFlowTests core.tests.AccountAndAdminPagesTest
  core.tests.SignUpFormTest core.tests.ProfilePopoverAuthTest` — 26 tests, OK
- Full suite — **383 tests, OK**
- Live E2E (curl): POST `/signup/` → 302 to `/dashboard/`; user persisted with
  `pbkdf2_sha256`; `authenticate()` returns the user; duplicate-ID POST rejected
  (CSRF token rotates on login — Django security default).

## 49. Header Layout — Profile Menu Moved to Top-Right Corner

Supersedes the top-left placement from section 47: the brand sits cleanly in
**top-left**, and the user profile avatar + notification bell are grouped in
the **top-right** corner of the header row, with the nav pills on the second
row beneath.

### Topbar structure (`templates/partials/topbar.html`)

- **Row 1 (`div.topbar-row`, `justify-content: space-between`)** — brand
  (`a.brand`) is now a direct child on the left; a new `div.topbar-right`
  group on the right holds the notification bell (authenticated only) then
  the user profile avatar (rightmost).
- **Row 2 (`nav.navlinks`)** — unchanged pill bar beneath the header row.
- Profile popover unchanged: user info, page links (mobile), and account
  actions (Notifications → opens bell, Settings, Switch Account, Sign Out).
- Removed the now-unused `.topbar-left` wrapper.

### CSS (`static/css/topbar.css`)

- `.topbar-left` replaced by `.topbar-right` (flex, `gap: 0.6rem`).
- `.profile-popover` re-anchored to `right: 0` (avatar is back at the far
  right, so the dropdown extends leftward and always fits on screen).
- Dropped the mobile `position: static` / `.topbar-left` anchoring hack from
  section 47 — no longer needed.

### Tests (`core/tests.py`)

- `UnifiedHeaderTest` now asserts `class="topbar-right"` (instead of
  `topbar-left`) and still asserts the standalone gear is gone.

### Verification

- `python manage.py check` — no issues
- `core.tests.UnifiedHeaderTest` + `ProfilePopoverAuthTest` + header
  dependents — 18 tests, OK
- Full suite — **384 tests, OK**
- Live checks: every public page serves `topbar-right` (and no
  `topbar-left`/`settings-link`); authenticated render confirms DOM order
  bell → profile inside `.topbar-right`, brand inside `.topbar-row`, and
  `profile-notif-link` still present.

---

## 50. Settings Tab Navigation & Account/Display Panels

**Date:** 11 August 2026  
**Branch:** main

### Overview

Fixed the Settings page tab navigation and completed the Account & Google and
Display panels so every tab is fully functional and persisted to the database.

### Completed Work

1. **Tab navigation fix (`templates/settings.html`)**
   - The active tab button is now marked with the `active` class server-side
     (matching `?tab=`), so the highlighted pill renders correctly on first
     load instead of only after a click. Click handlers, `?tab=` URL sync, and
     panel `hidden` toggling are unchanged.

2. **Account & Google tab**
   - New **Profile Details** section: read-only Student ID, editable Full Name
     and Email, and a **Save Account Settings** button.
   - `settings_view` now accepts a hidden `form=profile` POST and persists
     name/email via the new `_save_profile_settings` helper (splits Full Name
     into first/last name, validates email format with Django's
     `validate_email` + uniqueness across accounts, and renders inline
     success/error alerts).
   - Password Reset and Google OAuth (Connect / Unlink) sections unchanged.

3. **Display tab**
   - Theme picker upgraded from a 2-way boolean (Warm Light / Dark) to a
     tri-state **Light Mode / Dark Mode / System Default** picker.
   - New **Layout Density** picker: Comfortable / Compact (persisted as
     `compact_layout`; the settings page tightens its own spacing when
     Compact is active).
   - Timezone selector unchanged.

### Backend

- `UserNotificationPreference` gained `theme` (CharField: light/dark/system,
  default light) and `compact_layout` (BooleanField) fields; the legacy
  `dark_mode` boolean is kept for backward compatibility.
- Migration `0017_usernotificationpreference_theme_compact_layout` adds both
  fields and backfills `theme` from the legacy `dark_mode` boolean.
- `_save_settings_prefs` accepts `theme` and `compact_layout` keys, keeps the
  legacy `dark_mode` key working, and keeps `dark_mode` in sync with `theme`
  so older callers stay correct (partial updates preserved).
- `UserNotificationPreferenceAdmin` lists the two new fields.

### Frontend

- Theme JS resolves `system` via `matchMedia('(prefers-color-scheme: dark)')`
  (with Safari < 14 `addListener` fallback) and live-updates when the OS theme
  changes; the selection persists via the `theme` key. The save toast was
  moved to a fixed floating pill so it is visible from every tab.

### Testing

- `python manage.py check` ✔ (no issues)
- `python manage.py test` ✔ (389 tests — added coverage for the tri-state
  theme, the layout toggle, and the profile form: success, duplicate email,
  invalid email)
- Verified over HTTP: login → `/settings/` renders all three tabs; the Account
  panel shows Profile Details + Save Account Settings + Google status; the
  Display panel shows Light/Dark/System, timezone, and Comfortable/Compact;
  `?tab=display` activates the Display panel and hides the others; inline JS
  passes `node --check`.

---

## 51. Website Builder Component Library — Verification Pass

**Date:** 11 August 2026  
**Branch:** main

### Overview

Re-verified the structured block component library (FAQ Accordion, Stats
Counter Grid, Testimonial Slider, CTA Section) first built in §41. The
feature was already fully implemented; this pass confirms every requirement
and re-runs the full builder test battery.

### Confirmed (no code changes needed)

1. **Models (`core/models.py`)** — `ContentBlock.BLOCK_TYPE_CHOICES` already
   includes `faq` / `stats` / `testimonials` / `cta` (migration 0015) and
   `BLOCK_SCHEMAS` documents each type's `content_json` shape.
2. **Partials (`templates/builder/blocks/`)** — `faq_accordion.html`,
   `stats_grid.html`, `testimonial_slider.html`, `cta_section.html` all exist
   and match the schemas.
3. **Renderer (`core/templatetags/builder_tags.py`)** — `render_block` already
   dispatches by `block_type` through `_BLOCK_PARTIALS` with layered fallbacks:
   missing/malformed partial or bad JSON → `content_html` → `default_text`
   (a broken block never 500s a page).

### Verification

- `python manage.py check` — no issues
- `python manage.py makemigrations --check --dry-run` — no changes
- `python manage.py test core.tests.BuilderBlockLibraryTest
  core.tests.EditablePageRenderTest core.tests.BuilderBackendTest` — **52 tests,
  OK** (18 block-library tests cover model defaults, partial dispatch,
  fallbacks, `safe_url`, save-API structured fields, live-page rendering, and
  the editor badge)
- Live check: `/page/component-demo/` serves 200 and renders all four
  components (`data-builder-block="faq|stats|testimonials|cta"`).

Note: the literal `core.tests.test_builder` label from the task spec does not
resolve — builder tests live in `core/tests.py` (§41.4).

---

## 52. Website Builder Visual Editor — Live Canvas Controls & Block Management

**Date:** 11 August 2026  
**Branch:** main

### Overview

Enhanced the visual editor (`/builder/edit/<slug>/`) with responsive preview
canvas toggles, per-block Move Up / Move Down / Delete management wired to an
atomic reorder API, and instant custom-CSS injection into the live preview.

### Completed Work

1. **Canvas viewport toggles (`templates/builder/editor.html`, CSS)**
   - Desktop (fluid), Tablet (768px centered) and Mobile (375px centered)
     preview buttons with smooth `max-width`/`width` transitions on the canvas
     frame and iframe; toggles report the active width via toast and
     `aria-pressed`.

2. **Block management (`editor.html`, `editor.js`, `core/views.py`)**
   - Each inspector block card now carries **Move Up / Move Down / Delete**
     handles (first/last cards disable the corresponding move button).
   - Move buttons POST the full order to `/api/builder/save-block/` as one
     atomic `reorder` payload (`{page_slug, reorder: [{element_id, order}…]}`)
     and then refresh the canvas iframe; on failure the optimistic DOM swap is
     reverted so UI always matches the DB.
   - Delete POSTs `{delete: true}` to the same endpoint (superuser-gated),
     removes the card, updates the block count and refreshes the canvas.
   - `ContentBlock.order` (PositiveIntegerField, migration **0018**) + `Meta
     ordering ['order', 'id']`; the live page (`editable_page_view`) and the
     editor (`visual_editor`) render blocks in order. New blocks created via
     the API append after the page's last block unless an explicit `order` is
     sent. `save_content_block` validates every reorder entry before a single
     `transaction.atomic` (unknown block → 400, nothing persisted).

3. **Instant CSS injection (`editor.html`, `editor.js`)**
   - New **Save CSS** button persists `/api/builder/save-css/` and re-injects
     the `<style>` block straight into the preview iframe `<head>` — no page
     reload. Typing already previews live; Save CSS persists.

4. **Latent fix** — server-rendered inspector cards were never wired to the
   edit handlers (only dynamically discovered cards were). `wireItem` is now
   idempotent and applied to every card on init, so editing, selection, and
   the new action handles work on first load.

### Verification

- `python manage.py check` — no issues
- `python manage.py makemigrations --check --dry-run` — no changes
- `python manage.py test core.tests.BuilderBlockLibraryTest
  core.tests.EditablePageRenderTest core.tests.BuilderBackendTest
  core.tests.BuilderBlockOrderingTest` — **61 tests, OK** (10 new ordering
  tests: order default, API append order, atomic reorder, unknown-block and
  bad-entry rejection, delete, ordered live-page rendering, editor markup)
- **Full suite — 398 tests, OK**
- `node --check static/js/builder/editor.js` — syntax OK
- Rendered `/builder/edit/component-demo/` (superuser): Save CSS button,
  per-block Move Up/Down/Delete handles, and the 3 viewport buttons all
  present.

Note: block management handles live on the inspector cards (the builder's
block-management surface) rather than on the canvas wrappers, so the public
page markup stays clean. The spec's literal `core.tests.test_builder` label
still does not resolve — builder tests live in `core/tests.py` (§41.4).

---

## 53. Page Lifecycle Management & Automatic Navigation Linking

**Date:** 11 August 2026  
**Branch:** main

### Overview

Added page lifecycle controls (publish gating + SEO description) and wired
published builder pages flagged ``show_in_nav`` into the shared top navigation
as a live, DB-backed Pages menu.

### Completed Work

1. **Lifecycle flags (`core/models.py`, migration 0019)**
   - ``EditablePage.seo_description`` — optional meta description rendered in
     the ``<meta name="description">`` tag of ``/page/<slug>/`` (falls back to
     the page title).
   - ``EditablePage.show_in_nav`` (default False, indexed) — opt-in flag that
     surfaces a page in the top navigation. ``is_published`` already existed
     (default True) and is unchanged.
   - Admin: ``show_in_nav`` added to ``list_display`` / ``list_filter``.

2. **Publish gating (`core/views.py`)**
   - ``editable_page_view`` now 404s unpublished drafts for everyone except
     super admins, who reach them from the builder to preview work in
     progress. Existing anonymous 404 behaviour is preserved.

3. **Automatic navigation (`core/context_processors.py`, `config/settings.py`)**
   - New ``custom_pages_nav`` context processor exposes ``NAV_CUSTOM_PAGES``
     (published + ``show_in_nav`` pages ordered by title) to every template;
     registered in ``TEMPLATES``. The query is one small indexed lookup per
     render — note: any future test that renders a full page must subclass
     ``TestCase`` (``ResearchAIPageTest`` was converted for this reason).

4. **Topbar integration (`templates/partials/topbar.html`, `topbar.css`)**
   - Desktop: a **Pages** dropdown pill in the nav row lists every custom
     page with the current page highlighted; open/close on click, outside
     click, or Escape with ``aria-expanded`` + caret rotation.
   - Mobile: the same links appear under a **Custom Pages** label inside the
     profile menu (desktop pills are hidden on mobile, so each set renders
     exactly once).
   - ``editable_page.html`` now emits the page's ``seo_description`` in the
     meta description.

### Verification

- ``manage.py check`` — clean · ``makemigrations --check`` — no changes
- Builder tests (render / backend / block library / ordering / custom nav) —
  **66 tests OK** (5 new: superuser draft preview, staff draft 404, SEO meta,
  context-processor filtering, topbar dropdown rendering)
- Full suite — **403 tests OK**
- Live render check: flagged page appears twice in the topbar (dropdown +
  mobile menu) and the SEO meta is present.

---

## 54. Frontend Visual Page Builder & Drag-and-Drop Block Manager

**Date:** 11 August 2026  
**Branch:** main

### Overview

Added a frontend page builder at ``/builder/edit/<slug>/`` with a page-settings
toolbar (title, slug display, Published + Show-in-Nav toggles, Save Draft /
Publish), a drag-and-drop block manager with a section palette, and two new
AJAX endpoints for atomic reorder and block save. The older split-screen
canvas editor moved to ``/builder/visual/<slug>/``.

### Completed Work

1. **Page builder UI (`templates/builder/edit_page.html`, new)**
   - Top toolbar: editable page title, read-only slug chip, **Published** and
     **Show in Nav** toggle switches, SEO description input, **Save Draft**
     (sets ``is_published=false``) and **Publish** buttons, plus a link to the
     canvas Visual Editor.
   - Left panel: sortable block list (drag handle, type badge, element id,
     edit/delete), an **Add Block** palette with all section types, and an
     inline block editor (type select + content HTML + content JSON). Block
     contents are embedded safely via ``json_script`` for the editor.
   - Right panel: live preview iframe that refreshes after every mutation
     without a full page reload.
   - ``static/js/builder/page_manager.js`` + ``static/css/builder_page.css``.

2. **New section block types (`core/models.py`, partials, migration 0020)**
   - **Hero Header** (``hero``) and **Feature Cards Grid** (``features``)
     added to ``BLOCK_TYPE_CHOICES`` / ``BLOCK_SCHEMAS`` / the partial map;
     partials ``hero_section.html`` + ``features_grid.html``. The ``html``
     label is now **Text Block**. Migration 0020 records the choices change.

3. **Endpoints (`core/views.py`, `core/urls.py`)**
   - ``/builder/api/blocks/reorder/`` — atomic drag-and-drop reorder (all
     orders change in one transaction or none).
   - ``/builder/api/blocks/save/`` — create / update / delete a block (HTML
     sanitized on save, same trust model as the legacy endpoint).
   - ``/builder/api/page/save/`` — persist title / publish state / nav flag /
     SEO description; only keys present are written.
   - ``save_content_block`` refactored into shared helpers
     (``_get_builder_page`` / ``_reorder_content_blocks`` /
     ``_save_content_block_data``) used by both the legacy and new endpoints.

4. **Access control (`core/decorators.py`)**
   - New ``@change_editablepage_required`` decorator gates every builder route
     on the ``core.change_editablepage`` permission (staff may be granted it;
     superusers pass implicitly). Anonymous visitors redirect to login, logged-
     in users without the permission get 403 — matching the project's existing
     ``superuser_required`` UX (Django 4.2's ``permission_required(
     raise_exception=True)`` would 403 anonymous users, so a custom decorator
     is used).
   - ``editable_page_view`` draft preview now opens to permission holders
     (was superuser-only) so authorized builders can preview drafts in the
     builder's iframe.

5. **Routing** — ``builder_editor`` at ``/builder/edit/<slug>/``, the canvas
   ``visual_editor`` at ``/builder/visual/<slug>/``, and the dashboard's
   **Edit Page** button now opens the page builder (New Page lands there too).

### Verification

- ``manage.py check`` — clean · migrations consistent (0020 applied)
- Builder tests (backend / block library / render / ordering / custom nav /
  page manager) — **82 tests OK** (13 new: permissions, toolbar, reorder /
  block-save / page-save endpoints, new section types, draft preview for
  permission holders)
- Full suite — **419 tests OK** · ``node --check page_manager.js`` — clean
- Live check: toolbar + 7-type palette + 4 block rows render; save / reorder /
  page-save APIs return success; nav dropdown + hero/features partials render

---

## 55. Block Library Drawer, Section Creation & Deletion

**Date:** 11 August 2026  
**Branch:** main

### Overview

Added a block library to the frontend page builder: on-canvas "+ Add New
Section" insert handles (between sections and at the bottom) open a modal
drawer with four selectable section templates (live previews), backed by a
create endpoint and a delete-by-id endpoint with a soft-confirmation modal.

### Completed Work

1. **Section canvas (`templates/builder/edit_page.html`, `builder_page.css`)**
   - The right pane now renders an inline **canvas**: every block is shown
     as a real section (server-rendered partial, page ``custom_css`` applied)
     with a hover toolbar (type badge, edit, delete) and a dashed
     "**+ Add New Section**" insert handle after it, plus a large one at the
     bottom. A **Canvas / Live Preview** tab switcher toggles between the
     inline canvas and the existing page iframe.

2. **Block library drawer (modal)**
   - Insert handles (and the bottom button) open a modal presenting four
     template cards, each with a live partial preview, name and description:
     **Hero Section**, **Feature Grid**, **Text & Image Split** and
     **Announcement Banner / CTA**. Picking one POSTs to the create endpoint
     at the chosen position. Cards are keyboard accessible (role=button +
     Enter/Space) and previews are derived from the same default content the
     create endpoint seeds, so the preview always matches what is created.

3. **Endpoints (`core/views.py`, `core/urls.py`)**
   - ``/builder/api/blocks/create/`` — accepts ``{page_id, block_type,
     order_index?}``; seeds default content (``_BLOCK_TEMPLATES``) and
     inserts atomically, shifting existing blocks at/after the target order
     up by one (``F('order') + 1``) or appending when no index is given.
     Element ids are random-hex suffixed to stay unique.
   - ``/builder/api/blocks/<block_id>/delete/`` — removes a block by its
     database id, called from a **soft-confirmation modal** (Cancel/Delete,
     backdrop click or Escape closes; the old ``window.confirm`` is gone).
   - Both are gated by ``@change_editablepage_required`` like all builder
     routes.

4. **New block type: Text & Image Split (``split``)**
   - ``split_section.html`` partial (rich text left, image right), schema +
     choices added, migration **0021**. The image is URL-based
     (``image_url``) — a full media-upload pipeline is out of scope; the URL
     is validated by the ``safe_url`` filter at render time.

5. **Fixes found in review**
   - ``page_manager.js`` now indexes the ``json_script`` block payload by
     ``element_id`` (it is an array, not a map) — a latent bug from the
     previous task that broke the inline editor's data lookup.
   - Library previews derive from ``_BLOCK_TEMPLATES`` (single source of
     truth in Python) instead of a hand-written second copy.
   - Missing ``page_id`` on create returns 400 (was an accidental 404).
   - Pending insert/delete state is cleared when modals close.

### Verification

- ``manage.py check`` — clean · migrations consistent (0021 applied)
- Builder tests (backend / block library / render / ordering / custom nav /
  page manager / library drawer) — **90 tests OK** (8 new: create append +
  insert + validation + permissions, delete by id + 404, canvas/insert/
  library markup, split rendering)
- Full suite — **427 tests OK** · ``node --check page_manager.js`` — clean
- Live check: 4 canvas sections + insert handles render, library drawer
  shows 4 template cards, create (insert at index 1) and delete both return
  success.

---

## 56. Complete Dynamic Rendering & Inline Editing for All Page Templates

**Date:** 11 August 2026  
**Branch:** main

### Overview

Completed the frontend/backend integration for the premade page templates:
added the last two section types (Link Hub, Staff Grid), bound every template
field to ``data-edit-field`` for ``contenteditable`` inline editing, added a
64-colour style picker, and made the block-save API safe for complex array
payloads and partial (field/style-only) updates.

### Completed Work

1. **Two new block types (`core/models.py`, migration 0022)**
   - ``links`` (Link Hub) — labelled grid of internal/external links.
   - ``staff`` (Staff Grid) — photo/name/role cards.
   - Schemas documented in ``BLOCK_SCHEMAS``; partials registered in
     ``_BLOCK_PARTIALS`` (``links_grid.html``, ``staff_grid.html``). The
     library drawer now offers **six** template cards.

2. **Field-level edit bindings (all 9 structured partials)**
   - Headings, subtitles, body text, buttons and array items
     (``items.N.field`` dot-paths) all carry ``data-edit-field``; Text Blocks
     render a ``data-edit-html`` whole-body surface.
   - ``page_manager.js`` makes bound elements ``contenteditable`` and saves on
     blur via ``setPath``/``deepCopy`` against ``content_json`` (array-safe).

3. **64-colour style picker (`core/views.py`, `edit_page.html`)**
   - ``COLOR_PALETTE`` (8×8 swatches) server-rendered into the style popover;
     text-colour and background-colour groups save into ``style_json`` and are
     applied live to the section body and on the public page via
     ``_style_attr`` (camelCase → kebab-case CSS properties).

4. **Partial-save safety (`_save_content_block_data`)**
   - Payload keys are now written only when present: a style-only or
     field-only save no longer wipes ``content_html`` / ``content_json`` /
     ``style_json``. Complex array content (feature cards, staff grid items)
     round-trips losslessly.

5. **Tests (`BuilderDynamicRenderEditTest`, 8 new)**
   - links/staff choices + schemas + live rendering; complex-array round-trip;
     partial-save field retention; inline style on the public render; canvas
     edit bindings + 128 swatches + text-block HTML surface. Library drawer
     test updated to six cards.

### Verification

- ``manage.py check`` — clean · migrations consistent (0022 applied)
- Builder tests — **98 OK** · full suite — **435 OK** · ``node --check`` clean
- Live check — 78 edit-field bindings, 128 swatches, style popover, six
  library cards, staff block create + public render verified

---

## 57. Google Drive API Scopes & Offline Token Management

**Date:** 11 August 2026  
**Branch:** main

### Overview

Extended the Google OAuth integration for Google Drive API access: the
allauth scope list now covers openid/profile/email plus Drive (app-data and
read-only) and Sheets, offline access is requested so a refresh token is
stored, and a new allauth-``SocialToken``-based credential helper powers the
Drive status shown on the Account & Google settings tab.

### Completed Work

1. **OAuth scopes (`config/settings.py`)**
   - ``SCOPE`` now requests ``openid``, ``profile``, ``email``,
     ``drive.file``, ``drive.readonly`` (new) and ``spreadsheets``.
   - ``AUTH_PARAMS`` keeps ``access_type: offline`` (refresh token for
     background ops) plus ``prompt: consent`` — the consent prompt is what
     guarantees Google returns a *fresh* refresh token on every
     authorization, including unlink → re-grant flows.

2. **Credential helper (`core/google_service.py`)**
   - ``get_user_google_credentials(user)`` reads the user's active allauth
     ``SocialToken`` (access token in ``.token``, refresh token in
     ``.token_secret``, client id/secret on the linked ``SocialApp``),
     rebuilds ``google.oauth2.credentials.Credentials``, and **proactively
     refreshes** an expired access token before any API request, persisting
     the fresh access token + expiry back to allauth.
   - Refreshed/valid tokens are **mirrored into ``GoogleUserToken``** (which
     previously had no writer) so the existing Drive/Sheets service layer
     (``upload_note_to_user_drive``, gspread club backends) works end-to-end
     after a plain allauth login; ``get_google_credentials`` falls back to
     the allauth path when no legacy row exists.
   - ``user_has_drive_access(user)`` — cheap, network-free check (connected
     + Drive scope in the stored token) used by the settings page.

3. **Drive UI status (`templates/settings.html`, `settings.css`)**
   - The Account & Google tab now shows a dedicated Drive status card:
     ``Connected: Google Drive access granted`` when a valid Drive token
     exists, or ``Not Connected`` with a ``Grant Google Drive Access``
     button (links to the Google OAuth flow).
   - ``settings_view`` passes ``has_drive_access`` in the context.

4. **Tests (`GoogleDriveOAuthTest`, 12 new)**
   - Scope/AUTH_PARAMS config; credential reconstruction + legacy mirror;
     auto-refresh on expiry (persisted to allauth + legacy); not-connected
     and reauth error paths; ``user_has_drive_access`` variants; the Drive
     status card in both connected and not-connected states.

### Verification

- ``manage.py check`` — clean · migrations unchanged
- Google + settings test battery — **80 OK** (12 new) · full suite — **447 OK**
- Live check — Not Connected card renders first; after a SocialToken is
  created the card flips to "Connected: Google Drive access granted", the
  helper returns credentials with the Drive scope, and ``GoogleUserToken``
  is mirrored; all cleaned up after the check.

## 58. Payments Webhooks, Background Queue, Builder XSS Hardening & Security Audit

**Date:** 11 August 2026  
**Branch:** main

### Overview

Five workstreams shipped in one release: the Render/CI deployment fix, a
payments app connecting bKash/Nagad webhooks to the transport + meal models,
a Huey background queue for note analysis, render-time XSS hardening for the
Website Builder, and a production security audit with tests.

### 1. Deployment setup fix (Render + CI)

- **`render.yaml`** — web service build runs collectstatic + migrate cleanly
  (WhiteNoise), gunicorn/daphne deps specified, managed Postgres + Redis wired
  into `DATABASE_URL`/`REDIS_URL`; a new **worker service** runs the Huey
  consumer (`manage.py run_huey`).
- **`.github/workflows/deploy.yml`** — the workflow now runs `python manage.py
  test` before triggering the Render deploy webhook, so broken builds never
  ship.
- **`requirements.txt`** — pinned the channels/daphne implicit deps
  (`asgiref`, `autobahn`, `twisted[tls]`), plus `whitenoise`, `psycopg2-binary`
  and `huey[django-redis]`.
- **`.gitattributes`** — `*.sh text eol=lf` so a Windows CRLF checkout never
  corrupts the `build.sh` shebang on Render's Linux builder.

### 2. Payments app — bKash/Nagad webhooks (auto-activate paid tickets)

- **New `payments/` app.** `PaymentOrder`: provider (bKash/Nagad),
  amount/currency, unique `PINV-XXXXXX` merchant invoice id, status
  (`pending/paid/failed/cancelled`), indexed `provider_transaction_id`,
  raw-callback audit JSON, and a **generic link to the purchased item**
  (TransportBooking or MealTicket) with a one-order-per-item constraint.
- **`payments/services.py`** — `create_payment_order` (idempotent,
  race-safe), `fulfill_payment_order` — the SUCCESS connector: order → paid,
  linked ticket/booking → **PAID**, active `#MEAL-XXXX` / `TR-XXXXXX` code
  generated, real-time notification pushed (deferred via `on_commit`).
- **`payments/views.py`** — CSRF-exempt webhooks `POST
  /payments/webhook/bkash/` (GET callback + JSON/form payloads) and
  `/payments/webhook/nagad/` (sha256 signature verified); order matched by
  invoice then provider ids; **amount verified**; failure-after-success can
  never undo a payment; unknown order → 404, cross-provider/mismatch → 400.
- **`simulate_payment_callback`** management command — end-to-end callback
  testing with no merchant credentials.
- **Core integration** — `MealTicket`/`TransportBooking` tokens are now
  nullable until activation plus `payment_status`/`paid_at`/`payment_order`;
  `claim_meal`/`book_transport` accept an optional `payment_method`+`amount`
  (created PENDING, activated by the webhook). Migration **0023** backfills
  pre-existing rows as paid; the free instant flow is untouched. Invalid
  amounts → 400.
- **Caveats (documented in the webhook docstrings):** bKash callbacks carry
  no signature (trusted + amount-checked until the status API is wired with
  credentials) and the Nagad sha256 "signature" is tamper-evidence, not
  authentication — production should confirm via Nagad's verify API (reserved
  `BKASH_*`/`NAGAD_*` env vars).

### 3. Huey background task queue (async note analysis)

- **`huey[django-redis]>=2.5,<3.0`** added; `HUEY` settings driven by the same
  `REDIS_URL` as the channel layer — `immediate: True` while `DEBUG` or no
  Redis (dev/tests run synchronously), Redis queue in production;
  `huey.contrib.djhuey` registers `manage.py run_huey`.
- **`core/notes_analysis.py`** (extractors moved out of views) + **
  `core/tasks.py`** (`analyze_note_content` db_task — idempotent, failure →
  `failed`) + **`NoteAnalysis`** model (migration **0024**) with admin.
- **`note_summary`/`note_keywords`** now create a row, enqueue, and return
  instantly (`queued` + `analysis_id`); owner-scoped poll endpoint **`GET
  /api/notes/analysis/<uuid>/`**; `notes_engine.html` buttons show spinners
  and poll every 700 ms.
- **`render.yaml`** — `niter-centralized-dash-worker` service (`run_huey`).
- **Channel layer verified:** already reads `REDIS_URL` via `env()` with a
  graceful in-memory fallback — no change needed.

### 4. Website Builder — render-time XSS hardening + `/pages/` routing

- **New `core/block_sanitizer.py`** — the HTML/CSS allow-list sanitizer
  (moved out of `views.py`) is now the single source of truth, applied at
  **save time** (builder API) and **render time** (live page + template tag).
  `sanitize_css` also strips `<style>`/`<script>` opening tokens.
- **`render_block_html`** re-sanitizes every raw `content_html` path, so a
  pre-sanitizer row or admin-edited block can never ship scripts/event
  handlers; new **`sanitize_html` / `sanitize_css` template filters**;
  `custom_css` is re-guarded before its `|safe` injection; `_style_attr`
  relies on Django autoescaping (quotes become `&quot;` — no attribute
  breakout). Structured-block partials (which embed trusted inline JS for the
  stats/testimonial animations) are deliberately **not** sanitized — locked
  in by a regression test.
- **New public route** `GET /pages/<slug>/` (`editable_page_public`) alongside
  the legacy `/page/<slug>/`; published pages are public, drafts 404 for
  everyone except builders.
- No new dependency — reuses the project's existing tested sanitizer instead
  of adding bleach.

### 5. Production security audit

- **Verified (now proven by tests):** `DEBUG` hard-defaults to `False`;
  `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, HSTS
  (1 year + subdomains + preload), `SECURE_PROXY_SSL_HEADER` and
  `X_FRAME_OPTIONS=DENY` all activate only when `DEBUG=False`; `.env.example`
  documents them.
- **Gap fixed — `AUTH_PASSWORD_VALIDATORS` was missing** (Django's default is
  empty). Added the four standard validators (similarity, min-length 8,
  common-password, numeric); they apply to allauth signup, the password-
  change form, and `createsuperuser`.
- **Endpoint audit** (this project uses function views + decorators, not DRF):
  every protected endpoint is guarded — 21 `@login_required`, 10
  `@staff_member_required`, 11 builder-permission-gated
  (`@change_editablepage_required`), 1 `@superuser_required`. The payment
  webhooks are the documented unauthenticated exception (server-to-server,
  signature/amount-checked); `google_unlink` answers an inline **401** rather
  than a redirect so the settings page's `fetch()` works.
- **New `SecurityAuditTest` (7 tests):** bare-environment settings load
  (DEBUG unset → False + all secure flags; the gitignored dev `.env` is
  temporarily set aside), DEBUG=True never forces the secure flags,
  production security headers (HSTS/nosniff/X-Frame-Options), password-
  validator enforcement, an **exhaustive 45-endpoint anonymous-access
  matrix**, and webhook reachability (never a login redirect).

### Verification

- Full suite: **501 tests pass** (447 at the start of this session) ·
  `manage.py check` clean · migrations 0023/0024 + payments 0001/0002
  applied.
- End-to-end verified: bKash SUCCESS → order `paid`, booking `paid` with QR
  generated; Nagad FAILURE → order `failed`, ticket stays `pending` with no
  code; Huey task path in immediate mode; builder pages neutralize legacy XSS
  payloads at render time.

---

## 59. PWA Shell, Bleach Sanitizer Upgrade, Notice Broadcast Task & Versioned Payment Callback

**Date:** 11 August 2026  
**Branch:** main

### Overview

Five follow-ups landed after §58: an installable **PWA shell** (manifest +
service worker + offline caching), the builder HTML sanitizer rebuilt on
**bleach**, notice fan-out moved to a **Huey background task**, a **versioned
generic payment callback** plus a `simulate_payment` command alias, and
horizontal-scroll wrappers for the wide admin tables.

### 1. PWA shell (`manifest.json`, `/sw.js`, offline caching)

- **`GET /manifest.json`** (`pwa_manifest`, `core/urls.py` + `core/views.py`)
  — Web App Manifest with `start_url: /dashboard/`, `scope: /`, standalone
display, brand palette (`#FBF9F5` / `#EADCC9`), and 192/512 icons.
- **`GET /sw.js`** (`service_worker_view`) — serves `static/js/sw.js` from
the origin root with `Service-Worker-Allowed: /` and `Cache-Control:
no-cache` (never stale).
- **`static/js/sw.js`** — versioned cache (`niterhub-v1`): precaches the app
shell + core CSS + icons; network-first for navigations with a cached
fallback (falls back to the cached dashboard); stale-while-revalidate for
static; old caches purged on activate. **Bump `VERSION` when the precache
list changes.**
- **`static/js/pwa-register.js`** — deferred `register('/sw.js')` on `load`;
failures log a warning, never fatal.
- **`templates/partials/pwa_head.html`** — manifest link, `theme-color`,
mobile-web-app / apple-touch meta + `icon-180/192/512` links. Included in
`base.html`, `dashboard/home.html`, `index.html`, `academic/notes.html` and
`transport.html` (each also loads `pwa-register.js`).
- **`scripts/generate_pwa_icons.py`** — stdlib-only (struct + zlib) PNG
renderer for the rounded-square "N" badge in the brand palette; writes
`static/pwa/icon-{180,192,512}.png`.

### 2. Builder sanitizer rebuilt on bleach

- **`core/block_sanitizer.py`** — the hand-rolled `html.parser` allow-list
sink is replaced with **`bleach.clean`** (allow-listed tags/attrs + the same
`SAFE_URL_SCHEMES`), keeping save-time and render-time behaviour identical.
`<script>`/`<style>` blocks are pre-dropped **in full** (content included) so
an injected script never leaks its text onto the page.
- **`requirements.txt`** — `bleach>=6.0,<7.0` added (supersedes §58's note
that no new dependency was introduced).

### 3. Notice broadcast → Huey background task

- **`core/tasks.py`** — new `broadcast_notice(notice_id, bell_category)`
`db_task` fans out the per-user `Notification` rows + live WebSocket pushes
off the request path (returns the created count).
- **`create_notice` (`core/views.py`)** — enqueues the task (Huey queues it
in production when Redis is present; runs synchronously in immediate mode,
where the view uses the task's return value as the exact `notified` count).
Response gains `broadcast: sent|queued|none`.

### 4. Versioned generic payment callback

- **`POST/GET /api/v1/payments/callback/<gateway>/`**
  (`gateway_callback`, `payments/urls.py` + `payments/views.py`) — thin
CSRF-exempt dispatcher over the existing bKash/Nagad handlers; unknown
gateways answer 404, cross-provider callbacks stay rejected (400).
- **`payments/management/commands/simulate_payment.py`** — alias for
`simulate_payment_callback` so dev tooling can use the shorter name.

### 5. Admin table overflow fixes

- `sys_admin.html`, `club_admin.html`, `cafeteria_admin.html`, `clubs.html`
— every admin `<table>` is now wrapped in `.overflow-x-auto` so wide tables
scroll horizontally on small screens instead of overflowing the page.

### Tests

- New `PwaTests` (`core/tests.py`, 4): manifest metadata/icons, service
worker headers + precache contents, dashboard/offline-route PWA wiring.
- New `GatewayCallbackApiTests` (`payments/tests.py`, 4): bKash/Nagad
success through the generic route, unknown gateway 404, cross-provider 400.
- `CreateNoticeApiTest` updated to patch `core.tasks.notify_user` (the
broadcast push now lives in the task module).
- Full suite — **509 tests OK** · `manage.py check` clean · `node --check`
clean on all JS (incl. `sw.js` / `pwa-register.js`) · PNG icons validated.

---

## 60. Global Display Preferences — Theme / Timezone / Density

**Date:** 11 August 2026

### Overview

The Display tab (`/settings/?tab=display`) now actually persists **and applies
globally across the portal**, including the Website Builder and the public
pages it renders. Theme (Light / Dark / System), Timezone and Layout Density
(Comfortable / Compact) are driven by one client-side engine backed by a
per-user account row (`UserNotificationPreference`) + device `localStorage`.

### How it works

1. **Global JS driver — `static/js/display-preferences.js`**
   - Loaded (deferred) on **every** page via `partials/display_prefs.html`
     (included in `<head>` right after `theme.css` in `base.html`, the builder
     consoles, `settings.html`, `editable_page.html` and every standalone
     service page).
   - Exposes `window.DisplayPrefs` (`get` / `set` / `apply`). `set()` applies
     instantly, persists to `localStorage` (`niter.display.prefs`), fires a
     `display-prefs-change` event, and — for signed-in users — syncs the
     account copy via AJAX to `/settings/` (the existing JSON endpoint).
     The `density` key is translated to the backend's `compact_layout` boolean
     on the wire.
   - Theme application: toggles a `dark` class on `<html>`/`<body>` and stamps
     `data-theme="dark|light"`, `data-theme-mode="…"` and
     `data-density="compact|comfortable"`. `system` mode follows
     `prefers-color-scheme` live via `matchMedia`.
   - **No-flash:** the partial's tiny inline script runs synchronously in
     `<head>` (before first paint) and stamps the same attributes from the
     server-rendered `DISPLAY_PREFS` payload merged with `localStorage`.
     Signed-in users get their **account** prefs (follow them across devices);
     anonymous visitors keep their **device** prefs.

2. **Server plumbing**
   - `core/middleware.py` — `UserDisplayPreferencesMiddleware`: one query per
     authenticated request, caches `request.display_prefs`, and activates the
     user's timezone via `django.utils.timezone.activate()`.
   - `core/context_processors.py` — `display_prefs`: exposes `DISPLAY_PREFS`
     (theme/timezone/density + `saveUrl`/`authenticated`) to every template;
     serialised into the no-flash config via `{{ DISPLAY_PREFS|json_script }}`.
   - `config/settings.py` — middleware registered after `AuthenticationMiddleware`;
     context processor registered.

3. **Dark mode styling — `static/css/theme.css`**
   - `html[data-theme='dark']` flips the Tailwind rgb-triplet tokens
     (`--color-base/card/border/main/accent/…`) **and** the standalone-page
     hex tokens (`--bg-main/card/subtle`, `--text-primary/muted`,
     `--border-color`, `--accent-primary/-hover`, `--accent-dark`, semantic
     status soft-colors) — so the app shell, service pages, builder and
     editable pages all darken without touching component CSS.
   - `--accent-dark` is redefined to a light ink in dark mode; a repair block
     keeps the components that use it as a *background* dark (primary buttons,
     toasts, selected seats, toggles, `.btn-emergency`, `.redeem-btn`, etc.).
   - Landing-page glass panels/overlays get targeted dark overrides.

4. **Layout density — `html[data-density='compact']`**
   - Trims chrome padding/gaps across the Tailwind shell (`[data-region]`),
     standalone service pages (`.shell`, `.content-block`, `.topbar`) and the
     builder (`.pb-topbar`, `.pb-blocks`, `.pb-section-body`, `.pb-canvas`,
     `.pb-item`, `.pb-lib-card`) plus the settings page cards/toggles.

5. **Website Builder & public pages**
   - `editable_page.html` (the `/pages/<slug>/` renderer and the visual
     editor's live iframe canvas) includes the partial, so the builder canvas
     and published pages respect the active theme + density immediately.
   - Builder consoles (`builder/dashboard.html`, `builder/editor.html`,
     `builder/edit_page.html`) carry the driver too.

6. **Timezone in the UI**
   - `partials/topbar.html` `formatTime()` now applies the saved timezone
     (`Intl` `timeZone`) to *aware* ISO timestamps in the notification bell;
     naive timestamps are left untouched.
   - **Known limitation:** the project runs with `USE_TZ=False` (naive
     server-local datetimes), so `timezone.activate()` only affects aware
     datetime handling and `|localtime`. Fully honouring the timezone for
     server-rendered `|date` filters requires enabling `USE_TZ=True` (a
     follow-up; the preference itself persists and applies client-side).

7. **PWA** — `sw.js` bumped to `v2`, precaches `display-preferences.js`.

### Files

- **New:** `core/middleware.py`, `templates/partials/display_prefs.html`,
  `static/js/display-preferences.js`
- **Modified:** `config/settings.py`, `core/context_processors.py`,
  `static/css/theme.css`, `templates/settings.html`, `templates/base.html`,
  `templates/partials/topbar.html`, `static/js/sw.js`, `core/tests.py`, and
  the `display_prefs` partial include added to ~23 standalone templates
  (public pages, admin consoles, builder, auth).

### Tests

- New `DisplayPreferencesIntegrationTest` (7) — context processor payloads
  (authenticated / anonymous / rowless user), partial + driver presence on
  settings, public pages and all three builder consoles, and the JSON save
  round-trip.
- New `UserTimezoneMiddlewareTest` (2) — timezone activated during the
  request for a UTC-pref user; anonymous requests untouched.
- Full suite — **517 tests OK** · `manage.py check` clean.

---

## 61. Dark-Mode Hero Glow Fix — No More White Corner Blobs

> **⚠ Superseded (§61.1):** The amber-tint approach below was replaced the
> next day by **removing the corner glows entirely** — every standalone page
> now uses a flat `background: var(--bg-main)` in both themes (see §62 note),
> so the `radial-gradient` overrides documented here no longer exist.

**Date:** 11 August 2026

### Overview

In dark mode the standalone service pages (dashboard, meals, transport,
medical, notes, notices, profile, clubs, departments, settings, research AI,
checkout, auth, builder, admin consoles, …) showed bright **white/cream
blobs** at the top of the page. Root cause: every standalone page paints a
pair of warm-cream `radial-gradient` layers on `<body>` as a soft hero glow
(e.g. `rgba(232, 226, 216, 0.55)` top-right and `rgba(240, 235, 225, 0.6)`
top-left). Those hardcoded cream values stay bright when the page background
(`--bg-main`) flips to `#18181b` in dark mode.

### The fix — `static/css/theme.css`

Added a **centralized dark-mode override** (in the existing dark-theme
repair section) that swaps the cream glows for faint amber tints while
preserving their corner position and softness — the glows are kept, but they
no longer glare:

```css
html[data-theme='dark'] body.dashboard,
html[data-theme='dark'] body.landing,
html[data-theme='dark'] body.auth,
… /* every standalone page body class */
html[data-theme='dark'] .canvas-wrap {
    background:
        radial-gradient(1000px 520px at 85% -10%, rgba(217, 119, 6, 0.06), transparent 60%),
        radial-gradient(800px 420px at 5% 12%, rgba(180, 83, 9, 0.07), transparent 55%),
        var(--bg-main);
}

html[data-theme='dark'] .cta-block {
    background:
        radial-gradient(520px 300px at 15% 0%, rgba(255, 255, 255, 0.08), transparent 60%),
        linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-primary-hover) 100%);
}
```

- Covered body classes: `body.dashboard`, `body.landing`, `body.auth`,
  `body.profile`, `body.medical`, `body.notes`, `body.notices`, `body.meals`,
  `body.transport`, `body.clubs`, `body.dept-detail`, `body.settings`,
  `body.research`, `body.checkout`, `body.builder`, `body.editable-page`,
  `body.sys-admin`, `body.cafeteria-admin`, `body.club-admin`, plus the
  builder editor canvas (`.canvas-wrap`) and the editable-page CTA highlight
  (`.cta-block`).
- Chose one central place (`theme.css`, loaded first on **every** page) over
  editing 17 page stylesheets — matches the existing dark-mode repair
  convention; light mode is untouched.

### Tests

- Full suite — **517 tests OK** · `manage.py check` clean · CSS braces
  balanced.

---

## 62. WCAG AA Contrast Pass — Light Elements in Dark Mode

**Date:** 12 August 2026

### Overview

Fixed text legibility for **light-colored elements that stayed bright in dark
mode** — the classic “light ink on light tint” failure. Audited alert boxes,
warning banners, primary/secondary action buttons, status badges and auth
elements in **both** themes against WCAG AA (≥ 4.5:1 for small text).

### Root cause

`theme.css`’s `html[data-theme='dark']` block already redefined the
`--success` and `--danger` families for the standalone page tokens, but the
**`--warning` and `--info` families were missing**. Every component built on
`var(--warning-soft)` (meal subscription banner, inline meal alerts, checkout
security note, amber badges/chips) therefore kept its **light-cream `#fef3c7`
background with light text** on top in dark mode — unreadable. The Tailwind
“-100 bg / -700 text” badge pattern (host medical + tickets) also sits just
below AA (≈ 4.3:1) on small text.

### Fixes

1. **Dark tokens added (`static/css/theme.css`)** — the missing semantic
   families for standalone pages:
   - `--warning: #fbbf24` · `--warning-soft: #422006` · `--warning-border: #78350f`
   - `--info: #93c5fd` · `--info-soft: #172554` · `--info-border: #1e40af`
   - This single change flips **every** warning/info component to a dark
     amber/blue surface with high-contrast text in dark mode (meal-sub,
     meal-alert, security-note, admin/dashboard/clubs/departments/medical
     badges, ring/chip statuses, stat values).

2. **Auth dark overrides (`theme.css`)** — `.auth-alert` (error box) and
   `.auth-back-link` get dark-adapted surfaces (`rgba(248,113,113,…)` /
   `#27272a`) with `#fca5a5` / `#d4d4d8` text instead of light-on-light.

3. **Notes Engine light buttons (`templates/notes/notes_engine.html`)** —
   Extract Keywords / Save Note / Export as PDF changed from
   `bg-card hover:bg-white text-main` (hover = white bg + light text in dark
   mode) to the explicitly high-contrast light button pattern
   `bg-white hover:bg-gray-200 text-gray-900 font-semibold`.

4. **Monthly Meal Subscription banner (`static/css/meals.css`)** —
   high-contrast amber ink on the light tint: title `#78350f` (amber-900),
   subtitle `#92400e` (amber-800); dark mode uses `#fde68a`/`#fcd34d` on the
   new amber-950 surface. Active-state subtitle now uses the success green.

5. **Light-mode `--warning` token** bumped `#b45309` (amber-700 → 4.3:1) to
   `#92400e` (amber-800 → 6.3:1) in all **9** standalone stylesheets
   (meals, checkout, admin, dashboard, transport, departments, clubs,
   medical, research_ai) so amber text passes AA on `amber-100` tints.

6. **Status badge text shades** — hardcoded Tailwind badges in
   `host/medical/dashboard.html`, `host/medical/admin_dashboard.html` and
   `ticketing/tickets.html` bumped from `-700` to `-800` (amber / emerald /
   red / orange / green / gray) so they clear 4.5:1 in light mode and stay
   legible on light chips in dark mode.

### Files changed

- `static/css/theme.css` (dark warning/info tokens + auth overrides)
- `static/css/meals.css` (banner ink + `--warning` bump)
- `static/css/checkout.css`, `admin.css`, `dashboard.css`, `transport.css`,
  `departments.css`, `clubs.css`, `medical.css`, `research_ai.css`
  (`--warning` bump)
- `templates/notes/notes_engine.html` (light buttons)
- `templates/host/medical/dashboard.html`, `templates/host/medical/admin_dashboard.html`,
  `templates/ticketing/tickets.html` (badge text shades)

### Related

- §61 documents the hero glow treatment; its amber-tint approach was later
  replaced by a **flat clean background** (corner glow divs/gradients removed
  entirely, `background: var(--bg-main)`) — see commit “Remove decorative
  glow blobs: flat clean page backgrounds”.

### Tests

- Full suite — **517 tests OK** (run via `./venv/bin/python manage.py test`).

---

## 63. Dual-Database Architecture & Dedicated Admin Dashboards

Supabase PostgreSQL wiring, a Clubs Google Sheets data layer, and persisted
medical-doctor availability — the “database” layer behind the existing admin
consoles.

### Supabase PostgreSQL (main application DB)

- `config/settings.py` → `_build_databases()`:
  - Reads **`SUPABASE_DB_URL`** first, falling back to the generic
    **`DATABASE_URL`** (Render managed Postgres / Blueprint keeps working).
  - Appends **`sslmode=require`** automatically to `postgres://…` URLs that do
    not already carry an `sslmode` (Supabase requires TLS); explicit query
    params are left untouched.
  - No URL set → local SQLite for dev/tests (test runner stays on SQLite).
  - Parsing via **`dj-database-url`** (`dj_database_url.parse(url, conn_max_age=600)`).
- `requirements.txt`: added `dj-database-url>=2.0`.
- `build.sh` + `render.yaml`: `build.sh` runs `migrate --noinput` followed by
  `seed_demo_users` (idempotent — §76) against whichever database is configured
  (`SUPABASE_DB_URL` first, else `DATABASE_URL`); the render.yaml
  `releaseCommand` still migrates idempotently before the new release serves.
  Set `SUPABASE_DB_URL` to use Supabase.
- `.env.example`: documented `SUPABASE_DB_URL` (and `DATABASE_URL`) with the
  `postgresql://…` scheme hint.
- The **Clubs module** is the second data source: a user-connected Google
  Sheet (see below) — not a second Django DB.

### Clubs module — Google Sheets database (settings integration)

- **`core/club_sheets.py`** — high-level `gspread` data layer built on the
  existing `core/google_service.py` OAuth plumbing:
  - Reference normalization: full `docs.google.com/spreadsheets/d/…` URL *or*
    bare Sheet ID (`normalize_sheet_ref`).
  - Reads: `read_rows`, `get_members` (Members tab), `get_event_registrations`
    (Registrations), `get_club_notices` (Notices). Missing tab → first
    worksheet, so single-tab sheets keep working.
  - Writes: `append_rows`, `append_member`, `append_event_registration`,
    `append_club_notice`.
  - All Google/transport failures surface as `GoogleServiceError` (with
    `GoogleAccountNotConnected` / `GoogleReauthRequired` subtypes) so views
    answer 401 (re-connect Google) or 500 correctly.
- **Club Management auto-connect**: `club_admin_view` falls back to the saved
  `ClubSheetsConfig.sheet_ref` when no `?sheet_url=` param is given, and the
  page prefills the input from it. **Note (§71):** the sheets reference was
  originally saved from a Settings tab (`/settings/?tab=google_sheets`); that
  tab is now removed and the spreadsheet is managed from the Club Management
  dashboard only.

### Dedicated admin dashboards

**Cafeteria Meal Admin — `/cafeteria/admin/`** (staff-only):
- Live daily meal ratios (claimed/capacity per meal against
  `DAILY_MEAL_CAPACITY`), subscription counts, token redemption counters
  (issued/redeemed today, active total).
- Active (unredeemed) pass list.
- **Batch redemption** — `POST /api/cafeteria/batch-redeem/` (`tokens` list or
  `all_today=true`); returns per-token results; UI button redeems today's
  unredeemed passes in one action.

**Medical Center Admin — `/medical/admin/`** (staff-only):
- New persisted models: `Doctor` (name, specialty, working days, hours,
  active) and `DoctorSchedule` (doctor × date, `is_available`,
  `max_appointments`, unique_together). Seed migration `0026_seed_doctors`
  creates the four default doctors so the dashboard works immediately.
- Dashboard now renders doctors from the DB with today's schedule, booked
  counts, and **availability toggles + daily slot-cap inputs**.
- `POST /api/medical/doctor-availability/` upserts a `DoctorSchedule` row
  (staff-only).
- **Booking enforcement**: `book_appointment` reads the doctor's schedule for
  the requested date — blocks unavailable doctors (409) and enforces the
  daily `max_appointments` cap (409).

### Tests

- New test classes in `core/tests.py` (all Google calls mocked, no network):
  - `SupabaseDatabaseConfigTest` — sslmode=require wiring, precedence,
    explicit-sslmode passthrough, SQLite fallback.
  - `ClubSheetsModuleTest` — reference normalization, tab-targeted reads,
    row appends, error translation with `gspread` mocked.
  - `SettingsGoogleSheetsTabTest` — sheets tab save/validation, club admin
    prefill.
  - `BatchRedemptionApiTest` — staff guard, all-today + explicit tokens,
    already-redeemed/not-found handling.
  - `DoctorAvailabilityApiTest` — upsert, toggle, validation, and booking
    block/cap enforcement.
- Full suite — **546 tests OK** (run via `./venv/bin/python manage.py test`).

## 64. Google Drive & Sheets Integration — OAuth Flow, Encrypted Tokens, Drive Notes Upload

**Goal:** Let users connect Google Drive + Sheets via a proper OAuth2 Flow and
store credentials **encrypted at rest**; clubs sync spreadsheets through the
Sheets v4 API and academic notes/PDFs upload into the user's own Drive folder.

### Env vars (`.env.example`)

```
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REDIRECT_URI=https://yourdomain/drive/callback/
# Optional: explicit Fernet key for token encryption (defaults to a stable
# SHA-256 derivation of SECRET_KEY, so existing deployments need no new var).
GOOGLE_TOKEN_ENCRYPTION_KEY=
```

Settings read them via `os.environ` (django-environ) in `config/settings.py`.
Scopes configured: `drive.file` + `spreadsheets` (also mirrored in
`SOCIALACCOUNT_PROVIDERS` so the legacy allauth path keeps working).

### OAuth2 Flow (`/drive/connect/` + `/drive/callback/`)

- `core/views.py::drive_connect` — builds `google_auth_oauthlib.flow.Flow` from
  env creds, stores a CSRF `state` in the session, redirects to Google.
- `drive_callback` — `@login_required`; validates `state` (session pop) and
  `error` params, exchanges the code, and persists **encrypted** tokens on
  `GoogleUserToken` (`core/crypto.py` Fernet helpers). Also mirrors into the
  allauth `SocialToken` row (best effort — no SocialApp row required).
- Both views log failures via `logger.exception` so prod misconfigs are visible.

### Token encryption (`core/crypto.py`)

- `encrypt_secret` / `decrypt_secret` wrap `cryptography.fernet`; key comes from
  `GOOGLE_TOKEN_ENCRYPTION_KEY` or a stable `SECRET_KEY` derivation.
- `decrypt_secret` **falls back to the raw value** for non-Fernet payloads so
  legacy plaintext rows stay readable while new writes are always encrypted.
- The service layer (`core/google_service.py`) decrypts on read
  (`get_user_google_credentials` / refresh path).

### Google Sheets v4 (`core/club_sheets.py`)

- Rewritten internals from gspread → `googleapiclient.discovery.build('sheets',
  'v4')` using the authenticated user's token (kept the same public API:
  `read_rows`, `append_row`, `read_members/registrations/notices`,
  `append_member/registration/notice`).
- `normalize_sheet_ref` accepts a sheet **ID or full docs URL**.
- `verify_and_setup_sheet(user, ref)` — **Verify & Connect Sheet**: opens the
  spreadsheet and creates default tabs (Members / Registrations / Notices) with
  column headers when missing; returns title + created tabs for the UI.
- Error contract: `GoogleServiceError` subtypes incl. `GoogleAccountNotConnected`
  and `GoogleReauthRequired` (expired refresh → 401 `auth_required`).

### Google Drive v3 (`academic_notes/drive_service.py`)

- `upload_file_to_drive` — creates/reuses the **"NITER Centralized Dash Notes"**
  folder and uploads notes/PDFs (`drive.file` scope), returning `webViewLink` +
  `webContentLink`.
- `get_drive_storage_info` — account email + storage quota (limit/usage/remaining).
- `core/views.py::upload_note_view` now saves the Drive links onto
  `UserNote.drive_view_link` / `drive_content_link` and
  `CourseMaterial.drive_view_link` / `drive_content_link` (new fields, migration
  0027).

### Settings tabs (`/settings/`)

- **Notifications / Account & Google / Display** — the three user-preference
  tabs. **Note (§71):** the former **Google Drive** (`?tab=google_drive`) and
  **Club Google Sheets** (`?tab=google_sheets`) tabs were removed in a later
  restructure — Google Drive connect/callback still runs from `/drive/*` and
  club sheets management now lives exclusively in the Club Management
  dashboard.

### Tests (all offline, Google APIs mocked)

- `GoogleCryptoTest` — Fernet round-trip + plaintext fallback.
- `DriveOAuthFlowTest` — connect redirect + session state, callback state
  mismatch / denied / success (encrypted storage) / exchange failure, and
  login guards on both endpoints (note: test-client sessions need explicit
  `.save()`).
- `VerifyClubSheetApiTest` — staff/auth guards, missing ref, success saves
  config, auth-required 401, service error 500 (mocks target
  `core.club_sheets.verify_and_setup_sheet` — lazy import inside the view).
- `GoogleDriveSettingsTabTest` — tab renders, quota card when connected
  (`filesizeformat` uses `\xa0` separators), graceful failure.
- `DriveServiceModuleTest` — folder lookup/create + upload link extraction.
- Updated `GoogleServiceTest` / `ClubSheetsModuleTest` for the sheets-v4 mocks
  and encrypted-token assertions.
- Full suite — **572 tests OK** (run via `./venv/bin/python manage.py test`).

---

## 65. Research AI — OpenRouter LLM Integration & Persisted Threads

**Date:** 12 August 2026  
**Branch:** main

### Overview

Connected the Academic Research & Thesis Assistant (`/research-ai/`) to the
**OpenRouter** chat-completions API. The chat console, paper/abstract file
parser, citation selector, and saved-thread list now all execute through the
backend endpoint `POST /research-ai/api/query/`, which persists real
conversation threads and answers via OpenRouter — with graceful offline fallback
when `OPENROUTER_API_KEY` is not configured.

### 1. Environment & Configuration

- `OPENROUTER_API_KEY = env('OPENROUTER_API_KEY', default='')` and
  `OPENROUTER_DEFAULT_MODEL = env('OPENROUTER_DEFAULT_MODEL', default='nvidia/nemotron-3.5-lightning:free')`
  added to `config/settings.py`; both documented in `.env.example`. (The
  zero-cost free-model default, `OPENROUTER_FALLBACK_MODEL`, base URL and
  `OPENROUTER_ENABLED` landed in §66; the default slug moved to Nemotron 3.5
  Lightning in §67; `OPENROUTER_VISION_MODEL` landed in §73.)
- `OPENROUTER_VISION_MODEL = env('OPENROUTER_VISION_MODEL', default='meta-llama/llama-3.2-11b-vision-instruct:free')`
  — vision-capable free model for the dashboard routine extractor's image
  uploads (PNG/JPG), added to `config/settings.py` and `.env.example`.
- Base URL constant: `https://openrouter.ai/api/v1/chat/completions` (in
  `services/openrouter.py`).

### 2. Backend Service & API Routes

- **`services/openrouter.py`** (new package) — `requests.post` to OpenRouter
  with `Authorization: Bearer <key>`, `HTTP-Referer: https://<request host>`
  (fallback `https://niter.edu.bd`), and `X-Title: NITER Centralized Dash`;
  30s timeout cap. `build_system_prompt(style, document_text)` injects the
  selected citation style (IEEE / APA 7 / Harvard / Chicago) and the extracted
  reference text. Typed error hierarchy
  (`OpenRouterNotConfigured` / `OpenRouterAuthError` / `OpenRouterRateLimitError` /
  `OpenRouterTimeoutError` / `OpenRouterError`) is translated by the view into
  friendly JSON payloads with matching HTTP statuses (401/403→502, 429→429,
  timeout→504, transport→502).
- **`services/parser.py`** (new) — lazily-imported `pypdf` (`.pdf`) and
  `python-docx` (`.docx`) extraction; returns `None` gracefully when the
  libraries or the file are unparseable, so a bad upload never breaks a query.
- **`research_query` view** (`/research-ai/api/query/`) — reads `message`,
  `thread_id`, `citation_style`, and optional `file`; creates/reuses the
  owner-scoped thread, persists the user turn before the provider call (so a
  failure is retryable), returns
  `{status, response, thread_id, engine, model, citation_style, message}`.
  Missing key → `engine: 'offline'` deterministic fallback (the old keyword
  engine + style-aware references), so the page works with zero config.
- **Thread APIs** — `GET /research-ai/api/threads/` (list) and
  `GET|DELETE /research-ai/api/threads/<id>/` (history / delete, owner-scoped
  404). Legacy `POST /api/research/query/` is kept as an alias.
- **Models** — `ResearchThread` (user, title auto-derived from the first
  message, citation_style, timestamps) + `ResearchMessage` (role user/assistant,
  content); migration `0028`, registered in `core/admin.py` with an inline
  message list.

### 3. Frontend Wiring (`templates/research_ai.html` + `static/css/research_ai.css`)

- Send button / Enter submits via `fetch('/research-ai/api/query/')` using
  **FormData** (supports the attached file); user and assistant bubbles render
  dynamically; the returned `thread_id` becomes the active thread.
- **Upload dropzone / attach clip** — the selected PDF/DOCX is held as the
  pending reference, shown in an attachment status chip under the input, and
  sent with the next query; the extracted text is used server-side.
- **Citation selector** — the dropdown value is posted in the payload each
  turn; changing it mid-thread updates the thread's stored style.
- **Recent Research Threads** — loaded live from `/research-ai/api/threads/`;
  clicking one loads its full history via the detail endpoint and sets the
  active highlight; each thread has a delete button; "New Thread" resets the
  console. Canned JS responses remain only as a last-resort offline fallback.

### Testing

- OpenRouter HTTP calls mocked with `unittest.mock.patch` (offline suite):
  success path (headers / referer / model / timeout / system-prompt style),
  429→429, timeout→504, 401→502, transport→502.
- Missing-key test: endpoint returns a well-formed success JSON from the
  offline engine (graceful degradation, no crash).
- File-parser tests: in-memory DOCX (python-docx) and a hand-built minimal PDF
  extract the expected text; unsupported formats return `None`; an uploaded
  DOCX's text is asserted to appear in the OpenRouter system prompt.
- Thread tests: create/persist, thread_id reuse, 404 for unknown/foreign
  threads, style update, list/detail/delete, owner scoping.
- `python manage.py check` ✔; full suite **589 tests OK**
  (`./venv/bin/python manage.py test`). End-to-end verified in Chrome:
  login → research page → send (offline engine) → sidebar thread appears →
  resume history → New Thread reset — zero console errors.

### Files Added / Modified

- `services/` (new: `__init__.py`, `openrouter.py`, `parser.py`)
- `config/settings.py`, `.env.example`, `requirements.txt` (pypdf, python-docx)
- `core/models.py` (`ResearchThread`, `ResearchMessage`) + `0028_*` migration
- `core/views.py` (rewritten `research_query` + `research_threads` +
  `research_thread_detail`), `core/urls.py`, `core/admin.py`
- `templates/research_ai.html`, `static/css/research_ai.css`, `core/tests.py`

---

## 66. OpenRouter Zero-Cost Models, Fallback Retry, Model Selector & Contrast Fix

**Date:** 12 August 2026  
**Branch:** main

### Overview

Hardened the Research AI OpenRouter integration around **zero-cost models** and
polished the surrounding UI: switched the default to NVIDIA Nemotron 3 Ultra
550B (free), added automatic 429/503 failover to the `openrouter/free`
auto-router, renamed the extractor to `services/parser.py`, added a frontend
model selector, and fixed the last low-contrast action buttons.

### 1. Environment & Configuration

- `settings.py`: `OPENROUTER_DEFAULT_MODEL` now defaults to
  `nvidia/nemotron-3.5-lightning:free` (§67); new constants
  `OPENROUTER_FALLBACK_MODEL = 'openrouter/free'`,
  `OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1/chat/completions'` and
  `OPENROUTER_ENABLED = bool(OPENROUTER_API_KEY)`. `.env.example` documents all
  of them.
- `render.yaml`: web-service `envVars` gains `OPENROUTER_API_KEY`
  (`sync: false` — set once in the Render dashboard, never overwritten by
  Blueprint sync) and `OPENROUTER_DEFAULT_MODEL` with the Nemotron free slug.

### 2. Service Layer & Backend

- **`services/openrouter.py`** — new `call_openrouter(messages, model=None,
  system_prompt=None, timeout=30, referer=None)` entry point. It prepends the
  system prompt, POSTs to `OPENROUTER_BASE_URL`, and on HTTP **429/503** retries
  **once** with `OPENROUTER_FALLBACK_MODEL`, returning
  `(assistant_text, model_used)` so the API can report which model answered.
  New `OpenRouterServiceUnavailableError` (503) typed error; the pre-§66
  `chat_completion` alias was removed (no remaining callers). Added
  `get_fallback_model()` and `is_enabled()` helpers.
- **`services/parser.py`** — extraction module renamed from `document_text.py`
  (same `pypdf`/`python-docx` lazy-import behavior); all imports updated.
- **`research_query` view** — reads an optional `model` field, validated against
  the allow-list `{default, fallback}` (anything else silently uses the default
  so crafted requests can't select paid models); the response reports the model
  that actually answered. 503 → HTTP 503 in the error-status mapping.

### 3. Frontend

- **`templates/research_ai.html`** — new "AI Model" selector card in the
  sidebar offering `nvidia/nemotron-3-ultra-550b-a55b:free` (default) and
  `openrouter/free`; the selected value is posted as `model` with every
  FormData query. **Note (§67):** the frontend selector was intentionally left
  unchanged by the backend-only slug update — the view's model allow-list
  rejects the stale option and silently uses the configured default, so the
  selector still functions correctly until a UI pass updates its option value.
- **Contrast fix (`templates/notes/notes_engine.html`)** — the three light
  action buttons (Extract Keywords, Save Note, Export as PDF) now use the
  explicit high-contrast pattern `bg-white hover:bg-[#EADCC9] text-[#2B2927]`
  (dark ink on light surface, accent hover) instead of `text-gray-900`;
  Generate AI Summary kept its dark `bg-main text-white` treatment (already
  high contrast) at the time. **Note (§68):** a later contrast pass moved the
  AI Summary button to theme-agnostic `bg-white text-[#1E1E1E]` because
  `bg-main` flips light in dark mode (white-on-white) — see §68.

### Testing

- Mocked OpenRouter HTTP tests (`unittest.mock.patch`, offline):
  - Model param passthrough (`model=openrouter/free` reaches the payload).
  - Unknown/invalid model silently falls back to the default.
  - 429 → one automatic retry with `openrouter/free`, success + model reported.
  - 503 → one automatic retry with the fallback.
  - Both attempts rate-limited → friendly HTTP 429 error payload.
  - 503 exhausted → HTTP 503 error payload.
- Service-level `OpenRouterServiceTest` — `call_openrouter` fallback retry +
  system-prompt prepending.
- `python manage.py check` ✔; full suite **599 tests OK**
  (`./venv/bin/python manage.py test`).

### Files Modified

- `config/settings.py`, `.env.example`, `render.yaml`
- `services/openrouter.py` (fallback + `call_openrouter`), `services/parser.py`
  (renamed from `document_text.py`), `services/__init__.py`
- `core/views.py`, `core/tests.py`
- `templates/research_ai.html`, `templates/notes/notes_engine.html`
- `docs/HANDOVER.md`

---

## 67. OpenRouter Default Model — Nemotron 3.5 Lightning (Backend & Env Only)

**Date:** 12 August 2026  
**Branch:** main

### Overview

Switched the backend default OpenRouter model slug from
`nvidia/nemotron-3-ultra-550b-a55b:free` to **`nvidia/nemotron-3.5-lightning:free`**
across environment files, Django settings, the Render blueprint, unit-test
mocks, and this documentation. Per the task scope, **no frontend templates or
UI files were modified** — the model selector in `templates/research_ai.html`
still lists the previous slug, but the query view's allow-list rejects that
stale value and silently uses the configured default, so the page keeps
working until a UI pass updates the option.

### Changes

- **`.env.example`** — `OPENROUTER_DEFAULT_MODEL=nvidia/nemotron-3.5-lightning:free`
  (+ updated zero-cost-model comment).
- **`.env`** (local dev, gitignored) — `OPENROUTER_DEFAULT_MODEL` set to the
  new slug.
- **`config/settings.py`** — `OPENROUTER_DEFAULT_MODEL` default is now
  `'nvidia/nemotron-3.5-lightning:free'` (read via django-environ `env()`,
  equivalent to `os.environ.get(..., default)`).
- **`services/openrouter.py`** — `get_default_model()` fallback literal updated
  to the new slug.
- **`render.yaml`** — web-service env var `OPENROUTER_DEFAULT_MODEL` value set
  to `nvidia/nemotron-3.5-lightning:free`.
- **`core/tests.py`** — every mocked OpenRouter payload now asserts the new
  default slug (11 occurrences across the query/fallback/model tests).

### Testing

- `python manage.py check` ✔
- Research AI suite (mocked OpenRouter, offline):
  `python manage.py test core.tests.ResearchQueryApiTest core.tests.OpenRouterServiceTest core.tests.ResearchDocumentTextTest core.tests.ResearchAIPageTest` ✔
- Full suite: `python manage.py test` ✔ (599 tests OK).

### Files Modified

- `.env.example`, `.env` (gitignored), `config/settings.py`,
  `services/openrouter.py`, `render.yaml`, `core/tests.py`, `docs/HANDOVER.md`

### Remaining (deliberately out of scope)

- `templates/research_ai.html` model-selector option value still shows
  `nvidia/nemotron-3-ultra-550b-a55b:free` — update it in a future UI pass.

---

## 68. Button Contrast Fix — White Text on Light Backgrounds (Dark Mode)

**Date:** 12 August 2026  
**Branch:** main

### Overview

Fixed low-contrast buttons where white text rendered over white or light
surfaces. Root cause: several action buttons relied on theme tokens that
**flip in dark mode** — `--color-main` and `--text-primary` become light
values (`#f4f4f5`), while the button backgrounds stayed white/light, so dark
mode produced white-on-white. The fixes use **theme-agnostic colors** (fixed
hex ink) that stay readable in both themes.

### Changes

- **`templates/notes/notes_engine.html`** — "Generate AI Summary" button:
  `bg-main hover:bg-main/90 text-white` → `bg-white text-[#1E1E1E]
  hover:bg-gray-200 font-semibold` (layout classes `flex items-center gap-2` /
  `text-sm` / `shadow-sm` kept). Now matches the sibling buttons' dark-ink-on-
  white treatment in both themes.
- **`static/css/main.css`** — "Medical Services" hero button
  (`.hero-btn-secondary`): text colour is now hardcoded `#1E1E1E` (was
  `var(--text-primary)`, which flips light in dark mode) on the white
  background; hover now uses `#f3f4f6` (gray-100, was `var(--bg-subtle)`).
- **`templates/ticketing/tickets.html`** — "Claim Meal Ticket" submit button:
  `bg-main hover:bg-main/90 text-white` → `bg-[#2B2927] hover:bg-[#3A3836]
  text-white` — same dark-ink treatment, hardcoded so it stays dark in both
  themes.
- **`static/css/theme.css`** — added a dark-mode `.navbar` rule
  (`background: rgba(39, 39, 42, 0.82); border-color: #3f3f46`) so the
  translucent-white landing navbar pill doesn't carry light nav text on a
  light surface in dark mode (the scrolled-state rule already existed).

### Audit results (no other offenders)

- The remaining `bg-white` action buttons (Extract Keywords, Save Note, Export
  as PDF) already used explicit dark text (`text-[#2B2927]`).
- `bg-emerald-600` / `bg-red-600` admin buttons keep white text on dark fixed
  colours — fine in both themes.
- No `bg-white/10`, `bg-white/20`, or `text-white/50` instances found in any
  template. `grep 'bg-main.*text-white' templates/` and
  `grep 'bg-white.*text-white' templates/` now return nothing.
- The `#notes-toast` element uses `text-white` but always ends with
  `bg-success` / `bg-danger` (neither flips in dark mode) — fine.

### Testing

- Grep verification for residual `bg-main.*text-white` / `bg-white.*text-white`
  in `templates/` ✔ (none)
- Confirmed `templates/ticketing/tickets.html` extends `base.html` (Tailwind
  CDN) so the arbitrary hex utilities (`bg-[#2B2927]`) resolve.
- Code review ✔ — no regressions; cascade for the new navbar rule verified
  (scrolled-dark state is covered by the pre-existing higher-specificity rule).

### Files Modified

- `templates/notes/notes_engine.html`, `static/css/main.css`,
  `templates/ticketing/tickets.html`, `static/css/theme.css`,
  `docs/HANDOVER.md`

---

## 69. Demo Accounts — `seed_demo_users` Management Command

**Date:** 12 August 2026  
**Branch:** main

### Overview

`db.sqlite3` is gitignored, so a fresh clone starts with **no users** and the
documented demo accounts (`admin` / `admin123`, `student` / `student123`) had
to be recreated by hand. Added an idempotent management command so any
environment can bring back the demo accounts with one line:

```bash
venv/bin/python manage.py seed_demo_users
```

### Changes

- **`core/management/commands/seed_demo_users.py`** (new) — creates, when
  missing:
  - `admin` / `admin123` — superuser + staff (every admin dashboard, Django
    `/admin/`, and the Website Builder).
  - `student` / `student123` — regular student (all student-facing pages).
  - Options: `--password 'S3cret!x'` overrides the admin/staff password
    (student keeps its documented `student123`); `--extra-staff N` also
    creates `staff1..staffN` staff accounts.
  - **Idempotent** — existing users are never touched or password-reset, so
    re-running after a password change keeps the new password.
- **`core/tests.py`** — new `SeedDemoUsersCommandTest` (4 tests): creates the
  demo users with correct roles, idempotency + keeps a changed password,
  `--extra-staff` creation, and `--password` override (student unaffected).
- **`README.md`** — new "Demo Accounts" section with the credential table and
  the seed command + options.
- **`docs/HANDOVER.md`** — replaced the stale `.freebuff/run.md` references
  (that file does not exist) with the real command in §20 and §32 notes.

### Access mapping (unchanged, for reference)

| Dashboard | URL | Requires | Login |
| :--- | :--- | :--- | :--- |
| Student pages | `/dashboard/`, `/tickets/`, `/meals/`, `/transport/`, `/medical/`, `/notes/`, `/academic-notes/`, `/research-ai/` | any login | `student` / `student123` |
| System Admin | `/admin-dashboard/` | staff | `admin` / `admin123` |
| Medical Admin | `/medical/admin/` | staff | `admin` / `admin123` |
| Medical Host | `/host/medical/` | staff | `admin` / `admin123` |
| Cafeteria Admin | `/cafeteria/admin/` | staff | `admin` / `admin123` |
| Club Management | `/clubs/manage/` | staff | `admin` / `admin123` |
| Django Admin | `/admin/` | superuser | `admin` / `admin123` |
| Website Builder | `/builder/` | superuser / `change_editablepage` | `admin` / `admin123` |

### Testing

- Fresh empty-DB run: `migrate` → `seed_demo_users` creates both users;
  `admin` authenticates as staff+superuser, `student` as regular ✔
- Idempotency: second run reports `exists (skipped)` for every user ✔
- `python manage.py check` ✔; `SeedDemoUsersCommandTest` 4/4 ✔; full core
  suite **559 tests OK** ✔

### Files Modified

- `core/management/commands/seed_demo_users.py` (new),
  `core/management/__init__.py` (new), `core/management/commands/__init__.py`
  (new), `core/tests.py`, `README.md`, `docs/HANDOVER.md`

---

## 70. Skip Google OAuth Provider-Confirmation Screen

**Date:** 12 August 2026  
**Branch:** main

### Overview

By default allauth shows an intermediate **provider-confirmation page** when a
social login is initiated via GET (e.g. ``{% provider_login_url 'google' %}``
from the login page or the Google-reconnect modals). Enabled
``SOCIALACCOUNT_LOGIN_ON_GET`` so clicking the Google button proceeds straight
to Google's consent screen — one fewer hop in the sign-in flow.

### Changes

- **`config/settings.py`** — added, next to ``SOCIALACCOUNT_STORE_TOKENS``:

  ```python
  # Skip allauth's intermediate provider-confirmation page: initiating a social
  # login via GET (e.g. ``{% provider_login_url 'google' %}``) proceeds straight
  # to the provider instead of asking the user to confirm the sign-in first.
  SOCIALACCOUNT_LOGIN_ON_GET = True
  ```

### Testing

- `python manage.py check` ✔ (no issues)
- Verified via the shell that `settings.SOCIALACCOUNT_LOGIN_ON_GET` resolves to
  `True`.

### Files Modified

- `config/settings.py`, `docs/HANDOVER.md`

---

## 71. Account Settings Restructure — Sheets/Drive Tabs Removed

**Date:** 12 August 2026  
**Branch:** main

### Overview

Removed the **"Club Google Sheets"** and **"Google Drive"** tabs from Account
Settings (`/settings/`) so the page holds only the user-preference tabs
(Notifications / Account & Google / Display). Google Sheets integration now
lives **exclusively** in the staff-only Club Management dashboard, and the
club-sheet API endpoints are staff-gated.

### Changes

- **`templates/settings.html`** — removed the two tab buttons and their content
  panes (`tab-google_sheets`, `tab-google_drive`), the spreadsheet verify AJAX
  block, and the Drive-tab unlink wiring. The Account & Google tab keeps its
  Google connection status + Drive access status card.
- **`core/views.py::settings_view`** — dropped `form=sheets` handling and the
  `club_sheets` / `sheet_saved` / `sheet_errors` / `drive_info` context; the
  GET `?tab=` value is sanitised to the three remaining tabs. Removed the now
  unused `get_drive_storage_info` import.
- **`core/views.py`** — `fetch_club_sheet_view`, `append_club_sheet_view`, and
  `verify_club_sheet_view` changed from `@login_required` to
  `@staff_member_required(login_url=settings.LOGIN_URL)` — they are consumed
  only by the staff-only Club Management dashboard. (`upload_note_view` stays
  `@login_required` — students still upload notes.)
- **`core/views.py::drive_connect` / `drive_callback`** — error/success
  redirects now point at `?tab=account` (the removed `?tab=google_drive`
  target is gone).
- **`templates/club_admin.html`** — added a **Verify & Connect** button next
  to Connect/Refresh that calls `POST /clubs/dashboard/sheets/verify/` (moved
  from the removed Settings tab), with a success/error result panel; the
  prefill comment now references the saved spreadsheet instead of Settings.

### Permissions summary

| Endpoint | Guard |
| :--- | :--- |
| `GET/POST /clubs/dashboard/sheets/` / `append` / `verify` | staff only |
| `POST /api/clubs/verify-transaction/` | staff only (unchanged) |
| `POST /api/notes/upload/` | any authenticated user (unchanged) |

### Tests

- `GoogleApiViewsTest` / `VerifyClubSheetApiTest` users now `is_staff=True`;
  added non-staff denial tests (authenticated student → bounced to login).
- Removed `GoogleDriveSettingsTabTest` and the Settings-sheets POST tests;
  replaced `SettingsGoogleSheetsTabTest` with `ClubSheetsConfigPrefillTest`.
- `DriveOAuthFlowTest` redirect assertion now expects `?tab=account`.
- Full core suite **553 tests OK**; `host` + `payments` suites OK.

### Files Modified

- `templates/settings.html`, `templates/club_admin.html`, `core/views.py`,
  `core/tests.py`, `docs/HANDOVER.md`

---

## 72. Club Sheets Endpoints Moved to `/clubs/dashboard/sheets/`

**Date:** 12 August 2026  
**Branch:** main

### Overview

Renamed the club-sheet endpoints from the generic `/api/clubs/sheet/*` prefix
to the literal clubs-dashboard namespace requested for the settings
restructure (§71) — sheets management now routes under `/clubs/dashboard/`,
matching where the UI actually lives (the staff-only Club Management
dashboard).

### Changes

- **`core/urls.py`** — path rewrites (URL **names** unchanged, so no caller
  edits were needed — templates use `{% url %}` and tests use `reverse()`):

  | Before | After | View |
  | :--- | :--- | :--- |
  | `GET /api/clubs/sheet/` | `GET /clubs/dashboard/sheets/` | `fetch_club_sheet_view` |
  | `POST /api/clubs/sheet/append/` | `POST /clubs/dashboard/sheets/append/` | `append_club_sheet_view` |
  | `POST /api/clubs/sheet/verify/` | `POST /clubs/dashboard/sheets/verify/` | `verify_club_sheet_view` |

- **`core/tests.py`** — `VerifyClubSheetApiTest` docstring updated to the new
  path (all test calls use `reverse()` by name, so they re-pointed
automatically).
- **`docs/HANDOVER.md`** — endpoint tables and §71 permission table updated to
  the new paths (fetch/append also relabelled from `@login_required` to
  **staff only**, matching the §71 gating).

### Notes

- The old `/api/clubs/sheet/*` URLs now return 404 with no redirect — nothing
  internal references them (all consumers resolve by URL name), and the
  §71 task explicitly requested the clean clubs-namespace routing.
- No route conflicts: `clubs/` and `clubs/manage/` are exact-match `path()`
  patterns, and there is no generic `clubs/<slug>` pattern to shadow the new
  routes.

### Testing

- `manage.py check` ✔
- `reverse()` resolves to `/clubs/dashboard/sheets/`, `/append/`, `/verify/` ✔
- Repo-wide grep for `api/clubs/sheet` — zero remaining references ✔
- `GoogleApiViewsTest`, `VerifyClubSheetApiTest`, `ClubSheetsConfigPrefillTest`,
  `SecurityAuditTest` — **36 tests OK** ✔

### Files Modified

- `core/urls.py`, `core/tests.py`, `docs/HANDOVER.md`

## 73. Student Dashboard Overhaul — BST Clock, Routine, Calendar, AI Extractor

### Overview

The `/dashboard/` page was redesigned around the student's day instead of the
old meal/transport/medical summary widgets (which duplicated the standalone
`/meals/`, `/transport/` and `/medical/` pages and were removed):

- **Live Bangladesh clock card** — Asia/Dhaka (UTC+6) time rendered client-side
  via `Intl.DateTimeFormat(..., {timeZone: 'Asia/Dhaka'})`, with a countdown to
  the next class and a pulsing "in class now" state.
- **Today's Class Routine** — the signed-in user's weekly schedule with NOW /
  NEXT UP badges on the active/upcoming period, re-evaluated every second.
- **Interactive Academic Calendar** — a monthly grid (Saturday-first, matching
  the campus week) of `AcademicEvent` rows (exam / holiday / assignment /
  event), with prev/next month navigation fetching from the calendar API.
- **Recent Activity** — the user's newest notes / transport / medical / meals /
  club actions merged into one reverse-chronological feed (`_recent_activity`).
- **Quick Campus Info** — the latest published notice + shortcut tiles.

All time logic runs in the browser against the embedded schedule JSON: the
server is UTC and must not guess Dhaka time, so the clock, countdown and
highlighting never depend on server timezone configuration.

### New models (`core/models.py`)

- **`Routine`** — OneToOne to `User`; `schedule` JSONField in the canonical
  `{"days": [{"day": "Sun", "slots": [{"start": "08:30", "end": "10:00",
  "course": "CSE-1101", "room": "201"}]}]}` shape (24-hour `HH:MM` times,
  day keys `Sat`…`Fri`), plus `source_name` (uploaded file or "manual").
- **`AcademicEvent`** — `title`, `category` (exam/holiday/assignment/event),
  `event_date`, `description`. Seeded with a starter set of BD national
  holidays + exam windows + assignment deadlines by migration `0031`.
  Registered in Django admin for staff management.

### AI routine extraction (`services/routine_parser.py`)

`extract_routine_schedule(upload, referer)` drives `POST /api/routine/extract/`:

- **PDF/DOCX** → plain text via `services.parser.extract_document_text`, then a
  text-mode call to the default free model (`nvidia/nemotron-3.5-lightning:free`).
- **PNG/JPG** → the image is sent inline (base64 data URL) to the vision model
  `OPENROUTER_VISION_MODEL` (default `meta-llama/llama-3.2-11b-vision-instruct:free`,
  overridable via env).
- The model is asked for strict JSON; `normalize_schedule` validates and
  coerces the reply into the canonical shape (24-hour times, day aliases,
  Saturday-first ordering) and drops unreadable slots. The system prompt treats
  the uploaded file as untrusted data (prompt-injection guard).
- The endpoint allows only PDF/DOCX/PNG/JPG under 10 MB, requires login, and
  degrades to a friendly 503 when `OPENROUTER_API_KEY` is unset.

### Settings → Routine tab

`/settings/?tab=routine` (4th tab) lets students:
- see the current schedule preview grouped by day,
- upload a routine file and preview the AI extraction before saving
  (`save=1` persists to their `Routine` row),
- paste the schedule as JSON manually (`form=routine_json`),
- clear the saved schedule (`form=routine_clear`).

### New endpoints (`core/urls.py`)

| Method | Path | View | Purpose |
|---|---|---|---|
| POST | `/api/routine/extract/` | `routine_extract` | AI-extract a schedule from an uploaded file (`save=1` persists) |
| GET | `/api/calendar/events/?month=YYYY-MM` | `api_calendar_events` | Academic events + grid metadata for a month |

Both are `@login_required`. The calendar API returns the same shape the
initial dashboard render embeds, so month navigation reuses one code path.

### Files Modified

- `core/models.py` (+ `Routine`, `AcademicEvent`), `core/migrations/0030_*`,
  `0031_seed_academic_events.py`
- `core/views.py` (dashboard rewrite, settings Routine tab, two new views),
  `core/urls.py`, `core/admin.py`
- `services/routine_parser.py` (new), `services/openrouter.py` (+`get_vision_model`),
  `config/settings.py` (+`OPENROUTER_VISION_MODEL`)
- `templates/dashboard/home.html` (rewrite), `templates/settings.html` (Routine tab)
- `static/css/dashboard.css`, `static/css/settings.css`
- `core/tests.py` (see below)

### Testing

- `manage.py check` ✔
- Full core suite **575 tests OK** (was 553 — +22 new: `DashboardWidgetsTest`
  rewritten for the new widgets, plus `RoutineParserTest`, `RoutineExtractApiTest`,
  `CalendarApiTest`, `RoutineSettingsTabTest`, endpoint-auth-matrix entries) ✔
- `host` + `payments` suites OK ✔
- Browser-verified (Chrome): login → dashboard renders the live clock, next-class
  countdown, routine panel, calendar grid and activity feed with **no console
  errors**; Settings → Routine tab renders preview + upload + JSON entry ✔

---

## 74. Reports & Feedback Module

**Date:** 12 August 2026  
**Branch:** main

### Overview

Built a complete **Reports & Feedback** module so students can submit
issue/feedback reports and staff can triage them with a visible response —
modeled on the project's Django conventions (the original request described
this as a Next.js/Prisma/NextAuth feature; this repo is Django 4.2, so the
module is implemented natively with a `Report` model, JSON APIs, and
Tailwind-styled pages that work in the existing app).

### Data model (`core/models.py` + migration `0032`)

`Report` — `user` (FK), `title`, `category` (`academic` / `facility` /
`technical` / `other`), `description`, `status` (`pending` / `in_progress` /
`resolved` / `rejected`, default `pending`), `admin_notes`, `created_at`,
`updated_at`. Indexed for the two hot paths: per-user history and the staff
status inbox. Registered in Django admin with list filters + inline status
editing. Also added a `report` category to `Notification` so status changes
push real-time bell alerts.

### Pages

| URL | View | Access | Purpose |
|---|---|---|---|
| `/dashboard/student/reports/` | `reports_student_view` | `@login_required` | Submit form + personal history with status badges and staff responses |
| `/dashboard/admin/reports/` | `reports_admin_view` | `@staff_member_required` | Filterable table of every report with student details + inline status/notes management |

### API endpoints (`core/views.py`)

| Method | Path | Access | Behavior |
|---|---|---|---|
| GET | `/api/reports/` | `@login_required` | The signed-in student's own reports (never others') |
| POST | `/api/reports/` | `@login_required` | Submit a report (JSON or form body; validates title/description/category; starts `pending`) |
| GET | `/api/admin/reports/` | `@staff_member_required` | All reports with user details (name, student ID, department); `?status=` / `?category=` filters |
| PATCH | `/api/admin/reports/<id>/` | `@staff_member_required` | Update `status` + `admin_notes`; creates a `Notification` and WebSocket push to the student when anything changes |

### Navigation

- Sidebar: **Reports & Feedback** link for every signed-in user; a **Report
  Inbox** link in a new staff-only sidebar section (`{% if user.is_staff %}`).
- `core/context_processors.py` gains `reports_student`, `reports_admin`,
  `api_reports`, `api_admin_reports` in the `ENDPOINTS` registry.

### Templates

- `templates/reports/student_reports.html` — form (title / category dropdown /
  description) posting JSON via `fetch` + CSRF header; history cards with
  color-coded status badges, category chips, and a highlighted **Staff
  response** block; new submissions prepend live.
- `templates/reports/admin_reports.html` — client-side status/category filter
  bar, table with student identity, description clamp, inline status select +
  staff-notes input, and a per-row **Update** button that PATCHes and
  re-renders the badge/notes in place with a saved indicator.
- `templates/reports/_status_badge.html` — shared badge partial (warning /
  info / success / danger theme tokens).

### Files Modified

- `core/models.py` (+`Report`, +`report` notification category), migration `0032`
- `core/views.py` (+5 views + `_serialize_report`), `core/urls.py` (+5 routes),
  `core/admin.py` (+`ReportAdmin`), `core/context_processors.py`
- `templates/base.html` (sidebar links), `templates/reports/*` (3 new files)
- `core/tests.py` (`ReportModelTest` + `ReportsModuleTest` + admin-page gating)
- `docs/HANDOVER.md` (this section + pages/API tables)

### Testing

- `manage.py check` ✔
- Full suite **646 tests OK** (was 575 — +24 model/API/page tests for reports,
  +4 admin-page gating assertions, +2 endpoint-registry entries) ✔
- `host` + `payments` suites OK ✔

---

## 75. Hero Button Contrast Fix — "Medical Services" (Dark Ink on White)

**Date:** 12 August 2026  
**Branch:** main

### Problem

The **Medical Services** hero button next to "Login to Dashboard" showed a
low-contrast label. Root cause: the homepage's global link reset
`body.landing a { color: inherit }` (specificity 0,1,2) beat the button's own
color rule `.hero-btn-secondary` (0,1,0), so the button and its FontAwesome
heart-pulse icon inherited the body ink instead of their intended styling.

### Fix

- **`static/css/main.css`** — scoped the secondary-button rules under
  `body.landing` so they win the cascade over the link reset:
  - `body.landing .hero-btn-secondary` → `background:#ffffff` (white),
    `color:#111827` (gray-900 dark ink); hover `background:#f3f4f6` (gray-100).
  - `body.landing .hero-btn-secondary i` → `color:#DC2626` (red-500) so the
    heart-pulse icon is always visible on white.
- **`templates/index.html`** — the button element now also carries the exact
  utility intent (`bg-white text-gray-900 font-semibold hover:bg-gray-100
  transition-colors`) and the icon gets `text-red-500`. Note the public
  homepage does **not** load the Tailwind CDN (it uses `theme.css` +
  `main.css`), so the custom-CSS rules are what actually render; the utility
  classes document intent and are inert until Tailwind is added there.

### Verification

- `getComputedStyle` on a fresh origin: button color `rgb(17,24,39)`
  (gray-900), background `rgb(255,255,255)` (white), icon color
  `rgb(220,38,38)` (red-500), hover background `rgb(243,244,246)` (gray-100).
- Zero console errors. (An earlier `127.0.0.1` check was served from the
  browser's stale HTTP cache — `localhost` origin confirmed the fresh CSS.)

### Files Modified

- `static/css/main.css`, `templates/index.html`, `docs/HANDOVER.md` (this
  section).

---

## 76. Demo Users Seeded During Render Build (`build.sh`)

**Date:** 12 August 2026  
**Branch:** main  

### Overview

`build.sh` now seeds the demo accounts automatically during Render's build
phase: immediately after `migrate` it runs `manage.py seed_demo_users`
(idempotent, §69), so every deploy guarantees `admin`/`admin123` and
`student`/`student123` exist in the production PostgreSQL database with no
manual `createsuperuser` step. Pushed as commit `9542886`; pushing to `main`
triggers the GitHub Actions deploy workflow, which runs the test suite and then
posts to the Render deploy hook (Render's `autoDeploy` is off — the webhook is
the only path to production).

### Changes (`build.sh`)

- **`migrate --noinput` now runs unconditionally during the build** — it was
  previously gated behind `SUPABASE_DB_URL` (the Render-managed Postgres path
  relied on the release command). Migrating in the build phase guarantees the
  tables exist before the seed step, even on a fresh database. The render.yaml
  `releaseCommand: python manage.py migrate --noinput` is unchanged and still
  runs idempotently before the new release serves (a no-op on an already-
  migrated DB).
- **`python manage.py seed_demo_users`** added directly after the migrate step,
  with the same `RENDER_BUILD=true` guard. Idempotent — existing users are
  never touched, so re-running on every deploy is safe.
- **Kept from the previous script:** the venv/`python`/`python3` interpreter
  picker and the pip self-upgrade (old pip on Python 3.12 can mis-resolve
  dependency ranges).
- **`RENDER_BUILD=true` is required on every `manage.py` call:** `settings.py`
  fails closed (`ImproperlyConfigured`) when `SECRET_KEY` is missing and
  `DEBUG=false`, and Render injects the generated secret only at runtime — a
  bare `python manage.py …` line would crash the build.

### Resulting build flow

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py seed_demo_users
```

### Testing

- `bash -n build.sh` ✔ (syntax)
- `manage.py seed_demo_users` ✔ — idempotent locally (`exists (skipped)` for
  existing users)
- No test-suite changes — build script only; the seed command's own coverage
  lives in `SeedDemoUsersCommandTest` (§69).

### Files Modified

- `build.sh`, `docs/HANDOVER.md` (this section; §38/§39/§63 flow notes updated)

## 77. RBAC Audit & Admin Dashboard Split — Role-Based Areas, Admin Hub, Club Account Management

**Date:** 12 August 2026  
**Branch:** main

### Overview

Audited and fixed the entire Role-Based Access Control (RBAC) and Admin
Dashboard system. The admin dashboards previously looked identical to the
student dashboard because every role was routed through the same view and
layout; this section documents the root causes found, the new explicit-role
architecture, the dedicated Admin area at `/dashboard/admin/*`, and the new
Club Account Management module.

### Audit Report — Root Causes of the "Duplicate Layout"

1. **One dashboard for everyone.** `/dashboard/` (`views.dashboard`) rendered
the *student* dashboard for any visitor — there was no role dispatch, and
`LOGIN_REDIRECT_URL = '/dashboard/'` sent admins, club managers and students
to the exact same page. Admin consoles (System Admin, Cafeteria, Club,
Medical) were separate URLs but shared the student page shell.
2. **No explicit roles.** Access was implicit Django flags only (`is_staff` /
`is_superuser`); there was no `CLUB` role, no role constants, no
role-aware middleware, and no role-based redirects. Nothing enforced
"students cannot open admin routes" beyond per-view decorators.
3. **Shared look & feel.** Every admin console reused the same student-style
CampusDash top-pill header (`partials/topbar.html`) and `base.html` sidebar
— there was no distinct admin shell, sidebar, or navigation.
4. **No club account management.** `Club.lead_user` was a single FK; there
was no way to create dedicated club-manager accounts, assign users to
clubs, reset passwords, or toggle permissions/status.

### New RBAC Architecture

**`core/roles.py` (new) — the single source of truth.** Defines the three
explicit roles (`admin`, `club`, `student`), `get_user_role(user)` (precedence:
superuser/staff → admin, active `ClubAccount` → club, else student) and
`role_home_path(role)` (admin → `/dashboard/admin/`, club → `/clubs/manage/`,
student → `/dashboard/student/`).

**Role dispatcher at `/dashboard/`.** `views.dashboard` now redirects every
*authenticated* user to their role home; anonymous guests keep the pre-RBAC
behaviour of viewing the student dashboard (so public links and the demo
"Skip login" flow still work).

**`RoleAccessMiddleware` (`core/middleware.py`).** Enforced at the request
layer, before any view: students/club managers hitting `/dashboard/admin/*`
are bounced to their role home; club managers are also kept out of
`/dashboard/student/*`. The middleware uses `role_home_path()` so a student
typing an admin URL lands on their own dashboard, never the login loop.

**Role-aware sign-in.** `RoleAwareLoginView` (subclasses Django's `LoginView`,
wired in `config/urls.py`) sends every sign-in straight to the role home —
admin → `/dashboard/admin/`, club → `/clubs/manage/`, student →
`/dashboard/student/` — while still honouring a safe `?next=` target. Signup
redirects the new student to `/dashboard/student/` the same way.

**Page-level guards (`core/decorators.py`).** `admin_required` gates all
`/dashboard/admin/*` views (staff/superuser; 403 for authenticated
non-admins), and `club_access_required` admits staff **or** active club
accounts to the club workspace (`club_admin_view`).

### Admin Area — `/dashboard/admin/*` (distinct layout)

All six pages render through the new **`templates/admin/admin_base.html`** —
a dedicated admin shell with its own sidebar (Overview, Users & Clubs,
Club Accounts, Database, Website Builder, System Settings, plus links to the
legacy service dashboards), topbar and `static/css/admin_dashboard.css` —
completely separate from the student `base.html` layout.

| URL | View | Page |
| :--- | :--- | :--- |
| `/dashboard/admin/` | `admin_dashboard` | Overview — live platform stats, recent reports/notices/pages, quick links |
| `/dashboard/admin/users/` | `admin_users_view` | User & Club Management — students, staff/admins, club managers |
| `/dashboard/admin/users/clubs/` | `admin_club_accounts_view` | Club Account Management (new module) |
| `/dashboard/admin/database/` | `admin_database_view` | Database Quick Stats — live row counts per model group |
| `/dashboard/admin/content/` | `admin_content_view` | Website Builder / CMS — builder pages + notices + settings links |
| `/dashboard/admin/settings/` | `admin_settings_view` | System Settings — env/config summary + Django admin link |

`templates/reports/admin_reports.html` (Report Inbox) now uses the admin
layout too. The student sidebar (`base.html`) gained role-aware links: staff
see "Admin Panel", club managers see "Club Workspace".

### Club Account Management (new module)

**`ClubAccount` model** (`core/models.py`, migration `0033`): OneToOne to
`User`, FK to `Club`, a `role` (`manager` / `executive` / `president` /
`member`), three permission flags (`can_post_events`, `can_manage_members`,
`can_manage_finances`) and `is_active`. Registered in `core/admin.py`.

**Admin page** (`/dashboard/admin/users/clubs/`, `templates/admin/club_accounts.html`):
- List every club account (club, holder, role, permissions, status).
- **Create** a new club-manager account (username, name, email, password or
auto-generated, club, role, permissions, active flag).
- **Assign** an existing user to a club (duplicate assignment → 409).
- **Reset password** (explicit or auto-generated), **toggle active/inactive**,
and **update role + permission flags** inline.

**APIs** (`/api/admin/club-accounts/*`, all `@admin_required`):
| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| GET/POST | `/api/admin/club-accounts/` | List accounts; create new or assign existing user (`mode=create|assign`) |
| POST | `/api/admin/club-accounts/<id>/password/` | Reset password (blank → generated) |
| POST | `/api/admin/club-accounts/<id>/status/` | Toggle active/inactive |
| POST | `/api/admin/club-accounts/<id>/permissions/` | Update role + permission flags |

### Files Added / Modified

- **New:** `core/roles.py`, `core/migrations/0033_clubaccount.py`,
`static/css/admin_dashboard.css`, `templates/admin/` (`admin_base.html`,
`overview.html`, `users.html`, `club_accounts.html`, `database.html`,
`content.html`, `settings.html`)
- **Modified:** `core/models.py`, `core/views.py` (dispatcher, admin hub
views, club-account APIs, `RoleAwareLoginView`, signup redirect),
`core/decorators.py`, `core/middleware.py`, `core/admin.py`,
`core/urls.py`, `core/context_processors.py`, `config/settings.py`
(middleware + `user_role` processor), `config/urls.py`,
`templates/reports/admin_reports.html`, `templates/base.html`,
`core/tests.py`

### Testing

- `python manage.py check` ✔ (clean)
- `python manage.py test` ✔ — **678 tests pass**, including new
`RoleRoutingTest` (dispatcher + middleware matrix), `AdminDashboardPagesTest`
(admin area renders for staff, admin layout + sidebar), `ClubAccountApiTest`
(create/assign/reset/status/permissions + 403/404/409 guards), and updated
login/signup redirect assertions.

---

## 78. Toast Partial — Infinite Rendering Loop Fix (`partials/toasts.html`)

**Date:** 12 August 2026  
**Branch:** main

### Issue

The shared toast partial (`templates/partials/toasts.html`) was crashing the
Club workspace (and any layout that pulled it in) with an **infinite template
render loop** — the traceback showed `partials/toasts.html` re-rendering
itself over and over until the request hung / timed out.

### Root Cause & Fix

The loop comes from a partial including itself, directly or transitively
(e.g. a base template includes the toasts partial while another nested
partial also pulls it in, or `toasts.html` itself contained a recursive
include). The layout audit fixed the include graph:

1. **`partials/toasts.html` is now purely self-contained** — a single
   `#app-toasts` host `<div>`, one `<style>` block, and one inline `<script>`
   defining `window.showToast()`. It contains **no `{% include %}` and no
   `{% extends %}`** (its header comment mentions the include only inside a
   `{% comment %}` docstring, which Django never executes).
2. **`templates/club/club_base.html`** includes `partials/toasts.html`
   **exactly once**, at the outer body level (line ~145) — outside any loop
   or nested partial.
3. **`partials/display_prefs.html`** and **`partials/pwa_head.html`** are
   head-only partials that include **nothing** — they never pull in toasts.
4. No `{% extends %}` cycle exists anywhere in `templates/` (verified across
   all 14 extends chains); the only dynamic include
   (`builder/edit_page.html` → `{% include t.partial %}`) resolves to
   builder block partials only.

### Regression Guard (`core/tests.py` → `ToastPartialRenderTest`)

- `toasts.html` source (comment blocks stripped) contains no self-include and
  no `{% extends %}`.
- `/dashboard/club/` renders `id="app-toasts"` **exactly once**.
- `/medical/` renders `id="app-toasts"` **exactly once**.

### Verification

- `python manage.py check` ✔ (clean)
- `python manage.py test core.tests.ToastPartialRenderTest` ✔ (3/3)
- `python manage.py test core.tests.RoleRoutingTest core.tests.ClubsPublicPageTest
  core.tests.AdminCalendarApiTest` ✔ (26/26) — Club workspace pages render
  to 200 without hanging.

### Files Modified

- `core/tests.py` (new `ToastPartialRenderTest`)
- `docs/HANDOVER.md` (this section)

---

## 79. System-Default Theme — Hero Page Follows OS Light/Dark

**Date:** 13 August 2026  
**Branch:** main

### Overview

The public homepage (hero) already had full dark-mode styling wired through
`theme.css` (`html[data-theme='dark']` rules for the landing page: navbar,
glass panels, hero overlay, card deck, `body.landing` background). The only
gap was that the **default theme was hardcoded to `light`**, so a visitor on
a dark-OS device always saw the light hero. The default is now **`system`**
— users with no saved preference follow their OS light/dark setting, live
(via `matchMedia`), on the hero page and everywhere else. Explicit choices
still win: anyone who picks Light/Dark in Settings keeps it.

### What Changed

1. **`core/models.py`** — `UserNotificationPreference.theme` default
   `'light'` → `'system'` (new signups start on System Default).
2. **`core/middleware.py`** — `DEFAULT_DISPLAY_PREFS['theme']` → `'system'`
   (signed-in users without a prefs row).
3. **`static/js/display-preferences.js`** — both `'light'` fallbacks →
   `'system'` (anonymous visitors with no `localStorage` pref).
4. **`templates/partials/display_prefs.html`** — the no-flash head script
   falls back to `'system'` instead of `'light'`, so the OS theme applies
   before first paint with zero flash.
5. **`core/views.py`** — the legacy `dark_mode` form path no longer clobbers
   `'system'`: `dark_mode=False` only downgrades to `'light'` when the
   current theme is not `'system'` (so a System-Default user is never
   silently flipped to light by an old client posting the legacy key).
6. **`core/migrations/0034_alter_usernotificationpreference_theme.py`** —
   auto-generated `AlterField` (default → `'system'`) for new rows only.
7. **`core/tests.py`** — three assertions updated to the new default
   (`test_context_processor_defaults_for_rowless_user`,
   `test_invalid_theme_rejected`, and the middleware timezone test).

### Behavior Notes

- **Anonymous visitors** (the hero page's main audience): follow the OS via
  the driver fallback — no saved preference required.
- **New signups**: prefs row is created with `theme='system'`.
- **Existing accounts**: their stored theme (mostly the old `light` default)
  is untouched — deliberate, so explicit choices are never overridden. Only
  new rows get the `system` default; a data migration to flip existing rows
  is possible if portal-wide OS-following is desired (safe in practice
  because `system` resolves to light for light-OS users).
- Settings → Display still offers the tri-state Light / Dark / System
  Default buttons; the active one reflects the saved value.

### Verification

- `python manage.py test` ✔ — **698 tests, all pass** (206s)
- `python manage.py makemigrations --check --dry-run` ✔ — no drift
- Browser (Chrome, after clearing SW cache): hero page stamps
  `data-theme-mode="system"` with no saved preference; resolves to `dark`
  when the OS prefers dark and tracks OS changes live. Zero console errors.
- Note: `runserver --noreload` caches compiled templates — restart the dev
  server after editing templates to see changes.

### Files Modified

- `core/models.py`, `core/middleware.py`, `core/views.py`, `core/tests.py`
- `static/js/display-preferences.js`, `templates/partials/display_prefs.html`
- `core/migrations/0034_alter_usernotificationpreference_theme.py` (new)
- `docs/HANDOVER.md` (this section)

---

## 80. Local Development `.env` — Populated Environment Template

**Date:** 13 August 2026  
**Branch:** main

### Overview

Created a fully populated **local-development `.env`** in the repo root and
kept the tracked **`.env.example`** template in sync. The repo is Django-only
(there is **no Next.js / NextAuth app** — Django's `SECRET_KEY` is the session
and cookie signing secret), so the Next.js-style variables
(`NEXT_PUBLIC_APP_URL`, `NEXTAUTH_URL`, `NEXTAUTH_SECRET`) are intentionally
**not** part of the configuration.

### What Was Added

1. **`.env`** (gitignored — never committed; secrets live here locally):
   - `SECRET_KEY` — freshly generated random Django secret
   - `DEBUG=True`, `ALLOWED_HOSTS=localhost,127.0.0.1`,
     `CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000`
   - `DATABASE_URL=postgres://niter:change-me@127.0.0.1:5432/niter` —
     **local PostgreSQL is now the dev database** (start Postgres, then
     `createuser -P niter` + `createdb -O niter niter` + `manage.py migrate`;
     unset → SQLite fallback).
   - `REDIS_URL=redis://127.0.0.1:6379/0` — channel layer + Huey queue
     (unreachable → in-memory fallback, verified).
   - Google OAuth / Drive: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` (empty
     placeholders), `GOOGLE_REDIRECT_URI=http://localhost:8000/drive/callback/`,
     `GOOGLE_TOKEN_ENCRYPTION_KEY`.
   - Nagad / bKash: `NAGAD_MERCHANT_ID`, `NAGAD_PG_PUBLIC_KEY`,
     `NAGAD_PRIVATE_KEY`, `NAGAD_BASE_URL` (sandbox),
     `NAGAD_CALLBACK_URL` / `BKASH_CALLBACK_URL`
     (`/payments/webhook/nagad/` + `/payments/webhook/bkash/`), plus the
     reserved `BKASH_*` merchant block.
   - `OPENROUTER_API_KEY` (empty → offline engine fallback) + model defaults.
2. **`.env.example`** — added the `NAGAD_CALLBACK_URL` / `BKASH_CALLBACK_URL`
   variables and notes on localhost redirect URIs, so the tracked template
   matches the populated file.

### How Env Loading Works (verified)

`config/settings.py` reads `.env` via `django-environ`
(`environ.Env.read_env(BASE_DIR / '.env')`); **real OS environment variables
always take precedence** over `.env` values (verified: an exported
`SECRET_KEY` in the shell wins over the file). Every variable has a fallback:

- `SECRET_KEY` → dev fallback when `DEBUG=True`, fail-closed otherwise
- `DATABASE_URL` / `SUPABASE_DB_URL` → local SQLite when both unset
- `REDIS_URL` → `InMemoryChannelLayer` when unset/unreachable
- `GOOGLE_CLIENT_*` / `OPENROUTER_API_KEY` → empty → feature degrades
  (admin SocialApp / offline engine)
- Payments → webhooks work with no merchant credentials (invoice-id matching
  + built-in Nagad sha256 signature verification)

### Verification

- `python manage.py check` ✔ — no issues
- Settings dump via `manage.py shell` ✔ — `DEBUG=True`, Postgres engine
  (`django.db.backends.postgresql`, db `niter`, user `niter`,
  host `127.0.0.1`), `GOOGLE_REDIRECT_URI=localhost`, in-memory channel layer
  fallback (Redis not running), quoted `SECRET_KEY` with special characters
  parses correctly
- Full test suite stays green in CI (CI has no `.env` → SQLite test DB).

### Note for Local Dev

Because `DATABASE_URL` is now active, `runserver` / `migrate` / `test`
require local PostgreSQL to be running. Quick start: start Postgres, create
role `niter` (password `change-me`) + database `niter`, then
`python manage.py migrate`. To go back to SQLite, comment out
`DATABASE_URL` in `.env`.

### Files Modified

- `.env` (new, **gitignored** — local only, not committed)
- `.env.example` (tracked template updated)
- `docs/HANDOVER.md` (this section)

---

## 81. Google OAuth / Drive Connect Flow — Wiring & Setup Status

**Date:** 13 August 2026  
**Branch:** main

### Overview

Status of the **Google Drive / Sheets OAuth2 connect flow**. The flow is fully
wired in code and the environment placeholders are ready; only the **real
Google OAuth client credentials** (from the Google Cloud Console) are pending
— they cannot be committed and must be entered by the developer into the
local (gitignored) `.env`.

### How the Flow Works

1. **`GET /drive/connect/`** (`core.views.drive_connect`, `@login_required`)
   — builds a `google_auth_oauthlib.flow.Flow` from `GOOGLE_CLIENT_ID` /
   `GOOGLE_CLIENT_SECRET` / `GOOGLE_REDIRECT_URI` and redirects to Google's
   consent screen with Drive + Sheets scopes
   (`drive.file`, `drive.readonly`, `spreadsheets`). The CSRF `state` is
   stored in the session.
2. **Google consent** — user grants access (offline access_type + consent
   prompt, so a refresh token is always issued).
3. **`GET /drive/callback/`** (`core.views.drive_callback`, `@login_required`)
   — validates the session `state`, exchanges the code for tokens, and stores
   them **encrypted at rest** (Fernet, `core/crypto.py`) on the user's
   `GoogleUserToken` row (`access_token`, `refresh_token`, `token_uri`,
   `client_id`, `client_secret`, `scopes`, `expiry`).
4. **allauth mirror (best effort)** — the connection is also reflected into a
   `SocialAccount`/`SocialToken` so the existing Settings UI and token paths
   see it.
5. The Settings → Account & Google tab exposes connect status
   (`has_google_token`, `has_drive_access`) and the Drive connect/callback
   are linked from the Notes Engine export flows.

### Environment Variables (in the local `.env`)

| Variable | Purpose | Status |
| :--- | :--- | :--- |
| `GOOGLE_CLIENT_ID` | OAuth 2.0 Web client id | **empty — developer must add real value** |
| `GOOGLE_CLIENT_SECRET` | OAuth 2.0 Web client secret | **empty — developer must add real value** |
| `GOOGLE_REDIRECT_URI` | Must match an Authorized redirect URI in Google Cloud | `http://localhost:8000/drive/callback/` (dev) |
| `GOOGLE_TOKEN_ENCRYPTION_KEY` | Optional Fernet key (falls back to `SECRET_KEY` derivation) | empty (ok) |

When `GOOGLE_CLIENT_ID` is set, `config/settings.py` also wires it into
allauth's `SOCIALACCOUNT_PROVIDERS['google']['APP']`, so social sign-in and
the Drive flow share one source of truth.

### Google Cloud Console Checklist (developer)

1. Create an **OAuth 2.0 Client ID** (Application type: **Web application**).
2. Add `http://localhost:8000/drive/callback/` to **Authorized redirect
   URIs** (or the production `https://niter.edu.bd/drive/callback/`).
3. Enable the **Google Drive API** (and Sheets API if club sheets are used).
4. Paste the client id + secret into the local `.env`
   (`GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`).

### Verification

- **Wiring tests (mocked, no credentials needed)** — `core/tests.py`
  `GoogleDriveOAuthTest` (or equivalent) asserts `/drive/connect/` builds the
  Flow from the env credentials and `/drive/callback/` stores tokens; run via
  `python manage.py test core.tests` (or the specific class).
- **End-to-end (pending real credentials)** — sign in as any user, visit
  `/drive/connect/`, complete Google consent, and confirm a `GoogleUserToken`
  row is created and the Settings Account tab shows "connected".

### Note

Local Postgres is now the configured dev database (`.env` `DATABASE_URL`);
for a quick Drive-flow check without starting Postgres, run the server with
`DATABASE_URL` unset so settings fall back to SQLite
(e.g. `env -u DATABASE_URL venv/bin/python manage.py runserver 8000`).

### Files Modified

- `docs/HANDOVER.md` (this section — documentation only; no code changed)

---

## 82. Homepage (Hero) — Permanently Dark Mode

**Date:** 13 August 2026  
**Branch:** main

### Overview

The public homepage / hero page (`templates/index.html`) is now **always
dark**, by brand choice — it no longer follows the OS theme or the user's
Settings → Display preference. (Earlier work made the portal default
`system`; this overrides that **for this page only**.)

### What Changed

1. **`templates/index.html`** — replaced the shared display-preference driver
   (`{% include 'partials/display_prefs.html' %}` → the no-flash
   `display-preferences.js` driver) with a tiny inline script in `<head>` that
   permanently stamps the dark theme before first paint (zero flash):

   ```html
   <script>
       (function () {
           var root = document.documentElement;
           root.setAttribute('data-theme', 'dark');
           root.setAttribute('data-theme-mode', 'dark');
           root.setAttribute('data-density', 'comfortable');
           root.classList.add('dark');
       })();
   </script>
   ```

   Because `theme.css` already contains the complete `html[data-theme='dark']`
   landing palette (navbar, glass panels, hero overlay, card deck, `body.landing`
   background), stamping the attribute activates the dark design with no CSS
   duplication. The theme driver is **not loaded** on this page, so Settings →
   Display cannot lighten it.
2. **`static/css/main.css`** — header comment updated to describe the
   permanently-dark landing (light tokens in `:root` remain the fallback base;
   the dark token block wins by specificity). No functional change.

### Behavior

- The landing page is dark for **everyone**, including anonymous visitors and
  signed-in users with a light preference.
- The rest of the portal (dashboard, settings, service pages) is unaffected
  and still honours each user's theme setting.

### Verification

- `python manage.py test core.tests.StudentPagesSmokeTest.test_all_student_pages_render` ✔
- Served HTML: force-dark script present, `js/display-preferences.js` absent.
- Browser (Chrome, SW cache cleared): `data-theme="dark"`,
  `data-theme-mode="dark"`, `dark` class applied, body background
  `rgb(24,24,27)`, hero/navbar/glass cards + About/Medical sections all
  dark-themed, zero console errors.

### Files Modified

- `templates/index.html`
- `static/css/main.css`
- `docs/HANDOVER.md` (this section)

---

## 83. Google OAuth / Drive — Recurring "Google Access Required" Popup Fix

**Date:** 13 August 2026  
**Branch:** main

### Problem

Notes Engine uploads on Render kept popping the **"Google access required / session
expired"** re-auth modal. The modal only appeared *after* an upload failed with
`auth_required`, and the failures repeated — every attempt ended in the same popup
because the underlying causes were never addressed: no pre-flight session check,
a token-refresh path that gave up too early, an environment-locked redirect URI,
and no diagnostics for a deployment missing the Google credentials.

### Root causes fixed

1. **No session re-validation before upload.** There was no auth-status endpoint:
   the page only learned about a dead session when the upload itself 401'd. An
   expired (but refreshable) access token was never renewed ahead of time.
2. **`get_google_credentials` gave up on stale legacy rows.** When the
   `GoogleUserToken` row was expired and its refresh token was missing or the
   refresh failed, it raised `GoogleReauthRequired` even though the user's
   fresher allauth `SocialToken` was perfectly refreshable. On Render, where
   users sign in via Google (allauth), the legacy row went stale → permanent
   popup.
3. **Redirect URI locked to the environment value.** `GOOGLE_REDIRECT_URI` copied
   from a local `.env` points at `http://localhost:8000` — on Render the OAuth
   callback would hit the wrong origin and Google would reject the code exchange.
4. **Silent deployment misconfiguration.** `GOOGLE_CLIENT_ID` /
   `GOOGLE_CLIENT_SECRET` were still empty placeholders on the deployed server
   (§81) — the failure surfaced as the generic "session expired" popup with no
   server-side log or user-facing hint.

### Changes

**1. `core/google_service.py` — `get_google_credentials` allauth fallback.**
When the legacy `GoogleUserToken` row is expired and cannot refresh (no refresh
token, or the refresh raised `RefreshError` — now logged at WARNING), the user's
allauth `SocialToken` is consulted before raising: `get_user_google_credentials`
refreshes with its own refresh token and **mirrors a fresh `GoogleUserToken` row**
on success. A user who re-consented via Google sign-in keeps working even when
an older Drive-connect row went bad. Behavior with no allauth token is unchanged
(still `GoogleReauthRequired` / `GoogleAccountNotConnected`).

**2. New `GET /api/notes/auth-status/` (`notes_auth_status`, `@login_required`).**
Connection-health check consumed by the Notes Engine on page load:
- calls `get_google_credentials` — an expired access token is **silently
  refreshed** server-side before the user does anything, so an expiring session
  no longer triggers the modal;
- reports `connected`, `reason` (`not_connected` | `refresh_failed`), and
  `google_configured` — when `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` are
  unset it logs a WARNING (visible in Render logs) so the misconfiguration is
  diagnosable;
- returns `redirect_url` (allauth consent) + `drive_connect_url`; always 200
  (the client acts on the body); only the login gate redirects.

**3. Redirect URI resolution — `_drive_redirect_uri(request)`.**
`drive_connect` / `drive_callback` now resolve the callback URL per request: the
configured `GOOGLE_REDIRECT_URI` is honoured when it points at a non-local host;
when it points at `localhost` while the request arrives from a real domain (the
classic `.env`-copied-to-the-server mistake) it is ignored with a WARNING and the
request origin is used instead — so `http://localhost:PORT` (dev) and
`https://<app>.onrender.com` (production) both work without per-environment
Google Cloud changes. `_flow_client_config` also logs a WARNING when the
application credentials are missing.

**4. `_auth_required_response(reason=...)`** — the 401 payload now carries
`reason` (`not_connected` vs `refresh_failed`) and `drive_connect_url`;
`upload_note_view`, `fetch/append/verify club-sheet views`, and
`verify_club_transaction_view` pass the accurate reason.

**5. Notes Engine frontend (`templates/notes/notes_engine.html`).** On load the
page calls `checkGoogleStatus()`: a server without Google credentials shows a
one-time toast ("Google Drive is not configured on this server…") instead of the
modal; upload failures now show the modal with **reason-specific copy** (not
connected / session expired / not configured).

**6. `render.yaml`** — commented `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
(`sync: false`) and `GOOGLE_REDIRECT_URI` guidance so the Blueprint documents
exactly where the production credentials go.

### Scopes audit (requested check)

`drive.file`, `drive.readonly` and `spreadsheets` are requested both by the
Flow-based connect (`_DRIVE_SCOPES` in `core/views.py`) and by the allauth
`SOCIALACCOUNT_PROVIDERS['google']['SCOPE']` block — verified, unchanged, and
covered by existing tests.

### Testing

- `python manage.py check` ✔ · `makemigrations --check` ✔ (no model changes)
- Full suite **707 tests OK** (was 698 — 9 new): `NotesAuthStatusTest` (login
  gate, not-connected, connected, silent refresh + persistence, refresh-failed,
  missing-env-credentials with `assertLogs`), allauth-fallback test in
  `GoogleServiceTest`, `_drive_redirect_uri` tests in `DriveOAuthFlowTest`
  (localhost-env → request origin; production env URI honoured), updated
  upload/club-sheet `auth_required` payload assertions, and the new endpoint in
  the SecurityAuditTest anonymous-access matrix.

### Files Modified

- `core/google_service.py`, `core/views.py`, `core/urls.py`, `core/tests.py`
- `templates/notes/notes_engine.html`, `render.yaml`
- `docs/HANDOVER.md` (this section)

---

## 84. System Audit + Reports Module Upgrade (severity / attachments / envelope)

**Date:** 13 August 2026  
**Branch:** main

### Audit outcome — what was already in place (no changes needed)

A full-system audit against the "complete audit + fix RBAC + build missing UI"
brief found most requested items already implemented and tested. Recorded here
so nobody re-builds them:

| Requirement | Status | Where |
|---|---|---|
| Academic calendar (monthly grid, admin-managed events) | ✅ exists | `api_academic_calendar` (§73), color-coded dots red/orange/blue/green for Exam/Holiday/Assignment/Event in `static/css/dashboard.css` |
| RBAC role dispatch + login redirect | ✅ exists | `core/roles.py`, `core/middleware.py`, §77 |
| Distinct Admin / Student / Club layouts | ✅ exists | `admin/admin_base.html`, `base.html`, `club/club_base.html`; `/dashboard/club` is club-only (`club_access_required`) |
| Admin area: Users, Reports, Database Stats, Calendar Manager, Builder/CMS, Club Accounts | ✅ exists | `/dashboard/admin/*` (§77) |
| Medical booking (doctor/date/time-slot state, validation, toasts) | ✅ wired | `templates/medical/booking.html` — §87 fixed the real bugs: `RadioNodeList` TypeError killed the booking script (native POST fallback) + `.field-error { display:flex }` overriding `hidden` |
| Google Drive/Sheets auto-refresh on Notes | ✅ fixed | §83 + §88 — silent refresh on every check; mid-call 401 "Invalid Credentials" now maps to the re-auth modal instead of a 500 |

### Reports module upgrade (the real gap — built now)

**Model (`Report`)** — new fields + expanded categories (migration `0035`):

- `severity` — `low / medium / high / critical`, default `medium`.
- `attachment` — `FileField` → `reports/%Y/%m/`, optional, 10 MB cap enforced in
  the API (not just the form).
- `attachment_name` — original filename for display, truncated to 255 chars and
  stripped of path components server-side.
- Categories now `academic / facility / medical / technical / general`; legacy
  `other` rows remapped to `general` by the migration's `RunPython` step.

**API — canonical envelope.** All four reports endpoints now return the
standard `{success: boolean, message: string, data: any}` shape with proper
HTTP status codes (400/404/405):

- `GET  /api/reports/` → `data: {count, reports}` (own reports only)
- `POST /api/reports/` → `data: {report}` — multipart or JSON; accepts
  `title`, `category`, `severity`, `description`, optional `attachment`
- `GET  /api/admin/reports/?status=&category=&severity=` → `data: {count, reports}` (staff)
- `PATCH /api/admin/reports/<id>/` → `data: {report}` — status + admin_notes
  still push a real-time `Notification` (category `report`) to the student

> **Convention note:** the rest of the app (meals, transport, medical, notes)
> still uses the legacy `{status: 'success', …}` envelope. Reports is the
> reference implementation of the new convention — migrate other modules
> incrementally, updating their JS consumers + tests together.

**Upload hardening** (defense in depth):

- Size cap 10 MB checked in the view; `config/settings.py` now sets
  `DATA_UPLOAD_MAX_MEMORY_SIZE = 20 MB` so Django's own HTML 400
  (`RequestDataTooBig`, default 2.5 MB) doesn't preempt the JSON error.
- `content_type` whitelist **and** extension whitelist (`.html/.svg/.js/.xml`
  rejected even with a spoofed image content-type) — prevents serving
  same-origin HTML/SVG (stored XSS) from the Django-served `/media/`.

**UI:**

- Student page (`/dashboard/student/reports/`): category + severity selects,
  optional file picker, FormData submit, toast on success/error, severity chip
  + attachment link in history cards.
- Admin page (`/dashboard/admin/reports/`): severity column + client-side
  severity filter (server-side `?severity=` support added to the view + API),
  attachment links, toast on update.
- **Toast fix:** `templates/admin/admin_base.html` now includes
  `partials/toasts.html` — previously `window.showToast` was undefined on all
  admin pages, so the Calendar manager's toast calls threw `ReferenceError`.
  (`partials/toasts.html` is placement-agnostic: it looks up `#app-toasts` at
  call time.)

### Validation

- New tests: severity default/validation, medical category, multipart
  attachment accept, >10 MB reject, unsupported-type reject, dangerous
  extension with spoofed content-type reject, long-filename truncation, and
  canonical-envelope assertions across all four endpoints.
- **716 tests OK** (was 707) · `manage.py check` clean · migration `0035`
  applied to dev DB · live smoke: student login → role-home redirect to
  `/dashboard/student/`, reports page 200 with severity/attachment/toast
  markers, `GET /api/reports/` returns the canonical envelope.

### Files Modified

- `core/models.py`, `core/views.py`, `core/tests.py`, `core/admin.py`
- `core/migrations/0035_report_severity_attachment_categories.py` (new)
- `config/settings.py` (`DATA_UPLOAD_MAX_MEMORY_SIZE`)
- `templates/reports/student_reports.html`, `templates/reports/admin_reports.html`
- `templates/admin/admin_base.html` (toasts include)
- `docs/HANDOVER.md` (this section)

---

## 85. Android WebView Wrapper (`/mobile-webview`)

**Date:** 13 August 2026  
**Branch:** main

A lightweight native launcher for the dashboard, rendering
`https://niter-centralized-dash.onrender.com` in a full-screen Android WebView.
Kotlin, single `MainActivity`, no extra UI.

### Key implementation points (`MainActivity.kt`)

| Requirement | Where |
|---|---|
| `javaScriptEnabled`, `domStorageEnabled`, `databaseEnabled`, `allowFileAccess` | `configureWebView()` |
| Google OAuth "disallowed_useragent" fix | `chromeLikeUserAgent()` — strips the `Version/4.0` marker and normalises the Chrome token to `Chrome/125.0.0.0`, keeping device OS/model tokens; result looks like stock Chrome for Android |
| External redirects | `shouldOverrideUrlLoading` — http/https (Google auth, allauth + Drive callbacks, payment pages) stay in the WebView; `mailto:`/`tel:`/`intent:`/`whatsapp://` open external apps |
| Full-screen | `Theme.AppCompat.NoActionBar` + `android:windowFullscreen` + `WindowInsetsControllerCompat.hide(systemBars())` |
| Hardware BACK | `OnBackPressedCallback` — `webView.canGoBack() ? goBack() : finish()` |
| File uploads | `WebChromeClient.onShowFileChooser` → `ActivityResultContracts.StartActivityForResult` (used by Notes Engine + Reports attachments) |

Security posture: `MIXED_CONTENT_NEVER_ALLOW` (site is https-only), and
`allowFileAccessFromFileURLs` / `allowUniversalAccessFromFileURLs` explicitly
`false` alongside the required `allowFileAccess(true)`. Cleartext HTTP is
banned app-wide by `res/xml/network_security_config.xml` (wired into the
manifest via `android:networkSecurityConfig`), with exceptions only for
loopback hosts (`10.0.2.2`, `localhost`, `127.0.0.1`) used when pointing the
app at a local Django dev server.

### Project structure

```
mobile-webview/
├── settings.gradle.kts / build.gradle.kts / gradle.properties
├── gradle/wrapper/gradle-wrapper.properties   # Gradle 8.11.1 (JAR restored by Android Studio)
└── app/
    ├── build.gradle.kts        # AGP 8.10.1 · Kotlin 2.0.21 · compileSdk 36 · minSdk 26
    └── src/main/
        ├── AndroidManifest.xml # INTERNET, launcher activity, configChanges (no rotate reload)
        ├── java/com/niterhub/dash/MainActivity.kt
        └── res/                # layout (WebView + thin progress bar), theme, adaptive icon, xml/network_security_config
```

### How to open & compile the APK (Android Studio)

1. **File → Open…** → select the `mobile-webview/` folder → **OK** → **Trust Project**.
2. Let Gradle sync (it downloads Gradle 8.11.1 + AGP/Kotlin/AndroidX). If the
   wrapper JAR is missing, Android Studio restores it during sync (or run
   `gradle wrapper` inside `mobile-webview/`).
   - Recommended: **Android Studio Meerkat (2024.3.1)+**, which bundles JDK 17+.
3. **Build → Build APK(s)** → install `app/build/outputs/apk/debug/app-debug.apk`
   on a device, or plug in a phone and press **Run ▶**.
4. Release: **Build → Generate Signed Bundle / APK… → APK** (create a keystore).

Change the target URL via the `startUrl` constant at the top of `MainActivity.kt`.
Full details, including troubleshooting (Google login, blank screen, uploads):
see `mobile-webview/README.md`.

### Files

- `mobile-webview/` (new — Gradle project, `MainActivity.kt`, manifest, resources, README)
- `docs/HANDOVER.md` (this section)

---

## 86. Final Integration Status — Module Matrix, OAuth Refresh & Health Check

**Date:** 13 August 2026  
**Branch:** main

Closing handover: current status of every dashboard module, the Google OAuth
refresh-token behaviour, and the verification results that ship with the
Android wrapper.

### Dashboard module status matrix

| Module | Where | Status |
|---|---|---|
| **Admin** | `/dashboard/admin/*` (distinct `admin/admin_base.html` layout, not the student shell) | ✅ Users, Reports & Feedback, Database Stats, Academic Calendar Manager, Website Builder/CMS, Club Account Management — all present |
| **Student** | `/dashboard/*` (distinct student layout) | ✅ Home (academic calendar w/ red-orange-blue-green event dots), Reports w/ severity + attachments, Notes Engine (Google Drive), Meals, Transport, Medical booking, Notices, Tickets, Profile |
| **Medical** | `/medical/booking`, `/dashboard/student/medical`, host/admin dashboards | ✅ AJAX submit (`fetch` → `/book-appointment/`, no reload) gated on `data.success === true`; field errors clear on selection; live upcoming-appointments list (§87); host portal lists today's appointments |
| **Club Executive** | `/dashboard/club` (distinct `club/club_base.html` layout) | ✅ Isolated behind `club_access_required` (staff OR active club account); Google Sheets verify/append, member approvals, role assignments, event posts, payment verification |

RBAC: `RoleAccessMiddleware` (core/middleware.py) dispatches each user to their
role home (`role_home_path` in core/roles.py) on login and blocks cross-role
pages; admins never render the student layout. Verified by
`core.tests.RoleRoutingTest`.

### Google OAuth refresh-token auto-handling (summary)

- `get_google_credentials()` (core/google_service.py) first tries the legacy
  `GoogleUserToken` row; if the access token is expired, structurally broken,
  or the refresh fails, it falls back to the allauth `SocialToken` — whose
  `refresh()` silently exchanges the stored `refresh_token` for a new access
  token **without any user interaction**.
- `GET /api/notes/auth-status/` (new) renews an expired token on every check,
  so the Notes page no longer pops the "Google access required / session
  expired" modal for a merely-expired token.
- `_drive_redirect_uri()` resolves the OAuth callback per request origin, so
  one registered redirect URI works for both `localhost` dev and the
  `.onrender.com` deployment.
- Missing `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` env vars log a WARNING and
  surface a clear toast instead of a broken popup.
- Full detail in §83 above.

### Health check (this handover)

- `venv/bin/python manage.py test core.tests.RoleRoutingTest core.tests.ToastPartialRenderTest`
  → **18 tests, OK** (RBAC route security + toast partial rendering).
- Android XML resources (manifest, network security config) validated
  well-formed; `MainActivity.kt` carries the UA override, `onShowFileChooser`
  and back-navigation requirements (see §85).
- Prior full-suite run: **716 tests OK** (commit `b5fdb0e`, Reports upgrade).

### Release APK (quick reference)

Android Studio → **File → Open…** → `mobile-webview/` → **Trust Project** →
sync → **Build → Generate Signed Bundle / APK… → APK** (create a keystore) →
`release` → signed APK written to
`app/build/outputs/apk/release/app-release.apk`. Debug APK:
**Build → Build APK(s)** → `app/build/outputs/apk/debug/app-debug.apk`.

### Files

- `mobile-webview/app/src/main/res/xml/network_security_config.xml` (new)
- `mobile-webview/app/src/main/AndroidManifest.xml` (networkSecurityConfig wired)
- `mobile-webview/README.md` (network config + security notes updated)
- `.gitignore` (`daphne.log` added)
- `docs/HANDOVER.md` (this section)

## 87. Medical Booking — Form State Binding + AJAX Submission Fix

**Date:** 13 August 2026  
**Branch:** main

Hardened the `/medical/` appointment booking form
(`templates/medical/booking.html`) against two real bugs that matched the
"validation warnings don't clear / form redirects instead of AJAX" symptoms:

### Root causes fixed

1. **`.field-error` never hid** (`static/css/medical.css`) — the class set
   `display: flex`, which overrode the UA's `[hidden] { display: none }`, so
   "Please choose a doctor." / "Please pick a date." / "Please pick a time
   slot." were permanently visible and the JS `hidden` toggling was a no-op.
   Added `.field-error[hidden] { display: none; }`.

2. **Booking script died at page load** (`templates/medical/booking.html`) —
   `form.elements['time_slot']` returns a `RadioNodeList`, which has no
   `addEventListener`. The `TypeError` aborted the whole inline script, so the
   `submit` handler (with `e.preventDefault()` + `fetch`) was never attached
   and the form fell back to a native HTML POST (full page reload). The fix
   resolves every named control to a plain array (`querySelectorAll` for the
   radio group) and binds `change`/`input` on each input — field errors clear
   the moment the visitor picks a doctor / date / slot, and the generic alert
   disappears once all required fields are valid.

### AJAX submission (no page reload)

- The submit handler now `preventDefault()`s and posts the form payload to
  `/book-appointment/` with `fetch()` (CSRF header from the `csrftoken`
  cookie, `credentials: 'same-origin'`).
- Success is gated on `data.success === true` (the backend returns
  `{status: 'success', success: true, data: {...}}`): shows the
  "Appointment booked successfully!" toast + inline alert, prepends the new
  appointment (Pending badge) to the Upcoming Appointments list, resets the
  form + selection state, and adds the new appointment to the My
  Consultations starter dropdown — all without leaving `/medical/`.
- 409 slot-conflict and other error payloads surface the backend message via
  alert + toast.

### Real upcoming appointments list

- The side panel previously showed hardcoded mock rows; it now renders the
  signed-in student's live `MedicalAppointment` rows (doctor, reason, status
  badge, `|date:"D, M j"` + the new `|fmt_slot` filter for 12-hour display)
  with an empty state.
- `fmt_slot` lives in `core/templatetags/builder_tags.py`: 24h `HH:MM` →
  `HH:MM AM/PM`, already-formatted values pass through unchanged.

### Verification

- `venv/bin/python manage.py check` — no issues.
- Full suite: **724 tests OK**. New `MedicalBookingFormTest` coverage:
  `book_appointment` endpoint (success / login-required / missing fields / 409
  double-booking), the medical page rendering live appointments + empty state,
  a `.field-error[hidden]` CSS regression guard, and the radio-group bind fix.
- Live E2E against `runserver`: login → `/medical/` (all three field errors
  ship `hidden`, radio bind fix present) → `POST /book-appointment/` returns
  `success: true` → reload shows the appointment in the side panel and the
  empty state gone.

### Files

- `templates/medical/booking.html`
- `static/css/medical.css`
- `core/templatetags/builder_tags.py` (`fmt_slot` filter)
- `core/tests.py` (`MedicalBookingFormTest`)
- `docs/HANDOVER.md` (this section)

### Independent verification (no code changes needed)

A follow-up audit of the form-state binding + validation-clearing requirements
confirmed every behaviour in §87 is already live and working, so no further
code changes were made:

- **Input → state binding:** the doctor `<select>`, date input and each
  time-slot radio are individually bound via `change`/`input` listeners
  (`formControls` resolves the `RadioNodeList` to plain inputs, so the
  bind never throws).
- **Dynamic warning clearing:** `onFix` flips `#err-doctor` / `#err-date` /
  `#err-slot` to `hidden` the moment the field is filled and hides the generic
  alert once doctor + date + slot are all valid; warnings are only re-shown on
  submission when a field is empty.
- **Payload contract:** the POST sends `doctor_name`, `appointment_date`,
  `time_slot`, `reason` (matching `book_appointment` in `core/views.py`, which
  answers `{status: 'success', success: true, data: {...}}`).
- **Success flow:** resets the form, hides errors, shows the toast, prepends
  the new appointment to Upcoming Appointments and adds it to the consultation
  dropdown.
- **Live E2E (Chrome, logged in as demo student):** warnings appeared on an
  incomplete submit, cleared dynamically as each field was fixed, submission
  succeeded with no page reload, the new appointment prepended to the list,
  and the form reset — zero console errors. Test appointment cleaned up
  afterwards.

## 88. Google OAuth — 401/Invalid-Credentials Hardening + Upload Session Guard

**Date:** 13 August 2026  
**Branch:** main

Audit + hardening of the Notes Engine Google Drive pipeline. The core
requirements — server-side refresh-token exchange, offline/consent OAuth
params, and frontend modal suppression — were shipped in §83/§86; this pass
verifies each against the code and closes the remaining gaps found in review.

### Requirements verified (already implemented)

1. **Server-side auto-refresh** (`core/google_service.py`) —
   `get_google_credentials` checks `GoogleUserToken.is_expired` and, when
   expired, exchanges the stored `refresh_token` at
   `https://oauth2.googleapis.com/token` (via google-auth `Credentials.refresh`)
   and persists the new `access_token` + `expiry` **back to the database**
   (encrypted at rest). The allauth `SocialToken` path (`get_user_google_credentials`)
   does the same and mirrors the result into `GoogleUserToken`. The upload
   view and `GET /api/notes/auth-status/` both route through it, so an
   expiring session is renewed silently on every check/upload.
2. **Offline access on connect** — the allauth provider config
   (`config/settings.py`) sets `AUTH_PARAMS = {access_type: offline,
   prompt: consent}`, and the dedicated `/drive/connect/` flow calls
   `authorization_url(access_type='offline', prompt='consent',
   include_granted_scopes='true')` — both guarantee Google returns a refresh
   token on (re-)connection. New test assertions lock both in.
3. **Modal suppression** (`templates/notes/notes_engine.html`) — the native
   file picker opens immediately on "Upload Notes"; the re-auth modal only
   appears when the upload API answers `auth_required` (genuine not-connected
   or failed-refresh), never after a successful auto-refreshed upload.

### Gaps closed in this pass

- **Mid-call 401 "Invalid Credentials" → re-auth, not 500** — a Drive API
  `HttpError` 401 (revoked grant, or an access token that expired between the
  expiry check and the call whose one-shot auto-refresh also failed) was
  swallowed by the generic handler into `GoogleServiceError` → HTTP 500 →
  generic toast. `upload_note_to_user_drive` (`core/google_service.py`) and
  `upload_file_to_drive` / `get_or_create_notes_folder`
  (`academic_notes/drive_service.py`) now map 401 `HttpError` to
  `GoogleReauthRequired`, so the view answers `401 auth_required` and the
  Notes UI shows the reconnect modal.
- **Expired Django session during upload** — `@login_required` bounces a
  stale-session POST to the login page, and `fetch` followed the redirect,
  so the upload handler parsed login HTML as JSON and showed "Upload failed
  (HTTP 200)". The handler now checks `response.redirected` and sends the
  user to the login URL.

### Verification

- `venv/bin/python manage.py check` — no issues.
- Full suite: **730 tests OK** (up from 724). New coverage:
  `drive_connect` authorization kwargs (`access_type=offline` +
  `prompt=consent`), allauth `AUTH_PARAMS.prompt`, `HttpError` 401 →
  `GoogleReauthRequired` mapping in both Drive service modules (and
  non-401 `HttpError` still maps to `GoogleServiceError`), and the Notes
  Engine template redirect guard.
- Live E2E against `runserver`: login → `GET /api/notes/auth-status/` returns
  the structured envelope (`connected` / `reason` / `google_configured` /
  `redirect_url`), and `/notes/` ships the auth-status probe, the upload
  handler redirect guard, and the re-auth modal markup.

### Files

- `core/google_service.py`
- `academic_notes/drive_service.py`
- `templates/notes/notes_engine.html`
- `core/tests.py`
- `docs/HANDOVER.md` (this section)

## 89. Meal Ticket System — Monthly Subscriptions, QR Passes & 9 PM Cancel Rule

**Date:** 13 August 2026  
**Branch:** main

Overhaul of the Online Meal Ticket System (`/meals/`) from a front-end-only
mock into a live, payment-backed monthly subscription with QR meal passes
and a time-locked advance-cancellation rule.

### 1. Breakfast removed (UI + API)

- `DAILY_MEAL_CAPACITY` now holds **Lunch (200) / Dinner (160)** only — the
  claim API rejects `breakfast` with 400, and the meal-type selector on
  `/meals/` and `/tickets/` renders just the two chips/radios.
- The `breakfast` choice stays on the `MealTicket` model purely for legacy
  rows; old tickets still render in the cafeteria admin redemptions feed.

### 2. Monthly subscription + payment gateway

- New **Pay Monthly Meal Subscription** modal on `/meals/` (bKash / Nagad /
  Rocket) posts wallet number + TrxID to the existing checkout gateway
  (`/checkout/`, `type=meal`) and activates the subscription on success.
- `_process_checkout` now scopes the entitlement to the **current calendar
  month** (`expires_at` = last day of month 23:59:59, `month_start` = today)
  and **pre-allocates one Lunch + one Dinner slot per remaining day** into the
  new `MealSubscription.slots_remaining` balance (2 × remaining days).
- `claim_meal` accepts a `meal_date` (today or any future date inside the
  subscription), locks the subscription row (`select_for_update`) and
  decrements the balance atomically; an exhausted balance answers 403 with a
  clear renewal message.

### 3. Claim → QR digital meal pass

- A successful claim returns the backend token and the page renders a
  scannable QR code (qrcodejs via CDN) inside the **Active Digital Meal Pass**
  card. Payload: `MEAL|<token>|<date>|<student-id>|<meal-type>`.
- The pass card + ring/supply stats are now driven by the server-rendered
  `state_json` blob (live capacity, subscription balance, latest ticket).

### 4. Advance cancellation rule (before 9:00 PM previous night)

- New `POST /cancel-meal/` endpoint: a ticket for date D may be cancelled
  **only before 21:00 on D−1**. After the cutoff it answers 403 with
  "Meals for tomorrow can only be cancelled before 9:00 PM tonight." and the
  front-end swaps the button for a locked state; same-day cancels are always
  blocked (the cutoff has already passed).
- On success the ticket row is deleted (slot + capacity released) and the
  meal is **refunded back into `slots_remaining`**. Upcoming tickets render
  server-side with a Cancel Meal button (hidden once the window closes) and
  a real-time `Notification` is pushed on claim/cancel.

### Files

- `core/models.py` + `core/migrations/0036_…` (slots_remaining, month_start,
  meal_date)
- `core/views.py` (meal_dashboard context, claim/cancel, checkout month
  crediting, cafeteria admin Lunch/Dinner)
- `core/urls.py` (`cancel-meal/`)
- `templates/meals.html` (modal, QR pass, ticket list) + `static/css/meals.css`
- `templates/ticketing/tickets.html` (breakfast radio removed)
- `core/tests.py` + `payments/tests.py`

### Verification

- Full suite: **749 tests OK** (new: breakfast rejection, date-scoped claims,
  balance decrement/exhaustion, cancel before/after cutoff, redeemed/pending
  blocks, checkout month-slot crediting, meal dashboard balance/ticket
  rendering).
- Live E2E against `runserver`: login → `/meals/` markup (no breakfast chip,
  qrcodejs wired, subscription banner) → claim for tomorrow returned
  `#MEAL-0697` (balance 20→19) → cancel refunded the slot (19→20) and
  removed the ticket.

## 90. Dynamic User Names on All Passes + Cleaned-Up Profile Dropdown

**Date:** 13 August 2026  
**Branch:** main

Removed every hardcoded placeholder identity from the student-facing passes
and slimmed the shared profile popover to exactly the account actions that
matter.

### 1. Dynamic user names (no more "Rifat Hasan" mocks)

- **Transport** (`templates/transport.html`) — the Passenger Name field now
  pre-fills `user.get_full_name()` (falls back to `user.username`), and the
  boarding-pass fallback uses a server-rendered `CURRENT_USER_NAME` constant
  instead of the hardcoded string.
- **Medical** (`templates/medical/booking.html` + `core/views.py`) — the
  Active Medical Pass is no longer a static mock (`#MED-1042` / Rifat Hasan /
  Dr. Ahmed Khan / Tomorrow / 10:00 AM). It binds the Patient field to the
  signed-in user and renders the **next upcoming appointment's** real doctor,
  date, time (`|fmt_slot`) and status; with no appointment it shows a clean
  empty state.
- **Meals** (`/meals/`) — already dynamic (§89); verified.
- **Checkout** (`templates/checkout.html`) — the Student Verification badge
  now shows the real name, `student_profile.student_id` (fallback `username`)
  and `user.email` (fallback `username`) — the `"Rifat Hasan"` /
  `CSE-22014` / `rifat.hasan@niter.edu.bd` placeholders are gone.
- **Dashboard header** (`dashboard/home.html`) — already dynamic
  (`get_full_name` → `username` → `Guest`); verified, no change needed.

Every display falls back `get_full_name()` → `username` (→ email where
relevant) so an empty profile never renders a fake name.

### 2. Profile dropdown cleanup (`templates/partials/topbar.html`)

- Removed the **Notifications** menu item and its JS bell-link handler
  (the real-time bell stays in the header row).
- Removed the **Switch Account** item.
- Authenticated menu now contains **exactly Settings + Sign Out**; guests see
  Sign Up + Sign In. Settings is authenticated-only now.

### Files

- `templates/partials/topbar.html`
- `templates/transport.html`
- `templates/medical/booking.html` + `core/views.py`
- `templates/checkout.html`
- `core/tests.py` (updated `ProfilePopoverAuthTest`, new `DynamicUserNameTest`)

### Verification

- Full suite: **754 tests OK** (popover auth states + 5 new dynamic-name
  tests: transport/medical/checkout render the real name, no `Rifat Hasan`
  anywhere, fallback to username, latest-appointment pass).
- Live E2E as a user named "E2E Student" with a confirmed appointment:
  transport input `value="E2E Student"`, medical pass shows E2E Student /
  Dr. Farah / dynamic token, checkout shows real name+email, meals shows the
  name, and the dropdown has Settings + Sign Out only.
## 91. QR Attendance System + Academic Calendar Grid Fix

**Date:** 13 August 2026  
**Branch:** main

New end-to-end class attendance module (student scan side + admin session
console) and a fix for the dashboard Academic Calendar that never rendered
the date cells.

### 1. Academic Calendar grid fix

- **Root cause:** `student_dashboard` passed the calendar/routine payload to
  `templates/dashboard/home.html` as a pre-serialized JSON *string* rendered
  inside a plain `<script id="dash-data">`. Autoescape HTML-encoded the
  quotes (`{&quot;routine&quot;: null, ...}`), so `JSON.parse` threw and the
  calendar grid stayed empty while the static weekday header rendered.
- **Fix:** the view now passes the plain `dict` and the template renders it
  with `{% json_script 'dash-data' %}` (Django's own encoder) — no
  double-encoding, no HTML-escaping. The JS reads
  `document.getElementById('dash-data').textContent` as before and the grid
  (day cells, event dots, prev/next month navigation, legend) renders from
  the `calendar` metadata (`days_in_month`, `first_weekday`, `events_by_day`,
  `prev_month`, `next_month`) fetched per month from `/api/calendar/events/`.

### 2. Backend Attendance Engine

- **Models** (migration `0037`):
  - `AttendanceSession` — `course_code`, unique `session_token`
    (`ATD-XXXXXX`, generated by `generate_attendance_token()`), `created_at`,
    `expires_at`, `is_active`, `is_live` (computed: active + not expired).
  - `AttendanceRecord` — `student` FK, `session` FK, `timestamp`, `status`
    (`present`), `ip_address`. A `unique_together(student, session)` guards
    duplicate scans at the database level.
- **API endpoints:**
  - `POST /api/attendance/scan/` — accepts `session_token`; validates the
    session exists, is active, not expired, passes the campus-Wi-Fi gate,
    then creates the record (409 on duplicates). Returns course code + token
    on success.
  - `GET /api/attendance/my-stats/` — per-course totals, attended counts and
    percentages plus overall summary and recent check-in history.
- **Campus Wi-Fi architecture prep:** `core/middleware.py` now ships
  `is_campus_wifi(request)` — a placeholder IP/network check reading the
  client IP against `CAMPUS_NETWORK_CIDRS`. It stays open (returns True)
  until `ENFORCE_CAMPUS_WIFI=True` is set in settings/env, so the restriction
  can be flipped on later with zero caller changes.

### 3. Student side (`/attendance/`)

- New topbar "Attendance" pill (desktop + mobile profile menu).
- **Camera QR scanner** via `html5-qrcode` (CDN) — Start/Stop controls with
  graceful fallback messaging when the camera is unavailable or the library
  fails to load.
- **Manual token input** fallback with Enter-to-submit.
- On success a toast shows "Attendance marked Present for [Course Code]"
  and the stats table refreshes in place.
- **Stats table:** Course / Total Classes / Attended / Percentage badge
  (green ≥75 %, amber ≥50 %, red below) plus an overall summary strip and
  a Recent Check-ins list.

### 4. Admin side (`/dashboard/admin/attendance/`)

- New "Attendance & QR Sessions" entry in the admin sidebar.
- Course selector + duration → **Generate Class QR**: creates the session and
  renders a large `qrcodejs` QR (payload `ATT|<token>`) for projection.
- **Live panel**: auto-refreshing scan counter (`/api/admin/attendance/
  sessions/<token>/live/`), pulsing live indicator, recent-scanner feed, and
  a Close Session button.
- **Records console**: full attendance log with filters by course, date, and
  student name/ID (`/api/admin/attendance/records/`).
- Admin APIs are guarded by `admin_required` (403 for authenticated
  students; 302 → login for guests).

### 5. Tests & verification

- ~26 new tests (`AttendanceModelTest`, `AttendanceScanApiTest`,
  `AttendanceStatsApiTest`, `AdminAttendanceApiTest`, `AttendancePageTest`,
  `DashboardCalendarGridTest`): token format/uniqueness, scan success,
  duplicate 409, expired session, campus-gate open/closed paths, stats
  percentages, admin create/live/close/records + role guards, and the
  calendar `json_script` round-trip (asserts no `&quot;` escaping and valid
  `JSON.parse`).
- **Full suite: 780 tests OK.**
- **Live E2E:** dashboard grid metadata renders without escaping → admin
  created `ATD-F3CD13` (`ATT|ATD-F3CD13`) → student scan succeeded →
  duplicate rejected (409) → stats show CSE-1101 1/1 100% → live counter
  reported 1 with `is_live: True` → records listed the student → student
  blocked from admin API (403). E2E data cleaned afterwards.

### 6. Code-review hardening (included in `f832515`)

- **Precedence bug in the student page:** `if (!body.status === 'success')`
  parsed as `(!body.status) === 'success'` — always false for a truthy
  status, so the check was a no-op. Now `body.status !== 'success' ||
  !body.data`.
- **Stored-XSS hardening on the student page:** `renderStats` and the
  check-in history injected `course_code` / `status` into `innerHTML`
  unescaped; both now go through an `escapeHtml` helper (the admin console
  already escaped `student_name`, `student_id`, `course_code`, `session_token`,
  `status`, `ip_address`).
- **Race safety (already in the first pass):** the scan endpoint uses
  `get_or_create` inside `transaction.atomic` with an `IntegrityError` catch,
  so simultaneous double-scans surface as 409 — not a 500.
- **Server-side duration clamp (already in the first pass):**
  `duration_minutes` is clamped to 5–240 in the view, mirroring the admin
  form's `min`/`max`.
- **X-Forwarded-For caveat:** `core/middleware._client_ip` documents that the
  header is client-spoofable and only trustworthy behind a reverse proxy;
  harden it (e.g. trust `REMOTE_ADDR` unless a proxy is configured) before
  enforcing `ENFORCE_CAMPUS_WIFI` in production.
## 93. Attendance Page Dark-Mode Theming (Shared CSS Tokens)

**Date:** 13 August 2026  
**Branch:** main

The student-facing QR Attendance page (`/attendance/`, `templates/attendance.html`)
now follows the global Dark Mode toggle from Settings → Display preferences,
matching `/meals/` and `/medical/`.

### 1. Root cause

`static/css/attendance.css` hardcoded the warm-light palette (`#faf9f6`,
`#ffffff`, `#f7f4ef`, `#f0ebe1`, `#1f2937`, `#6b7280`) everywhere and defined
no CSS custom properties, so the global theme driver's `html[data-theme='dark']`
overrides in `theme.css` had nothing to flip — the page stayed permanently light
while the rest of the app went dark.

The template already loads the theme system correctly (`theme.css` +
`partials/display_prefs.html` + the shared topbar), so the fix was pure CSS.

### 2. Changes

- **`static/css/attendance.css`** — converted to the same `:root` token block
  used by `meals.css` / `medical.css` (`--bg-main`, `--bg-card`, `--bg-subtle`,
  `--text-primary`, `--text-muted`, `--border-color`, `--shadow-card`,
  `--accent-primary`, `--accent-primary-hover`, `--accent-dark`, plus the
  success / warning / danger soft-border trios). Every hardcoded colour now
  references a token, so `theme.css`'s dark override flips the page in one shot:
  - body canvas, cards, the camera preview box (`.scanner-box`), the overall
    summary row and table separators → `--bg-main` / `--bg-card` / `--bg-subtle`
    / `--border-color`;
  - titles ("Class Attendance", "Scan Class QR", "My Attendance"), table
    headers and cells → `--text-primary`; subtitles, labels, scanner status,
    empty states and timestamps → `--text-muted`;
  - percentage badges (`pct-good/warn/bad`) → the semantic soft tokens;
  - manual code input (`.field-input`) and `::placeholder` now dark-adapt.
- **Dark-mode repairs:** `--accent-dark` reads as a light cream in dark mode,
  so the ink-inverted "Start Camera" button (`.btn-start`) gets an explicit
  `html[data-theme='dark']` override keeping a dark surface with white text
  (mirrors the existing `.btn-dark` / `.redeem-btn` repairs in `theme.css`).
- **No template change needed** — `/attendance/` already includes
  `partials/display_prefs.html`, which stamps the `dark` class + `data-theme`
  on `<html>` before first paint.

### 3. Verification

- Manual: toggling Dark Mode in Settings now repaints `/attendance/` with the
  dark canvas, slate cards and high-contrast text, matching `/meals/` and
  `/medical/`; light mode is pixel-identical to before (tokens resolve to the
  exact same hex values).
## 92. Two-Step Student Signup Verification (Django Gmail SMTP)

**Date:** 13 August 2026  
**Branch:** main

> **Superseded by §111** — the email OTP verification was removed; signup now
> creates the account immediately, signs the student in and redirects to the
> dashboard. The flow below is historical.

Self-registration now verifies the student's email address before any
account is created: step 1 collects the signup form and emails a 6-digit
code; step 2 confirms the code and only then persists the `User` +
`StudentProfile` and signs the student in.

### 1. SMTP / email configuration (`config/settings.py`)

- Gmail SMTP via TLS, env-driven (see `.env.example`):
  `EMAIL_BACKEND` (default `smtp.EmailBackend`), `EMAIL_HOST` (`smtp.gmail.com`),
  `EMAIL_PORT` (`587`), `EMAIL_USE_TLS` (`True`), `EMAIL_HOST_USER` /
  `EMAIL_HOST_PASSWORD` from the environment, `DEFAULT_FROM_EMAIL`
  (falls back to `EMAIL_HOST_USER` or `noreply@niterdash.com`).
- **Local convenience fallback:** when `DEBUG=True` and no `EMAIL_HOST_USER`
  is configured (fresh checkout), the backend switches to the console email
  backend — the code prints to the terminal so the whole flow stays testable
  without a Gmail app password. Production always uses the SMTP backend.
- `.env.example` documents the two required vars plus an App-Password link.

### 2. Two-step flow

- **Step 1 — `/signup/` (`signup_view`):** `SignUpForm` validates the fields
  (duplicate Student ID / email, password confirmation) exactly as before,
  but **no account is created**. A 6-digit code is generated
  (`secrets.randbelow`) and emailed via `send_mail`; the pending payload —
  validated form data, a **salted SHA-256 hash of the code** (raw code never
  touches the session), a 10-minute `expires_at`, and an attempt counter —
  is stashed in the session, then the student is redirected to step 2.
  An existing pending signup short-circuits back to step 2 (no re-entry).
  If the email cannot be sent (SMTP/auth/network), the pending payload is
  discarded and a friendly error is shown.
- **Step 2 — `/signup/verify/` (`verify_email_view`):** renders the code-entry
  screen with the pending address masked (`t**********t@…`). POST compares the
  submitted code against the session hash via constant-time comparison:
  - correct → the pending data is re-validated (duplicate ID/email race guard),
    the `User` + `StudentProfile` are created, the student is signed in, and
    the pending payload is cleared;
  - wrong → attempt counter increments; after **5** wrong attempts the pending
    signup is discarded (restart from step 1);
  - expired → pending cleared, "sign up again" message;
  - **Resend** (`action=resend`) issues a fresh code to the same address and
    emails it again. Security hardening: the new code hash is only committed
    after the send succeeds (a delivery failure never invalidates the previous
    code), and the attempt counter is deliberately **not** reset — an attacker
    with the session cookie can't interleave resends with wrong guesses to
    defeat the 5-attempt brute-force lockout;
  - **Use a different email** (`action=restart`) discards the pending payload
    and returns to the signup form, so a mistyped address is fixable without
    waiting for expiry.
- Code comparison uses `hmac.compare_digest` (constant-time); the raw code is
  salted with `SECRET_KEY` and hashed, so it never touches the session or logs.
- No pending payload → redirect back to `/signup/`.

### 3. UI

- `templates/verify_email.html` — masked-email code entry (monospace, 6-char
  numeric input with client-side digit stripping), inline errors, a resend
  button, and login fallback; reuses the shared auth card styling.
- `templates/signup.html` — subtitle now reads "Step 1 of 2" and the submit
  button says "Send Verification Code".
- `static/css/signup.css` — `.field-help`, `.verify-code-input`, and resend
  button styles.

### 4. Tests & verification

- `TwoStepSignupTest` (12 tests) + updated `AccountAndAdminPagesTest` /
  `SignUpFormTest`: step 1 emails exactly one code to the pending address and
  creates **no** rows; the raw code is never stored (only its hash); verify
  creates the user + profile and signs in; wrong code rejected (attempt
  counter); 5-wrong-attempt lockout discards the payload; expired code
  rejects; resend mails a fresh code that works **without resetting the
  attempt counter**; resend after lockout redirects to signup; restart
  discards the pending payload; duplicate created between the steps fails
  closed; verify page masks the email; no-pending redirect.
- **Full suite: 792 tests OK.** (Email verified through Django's locmem
  backend / `mail.outbox` in tests; console backend locally.)

---

## 94. Mobile Responsiveness (Calendar / Clock / Attendance) + Transport Payment Gateway Modal

**Date:** 13 August 2026  
**Branch:** main

Two passes: a mobile-responsiveness pass over the dashboard's Academic
Calendar + BST clock and the Attendance page, and the long-missing payment
gateway trigger on Transport ticket purchase ("Book Seat & Pay" now pops a
bKash / Nagad checkout modal instead of silently booking a free seat).

### 1. Mobile responsiveness

- **`static/css/dashboard.css`** — the Academic Calendar panel gets an
  `overflow-x: auto` guard on small screens (the ``w-full overflow-x-auto
  sm:overflow-visible`` equivalent) and the 7-column grid is compacted
  (smaller cell min-height/padding/day-number/dots/legend) so it fits below
  640px with no horizontal clipping. The clock card stacks the live time
  above the next-class block (`.clock-main` / `.clock-next` go full-width)
  and the 8-digit time + countdown scale down (34px / 20px, 30px below 400px)
  so nothing wraps awkwardly on <390px phones.
- **`static/css/attendance.css`** — `.att-layout` is now mobile-first single
  column (``grid-cols-1``) with the two-column scanner/stats split restored
  at `min-width: 900px` (``lg:grid-cols-2``). On small screens the cards get
  tighter padding, the QR camera box a 170px min-height, the action buttons
  share the row, the stats table uses smaller cell padding/font, and the
  recent check-ins rows wrap.
- **Verification:** headless Chrome at 380×740 — `/dashboard/`,
  `/attendance/` and `/transport/` all report `scrollWidth == clientWidth`
  (no horizontal overflow), the attendance cards stack, and the transport
  payment modal fits the viewport with zero console errors.

### 2. Transport payment gateway trigger

The "Buy Ticket" diagnosis was real: `transport.html`'s "Book Seat & Pay"
POSTed `/book-transport/` with **no** payment method, so every seat was
instantly `paid` and no checkout ever triggered. Now the button opens a
payment modal and the flow is:

1. `templates/transport.html` — new `.modal-backdrop` checkout modal
   (bKash / Nagad method pills, wallet number, TrxID, live order summary
   with route / departure / seat / **fare**); validation mirrors the meals
   modal (`01\d{9}` wallet, `[A-Za-z0-9-]{6,}` TrxID).
2. Confirm → `POST /book-transport/` with `payment_method` + `amount` →
   PENDING booking + `PaymentOrder` (`PINV-…`) — the existing paid-flow
   path, unchanged.
3. → `POST /checkout/` with `type=transport` + `booking_id` + wallet/TrxID.
   `_process_checkout` (core/views.py) now records the `PaymentTransaction`
   **and** fulfills the linked `PaymentOrder` via
   `payments.services.fulfill_payment_order` (amount must match the ticket
   fare → 400 otherwise), which issues the `TR-…` boarding QR token, marks
   the booking PAID, and pushes the "Transport payment confirmed"
   notification — the same connector the bKash/Nagad webhooks use.
4. The pass renders immediately in the Digital Boarding Pass card (QR SVG +
   token + route/seat/time) and the seat grid live-updates.

Robustness: a retry after a failed checkout reuses the pending booking
instead of re-booking the same seat (409 dead-end avoided); foreign users'
bookings are never activated; `TRANSPORT_DEFAULT_FARE` (৳30) covers the
legacy constant-only catalog while DB routes use their seeded per-route
`fare` (now exposed through `_transport_catalog()` → `transport-data` and
displayed on the route cards).

### 3. Files changed

- `static/css/dashboard.css`, `static/css/attendance.css`
- `templates/transport.html`, `static/css/transport.css`
- `core/views.py` (`_transport_catalog` fare, `transport_dashboard`,
  `_process_checkout` transport fulfillment)
- `payments/tests.py` (4 new tests: fulfill-on-checkout, record-without-
  booking, foreign-booking guard, amount-mismatch rejection)

### 4. Tests & verification

- `python manage.py check` clean; **full suite 795 tests OK** (was 792).
- Browser e2e @ 380×740: student login → seat select → payment modal →
  bKash TrxID submit → boarding pass with `TR-…` QR token renders, zero
  console errors; seat-required validation toast intact.

---

## 95. Medical API Payload Alignment — Booking Keys + Consultation Lookup

Aligned the medical booking/consultation frontend with what the backend
serializers actually expect, so "all fields selected" forms no longer fail
with 400s and "Start Consultation" no longer 404s.

### 1. Appointment booking payload (`book_appointment`, core/views.py)

- **Doctor id resolution:** the endpoint already honoured the legacy
  constant catalog (`DOCTORS`) for a posted `doctor` id. It now also
  resolves **live-DB `Doctor` rows** (`pk=int(id), is_active=True`) — the
  same catalog the booking form renders — so an id-based client posting a
  real record id gets the doctor name server-side.
- **`symptoms` alias:** `reason` remains canonical, but the
  `symptoms` key is now accepted as an alias (`reason` → `symptoms`
  fallback), honouring the documented `{doctor, appointment_date,
  time_slot, symptoms}` contract.
- **Frontend (`templates/medical/booking.html`):** every `<option>` in the
  doctor `<select>` now carries `data-doctor-id`; the submit handler posts
  an **explicit, aligned payload** — `doctor` (record id), `doctor_name`,
  `appointment_date` (`YYYY-MM-DD`), `time_slot`, `symptoms` — instead of
  serializing raw form fields, and field errors clear the moment each
  control is fixed (existing `change`/`input` listeners + generic-alert
  auto-hide when all required fields are valid).

### 2. Start-consultation lookup (`medical_chat_start`, core/views.py)

- **`appointment_id` alias:** the canonical `appointment_id` key is
  accepted, plus an `appointment` alias for clients posting the record PK
  under that name; both resolve the same `MedicalAppointment` row
  (owner-scoped 404 otherwise).
- **Frontend:** the "Choose an appointment…" dropdown already bound
  `value={{ appointment.id }}` (the record primary key, never the
  concatenated label); the start handler posts `appointment_id` and now
  **clears any active error banner on selection change** and after a
  successful start, opening the consultation thread window immediately.

### 3. Files changed

- `core/views.py` (`book_appointment`, `medical_chat_start`)
- `templates/medical/booking.html` (payload build, `data-doctor-id`,
  error-banner clearing)
- `core/tests.py` (4 new regression tests: live-DB doctor id,
  symptoms alias, appointment alias param — plus the pre-existing
  legacy-id test)

### 4. Tests & verification

- `python manage.py check` clean; **full suite 799 tests OK** (was 795).
- Browser e2e: student login → book with Dr. Sarah Smith (200, inline
  success, appears in Upcoming Appointments) → "Start Consultation"
  without selection shows the choose-first banner → selecting clears it
  instantly → start opens `Consultation #…` thread window; zero console
  errors.

---

## 96. Teacher Management + QR Email Dispatch + Attendance Report Emails

Closed the teacher→QR→report email loop for the QR Attendance module:
admins register course teachers, dispatch the class QR code by email when a
session opens, and send (or auto-send on close) the styled attendance
report.

### 1. Teacher Management (Admin)

- **Model (`core/models.py`)**: new `Teacher` — `name`, `email` (unique),
  `department` (FK → `Department`), `designation`, `phone_number`
  (optional), `courses` (M2M → `Course`), `is_active`, timestamps.
  `Teacher.for_course(code)` resolves the active teacher for a course code
  (case-insensitive) — the lookup the email dispatch uses.
- **Migration `0038_teacher_and_more`** (plus Django's automatic
  attendance index/field normalizations).
- **Admin UI** (`/dashboard/admin/teachers/`): new **Teachers** tab in the
  admin sidebar. Add/edit form (name, email, department, designation,
  phone, active, assigned-course checkboxes) + a registered-teachers table
  with Edit / Delete actions, wired to the CRUD API.
- **API**: `GET/POST /api/admin/teachers/` (list / create),
  `POST/DELETE /api/admin/teachers/<id>/` (update / delete) —
  `admin_required`, duplicate email → 409, validation errors → 400.
  Registered in the Django admin (`TeacherAdmin`, `filter_horizontal`
  courses).

### 2. QR Code Email Dispatch

- **`services/attendance_email.py`**: `attendance_qr_png(session)` renders
  the `ATT|<token>` payload to a PNG via the **`qrcode`** library (+Pillow,
  newly pinned `qrcode[pil]>=7.4,<9.0`); `email_qr_to_teacher` attaches the
  QR image and emails course + session token + expiry to the teacher using
  the configured Django email backend (Gmail SMTP / console fallback).
- **Button** "Email QR to Teacher" on the admin attendance live panel →
  `POST /api/attendance/sessions/<token>/email-qr/` (admin-only; resolves
  the session by token or numeric id; 404 when no teacher is assigned to
  the course, 502 on SMTP failure).

### 3. Attendance Report Email

- **`attendance_report(session)`**: builds the per-session roster (every
  student who attended any session of the course — Present with check-in
  timestamps, others Absent), a styled inline-CSS **HTML** summary and a
  **CSV** attachment.
- **Button** "Send Report to Teacher" →
  `POST /api/attendance/sessions/<token>/email-report/` (admin-only).
- **Auto-dispatch**: closing a session now best-effort emails the report to
  the assigned teacher automatically (`report_emailed_to` in the close
  response, surfaced in the close toast); a missing teacher or SMTP failure
  never blocks the close.

### 4. Files changed

- `core/models.py`, `core/migrations/0038_teacher_and_more.py`,
  `core/admin.py`, `core/views.py`, `core/urls.py`,
  `core/context_processors.py`
- `services/attendance_email.py` (new), `services/__init__.py`
- `templates/admin/teachers.html` (new), `templates/admin/attendance.html`,
  `templates/admin/admin_base.html`
- `requirements.txt` (`qrcode[pil]`)
- `core/tests.py` (3 new test classes: TeacherModel, AdminTeachersApi,
  AttendanceEmailDispatchApi)

### 5. Tests & verification

- `python manage.py check` clean; **full suite 826 tests OK** (was 799).
- Browser e2e: admin login → create teacher (assigned CSE-1101) → generate
  QR session → "Email QR to Teacher" and "Send Report to Teacher" both
  succeed with toasts → close auto-emails the report; zero console errors.


## 97. Emergency Announcement System — Banner + Siren + Mobile Push

Campus-wide emergency broadcasting: an admin triggers a live alert from the
Admin Overview and every dashboard tab shows a severity-styled banner (and,
for CRITICAL, a full-screen overlay) with an optional looping siren — plus an
opt-in Firebase push fan-out for the mobile app.

### 1. Backend & model

- **Model (`core/models.py`)**: new `EmergencyAlert` — `title`, `message`,
  `severity_level` (CRITICAL / WARNING / INFO), `play_alarm_sound`,
  `is_active`, `created_by` (FK → admin), `created_at`, `resolved_at` /
  `resolved_by`. **Only one alert is live at a time** — triggering a new
  one retires the previous. `severity_lower` helper for client styling.
- **Migration `0039_emergencyalert`**; registered in the Django admin.
- **API**: `POST /api/admin/emergency/trigger/` (create + activate +
  broadcast), `POST /api/admin/emergency/resolve/` (deactivate + stamp
  resolution), `GET /api/emergency/active/` (student-side poll — returns
  the live alert or `null`). Trigger/resolve are `admin_required`; the
  active poll is `login_required`. Validation: missing title/message → 400,
  unknown severity → 400, title > 200 chars → 400.

### 2. Real-time delivery

- **WebSocket** (`ws/emergency/`): new `EmergencyConsumer` joins the global
  `emergency_alerts` group (auth required, anonymous rejected);
  `broadcast_emergency(payload)` fans trigger/resolve events out to every
  open tab. Channel-layer outages degrade gracefully to poll-only (never
  raise).
- **Bell fan-out** (`core.tasks.broadcast_emergency_alert`): one urgent
  `Notification` row per active user + live push, off the trigger request
  path (Huey immediate in dev/tests).
- **Mobile push** (`services/emergency_push.py`): lazy firebase-admin
  integration — high-priority FCM message (topic `emergency_alerts`) with
  `data.type = EMERGENCY_ALERT`, severity, `emergency_siren.wav` sound,
  critical-channel Android config and `apns-priority: 10`. Reads
  `FIREBASE_CREDENTIALS` (inline JSON or path); **unconfigured → graceful
  no-op** (`push_sent: 0`), never fatal. firebase_admin need not be
  installed to run the portal.

### 3. Student overlay + siren

- `templates/partials/emergency_banner.html` included in **every shell**
  (topbar, base, admin_base, club_base) for authenticated users: polls
  `/api/emergency/active/` every 10 s + listens on `ws/emergency/` (instant
  trigger/resolve). Renders a pulsating severity-styled fixed banner on ALL
  dashboard pages (`/meals/`, `/transport/`, `/medical/`, `/attendance/`,
  …), a full-screen overlay for CRITICAL alerts (dismissible, banner
  persists), and loops the siren when `play_alarm_sound` is set — silenced
  per-alert via the "Silence alarm" button, stopped on resolve. Content is
  set via `textContent` (no XSS).
- **Siren audio**: `static/audio/emergency_siren.wav` (4 s two-tone 660/880
  Hz sweep, 44.1 kHz 16-bit mono, loop-friendly) generated with the Python
  stdlib (`wave` + `math` — no ffmpeg on the box). WAV plays natively in
  every browser; the spec's own push payload references
  `emergency_siren.wav`. Browsers gate autoplay behind a first user
  gesture — the driver retries on the next pointer/key event (bound once
  per page).

### 4. Admin broadcast console

- New **Emergency Siren / Broadcast** card at the top of the Admin Overview
  (`/dashboard/admin/`): live status chip (All clear ↔ LIVE ALERT with
  pulse), the active alert's title/severity/timestamp/message, a red
  **Trigger Emergency Alert** button opening a confirmation modal (title,
  instructions textarea, severity select, play-alarm toggle) and a **Clear
  / Resolve Emergency** button (enabled only while an alert is live). The
  console polls the active endpoint every 8 s, so it stays in sync with
  alerts triggered elsewhere.

### 5. Files changed

- `core/models.py`, `core/migrations/0039_emergencyalert.py`,
  `core/admin.py`, `core/views.py`, `core/urls.py`,
  `core/context_processors.py`, `core/consumers.py`, `core/routing.py`,
  `core/tasks.py`
- `services/emergency_push.py` (new), `config/settings.py`
  (`FIREBASE_CREDENTIALS`)
- `static/css/emergency.css` (new), `static/audio/emergency_siren.wav`
  (new), `templates/partials/emergency_banner.html` (new),
  `templates/admin/overview.html` (console + modal),
  `templates/partials/topbar.html`, `templates/base.html`,
  `templates/admin/admin_base.html`, `templates/club/club_base.html`
- `core/tests.py` (3 new test classes: EmergencyAlertModel,
  EmergencyBroadcastApi, EmergencyConsumer)

### 6. Tests & verification

- `python manage.py check` clean; **full suite 851 tests OK** (was 826).
- Browser e2e: admin login → trigger CRITICAL alert with siren → student
  /meals/ tab shows the pulsating banner + full-screen overlay (acknowledge
  keeps the banner) → resolve from the admin console → banner clears across
  tabs; zero console errors.

---

## 98. Emergency Alert Modal — Auto-Open / Unclosable State Fix

### Overview

The "Trigger Emergency Alert" confirmation modal on the Admin Overview
(`/dashboard/admin/`) popped up immediately on page load and could not be
dismissed — the ✕ close icon, Cancel button, backdrop click, and Escape key
all appeared to do nothing. Toast "Emergency alert broadcast to the campus."
notifications could also surface without the admin pressing **Confirm &
Broadcast**, because the always-visible modal made accidental submits
possible (typing + Enter inside the open form fires the POST).

### Root cause

`static/css/admin_dashboard.css` declared
`.emergency-modal { … display: flex; … }`. The modal markup ships with the
HTML `hidden` attribute and the page JS toggles it (`closeModal()` sets
`modal.hidden = true`), but an author rule that sets `display` always wins
over the browser's UA `[hidden] { display: none }` rule — so the modal was
permanently visible and setting `hidden = true` had no visual effect. Same
class of bug as the medical booking `.field-error` fix (§87,
`.field-error[hidden]` in `medical.css`).

### Fix

- `static/css/admin_dashboard.css`: added
  `.emergency-modal[hidden] { display: none; }` so the `hidden` attribute
  (initial state and every `closeModal()`) actually hides the modal, while
  `openModal()` (`hidden = false`) still reveals it via `display: flex`.
- No JS changes were needed — the ✕ / Cancel / backdrop / Escape dismiss
  handlers and the submit-only trigger already existed; they were just
  fighting a CSS rule that ignored the `hidden` attribute.
- `core/tests.py`: new regression guard
  `EmergencyBroadcastApiTest.test_emergency_modal_starts_hidden_and_css_respects_hidden`
  — asserts the rendered overview ships `id="emergency-modal" hidden` and
  that `admin_dashboard.css` contains `.emergency-modal[hidden]`.

### Tests & verification

- `python manage.py check` clean.
- Full suite passes: **852 tests OK** (was 851).
- Browser e2e: `/dashboard/admin/` loads clean with no modal; clicking
  "Trigger Emergency Alert" opens it; Cancel / ✕ / backdrop / Escape close
  it seamlessly; only **Confirm & Broadcast** fires the POST + success
  toast.

---

## 99. Test-Suite Redis Isolation — In-Memory Channel Layer Under the Test Runner

### Problem

Two tests failed intermittently with `ConnectionError: redis is down`
(850/852 passed). `config/settings.py` picked the `channels_redis` backend
whenever a `REDIS_URL` was configured **and** the startup ping probe
succeeded — so with a local Redis up at boot that later dropped (or became
flaky), the WebSocket/consumer tests (`NotificationConsumerTest`,
`EmergencyConsumerTest`, `MedicalChatConsumerTest`, …) bound to a real Redis
and died mid-suite instead of staying deterministic. The same class of
failure could hit CI if a Redis ever reached the runner environment.

### Fix (mock Redis in the test environment)

- `config/settings.py`:
  - New `_running_tests()` helper — true while the test suite executes
    (`'test' in sys.argv` for `manage.py test`, or the explicit `TESTING`
    environment variable).
  - `CHANNEL_LAYERS` is forced to
    `channels.layers.InMemoryChannelLayer` whenever `_running_tests()` — the
    Redis probe is skipped entirely under the test runner, so a
    reachable-but-flaky Redis can never leak into the consumer tests.
  - `HUEY.immediate` also honors `_running_tests()`, keeping the background
    task queue synchronous in-process during tests even if the suite is run
    with `DEBUG=False` and a `REDIS_URL` set.
- `.github/workflows/ci.yml`: the check and test jobs now set
  `TESTING: "true"` (double-locking the in-memory guarantee) and the
  workflow documents that no Redis service is needed.
- `core/tests.py`: new regression guard
  `TestChannelLayerConfig.test_channel_layer_is_in_memory_during_tests` —
  asserts the configured channel layer is in-memory while the suite runs.

### Tests & verification

- `python manage.py check` clean.
- Full suite passes: **853 tests OK** (was 852 — +1 regression guard).
- Verified the guard end-to-end: with `REDIS_URL` set and a dead Redis, the
  settings still resolve to `InMemoryChannelLayer` under the test runner,
  and the WebSocket/consumer classes pass without touching Redis.

---

## 100. CI Hardening — Pytest-Proof Channel Layer + dash-data / Huey Regression Guards

Follow-up hardening pass for the two GitHub-Actions failure classes reported
against `core/tests.py` (`DashboardCalendarGridTest` and channel-layer Redis
errors). Both were already fixed on `main` (§91 shipped the `dash-data`
`|json_script` embedding, §99 forced the in-memory channel layer under the
test runner); this pass makes the guarantees airtight for **any** test runner
and pins them with regression guards.

### 1. `_running_tests()` now detects pytest too (`config/settings.py`)

- The helper previously returned true for `manage.py test` (`'test' in
  sys.argv`) or the explicit `TESTING` env var. It now also checks
  `PYTEST_CURRENT_TEST` (set by pytest for the duration of a run), so the
  in-memory channel layer + Huey `immediate` overrides hold even if the suite
  is ever invoked through pytest or another runner that doesn't put `test`
  in `sys.argv` — a reachable-but-flaky Redis can never leak into consumer
  tests again.

### 2. Stronger regression guards (`core/tests.py`)

- `DashboardCalendarGridTest.test_embedded_calendar_json_parses_and_has_grid_metadata`
  now also asserts the `dash-data` script tag renders with
  `type="application/json"` and that its body contains no `</script>` or
  `&quot;` — pinning the `|json_script` rendering so a regression to
  `{{ dash_data }}` or `|safe` is caught immediately (`JSON.parse` would
  fail and the calendar grid would go blank).
- `TestChannelLayerConfig` gains
  `test_huey_queue_is_immediate_during_tests` — asserts `HUEY['immediate']`
  is `True` under the test runner, so background tasks (note analysis,
  emergency alert fan-out) never dispatch to a Redis queue that may be
  absent or flaky.

### Tests & verification

- `python manage.py check` clean.
- Full suite passes: **854 tests OK** (was 853 — +1 regression guard).
- Browser e2e unchanged: dashboard calendar + clock render from the embedded
  JSON; emergency/notification flows still push over the in-memory layer
  during tests.

---

## 101. dash-data Dashboard JSON Embedding — Verified on main

**Date:** 14 August 2026  
**Branch:** main

Verification pass for the two `DashboardCalendarGridTest` failures reported
against `core/tests.py` (`test_clock_label_renders_from_dict`,
`test_embedded_calendar_json_parses_and_has_grid_metadata`):
`_dash_script()` asserted the rendered dashboard HTML was missing the
`id="dash-data"` script tag.

### Finding

- The `dash-data` script tag is **present** in `templates/dashboard/home.html`,
  rendered from the view's `dash_data` dict via Django's
  `{% json_script 'dash-data' %}` filter (the §91 fix) — no `{{ |safe }}` or
  pre-serialized-string regression.
- Both regression guards pass locally and the full suite is green under the
  exact CI invocation (`TESTING=true python manage.py test`): **854 tests OK**.
- **No code change was required** for the tag itself — but see §102: the
  same CI log's `dash-data script tag missing` failures were eventually
  traced to an `ALLOWED_HOSTS` mismatch, not a missing tag, and that fix
  **did** require a code change.

## 103. Emergency Alarm Persistent Silence + WYSIWYG Student-View Editor Overlay

**Date:** 14 August 2026  
**Branch:** main

Two features shipped together: (1) the emergency banner's "Silence alarm" now
actually stays silenced across pages, and staff can resolve from the banner
itself; (2) the Website Builder's visual editor becomes a full WYSIWYG
student-view overlay — click-to-edit text on the canvas, a floating style
toolbar, Save Changes / Publish Page wired to a new per-page endpoint.

### 1. Emergency alarm — persistent silence + banner resolve

- **Root cause:** "Silence alarm" only stopped the siren in-memory
  (`silencedAlertId` was a page-scoped variable), so the banner + siren came
  back on every page navigation — the exact "stays active across admin pages"
  report.
- **Fix (`templates/partials/emergency_banner.html`):**
  - The silenced alert id is now persisted to `localStorage` under
    `emergency_alarm_silenced`; on load the driver reads it back, so silence
    survives navigation for that alert.
  - Silencing hides the **banner + overlay** too (not just the siren) and
    flips the button to "Alarm silenced"; clicking again un-silences.
  - A **new alert id re-arms** the alarm automatically (the old silenced id is
    cleared), and resolving the alert clears the localStorage key.
  - **Staff get a "Resolve alert" button** right on the banner (staff-only,
    `{% if user.is_staff %}`) that POSTs to `/api/admin/emergency/resolve/`
    with CSRF — ends the emergency site-wide for everyone from any page.
- `static/css/emergency.css`: `.emergency-resolve-btn` styling.

### 2. Website Builder — WYSIWYG student-view editor overlay

- **Entry points:** the builder dashboard's "Edit Page" and the admin CMS
  table's "Edit" now open `/builder/visual/<slug>/` (the student-layout
  editor) instead of the block manager; "Block Manager" stays one click away
  on the dashboard. The admin overview's "Website Builder" tile still lands
  on the builder console.
- **Canvas:** the editor renders the real student page (topbar + blocks) in a
  same-origin iframe — the exact layout visitors see.
- **Inline editing:** double-clicking text inside an `html`-type block makes
  it `contenteditable` on the canvas; edits are captured into a dirty map and
  sent on save. (Structured blocks stay style-editable; their content lives
  in `content_json` and is edited via the block library.)
- **Floating style toolbar (`#wysiwyg-toolbar`):** clicking any block pops it
  up near the section — font size, text colour, background colour, and
  left/center/right alignment, applied live to the section via its
  `style_json`. Includes an "Edit text" button and Escape/✕ dismissal.
- **Top bar:** "Save Changes" POSTs `{blocks: [...]}` (content + style)
  plus the page CSS to the new endpoint; "Publish Page" POSTs
  `is_published: true`. Both go to
  **`POST /api/builder/pages/<page_id>/save/`**.
- **New endpoint (`builder_page_wysiwyg_save`):** accepts
  `{blocks: [{element_id, content_html?, style_json?, block_type?,
  content_json?, order?}], is_published?}`; every block reuses the shared
  `_save_content_block_data` path (sanitized + partial-update safe), and
  `is_published` toggles the page's live state. Gated by
  `@change_editablepage_required`.
- `templates/builder/editor.html`, `static/js/builder/editor.js`,
  `static/css/builder_editor.css`, `core/views.py`, `core/urls.py`.

### Tests & verification

- `python manage.py check` clean; full suite **869 tests OK** (was 854).
- New guards: `EmergencyBannerSilenceTest` (5) — localStorage persistence,
  visual hide, new-alert re-arm, staff-resolve vs student banner;
  `BuilderWysiwygSaveApiTest` (12) — block content/style save, html-block
  save, sanitizer, publish toggle, 403/302/404 guards, editor chrome render,
  edit-link rewiring.

---

## 104. Global News & Search Widget (Student + Admin Dashboards)

**Date:** 14 August 2026  
**Branch:** main

A Global News & Search section on both dashboards — top headlines from
NewsAPI.org on the student dashboard and the admin overview, with a keyword
search box that queries a new JSON endpoint. The widget must never take a
dashboard down over an external service, so every failure mode degrades to
deterministic sample headlines.

### 1. Backend service (`core/news_service.py`)

- `fetch_global_news(query=None, category="technology", page_size=12)`:
  - No query → `https://newsapi.org/v2/top-headlines` (category feed);
    query → `https://newsapi.org/v2/everything` (keyword search).
  - Reads `NEWS_API_KEY` from the environment; unset/placeholder
    (`dummy_key`) → fallback feed, no network.
  - 5s timeout; any exception, non-200 (rate limit 429 included) → fallback
    feed. 200 responses are normalized to a stable shape
    (`title / description / url / image / source / published_at`) with blank
    titles and non-dict entries dropped.
- `get_fallback_news_data(query)` — deterministic sample headlines in the
  same article shape; ``query`` flavors the titles so a degraded search still
  looks relevant.
- **Test-run short-circuit** (`_is_test_run()`, mirrors
  `config.settings._running_tests`): under `manage.py test` / `TESTING` /
  pytest the fetch is skipped entirely — the suite stays fast and
  network-free, and every dashboard render test is deterministic.
- Uses `logging` (project convention), not `print`.

### 2. Views & API

- `student_dashboard` and `admin_dashboard` now pass `news_articles`
  (always a list) into their templates.
- **`GET /api/news/search/?q=…`** (`api_news_search`) — public JSON search:
  `{status: "success", data: [articles]}`; `q` optional (headlines when
  omitted); non-GET → 405. Route: `core/urls.py`.

### 3. UI (shared partial + CSS)

- `templates/partials/global_news.html` — the same section on both
  dashboards: search bar + responsive article-card grid. Server-rendered on
  load; the search box fetches `/api/news/search/` client-side and
  re-renders the grid (all API strings HTML-escaped before innerHTML,
  non-http(s) links dropped).
- Included in `templates/dashboard/home.html` (after the feeds row) and
  `templates/admin/overview.html` (after the Latest Builder Pages row).
- `static/css/news.css` — self-contained card styling using CSS-variable
  fallbacks so it matches both the student theme and the admin tokens.

### Tests & verification

- Full suite **880 tests OK** (was 869; +11 new).
- `GlobalNewsServiceTest` (6) — test-run short-circuit, dummy-key fallback,
  network-error fallback, rate-limit fallback, article normalization,
  everything-endpoint params.
- `GlobalNewsApiTest` (3) — search returns articles, no-query headline feed,
  405 on POST.
- `GlobalNewsDashboardTest` (2) — widget renders on the student dashboard and
  the admin overview.

---

## 105. `seed_demo_data` — Realistic NITER Demo Dataset (run against Supabase)

**Date:** 14 August 2026  
**Branch:** main

A management command that populates a realistic NITER campus mock dataset —
run against the live Supabase database on request:

    python manage.py seed_demo_data

### New model: `MealMenu` (migration `0040_mealmenu`)

The cafeteria daily menu had no DB home — added a small model
(`day` / `meal_type` / `items` / `is_active`, unique on day+meal_type) so the
breakfast / lunch / evening-snacks menu is actually seedable.

### Dataset seeded (all via `get_or_create` — idempotent, re-run safe)

- **Accounts & profiles** (password `password123`; existing users are never
  touched — passwords never reset, only a blank email gets filled):
  `admin@niter.edu.bd` (superuser), `dr.chen@niter.edu.bd` +
  `prof.rahman@niter.edu.bd` (staff + `Teacher` rows), `kn8trix@niter.edu.bd`
  (Ahsanul Haque, EEE, `2026-EEE-01`), `student2@niter.edu.bd` (CSE).
- **Departments** CSE / EEE (get_or_create by code) and **Teachers** linked
  to their courses.
- **Transport**: 3 routes — NITER Campus ↔ Mirpur 10 / Farmgate (Bus #01,
  07:30 AM & 04:30 PM), ↔ Uttara / Gazipur (Bus #02, 08:00 AM & 05:00 PM),
  ↔ Baipal / Nabinagar Shuttle (Bus #03); 3 drivers; 3 paid seat bookings
  with boarding QR tokens.
- **Medical**: Dr. Michael Chen (General Physician) + Dr. Emily Johnson
  (Dentist) — **converged via `update_or_create`** to clinic hours
  Sun–Thu 09:00 AM – 05:00 PM (a data migration had seeded them with other
  values); 3 appointments (confirmed / pending / completed).
- **Cafeteria**: 3 `MealMenu` lines (breakfast / lunch / evening snacks);
  2 active `MealSubscription`s; 4 paid digital `MealTicket`s
  (`#MEAL-1001/1002/2001/2002`).
- **Academic**: 3 courses (EEE-2101, CSE-1101, EEE-3105) + 5
  `CourseMaterial` rows (PDF notes, lab manual, lecture slides, study guide).
- **Clubs**: NITER Computer Club (NCC) + NITER Robotics Society; 2 upcoming
  `ClubEvent`s; 3 published `Notice` announcements.

### Notes

- Existing migration-seeded rows (3 generic transport routes, 4 default
  doctors, 6 default clubs) are left in place; the command only adds its own
  named rows and converges the two named doctors.
- `timezone.now().date()` is used (not `timezone.localdate()`) because the
  project runs `USE_TZ=False`.

### Tests & verification

- Full suite **883 tests OK** (was 880; +3 new `SeedDemoDataCommandTest`
  guards — full dataset created, idempotent re-run, existing users never
  touched).
- Executed against Supabase: migration `0040_mealmenu` applied, seed run
  twice (second run all-skipped except the doctor convergence) — verified
  with read-only row counts.

---

## 106. Builder Preview Iframe Fix — X-Frame-Options SAMEORIGIN on Public Pages

**Date:** 14 August 2026  
**Branch:** main

**Symptom:** the builder's live preview iframe refused to load the page
("Firefox Can't Open This Page" / blank frame) on `/builder/visual/<slug>/`.

**Root cause:** `config/settings.py` sets the global `X_FRAME_OPTIONS =
'DENY'` (`XFrameOptionsMiddleware`), so the public page served at
`/page/<slug>/` — which the editor embeds in a same-origin `<iframe>`
(`templates/builder/editor.html` `#page-preview`, src=`{% url 'editable_page'
page.slug %}`) — was refused by the browser.

**Fix (`core/views.py`):** decorated `editable_page_view` with
`@xframe_options_sameorigin` (from `django.views.decorators.clickjacking`).
The middleware leaves a response's existing `X-Frame-Options` header alone, so
public builder pages now respond with `X-Frame-Options: SAMEORIGIN` — the
same-origin editor iframe loads, while cross-origin clickjacking stays
blocked (DENY is still the default for every other view).

**Regression guard:** `EditablePageRenderTest.test_page_allows_same_origin_framing`
asserts the header is exactly `SAMEORIGIN`.

---

## 107. Builder Edit Page — Auto-Opening "Delete Section" Modal Fix

**Date:** 14 August 2026  
**Branch:** main

**Symptom:** loading `/builder/edit/<slug>/` immediately showed the "Delete
Section" confirmation modal stacked on top of the "Block Library" modal,
with no click.

**Root cause:** same defect class as the §98 emergency modal —
`.pb-modal-backdrop { display: grid; }` in `static/css/builder_page.css`
overrides the `hidden` attribute, so **both** backdrops rendered on load. The
delete-confirm backdrop sits later in the DOM and painted over the library
backdrop (identical `z-index`, later element wins). The JS was never the
problem: `openDeleteConfirm` is only reachable from an explicit trash-icon
click, and `closeAllModals()` already exists.

**Fix:**
- `static/css/builder_page.css`: added `.pb-modal-backdrop[hidden] {
  display: none; }` so the `hidden` attribute beats the `display: grid` rule.
- `static/js/builder/page_manager.js`: hardened init — both modals are
  explicitly forced to `hidden` and `pendingOrder` / `pendingDelete` are
  cleared on load, so a future CSS regression can never auto-open a dialog.

**Regression guard:** `BuilderPageManagerTest.test_modals_start_hidden`
asserts both backdrops render with the `hidden` attribute.

---

## 108. Builder Routes Locked to the Admin Console Layout

**Date:** 14 August 2026  
**Branch:** main

**Goal:** every admin route (`/dashboard/admin/*`, `/builder/*`,
`/builder/edit/*`, `/builder/visual/*`) must render the dark Admin Console
sidebar ("Niter Hub / Admin Console") — never the student top navigation.

**Audit result:** `/dashboard/admin/*` already extended
`admin/admin_base.html`. The one violation was the builder **console** at
`/builder/` — `templates/builder/dashboard.html` included the **student**
`partials/topbar.html`. The two full-screen editors (`/builder/visual/*`
`editor.html`, `/builder/edit/*` `edit_page.html`) are standalone
full-height workspaces (`body { height: 100vh }`, `calc(100vh - topbar)`
canvases + iframe previews) with their own admin tooling and **no** student
navigation — wrapping them in the 256px sidebar would break their layout
math, so they were kept full-screen (decision confirmed with the user).

**Changes:**
- `templates/builder/dashboard.html` — now `{% extends "admin/admin_base.html" %}`:
  the dark sidebar with the Website Builder / CMS nav item highlighted
  (`admin_section='content'` added to the `builder_dashboard` view), the
  admin sticky header, emergency banner + toasts — student topbar removed.
  The create-page modal, inline script, and `builder.css` (loaded via
  `{% block extra_head %}`) are unchanged.
- Both editor top bars now carry an **Admin Console** pill badge
  (`.admin-console-badge`, `#2B2927` matching the sidebar chrome) so the
  full-screen editors read unmistakably as admin tooling.

**Regression guard:** `test_builder_dashboard_uses_admin_console_layout`
asserts the admin sidebar renders, `partials/topbar` / `#avatar-btn` /
student topbar ids are absent.

---

## 109. Visual Builder — Inline Canvas Editing + Active-Block Sync + Publish Flow

**Date:** 14 August 2026  
**Branch:** main

Polished the `/builder/visual/<slug>/` editor so every canvas element is
directly editable and stays in sync with the left inspector. The §103
WYSIWYG overlay already shipped most of the machinery — this pass closed
the binding gaps and matched the requested UX/toast wording.

### What was already there (verified, no rework)

- **Save / Publish endpoint:** `POST /api/builder/pages/<page_id>/save/`
  (`builder_page_wysiwyg_save`) accepts `{page_id, blocks, is_published?}` —
  blocks persist through the shared sanitizing `_save_content_block_data`
  path and `is_published` toggles the live state while bumping `updated_at`.
  The requested `/builder/api/save/` + `/builder/api/publish/` URL shapes are
  served by this single endpoint (verified by `BuilderWysiwygSaveApiTest`).
- **Canvas editing:** double-click text on an `html` block → `contenteditable`;
  single click → floating style toolbar (font size / text colour /
  background / alignment) with an "Edit text" button.
- **Sidebar → canvas:** typing in the Active Blocks Content (HTML) textarea
  or the Align / Color / Font size / Padding inputs updates the matching
  `[data-editable-id]` element in the iframe in real time.

### Gaps closed (`static/js/builder/editor.js`)

- **Active-element outline:** the selected canvas element now shows the spec'd
  `outline: 2px dashed #3b82f6` (was solid dark gray).
- **Canvas → sidebar binding:** typing on the canvas now mirrors straight
  into the Active Blocks Content (HTML) textarea (bidirectional — previously
  only sidebar → canvas).
- **Unified active block:** showing the floating toolbar now also drives the
  inspector `.active` highlight + canvas outline through one `selectItem`
  path, so canvas click, sidebar click, and toolbar selection all agree on
  the same active block.
- **Toasts:** Save Changes → "Draft Saved!", Publish Page →
  "Page Published Successfully!".

### Tests & verification

- Full suite **884 tests OK** (was 883; +1 new `test_publish_bumps_updated_at`
  asserting publishing touches the page's `updated_at`).
- `editor.js` syntax-checked; existing `BuilderWysiwygSaveApiTest` (12)
  unchanged and green.

---

## 110. Global News Tab + Emergency Resolve Audit + Student Mobile Pass

**Date:** 14 August 2026  
**Branch:** main

### 1. Emergency siren clear / resolve — verified, no change needed

The requested behaviour already shipped (§97/§98/§103) and was audited:

- `api_emergency_resolve` (`POST /api/admin/emergency/resolve/`) sets
  `is_active=False`, stamps `resolved_at`/`resolved_by`, and broadcasts a
  `resolve` event.
- The banner's staff **Resolve alert** button and the Admin Overview's
  **Resolve** button both POST to that endpoint and immediately hide the
  banner/overlay + stop the siren (`clearAlert()` / `renderActive(null)`) —
  no refresh needed; the WebSocket broadcast clears every open tab.
  (The requested `/api/emergency/clear/` URL shape is covered by this
  endpoint.)

### 2. Global News tab in the student portal navbar

- New **Global News** pill in `templates/partials/topbar.html` (desktop
  `.navlinks` + mobile profile links, after Clubs) with an FA newspaper icon
  and `active` state for `active='news'`.
- New student-facing page **`/news/`** (`news_page` view + `templates/news.html`)
  reusing the shared `partials/global_news.html` widget — headline feed +
  client-side keyword search — with the standard portal chrome
  (topbar / intro / shell). Route: `core/urls.py` (`name='news'`).

### 3. Student pages mobile pass

- `static/css/dashboard.css`: extended the 640px breakpoint — tighter
  `panel-card`/`widget-card` padding, `panel-head` wraps (title + "View All →"
  never squeeze), compact `notice-item`/`quick-grid` spacing. The news grid
  was already responsive (`news.css`); dashboards already collapse
  `split-grid`/`main-grid`/`summary-grid` below 1024px.

### Tests & verification

- Full suite **all green** (885 tests; +1 `test_news_page_renders_widget_with_active_pill`).
- `UnifiedHeaderTest` now covers `/news/` in its shared-header matrix and
  `Global News` in the nav-link set; the active-pill map includes `/news/`.

---

## 102. dash-data CI Failure — Real Root Cause: ALLOWED_HOSTS vs localhost

**Date:** 14 August 2026  
**Branch:** main

Follow-up to §101: GitHub Actions still failed the two `DashboardCalendarGridTest`
regression guards (`dash-data script tag missing`) even though the tag is
present on `main`. This pass found and fixed the real root cause.

### Root cause

- `_dash_script()` requested the dashboard with `HTTP_HOST='localhost'`.
- **Locally** `.env` sets `ALLOWED_HOSTS=localhost,127.0.0.1`, so the test
  runner's `ALLOWED_HOSTS` (which becomes `['localhost', '127.0.0.1',
  'testserver']`) permits `localhost` and the dashboard renders.
- **In CI** there is no `.env` and the workflow sets no `ALLOWED_HOSTS`, so
  `ALLOWED_HOSTS=[]` (the django-environ schema default). Django's test
  runner then rewrites it to `['testserver']` — `localhost` is **not**
  allowed, so `self.client.get(..., HTTP_HOST='localhost')` returns a **400
  DisallowedHost** error page. That page contains no `dash-data` script tag,
  hence `dash-data script tag missing` — the tag itself was never absent.
- Reproduced locally with `ALLOWED_HOSTS='' DEBUG=true SECRET_KEY=ci-test-key
  TESTING=true python manage.py test` — the identical 2 failures.

### Fix

- `core/tests.py` (`DashboardCalendarGridTest._dash_script`): request with
  `HTTP_HOST='testserver'` — the Django test client's canonical host, which
  the test runner always appends to `ALLOWED_HOSTS`. The dashboard view and
  template are host-independent, so nothing else changed; no template or
  view edits were needed, and no hardcoded fallback `<script>` was added.

### Tests & verification

- `python manage.py check` clean.
- Full suite under the exact CI environment (`ALLOWED_HOSTS='' DEBUG=true
  SECRET_KEY=ci-test-key TESTING=true python manage.py test`):
  **854 tests OK** (was FAILED failures=2 before the fix).

---

## 111. Remove Email OTP Verification from Signup — Direct Registration

**Date:** 15 August 2026  
**Branch:** main

The two-step email verification (§92) is gone: signup now creates the account
immediately instead of emailing a 6-digit code and gating account creation
behind a verify step — registration works end-to-end with no email server
connection.

### Changes

- `core/views.py` — `signup_view` now validates `SignUpForm`, creates the
  `User` + `StudentProfile` right away (`is_active=True` via `create_user`),
  signs the student in (`auth_login`) and redirects to their dashboard
  (`/dashboard/student/`). Deleted `verify_email_view`, `_generate_verify_code`,
  `_verify_code_hash`, `_send_verify_code_email`, `_pending_signup`,
  `_mask_email`, the code constants, and the now-unused `hashlib` / `hmac` /
  `time` imports.
- `core/urls.py` — dropped the `signup/verify/` route (`verify_email`).
- `templates/verify_email.html` — deleted; `templates/signup.html` no longer
  reads "Step 1 of 2" (subtitle + button now say "Create Account").
- `static/css/signup.css` — removed the dead `.verify-code-input` /
  `.field-help` / `.auth-resend-*` styles.
- `core/tests.py` — `TwoStepSignupTest` replaced by `SignupViewTest` (creates
  user + profile, signs in, redirects); signup tests now assert immediate
  account creation with `is_active=True` and no email/OTP dependency.

### Tests & verification

- `python manage.py check` clean; signup tests green — registration no longer
  requires an email server connection.

---

## 112. Global News — Dedicated Video News Section (YouTube Data API v3)

**Date:** 15 August 2026  
**Branch:** main

Builds on §104/§111: the Global News widget now shows a dedicated **Video News**
section with playable YouTube cards alongside the text-article grid.

### Changes

- `core/news_service.py` — new `fetch_youtube_videos(query=None, max_results=4)`:
  queries `GET https://www.googleapis.com/youtube/v3/search` with
  `part=snippet&type=video&q={query} news&maxResults=4&key={YOUTUBE_API_KEY}`
  (defaults to `{DEFAULT_CATEGORY} news` without a query) and returns the raw
  API items (`id.videoId` / `snippet.title` / `snippet.description` /
  `snippet.channelTitle` / thumbnails), filtered to real videos. No key or any
  failure → `[]` (never blocks the widget); short-circuits under the test
  runner. The previous interleaved-video enrichment of `fetch_global_news` was
  removed in favour of this dedicated section.
- `templates/partials/global_news.html` — new "Video News" block under the
  article grid: each `.video-news-card` embeds
  `https://www.youtube.com/embed/{{ video.id.videoId }}` in a 16:9 responsive
  wrapper with a red VIDEO NEWS badge, white title and muted channel name; a
  muted empty state renders when no key/videos. The client-side search now
  re-renders both the article grid and the video grid from
  `/api/news/search/` (which returns `data` + `videos`).
- `core/views.py` — `student_dashboard`, `admin_dashboard`, `news_page` and
  `api_news_search` pass `videos = fetch_youtube_videos(...)` into the widget
  context / JSON response.
- `static/css/news.css` — `.news-videos*` / `.video-news-card*` styles (dark
  `#1e1e24` cards, `#2d2d38` border, `#ef4444` badge, 56.25% iframe wrapper).

### Tests & verification

- `python manage.py check` clean; news suites green (19 tests) — new coverage
  for the YouTube query params (`q` gets ` news` appended), raw-item
  pass-through, non-video filtering, no-key/test-run short-circuit, and the
  API + dashboard video rendering. Live check with the configured
  `YOUTUBE_API_KEY`: `fetch_youtube_videos('bangladesh')` returned 4 real
  video cards (BD NEWS71 / Jamuna TV).

---

## 113. Study Corner — Academic Notes + YouTube Lectures + AI Study Assistant

**Date:** 15 August 2026  
**Branch:** main

The Academic Notes page becomes **Study Corner** (`/study-corner/`): the
course-material drive gains a YouTube lecture-video search module and an AI
Study Assistant chat box in a responsive two-column layout.

### Changes

- **Rename:** `academic_notes` view/route → `study_corner` (`/study-corner/`,
  URL name `study_corner`); the old `/academic-notes/` URL stays as a
  permanent 301 redirect. Nav labels updated everywhere: topbar pills (desktop
  + mobile profile links, active state `study`), `base.html` sidebar, dashboard
  quick tiles / panel, `department_detail.html` CTA, `sw.js` precache (`v3`),
  context-processor `ENDPOINTS.study_corner`, README.
- **`core/study_service.py`** (new) — `search_lecture_videos(query, max_results=6)`
  hits `GET https://www.googleapis.com/youtube/v3/search` with
  `part=snippet&type=video&q={query} lecture tutorial&maxResults=6&key=…`
  (or a default `university lecture` query on page load) and returns raw API
  items (`id.videoId` / `snippet.*`), filtered to real videos. No key or any
  failure → `[]`; short-circuits under the test runner. Also owns
  `STUDY_SYSTEM_PROMPT` + `offline_study_response` (deterministic chat reply).
- **`core/views.py`** — `study_corner` renders the new template (notes drive +
  server-rendered default lecture videos); `study_youtube_search`
  (`GET /api/study/youtube/?q=…`) and `study_chat`
  (`POST /api/study/chat/`, OpenRouter with a study-tutor system prompt and
  the last ~10 turns kept in the session; offline fallback when no
  `OPENROUTER_API_KEY`).
- **`templates/academic/study_corner.html`** (new, replaces `academic/notes.html`)
  — two-column layout: left (70-75%) holds the Academic Notes & Resources
  manager (search + upload, folders, documents) on top and the "Video
  Tutorials & Lectures" module (inline search + `.yt-study-card` grid with
  16:9 iframe players and a red VIDEO LECTURE badge) below; right (25-30%) is
  the sticky Study Assistant chat (markdown-lite bubbles, typing indicator,
  CSRF-protected POST). Stacks to one column ≤1024px.
- **`static/css/study.css`** (new) — layout grid, YouTube module, chat box,
  mobile breakpoints, dark-mode overrides. `notes.css` header comment updated.
- **`core/tests.py`** — `AcademicNotesPageTest` → `StudyCornerPageTest` (plus
  heading/module assertions and the 301 redirect check); new
  `StudyYouTubeApiTest` + `StudyChatApiTest` (offline + OpenRouter modes,
  session context across turns); nav/PWA/security tests updated to
  `study_corner` / "Study Corner" label.

### Tests & verification

- `python manage.py check` clean; study/nav/PWA suites green (33 tests).
- Live check with the configured `YOUTUBE_API_KEY`:
  `search_lecture_videos('circuit analysis')` returned 6 real lecture videos
  (e.g. Engineering Circuit Analysis playlists).

## 114. Online Pharmacy Module — Rx Verification, Checkout, Order Tracking, Inventory

**Date:** 15 August 2026  
**Branch:** main

New end-to-end **Online Pharmacy** module (storefront → prescription
verification → checkout → tracked delivery → inventory management), built from
scratch per the operations spec. Analytical tools are out of scope.

### Changes

- **Models (`core/models.py`)** — `MedicineItem` (brand + generic name for
  substitutes, strength, category, price, `is_prescription` Rx flag, and the
  new `batch_number` / `expiry_date` / `reorder_level` fields), `Prescription`
  (student upload, `pending` → `approved` / `rejected` + rejection reason +
  reviewer audit), `PharmacyOrder` (status tracker `placed → rx_verified →
  packaging → out_for_delivery → delivered` / `cancelled`, shipping details,
  bKash / Nagad / SSLCommerz / COD payment, wallet TrxID), `PharmacyOrderItem`
  (line items with snapshot price). `PaymentTransaction` gains the
  `pharmacy` purpose + `sslcommerz` method. Migrations `0041` + `0042`.
- **`core/views.py` + `core/urls.py`** — public storefront `/pharmacy/`;
  customer tracking `/pharmacy/orders/`; medical admin
  `/dashboard/medical/pharmacy/`; and APIs: prescription upload (PDF/JPG/PNG,
  ≤5 MB), checkout (Rx gate: prescription-only items need an *approved,
  user-owned* prescription; stock validation; wallet-TrxID or COD; digital
  receipt with `PO-…` reference; stock decremented atomically), owner-scoped
  order detail (live poll for the tracker), prescription approve/reject,
  order advance/cancel, and bulk stock restock / expiry update. Every state
  change pushes an in-app notification (shared `_broadcast_notification`).
- **`templates/pharmacy/store.html`** — catalog grid (Rx Required badge,
  In/Low/Out stock badges, search), drag-and-drop prescription upload modal,
  product detail modal with an automatic **Generic Substitutes** section
  (same-generic in-stock alternatives, emphasised when the brand is out of
  stock), and a multi-step checkout modal (shipping → payment method → digital
  receipt with reference ID + Track Order link).
- **`templates/pharmacy/orders.html`** — 5-step visual tracker bar
  [Order Placed ➔ Rx Verified ➔ Packaging ➔ Out for Delivery ➔ Delivered]
  with live client-side polling of the order API; cancelled state shown.
- **`templates/pharmacy/admin.html`** — tabbed dashboard: Rx Verification
  Queue (view file, Approve / Reject with reason), Order Management
  (Advance / Cancel with live notifications), and Inventory with color-coded
  badges — red **Out of Stock** / **Expiring Soon** (≤30 days), yellow
  **Low Stock Alert** (≤ reorder level) — plus bulk restock and expiry-date
  actions.
- **`static/css/pharmacy.css`** (new) — modals, cart, tracker bar, badges,
  admin tables, receipt; mobile breakpoints (≤768px) and dark-mode contrast
  overrides.
- **Nav** — Pharmacy pill in the topbar; Pharmacy tile on the student
  dashboard home.
- **`core/tests.py`** — 41 new tests: inventory status logic, public
  storefront, prescription upload gating, checkout (Rx gate incl. owner-scope
  and pending-block, COD vs wallet TrxID, SSLCommerz purpose, stock
  decrement, notifications), tracking page + owner-scoped API, and admin
  (staff gating, Rx approve/reject, order advance/cancel, bulk restock /
  expiry).

### Tests & verification

- `python manage.py check` clean; 41 pharmacy tests + 27 nav/dashboard
  regression tests green.
- End-to-end flows verified: Rx upload → staff approve → Rx order placed →
  tracker advance → delivered, plus COD and bKash/TrxID payment paths.

## 115. Signup — Show / Hide Password Toggle

**Date:** 15 August 2026  
**Branch:** main

The signup form's **Password** field now has an in-field **show/hide toggle**
(eye / eye-slash button) so users can check what they typed while creating an
account.

### Changes

- **`templates/signup.html`** — a `.password-toggle` button (FontAwesome
  `fa-eye` icon) sits inside the Password `.field-input`, with
  `data-target="id_password"`; a small inline script flips the input between
  `type="password"` and `type="text"`, swaps the icon to `fa-eye-slash`,
  updates the `aria-label`/`title`, and returns focus to the field.
- **`static/css/signup.css`** — toggle button styled as a right-aligned
  transparent chip inside the field (hover chip in both light and dark
  themes); inputs in `.field-input.has-toggle` gain right padding so typed
  text never runs under the button. Overrides `auth.css`'s global
  `.field-input i` left-icon rule for the toggle's icon only.

### Tests & verification

- `python manage.py check` clean; signup suites green (22 tests).
- Rendered `/signup/` page verified to include the toggle button, the
  `data-target` wiring, and the eye icon.

## 116. Fix 500 on /study-corner/ — Fileless CourseMaterial Crash

**Date:** 15 August 2026  
**Branch:** main

`/study-corner/` (and `/notes/`) returned **500** whenever a `CourseMaterial`
row had an empty `file` field — the templates called `material.file.url`,
which raises `ValueError: The 'file' attribute has no file associated with
it.` The demo rows seeded by `seed_demo_data` were created with only
`file_type` and no actual file, so a fresh environment crashed immediately.

### Changes

- **`templates/academic/study_corner.html`** — the document card's "Open"
  action is now guarded: real file → `material.file.url`, else Drive link →
  `drive_view_link`, else a muted "—" chip (`.doc-view-muted`). Never
  evaluates `.file.url` on an empty file.
- **`templates/notes/notes_engine.html`** — the Recent PDFs row builds its
  `href` conditionally (file → Drive link → `#` with `pointer-events-none
  opacity-60` for fileless rows).
- **`static/css/notes.css`** — `.doc-view-muted` dashed-chip style.
- **`core/views.py`** — `study_corner` view hardened: the notes/materials
  catalog queries and the YouTube fetch each run under their own try-except
  with `logger.error`, degrading to empty lists so a transient DB/API failure
  never 500s the page.
- **`core/management/commands/seed_demo_data.py`** — seeded `CourseMaterial`
  rows now get a real placeholder PDF (`_placeholder_pdf`, a small valid
  single-page PDF) attached to `file`. The check is `if not material.file`
  (not just `created`), so re-running the seed also **backfills files onto
  existing fileless demo rows**; real uploads are never touched.
- **`core/tests.py`** — regression tests: fileless materials render
  `/study-corner/` (muted chip) and `/notes/` at 200.

### Notes

- `requirements.txt` verified: `requests>=2.31` already present.
- The root cause is the template contract, not the view — the try-except
  guard alone would not have fixed this crash, which is why the templates
  were hardened at the source.

### Tests & verification

- `python manage.py check` clean; 20 study-corner / notes-engine tests green.
- Original crash reproduced with `raise_request_exception` (ValueError on
  `.file.url`), then confirmed fixed: `/study-corner/` and `/notes/` both
  200 against the same fileless rows.
- Seed verified against a throwaway DB: 5 fresh materials get real files on
  disk; re-run stays idempotent (no duplicates).

## 118. Online Pharmacy Polish — BD Catalog Seed, Product Details, Buy Now, Stock Requests & Nav

**Date:** 15 August 2026  
**Branch:** main

Follow-up to §114: the Online Pharmacy module now ships with a seeded
Bangladeshi medicine catalog, a full product-detail modal (image / manufacturer /
usage / dosage / precautions / side effects / live stock units / delivery ETA),
a **Buy Now** shortcut into the existing multi-step checkout gateway, an
**Out-of-Stock Medicine Request** pipeline (student modal → staff review tab),
Online Pharmacy entry points on the hero + medical pages, and a modal
overlay CSS fix (the `.modal-backdrop[hidden]` bug class from §98/§107).

### 1. Medicine catalog fields + seed (`core/models.py`, migration `0044`)

- **`MedicineItem`** gains: `manufacturer` (e.g. Square Pharmaceuticals),
  `image_url` (store card + modal photo), `delivery_eta` (e.g. "30-45 mins on
  campus"), and the detail-modal text fields `usage_info` / `dosage_info` /
  `precautions` / `side_effects`. Admin list/search updated.
- **New `seed_pharmacy_catalog` command** (idempotent `get_or_create` on
  name+strength) seeds the 8 requested BD medicines — Napa Extra, Seclo,
  Sergel, Ace Plus, Entacyd, Savlon Antiseptic Liquid, Ceevit, Monas — with
  BDT prices, stock levels, expiry/batch, image URLs and full detail content.
  **Monas 10mg** is seeded Rx-required and **out of stock** so the Request
  Stock flow is demonstrable out of the box. `seed_demo_data` now invokes it
  (re-run safe, admin-edited rows preserved).

### 2. Product detail modal + Buy Now (`templates/pharmacy/store.html`)

- Cards render an image (with an icon fallback on load failure), manufacturer
  line, and — for out-of-stock items — a **Request** button instead of Add.
- The detail modal now shows: image, full name, generic + manufacturer,
  price, **live stock count** ("In Stock: 45 packs" / "Out of Stock"),
  **delivery estimate** ("Delivered within …"), description, and structured
  Usage / Dosage / Precautions / Side Effects sections, plus Generic
  Substitutes.
- Actions: **Add to Cart**, **Buy Now** (adds the item and opens the
  multi-step checkout modal at Step 1 — shipping → payment gateway →
  receipt), and **Request Stock** for out-of-stock items (opens the request
  modal).

### 3. Out-of-stock medicine requests

- **New `MedicineRequest` model** (medicine, user, quantity, urgency_note,
  phone, status pending/fulfilled/rejected, admin_note, timestamps).
- **`POST /api/pharmacy/request-stock/`** (login required): validates the
  medicine, quantity 1–999 and a contact phone; persists the pending request
  and notifies the student in real time.
- **`POST /api/pharmacy/admin/requests/<id>/status/`** (staff only): marks
  fulfilled (or rejected with a reason) and pushes the outcome notification.
- **Admin dashboard** (`/dashboard/medical/pharmacy/`) gains a fourth tab,
  **Medicine Requests**, with a pending-count badge and per-card
  Fulfil / Reject actions.

### 4. Navigation entry points

- **Hero (`templates/index.html`)** — a prominent **Online Pharmacy** button
  (`.hero-btn-pharmacy`, emerald tint that reads on the permanently-dark
  hero) linking to `/pharmacy/`.
- **Medical page header (`templates/medical/booking.html`)** — an **Online
  Pharmacy** pill button (`.med-pharmacy-btn`) under the intro.

### 5. Layout & dark-mode fixes (`static/css/pharmacy.css`)

- **Critical modal fix:** added `.modal-backdrop[hidden] { display: none; }`
  — the `.modal-backdrop { display: flex }` rule overrode the `hidden`
  attribute, so every modal (Rx / product / checkout) rendered stacked on
  page load with dark glitches. Same defect class as §98/§107.
- New styles for the card/modal images (+ fallbacks), stock-units chips,
  delivery-ETA line, detail sections, and dark-mode contrast for all of them.

### Tests

- New suites: `PharmacyCatalogSeedCommandTest` (8 medicines, idempotency,
  edit preservation, Monas Rx/out-of-stock), `PharmacyStockRequestApiTest`
  (login gate, persistence + notification, unknown medicine, quantity/phone
  validation), `PharmacyRequestStatusApiTest` (staff gate, fulfil/reject +
  notification, already-reviewed 409, invalid action), `PharmacyNavButtonsTest`
  (hero + medical page link to `/pharmacy/`), `PharmacyModalCssGuardTest`
  (the `[hidden]` rule is present in the CSS).
- `PharmacyStorePageTest` extended (manufacturer/image/delivery in catalog
  JSON, request modal + Buy Now markup); `SecurityAuditTest` anonymous matrix
  covers the two new endpoints.
- Full suite — **973 tests OK** · `manage.py check` clean · migrations
  consistent (`makemigrations --check` clean).

---

## 117. Website Builder Overhaul — System Page Registration + Feature Blocks + Live Editing + UI

**Date:** 15 August 2026  
**Branch:** main

Comprehensive Website Builder / CMS overhaul: core system pages are now
auto-registered in the CMS, their default components are exposed as editable
feature blocks (Block Manager), edits render live on the public routes with a
clean fallback to the default templates, and the `/builder/` dashboard got a
UI redesign.

### Changes

- **System page discovery & registration** — new `core/system_pages.py`
  registry + `register_system_pages` management command (auto-run on every
  `/builder/` visit, idempotent). Registers the 5 core routes as
  `EditablePage` rows keyed by the new `system_key` field: Home (`/`),
  Study Corner (`/study-corner/`), Online Pharmacy (`/pharmacy/`), Global
  News (`/news/`), Clubs Hub (`/clubs/`) — all listed in the Editable Pages
  grid. Re-runs never clobber admin edits.
- **Feature-block extraction** — each system page seeds its default
  components as `ContentBlock`s (hidden until revealed):
  Landing → hero banner / quick announcements / feature grid; Study Corner →
  notes listing / YouTube section / study assistant chat; Pharmacy → category
  nav / hero promo / top brands / product grid; News → search bar / image
  card grid / video feed. 11 new block types + partials
  (`templates/builder/blocks/*`), each editable (headings, subtext, media
  URLs) and registered in the shared `render_block_html` map.
- **Live route rendering** — new `cms_system_blocks` context processor maps
  the current URL name to its system page and injects visible, content-bearing
  blocks as `cms_blocks`; the shared `templates/cms/system_zone.html` partial
  (added to all 5 system templates + `static/css/cms.css`) renders them. No
  edits → empty zone → default templates render untouched. New
  `ContentBlock.visible` toggle (Block Manager eye button + save API +
  `editable_page_view` skips hidden blocks) shows/hides sections like video
  feeds or chat boxes live.
- **Builder dashboard UI** — metrics header (total / published / drafts /
  blocks), client-side search + status/type filter bar, upgraded page cards
  (live route slug, published/draft badges, block count, last-modified), and
  the 3 starter blueprints ("Standard Landing Page", "Resource Hub",
  "Noticeboard Grid") with 1-click **Create from Template** that prefills and
  submits the create modal.
- **Models / migration** — `EditablePage.system_key`, `ContentBlock.visible`,
  11 new block types + schemas (`core/migrations/0043_*`).

### Tests & verification

- `python manage.py check` clean; 17 new CMS tests (registration spec +
  idempotency + edit preservation, live zone rendering on all 5 routes,
  dashboard listing/metrics, visibility toggle API + render gating) + 79
  regression tests (builder backend, touched system pages, news, clubs)
  green.
- Verified live: system routes return 200 with no zone before edits; revealing
  a block renders it on the route; hiding restores defaults; `/builder/`
  lists all system pages with metrics and blueprints.

---

## 119. Fix Visual Builder Empty Canvas — Default Block HTML + Preview Mode + Cache Flush

**Date:** 15 August 2026  
**Branch:** main

Fixes the "This page has no content yet" canvas in the visual Website Builder
(`/builder/visual/<slug>/`) for the auto-registered system pages (Home, Study
Corner, Pharmacy, Global News, Clubs): system blocks were seeded with empty
`content_html` **and** `visible=False`, and the editor canvas (an iframe of
`editable_page_view`) only rendered `visible=True` blocks — so the canvas
rendered zero blocks. Now blocks carry their real default layout and the
canvas preview shows every block.

### Changes

- **Default block HTML backfill (`core/system_pages.py`)** — `register_system_pages()`
  now renders each block's matching partial (`templates/builder/blocks/*.html`)
  with its seeded `content_json` via the shared `render_block_html` helper and
  stores the result in `content_html` — the same markup a revealed block
  renders on the public route. New registrations seed it directly; existing
  rows with empty `content_html` are backfilled on the next `/builder/` visit.
  A non-empty (admin-authored) `content_html` is never overwritten, so the
  "never clobber admin edits" contract holds.
- **Preview-mode canvas (`core/views.py`, `templates/builder/editor.html`)** —
  `editable_page_view` accepts `?preview=1`, which renders EVERY block
  (including visibility-toggled-off sections) but only for users with the
  builder's `change_editablepage` permission. The visual editor's canvas
  iframe now loads `/page/<slug>/?preview=1`, so it shows the full page
  layout — hero banner, notes grid, YouTube section, news search/cards,
  pharmacy category nav + product grid — instead of the empty state.
  Anonymous / regular visitors keep seeing only published, visible blocks
  (the public routes and the CMS system zone are unchanged).
- **Template-cache flush on save/publish (`core/views.py`)** — new
  `_flush_template_caches()` helper (resets the Django template engines'
  compiled-template caches) wired into `_save_content_block_data`,
  `builder_page_wysiwyg_save` (Save Changes + Publish Page) and
  `save_page_css`, so live routes never serve a stale compiled copy after an
  edit. Block HTML is DB-backed and read per-request, so edits were already
  immediate — this is a defensive reset for a future cached loader.
- **Sidebar ↔ canvas live editing** — the existing `editor.js`
  `data-edit="html"` binding (typing in the sidebar's "Content (HTML)"
  textarea updates the matching canvas element in real time) now has content
  to sync, since blocks render in the canvas.

### Tests & verification

- 6 new tests: registered blocks carry rendered default HTML (marker per block
  type across all 4 system pages); empty-`content_html` backfill + admin HTML
  preservation; `?preview=1` renders hidden blocks for editors; preview is
  gated for anonymous users and non-editor staff; the editor canvas iframe
  uses the preview URL; a WYSIWYG save + publish of an edited block renders
  live on `/study-corner/`.
- Full suite — **979 tests OK** (973 before) · `manage.py check` clean.
- Verified via rendered DOM: all 14 system blocks carry default HTML; the
  editor page contains no empty-state text; `/page/{home,study-corner,news,
  pharmacy}/?preview=1` each render their full component set; anonymous
  visitors on the same URL see no hidden blocks.

---

## 120. Club Dashboard Sub-Routes + Event Banner Upload + Event Visibility Sync

**Date:** 15 August 2026  
**Branch:** main

Restructured the Club Management dashboard into dedicated sub-routes (each
sidebar item opens its own focused page instead of scrolling to a hash anchor
on one long page), added event banner / poster uploads with a remote-URL
fallback, and synced published event visibility to the student dashboard and
the public /clubs/ page.

### Changes

- **Dedicated sub-routes (`core/urls.py`, `core/views.py`, `templates/club/*`)**
  — the club sidebar now links to six separate pages, each extending
  `club/club_base.html` with the active nav state driven by a `club_section`
  context value:
  - `/dashboard/club/` — Overview (`club/overview.html`, quick-link cards +
    at-a-glance stats)
  - `/dashboard/club/google-sheet/` — Live Google Sheet (`club/sheet.html`)
  - `/dashboard/club/members/` — Member Approvals (`club/members.html`)
  - `/dashboard/club/roles/` — Role Assignments (`club/roles.html`)
  - `/dashboard/club/events/` — Events Management (`club/events.html`)
  - `/dashboard/club/transactions/` — Transaction Verifier
    (`club/transactions.html`)
  The legacy single-page `club_admin.html` at `/clubs/manage/` is untouched
  (existing links/tests keep working); the RoleAccessMiddleware's
  `/dashboard/club/*` guard covers the new routes automatically.
- **Event banner support (`core/models.py`, migration **0045**, admin)** —
  `ClubEvent.banner` (ImageField, `upload_to='club_events/banners/'`),
  `banner_url` (CharField fallback for a remote poster URL) and
  `is_published` (default True, indexed). Admin list/filter shows the publish
  state.
- **Event creation form (`core/forms.py`, `club/events.html`)** — new
  `ClubEventForm` (ModelForm over the six event fields + banner + banner_url +
  is_published). The events page POSTs with `enctype="multipart/form-data"`,
  shows a live image preview (file picker **or** pasted URL), validates
  inline field errors, saves the row, and redirects with `?created=1` so the
  new event appears immediately in the list below the form.
- **Event visibility sync** —
  - `student_dashboard` fetches the 5 nearest upcoming published events
    (`is_published=True, event_date>=today`, select_related club) and
    `dashboard/home.html` renders an **Upcoming Club Events** feed with the
    banner poster, club name, date, venue and a Register / Details button.
  - `clubs_dashboard` (public `/clubs/`) now filters `is_published=True` and
    `clubs.html` event cards show the banner image when present.
  - Draft events stay invisible on both student surfaces until published.
- **Styling** — club overview cards/stat pills, banner preview + event list
  thumbnails, publish/draft badges and field errors added to
  `club_dashboard.css`; event card banners in `clubs.css`; the student feed
  cards in `dashboard.css` (all with dark-mode overrides).

### Tests & verification

- 16 new tests: `ClubEventModelFieldsTest` (banner/URL/publish defaults),
  `ClubDashboardSubRoutesTest` (each sub-route renders for club managers and
  staff with active nav, blocks students with the role redirect, redirects
  anonymous to login, overview links every section), `ClubEventCreationTest`
  (multipart form markup, banner-file save, URL-fallback save, draft stays
  hidden on /clubs/ + student dashboard, invalid form rerenders with errors),
  `StudentDashboardClubEventsTest` (published events + banners render on the
  home feed, drafts/past events omitted), plus clubs-page banner + draft
  filtering tests. Security audit matrix and endpoint registry extended with
  the five new sub-routes.
- Full suite — **995 tests OK** (979 before) · `manage.py check` clean · no
  migration drift. Rendered pages verified: all six sub-routes return 200
  with the club layout and valid inline JS; event banner upload persists and
  shows on both student surfaces.

---

## 121. Public Pharmacy Storefront — Guest Browsing + Hero Button Contrast + Auto-Seeded Catalog

**Date:** 16 August 2026  
**Branch:** main

Made `/pharmacy/` a standalone public store: guests can now browse the full
catalog, search medicines, open product details and build a cart without an
account. Login is required only for the privileged actions (proceeding to
checkout, out-of-stock requests, prescription uploads). The hero's **Online
Pharmacy** button got a high-contrast sky-blue restyle, and the Bangladeshi
medicine catalog now auto-seeds on every deploy.

### Changes

- **Public storefront (`templates/pharmacy/store.html`)** — removed the
  client-side `requireAuth()` gate from the add-to-cart / substitute actions
  so anonymous visitors can browse freely and build a cart (localStorage).
  Login redirects remain on **Proceed to Checkout** (cart button / Buy Now /
  Place Order), **Out-of-Stock Request** and **Prescription upload** — the
  corresponding APIs (`api_pharmacy_checkout`, `api_pharmacy_stock_request`,
  `api_pharmacy_prescription_upload`) were already `@login_required`
  server-side, so the relaxation never weakens a protected action. A guest's
  cart survives the login round-trip via `?next=/pharmacy/`.
- **Hero button contrast (`templates/index.html` + `static/css/main.css`)** —
  the Online Pharmacy button on the landing hero is restyled as
  `.btn-pharmacy-hero` with inline sky-blue styling (`#0284c7` fill, white
  text, `#38bdf8` border, 12px/24px padding, rounded 8px, 🛒 emoji). The dead
  green `.hero-btn-pharmacy` CSS was replaced with a hover lift/glow
  (transform / filter / box-shadow — the inline styles can't be overridden
  for background), and the button joins the other hero CTAs in the mobile
  full-width rule. The builder's `data-widget-id` / `data-editable-field`
  hooks are preserved so the Website Builder can still live-edit it.
- **Auto-populated BD catalog (`build.sh`)** — every deploy now runs the
  idempotent `seed_pharmacy_catalog` command right after `seed_demo_users`,
  so the storefront ships with the 8 popular Bangladeshi medicines
  (Napa Extra, Seclo, Sergel, Ace Plus, Entacyd, Savlon Antiseptic Liquid,
  Ceevit, Monas) without manual seeding. `get_or_create` on name+strength
  means re-runs never duplicate rows or clobber admin edits.

### Tests & verification

- `PharmacyNavButtonsTest` updated for the new `btn-pharmacy-hero` class.
- 30 pharmacy/nav tests (store page, checkout, stock request, prescription
  upload) + 5 seed/modal tests OK · `manage.py check` clean.
- Rendered pages verified: `/` returns 200 with the new button; `/pharmacy/`
  returns 200 anonymous with `USER_AUTH=false`, add-to-cart ungated, and
  checkout / stock request still login-gated.

---

## 122. Student Edition Android App — Splash + Icons, Persistent Sessions, FCM Push & Emergency Siren

**Date:** 16 August 2026  
**Branch:** main

Upgraded the §85 Android WebView wrapper into a full-fledged **Student
Edition** app: branded splash + launcher icons at every density, 1-year
persistent login with direct dashboard landing, a student-only navigation
shell, the full native-permission set, Firebase Cloud Messaging push with
**picture banners**, and an **emergency siren** that breaks through silent
mode. Every native feature is Firebase-optional — the app builds and runs
unchanged until `google-services.json` is dropped in.

### Backend (Django)

- **Persistent sessions (`config/settings.py`)** — `SESSION_EXPIRE_AT_BROWSER_CLOSE
  = False` and `SESSION_COOKIE_AGE = 31536000` (1 year): students stay logged
  in indefinitely until they explicitly tap **Log Out**, so the app lands
  straight on the dashboard after every launch.
- **Direct dashboard landing (`core/views.py` `public_home`)** — the root URL
  now redirects authenticated users to their role home (student →
  `/dashboard/student/`, admin → `/dashboard/admin/`, club →
  `/dashboard/club/`) instead of the hero; guests keep the landing page.
- **Emergency push payload (`services/emergency_push.py`)** — the FCM
  broadcast now carries `play_alarm_sound` (loop the siren) and a `banner`
  picture field alongside `type=EMERGENCY_ALERT` / `severity`.

### Native app (`mobile-webview`)

- **Splash (`SplashActivity.kt`, `layout/activity_splash.xml`)** — launcher
  entry: charcoal screen with the campus-hub logo + "NITER Campus Hub —
  Student Edition", then a hand-off to the WebView shell (`Theme.NiterDash.Splash`
  prevents any white flash).
- **Launcher icons (`scripts/generate_assets.py`)** — PNG `ic_launcher` /
  `ic_launcher_round` (charcoal rounded square / circle with the beige "N"
  monogram) generated for **mdpi / hdpi / xhdpi / xxhdpi / xxxhdpi**; the
  adaptive vector foreground is unchanged. `android:roundIcon` wired.
- **Permissions (`AndroidManifest.xml`)** — INTERNET, ACCESS_NETWORK_STATE,
  CAMERA, READ_MEDIA_IMAGES, READ/WRITE_EXTERNAL_STORAGE (legacy caps),
  POST_NOTIFICATIONS (runtime-requested on Android 13+), VIBRATE, WAKE_LOCK.
- **Persistent login (`MainActivity.kt`)** — `CookieManager` stores the 1-year
  session cookie; `setAcceptThirdPartyCookies` keeps Google OAuth working.
- **Student-only shell** — staff/admin URL prefixes (`/builder/`, `/admin/`,
  `/django-admin/`, `/dashboard/admin/`, `/dashboard/club/`,
  `/dashboard/medical/`, `/medical/admin/`, `/host/`) are blocked at the
  navigation layer and bounced to `/dashboard/student/` — defense in depth
  on top of the server-side `RoleAccessMiddleware`.
- **FCM push (`EmergencyMessagingService.kt`, `NotificationHelper.kt`)** —
  subscribes to the `emergency_alerts` topic; `EMERGENCY_ALERT` pushes render
  as high-priority **BigPicture** notifications (push `banner` URL, or the
  bundled `drawable/emergency_banner.png`); other pushes use a general
  channel. `google-services` Gradle plugin is applied **only when
  `google-services.json` exists**, so the build never breaks without Firebase.
- **Emergency siren controls** — `raw/emergency_siren.wav` (6 s two-tone,
  generated) plays through a high-importance `emergency_alerts` channel with
  vibration; `play_alarm_sound=true` loops the siren until dismissed via the
  **Stop Siren** notification action or by opening the app (which hands
  control to the in-app banner so the native loop and WebView siren never
  overlap).

### Tests & verification

- `LandingRedirectTest` (new): anonymous `/` keeps the hero; student / staff /
  club-manager are redirected past the hero to their role dashboard.
- 21 tests OK (landing redirect + role routing + pharmacy nav) · `manage.py
  check` clean.
- All 10 Android XML resources validated well-formed; icons verified
  (transparent corners, charcoal body, beige monogram); siren WAV is valid
  16-bit PCM. APK build remains an Android Studio step (no Android SDK on the
  dev box) — see `mobile-webview/README.md`.

### Firebase activation (optional, for real push)

1. Firebase console → add Android app `com.niterhub.dash` → download
   `google-services.json` into `mobile-webview/app/`.
2. Set `FIREBASE_CREDENTIALS` (service-account JSON) in the Django env — the
   backend already broadcasts to the `emergency_alerts` topic.
3. Rebuild the APK; emergency broadcasts then push with picture banner +
   siren. Without these steps push is inert and the app is unaffected.

### Follow-up: Gradle wrapper committed (`9478115`)

The wrapper directory originally shipped only `gradle-wrapper.properties`, so
terminal builds (`./gradlew`) failed instantly with "Could not find or load
main class org.gradle.wrapper.GradleWrapperMain" and no `app/build/outputs`
was ever produced. The official Gradle 8.11.1 wrapper JAR + `gradlew` /
`gradlew.bat` scripts are now committed, and the README documents the
`./gradlew assembleDebug` path (`app/build/outputs/apk/debug/app-debug.apk`).
Building still requires the Android SDK (`platforms;android-36` +
`build-tools;35.0.0`) on the machine that runs the build.

---

## 123. Pharmacy Polish, Native-App-Only Hero Redirect, Request-Any-Medicine Page & Android Compile Fixes

**Date:** 17 August 2026
**Branch:** main

Closed out the remaining pharmacy UX items, restricted the hero-page
auto-redirect to the native app wrapper, removed the global Pharmacy nav pill,
added a standalone "Request any medicine" page, made the Android wrapper
compile against firebase-messaging 24.1.0, and added mobile WebView polish.

### Pharmacy contrast + product images (`static/css/pharmacy.css`, `templates/pharmacy/store.html`, `core/management/commands/seed_pharmacy_catalog.py`)

- **Button contrast** — the catalog's primary actions are now explicit solid
  fills instead of the shared dark-grey `.btn-primary`:
  - `+ Add` / Add to Cart / substitute add / Cart pill / Upload Prescription:
    `background:#0284c7; color:#fff; font-weight:600` (hover `#0369a1`).
  - Out-of-stock `Request` / `Request Stock`: `background:#b91c1c; color:#fff`
    (hover `#991b1b`).
  - `Details`: `background:#374151; color:#f3f4f6; border:1px solid #4b5563`.
- **Image placeholders** — `.med-img` / `.pd-img` containers are now dark
  slate `#1f2937` with light `#f3f4f6` fallback icons (no more washed-out
  white boxes).
- **Local product photos** — `seed_pharmacy_catalog` no longer uses
  placehold.co. Each of the 8 seeded medicines now points at a self-hosted
  generated photo in `static/images/pharmacy/` (`napa_extra.png`, `seclo.png`,
  `sergel.png`, `ace_plus.png`, `entacyd.png`, `savlon.png`, `ceevit.png`,
  `monas.png`), with `default_medicine.png` as the universal fallback. The
  command backfills existing rows whose `image_url` still contains
  `placehold.co` (idempotent — admin edits elsewhere are never clobbered).
- **`onerror` fallback** — `cardImage()` and the product-detail renderer now
  swap a broken image to `/static/images/pharmacy/default_medicine.png` via
  `onerror="this.onerror=null; this.src=…"`.

### Hero auto-redirect restricted to the native app (`core/views.py` `public_home`)

- Desktop/mobile **browsers keep the public hero landing page even when
  signed in**. Only the native Mobile App wrapper (`niterapp` in the
  User-Agent, or `X-Native-App: true`) is redirected past `/` to the role
  dashboard (student → `/dashboard/student/`, admin → `/dashboard/admin/`,
  club → `/dashboard/club/`).
- `LandingRedirectTest` rewritten: browser requests (logged-in student /
  staff) return 200 with the hero; `niterapp` UA and `X-Native-App` header
  requests redirect to the right role dashboard.

### Global navigation (`templates/partials/topbar.html`)

- Removed the **Pharmacy pill** from both the desktop nav pills and the
  mobile profile-popover page links. The dedicated "Online Pharmacy" action
  button inside `/medical/` (`templates/medical/booking.html`) is unchanged.

### Standalone "Request any medicine" page (`/pharmacy/request/`)

- **Model (`core/models.py` → migration `0046`)** — `MedicineRequest` gained
  `medicine_name`, `generic_name`, `student_name`, `student_id` and
  `urgency` (`normal` / `urgent`); `medicine` and `user` FKs are now
  **nullable** so free-text requests work without a catalog match. Helpers:
  `display_name`, `requester_label`, `requester_id` (used by the admin tab
  for both request kinds).
- **View (`core/views.py` `pharmacy_request`)** — public form (login
  optional): free-text medicine/generic name, quantity, urgency, name/ID,
  phone, notes. Signed-in students get name/ID prefilled from their profile;
  a best-effort catalog match links the request when the name matches an
  `is_active` `MedicineItem`; authenticated submitters get a notification.
  Guests post without an account.
- **Template (`templates/pharmacy/request.html`)** — matches the pharmacy
  shell (topbar + pharmacy.css), 44px touch targets, success/error banners.
  The storefront toolbar gains a **"Request a Medicine"** button
  (`pharm-request-btn`) linking to it.
- **Admin tab (`templates/pharmacy/admin.html`)** — the Medicine Requests
  tab renders both kinds: catalog requests (stock shown) and free-text
  requests (generic name, typed student name/ID, urgency badge). Guest
  (user-less) requests skip the notification on fulfil/reject
  (`api_pharmacy_request_status` now uses `display_name`).

### Android wrapper compiles (`mobile-webview/`)

- `settings.gradle.kts` gained `jitpack.io` (commit `4253795`); `local.properties`
  points at the local SDK (gitignored).
- firebase-messaging 24.1.0 makes `onStartCommand` **final** on
  `EnhancedIntentService`, so `EmergencyMessagingService.kt` no longer
  overrides it; the notification's **Stop Siren** action now routes through a
  new `SirenControlReceiver` (BroadcastReceiver, registered in the manifest).
- `NotificationHelper.kt` fixed `bannerUrl?.trim()?.takeIf { … }` (safe call
  on the nullable string).
- `./gradlew assembleDebug` **passes** — `app-debug.apk` produced. Remaining
  output is 3 harmless WebSettings deprecation warnings.

### Mobile WebView responsiveness

- Pharmacy pages (`store`, `orders`, `admin`, `request`) now ship the full
  viewport: `width=device-width, initial-scale=1.0, maximum-scale=1.0,
  user-scalable=no`.
- New `@media (max-width: 640px)` block in `pharmacy.css`: modals get
  `width:95vw; max-height:90vh; overflow-y:auto`, all buttons/inputs get a
  44px min-height touch target, and `.navlinks` scrolls horizontally instead
  of wrapping.
- Admin tables were already wrapped in `.admin-table-wrap` (overflow-x).

### Tests & verification

- 64 pharmacy tests (inventory, store page, request page, prescription
  upload, checkout, order tracking, admin, seed command, stock request +
  status APIs, nav buttons, modal CSS guard) + landing redirect, smoke +
  unified header tests all pass (21 targeted, 64 pharmacy) · `manage.py
  check` clean.
- `PharmacyRequestPageTest` (new, 5 tests): public GET, free-text POST
  without catalog match, catalog-match POST, validation errors, profile
  prefill for authenticated users.
- `StudentPagesSmokeTest` / `UnifiedHeaderTest` PAGES and the ENDPOINTS
  registry now include `pharmacy_store` + `pharmacy_request`.
- Tests run with `DATABASE_URL=sqlite:///db.sqlite3` overrides — the dev
  `.env` carries a `SUPABASE_DB_URL` that would otherwise route the test
  runner at the remote Postgres.

## 124. Dedicated Medical Staff Role & Portal — Separate From the Main Admin

### Why
The medical dashboards (`/medical/admin/`, `/host/medical/`) were previously
reached only through the main admin sidebar and gated by the generic staff
flag, so the superuser `admin` was the de-facto "medical admin". The request:
a **separate medical dashboard** with a **dedicated medical staff account**,
and **no medical links in the main admin dashboard**.

### What changed
- **New `medical` role** (`core/roles.py`): a staff member holding the
  `Medical Staff` Django group resolves to the `medical` role, which lands on
  `/medical/admin/` (login redirect, `/dashboard/` dispatcher, native-app
  hero redirect) and is **kept out of `/dashboard/admin/*`** by
  `RoleAccessMiddleware`. Superusers always stay `admin` (full platform
  access, including the medical URL if typed directly — just no nav link).
- **Middleware guard** (`core/middleware.py`): `/medical/admin/*`, `/host/*`
  and `/dashboard/medical/*` now require the `medical` or `admin` role —
  students/club managers are bounced to their own dashboard instead of
  reaching the staff views. The public `/medical/` student booking page is
  **not** guarded (only `/medical/admin/` is).
- **Dedicated account**: `seed_demo_users` now creates
  `medical` / `medical123` (staff, not superuser) and adds it to the
  `Medical Staff` group (idempotent, group backfilled for pre-existing
  accounts).
- **Admin sidebar cleanup** (`templates/admin/admin_base.html`): removed the
  "Medical Admin" and "Host Portal" links from the Service Dashboards section.
- **Medical portal shell** (`templates/host/host_base.html`): rebranded
  "Host Portal" → "Medical Staff Portal", sidebar now lists the three real
  destinations (Medical Admin Dashboard, Medical Dashboard, Pharmacy Admin)
  and the profile card shows the signed-in user's name instead of a hardcoded
  placeholder. Dead `#` links removed.

### Demo credentials
- Medical staff: **`medical` / `medical123`** → lands on `/medical/admin/`
- Main admin (unchanged): **`admin` / `admin123`** → `/dashboard/admin/`
- Student (unchanged): **`student` / `student123`**

### Files touched
- `core/roles.py` — `ROLE_MEDICAL`, `MEDICAL_STAFF_GROUP`, `is_medical_staff()`,
  role resolution precedence (superuser → admin, medical group staff → medical)
- `core/middleware.py` — medical-area guard
- `core/context_processors.py` — `medical_pharmacy` endpoint for the sidebar
- `core/management/commands/seed_demo_users.py` — medical account + group
- `templates/admin/admin_base.html` — medical links removed
- `templates/host/host_base.html` — Medical Staff Portal branding/sidebar
- `core/tests.py`, `host/tests.py` — medical-role tests; student access
  expectations updated (middleware bounces instead of 403/login-loop)

### Verified
- Full suite: **1012 tests pass** (RoleRoutingTest medical-role cases, host
  dashboard tests, pharmacy admin, toast/profile/medical booking pages).
- Headless-Chrome check: `medical` login lands on `/medical/admin/`, the
  portal sidebar renders "Medical Staff Portal" + the three links, medical
  user is bounced from `/dashboard/admin/`, and the admin sidebar no longer
  contains "Medical Admin" / "Host Portal" links.
- Tests run with `DATABASE_URL=sqlite:///db.sqlite3` overrides — the dev
  `.env` carries a `SUPABASE_DB_URL` that would otherwise route the test
  runner at the remote Postgres.

## 125. Android Studio Gradle Sync Fix — `prepareKotlinBuildScriptModel` Not Found

### Why
Android Studio failed Gradle sync with
`Task 'prepareKotlinBuildScriptModel' not found in project ':app'`. The
Gradle root structure itself was already correct (`mobile-webview/` has
`settings.gradle.kts` declaring `include(":app")`); the real cause was a
**stray `.idea` folder inside `mobile-webview/app/`** (plus a stray
`app/local.properties`), left over from opening the `app/` sub-module as a
project. Android Studio detects a project root by the `.idea` directory, so
it treated `app/` as the root and its sync asked for the Kotlin build-script
model on the wrong project.

### What changed
- **Removed the open-app-as-root artifacts** — `app/.idea/` and
  `app/local.properties` deleted (both gitignored, nothing tracked touched).
- **Aligned `rootProject.name`** in `mobile-webview/settings.gradle.kts` from
  `NiterDash` → `NiterCentralizedDash` (matches the requested spec). The
  file already had the required `pluginManagement` (google/mavenCentral/
  gradlePluginPortal) + `dependencyResolutionManagement`
  (google/mavenCentral/jitpack.io) + `include(":app")` structure.
- **README troubleshooting section** (`mobile-webview/README.md`) under
  "Open & build the APK": always open the `mobile-webview` root folder, never
  `app/`; recovery steps = close project → delete any `app/.idea` →
  Invalidate Caches & Restart → re-sync from the root.

### Verified
- `./gradlew assembleDebug` → BUILD SUCCESSFUL (APK builds).
- `./gradlew :prepareKotlinBuildScriptModel --dry-run` → BUILD SUCCESSFUL —
  the IDE-sync task resolves on the root project, confirming the sync path
  Android Studio uses is intact.

## 126. Repo Branding & README — Banner Asset + Comprehensive README

### Why
The repo had a minimal 3-line README (just demo accounts). The request:
build the README from the project's hackathon documentation PDF and make the
repository presentable ("make the repo beautiful").

### What changed
- **`docs/assets/banner.png`** — generated 1280×420 branded banner using the
  app's palette (charcoal `#27272a` gradient, warm beige `#e8e2d8` title,
  cyan `#0284c7` accents), built with Pillow from the same branding as the
  PWA icon.
- **`README.md`** — full rewrite from the hackathon doc: hero header with
  badges (Python/Django/PostgreSQL/Channels/Android/MIT), table of contents,
  What-is / Problem / Solution sections, all 10 core feature groups, the
  role-based access table (incl. the new `medical` role), accurate tech-stack
  table, getting-started steps (clone → env → migrate → seed → run → test),
  demo accounts table (now with `medical`/`medical123`), project tree,
  mobile-app section pointing at `mobile-webview/`, API/realtime overview,
  security list, roadmap, and documentation links.
- **`docs/HANDOVER.md`** — changelog row §126.

### Verified
- All README links resolve (`docs/assets/banner.png`, `LICENSE`,
  `mobile-webview/README.md`, `docs/HANDOVER.md`, `UNFINISHED.md`).
- Seed commands referenced (`seed_demo_users`, `seed_pharmacy_catalog`)
  exist in `core/management/commands/`.

## 127. App Notifications & Sound Without Firebase — Background Emergency Watcher + Native Siren Bridge

The Android app already had full FCM plumbing, but without `google-services.json`
the push channel is inert — so no notification and no siren ever fired. This
section makes native notifications + alarm sound work **immediately, with zero
Firebase setup**, and wires the dashboard banner to the native alarm channel.

### Changes
- **`mobile-webview/.../EmergencyPollWorker.kt`** *(new)* — a WorkManager
  worker that polls `GET /api/emergency/active/` every ~30s using the WebView's
  session cookie (same-origin), and self-re-schedules so the loop survives
  process death:
  - new active alert → `NotificationHelper.notifyEmergency` (BigPicture
    notification + looping alarm-channel siren, bypasses silent mode);
  - `alert: null` → siren stopped, notification cleared, state re-armed;
  - network/auth failure → state untouched (never silence a live emergency on
    a transient error).
- **`MainActivity.kt`** — schedules the worker on launch; exposes the
  `NiterHub` JS bridge (`playSiren()` / `stopSiren()`) to the WebView.
- **`templates/partials/emergency_banner.html`** — the banner's `startSiren` /
  `stopSiren` now drive the native alarm siren when `window.NiterHub` exists
  (browser `Audio` remains the fallback on desktop/web).
- **`SirenControlReceiver.kt`** — the notification's Stop Siren action also
  persists the silenced alert id, so the poller never re-triggers the same
  alert (a new alert id re-arms automatically).
- **`app/build.gradle.kts`** — added `androidx.work:work-runtime-ktx:2.9.1`.

FCM (once configured) remains the instant-delivery channel; both paths key off
the alert id so they never double-alert.

### Verified
- `./gradlew assembleDebug assembleRelease` → **BUILD SUCCESSFUL** (only
  pre-existing deprecation warnings).
- Fresh signed APKs copied to the project root (`NiterCampusHub-v2.0-*.apk`).

## 128. README Solution Section — Official Project Description

Replaced the hand-written "The Solution" lead with the official project
description: a modular central hub paired with a dedicated mobile app for
students/employees/staff (routines, attendance, shuttle, meal tokens, medical,
Online Pharmacy, clubs, payment gateway, Global News Hub, role-restricted
Google Drive/Sheets), plus the all-in-one management command center
(Medical/Pharmacy · Cafeteria · Club Workspace · System Admin sub-dashboards,
drag-and-drop Website Builder & CMS, and the real-time Emergency Siren &
Broadcast system pushing visual + audio alerts to every active mobile app and
web dashboard). The structured Students/Admins breakdown is retained below the
new prose, and the Mobile App feature list now documents the Firebase-free
background emergency watcher + native siren bridge.

## 129. NCC Club-Manager Demo Account

Added a dedicated club-manager demo account so the club workspace
(`/dashboard/club/`) can be demoed with one login.

### Changes
- **`core/management/commands/seed_demo_users.py`** — now also creates:
  - User **`NCC`** / **`ncc@gmail.com`** (regular user, not staff);
  - the **NITER Computer Club (NCC)** (`slug=niter-computer-club`) if missing;
  - an **active `ClubAccount`** linking `NCC` to that club as **manager** with
    all capabilities enabled (`can_post_events`, `can_manage_members`,
    `can_manage_finances`) — RBAC routes the account to the club workspace
    after login and the middleware bounces it out of student/admin areas.
  - Idempotent like the rest of the command — existing users/accounts/clubs
    are never reset.
- **`core/tests.py`** — `test_creates_ncc_club_manager` covers the account,
  club link, capabilities and idempotency.
- **`README.md`** — demo-accounts table now lists `NCC` / `ncc@gmail.com`.

### Verified
- Seeded into the local dev DB (`db.sqlite3`); `NCC` login works, role
  resolves to `club`, `GET /dashboard/` → 302 → `/dashboard/club/`, and
  `/dashboard/student/` bounces back to the club dashboard.
- `SeedDemoUsersCommandTest` + `RoleRoutingTest` → 25 tests **OK**.

## 130. Navbar Underline Fix + Modal Button Contrast + Mobile WebView Polish

Fixes the top navigation across every shared-topbar page and the new
`/news/` / `/attendance/` / `/pharmacy/` pages at mobile WebView sizes.

### Changes
- **`static/css/topbar.css`** — nav pills (`brand`, `.navlinks a`,
  `.nav-dropdown-btn`, dropdown + profile links, profile actions) now force
  `text-decoration: none !important`, so pages whose body class does not
  blanket-reset link underlines (news/attendance/pharmacy) never show
  browser-default underlines. All pills share `border-radius: 9999px` and a
  uniform `0.875rem` font; the **active pill is a solid `#374151` fill with
  `#ffffff` text** (hover `#4b5563`) instead of an underline/font-weight shift.
- **`static/css/pharmacy.css`** — Rx Upload (`#rx-submit-btn`) and Checkout
  Continue (`#co-next-1`) buttons: solid `#0284c7`/white primary; disabled
  state `#1f2937`/`#6b7280` at 0.6 opacity with `cursor: not-allowed`.
  `body.pharmacy .shell` gets `width/box-sizing/overflow-x` and 12px mobile
  padding. (The store does not load dashboard.css, so its shell needed its own
  rule.)
- **`templates/pharmacy/store.html`** — Upload button starts `disabled` and
  unlocks only when a valid file is selected (matching the muted disabled
  style).
- **`static/css/dashboard.css`** — `.shell` gets `width: 100%`,
  `box-sizing: border-box`, `overflow-x: hidden`, and `padding: 0.75rem` on
  mobile.
- **`static/css/news.css`** — article + video grids stack to 1 column at
  `<= 768px` (was 640px, article grid only).
- **`static/css/attendance.css`** — shell container rules + 12px mobile
  padding (layout was already mobile-first single column; camera video is
  100% width).

### Verified
- Headless-Chrome at 390px + 1280px on `/news/`, `/attendance/`,
  `/pharmacy/`: no nav underlines, active pills solid `#374151`/white,
  14px pill font, shell padding 12px on mobile, news grid 1-col at 390px /
  4-col at 1280px, attendance 1-col at 390px / 2-col at 1280px, pharmacy
  Rx/checkout buttons at the specified colors (disabled state confirmed).
- Full suite: **1013 tests OK**.

## 131. Meals/News Loading Fixes · Study Corner PDF Preview + Local Uploads · Vector DB (RAG)

Three requests against localhost behaviour: (1) `/meals/` and `/news/` loading
problems, (2) a working Study Corner document experience (PDF preview + real
uploads, no Google Drive), and (3) an embedded vector database (ChromaDB) with
full RAG retrieval, **restricted to the Study Corner and Research AI
assistants**.

Everything vector-related is offline-friendly: `chromadb` is imported lazily
and every vector operation logs once then no-ops when it is unavailable, so
uploads and chat never break. Embeddings use a hosted model when
`EMBEDDINGS_API_KEY` is set, otherwise a deterministic, dependency-free
fallback in `services/embeddings.py`.

### Task 1 — `/meals/` + `/news/`
- **`templates/meals.html`** — the "remaining" figure rendered the literal
  string `200-15` because it (mis)used the `add` filter as subtraction
  (`{{ total_capacity|add:"-"|add:total_claimed_today }}`). All three spots
  (ring "X remaining", "Remaining Supply", "Slots Remaining") now render a
  view-computed `{{ total_remaining }}`.
- **`core/views.py::meal_dashboard`** — computes `total_capacity`,
  `total_claimed_today`, a per-meal `remaining` map, and
  `total_remaining = max(total_capacity - total_claimed_today, 0)`; added to
  both the template context and the JSON state. The claimed-today aggregate and
  the authenticated subscription/ticket lookups are wrapped in `try/except`
  that degrades to zeros + an empty ticket list (the requested fallback state).
- **`core/views.py::news_page`** (+ the student dashboard and admin overview
  call sites) — the two live API calls now go through
  `cache.get_or_set('news:global' / 'news:videos', …, 900)` (15-min TTL), so
  only the first load pays the latency and every subsequent load is instant.
  Fallback behaviour is unchanged.
- **`core/news_service.py`** — `TIMEOUT_SECONDS` 5 → 3 so a cold/offline load
  degrades to sample data faster (worst case ~6 s instead of ~10 s).

> Note: no hard 500/hang was reproducible on `/meals/` — its only visible
> defect was the `200-15` remaining count. The `try/except` was added as
> belt-and-suspenders per the "add fallback state" request.

### Task 2 — Study Corner: PDF preview, Drive removal, local uploads
(all UI changes confined to `templates/academic/study_corner.html`)
- **PDF preview box** — a `#doc-preview` pane embeds the selected material in an
  `<iframe>`; PDFs render inline, non-PDF files show a download affordance, and
  the newest material is selected on load. Doc cards are now clickable and
  keyboard-accessible (`data-file-view` / `data-file-url` / `data-file-type`).
- **Google Drive removed from this page** — the `{% elif material.drive_view_link %}`
  card branch and the placeholder "connect Google Drive" upload toast are gone.
  No shared Drive code (google_service, Notes Engine, Clubs, Settings) touched.
- **Direct local/DB upload** — the upload button (auth-only) reveals a real
  `multipart/form-data` form posting to a new view; a `fetch()` handler submits
  it and reloads on success. Backed by:
  - `core/forms.py::CourseMaterialForm` — `title` / `course` / `file`, validates
    extension (`.pdf/.docx/.pptx`) and size (≤10 MB).
  - `core/views.py::study_material_upload` (`@login_required`, POST) — saves to
    the shared `CourseMaterial` catalog, sets `file_type` from the extension,
    enqueues indexing, returns JSON for the fetch path.
  - `core/views.py::study_material_file` (`@xframe_options_sameorigin`) +
    `core/urls.py` route `study-corner/file/<id>/` — serves the file inline so
    the iframe can preview it (the site-wide `X-Frame-Options: DENY` is
    overridden to SAMEORIGIN on this one response only, not globally).

### Task 3 — Vector DB (ChromaDB) + RAG, restricted to Study Corner & Research AI
- **New `services/` adapters** (mirror the `openrouter.py` / `parser.py` ethos):
  - `services/chunking.py` — `chunk_text(text, size=1000, overlap=150)`,
    dependency-free.
  - `services/embeddings.py` — `embed_text` / `embed_texts` → 384-dim vectors
    (hosted model when configured, deterministic L2-normalized offline fallback
    otherwise).
  - `services/vector_store.py` — embedded ChromaDB `PersistentClient` with
    **exactly two collections** (`study_corner`, `research_ai`; any other name
    raises `ValueError`). `index` / `query` / `delete`; cosine space; our own
    embeddings passed in (no ONNX download); idempotent re-index; owner filter
    for per-user Research AI. Lazy import + no-op on failure; chromadb telemetry
    logger silenced (0.5.x posthog noise).
- **`core/models.py::VectorDocument`** (+ migration
  `0047_vectordocument_and_more`) — tracks module / source / owner / status /
  chunk_count / indexed_at with a per-source uniqueness constraint; gives
  idempotency and admin visibility.
- **`core/tasks.py`** — `@db_task()` `index_course_material(material_id)` and
  `index_research_document(owner_id, source_id, text, title)`; self-contained
  with internal `try/except` (never re-raise), run inline in dev (Huey immediate
  mode) and on the worker in prod.
- **Auto-index on upload** — `study_material_upload` enqueues
  `index_course_material`; Research AI enqueues `index_research_document`
  (owner-scoped) for the attached document.
- **Retrieval wired into answers (RAG):**
  - `study_chat` (`/api/study/chat/`) — retrieves top-k from the shared
    `study_corner` collection and injects the excerpts into the system prompt,
    framed as untrusted reference data (prompt-injection defense), truncated to
    ~6 000 chars.
  - `research_query` — retrieves top-k from `research_ai` scoped to
    `owner=request.user.id` (retrieval *before* indexing to avoid duplicating
    the current turn), combines it with the freshly-extracted document text, and
    passes the richer context to `build_system_prompt`.
- **Config** — `config/settings.py` gains `VECTOR_STORE_BACKEND`,
  `VECTOR_STORE_PATH`, `EMBEDDINGS_API_KEY` / `EMBEDDINGS_MODEL`,
  `VECTOR_INDEXING_ENABLED`; the duplicate `cms_system_blocks` context-processor
  registration was removed (it ran the same `EditablePage` query twice per
  request). `vector_store/` added to `.gitignore`; `requirements.txt` adds
  `chromadb>=0.5,<0.6` (installed & tested: 0.5.23).

### Notes
- Offline embeddings are low-quality by design (deterministic hashing/TF
  fallback) — fine for wiring and keys-absent dev; set `EMBEDDINGS_API_KEY` for
  production-grade retrieval (a one-file swap in `services/embeddings.py`).
- Chroma is per-instance on the local path; multi-worker prod wants a shared
  volume or a client/server Chroma — the adapter isolates that choice.
- **Dependency hygiene:** removed two spurious, never-committed lines from
  `requirements.txt` — `chromadb==1.5.9` (conflicts with the tested `<0.6` pin)
  and `xberg==1.0.14` (an unused compiled "document intelligence" package
  referenced nowhere in the code, installed separately from the vector-DB
  work). `xberg` remains installed in the local venv only; recommend
  `pip uninstall xberg`.

### Verified
- `manage.py check` clean.
- Django-shell sanity check of the full pipeline: chunk → embed (384-dim, L2
  norm 1.0) → index → query round-trips the indexed chunk; the module
  allow-list rejects disallowed names; `is_available()` True with chromadb
  0.5.23; offline embedding fallback active (`api_enabled=False`).
- Core suite on SQLite (`SUPABASE_DB_URL= DATABASE_URL= TESTING=1 manage.py
  test core`): **965 tests OK** (0 failures). Three `GlobalNewsDashboardTest`
  cases initially failed because the new news cache leaked mocked payloads
  across test methods (LocMemCache is not reset between tests); fixed by
  bypassing the cache under the test runner (same `_is_test_run()` gate the
  network already uses), leaving production caching active.

## 132. Study Corner PDF-Preview Overlap Fix · Case-Insensitive Student ID Login

Two follow-up bug fixes on top of §131: (1) the Study Corner PDF preview
rendered its iframe, empty state and fallback download card stacked on top of
one another, and (2) valid Student/Staff IDs failed to log in unless the exact
stored letter-case was typed.

### Issue 1 — PDF preview overlap (`templates/academic/study_corner.html`)
The preview's three stage layers (`#doc-preview-frame`, `#doc-preview-empty`,
`#doc-preview-fallback`) are shown/hidden by JS toggling their `hidden`
attribute, but each carried an explicit `display` rule in the page CSS
(`.doc-preview-frame{display:block}`;
`.doc-preview-empty`/`.doc-preview-fallback{display:flex}`). An **author**
`display` declaration beats the browser's UA `[hidden]{display:none}` rule
regardless of specificity, so the `hidden` attribute was silently ignored and
all three layers rendered simultaneously — the iframe bleeding through the
"Download file" overlay.

**Fix:** a single page-scoped guard at the top of the template's `<style>`
block — `[hidden] { display: none !important; }` (the canonical normalize.css
remedy for this UA-vs-author conflict). Each state now resolves cleanly: a valid
PDF shows only the `<iframe>`; a non-previewable file shows only the fallback
download card; nothing selected shows only the empty state. The one rule also
fixes two latent instances of the same defect on the page — the
`#doc-preview-open` "Open in new tab" link (`display:inline-flex`), which would
otherwise show with `href="#"` before any document is selected, and folder
card-filter hiding (`card.hidden`). The opacity-based `.study-toast` never uses
the `hidden` attribute, so it is unaffected.

### Issue 2 — Student/Staff ID login (`core/views.py`)
IDs are stored **upper-cased** — `SignUpForm.clean_student_id` normalizes them
before the `User` is created — but Django's default `ModelBackend` resolves
usernames **case-sensitively** (`get_by_natural_key`). A student stored as
`S1001` who typed `s1001` therefore failed authentication *even with the correct
password*. Fresh signups always worked because `signup_view` signs the
just-created `User` in directly (`auth_login(request, user)`) without ever
re-authenticating — which is exactly what drove the "keep creating new test
accounts" symptom. Session persistence itself was already correct in dev
(`DEBUG=True` → `SESSION_COOKIE_SECURE=False`).

**Fix:** a form-layer `StudentIdAuthenticationForm(AuthenticationForm)` whose
`clean_username` maps the typed value to the stored username's exact casing — an
exact match wins; otherwise a single case-insensitive match (`username__iexact`)
is substituted; anything ambiguous (two records differing only by case) or
unknown is left untouched so authentication fails normally. It is wired onto
`RoleAwareLoginView` via `authentication_form`. The authentication backend, the
signup auto-login path, existing sessions and all production security settings
are left untouched — nothing weakened.

### Verified
- `manage.py check` clean.
- New `core.tests.LoginCaseInsensitiveTest` (4 tests) drives the real login POST:
  a lower-cased ID authenticates and establishes the session (`_auth_user_id`),
  exact case still works, and wrong password / unknown ID still fail.
- Full core suite on SQLite (`SUPABASE_DB_URL= DATABASE_URL= TESTING=1 manage.py
  test core`): **969 tests OK** (0 failures) — the §131 baseline of 965 plus the
  4 new login tests, no regressions.

## 133. Native QR Scanner — CameraX + ML Kit (Bypasses WebView getUserMedia)

**Date:** 24 August 2026
**Branch:** main

### Problem

The attendance page (`/attendance/`) uses the `html5-qrcode` library (CDN) which
calls `navigator.mediaDevices.getUserMedia()` to access the device camera for QR
scanning. In Android WebView, `getUserMedia` is unreliable — the camera request
silently fails even with the `CAMERA` permission granted and
`onPermissionRequest` auto-granting WebRTC resources. The result: "Start Camera"
shows "Camera unavailable or permission denied" and the user falls back to
manual code entry.

### Solution — Native CameraX + ML Kit Scanner

Instead of fighting WebView's limited WebRTC support, bypass it entirely with a
**native Android camera scanner** that opens as a full-screen Activity, decodes
QR codes in real-time using ML Kit barcode detection, and injects the result
back into the WebView page via JavaScript.

### Architecture

```
attendance.html                    MainActivity.kt                 ScannerActivity.kt
┌──────────────┐   JS bridge      ┌──────────────────┐  intent    ┌──────────────────┐
│ Start Camera │ ───────────────► │ NiterHub.scanQR()│ ─────────► │ CameraX preview   │
│              │                  │ qrScannerLauncher│            │ ML Kit barcode    │
│ __qrScan ◄──│ ◄─────────────── │ evaluateJavascript│ ◄───────── │ RESULT_OK + value │
│   Callback   │                  │                  │            │                  │
└──────────────┘                  └──────────────────┘            └──────────────────┘
```

### Changes

#### 1. Dependencies (`mobile-webview/app/build.gradle.kts`)
- **CameraX 1.4.1** — `camera-camera2`, `camera-lifecycle`, `camera-view` for
  the camera pipeline.
- **ML Kit Barcode Scanning 17.3.0** — bundled (no Google Play Services
  required); decodes QR_CODE, AZTEC, and DATA_MATRIX formats.

#### 2. ScannerActivity (`mobile-webview/.../ScannerActivity.kt`)
- Full-screen Activity with a `PreviewView` camera preview.
- `ImageAnalysis` + `BarcodeScanner` pipeline: each camera frame is fed to ML
  Kit; the first decoded barcode delivers the result and finishes the Activity.
- `RESULT_OK` with `EXTRA_QR_RESULT` (the raw decoded string) on success;
  `RESULT_CANCELED` on back/close.
- Runtime camera permission request via `ActivityResultContracts`.
- Close button (top-left ✕) and hardware BACK both cancel gracefully.
- Anti-duplicate guard (`resultDelivered` volatile) prevents double-fires.

#### 3. Layout (`mobile-webview/.../res/layout/activity_scanner.xml`)
- Full-screen `PreviewView`, semi-transparent top bar with close button +
  "Scan QR Code" title, and a bottom status text ("Point your camera at the
  QR code…").

#### 4. JS Bridge (`mobile-webview/.../MainActivity.kt`)
- **`qrScannerLauncher`** (`ActivityResultLauncher`) — receives the scanned
  value from `ScannerActivity`, escapes it for safe JS injection, and calls
  `window.__qrScanCallback(value)` on the WebView. On cancel, calls the
  callback with `null`.
- **`NiterHub.scanQR()`** — added to the existing `EmergencyBridge` JS
  interface. Sets a pending callback marker and launches `ScannerActivity`.
- **AndroidManifest.xml** — `ScannerActivity` registered with
  `screenOrientation="portrait"`.

#### 5. Attendance Page (`templates/attendance.html`)
- **Native app detection:** `isNativeApp = !!(window.NiterHub &&
  window.NiterHub.scanQR)` — true inside the Android wrapper (which exposes
  `NiterHub`), false in a normal browser.
- **`startScanner()` rewritten:** when `isNativeApp` is true, it sets
  `window.__qrScanCallback` (receives the decoded string or `null` on cancel)
  and calls `NiterHub.scanQR()`. The callback auto-submits the token or resets
  the UI on cancel. The browser `html5-qrcode` fallback is unchanged for
  non-app visitors.
- The "Stop" button is hidden for the native path (the scanner is a separate
  Activity, not an in-page stream).

#### 6. Accessibility
- `onPermissionRequest` added to `WebChromeClient` (for any remaining WebRTC
  use-cases in the browser path).
- `READ_MEDIA_IMAGES` / `READ_EXTERNAL_STORAGE` / `POST_NOTIFICATIONS`
  permissions already in the manifest from §122.

### Testing
- `./gradlew clean assembleDebug assembleRelease test` — **BUILD SUCCESSFUL**,
  90 tasks, zero failures.
- `python manage.py test core.tests.StudentPagesSmokeTest
  core.tests.UnifiedHeaderTest core.tests.AttendancePageTest` — **6/6 OK**
  (template changes are purely client-side JS; server-rendered output unchanged).
- Verified: attendance page renders the `isNativeApp` detection script; scanner
  Activity class exists in the APK's DEX.

### Files Added / Modified
- **New:** `mobile-webview/app/src/main/java/com/niterhub/dash/ScannerActivity.kt`,
  `mobile-webview/app/src/main/res/layout/activity_scanner.xml`
- **Modified:** `mobile-webview/app/build.gradle.kts` (CameraX + ML Kit deps),
  `mobile-webview/app/src/main/java/com/niterhub/dash/MainActivity.kt` (bridge +
  launcher), `mobile-webview/app/src/main/AndroidManifest.xml` (register
  activity), `templates/attendance.html` (native scanner path)

---

## 134. Mobile Viewport Optimization — Touch Targets + Zoom Prevention

**Date:** 24 August 2026
**Branch:** main

### Problem

Pages rendered inside the Android WebView lacked the mobile-optimized viewport
meta tag (`maximum-scale=1.0, user-scalable=no`), so users could pinch-zoom,
causing layout breaks, text reflow, and inconsistent sizing. Additionally,
interactive elements (buttons, nav pills, input fields) had touch targets below
the 44×44 px recommended minimum, making them hard to tap on small screens.

### Changes

#### 1. Viewport Meta Tags (31 template files)
Every standalone template was updated from:
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```
to:
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
```

Files updated: `base.html`, `index.html`, `login.html`, `signup.html`,
`settings.html`, `profile.html`, `dashboard/home.html`, `attendance.html`,
`transport.html`, `meals.html`, `clubs.html`, `medical/booking.html`,
`notices/notices.html`, `academic/study_corner.html`, `notes/notes_engine.html`,
`news.html`, `research_ai.html`, `checkout.html`, `departments.html`,
`department_detail.html`, `editable_page.html`, `club/club_base.html`,
`admin/admin_base.html`, `cafeteria_admin.html`, `sys_admin.html`,
`builder/editor.html`, `builder/edit_page.html`.

Pharmacy pages already had the correct viewport tag from §123.

#### 2. Global Touch-Target Minimum (`static/css/theme.css`)
New `@media (max-width: 640px)` block at the end of `theme.css`:
- Enforces `min-height: 44px; min-width: 44px` on all interactive elements
  (buttons, nav pills, avatars, quick tiles, links with `.btn` classes).
- Bumps small text (`section-subtitle`, `stats-table`, `notice-date`,
  `cal-day-num`, `pct-badge`, etc.) to `max(0.78rem, 12.5px)` minimum.
- Adds `-webkit-overflow-scrolling: touch` on `.table-wrap` for smooth
  horizontal scroll.
- Ensures `.card`, `.panel-card`, `.widget-card` have `padding: 1rem` on mobile.

#### 3. Attendance Page (`static/css/attendance.css`)
- Scanner + manual input buttons: `min-height: 48px; font-size: 0.9rem`.
- Field input and submit button: `min-height: 48px; font-size: 1rem`.

#### 4. Dashboard (`static/css/dashboard.css`)
- Quick tiles: `min-height: 80px; padding: 1rem`.
- Widget buttons: `min-height: 44px; font-size: 0.88rem`.
- Stat numbers/captions sized for mobile readability.

### Testing
- `python manage.py test core.tests.StudentPagesSmokeTest
  core.tests.UnifiedHeaderTest core.tests.AttendancePageTest` — **6/6 OK**.
- `./gradlew clean assembleDebug assembleRelease test` — **BUILD SUCCESSFUL**,
  90 tasks, zero failures.
- All 31 templates confirmed to have `maximum-scale=1.0, user-scalable=no`.

### Files Modified
- 31 template files (viewport meta tag)
- `static/css/theme.css` (global mobile touch targets)
- `static/css/attendance.css` (scanner/input button sizing)
- `static/css/dashboard.css` (quick tile + widget button sizing)

---

## 135. WebView Zoom & Layout Settings — Disable Zoom + Text Autosizing

**Date:** 24 August 2026
**Branch:** main

### Problem

Even after adding `maximum-scale=1.0, user-scalable=no` to the HTML viewport
meta tag (§134), Android WebView still allowed pinch-to-zoom via its built-in
gesture handling, and long text blocks could overflow their containers on narrow
screens because the default layout algorithm doesn't reflow text to fit.

### Changes (`mobile-webview/.../MainActivity.kt` → `configureWebView()`)

Added four settings after the existing `useWideViewPort` / `loadWithOverviewMode`
pair:

```kotlin
// Disable all zoom controls — the viewport meta tag handles scaling.
settings.setSupportZoom(false)
settings.builtInZoomControls = false
settings.displayZoomControls = false
// Let WebView auto-size text to fit the viewport width.
settings.layoutAlgorithm = WebSettings.LayoutAlgorithm.TEXT_AUTOSIZING
```

| Setting | Effect |
|---------|--------|
| `setSupportZoom(false)` | Prevents pinch-to-zoom gestures entirely |
| `builtInZoomControls = false` | Hides the built-in +/- zoom buttons |
| `displayZoomControls = false` | Hides the transient zoom overlay |
| `layoutAlgorithm = TEXT_AUTOSIZING` | WebView reflows text to fit the viewport
  width, breaking long paragraphs across lines instead of overflowing |

The existing `useWideViewPort = true` and `loadWithOverviewMode = true` remain
unchanged — they ensure the WebView respects the `<meta viewport>` width and
fits the page content to the screen on first load.

### Testing
- `./gradlew assembleDebug assembleRelease test` — **BUILD SUCCESSFUL**,
  89 tasks, zero failures.
- Version bumped to `2.4` (versionCode 6).

### Files Modified
- `mobile-webview/app/src/main/java/com/niterhub/dash/MainActivity.kt`
  (4 new WebView settings lines)
- `mobile-webview/app/build.gradle.kts` (versionCode 5→6, versionName 2.3→2.4)

---

## 136. Attendance Page Mobile Layout — Card Overflow, Video Scaling, Button/Input Sizing

**Date:** 24 August 2026
**Branch:** main

### Problem

The Class Attendance page had several mobile layout issues inside the Android
WebView: card containers overflowed the right edge on narrow viewports, the
camera `<video>` element didn't scale proportionally, action buttons shrank
below readable size, and the manual input row didn't fill the available width.

### Changes (`static/css/attendance.css`)

#### 1. Card container — prevent right-edge overflow
```css
.card {
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
}
```
On mobile (≤560px), padding tightened to `1rem`.

#### 2. Camera box video — proportional scaling
```css
.scanner-box video {
    width: 100%;
    height: auto;
    max-width: 100%;
    object-fit: cover;
}
```
The video stream now scales to the container width while preserving aspect
ratio, instead of stretching to fill height.

#### 3. Action buttons — flex-wrap with 45% minimum
```css
.scanner-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    width: 100%;
}
.scanner-actions .btn {
    flex: 1 1 45%;
}
```
Buttons stay side-by-side above 560px (each at least 45% wide), then stack
full-width below 560px.

#### 4. Manual input + submit — full-width on mobile
```css
@media (max-width: 560px) {
    .field-input {
        width: 100%;
        box-sizing: border-box;
    }
    .btn-primary {
        width: 100%;
        box-sizing: border-box;
    }
}
```
The session code input and "Mark Present" button now take the full card width
on small screens instead of sharing a cramped row.

### Testing
- `./gradlew assembleDebug assembleRelease test` — **BUILD SUCCESSFUL**, 89 tasks.
- `python manage.py test core.tests.AttendancePageTest` — **2/2 OK**.

### Files Modified
- `static/css/attendance.css` (card overflow fix, video scaling, button flex,
  input/button width)

---

## 137. E-Commerce Pharmacy Inventory & Medical Staff Logout

### Date
August 2026

### Summary
Added a full e-commerce-style **Pharmacy Product & Inventory Management** module to the
Medical Staff dashboard, plus a **functional logout button** on the medical staff sidebar.

### 1. Model Updates (`core/models.py`)

Added two fields to the existing `MedicineItem` model:

| Field | Type | Details |
|-------|------|---------|
| `image` | `ImageField` | `upload_to='pharmacy_products/'`, nullable, optional |
| `is_available` | `BooleanField` | Default `True` |

Migration `0048_medicineitem_image_medicineitem_is_available_and_more` created and applied.

### 2. CRUD Views & URLs (`host/views.py`, `host/urls.py`)

Six new views under the `host` namespace:

| View | URL Pattern | Method | Description |
|------|-------------|--------|-------------|
| `pharmacy_inventory` | `/host/medical/pharmacy/inventory/` | GET | Product catalog grid with live search, category filters, stock status |
| `pharmacy_product_add` | `/host/medical/pharmacy/inventory/add/` | GET/POST | Form with image upload (`enctype="multipart/form-data"`) |
| `pharmacy_product_edit` | `/host/medical/pharmacy/inventory/<pk>/edit/` | GET/POST | Edit pricing, stock, photo, availability |
| `pharmacy_product_delete` | `/host/medical/pharmacy/inventory/<pk>/delete/` | GET/POST | Confirmation + removal |
| `pharmacy_stock_toggle` | `/host/medical/pharmacy/inventory/<pk>/toggle/` | POST | AJAX-style availability toggle |
| `pharmacy_stock_adjust` | `/host/medical/pharmacy/inventory/<pk>/adjust/` | POST | +/- stock quantity adjustment |

### 3. Templates Created

| Template | Path | Description |
|----------|------|-------------|
| `pharmacy_inventory.html` | `templates/host/medical/` | Full inventory grid with search, filters, add/edit/delete buttons |
| `pharmacy_product_form.html` | `templates/host/medical/` | Add/Edit form with image upload, dark theme |
| `pharmacy_product_confirm_delete.html` | `templates/host/medical/` | Deletion confirmation with back button |

### 4. Medical Staff Sidebar Logout (`templates/host/host_base.html`)

Added to the MEDICAL MENU sidebar profile block:
- **Logout button** — Django POST form with CSRF token, routes to `{% url 'logout' %}`
- **Pharmacy Inventory** nav link — routes to `host:pharmacy_inventory`

### 5. UI Features
- Dark theme matching CampusDash design system
- Card layout with product image preview (or SVG pill placeholder fallback)
- Stock status badges: **In Stock** (green), **Low Stock** (amber), **Out of Stock** (red)
- Category tags with color coding
- Quick stock toggle (single-click) and quantity +/- adjustment
- Image upload with file preview

### Files Modified
- `core/models.py` — added `image` and `is_available` fields to `MedicineItem`
- `host/views.py` — added 6 inventory CRUD views + imports
- `host/urls.py` — added 6 URL patterns
- `templates/host/host_base.html` — added logout form + Pharmacy Inventory nav link
- `templates/host/medical/pharmacy_inventory.html` — **new** inventory grid
- `templates/host/medical/pharmacy_product_form.html` — **new** add/edit form
- `templates/host/medical/pharmacy_product_confirm_delete.html` — **new** delete confirmation

### Testing
- `python manage.py check` — **0 issues**
- `python manage.py migrate` — migration `0048` applied successfully
- URL reverse check — all 6 routes resolve correctly under `host:` namespace

---

## 138. Pharmacy Product Image Display Fix

### Date
August 2026

### Summary
Fixed the student-facing Online Pharmacy page (`/pharmacy/`) so uploaded product
images (via the new `MedicineItem.image` ImageField) display correctly in both the
catalog grid and the product detail modal.

### Root Cause
The catalog serializer (`_pharmacy_medicine_catalog()` in `core/views.py`) was
serializing `'image': item.image_url` — using only the legacy `image_url` text field.
The new `MedicineItem.image` ImageField (added in §137) was never referenced, so
uploaded product photos were invisible on the storefront.

### Fix Applied
**`core/views.py` — `_pharmacy_medicine_catalog()`** (line ~811):

```python
# Before:
'image': item.image_url,

# After:
'image': item.image.url if item.image else (item.image_url or None),
```

The ImageField `.url` property automatically prepends `MEDIA_URL` (`/media/`) and
returns the correct path. Falls back to the legacy `image_url` text field (static
placeholder paths like `/static/images/pharmacy/...`) when no upload exists.

### Media Files Serving
`config/urls.py` already includes:
```python
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
This serves uploaded files from `media/` in development. In production, WhiteNoise
or a CDN handles media.

### Store Template Image Handling (already correct)
The storefront JS in `templates/pharmacy/store.html` already handles both cases:

1. **Catalog grid** — `cardImage(m)` renders `<img>` with `onerror` fallback to
   `DEFAULT_MED_IMG` (`/static/images/pharmacy/default_medicine.png`).
2. **Product detail modal** — `openProduct(id)` renders `<img>` with the same
   `onerror` fallback when `item.image` is truthy.
3. **No image** — Renders a pill icon placeholder (`<i class="fa-solid fa-pills">`)
   inside a dark slate container.

### Verification
- `python manage.py check` — **0 issues**
- Catalog serializer returns correct URLs:
  - Uploaded images: `/media/pharmacy_products/aceplus.jpg`
  - Static placeholders: `/static/images/pharmacy/ceevit.png`, etc.

### Files Modified
- `core/views.py` — updated `_pharmacy_medicine_catalog()` image serialization

---

## 139. Pharmacy Product Detail Modal & Card Image Fixes

### Date
August 2026

### Summary
Fixed the product detail modal and catalog card image rendering on the student-facing
Online Pharmacy page (`/pharmacy/`) so uploaded product photos display correctly with
proper styling, fallback placeholders, and scrollable modal content.

### 1. Catalog Card Image Fix (`templates/pharmacy/store.html`)

**Before:** When no image existed, `cardImage(m)` returned an empty string — no
image container rendered at all, leaving a blank gap in the card.

**After:**
- When `m.image` exists → renders `<img>` with `onerror` that adds `.no-img` class
  to show the fallback pill icon
- When no image → renders a dark slate container with a visible pill icon placeholder
  (`<i class="fa-solid fa-pills">`)

```javascript
// Before:
if (!m.image) return '';

// After — shows pill placeholder when no image:
if (m.image) {
    return '<div class="med-img"><img ... onerror="this.parentElement.classList.add(\'no-img\');">...</div>';
}
return '<div class="med-img no-img"><span class="med-img-fallback" style="opacity:1"><i class="fa-solid fa-pills"></i></span></div>';
```

### 2. Product Detail Modal Image Fix (`templates/pharmacy/store.html`)

**Before:** Modal image had `object-fit: cover` with no padding — photos were cropped
and could overlap the title text below.

**After:**
- `<img>` styled with `max-height: 180px; object-fit: contain; padding: 8px;
  border-radius: 8px; background: rgba(0,0,0,0.2)` — photos display fully without
  cropping, with a subtle dark background and rounded corners
- When no image exists → pill icon placeholder is always shown (was previously
  rendering nothing)

### 3. Modal Header & Scroll Fix (`static/css/pharmacy.css`)

| Element | Before | After |
|---------|--------|-------|
| `.pd-img` (container) | Dark bg `#1f2937`, flex layout | Replaced with `.modal-img-container` — transparent, `text-align: center; padding: 12px 0` |
| `.pd-img img` | `object-fit: cover; max-height: 180px` + inline dark bg | `max-height: 160px; width: auto; object-fit: contain; margin: 0 auto` — no background box |
| `.pd-head` | `padding-top: 1rem` | `padding-top: 0` — title sits directly below image |
| `#product-modal .modal-card` | no scroll constraint | `max-height: 85vh; display: flex; flex-direction: column` |
| `#product-modal .product-detail` | unscrollable | `flex: 1; overflow-y: auto` — all sections scroll cleanly |
| Close button | `data-close` attribute only | Added `onclick="closeDetailsModal()"` + new JS function |

### 4. Media URL Verification

Already correctly configured:
- `config/urls.py`: `urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)`
- `config/settings.py`: `MEDIA_URL = '/media/'`, `MEDIA_ROOT = BASE_DIR / 'media'`
- Uploaded images served at `/media/pharmacy_products/...` in development

### 5. Close Button Fix (`templates/pharmacy/store.html`)

- Added `closeDetailsModal()` JS function that calls `closeModal('product-modal')`
- Close button wired via `onclick="closeDetailsModal()"`
- X button (`data-close="product-modal"`), backdrop click, and Escape key all
  still work via the existing delegated event listeners

### Files Modified
- `templates/pharmacy/store.html` — `.modal-img-container`, `closeDetailsModal()`, inline img style
- `static/css/pharmacy.css` — `.modal-img-container` replaces `.pd-img`, dark mode cleanup

---

## 140. CMS Dynamic Navigation — Per-Page Icons, Sort Order & Builder Toolbar

### Date
August 2026

### Summary
Enhanced the Website Builder / CMS so published pages flagged for navigation get
individual **icons** and **sort order** in the student portal navbar. Previously,
all nav pages used a hardcoded `fa-file-lines` icon and sorted alphabetically;
now each page carries its own `nav_icon` (FontAwesome name) and `nav_order`
(lower = further left).

### 1. Model Updates (`core/models.py`)

Two new fields on `EditablePage`:

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `nav_order` | `IntegerField` | `0` | Sort position in the nav menu (lower = left). Indexed. |
| `nav_icon` | `CharField(max_length=50)` | `'file-lines'` | FontAwesome icon name for the nav pill (e.g. `globe`, `book`, `flask`). |

Migration **0049** adds both fields. The existing `show_in_nav` (BooleanField,
db_index) and `is_published` (BooleanField) are unchanged — a page must be
both published AND flagged for nav to appear.

### 2. Context Processor (`core/context_processors.py`)

`custom_pages_nav` now orders by `nav_order, title` (was `title` only). The
`NAV_CUSTOM_PAGES` queryset is unchanged otherwise — still filtered to
`is_published=True, show_in_nav=True`.

### 3. Topbar Integration (`templates/partials/topbar.html`)

Both the **desktop Pages dropdown** and the **mobile profile menu** now render
the per-page icon:

```html
<i class="fa-solid fa-{{ item.nav_icon|default:'file-lines' }}"></i> {{ item.title }}
```

Instead of the previous hardcoded `<i class="fa-solid fa-file-lines"></i>`.

### 4. Builder Edit Page (`templates/builder/edit_page.html`)

Two new inputs in the toolbar, next to the existing "Show in Nav" toggle:

- **Order** — `<input type="number" id="pb-nav-order">` (min 0, step 1)
- **Icon** — `<input type="text" id="pb-nav-icon">` (maxlength 50, placeholder
  `file-lines`)

Both pre-populated from the page object. The page manager JS
(`static/js/builder/page_manager.js`) sends `nav_order` and `nav_icon` in the
`savePage()` payload alongside `show_in_nav`.

### 5. Page Save API (`core/views.py` → `builder_page_save`)

Accepts optional `nav_order` (int) and `nav_icon` (string, max 50) in the JSON
payload. Only present keys are written. Response includes both fields.

### 6. Admin CMS Dashboard (`templates/admin/content.html`)

The Builder Pages table now has two additional columns:

- **Icon** — shows `fa-{icon} {icon_name}` when in nav, `—` otherwise
- **Order** — shows the nav_order number when in nav, `—` otherwise

The "In Nav" column badge is now green with a checkmark (`Active`) instead of
the plain `In nav` text badge.

### 7. Django Admin (`core/admin.py`)

`EditablePageAdmin.list_display` now includes `nav_order` and `nav_icon` for
visibility in the Django admin changelist.

### Files Modified

- `core/models.py` — `nav_order`, `nav_icon` fields
- `core/migrations/0049_editablepage_nav_order_nav_icon.py` — new migration
- `core/context_processors.py` — `order_by('nav_order', 'title')`
- `core/views.py` — `builder_page_save` handles `nav_order` + `nav_icon`
- `core/admin.py` — `list_display` extended
- `templates/partials/topbar.html` — per-page icon in desktop dropdown + mobile menu
- `templates/builder/edit_page.html` — Order + Icon toolbar inputs
- `templates/admin/content.html` — Icon + Order columns, green Active badge
- `static/js/builder/page_manager.js` — `savePage()` sends `nav_order` + `nav_icon`

### Verification

- `python manage.py check` — **0 issues**
- `makemigrations --check` — **no drift**
- 62 targeted tests (CustomPagesNav, BuilderPageManager, WYSIWYG, BlockLibrary,
  UnifiedHeader, SecurityAudit) — **all pass**
- `node --check page_manager.js` — **syntax OK**

---

## 141. CMS WYSIWYG Integration — End-to-End Tests for System Pages, AJAX Save & Live Rendering

### Date
August 2026

### Summary
The full Website Builder CMS WYSIWYG pipeline — system page auto-registration,
feature block seeding, the visual editor (`/builder/visual/<slug>/`), the
WYSIWYG save endpoint (`POST /api/builder/pages/<id>/save/`), the CMS context
processor (`cms_system_blocks`), and the template zone (`cms/system_zone.html`)
— was already fully implemented across §53, §103, §109, §117 and §119. This
task audits that pipeline end-to-end and adds **four integration tests**
that prove the full round-trip: seed → edit → persist → render.

### Existing Pipeline (verified, no code changes)

| Component | Where | Behaviour |
|---|---|---|
| System page registry | `core/system_pages.py` | Auto-registers 5 core routes (home, study-corner, pharmacy, news, clubs) as `EditablePage` rows keyed by `system_key`; seeds `ContentBlock`s with `content_json` + rendered default `content_html`; blocks start `visible=False` |
| CMS context processor | `core/context_processors.py` → `cms_system_blocks` | Maps `request.resolver_match.url_name` to `SYSTEM_ROUTE_KEYS`, loads visible blocks, renders via `render_block_html`, returns as `cms_blocks` |
| Template zone | `templates/cms/system_zone.html` | Included in all 5 student-facing templates (`index.html`, `study_corner.html`, `store.html`, `news.html`, `clubs.html`); renders `cms_blocks` inside a `cms-system-zone` section; empty when no blocks are visible → default template content shows through |
| Visual editor | `/builder/visual/<slug>/` → `editor.html` + `editor.js` | Split-screen WYSIWYG: iframe of the real student page (`?preview=1` shows hidden blocks), double-click text → `contenteditable`, floating style toolbar, sidebar ↔ canvas bidirectional editing |
| WYSIWYG save | `POST /api/builder/pages/<id>/save/` → `builder_page_wysiwyg_save` | Persists `content_html` / `content_json` / `style_json` per block via sanitized `_save_content_block_data` path; toggles `is_published`; flushes compiled-template caches |
| Block visibility | `ContentBlock.visible` | Public routes skip hidden blocks; `?preview=1` shows all for users with builder permission; admin reveals from Block Manager |

### New Tests (`core/tests.py` → `CmsWysiwygIntegrationTest`)

#### Test 1: `test_all_system_pages_exist_with_default_content`
Verifies all 5 core system pages are registered with the correct feature blocks,
published status, non-empty `content_json` (seeded data), and non-empty
`content_html` (rendered default layout). Covers home (3 blocks), study-corner
(3), pharmacy (4), news (3), clubs (1).

#### Test 2: `test_ajax_save_updates_pharmacy_block_headline`
POSTs to the WYSIWYG save endpoint (`/api/builder/pages/<id>/save/`) with an
edited `content_json` payload for the pharmacy `hero-promo` block → verifies the
block's headline is persisted to the database.

#### Test 3: `test_pharmacy_page_renders_updated_cms_text`
Updates a CMS block's `content_json['headline']` and sets `visible=True` →
simulates an admin editing + revealing a section → student GET to `/pharmacy/`
returns the customized text inside the `cms-system-zone` section.

#### Test 4: `test_home_page_renders_updated_cms_text`
Same flow for the home `hero-banner` block → student GET to `/` returns the
updated headline text.

### Test Flow Diagram

```
register_system_pages()          admin edits block
        │                              │
        ▼                              ▼
 EditablePage + ContentBlock     POST /api/builder/pages/<id>/save/
 (visible=False, seeded)         → content_json updated, cache flushed
        │                              │
        ▼                              ▼
 Test 1: all 5 pages exist     Test 2: headline persisted
        │                              │
        ▼                              ▼
 block.visible = True          GET /pharmacy/ or GET /
        │                              │
        ▼                              ▼
 Test 3 & 4: CMS text renders on student pages
```

### Files Modified

- `core/tests.py` — added `CmsWysiwygIntegrationTest` (4 tests)

### Verification

- `python manage.py check` — **0 issues**
- `makemigrations --check` — **no drift**
- 18 targeted tests (RegisterSystemPages 8, ContentBlockVisibility 5,
  CmsWysiwygIntegration 4, + 1 shared) — **all pass**
- No model/view/template changes required — the pipeline was already complete

---

## 142. News Visual Builder Fix — Live Student Layout in Editor Canvas + CMS Text Binding

### Date
August 2026

### Summary
Fixed the Global News visual builder (`/builder/visual/news/`) so the editor
canvas renders the **actual live student `/news/` page** — with real news feed,
video cards, and search bar — instead of the generic `/page/news/` builder
template showing only CMS block placeholders. Also wired the student-facing
templates to pull editable text from CMS `content_json` with graceful fallback
defaults.

### Problem
The visual editor iframe loaded `{% url 'editable_page' page.slug %}?preview=1`
which resolved to `/page/news/?preview=1` — a generic builder template that
only rendered CMS `ContentBlock` markup. The real student news page at `/news/`
has a completely different layout: topbar, intro section, live NewsAPI feed,
YouTube video cards, and client-side search. Admins editing the news page in
the builder saw none of this.

### Changes

#### 1. Visual editor iframe loads the real system route (`core/views.py`)

`visual_editor` now resolves the system route URL for pages with a `system_key`:

```python
system_route_url = None
if page.system_key:
    view_name = {v: k for k, v in SYSTEM_ROUTE_KEYS.items()}.get(page.system_key)
    if view_name:
        system_route_url = reverse(view_name)
```

The `system_route_url` is passed to the template context. For the news page,
this resolves to `/news/`.

#### 2. Editor template uses system route (`templates/builder/editor.html`)

The iframe `src` now checks for `system_route_url`:

```html
{% if system_route_url %}
<iframe src="{{ system_route_url }}?builder=1&preview=1" ...>
{% else %}
<iframe src="{% url 'editable_page' page.slug %}?preview=1" ...>
{% endif %}
```

System pages load their real student route with `?builder=1&preview=1`;
non-system pages keep the generic builder route unchanged.

#### 3. CMS context processor shows hidden blocks in preview mode
(`core/context_processors.py` → `cms_system_blocks`)

When the editor iframe loads `/news/?preview=1`, the context processor now
includes **all** CMS blocks (including `visible=False`) so the canvas renders
the full page layout — not just the subset an admin has already revealed:

```python
is_preview = (
    request.GET.get('preview') == '1'
    and request.user.has_perm('core.change_editablepage')
)
block_qs = page.content_blocks.order_by('order', 'id')
if not is_preview:
    block_qs = block_qs.filter(visible=True)
```

Regular student visitors (no `?preview=1` or no builder permission) still
see only `visible=True` blocks — no change to the public rendering.

#### 4. News view passes CMS block content (`core/views.py` → `news_page`)

The news view now loads the CMS system page and builds a `cms_content` dict
mapping each visible block's `element_id` → `content_json`. The template can
reference these values inline with `|default` filters for hardcoded fallbacks:

```python
cms_content = {}
page = EditablePage.objects.filter(system_key='news').first()
if page:
    for block in page.content_blocks.filter(visible=True):
        cms_content[block.element_id] = block.content_json or {}
```

#### 5. News template binds to CMS content (`templates/news.html`)

The intro section now pulls from `cms_content.news_search`:

```html
<h1 data-editable-id="news-search">
    {{ cms_content.news_search.title|default:"Global News" }}
</h1>
<p>{{ cms_content.news_search.subtitle|default:"Top headlines from around the world…" }}</p>
```

When no CMS content is set, the hardcoded defaults render. When an admin
edits the `news-search` block's `content_json` and reveals it, the custom
title appears on the live page.

#### 6. Global news partial section headers (`templates/partials/global_news.html`)

Section headers bind to their respective CMS blocks:

- **Global News heading** → `cms_content.image-card-grid.title` (default: "Global News")
- **Video News heading** → `cms_content.video-feed.title` (default: "Video News")

Both carry `data-editable-id` attributes so the WYSIWYG editor can target
them for inline editing.

### End-to-End Flow

```
Admin opens /builder/visual/news/
        │
        ▼
Editor loads /news/?builder=1&preview=1 in iframe
(→ cms_system_blocks returns ALL blocks including hidden ones)
(→ news.html renders live feed + video cards + search bar)
(→ intro section binds to cms_content.news_search.title)
        │
        ▼
Admin double-clicks text → contenteditable → edits title
        │
        ▼
Admin clicks "Save Changes"
→ POST /api/builder/pages/<id>/save/
→ content_json updated in DB, template caches flushed
        │
        ▼
Student visits /news/
→ cms_system_blocks loads visible blocks (no preview mode)
→ news.html renders cms_content.news_search.title (or default)
→ global_news.html renders cms_content.image-card-grid.title
```

### Files Modified

- `core/views.py` — `visual_editor` passes `system_route_url`; `news_page` passes `cms_content`
- `core/context_processors.py` — `cms_system_blocks` preview-mode block visibility
- `templates/builder/editor.html` — iframe `src` uses system route when available
- `templates/news.html` — intro section binds to `cms_content.news_search`
- `templates/partials/global_news.html` — section headers bind to `cms_content`
- `core/tests.py` — added `NewsBuilderIntegrationTest` (6 tests)

### Tests (`NewsBuilderIntegrationTest`)

| Test | What it verifies |
|---|---|
| `test_visual_editor_iframe_loads_real_news_route` | Editor canvas iframe src is `/news/?builder=1&preview=1`, not `/page/news/` |
| `test_wysiwyg_save_updates_news_search_title` | POST to WYSIWYG save updates `news-search` block's `content_json` |
| `test_live_news_renders_updated_section_title` | After save + reveal, student GET to `/news/` returns updated `image-card-grid` title |
| `test_live_news_renders_updated_video_feed_title` | After save + reveal, student GET to `/news/` returns updated `video-feed` title |
| `test_preview_mode_shows_hidden_blocks_for_editors` | `?preview=1` includes hidden blocks for builder-permissioned users |
| `test_news_intro_uses_cms_content_with_defaults` | Intro h1 falls back to "Global News" when no CMS content is set |

### Verification

- `python manage.py check` — **0 issues**
- `node --check editor.js` — **syntax OK**
- 10 targeted tests (NewsBuilderIntegration 6, CmsWysiwygIntegration 4) — **all pass**

---

## 143. Visual Builder Extended to All 11 Navbar Routes — System Pages, Frame Security & CMS Zone

### Date
August 2026

### Summary
Extended the Website Builder visual editor to cover **all 11 student navbar
routes** so every page can be edited inline from `/builder/visual/<slug>/`. The
SYSTEM_PAGES registry grew from 5 to 13 entries, `@xframe_options_sameorigin`
was added to 8 remaining views, and `{% include 'cms/system_zone.html' %}` was
added to 8 student templates that were missing it.

### Changes

#### 1. SYSTEM_PAGES registry (`core/system_pages.py`)

8 new entries added (bringing total from 5 to 13):

| key | slug | view_name | route_url | blocks |
|---|---|---|---|---|
| `dashboard` | `dashboard` | `student_dashboard` | `/dashboard/student/` | `welcome-banner` (hero) |
| `departments` | `departments` | `departments` | `/departments/` | `dept-hero` (hero) |
| `research-ai` | `research-ai` | `research_ai` | `/research-ai/` | `research-hero` (hero) |
| `notices` | `notices` | `notices` | `/notices/` | `notices-hero` (hero) |
| `transport` | `transport` | `transport_dashboard` | `/transport/` | `transport-hero` (hero) |
| `meals` | `meals` | `meal_dashboard` | `/meals/` | `meals-hero` (hero) |
| `medical` | `medical` | `medical` | `/medical/` | `medical-hero` (hero) |
| `attendance` | `attendance` | `attendance` | `/attendance/` | `attendance-hero` (hero) |

Each entry seeds one hero-type `ContentBlock` with `visible=False` so the
default template content is preserved until an admin reveals a block.

#### 2. Frame security — `@xframe_options_sameorigin` (`core/views.py`)

Added to 8 views that were missing it (the original 5 + `editable_page_view`
+ `study_material_file` already had it):

- `student_dashboard`
- `medical`
- `notices`
- `transport_dashboard`
- `meal_dashboard`
- `research_ai_page`
- `departments_directory`
- `attendance_dashboard`

All 11 student navbar routes now respond with `X-Frame-Options: SAMEORIGIN`
so the builder canvas can embed them in a same-origin iframe.

#### 3. CMS zone added to 8 student templates

`{% include 'cms/system_zone.html' %}` inserted after the intro section in:

- `templates/dashboard/home.html`
- `templates/transport.html`
- `templates/meals.html`
- `templates/medical/booking.html`
- `templates/notices/notices.html`
- `templates/research_ai.html`
- `templates/attendance.html`
- `templates/departments.html`

All 11 student navbar templates now include the CMS zone, so customized
blocks render on the live page after an admin reveals them from the Block
Manager.

#### 4. Visual editor iframe (`core/views.py` → `visual_editor`)

The `visual_editor` view resolves `system_route_url` for any page with a
`system_key`, and `templates/builder/editor.html` uses it for the iframe
`src` with `?builder=1&preview=1`. This was previously only wired for the
original 5 system pages; it now works for all 13.

### Tests (`AllNavbarRoutesBuilderIntegrationTest`)

| Test | Coverage |
|---|---|
| `test_all_11_system_pages_registered` | All 11 navbar routes have an `EditablePage` with `system_key` and ≥1 content block |
| `test_all_11_routes_set_xframe_sameorigin` | Every navbar route returns `X-Frame-Options: SAMEORIGIN` |
| `test_visual_editor_loads_real_routes_for_all_pages` | Editor iframe src contains `builder=1` + `preview=1` for all 11 pages |
| `test_cms_blocks_render_after_reveal_on_all_pages` | After revealing a block, `cms-system-zone` renders on the student page |
| `test_wysiwyg_save_updates_content_json_for_all_pages` | Direct `content_json` save persists on every system page |

Also fixed `RegisterSystemPagesTest` for the expanded registry (5→13 pages).

### Files Modified

- `core/system_pages.py` — 8 new SYSTEM_PAGES entries
- `core/views.py` — 8 new `@xframe_options_sameorigin` decorators
- `core/tests.py` — `AllNavbarRoutesBuilderIntegrationTest` (5 tests) + `RegisterSystemPagesTest` fix
- `templates/dashboard/home.html` — CMS zone
- `templates/transport.html` — CMS zone
- `templates/meals.html` — CMS zone
- `templates/medical/booking.html` — CMS zone
- `templates/notices/notices.html` — CMS zone
- `templates/research_ai.html` — CMS zone
- `templates/attendance.html` — CMS zone
- `templates/departments.html` — CMS zone

### Verification

- `python manage.py check` — **0 issues**
- 26 targeted tests (RegisterSystemPages 8, NewsBuilderIntegration 6, CmsWysiwygIntegration 4, AllNavbarRoutes 5, ContentBlockVisibility 3) — **all pass**
