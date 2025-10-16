"""
============================================================================
API URL CONFIGURATION - Medicine Assistant Application
============================================================================

This file maps URL paths to view functions (request handlers).
Django routes incoming HTTP requests through this file to find the
appropriate function to handle each request.

URL Routing Flow:
1. Request arrives: http://localhost:8000/api/prescription/analyze/
2. Main urls.py (medicine_assistant/urls.py) routes /api/* here
3. This file matches /prescription/analyze/ to views.analyze_prescription
4. View function executes and returns response

Structure:
- Authentication endpoints (login, register, profile)
- Prescription endpoints (analyze, history)
- Medicine endpoints (search, details, alternatives)
- Reminder endpoints (CRUD operations, notifications)
- Notification endpoints (list, read, delete)
- Medical knowledge endpoints (search, explanations)
- Drug interaction endpoints (checking, validation)

All endpoints require JWT authentication except:
- auth/register/ (new users)
- auth/login/ (get token)
- ping/ (health check)

Frontend Integration:
- Flutter app calls these endpoints via ApiService
- All requests include JWT token in Authorization header
- Responses are JSON formatted
============================================================================
"""

from django.urls import path, include
from . import views        # Import main view functions
from . import auth_views   # Import authentication view functions

urlpatterns = [
    # ========================================================================
    # AUTHENTICATION ENDPOINTS
    # ========================================================================
    # Handles user registration, login, JWT token management, and profiles
    # All handled by auth_views.py
    
    # Register new user
    # POST /api/auth/register/
    # Body: {username, email, password, first_name, last_name}
    # Returns: JWT tokens + user data
    # Called by: Flutter RegistrationScreen
    path('auth/register/', auth_views.register_user, name='register_user'),
    
    # Login existing user
    # POST /api/auth/login/
    # Body: {username, password}
    # Returns: JWT access + refresh tokens, user data
    # Called by: Flutter LoginScreen
    path('auth/login/', auth_views.login_user, name='login_user'),
    
    # Refresh JWT access token
    # POST /api/auth/refresh/
    # Body: {refresh}
    # Returns: New access token
    # Called by: Flutter ApiService when token expires
    path('auth/refresh/', auth_views.refresh_token, name='refresh_token'),
    
    # Logout user (invalidate tokens)
    # POST /api/auth/logout/
    # Called by: Flutter UserProfileScreen logout button
    path('auth/logout/', auth_views.logout_user, name='logout_user'),
    
    # Verify if JWT token is valid
    # POST /api/auth/verify/
    # Body: {token}
    # Returns: {valid: true/false}
    # Called by: Flutter on app launch
    path('auth/verify/', auth_views.verify_token, name='verify_token'),
    
    # Get user profile with medical data
    # GET /api/auth/profile/
    # Returns: user data, medical history, allergies, activity summary
    # Called by: Flutter UserProfileScreen, MedicalHistoryScreen
    path('auth/profile/', auth_views.get_user_profile, name='get_user_profile'),
    
    # Update user profile and medical history
    # POST /api/auth/profile/update/
    # Body: {first_name, last_name, allergies[], current_conditions[], etc}
    # Returns: Updated profile data
    # Called by: Flutter PersonalInfoScreen, MedicalHistoryScreen
    path('auth/profile/update/', auth_views.update_user_profile, name='update_user_profile'),
    
    # ========================================================================
    # CORE API ENDPOINTS
    # ========================================================================
    
    # Health check endpoint (no authentication required)
    # GET /api/ping/
    # Returns: {message: "API is running", status: "success"}
    # Called by: Flutter app startup, server monitoring
    path('ping/', views.ping, name='ping'),
    
    # ========================================================================
    # PRESCRIPTION ANALYSIS ENDPOINTS
    # ========================================================================
    
    # Analyze prescription text using AI (BioBERT) or rule-based extraction
    # POST /api/prescription/analyze/
    # Body: {text: "prescription text", allergies: ["Penicillin"]}
    # Returns: medicines[], interactions[], allergies[], alternatives[]
    # Processing: BioBERT AI → drug_interactions.py → allergy_checker.py
    # Called by: Flutter PrescriptionEntryScreen
    path('prescription/analyze/', views.analyze_prescription, name='analyze_prescription'),
    
    # Enhanced analysis with comprehensive safety checks
    # POST /api/prescription/analyze-with-safety/
    # Includes: OpenFDA data, RxNorm validation, enhanced interaction checking
    # Called by: Advanced analysis feature
    path('prescription/analyze-with-safety/', views.analyze_prescription_with_safety, name='analyze_prescription_with_safety'),
    
    # Get user's prescription history (paginated)
    # GET /api/prescription/history/?limit=20&offset=0
    # Returns: List of past analyses with summary data
    # Called by: Flutter PrescriptionHistoryScreen
    path('prescription/history/', views.get_prescription_history, name='get_prescription_history'),
    
    # Get detailed view of single prescription analysis
    # GET /api/prescription/history/<id>/
    # Returns: Complete analysis results, medicines, alerts
    # Called by: Flutter PrescriptionHistoryDetailScreen
    path('prescription/history/<int:history_id>/', views.get_prescription_detail, name='get_prescription_detail'),
    
    # ========================================================================
    # MEDICINE DATABASE ENDPOINTS
    # ========================================================================
    
    # Get details for specific medicine
    # GET /api/medicine/<medicine_name>/
    # Returns: Full medicine data (side effects, interactions, etc.)
    # Called by: Flutter medicine detail views
    path('medicine/<str:medicine_id>/', views.get_medicine_details, name='get_medicine_details'),
    
    # Get alternative medicines for specific medicine
    # GET /api/alternatives/<medicine_name>/
    # Returns: List of alternative medicines with similar effects
    # Called by: Flutter after prescription analysis
    path('alternatives/<str:medicine_id>/', views.get_alternatives, name='get_alternatives'),
    
    # Legacy endpoints removed - use new endpoints below:
    # - reminders/list/ (GET)
    # - reminders/create/ (POST)
    # - reminders/<id>/update/ (PUT)
    # - reminders/<id>/delete/ (DELETE)
    # - auth/profile/ (GET/POST)
    
    # ========================================================================
    # DRUG INTERACTION ENDPOINTS (Enhanced - OpenFDA + RxNorm)
    # ========================================================================
    
    # Check drug interactions using OpenFDA data
    # POST /api/interactions/enhanced/check/
    # Body: {medicines: ["Aspirin", "Warfarin"]}
    # Returns: Interaction warnings with severity levels
    path('interactions/enhanced/check/', views.check_enhanced_drug_interactions, name='check_enhanced_drug_interactions'),
    
    # Get comprehensive medicine info from OpenFDA
    path('interactions/enhanced/medicine/<str:medicine_name>/', views.get_medicine_info_enhanced, name='get_medicine_info_enhanced'),
    
    # Bulk download medicine data for caching
    path('interactions/enhanced/bulk-download/', views.bulk_download_medicine_data, name='bulk_download_medicine_data'),
    
    # Get cache statistics
    path('interactions/enhanced/cache-stats/', views.get_cache_stats, name='get_cache_stats'),
    
    # Enhanced prescription analysis with OpenFDA
    path('prescription/analyze-enhanced/', views.analyze_prescription_enhanced, name='analyze_prescription_enhanced'),
    
    # ========================================================================
    # DRUG INTERACTION ENDPOINTS (Basic - Database)
    # ========================================================================
    
    # Check basic drug interactions from database
    # POST /api/interactions/check/
    # Body: {medicines: ["Aspirin", "Ibuprofen"]}
    # Returns: Known interactions from database
    path('interactions/check/', views.check_drug_interactions, name='check_drug_interactions'),
    
    # Validate prescription safety
    path('interactions/validate-safety/', views.validate_prescription_safety, name='validate_prescription_safety'),
    
    # Get all known interactions for a medicine
    path('interactions/medicine/<str:medicine_name>/', views.get_medicine_interactions, name='get_medicine_interactions'),
    
    # Get specific interaction between two medicines
    path('interactions/<str:medicine1>/<str:medicine2>/', views.get_interaction_details, name='get_interaction_details'),
    
    # ========================================================================
    # MEDICAL KNOWLEDGE ENDPOINTS
    # ========================================================================
    
    # Search medical terms and conditions
    # GET /api/medical-knowledge/search/?query=diabetes
    # Returns: List of matching medical terms with explanations
    # Called by: Flutter MedicalKnowledgeScreen
    path('medical-knowledge/search/', views.search_medical_knowledge, name='search_medical_knowledge'),
    
    # Get explanation for specific medical term
    # GET /api/medical-knowledge/explanation/<term>/
    # Returns: Detailed explanation and related terms
    path('medical-knowledge/explanation/<str:medicine_name>/', views.get_medical_explanation, name='get_medical_explanation'),
    
    # Get medical knowledge database statistics
    # GET /api/medical-knowledge/stats/
    # Returns: Total terms, categories, etc.
    path('medical-knowledge/stats/', views.get_medical_knowledge_stats, name='get_medical_knowledge_stats'),
    
    # ========================================================================
    # MEDICINE SEARCH ENDPOINTS
    # ========================================================================
    
    # Search medicine database
    # GET /api/medicines/search/?query=aspirin
    # Returns: List of matching medicines
    # Called by: Flutter MedicineSearchScreen
    path('medicines/search/', views.search_medicines, name='search_medicines'),
    
    # ========================================================================
    # NOTIFICATION ENDPOINTS (Day 16 Feature)
    # ========================================================================
    
    # Get all notifications for user (with filters)
    # GET /api/notifications/?type=reminder&is_read=false
    # Returns: List of notifications
    # Called by: Flutter NotificationsScreen
    path('notifications/', views.get_notifications, name='get_notifications'),
    
    # Get unread notification count for badge
    # GET /api/notifications/unread-count/
    # Returns: {unread_count: 5}
    # Called by: Flutter UserDashboard (bell icon badge)
    path('notifications/unread-count/', views.get_unread_count, name='get_unread_count'),
    
    # Create notification manually
    # POST /api/notifications/create/
    # Body: {type, title, message, priority}
    path('notifications/create/', views.create_notification, name='create_notification'),
    
    # Mark single notification as read
    # POST /api/notifications/<id>/read/
    # Called by: Flutter when user taps notification
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Mark all notifications as read
    # POST /api/notifications/mark-all-read/
    # Called by: Flutter "Mark all as read" button
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    
    # Delete single notification
    # DELETE /api/notifications/<id>/delete/
    # Called by: Flutter swipe-to-delete
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    
    # ========================================================================
    # MEDICATION REMINDER ENDPOINTS (Day 16 Feature)
    # ========================================================================
    
    # Get all reminders for user
    # GET /api/reminders/list/?active=true
    # Returns: List of medication reminders
    # Called by: Flutter RemindersScreen
    path('reminders/list/', views.get_reminders, name='get_all_reminders'),
    
    # Create new medication reminder
    # POST /api/reminders/create/
    # Body: {medicine_name, dosage, frequency, reminder_times[], notes}
    # Returns: Created reminder with ID
    # Called by: Flutter CreateReminderScreen
    path('reminders/create/', views.create_reminder, name='create_reminder'),
    
    # Update existing reminder
    # PUT /api/reminders/<id>/update/
    # Body: {active: false} or other fields to update
    # Called by: Flutter RemindersScreen (toggle active/inactive)
    path('reminders/<int:reminder_id>/update/', views.update_reminder, name='update_reminder'),
    
    # Delete reminder
    # DELETE /api/reminders/<id>/delete/
    # Called by: Flutter RemindersScreen delete button
    path('reminders/<int:reminder_id>/delete/', views.delete_reminder, name='delete_reminder'),
    
    # Trigger reminder notification check (Day 17 Feature)
    # POST /api/reminders/trigger-notifications/
    # Checks all active reminders and creates notifications for due times
    # Returns: {notifications_created, reminders_checked}
    # Called by: Flutter UserDashboard on app launch
    path('reminders/trigger-notifications/', views.trigger_reminder_notifications, name='trigger_reminder_notifications'),
    
    # Get reminder statistics (Day 17 Feature)
    # GET /api/reminders/stats/
    # Returns: {total_reminders, active_reminders, total_notifications_sent, next_reminder}
    # Called by: Future dashboard widget
    path('reminders/stats/', views.get_reminder_stats, name='get_reminder_stats'),
]
