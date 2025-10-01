from django.urls import path
from . import views

urlpatterns = [
    path('ping/', views.ping, name='ping'),
    path('prescription/analyze/', views.analyze_prescription, name='analyze_prescription'),
    path('prescription/analyze-with-safety/', views.analyze_prescription_with_safety, name='analyze_prescription_with_safety'),
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
]
