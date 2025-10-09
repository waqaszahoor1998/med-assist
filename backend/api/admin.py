from django.contrib import admin
from .models import (
    Medicine,
    UserProfile,
    MedicationReminder,
    PrescriptionHistory,
    MedicalKnowledge,
    UserFeedback,
    Notification
)


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'generic_name', 'category', 'created_at']
    search_fields = ['name', 'generic_name', 'category']
    list_filter = ['category', 'created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    list_filter = ['created_at']


@admin.register(MedicationReminder)
class MedicationReminderAdmin(admin.ModelAdmin):
    list_display = ['user', 'medicine_name', 'dosage', 'frequency', 'active', 'created_at']
    search_fields = ['user__username', 'medicine_name']
    list_filter = ['frequency', 'active', 'created_at']
    readonly_fields = ['total_notifications_sent', 'last_notified_at']


@admin.register(PrescriptionHistory)
class PrescriptionHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'processing_method', 'confidence_score', 'created_at']
    search_fields = ['user__username', 'prescription_text']
    list_filter = ['processing_method', 'created_at']
    readonly_fields = ['created_at']


@admin.register(MedicalKnowledge)
class MedicalKnowledgeAdmin(admin.ModelAdmin):
    list_display = ['term', 'category', 'source', 'created_at']
    search_fields = ['term', 'explanation', 'category']
    list_filter = ['category', 'source', 'created_at']


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'medicine_name', 'feedback_type', 'rating', 'created_at']
    search_fields = ['user__username', 'medicine_name', 'comment']
    list_filter = ['feedback_type', 'rating', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'priority', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    readonly_fields = ['created_at', 'read_at']
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{queryset.count()} notifications marked as read')
    mark_as_read.short_description = 'Mark selected as read'
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'{queryset.count()} notifications marked as unread')
    mark_as_unread.short_description = 'Mark selected as unread'

