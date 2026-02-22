from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Applications
    path('applications/', views.applications_list, name='applications'),
    path('apply/', views.apply_attachment, name='apply'),
    path('application/<int:app_id>/', views.application_detail, name='application_detail'),
    path('application/<int:app_id>/withdraw/', views.withdraw_application, name='withdraw_application'),
    
    # Organizations
    path('organizations/', views.organizations_list, name='organizations'),
    path('organizations/<int:org_id>/', views.organization_detail, name='organization_detail'),
    path('organizations/register/', views.register_organization, name='register_organization'),
    path('organizations/<int:org_id>/verify/', views.verify_organization, name='verify_organization'),
    
    # Logbook
    path('logbook/<int:app_id>/', views.logbook, name='logbook'),
    path('logbook/<int:app_id>/entry/<int:week>/', views.logbook_entry, name='logbook_entry'),
    path('logbook/<int:entry_id>/approve/', views.approve_logbook, name='approve_logbook'),
    
    # Evaluations
    path('evaluate/<int:app_id>/', views.evaluate, name='evaluate'),
    path('evaluations/', views.evaluations_list, name='evaluations'),
    path('evaluation/<int:eval_id>/', views.evaluation_detail, name='evaluation_detail'),
    
    # Messaging
    path('messages/', views.messages_list, name='messages'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('messages/new/', views.new_message, name='new_message'),
    path('messages/<int:message_id>/reply/', views.reply_message, name='reply_message'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications'),
    path('notifications/<int:notif_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_read, name='mark_all_read'),
    
    # API endpoints
    path('api/notifications/unread-count/', views.unread_notifications_count, name='unread_notifications_count'),
    path('api/messages/unread-count/', views.unread_messages_count, name='unread_messages_count'),
    
    # Reports
    path('reports/', views.reports_list, name='reports'),
    path('reports/generate/', views.generate_report, name='generate_report'),
    path('reports/<int:report_id>/download/', views.download_report, name='download_report'),
    
    # Admin/Coordinator
    path('students/', views.students_list, name='students_list'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students/<int:student_id>/message/', views.message_student, name='message_student'),
    path('supervisors/', views.supervisors_list, name='supervisors_list'),
    path('departments/', views.departments_list, name='departments_list'),
    path('attachment-periods/', views.attachment_periods, name='attachment_periods'),
    path('attachment-periods/create/', views.create_attachment_period, name='create_attachment_period'),
    
    # Announcements
    path('announcements/', views.announcements_list, name='announcements'),
    path('announcements/create/', views.create_announcement, name='create_announcement'),
    path('announcements/<int:ann_id>/', views.announcement_detail, name='announcement_detail'),
]
