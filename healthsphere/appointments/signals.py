"""
HealthSphere AI - Appointment Signals
====================================

Django signals for automatic audit logging and reminder management.
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment, AppointmentReminder
from users.models import AuditLog


@receiver(post_save, sender=Appointment)
def create_appointment_audit_log(sender, instance, created, **kwargs):
    """Create audit log when appointment is created or updated."""
    action = 'CREATE' if created else 'UPDATE'
    
    # Get the current user from the thread local storage if available
    # In a real implementation, you'd use middleware to track the current user
    user = getattr(instance, '_current_user', None)
    
    AuditLog.objects.create(
        user=user,
        action=action,
        resource_type='Appointment',
        resource_id=str(instance.id),
        description=f"Appointment {action.lower()}: {instance}",
        success=True
    )


@receiver(post_save, sender=Appointment)
def create_appointment_reminders(sender, instance, created, **kwargs):
    """Create automatic reminders when an appointment is created or confirmed."""
    if created or (instance.status == 'confirmed' and instance.send_reminder):
        # Clear existing reminders
        instance.reminders.filter(is_sent=False).delete()

        # Make sure scheduled_datetime is timezone-aware for comparisons
        scheduled_dt = instance.scheduled_datetime
        if timezone.is_naive(scheduled_dt):
            scheduled_dt = timezone.make_aware(scheduled_dt)

        # Create 24-hour reminder
        reminder_24h = scheduled_dt - timedelta(hours=24)
        if reminder_24h > timezone.now():
            AppointmentReminder.objects.create(
                appointment=instance,
                reminder_type='email',
                scheduled_time=reminder_24h
            )

        # Create 1-hour reminder
        reminder_1h = scheduled_dt - timedelta(hours=1)
        if reminder_1h > timezone.now():
            AppointmentReminder.objects.create(
                appointment=instance,
                reminder_type='sms',
                scheduled_time=reminder_1h
            )


@receiver(pre_delete, sender=Appointment)
def log_appointment_deletion(sender, instance, **kwargs):
    """Log when an appointment is deleted."""
    user = getattr(instance, '_current_user', None)
    
    AuditLog.objects.create(
        user=user,
        action='DELETE',
        resource_type='Appointment',
        resource_id=str(instance.id),
        description=f"Appointment deleted: {instance}",
        success=True
    )