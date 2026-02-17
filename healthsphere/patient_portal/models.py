"""
HealthSphere AI - Patient Portal Models
=======================================

Models for patient self-service features.

Models:
- PatientProfile: Extended patient information
- Appointment: Patient appointments with doctors
- HealthMetric: Self-reported health metrics
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class PatientProfile(models.Model):
    """
    Patient Profile Model
    =====================
    
    Extended profile information specific to patients.
    Supplements the UserProfile with patient-specific data.
    """
    
    # Insurance type choices
    INSURANCE_TYPES = [
        ('private', 'Private Insurance'),
        ('public', 'Public Insurance'),
        ('medicare', 'Medicare'),
        ('medicaid', 'Medicaid'),
        ('none', 'No Insurance'),
        ('other', 'Other'),
    ]
    
    # Link to User
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_profile',
        help_text='The patient user account'
    )
    
    # Medical information
    primary_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_patients',
        limit_choices_to={'role__name': 'doctor'},
        help_text='Primary care physician'
    )
    medical_record_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text='Hospital medical record number'
    )
    
    # Insurance information
    insurance_type = models.CharField(
        max_length=20,
        choices=INSURANCE_TYPES,
        default='none',
        help_text='Type of health insurance'
    )
    insurance_provider = models.CharField(
        max_length=100,
        blank=True,
        help_text='Insurance company name'
    )
    insurance_policy_number = models.CharField(
        max_length=50,
        blank=True,
        help_text='Insurance policy number'
    )
    
    # Health preferences
    preferred_pharmacy = models.CharField(
        max_length=200,
        blank=True,
        help_text='Preferred pharmacy for prescriptions'
    )
    communication_preference = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('sms', 'SMS'),
            ('portal', 'Patient Portal'),
        ],
        default='email',
        help_text='Preferred communication method'
    )
    
    # Consent flags
    consent_to_research = models.BooleanField(
        default=False,
        help_text='Consent to use data for research'
    )
    consent_to_marketing = models.BooleanField(
        default=False,
        help_text='Consent to receive marketing communications'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'
    
    def __str__(self):
        return f"Patient Profile for {self.user.get_full_name()}"


class Appointment(models.Model):
    """
    Appointment Model
    =================
    
    Manages patient appointments with healthcare providers.
    """
    
    # Appointment type choices
    APPOINTMENT_TYPES = [
        ('consultation', 'Consultation'),
        ('follow_up', 'Follow-up'),
        ('checkup', 'Regular Checkup'),
        ('vaccination', 'Vaccination'),
        ('lab_test', 'Lab Test'),
        ('imaging', 'Imaging/Scan'),
        ('procedure', 'Procedure'),
        ('emergency', 'Emergency'),
        ('telemedicine', 'Telemedicine'),
        ('other', 'Other'),
    ]
    
    # Status choices
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    # Fields
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
        limit_choices_to={'role__name': 'patient'},
        help_text='Patient booking the appointment'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'role__name': 'doctor'},
        help_text='Doctor for the appointment'
    )
    appointment_type = models.CharField(
        max_length=20,
        choices=APPOINTMENT_TYPES,
        default='consultation',
        help_text='Type of appointment'
    )
    appointment_date = models.DateField(
        help_text='Date of appointment'
    )
    appointment_time = models.TimeField(
        help_text='Time of appointment'
    )
    duration_minutes = models.PositiveIntegerField(
        default=30,
        help_text='Expected duration in minutes'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        help_text='Appointment status'
    )
    reason = models.TextField(
        blank=True,
        help_text='Reason for the appointment'
    )
    notes = models.TextField(
        blank=True,
        help_text='Additional notes'
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text='Appointment location (room, department)'
    )
    is_telemedicine = models.BooleanField(
        default=False,
        help_text='Whether this is a telemedicine appointment'
    )
    meeting_link = models.URLField(
        blank=True,
        help_text='Video call link for telemedicine'
    )
    
    # Reminders
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
        ordering = ['appointment_date', 'appointment_time']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} with Dr. {self.doctor.get_full_name()} on {self.appointment_date}"
    
    @property
    def datetime(self):
        """Combine date and time into datetime."""
        return timezone.make_aware(
            timezone.datetime.combine(self.appointment_date, self.appointment_time)
        )
    
    @property
    def is_upcoming(self):
        """Check if appointment is in the future."""
        return self.datetime > timezone.now()
    
    @property
    def is_today(self):
        """Check if appointment is today."""
        return self.appointment_date == timezone.now().date()


class HealthMetric(models.Model):
    """
    Health Metric Model
    ===================
    
    Self-reported health metrics from patients.
    Used for tracking health trends over time.
    """
    
    # Metric type choices
    METRIC_TYPES = [
        ('weight', 'Weight (kg)'),
        ('blood_pressure', 'Blood Pressure'),
        ('heart_rate', 'Heart Rate (bpm)'),
        ('blood_glucose', 'Blood Glucose (mg/dL)'),
        ('temperature', 'Temperature (°C)'),
        ('steps', 'Steps'),
        ('sleep_hours', 'Sleep Hours'),
        ('water_intake', 'Water Intake (L)'),
        ('mood', 'Mood (1-10)'),
        ('pain_level', 'Pain Level (1-10)'),
        ('exercise_minutes', 'Exercise (minutes)'),
        ('calories', 'Calories Consumed'),
        ('other', 'Other'),
    ]
    
    # Fields
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='health_metrics',
        limit_choices_to={'role__name': 'patient'},
        help_text='Patient recording the metric'
    )
    metric_type = models.CharField(
        max_length=20,
        choices=METRIC_TYPES,
        help_text='Type of health metric'
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Metric value'
    )
    secondary_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Secondary value (e.g., diastolic for blood pressure)'
    )
    unit = models.CharField(
        max_length=20,
        blank=True,
        help_text='Unit of measurement'
    )
    notes = models.TextField(
        blank=True,
        help_text='Additional notes'
    )
    recorded_at = models.DateTimeField(
        default=timezone.now,
        help_text='When the metric was recorded'
    )
    
    # Source of data
    source = models.CharField(
        max_length=50,
        default='manual',
        choices=[
            ('manual', 'Manual Entry'),
            ('device', 'Connected Device'),
            ('imported', 'Imported'),
        ],
        help_text='How the metric was recorded'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Health Metric'
        verbose_name_plural = 'Health Metrics'
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.get_metric_type_display()}: {self.value} - {self.patient.get_full_name()}"
    
    @property
    def formatted_value(self):
        """Return formatted value with unit."""
        if self.metric_type == 'blood_pressure' and self.secondary_value:
            return f"{int(self.value)}/{int(self.secondary_value)} mmHg"
        elif self.unit:
            return f"{self.value} {self.unit}"
        return str(self.value)
