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
- **Margin:** Offset by `256px` (ml-64).
- **Header:** Sticky top bar with page title, global search, and notification bell.
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

## 5. Template Usage

### 5.1 Base Template
All templates extend `templates/base.html` which provides:
- Fixed sidebar with navigation.
- Sticky header with search and notifications.
- Consistent styling and theme colors.
- Responsive design with mobile toggle.

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
| **Dashboard** | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) | Main student dashboard |
| **Academic & Notes** | [http://127.0.0.1:8000/academic-notes/](http://127.0.0.1:8000/academic-notes/) | Courses & assignments |
| **Official Notices** | [http://127.0.0.1:8000/notices/](http://127.0.0.1:8000/notices/) | Announcements & events |
| **Tickets** | [http://127.0.0.1:8000/tickets/](http://127.0.0.1:8000/tickets/) | Meal & transport tickets |
| **Medical** | [http://127.0.0.1:8000/medical/](http://127.0.0.1:8000/medical/) | Appointment booking |
| **Notes Engine** | [http://127.0.0.1:8000/notes/](http://127.0.0.1:8000/notes/) | Notes engine |

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
│   └── urls.py                  # App URL routes
├── templates/
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

## 9. Git Repository
- **Repository:** [https://github.com/kn8trix/Niter-centralized-dash](https://github.com/kn8trix/Niter-centralized-dash)
- **Branch:** `main`
- **Git Ignore:** `venv/`, `__pycache__/`, `*.pyc`, `.env`

## 10. API Endpoints (Planned)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | `/claim-meal/` | Claim a meal ticket |
| POST | `/book-transport/` | Book a transport ticket |
| POST | `/book-appointment/` | Schedule a medical appointment |
| GET | `/api/notices/` | Fetch official notices |
| GET | `/api/courses/` | Fetch course materials |

## 11. Next Steps
1. **Backend Integration:** Connect templates to Django views and models.
2. **API Development:** Create endpoints for meal claims, transport bookings, and appointments.
3. **User Authentication:** Implement login/logout functionality.
4. **Database Models:** Design models for users, courses, tickets, and appointments.
5. **Testing:** Add unit tests for views and forms.
6. **Deployment:** Configure for production environment.
7. **Mobile App:** Consider building a React Native or Flutter companion app.
8. **Real-time Updates:** Implement WebSocket for live notifications and seat availability.

## 12. Update by Tajkia Tasnim

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

# CampusDash – Development Handover

## Latest Development Update
**Date:** August 8, 2026  
**Branch:** `taj`  
**Latest Commit:** `7366f53`

---

## 1. Medical Admin Dashboard

A separate Medical Admin Dashboard has been added to keep medical administration functionality separate from the Student Dashboard.

### Intended Route

`/medical/admin/`

### Medical Admin Features

The Medical Admin Dashboard is designed to provide:

- Dashboard overview
- Appointment management
- Pending appointment management
- Confirm appointment
- Cancel appointment
- Appointment search/filter
- Appointment details
- Medical chat management
- Doctor schedule management
- Medical information management
- Health tips management
- Disease awareness management
- First aid information
- Medical facilities management
- Emergency contacts management
- Medical news management
- Public medical information management

---

## 2. Student Medical Appointment

The Student Dashboard should only provide student-level medical appointment functionality.

### Student can:

- Book a medical appointment
- View their own appointments
- View appointment status

### Student cannot:

- Confirm appointments
- Cancel appointments as an admin
- Approve appointments
- Manage other students' appointments
- Manage doctors
- Manage medical information
- Access Medical Admin controls

### Intended Flow

```text
Student
   ↓
Book Appointment
   ↓
PENDING
   ↓
Medical Admin Reviews
   ↓
CONFIRMED / CANCELLED
   ↓
Student Views Updated Status