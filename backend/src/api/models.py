from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class Medicine(models.Model):
    """Model for storing medicine information"""
    name = models.CharField(max_length=255, unique=True)
    generic_name = models.CharField(max_length=255, blank=True, null=True)
    brand_names = models.JSONField(default=list, blank=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    common_doses = models.JSONField(default=list, blank=True)
    side_effects = models.JSONField(default=list, blank=True)
    interactions = models.JSONField(default=list, blank=True)
    contraindications = models.JSONField(default=list, blank=True)
    alternatives = models.JSONField(default=list, blank=True)
    cost_analysis = models.JSONField(default=dict, blank=True)
    molecular_structure = models.JSONField(default=dict, blank=True)
    medical_explanation = models.TextField(blank=True, null=True)
    data_sources = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class UserProfile(models.Model):
    """Model for storing user profiles and medical information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    medical_history = models.JSONField(default=list, blank=True)
    allergies = models.JSONField(default=list, blank=True)
    current_conditions = models.JSONField(default=list, blank=True)
    medications = models.JSONField(default=list, blank=True)
    emergency_contact = models.JSONField(default=dict, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_activity_summary(self):
        """Get user activity summary"""
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


class MedicationReminder(models.Model):
    """Model for storing medication reminders"""
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

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    medicine_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=50, choices=FREQUENCY_CHOICES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    reminder_times = models.JSONField(default=list)  # List of times like ["08:00", "20:00"]
    notes = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.medicine_name}"

    class Meta:
        ordering = ['-created_at']


class PrescriptionHistory(models.Model):
    """Model for storing prescription analysis history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescription_history')
    prescription_text = models.TextField()
    extracted_data = models.JSONField(default=dict)
    analysis_results = models.JSONField(default=dict)
    safety_alerts = models.JSONField(default=list)
    processing_method = models.CharField(max_length=100)  # 'BioBERT AI' or 'Rule-based'
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']


class MedicalKnowledge(models.Model):
    """Model for storing medical knowledge and explanations"""
    term = models.CharField(max_length=255, unique=True)
    explanation = models.TextField()
    category = models.CharField(max_length=100, blank=True, null=True)
    related_terms = models.JSONField(default=list, blank=True)
    source = models.CharField(max_length=100, default='Wiki')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.term

    class Meta:
        ordering = ['term']


class UserFeedback(models.Model):
    """Model for storing user feedback on medications"""
    FEEDBACK_TYPES = [
        ('effectiveness', 'Effectiveness'),
        ('side_effects', 'Side Effects'),
        ('experience', 'General Experience'),
        ('suggestion', 'Suggestion'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback')
    medicine_name = models.CharField(max_length=255)
    feedback_type = models.CharField(max_length=50, choices=FEEDBACK_TYPES)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    comment = models.TextField()
    side_effects_reported = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.medicine_name} ({self.feedback_type})"

    class Meta:
        ordering = ['-created_at']
