"""
HealthSphere AI - Appointment Management Models
==============================================

This module defines models for managing appointments, schedules,
and appointment-related functionality in the HealthSphere AI platform.

Models:
- AppointmentType: Types of medical appointments
- DoctorSchedule: Doctor availability schedules
- Appointment: Patient appointments with doctors
- AppointmentReminder: Automated appointment reminders
"""

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import User
from datetime import datetime, timedelta


class AppointmentType(models.Model):
    """
    Appointment Type Model
    =====================
    
    Defines different types of appointments available in the system
    (e.g., Consultation, Follow-up, Emergency, Telemedicine).
    """
    
    CONSULTATION = 'consultation'
    FOLLOW_UP = 'follow_up'
    EMERGENCY = 'emergency'
    TELEMEDICINE = 'telemedicine'
    ROUTINE_CHECKUP = 'routine_checkup'
    SPECIALIST = 'specialist'
    
    TYPE_CHOICES = [
        (CONSULTATION, 'Consultation'),
        (FOLLOW_UP, 'Follow-up'),
        (EMERGENCY, 'Emergency'),
        (TELEMEDICINE, 'Telemedicine'),
        (ROUTINE_CHECKUP, 'Routine Checkup'),
        (SPECIALIST, 'Specialist Visit'),
    ]
    
    name = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        unique=True,
        help_text='Type of appointment'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Description of the appointment type'
    )
    
    duration_minutes = models.PositiveIntegerField(
        default=30,
        help_text='Default duration in minutes'
    )
    
    color_code = models.CharField(
        max_length=7,
        default='#007bff',
        help_text='Color code for calendar display (hex format)'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this appointment type is currently available'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Appointment Type'
        verbose_name_plural = 'Appointment Types'
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()


class DoctorSchedule(models.Model):
    """
    Doctor Schedule Model
    ====================
    
    Defines doctor availability schedules including working hours,
    break times, and availability for appointments.
    """
    
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role__name': 'doctor'},
        related_name='doctor_schedules',
        help_text='Doctor this schedule belongs to'
    )
    
    day_of_week = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        help_text='Day of the week (0=Monday, 6=Sunday)'
    )
    
    start_time = models.TimeField(
        help_text='Start time for availability'
    )
    
    end_time = models.TimeField(
        help_text='End time for availability'
    )
    
    break_start_time = models.TimeField(
        null=True,
        blank=True,
        help_text='Break start time (optional)'
    )
    
    break_end_time = models.TimeField(
        null=True,
        blank=True,
        help_text='Break end time (optional)'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this schedule is currently active'
    )
    
    max_appointments = models.PositiveIntegerField(
        default=20,
        help_text='Maximum appointments allowed per day'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Doctor Schedule'
        verbose_name_plural = 'Doctor Schedules'
        unique_together = ['doctor', 'day_of_week']
        ordering = ['doctor', 'day_of_week', 'start_time']
    
    def __str__(self):
        day_name = dict(self.WEEKDAY_CHOICES)[self.day_of_week]
        return f"{self.doctor.get_full_name()} - {day_name} {self.start_time}-{self.end_time}"
    
    def clean(self):
        """Validate schedule times."""
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time")
        
        if self.break_start_time and self.break_end_time:
            if self.break_start_time >= self.break_end_time:
                raise ValidationError("Break start time must be before break end time")
            
            if not (self.start_time <= self.break_start_time < self.break_end_time <= self.end_time):
                raise ValidationError("Break times must be within working hours")


class Appointment(models.Model):
    """
    Appointment Model
    ================
    
    Represents a scheduled appointment between a patient and a doctor.
    Includes status tracking, notes, and reminder functionality.
    """
    
    REQUESTED = 'requested'
    CONFIRMED = 'confirmed'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    NO_SHOW = 'no_show'
    RESCHEDULED = 'rescheduled'
    
    STATUS_CHOICES = [
        (REQUESTED, 'Requested'),
        (CONFIRMED, 'Confirmed'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (NO_SHOW, 'No Show'),
        (RESCHEDULED, 'Rescheduled'),
    ]
    
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role__name': 'patient'},
        related_name='appointments_as_patient',
        help_text='Patient for this appointment'
    )
    
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role__name': 'doctor'},
        related_name='appointments_as_doctor',
        help_text='Doctor for this appointment'
    )
    
    appointment_type = models.ForeignKey(
        AppointmentType,
        on_delete=models.PROTECT,
        related_name='appointments',
        help_text='Type of appointment'
    )
    
    scheduled_date = models.DateField(
        help_text='Date of the appointment'
    )
    
    scheduled_time = models.TimeField(
        help_text='Time of the appointment'
    )
    
    duration_minutes = models.PositiveIntegerField(
        help_text='Duration of appointment in minutes'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=REQUESTED,
        help_text='Current status of the appointment'
    )
    
    reason = models.TextField(
        help_text='Reason for the appointment'
    )
    
    notes = models.TextField(
        blank=True,
        help_text='Additional notes about the appointment'
    )
    
    doctor_notes = models.TextField(
        blank=True,
        help_text='Doctor notes after the appointment'
    )
    
    is_telemedicine = models.BooleanField(
        default=False,
        help_text='Whether this is a telemedicine appointment'
    )
    
    video_room_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='Video room ID for telemedicine appointments'
    )
    
    # Cancellation tracking
    cancelled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments_cancelled_by_user',
        help_text='User who cancelled the appointment'
    )
    
    cancellation_reason = models.TextField(
        blank=True,
        help_text='Reason for cancellation'
    )
    
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the appointment was cancelled'
    )
    
    # Reminder settings
    send_reminder = models.BooleanField(
        default=True,
        help_text='Whether to send appointment reminders'
    )
    
    reminder_sent = models.BooleanField(
        default=False,
        help_text='Whether reminder has been sent'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['scheduled_date', 'scheduled_time']
        indexes = [
            models.Index(fields=['patient', '-scheduled_date']),
            models.Index(fields=['doctor', '-scheduled_date']),
            models.Index(fields=['status', '-scheduled_date']),
            models.Index(fields=['scheduled_date', 'scheduled_time']),
        ]
    
    def __str__(self):
        return f"{self.patient.get_full_name()} with {self.doctor.get_full_name()} on {self.scheduled_date} at {self.scheduled_time}"
    
    @property
    def scheduled_datetime(self):
        """Get combined datetime for the appointment."""
        return datetime.combine(self.scheduled_date, self.scheduled_time)
    
    @property
    def end_datetime(self):
        """Get the end datetime for the appointment."""
        return self.scheduled_datetime + timedelta(minutes=self.duration_minutes)
    
    @property
    def is_past_due(self):
        """Check if the appointment is past its scheduled time."""
        return self.scheduled_datetime < timezone.now()
    
    @property
    def can_be_cancelled(self):
        """Check if the appointment can still be cancelled."""
        return (
            self.status in [self.REQUESTED, self.CONFIRMED] and
            not self.is_past_due
        )
    
    @property
    def can_be_rescheduled(self):
        """Check if the appointment can be rescheduled."""
        return (
            self.status in [self.REQUESTED, self.CONFIRMED] and
            not self.is_past_due
        )
    
    def clean(self):
        """Validate appointment data."""
        if self.scheduled_date < timezone.now().date():
            raise ValidationError("Cannot schedule appointment in the past")
        
        if self.patient.role.name != 'patient':
            raise ValidationError("Patient must have patient role")
        
        if self.doctor.role.name != 'doctor':
            raise ValidationError("Doctor must have doctor role")
    
    def save(self, *args, **kwargs):
        """Custom save to handle duration and validation."""
        if not self.duration_minutes:
            self.duration_minutes = self.appointment_type.duration_minutes
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def cancel(self, cancelled_by, reason=""):
        """Cancel the appointment."""
        if not self.can_be_cancelled:
            raise ValidationError("This appointment cannot be cancelled")
        
        self.status = self.CANCELLED
        self.cancelled_by = cancelled_by
        self.cancellation_reason = reason
        self.cancelled_at = timezone.now()
        self.save()
    
    def confirm(self):
        """Confirm a requested appointment."""
        if self.status != self.REQUESTED:
            raise ValidationError("Only requested appointments can be confirmed")
        
        self.status = self.CONFIRMED
        self.save()
    
    def complete(self, doctor_notes=""):
        """Mark appointment as completed."""
        if self.status != self.IN_PROGRESS:
            raise ValidationError("Only in-progress appointments can be completed")
        
        self.status = self.COMPLETED
        self.doctor_notes = doctor_notes
        self.save()
    
    def start(self):
        """Start the appointment (mark as in progress)."""
        if self.status != self.CONFIRMED:
            raise ValidationError("Only confirmed appointments can be started")
        
        self.status = self.IN_PROGRESS
        self.save()


class AppointmentReminder(models.Model):
    """
    Appointment Reminder Model
    =========================
    
    Tracks appointment reminders sent to patients via email or SMS.
    Supports multiple reminder types (24hr, 1hr before).
    """
    
    EMAIL = 'email'
    SMS = 'sms'
    PUSH = 'push'
    
    REMINDER_TYPE_CHOICES = [
        (EMAIL, 'Email'),
        (SMS, 'SMS'),
        (PUSH, 'Push Notification'),
    ]
    
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='reminders',
        help_text='Appointment this reminder is for'
    )
    
    reminder_type = models.CharField(
        max_length=10,
        choices=REMINDER_TYPE_CHOICES,
        help_text='Type of reminder'
    )
    
    scheduled_time = models.DateTimeField(
        help_text='When the reminder should be sent'
    )
    
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the reminder was actually sent'
    )
    
    is_sent = models.BooleanField(
        default=False,
        help_text='Whether the reminder has been sent'
    )
    
    delivery_status = models.CharField(
        max_length=20,
        blank=True,
        help_text='Delivery status (delivered, failed, etc.)'
    )
    
    error_message = models.TextField(
        blank=True,
        help_text='Error message if delivery failed'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Appointment Reminder'
        verbose_name_plural = 'Appointment Reminders'
        ordering = ['scheduled_time']
        unique_together = ['appointment', 'reminder_type', 'scheduled_time']
    
    def __str__(self):
        return f"{self.get_reminder_type_display()} reminder for {self.appointment}"
    
    def send(self):
        """Send the reminder (implement in service layer)."""
        # This would be implemented in a service layer with actual email/SMS providers
        pass