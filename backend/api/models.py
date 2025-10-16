"""
============================================================================
DATABASE MODELS - Medicine Assistant Application
============================================================================

This file defines all database tables (models) for the application.
Each model class creates a table in the database with fields as columns.

Models defined here are used by:
- api/views.py (main API endpoints)
- api/auth_views.py (authentication endpoints)
- api/admin.py (Django admin panel)
- api/management/commands/ (CLI commands)
- Frontend via API calls

Database: SQLite (development) / PostgreSQL (production)
ORM: Django ORM (Object-Relational Mapping)

Models:
1. Medicine - Medicine database (10,000+ entries)
2. UserProfile - User medical information
3. MedicationReminder - Medication schedules
4. PrescriptionHistory - Analyzed prescriptions
5. MedicalKnowledge - Medical terms & explanations
6. UserFeedback - User feedback on medications
7. Notification - User notifications & alerts
============================================================================
"""

from django.db import models
from django.contrib.auth.models import User  # Django's built-in user model
from django.utils import timezone
import json


# ============================================================================
# MEDICINE MODEL - Central medicine database
# ============================================================================
class Medicine(models.Model):
    """
    Stores comprehensive information about medicines from DrugBank and other sources.
    
    Database Table: api_medicine
    Total Records: ~18,000+ medicines
    
    Used by:
    - api/views.py: search_medicines(), get_medicine_details()
    - api/biobert_processor.py: Validates extracted medicine names
    - api/drug_interactions.py: Looks up interaction data
    - api/nlp_processor.py: Medicine name matching
    
    Related to:
    - PrescriptionHistory (medicines found in prescriptions)
    - MedicationReminder (medicines being tracked)
    - UserProfile.medications (current medicines)
    
    API Endpoints that use this:
    - GET /api/medicines/search/?query=aspirin
    - GET /api/medicine/<medicine_id>/
    - GET /api/alternatives/<medicine_id>/
    """
    # Primary medicine name (unique identifier)
    name = models.CharField(max_length=255, unique=True)
    
    # Generic/scientific name (e.g., Acetaminophen for Tylenol)
    generic_name = models.CharField(max_length=255, blank=True, null=True)
    
    # List of brand names (e.g., ["Tylenol", "Panadol"])
    brand_names = models.JSONField(default=list, blank=True)
    
    # Medicine category (e.g., "Analgesic", "Antibiotic")
    category = models.CharField(max_length=100, blank=True, null=True)
    
    # Detailed description of medicine and its uses
    description = models.TextField(blank=True, null=True)
    
    # Common dosage amounts (e.g., ["500mg", "1000mg"])
    common_doses = models.JSONField(default=list, blank=True)
    
    # List of known side effects
    side_effects = models.JSONField(default=list, blank=True)
    
    # List of medicines this interacts with
    interactions = models.JSONField(default=list, blank=True)
    
    # Conditions where this medicine shouldn't be used
    contraindications = models.JSONField(default=list, blank=True)
    
    # Alternative medicines with similar effects
    alternatives = models.JSONField(default=list, blank=True)
    
    # Cost information and price comparison
    cost_analysis = models.JSONField(default=dict, blank=True)
    
    # Chemical structure data for visualization
    molecular_structure = models.JSONField(default=dict, blank=True)
    
    # Human-readable explanation for non-medical users
    medical_explanation = models.TextField(blank=True, null=True)
    
    # Sources of data (e.g., ["DrugBank", "OpenFDA"])
    data_sources = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation for admin panel and debugging"""
        return self.name

    class Meta:
        ordering = ['name']  # Alphabetical order by default


# ============================================================================
# USER PROFILE MODEL - User medical information and preferences
# ============================================================================
class UserProfile(models.Model):
    """
    Stores medical information and preferences for each user.
    Created automatically when user registers.
    
    Database Table: api_userprofile
    Relationship: One-to-One with Django User model
    
    Used by:
    - api/auth_views.py: get_user_profile(), update_user_profile()
    - api/views.py: analyze_prescription() (for allergy checking)
    - api/allergy_checker.py: Validates medicines against allergies
    - Frontend: UserProfileScreen, MedicalHistoryScreen
    
    Related to:
    - User (Django built-in): One profile per user
    - MedicationReminder: User's reminders via user relationship
    - PrescriptionHistory: User's analyses via user relationship
    
    API Endpoints that use this:
    - GET /api/auth/profile/ (fetch profile)
    - POST /api/auth/profile/update/ (save changes)
    
    Frontend Integration:
    - Flutter calls getUserProfile() to load medical data
    - Flutter calls updateUserProfile() to save allergies/conditions
    """
    # Link to Django User model (one profile per user)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # List of past medical events/conditions (e.g., ["Surgery 2020", "Diabetes diagnosed 2019"])
    medical_history = models.JSONField(default=list, blank=True)
    
    # List of user's allergies (e.g., ["Penicillin", "Peanuts"])
    # Used by allergy_checker.py to validate prescriptions
    allergies = models.JSONField(default=list, blank=True)
    
    # Current medical conditions (e.g., ["Hypertension", "Diabetes Type 2"])
    current_conditions = models.JSONField(default=list, blank=True)
    
    # Current medications user is taking (e.g., ["Metformin 500mg", "Lisinopril 10mg"])
    medications = models.JSONField(default=list, blank=True)
    
    # Emergency contact information (e.g., {"name": "John Doe", "phone": "555-1234"})
    emergency_contact = models.JSONField(default=dict, blank=True)
    
    # User preferences for notifications, reminders, etc.
    preferences = models.JSONField(default=dict, blank=True)
    
    # Timestamps for tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation for admin panel"""
        return f"{self.user.username}'s Profile"

    def get_activity_summary(self):
        """
        Calculate user activity statistics.
        
        Called by:
        - api/auth_views.py: get_user_profile() 
        
        Returns:
        - Dictionary with total_reminders, active_reminders, 
          total_prescriptions_analyzed, last_activity
        
        Used for:
        - Dashboard statistics display
        - User engagement tracking
        """
        reminders = MedicationReminder.objects.filter(user=self.user)
        prescriptions = PrescriptionHistory.objects.filter(user=self.user)
        
        return {
            'total_reminders': reminders.count(),
            'active_reminders': reminders.filter(active=True).count(),
            'total_prescriptions_analyzed': prescriptions.count(),
            'last_activity': max(
                [r.updated_at for r in reminders] + 
                [p.created_at for p in prescriptions] + 
                [self.updated_at]
            ).isoformat() if reminders.exists() or prescriptions.exists() else None
        }


