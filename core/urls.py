from django.urls import path
from . import views

urlpatterns = [
    # Public homepage (landing page) at the root; the student dashboard lives at /dashboard/
    path('', views.public_home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tickets/', views.tickets, name='tickets'),
    path('medical/', views.medical, name='medical'),
    path('notes/', views.notes, name='notes'),
    
    # Additional routes for sidebar links
    path('academic-notes/', views.academic_notes, name='academic_notes'),
    path('notices/', views.notices, name='notices'),

    # Account & profile pages
    path('signup/', views.signup_view, name='signup'),
    path('settings/', views.settings_view, name='settings'),
    path('profile/', views.profile_view, name='profile'),

    # Staff / admin dashboards
    path('admin-dashboard/', views.system_admin_view, name='sys_admin'),
    path('cafeteria/admin/', views.cafeteria_admin_view, name='cafeteria_admin'),
    path('clubs/manage/', views.club_admin_view, name='club_admin'),
    path('clubs/', views.clubs_dashboard, name='clubs_dashboard'),
    path('transport/', views.transport_dashboard, name='transport_dashboard'),
    path('meals/', views.meal_dashboard, name='meal_dashboard'),
    path('checkout/', views.checkout_page, name='checkout'),
    path('research-ai/', views.research_ai_page, name='research_ai'),
    path('departments/', views.departments_directory, name='departments'),
    path('departments/<slug:dept_slug>/', views.department_detail, name='department_detail'),
    
    # Form submission placeholders
    path('claim-meal/', views.claim_meal_ticket, name='claim_meal_ticket'),
    path('book-transport/', views.book_transport_ticket, name='book_transport_ticket'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
]
