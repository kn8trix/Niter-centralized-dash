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
    - Search bar for filtering files.
    - Upload button for new documents.
    - Folder tree (Computer Science, Mathematics).
    - Recent PDF list with metadata.
- **Main Pane (Markdown Editor):**
    - Title input field.
    - Action buttons: "Generate AI Summary", "Extract Keywords", "Export as PDF".
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
- **Mock actions** via query params with Django `messages` feedback (no DB changes yet).

### 4.9 Medical Admin Dashboard (`templates/host/medical/admin_dashboard.html`)
Admin-only medical management interface at `/medical/admin/` with:
- **Summary Cards:** Total, Pending, Confirmed, and Cancelled appointment counts.
- **Appointment Management:** Multi-field filter form (keyword, student name, student ID, date, status, department, doctor) and a table with Confirm / Cancel / View Details actions.
- **Appointment Details Panel:** Full student and appointment info (contact, reason, doctor, booking time).
- **Medical Chat Management:** Mock chat threads with statuses (Active, Waiting, Resolved).
- **Doctor Schedule:** Doctor list with specialty, working days, and availability status.
- **Medical Content Management:** Mock content sections (Health Tips, Disease Awareness, First Aid, Medical Facilities, Emergency Contacts, Medical News).
- **Home Page Medical Information:** Mock editable sections for the medical center's public pages.

### 4.10 Clubs & Events (`templates/clubs.html`)
Frontend-only Club & Event dashboard at `/clubs/` — a standalone page (own `clubs.css`, exact warm palette `#faf9f6` / `#ffffff` / `#f0ebe1` / `#e8e2d8`) driven entirely by mock JavaScript data (no backend/database):
- **Student View:**
    - Featured clubs showcase (Computer Club, Electronics Club, Cultural Society, Sports Club) rendered from JS with active status badges and member counts.
    - Upcoming events grid (date, time, location, description, fee tags "Free" / "৳200 BDT") with a "Register Now" button that opens a mock registration modal (Student Name, Student ID, Payment Method bKash/Nagad, Trx ID).
- **Club Executive Workspace:**
    - Stat summary cards: Total Members, Active Registrations, Event Revenue, Pending Approvals.
    - Mock registrations & payment tracking table (student name/ID, event, bKash/Nagad + TrxID chips, amount, Verified / Pending Review badges) rendered from JS.
    - Announcement Publisher form (title, target audience dropdown, details) with mock confirmation toast.
- The view (`clubs_dashboard`) is a pure stub rendering `clubs.html`; toggle + modal + toast are client-side vanilla JS with mock data arrays in the template.

### 4.11 Transport Online Ticket System (`templates/transport.html`)
Standalone frontend-only transport booking dashboard at `/transport/` (`static/css/transport.css`, mock JS data):
- **Live Status Tracker** — pulsing status badges per route ("On Time" green, "In Transit" blue, "Arriving in 10 mins" amber).
- **Bus Routes & Schedules** — route cards (Route 1: Campus → Town Center, etc.) with driver info, departure times, and color-coded live seats badges ("12 / 40 seats left").
- **Seat Selector / Booking Form** — route dropdown, trip-time chips, passenger name, and a clickable 40-seat grid (booked seats disabled); "Book Seat" validates and generates the pass, then live-updates seats-left on the route cards.
- **Digital Boarding Pass** — visual QR ticket (deterministic SVG QR placeholder) showing passenger, route, assigned seat, departure time, and token.

### 4.12 Online Meal Ticket System (`templates/meals.html`)
Standalone frontend-only meal ticket dashboard at `/meals/` (`static/css/meals.css`, mock JS data):
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
- **Backend:** Django 6.0
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
pip install django

# 4. Run the development server
python manage.py runserver 0.0.0.0:8000

