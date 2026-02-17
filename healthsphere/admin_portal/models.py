"""
HealthSphere AI - Admin Portal Models
=====================================

Models for hospital administration and resource management.

Models:
- HospitalResource: Equipment, beds, rooms, and other hospital resources
- AdmissionRecord: Patient admission and discharge records
- StaffSchedule: Staff work schedules and shifts
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class HospitalResource(models.Model):
    """
    Hospital Resource Model
    =======================
    
    Tracks hospital resources like beds, equipment, rooms, etc.
    Used for resource monitoring and capacity planning.
    """
    
    # Resource type choices
    RESOURCE_TYPES = [
        ('bed', 'Hospital Bed'),
        ('icu_bed', 'ICU Bed'),
        ('ventilator', 'Ventilator'),
        ('wheelchair', 'Wheelchair'),
        ('monitor', 'Patient Monitor'),
        ('room', 'Room'),
        ('operating_room', 'Operating Room'),
        ('ambulance', 'Ambulance'),
        ('other', 'Other'),
    ]
    
    # Status choices
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
        ('out_of_service', 'Out of Service'),
    ]
    
    # Fields
    name = models.CharField(
        max_length=100,
        help_text='Name or identifier of the resource'
    )
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPES,
        help_text='Type of resource'
    )
    description = models.TextField(
        blank=True,
        help_text='Description or notes about the resource'
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text='Physical location (e.g., Ward A, Room 101)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        help_text='Current status of the resource'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        help_text='Number of units (for countable resources)'
    )
    last_maintenance = models.DateField(
        null=True,
        blank=True,
        help_text='Date of last maintenance'
    )
    next_maintenance = models.DateField(
        null=True,
        blank=True,
        help_text='Scheduled next maintenance date'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Hospital Resource'
        verbose_name_plural = 'Hospital Resources'
        ordering = ['resource_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_resource_type_display()})"
    
    @property
    def is_available(self):
        """Check if resource is available."""
        return self.status == 'available'


class AdmissionRecord(models.Model):
    """
    Admission Record Model
    ======================
    
    Tracks patient admissions and discharges.
    Links patients to their hospital stay information.
    """
    
    # Admission type choices
    ADMISSION_TYPES = [
        ('emergency', 'Emergency'),
        ('scheduled', 'Scheduled'),
        ('transfer', 'Transfer'),
        ('observation', 'Observation'),
    ]
    
    # Status choices
    STATUS_CHOICES = [
        ('admitted', 'Admitted'),
        ('discharged', 'Discharged'),
        ('transferred', 'Transferred'),
        ('deceased', 'Deceased'),
    ]
    
    # Fields
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admissions',
        limit_choices_to={'role__name': 'patient'},
        help_text='The admitted patient'
    )
    admission_type = models.CharField(
        max_length=20,
        choices=ADMISSION_TYPES,
        default='scheduled',
        help_text='Type of admission'
    )
    admission_date = models.DateTimeField(
        default=timezone.now,
        help_text='Date and time of admission'
    )
    discharge_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date and time of discharge'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='admitted',
        help_text='Current admission status'
    )
    ward = models.CharField(
        max_length=50,
        blank=True,
        help_text='Ward or department'
    )
    room_number = models.CharField(
        max_length=20,
        blank=True,
        help_text='Room number'
    )
    bed_number = models.CharField(
        max_length=20,
        blank=True,
        help_text='Bed number'
    )
    attending_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attended_admissions',
        limit_choices_to={'role__name': 'doctor'},
        help_text='Primary attending physician'
    )
    diagnosis = models.TextField(
        blank=True,
        help_text='Initial diagnosis'
    )
    notes = models.TextField(
        blank=True,
        help_text='Additional notes'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Admission Record'
        verbose_name_plural = 'Admission Records'
        ordering = ['-admission_date']
    
    def __str__(self):
        return f"Admission #{self.id} - {self.patient.get_full_name()}"
    
    @property
    def is_active(self):
        """Check if admission is currently active."""
        return self.status == 'admitted'
    
    @property
    def length_of_stay(self):
        """Calculate length of stay in days."""
        end_date = self.discharge_date or timezone.now()
        delta = end_date - self.admission_date
        return delta.days


class StaffSchedule(models.Model):
    """
    Staff Schedule Model
    ====================
    
    Manages work schedules for doctors, nurses, and other staff.
    Supports shift-based scheduling.
    """
    
    # Shift choices
    SHIFT_CHOICES = [
        ('morning', 'Morning (6 AM - 2 PM)'),
        ('afternoon', 'Afternoon (2 PM - 10 PM)'),
        ('night', 'Night (10 PM - 6 AM)'),
        ('day', 'Day Shift (8 AM - 6 PM)'),
        ('on_call', 'On Call'),
    ]
    
    # Status choices
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    # Fields
    staff_member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='schedules',
        help_text='Staff member for this schedule'
    )
    date = models.DateField(
        help_text='Date of the scheduled shift'
    )
    shift = models.CharField(
        max_length=20,
        choices=SHIFT_CHOICES,
        help_text='Type of shift'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text='Department or ward assignment'
    )
    start_time = models.TimeField(
        null=True,
        blank=True,
        help_text='Shift start time'
    )
    end_time = models.TimeField(
        null=True,
        blank=True,
        help_text='Shift end time'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        help_text='Schedule status'
    )
    notes = models.TextField(
        blank=True,
        help_text='Additional notes'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Staff Schedule'
        verbose_name_plural = 'Staff Schedules'
        ordering = ['date', 'shift']
        # Prevent duplicate schedules for same staff on same day/shift
        unique_together = ['staff_member', 'date', 'shift']
    
    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.date} ({self.get_shift_display()})"
