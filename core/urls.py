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

    # Website Builder — dynamic pages rendered from EditablePage + ContentBlock
    path('page/<slug:slug>/', views.editable_page_view, name='editable_page'),

    # Website Builder — Super Admin console (Phase 2)
    path('builder/', views.builder_dashboard, name='builder_dashboard'),
    path('builder/edit/<slug:page_slug>/', views.visual_editor, name='visual_editor'),
    path('api/builder/create-page/', views.create_page, name='create_page'),
    path('api/builder/save-block/', views.save_content_block, name='save_content_block'),
    path('api/builder/save-css/', views.save_page_css, name='save_page_css'),

    # Google integration — Drive notes upload + club sheets (Phase 4)
    path('api/notes/upload/', views.upload_note_view, name='api_upload_note'),
    path('api/clubs/sheet/', views.fetch_club_sheet_view, name='api_club_sheet_fetch'),
    path('api/clubs/sheet/append/', views.append_club_sheet_view, name='api_club_sheet_append'),

    # Real-time notification & system alert engine
    path('api/notifications/', views.fetch_notifications, name='api_notifications'),
    path('api/notifications/<int:notification_id>/read/', views.mark_notification_read, name='api_notification_read'),
    
    # Campus services — meal, transport, medical action handlers
    path('claim-meal/', views.claim_meal, name='claim_meal_ticket'),
    path('book-transport/', views.book_transport, name='book_transport_ticket'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),

    # Staff action endpoints — persistent service handlers for admin dashboards
    path('api/cafeteria/redeem/', views.redeem_meal_ticket, name='api_cafeteria_redeem'),
    path('api/medical/appointments/<int:appointment_id>/status/', views.update_appointment_status, name='api_appointment_status'),
    path('api/clubs/verify-transaction/', views.verify_club_transaction_view, name='api_club_verify_transaction'),
    path('api/admin/update-role/', views.update_user_role, name='api_admin_update_role'),
]
