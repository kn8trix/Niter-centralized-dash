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
    
    # Form submission placeholders
    path('claim-meal/', views.claim_meal_ticket, name='claim_meal_ticket'),
    path('book-transport/', views.book_transport_ticket, name='book_transport_ticket'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
]