# 5. Open your browser
# Navigate to: http://127.0.0.1:8000/
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
| **Settings** | [http://127.0.0.1:8000/settings/](http://127.0.0.1:8000/settings/) | Account settings (password change, toggles, theme) |
| **Sign Up** | [http://127.0.0.1:8000/signup/](http://127.0.0.1:8000/signup/) | Student sign-up (creates account + profile) |
| **Profile** | [http://127.0.0.1:8000/profile/](http://127.0.0.1:8000/profile/) | Virtual student ID card + booking history |
| **System Admin** | [http://127.0.0.1:8000/admin-dashboard/](http://127.0.0.1:8000/admin-dashboard/) | Staff-only dashboard (users, notices, transport, security) |
| **Cafeteria Admin** | [http://127.0.0.1:8000/cafeteria/admin/](http://127.0.0.1:8000/cafeteria/admin/) | Staff-only meal slots, inventory, QR redemption |
| **Club Management** | [http://127.0.0.1:8000/clubs/manage/](http://127.0.0.1:8000/clubs/manage/) | Staff-only club executive workspace |

### Troubleshooting
- **Port already in use:** Use `python manage.py runserver 8080` to run on a different port.
- **ModuleNotFoundError:** Ensure virtual environment is activated (`source venv/bin/activate`).
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
│   ├── settings.py              # Django settings
│   ├── urls.py                  # Main URL configuration
│   └── wsgi.py                  # WSGI application
├── core/
│   ├── __init__.py
│   ├── models.py                # StudentProfile (student ID + department, 1:1 User)
│   ├── views.py                 # View functions
│   ├── urls.py                  # App URL routes
│   ├── context_processors.py    # Centralized ENDPOINTS registry
│   └── migrations/
│       └── 0001_initial.py      # StudentProfile
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
- **DEBUG:** `True` (development mode)
- **ALLOWED_HOSTS:** `[]` (add your domain in production)
- **INSTALLED_APPS:** `django.contrib.staticfiles`, `django.contrib.contenttypes`, `django.contrib.auth`, `django.contrib.sessions`, `core`
- **MIDDLEWARE:** Security, Session, Common, Csrf, Auth
- **TEMPLATES DIRS:** `[BASE_DIR / 'templates']`
- **DATABASES:** SQLite (`db.sqlite3`) — required for Django auth (run `manage.py migrate` first)
- **AUTH SETTINGS:** `LOGIN_URL='/login/'`, `LOGIN_REDIRECT_URL='/dashboard/'`, `LOGOUT_REDIRECT_URL='/'`

### Environment Variables (Recommended for Production)
Create a `.env` file in the root directory:
```env
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgres://user:pass@localhost:5432/niter_db
```

## 10. Git Repository
- **Repository:** [https://github.com/kn8trix/Niter-centralized-dash](https://github.com/kn8trix/Niter-centralized-dash)
- **Branch:** `main` (work-in-progress lives on `taj` and gets merged into `main`)
- **Git Ignore:** `venv/`, `.venv/`, `__pycache__/`, `*.pyc`, `.env`, `db.sqlite3`

## 11. API Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | `/claim-meal/` | Claim a meal ticket |
| POST | `/book-transport/` | Book a transport ticket |
| POST | `/book-appointment/` | Schedule a medical appointment |
| GET | `/api/notices/` | Fetch official notices |
| GET | `/api/courses/` | Fetch course materials |
| GET | `/` | Public homepage (glassmorphism landing page) |
| GET | `/dashboard/` | Student dashboard (moved from `/`) |
| GET | `/clubs/` | Clubs & Events (frontend-only) |
| GET | `/transport/` | Transport ticket system (frontend-only) |
| GET | `/meals/` | Meal ticket system (frontend-only) |
| GET | `/medical/admin/` | Medical admin dashboard (implemented) |
| GET | `/host/medical/` | Medical host dashboard (implemented) |
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

### Remaining Internal Pages (UI)
1. **5 Department Student Dashboards** - one dashboard per department (CSE, TEX, IPE, FD, EEE).
2. ~~**Club Admin Dashboard**~~ — **done (see section 31):** `/clubs/manage/` now provides the role-gated club executive workspace.
3. ~~**Meal System (Admin/Kitchen side)**~~ — **done (see section 31):** `/cafeteria/admin/` covers meal slots, kitchen inventory, and QR redemption.
4. **Visual Builder / Editor Integration** - the public homepage is now fully tagged with `data-widget-id` / `data-editable-field`; wire the standalone WYSIWYG editor to it and the app templates (`data-widget`/`data-component` tags) next.

### Backend & Infrastructure
5. **Backend Integration:** Connect templates to Django views and models (most flows are still mock-only).
6. **Database Models:** Design models for users, courses, tickets, and appointments.
7. **Role-based Access Control:** Login/logout (section 20) plus `@login_required` on `/profile/` + `/settings/` and `@staff_member_required` on `/admin-dashboard/`, `/cafeteria/admin/`, `/clubs/manage/` (section 31). Remaining: host-portal gating and a full student/staff/admin permission model.
8. **API Development:** Create endpoints for meal claims, transport bookings, and appointments.
9. **Real-time Updates:** WebSocket for live notifications and seat availability.
10. **Deployment:** Configure for production (env vars, ALLOWED_HOSTS, static files).

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