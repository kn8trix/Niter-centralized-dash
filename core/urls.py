from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    # Public homepage (landing page) at the root; the student dashboard lives at /dashboard/
    path('', views.public_home, name='home'),

    # PWA — web app manifest + service worker (origin-root URLs)
    path('manifest.json', views.pwa_manifest, name='pwa_manifest'),
    path('sw.js', views.service_worker_view, name='service_worker'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Role-based dashboard areas: students live under /dashboard/student/*,
    # admins under /dashboard/admin/* (see core.roles + RoleAccessMiddleware).
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/club/', views.club_dashboard, name='club_dashboard'),
    # Club workspace — dedicated sub-routes (Overview / Google Sheet / Member
    # Approvals / Roles / Events / Transactions).
    path('dashboard/club/google-sheet/', views.club_sheet_view, name='club_dashboard_sheet'),
    path('dashboard/club/members/', views.club_members_view, name='club_dashboard_members'),
    path('dashboard/club/roles/', views.club_roles_view, name='club_dashboard_roles'),
    path('dashboard/club/events/', views.club_events_view, name='club_dashboard_events'),
    path('dashboard/club/transactions/', views.club_transactions_view, name='club_dashboard_transactions'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/users/', views.admin_users_view, name='admin_users'),
    path('dashboard/admin/users/clubs/', views.admin_club_accounts_view, name='admin_club_accounts'),
    path('dashboard/admin/database/', views.admin_database_view, name='admin_database'),
    path('dashboard/admin/content/', views.admin_content_view, name='admin_content'),
    path('dashboard/admin/settings/', views.admin_settings_view, name='admin_settings'),
    path('dashboard/admin/calendar/', views.admin_calendar_view, name='admin_calendar'),
    path('dashboard/admin/attendance/', views.admin_attendance_view, name='admin_attendance'),
    path('tickets/', views.tickets, name='tickets'),
    path('medical/', views.medical, name='medical'),
    # Pharmacy (Online Pharmacy module) — storefront, Rx upload, orders, admin
    path('pharmacy/', views.pharmacy_store, name='pharmacy_store'),
    path('pharmacy/orders/', views.pharmacy_orders, name='pharmacy_orders'),
    path('api/pharmacy/prescription/upload/', views.api_pharmacy_prescription_upload, name='api_pharmacy_prescription_upload'),
    path('api/pharmacy/checkout/', views.api_pharmacy_checkout, name='api_pharmacy_checkout'),
    path('api/pharmacy/orders/<str:reference>/', views.api_pharmacy_order_detail, name='api_pharmacy_order_detail'),
    path('api/pharmacy/request-stock/', views.api_pharmacy_stock_request, name='api_pharmacy_stock_request'),
    # Pharmacy admin — Rx verification queue + order management + inventory + requests
    path('dashboard/medical/pharmacy/', views.medical_pharmacy, name='medical_pharmacy'),
    path('api/pharmacy/admin/prescriptions/<int:prescription_id>/review/', views.api_pharmacy_prescription_review, name='api_pharmacy_prescription_review'),
    path('api/pharmacy/admin/orders/<int:order_id>/status/', views.api_pharmacy_order_status, name='api_pharmacy_order_status'),
    path('api/pharmacy/admin/requests/<int:request_id>/status/', views.api_pharmacy_request_status, name='api_pharmacy_request_status'),
    path('api/pharmacy/admin/stock/update/', views.api_pharmacy_stock_update, name='api_pharmacy_stock_update'),
    path('notes/', views.notes, name='notes'),
    
    # Additional routes for sidebar links
    # Study Corner — the renamed Academic Notes drive + YouTube lectures + AI
    # Study Assistant. The old /academic-notes/ URL stays as a permanent
    # redirect so bookmarks/service-worker caches keep working.
    path('study-corner/', views.study_corner, name='study_corner'),
    path('academic-notes/', RedirectView.as_view(pattern_name='study_corner', permanent=True), name='academic_notes'),
    path('notices/', views.notices, name='notices'),
    path('news/', views.news_page, name='news'),

    # Account & profile pages
    path('signup/', views.signup_view, name='signup'),
    path('settings/', views.settings_view, name='settings'),
    # Student dashboard — AI routine extraction + academic calendar month API.
    path('api/routine/extract/', views.routine_extract, name='api_routine_extract'),
    path('api/calendar/events/', views.api_calendar_events, name='api_calendar_events'),
    path('api/news/search/', views.api_news_search, name='api_news_search'),
    # Study Corner — YouTube lecture search + AI Study Assistant chat.
    path('api/study/youtube/', views.study_youtube_search, name='api_study_youtube_search'),
    path('api/study/chat/', views.study_chat, name='api_study_chat'),
    # QR Attendance — student scan + stats, admin session management
    path('attendance/', views.attendance_dashboard, name='attendance'),
    path('api/attendance/scan/', views.api_attendance_scan, name='api_attendance_scan'),
    path('api/attendance/my-stats/', views.api_attendance_my_stats, name='api_attendance_my_stats'),
    path('api/admin/attendance/sessions/', views.api_attendance_session_create, name='api_admin_attendance_session_create'),
    path('api/admin/attendance/sessions/<str:session_token>/live/', views.api_attendance_session_live, name='api_admin_attendance_session_live'),
    path('api/admin/attendance/sessions/<str:session_token>/close/', views.api_attendance_session_close, name='api_admin_attendance_session_close'),
    path('api/admin/attendance/records/', views.api_attendance_records, name='api_admin_attendance_records'),
    # Attendance QR / report email dispatch to the assigned course teacher
    path('api/attendance/sessions/<str:session_token>/email-qr/', views.api_attendance_session_email_qr, name='api_attendance_session_email_qr'),
    path('api/attendance/sessions/<str:session_token>/email-report/', views.api_attendance_session_email_report, name='api_attendance_session_email_report'),
    # Teacher Management — admin CRUD (create/list + item update/delete)
    path('dashboard/admin/teachers/', views.admin_teachers_view, name='admin_teachers'),
    path('api/admin/teachers/', views.api_admin_teachers, name='api_admin_teachers'),
    path('api/admin/teachers/<int:teacher_id>/', views.api_admin_teacher_item, name='api_admin_teacher_item'),
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
    # WYSIWYG student-view overlay editor — bulk block + publish save by page id
    path('api/builder/pages/<int:page_id>/save/', views.builder_page_wysiwyg_save, name='builder_page_wysiwyg_save'),
    # Block library: create from a section template + delete by block id
    path('builder/api/blocks/create/', views.builder_block_create, name='builder_block_create'),
    path('builder/api/blocks/<int:block_id>/delete/', views.builder_block_delete, name='builder_block_delete'),
    # Legacy JSON endpoints (visual editor + dashboard)
    path('api/builder/create-page/', views.create_page, name='create_page'),
    path('api/builder/save-block/', views.save_content_block, name='save_content_block'),
    path('api/builder/save-css/', views.save_page_css, name='save_page_css'),

    # Google integration — Drive notes upload + club sheets (Phase 4).
    # Club sheets endpoints live under /clubs/dashboard/sheets/ (the clubs
    # namespace) — the sheets management UI is the staff-only Club Management
    # dashboard, not Account Settings.
    path('api/notes/upload/', views.upload_note_view, name='api_upload_note'),
    # Google Drive — connection health for the Notes Engine upload UI (silent
    # refresh + deployment config audit).
    path('api/notes/auth-status/', views.notes_auth_status, name='api_notes_auth_status'),
    path('clubs/dashboard/sheets/', views.fetch_club_sheet_view, name='api_club_sheet_fetch'),
    path('clubs/dashboard/sheets/append/', views.append_club_sheet_view, name='api_club_sheet_append'),
    # Verify & Connect a club spreadsheet (creates default tabs/headers)
    path('clubs/dashboard/sheets/verify/', views.verify_club_sheet_view, name='api_club_sheet_verify'),

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

    # Research AI — OpenRouter-backed chat endpoint + persisted thread APIs
    path('research-ai/api/query/', views.research_query, name='api_research_query'),
    path('research-ai/api/threads/', views.research_threads, name='api_research_threads'),
    path('research-ai/api/threads/<int:thread_id>/', views.research_thread_detail, name='api_research_thread_detail'),
    # Legacy alias — /api/research/query/ keeps working for old clients/tests.
    path('api/research/query/', views.research_query, name='api_research_query_legacy'),

    # Real-time notification & system alert engine
    path('api/notifications/', views.fetch_notifications, name='api_notifications'),
    path('api/notifications/<int:notification_id>/read/', views.mark_notification_read, name='api_notification_read'),

    # Emergency broadcast system — admin trigger/resolve + public active poll
    path('api/admin/emergency/trigger/', views.api_emergency_trigger, name='api_admin_emergency_trigger'),
    path('api/admin/emergency/resolve/', views.api_emergency_resolve, name='api_admin_emergency_resolve'),
    path('api/emergency/active/', views.api_emergency_active, name='api_emergency_active'),
    
    # Campus services — meal, transport, medical action handlers
    path('claim-meal/', views.claim_meal, name='claim_meal_ticket'),
    path('cancel-meal/', views.cancel_meal, name='cancel_meal_ticket'),
    path('book-transport/', views.book_transport, name='book_transport_ticket'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),

    # Staff action endpoints — persistent service handlers for admin dashboards
    path('api/cafeteria/redeem/', views.redeem_meal_ticket, name='api_cafeteria_redeem'),
    path('api/cafeteria/batch-redeem/', views.batch_redeem_meal_tickets, name='api_cafeteria_batch_redeem'),
    path('api/medical/appointments/<int:appointment_id>/status/', views.update_appointment_status, name='api_appointment_status'),
    path('api/clubs/verify-transaction/', views.verify_club_transaction_view, name='api_club_verify_transaction'),
    path('api/admin/update-role/', views.update_user_role, name='api_admin_update_role'),

    # Admin Dashboard — club account management (create/assign/reset/toggle)
    path('api/admin/academic-calendar/', views.api_academic_calendar, name='api_admin_academic_calendar'),
    path('api/admin/academic-calendar/<int:event_id>/', views.api_academic_calendar_item, name='api_admin_academic_calendar_item'),
    path('api/admin/club-accounts/', views.api_club_accounts, name='api_club_accounts'),
    path('api/admin/club-accounts/<int:account_id>/password/', views.api_club_account_password, name='api_club_account_password'),
    path('api/admin/club-accounts/<int:account_id>/status/', views.api_club_account_status, name='api_club_account_status'),
    path('api/admin/club-accounts/<int:account_id>/permissions/', views.api_club_account_permissions, name='api_club_account_permissions'),

    # Official notices — publish from the System Admin dashboard
    path('api/notices/create/', views.create_notice, name='api_notices_create'),

    # Reports & Feedback — student submission + staff inbox
    path('dashboard/student/reports/', views.reports_student_view, name='reports_student'),
    path('dashboard/admin/reports/', views.reports_admin_view, name='reports_admin'),
    path('api/reports/', views.api_reports, name='api_reports'),
    path('api/admin/reports/', views.api_admin_reports, name='api_admin_reports'),
    path('api/admin/reports/<int:report_id>/', views.api_admin_report_update, name='api_admin_report_update'),

    # Medical consultation chat + live queue (patient ↔ doctor, real-time)
    path('api/medical/chat/threads/', views.medical_chat_threads, name='api_medical_chat_threads'),
    path('api/medical/chat/start/', views.medical_chat_start, name='api_medical_chat_start'),
    path('api/medical/chat/<int:thread_id>/messages/', views.medical_chat_messages, name='api_medical_chat_messages'),
    path('api/medical/queue/', views.medical_queue_api, name='api_medical_queue'),
    path('api/medical/doctor-availability/', views.medical_doctor_availability, name='api_doctor_availability'),
]

