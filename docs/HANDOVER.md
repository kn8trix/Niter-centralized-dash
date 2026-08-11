# Niter Centralized Dash - Handover Document

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
    - **Clubs & Events:** Club discovery + executive workspace (`/clubs/`).
- **Footer:** User profile section with avatar and logout option (posts to `/logout/` when signed in).

### 3.2 Main Content Area
- **Margin:** Offset by `256px` on desktop (`lg:ml-64`); full-width on mobile (`ml-0`) so content reflows when the drawer is hidden.
- **Header:** Sticky top bar with page title, global search, and notification bell. On mobile the hamburger sits inline next to the title and the search bar wraps to its own row.
- **Grid System:** Responsive grid using Tailwind CSS utility classes.

## 4. Implemented Templates

### 4.1 Dashboard Home (`templates/dashboard/home.html`)
A comprehensive student dashboard with:
- **Welcome Banner:** Personalized greeting with "+ Quick Action" button.
- **3-Column Grid:**
    - Meal Ratio Counter (140/200 slots with progress bar).
    - Transport Service (Bus Route 1 - 8:00 AM with "Reserve Seat" button).
    - Medical Center (Doctor availability with "Book Slot" button).
- **Bottom Split Section:**
    - Recent Official Notices (with status badges: Urgent, General, Event).
    - Quick Links to Academic Notes (CS101, Mathematics, Physics Lab, Programming).

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
    - Sticky sidebar showing scheduled appointments.
    - Status badges (Confirmed/Pending) with color coding.
    - Appointment details (Doctor, Date, Time).

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
- **Doctor Schedule:** Doctor list with specialty, working days, and availability status — **backend pending**.
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
| **Research AI** | [http://127.0.0.1:8000/research-ai/](http://127.0.0.1:8000/research-ai/) | Academic research & thesis assistant (frontend-only) |
| **Departments** | [http://127.0.0.1:8000/departments/](http://127.0.0.1:8000/departments/) | Department directory & hub (`/departments/<slug>/`) |
| **Builder** | [http://127.0.0.1:8000/builder/](http://127.0.0.1:8000/builder/) | Website Builder dashboard (super-admin) + `/builder/edit/<slug>/` editor |
| **Builder Pages** | [http://127.0.0.1:8000/page/<slug>/](http://127.0.0.1:8000/page/<slug>/) | Public render of builder-authored pages (e.g. `/page/research-ai/`) |

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
- **REAL-TIME:** `ASGI_APPLICATION = 'config.asgi.application'`; `CHANNEL_LAYERS` uses **`channels_redis`** when a reachable `REDIS_URL` is configured, otherwise falls back to `InMemoryChannelLayer` (startup ping probe; `notify_user` never raises on a runtime outage)
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
REDIS_URL=redis://127.0.0.1:6379/0     # unset/unreachable → in-memory channel layer
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
| GET | `/api/clubs/sheet/` | Fetch club Google Sheet records (`@login_required`) |
| POST | `/api/clubs/sheet/append/` | Append a row to the club Google Sheet (`@login_required`) |
| GET | `/api/builder/create-page/` | Super-admin: create a builder page |
| POST | `/api/builder/save-block/` | Super-admin: save a ContentBlock |
| POST | `/api/builder/save-css/` | Super-admin: save page custom CSS |
| POST | `/api/cafeteria/redeem/` | Staff: validate a `#MEAL-XXXX` token, mark `is_redeemed=True` + `redeemed_at` (`redeem_meal_ticket`) |
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
| POST | `/api/research/query/` | Student: structured research responses (topic, markdown, IEEE/APA7/Harvard/Chicago references) |
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
- **Research AI** — `POST /api/research/query/` returns structured responses with style-aware references
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
3. **~~LOW — Medical admin chat~~ — DONE in §39**: persistent patient–doctor consultation threads (models + REST + WebSockets). The doctor-schedule and content-management panels in the admin dashboard remain mock.
4. **LOW — Research AI persisted threads & real LLM**: `/api/research/query/` is deterministic server-side (no external AI calls); persisted thread history + an actual LLM integration would be the next step.
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
   - Fresh clones must run `venv/bin/python manage.py migrate` and recreate users before real logins work.

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
- Demo users recreated locally (`db.sqlite3` is gitignored): `admin` / `admin123` (staff) and `student` / `student123`. See `.freebuff/run.md` for the one-liner to recreate them.
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
| `build.sh` | Render build command (executable): pip install → collectstatic → migrate |
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

"$PYTHON" -m pip install -r requirements.txt
RENDER_BUILD=true "$PYTHON" manage.py collectstatic --noinput
RENDER_BUILD=true "$PYTHON" manage.py migrate
```

**Hardening** (`chmod +x build.sh`): `errexit` + `pipefail` abort the build on
any failing step; `RENDER_BUILD=true` tells settings.py this is the **build
phase**, so `collectstatic`/`migrate` succeed even before Render injects the
service's generated `SECRET_KEY` (see below). Verified locally: `./build.sh`
installs (no-op when satisfied), collects 147 static files, applies migrations,
and exits `Build complete`.

### Settings Changes (`config/settings.py`)

Render injects `RENDER=true` for every service. When present, the app **appends** the platform host `.onrender.com`, the production custom domain `niter.edu.bd` (+ `www.`), and `localhost`/`127.0.0.1` to `ALLOWED_HOSTS`; `CSRF_TRUSTED_ORIGINS` gets `https://*.onrender.com` plus `https://niter.edu.bd` / `https://www.niter.edu.bd`. The block only ever **appends** — env-provided hosts still pass through untouched. Non-Render environments (local dev/tests) are unaffected. Verified: `RENDER=true` → `ALLOWED_HOSTS=['.onrender.com','niter.edu.bd','www.niter.edu.bd','localhost','127.0.0.1']`, `CSRF_TRUSTED_ORIGINS=['https://*.onrender.com','https://niter.edu.bd','https://www.niter.edu.bd']`; without `RENDER` → unchanged.

**Build-time SECRET_KEY fallback.** `SECRET_KEY` still **fails closed** at
runtime (`ImproperlyConfigured` when `DEBUG=false` and no secret), but when
`RENDER_BUILD=true` (set only by `build.sh`, never by the start command) a
throwaway placeholder key is used so the build's `collectstatic`/`migrate`
run cleanly even if the env var hasn't loaded yet. Probes (`.env` moved aside):
`DEBUG=false RENDER_BUILD=true` → check OK; `DEBUG=false` alone →
`ImproperlyConfigured`; `DEBUG=true` → dev fallback key. This is defense-in-depth
— Render's `generateValue` secret is normally injected before the build runs.

WhiteNoise (`CompressedStaticFilesStorage`, middleware) already serves collected static in production — no changes needed; `build.sh` runs `collectstatic` so `staticfiles/` is fresh on every deploy.

### Deploying (First Launch)

1. Commit and push `render.yaml` + `build.sh` (plus the settings/requirements changes) to the GitHub repo (`kn8trix/Niter-centralized-dash`).
2. In the Render dashboard: **New + → Blueprint → select the repo** → Render validates the Blueprint and creates all three resources.
3. First deploy runs `build.sh`: pip install → collectstatic → migrate (seeded departments/clubs come via migration `0009`).
4. Open `https://niter-centralized-dash.onrender.com`. Create the admin with `python manage.py createsuperuser` — easiest via a one-off command in the Render **Shell** tab, or temporarily via `DJANGO_SUPERUSER_*` env vars + `createsuperuser --noinput`.

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

1. **Render Blueprint deployment** — `render.yaml` (web service + managed PostgreSQL + managed Redis, `domains: [niter.edu.bd]`), executable `build.sh` (pip install → collectstatic → migrate), `RENDER=true` auto-config in `config/settings.py` (appends `.onrender.com` + `niter.edu.bd`/`www` to `ALLOWED_HOSTS` and CSRF origins), `psycopg2-binary` Postgres driver. → §38
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
