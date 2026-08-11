from django.urls import path
from . import views

urlpatterns = [
    # Public homepage (landing page) at the root; the student dashboard lives at /dashboard/
    path('', views.public_home, name='home'),

    # PWA — web app manifest + service worker (origin-root URLs)
    path('manifest.json', views.pwa_manifest, name='pwa_manifest'),
    path('sw.js', views.service_worker_view, name='service_worker'),
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
    path('api/clubs/join/', views.join_club, name='api_club_join'),
    path('transport/', views.transport_dashboard, name='transport_dashboard'),
    path('meals/', views.meal_dashboard, name='meal_dashboard'),
    path('checkout/', views.checkout_page, name='checkout'),
    path('research-ai/', views.research_ai_page, name='research_ai'),
    path('departments/', views.departments_directory, name='departments'),
    path('departments/<slug:dept_slug>/', views.department_detail, name='department_detail'),

    # Website Builder — dynamic pages rendered from EditablePage + ContentBlock.
    # Both /page/<slug>/ (legacy + builder previews) and /pages/<slug>/ (public
    # canonical route) serve the same view; published pages are public, drafts
    # 404 for everyone except users with the builder permission.
    path('page/<slug:slug>/', views.editable_page_view, name='editable_page'),
    path('pages/<slug:slug>/', views.editable_page_view, name='editable_page_public'),

    # Website Builder — Super Admin console (Phase 2)
    path('builder/', views.builder_dashboard, name='builder_dashboard'),
    # Frontend page builder (page-settings toolbar + drag-and-drop block manager)
    path('builder/edit/<slug:page_slug>/', views.builder_editor, name='builder_editor'),
    # Split-screen canvas visual editor
    path('builder/visual/<slug:page_slug>/', views.visual_editor, name='visual_editor'),
    # Page builder JSON endpoints (atomic block reorder / save + page settings)
    path('builder/api/blocks/reorder/', views.builder_blocks_reorder, name='builder_blocks_reorder'),
    path('builder/api/blocks/save/', views.builder_blocks_save, name='builder_blocks_save'),
    path('builder/api/page/save/', views.builder_page_save, name='builder_page_save'),
    # Block library: create from a section template + delete by block id
    path('builder/api/blocks/create/', views.builder_block_create, name='builder_block_create'),
    path('builder/api/blocks/<int:block_id>/delete/', views.builder_block_delete, name='builder_block_delete'),
    # Legacy JSON endpoints (visual editor + dashboard)
    path('api/builder/create-page/', views.create_page, name='create_page'),
    path('api/builder/save-block/', views.save_content_block, name='save_content_block'),
    path('api/builder/save-css/', views.save_page_css, name='save_page_css'),

    # Google integration — Drive notes upload + club sheets (Phase 4)
    path('api/notes/upload/', views.upload_note_view, name='api_upload_note'),
    path('api/clubs/sheet/', views.fetch_club_sheet_view, name='api_club_sheet_fetch'),
    path('api/clubs/sheet/append/', views.append_club_sheet_view, name='api_club_sheet_append'),
    # Verify & Connect a club spreadsheet (creates default tabs/headers)
    path('api/clubs/sheet/verify/', views.verify_club_sheet_view, name='api_club_sheet_verify'),

    # Google Drive — OAuth2 connect/callback (google_auth_oauthlib Flow)
    path('drive/connect/', views.drive_connect, name='drive_connect'),
    path('drive/callback/', views.drive_callback, name='drive_callback'),

    # Settings — Google OAuth account unlinking
    path('api/settings/google-unlink/', views.google_unlink, name='api_google_unlink'),

    # Notes Engine — server-side actions (fetch one / save / summarize / keywords / export)
    path('api/notes/<int:note_id>/', views.get_note, name='api_note_get'),
    path('api/notes/save/', views.save_note, name='api_note_save'),
    path('api/notes/summarize/', views.note_summary, name='api_note_summarize'),
    path('api/notes/keywords/', views.note_keywords, name='api_note_keywords'),
    # Poll endpoint for a queued note analysis (Huey background task)
    path('api/notes/analysis/<uuid:analysis_id>/', views.note_analysis_status, name='api_note_analysis_status'),
    path('api/notes/export/', views.export_note, name='api_note_export'),

    # Research AI — structured query endpoint
    path('api/research/query/', views.research_query, name='api_research_query'),

    # Real-time notification & system alert engine
    path('api/notifications/', views.fetch_notifications, name='api_notifications'),
    path('api/notifications/<int:notification_id>/read/', views.mark_notification_read, name='api_notification_read'),
    
    # Campus services — meal, transport, medical action handlers
    path('claim-meal/', views.claim_meal, name='claim_meal_ticket'),
    path('book-transport/', views.book_transport, name='book_transport_ticket'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),

    # Staff action endpoints — persistent service handlers for admin dashboards
    path('api/cafeteria/redeem/', views.redeem_meal_ticket, name='api_cafeteria_redeem'),
    path('api/cafeteria/batch-redeem/', views.batch_redeem_meal_tickets, name='api_cafeteria_batch_redeem'),
    path('api/medical/appointments/<int:appointment_id>/status/', views.update_appointment_status, name='api_appointment_status'),
    path('api/clubs/verify-transaction/', views.verify_club_transaction_view, name='api_club_verify_transaction'),
    path('api/admin/update-role/', views.update_user_role, name='api_admin_update_role'),

    # Official notices — publish from the System Admin dashboard
    path('api/notices/create/', views.create_notice, name='api_notices_create'),

    # Medical consultation chat + live queue (patient ↔ doctor, real-time)
    path('api/medical/chat/threads/', views.medical_chat_threads, name='api_medical_chat_threads'),
    path('api/medical/chat/start/', views.medical_chat_start, name='api_medical_chat_start'),
    path('api/medical/chat/<int:thread_id>/messages/', views.medical_chat_messages, name='api_medical_chat_messages'),
    path('api/medical/queue/', views.medical_queue_api, name='api_medical_queue'),
    path('api/medical/doctor-availability/', views.medical_doctor_availability, name='api_doctor_availability'),
]

