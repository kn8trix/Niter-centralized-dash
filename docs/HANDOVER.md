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
    - **Bus & Meal Tickets:** Campus service management.
    - **Medical Booking:** Appointment scheduling.
- **Footer:** User profile section with avatar and logout option.

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
| **Public Homepage** | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) | Glassmorphism landing page (public nodes) |
| **Dashboard** | [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/) | Main student dashboard (moved from `/`) |
| **Academic & Notes** | [http://127.0.0.1:8000/academic-notes/](http://127.0.0.1:8000/academic-notes/) | Courses & assignments |
| **Official Notices** | [http://127.0.0.1:8000/notices/](http://127.0.0.1:8000/notices/) | Announcements & events |
| **Tickets** | [http://127.0.0.1:8000/tickets/](http://127.0.0.1:8000/tickets/) | Meal & transport tickets |
| **Medical** | [http://127.0.0.1:8000/medical/](http://127.0.0.1:8000/medical/) | Appointment booking |
| **Notes Engine** | [http://127.0.0.1:8000/notes/](http://127.0.0.1:8000/notes/) | Notes engine |
| **Medical Admin** | [http://127.0.0.1:8000/medical/admin/](http://127.0.0.1:8000/medical/admin/) | Medical admin dashboard |
| **Medical Host** | [http://127.0.0.1:8000/host/medical/](http://127.0.0.1:8000/host/medical/) | Medical host dashboard (`/host/` redirects here) |

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
│   ├── views.py                 # View functions
│   ├── urls.py                  # App URL routes
│   └── context_processors.py    # Centralized ENDPOINTS registry
├── host/
│   ├── __init__.py
│   ├── views.py                 # Host portal views (medical host + admin dashboards)
│   ├── urls.py                  # Host app URL routes
│   └── tests.py                 # Host app tests
├── static/
│   └── css/
│       ├── theme.css            # Global design tokens (:root variables)
│       └── main.css             # Public homepage glassmorphism styles
├── templates/
│   ├── index.html               # Public homepage (glass hero, about/medical nodes)
│   ├── base.html                # Base template with sidebar & header
│   ├── dashboard/
│   │   └── home.html            # Student dashboard
│   ├── academic/
│   │   └── notes.html           # Academic materials & courses
│   ├── notices/
│   │   └── notices.html         # Official announcements
│   ├── ticketing/
│   │   └── tickets.html         # Meal & transport tickets
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
- **INSTALLED_APPS:** `django.contrib.staticfiles`, `core`
- **TEMPLATES DIRS:** `[BASE_DIR / 'templates']`
- **DATABASES:** `{}` (no database configured yet)

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
- **Git Ignore:** `venv/`, `.venv/`, `__pycache__/`, `*.pyc`, `.env`

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
| GET | `/medical/admin/` | Medical admin dashboard (implemented) |
| GET | `/host/medical/` | Medical host dashboard (implemented) |
| GET | `/host/` | Host portal index (redirects to medical host dashboard) |

## 12. Next Steps

### Remaining Internal Pages (UI)
1. **5 Department Student Dashboards** - one dashboard per department (CSE, TEX, IPE, FD, EEE).
2. **Club Admin Dashboard** - student club management view.
3. **Meal System (Admin/Kitchen side)** - meal management beyond the student claim counter.
4. **Visual Builder / Editor Integration** - the public homepage is now fully tagged with `data-widget-id` / `data-editable-field`; wire the standalone WYSIWYG editor to it and the app templates (`data-widget`/`data-component` tags) next.

### Backend & Infrastructure
5. **Backend Integration:** Connect templates to Django views and models (most flows are still mock-only).
6. **Database Models:** Design models for users, courses, tickets, and appointments.
7. **User Authentication:** Implement login/logout and role-based access (student / host / admin).
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