# ============================================================================
# MEDICATION REMINDER MODEL - Scheduled medication tracking
# ============================================================================
class MedicationReminder(models.Model):
    """
    Stores medication reminder schedules for users.
    System checks these reminders and creates notifications when it's time to take medicine.
    
    Database Table: api_medicationreminder
    
    Used by:
    - api/views.py: create_reminder(), get_reminders(), update_reminder(), delete_reminder()
    - api/views.py: trigger_reminder_notifications(), get_reminder_stats()
    - api/management/commands/send_reminder_notifications.py (CLI command)
    - Frontend: RemindersScreen, CreateReminderScreen
    
    Related to:
    - User: Many reminders per user (ForeignKey)
    - Notification: Related via related_reminder_id field
    
    API Endpoints that use this:
    - GET /api/reminders/list/ (get all reminders)
    - POST /api/reminders/create/ (create new reminder)
    - PUT /api/reminders/<id>/update/ (update reminder)
    - DELETE /api/reminders/<id>/delete/ (delete reminder)
    - POST /api/reminders/trigger-notifications/ (check and notify)
    - GET /api/reminders/stats/ (get statistics)
    
    Notification Flow:
    1. User creates reminder via API
    2. Reminder stored in database
    3. Cron job or app launch triggers check
    4. If current time matches reminder_times (±15 min)
    5. Notification created and linked via related_reminder_id
    6. last_notified_at and total_notifications_sent updated
    """
    # Frequency options for medication schedule
    FREQUENCY_CHOICES = [
        ('once', 'Once'),
        ('daily', 'Daily'),
        ('twice_daily', 'Twice Daily'),
        ('three_times_daily', 'Three Times Daily'),
        ('four_times_daily', 'Four Times Daily'),
        ('as_needed', 'As Needed'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    # Link to user who owns this reminder
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    
    # Name of medicine to be taken (e.g., "Aspirin", "Metformin")
    medicine_name = models.CharField(max_length=255)
    
    # Dosage amount (e.g., "500mg", "10ml", "2 tablets")
    dosage = models.CharField(max_length=100)
    
    # How often to take (from FREQUENCY_CHOICES above)
    frequency = models.CharField(max_length=50, choices=FREQUENCY_CHOICES)
    
    # When reminder schedule starts
    start_date = models.DateTimeField()
    
    # When reminder schedule ends (null = ongoing)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # List of times to send notifications (e.g., ["08:00", "14:00", "20:00"])
    # Format: 24-hour time as strings
    reminder_times = models.JSONField(default=list)
    
    # Optional notes (e.g., "Take with food", "Before bed")
    notes = models.TextField(blank=True, null=True)
    
    # Whether reminder is currently active
    # Set to False when ended or user deactivates
    active = models.BooleanField(default=True)
    
    # Timestamp of last notification sent
    # Used to prevent duplicate notifications (1-hour cooldown)
    last_notified_at = models.DateTimeField(blank=True, null=True)
    
    # Counter of total notifications sent for this reminder
    # Used for tracking and analytics
    total_notifications_sent = models.IntegerField(default=0)
    
    # Reminder precision in minutes (how close to exact time to trigger)
    # Options: 0 (exact), 1, 2, 5, 10, 15 minutes
    # Default: 2 minutes for good balance of precision and reliability
    precision_minutes = models.IntegerField(default=2, help_text="How many minutes before/after exact time to trigger reminder")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation for admin panel"""
        return f"{self.user.username} - {self.medicine_name}"

    def get_next_reminder_time(self):
        """
        Calculate next upcoming reminder time.
        
        Called by:
        - api/views.py: get_reminder_stats() to show "next reminder"
        
        Logic:
        1. Get current time
        2. Compare with all reminder_times
        3. Return next future time today
        4. If no times left today, return first time tomorrow
        
        Returns:
        - datetime.time object or None
        """
        from datetime import datetime, time as dt_time
        now = timezone.now()
        current_time = now.time()
        
        # Convert reminder times to time objects and sort
        times = []
        for time_str in self.reminder_times:
            hour, minute = map(int, time_str.split(':'))
            times.append(dt_time(hour, minute))
        
        times.sort()
        
        # Find next time
        for reminder_time in times:
            if current_time < reminder_time:
                return reminder_time
        
        # If all times passed today, return first time tomorrow
        return times[0] if times else None

    class Meta:
        ordering = ['-created_at']  # Newest first


# ============================================================================
# PRESCRIPTION HISTORY MODEL - Analyzed prescription records
# ============================================================================
class PrescriptionHistory(models.Model):
    """
    Stores complete analysis results for each prescription analyzed by the system.
    Auto-saved every time user analyzes a prescription (Day 16 feature).
    
    Database Table: api_prescriptionhistory
    
    Used by:
    - api/views.py: analyze_prescription() (auto-saves analysis)
    - api/views.py: get_prescription_history() (retrieves list)
    - api/views.py: get_prescription_detail() (retrieves single record)
    - Frontend: PrescriptionHistoryScreen, PrescriptionHistoryDetailScreen
    
    Related to:
    - User: Many prescription histories per user (ForeignKey)
    - Medicine: References medicines found in analysis
    
    API Endpoints that use this:
    - POST /api/prescription/analyze/ (creates new record)
    - GET /api/prescription/history/ (list with pagination)
    - GET /api/prescription/history/<id>/ (detailed view)
    
    Frontend Integration:
    - Flutter displays list of past analyses
    - Users can review previous prescription checks
    - Confidence scores and processing methods shown
    
    Data Flow:
    1. User submits prescription text
    2. BioBERT or rule-based extraction runs
    3. Results saved to this model
    4. User can view history anytime
    """
    # Link to user who submitted the prescription
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescription_history')
    
    # Original prescription text submitted by user
    prescription_text = models.TextField()
    
    # Extracted data: medicines, dosages, frequencies (JSON format)
    # Example: {"medicines": [{"name": "Aspirin", "dosage": "100mg", "frequency": "daily"}]}
    extracted_data = models.JSONField(default=dict)
    
    # Complete analysis results including alternatives, warnings
    analysis_results = models.JSONField(default=dict)
    
    # List of safety alerts (interactions, allergies, warnings)
    safety_alerts = models.JSONField(default=list)
    
    # Which method was used: "BioBERT AI" or "Rule-based"
    processing_method = models.CharField(max_length=100)
    
    # AI confidence score (0.0 to 1.0)
    # Higher = more confident in extraction accuracy
    confidence_score = models.FloatField(default=0.0)
    
    # When analysis was performed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """String representation showing user and timestamp"""
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']  # Newest first


# ============================================================================
# MEDICAL KNOWLEDGE MODEL - Medical terms and explanations database
# ============================================================================
class MedicalKnowledge(models.Model):
    """
    Stores medical terms, conditions, and their explanations.
    Populated from Wikipedia medical articles and other sources.
    
    Database Table: api_medicalknowledge
    Total Records: 1,000+ medical terms
    
    Used by:
    - api/views.py: search_medical_knowledge() (search functionality)
    - api/views.py: get_medical_explanation() (get single term)
    - api/views.py: get_medical_knowledge_stats() (statistics)
    - Frontend: MedicalKnowledgeScreen
    
    API Endpoints that use this:
    - GET /api/medical-knowledge/search/?query=diabetes
    - GET /api/medical-knowledge/explanation/<term>/
    - GET /api/medical-knowledge/stats/
    
    Frontend Integration:
    - Users search medical terms
    - Displays explanations in plain language
    - Shows related terms for further reading
    
    Populated by:
    - populate_medical_explanations.py (script)
    - populate_real_medical_knowledge.py (script)
    """
    # Medical term (e.g., "Diabetes", "Hypertension", "Asthma")
    term = models.CharField(max_length=255, unique=True)
    
    # Plain language explanation of the medical term
    explanation = models.TextField()
    
    # Category (e.g., "Disease", "Symptom", "Treatment")
    category = models.CharField(max_length=100, blank=True, null=True)
    
    # Related medical terms (e.g., for "Diabetes": ["Insulin", "Glucose", "Pancreas"])
    related_terms = models.JSONField(default=list, blank=True)
    
    # Data source (e.g., "Wiki", "Medical Journal", "DrugBank")
    source = models.CharField(max_length=100, default='Wiki')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation for admin panel"""
        return self.term

    class Meta:
        ordering = ['term']  # Alphabetical order


# ============================================================================
# USER FEEDBACK MODEL - User feedback and medication reviews
# ============================================================================
class UserFeedback(models.Model):
    """
    Stores user feedback on medication effectiveness and experiences.
    Future feature for collecting real-world medication data.
    
    Database Table: api_userfeedback
    
    Used by:
    - Future endpoints for feedback submission
    - Analytics for medication effectiveness
    
    Related to:
    - User: Many feedback entries per user (ForeignKey)
    - Medicine: Feedback references medicine by name
    
    Future API Endpoints:
    - POST /api/feedback/submit/
    - GET /api/feedback/<medicine_name>/
    """
    # Types of feedback users can provide
    FEEDBACK_TYPES = [
        ('effectiveness', 'Effectiveness'),
        ('side_effects', 'Side Effects'),
        ('experience', 'General Experience'),
        ('suggestion', 'Suggestion'),
    ]

    # Link to user providing feedback
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback')
    
    # Name of medicine being reviewed
    medicine_name = models.CharField(max_length=255)
    
    # Type of feedback (from FEEDBACK_TYPES)
    feedback_type = models.CharField(max_length=50, choices=FEEDBACK_TYPES)
    
    # Rating 1-5 stars (optional)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    
    # User's detailed comment/review
    comment = models.TextField()
    
    # List of side effects user experienced
    side_effects_reported = models.JSONField(default=list, blank=True)
    
    # When feedback was submitted
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """String representation for admin panel"""
        return f"{self.user.username} - {self.medicine_name} ({self.feedback_type})"

    class Meta:
        ordering = ['-created_at']  # Newest first


# ============================================================================
# NOTIFICATION MODEL - User notifications and alerts
# ============================================================================
class Notification(models.Model):
    """
    Stores all user notifications including reminders, warnings, and alerts.
    Core notification system for the application (Day 16 feature).
    
    Database Table: api_notification
    
    Used by:
    - api/views.py: get_notifications(), create_notification()
    - api/views.py: mark_notification_read(), mark_all_read(), delete_notification()
    - api/views.py: trigger_reminder_notifications() (creates reminder notifications)
    - api/management/commands/send_reminder_notifications.py (creates notifications)
    - Frontend: NotificationsScreen
    
    Related to:
    - User: Many notifications per user (ForeignKey)
    - MedicationReminder: Linked via related_reminder_id field
    
    API Endpoints that use this:
    - GET /api/notifications/ (list with filters)
    - GET /api/notifications/unread-count/ (badge count)
    - POST /api/notifications/create/ (manual creation)
    - POST /api/notifications/<id>/read/ (mark as read)
    - POST /api/notifications/mark-all-read/ (mark all)
    - DELETE /api/notifications/<id>/delete/ (delete one)
    
    Frontend Integration:
    - Bell icon shows unread count badge
    - NotificationsScreen displays all notifications
    - Color-coded by priority (red=critical, orange=high, blue=medium, gray=low)
    - Swipe-to-delete functionality
    - Filter by type and read status
    
    Notification Types:
    - reminder: Time to take medicine (auto-generated from reminders)
    - warning: Important health warnings
    - info: General information
    - critical: Urgent alerts requiring immediate attention
    - interaction: Drug interaction detected
    - allergy: Allergy conflict detected
    - refill: Medicine refill needed
    - system: System updates and announcements
    
    Priority Levels:
    - low: Can be addressed later
    - medium: Should be reviewed soon
    - high: Requires prompt attention
    - critical: Immediate action required
    """
    
    # Available notification types (displayed with different icons in UI)
    NOTIFICATION_TYPES = [
        ('reminder', 'Medicine Reminder'),     # Time to take medicine
        ('warning', 'Warning'),                 # Health warning
        ('info', 'Information'),                # General info
        ('critical', 'Critical Alert'),         # Urgent alert
        ('interaction', 'Drug Interaction'),    # Drug interaction found
        ('allergy', 'Allergy Alert'),          # Allergy conflict
        ('refill', 'Refill Reminder'),         # Medicine running low
        ('system', 'System Notification'),     # System message
    ]

    # Priority levels (displayed with different colors in UI)
    PRIORITY_LEVELS = [
        ('low', 'Low'),           # Gray
        ('medium', 'Medium'),     # Blue
        ('high', 'High'),         # Orange
        ('critical', 'Critical'), # Red
    ]

    # Link to user who receives this notification
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # Type of notification (from NOTIFICATION_TYPES above)
    # Determines icon shown in UI
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    
    # Notification title (displayed prominently in notification card)
    # Example: "Time to take Aspirin"
    title = models.CharField(max_length=255)
    
    # Detailed message content
    # Example: "It's time to take your medication: Aspirin\nDosage: 100mg"
    message = models.TextField()
    
    # Priority level (affects UI color and sort order)
    # Higher priority shows at top with more prominent colors
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    
    # Optional: Related medicine name for filtering
    # Allows querying "show all Aspirin notifications"
    related_medicine = models.CharField(max_length=255, blank=True, null=True)
    
    # Optional: Link to related MedicationReminder
    # Used to connect notification back to the reminder that created it
    related_reminder_id = models.IntegerField(blank=True, null=True)
    
    # Optional: URL for action button (future feature)
    action_url = models.CharField(max_length=255, blank=True, null=True)
    
    # Additional data stored as JSON for flexibility
    # Example: {"dosage": "100mg", "auto_generated": true, "triggered_via": "api"}
    metadata = models.JSONField(default=dict, blank=True)
    
    # Read status (affects badge count and UI display)
    is_read = models.BooleanField(default=False)
    
    # When notification was read (null if unread)
    read_at = models.DateTimeField(blank=True, null=True)
    
    # When notification was created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """String representation for admin panel"""
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        """
        Mark notification as read and record the timestamp.
        
        Called by:
        - api/views.py: mark_notification_read() endpoint
        - Frontend: When user taps notification
        
        Logic:
        - Only updates if currently unread (avoids unnecessary DB writes)
        - Sets is_read = True
        - Records read_at timestamp
        
        Side effects:
        - Decreases unread count in UI badge
        - Changes notification appearance in list
        """
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    class Meta:
        # Order by most recent first
        ordering = ['-created_at']
        # Database indexes for faster queries
        # These optimize common queries like "get unread notifications for user"
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'created_at']),
        ]
