from django.urls import path, include
from . import views
from . import auth_views

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', auth_views.register_user, name='register_user'),
    path('auth/login/', auth_views.login_user, name='login_user'),
    path('auth/refresh/', auth_views.refresh_token, name='refresh_token'),
    path('auth/logout/', auth_views.logout_user, name='logout_user'),
    path('auth/verify/', auth_views.verify_token, name='verify_token'),
    path('auth/profile/', auth_views.get_user_profile, name='get_user_profile'),
    path('auth/profile/update/', auth_views.update_user_profile, name='update_user_profile'),
    
    # JWT token endpoints (handled by custom auth_views)
    
    # Core API endpoints
    path('ping/', views.ping, name='ping'),
    path('prescription/analyze/', views.analyze_prescription, name='analyze_prescription'),
    path('prescription/analyze-with-safety/', views.analyze_prescription_with_safety, name='analyze_prescription_with_safety'),
    path('prescription/history/', views.get_prescription_history, name='get_prescription_history'),
    path('prescription/history/<int:history_id>/', views.get_prescription_detail, name='get_prescription_detail'),
    path('medicine/<str:medicine_id>/', views.get_medicine_details, name='get_medicine_details'),
    path('alternatives/<str:medicine_id>/', views.get_alternatives, name='get_alternatives'),
    path('reminders/', views.get_reminders, name='get_reminders'),
    path('reminders/set/', views.set_reminder, name='set_reminder'),
    path('reminders/<str:reminder_id>/', views.manage_reminder, name='manage_reminder'),
    path('reminders/<str:reminder_id>/track/', views.track_medication, name='track_medication'),
    path('user/profile/', views.user_profile, name='user_profile'),
    
    # Enhanced Drug Interaction Endpoints (OpenFDA + RxNorm) - Must come first
    path('interactions/enhanced/check/', views.check_enhanced_drug_interactions, name='check_enhanced_drug_interactions'),
    path('interactions/enhanced/medicine/<str:medicine_name>/', views.get_medicine_info_enhanced, name='get_medicine_info_enhanced'),
    path('interactions/enhanced/bulk-download/', views.bulk_download_medicine_data, name='bulk_download_medicine_data'),
    path('interactions/enhanced/cache-stats/', views.get_cache_stats, name='get_cache_stats'),
    path('prescription/analyze-enhanced/', views.analyze_prescription_enhanced, name='analyze_prescription_enhanced'),
    
    # Drug Interaction Endpoints (Basic)
    path('interactions/check/', views.check_drug_interactions, name='check_drug_interactions'),
    path('interactions/validate-safety/', views.validate_prescription_safety, name='validate_prescription_safety'),
    path('interactions/medicine/<str:medicine_name>/', views.get_medicine_interactions, name='get_medicine_interactions'),
    path('interactions/<str:medicine1>/<str:medicine2>/', views.get_interaction_details, name='get_interaction_details'),
    
    # Medical Knowledge Endpoints
    path('medical-knowledge/search/', views.search_medical_knowledge, name='search_medical_knowledge'),
    path('medical-knowledge/explanation/<str:medicine_name>/', views.get_medical_explanation, name='get_medical_explanation'),
    path('medical-knowledge/stats/', views.get_medical_knowledge_stats, name='get_medical_knowledge_stats'),
    
    # Medicine Search Endpoints
    path('medicines/search/', views.search_medicines, name='search_medicines'),
    
    # Notification Endpoints
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/unread-count/', views.get_unread_count, name='get_unread_count'),
    path('notifications/create/', views.create_notification, name='create_notification'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    
    # Reminder Endpoints
    path('reminders/list/', views.get_reminders, name='get_all_reminders'),
    path('reminders/create/', views.create_reminder, name='create_reminder'),
    path('reminders/<int:reminder_id>/update/', views.update_reminder, name='update_reminder'),
    path('reminders/<int:reminder_id>/delete/', views.delete_reminder, name='delete_reminder'),
]
