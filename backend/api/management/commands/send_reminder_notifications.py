"""
Django management command to check medication reminders and send notifications

This command checks all active medication reminders and creates notifications
for any reminders whose scheduled time has arrived or passed.

Usage:
    python manage.py send_reminder_notifications
    
This can be run:
- Manually when needed
- Via cron job for scheduled execution
- Via API endpoint for on-demand checks
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from api.models import MedicationReminder, Notification


class Command(BaseCommand):
    help = 'Check medication reminders and send notifications for due reminders'

    def add_arguments(self, parser):
        # Optional argument to process reminders for specific user
        parser.add_argument(
            '--user-id',
            type=int,
            help='Process reminders for specific user only',
        )
        
        # Optional argument for testing/debugging
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without creating notifications',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        dry_run = options.get('dry_run', False)
        
        # Get all active reminders
        reminders = MedicationReminder.objects.filter(active=True)
        
        # Filter by user if specified
        if user_id:
            reminders = reminders.filter(user_id=user_id)
            self.stdout.write(f"Processing reminders for user {user_id}")
        else:
            self.stdout.write("Processing all active reminders")
        
        now = timezone.now()
        notifications_created = 0
        reminders_processed = 0
        
        for reminder in reminders:
            # Check if reminder has ended
            if reminder.end_date and now > reminder.end_date:
                if not dry_run:
                    reminder.active = False
                    reminder.save()
                self.stdout.write(
                    self.style.WARNING(
                        f"  Deactivated expired reminder: {reminder.medicine_name} for {reminder.user.username}"
                    )
                )
                continue
            
            # Check if it's time to send notification
            should_notify = self._should_send_notification(reminder, now)
            
            if should_notify:
                reminders_processed += 1
                
                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  [DRY RUN] Would notify: {reminder.user.username} - {reminder.medicine_name} at {now.strftime('%H:%M')}"
                        )
                    )
                else:
                    # Create notification
                    notification = self._create_notification(reminder, now)
                    
                    # Update reminder tracking
                    reminder.last_notified_at = now
                    reminder.total_notifications_sent += 1
                    reminder.save()
                    
                    notifications_created += 1
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Notification sent: {reminder.user.username} - {reminder.medicine_name}"
                        )
                    )
        
        # Summary
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n[DRY RUN] Would create {reminders_processed} notifications"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nCompleted: {notifications_created} notifications created from {reminders.count()} active reminders"
                )
            )

    def _should_send_notification(self, reminder, now):
        """
        Determine if a notification should be sent for this reminder
        
        Improved Logic:
        1. Check each reminder time with precise timing
        2. Use exact time matching with small buffer (±2 minutes)
        3. Avoid duplicates with smart cooldown
        4. Handle edge cases (midnight, etc.)
        """
        current_time = now.time()
        current_date = now.date()
        
        # Smart cooldown: shorter for exact matches, longer for missed reminders
        cooldown_minutes = 5  # Reduced from 60 minutes
        
        # If we've already notified recently, skip
        if reminder.last_notified_at:
            time_since_last = now - reminder.last_notified_at
            if time_since_last < timedelta(minutes=cooldown_minutes):
                return False
        
        # Check each reminder time with precise matching
        for time_str in reminder.reminder_times:
            hour, minute = map(int, time_str.split(':'))
            reminder_time = datetime.strptime(time_str, '%H:%M').time()
            
            # Create datetime objects for comparison
            reminder_datetime = datetime.combine(current_date, reminder_time)
            now_datetime = datetime.combine(current_date, current_time)
            
            # Calculate time difference in minutes
            time_diff = (now_datetime - reminder_datetime).total_seconds() / 60
            
            # DYNAMIC PRECISION: Use user-defined precision or default to 2 minutes
            precision = getattr(reminder, 'precision_minutes', 2)
            
            # PRECISE TIMING: Exact time ±precision minutes
            if -precision <= time_diff <= precision:
                return True
            
            # FALLBACK: If we're past the reminder time by more than precision but less than 10 minutes
            # This handles cases where the system was down or missed the exact time
            elif precision < time_diff <= 10:
                # Only send if we haven't notified for this specific time today
                if self._should_send_late_notification(reminder, time_str, now):
                    return True
        
        return False
    
    def _should_send_late_notification(self, reminder, time_str, now):
        """
        Check if we should send a late notification for a missed reminder time
        """
        # Check if we already notified for this specific time today
        if reminder.last_notified_at:
            # If last notification was for a different time, allow late notification
            last_notification_time = reminder.last_notified_at.time()
            current_reminder_time = datetime.strptime(time_str, '%H:%M').time()
            
            # If times are different, allow late notification
            if last_notification_time != current_reminder_time:
                return True
        
        return False

    def _create_notification(self, reminder, now):
        """
        Create a notification for the given reminder
        """
        # Determine priority based on frequency
        priority = 'medium'
        if reminder.frequency in ['daily', 'twice_daily', 'three_times_daily', 'four_times_daily']:
            priority = 'high'
        elif reminder.frequency == 'as_needed':
            priority = 'low'
        
        # Create notification message
        title = f"Time to take {reminder.medicine_name}"
        
        message_parts = [
            f"It's time to take your medication: {reminder.medicine_name}",
            f"Dosage: {reminder.dosage}",
        ]
        
        if reminder.notes:
            message_parts.append(f"Note: {reminder.notes}")
        
        message = "\n".join(message_parts)
        
        # Create the notification
        notification = Notification.objects.create(
            user=reminder.user,
            notification_type='reminder',
            title=title,
            message=message,
            priority=priority,
            related_medicine=reminder.medicine_name,
            related_reminder_id=reminder.id,
            metadata={
                'dosage': reminder.dosage,
                'frequency': reminder.frequency,
                'reminder_time': now.strftime('%H:%M'),
                'auto_generated': True
            }
        )
        
        return notification

