"""
HealthSphere AI - Clinical Portal Models
========================================

Models for clinical care management.

Models:
- MedicalRecord: Patient medical history and records
- TreatmentPlan: Treatment plans and prescriptions
- VitalRecord: Patient vital signs recordings
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class MedicalRecord(models.Model):
    """
    Medical Record Model
    ====================
    
    Stores patient medical history and clinical notes.
    Created by doctors and nurses during patient encounters.
    """
    
    # Record type choices
    RECORD_TYPES = [
        ('consultation', 'Consultation'),
        ('diagnosis', 'Diagnosis'),
        ('lab_result', 'Lab Result'),
        ('imaging', 'Imaging Report'),
        ('procedure', 'Procedure Note'),
        ('progress', 'Progress Note'),
        ('discharge', 'Discharge Summary'),
        ('other', 'Other'),
    ]
    
    # Priority/Severity choices
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Fields
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medical_records',
        limit_choices_to={'role__name': 'patient'},
        help_text='Patient this record belongs to'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_records',
        help_text='Healthcare provider who created this record'
    )
    record_type = models.CharField(
        max_length=20,
        choices=RECORD_TYPES,
        default='consultation',
        help_text='Type of medical record'
    )
    title = models.CharField(
        max_length=200,
        help_text='Record title or summary'
    )
    description = models.TextField(
        help_text='Detailed description or notes'
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='low',
        help_text='Severity or priority level'
    )
    diagnosis_code = models.CharField(
        max_length=20,
        blank=True,
        help_text='ICD-10 diagnosis code (if applicable)'
    )
    attachments = models.FileField(
        upload_to='medical_records/',
        null=True,
        blank=True,
        help_text='Attached files (lab reports, images, etc.)'
    )
    is_confidential = models.BooleanField(
        default=False,
        help_text='Mark as confidential (restricted access)'
    )
    
    # AI-related fields (for integration with AI services)
    ai_risk_score = models.FloatField(
        null=True,
        blank=True,
        help_text='AI-predicted risk score (0-100)'
    )
    ai_recommendations = models.TextField(
        blank=True,
        help_text='AI-generated recommendations'
    )
    
    # Timestamps
    record_date = models.DateTimeField(
        default=timezone.now,
        help_text='Date and time of the medical event'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Medical Record'
        verbose_name_plural = 'Medical Records'
        ordering = ['-record_date']
    
    def __str__(self):
        return f"{self.title} - {self.patient.get_full_name()}"


class TreatmentPlan(models.Model):
    """
    Treatment Plan Model
    ====================
    
    Defines treatment plans including medications, procedures,
    and follow-up care instructions.
    """
    
    # Status choices
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold'),
    ]
    
    # Fields
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='treatment_plans',
        limit_choices_to={'role__name': 'patient'},
        help_text='Patient for this treatment plan'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_plans',
        help_text='Doctor who created this plan'
    )
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='treatment_plans',
        help_text='Associated medical record'
    )
    title = models.CharField(
        max_length=200,
        help_text='Treatment plan title'
    )
    description = models.TextField(
        help_text='Detailed treatment description'
    )
    diagnosis = models.TextField(
        help_text='Primary diagnosis for this treatment'
    )
    medications = models.TextField(
        blank=True,
        help_text='Prescribed medications (name, dosage, frequency)'
    )
    procedures = models.TextField(
        blank=True,
        help_text='Scheduled procedures or interventions'
    )
    lifestyle_recommendations = models.TextField(
        blank=True,
        help_text='Diet, exercise, and lifestyle recommendations'
    )
    follow_up_instructions = models.TextField(
        blank=True,
        help_text='Follow-up care instructions'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text='Current status of the treatment plan'
    )
    start_date = models.DateField(
        default=timezone.now,
        help_text='Treatment start date'
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text='Expected treatment end date'
    )
    next_review_date = models.DateField(
        null=True,
        blank=True,
        help_text='Next review/follow-up date'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Treatment Plan'
        verbose_name_plural = 'Treatment Plans'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.patient.get_full_name()}"
    
    @property
    def is_active(self):
        """Check if treatment plan is currently active."""
        return self.status == 'active'
    
    @property
    def duration_days(self):
        """Calculate treatment duration in days."""
        if self.end_date:
            return (self.end_date - self.start_date).days
        return None


class VitalRecord(models.Model):
    """
    Vital Record Model
    ==================
    
    Records patient vital signs measurements.
    Used for monitoring patient health status over time.
    """
    
    # Fields
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vital_records',
        limit_choices_to={'role__name': 'patient'},
        help_text='Patient whose vitals are recorded'
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_vitals',
        help_text='Staff member who recorded the vitals'
    )
    
    # Vital signs
    temperature = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text='Body temperature in Celsius'
    )
    blood_pressure_systolic = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Systolic blood pressure (mmHg)'
    )
    blood_pressure_diastolic = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Diastolic blood pressure (mmHg)'
    )
    heart_rate = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Heart rate (beats per minute)'
    )
    respiratory_rate = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Respiratory rate (breaths per minute)'
    )
    oxygen_saturation = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Blood oxygen saturation (%)'
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Weight in kilograms'
    )
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Height in centimeters'
    )
    blood_glucose = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Blood glucose level (mg/dL)'
    )
    pain_level = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Pain level (0-10 scale)'
    )
    
    # Additional notes
    notes = models.TextField(
        blank=True,
        help_text='Additional observations or notes'
    )
    
    # Timestamps
    recorded_at = models.DateTimeField(
        default=timezone.now,
        help_text='Date and time when vitals were recorded'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Vital Record'
        verbose_name_plural = 'Vital Records'
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"Vitals for {self.patient.get_full_name()} at {self.recorded_at}"
    
    @property
    def blood_pressure(self):
        """Return formatted blood pressure reading."""
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return None
    
    @property
    def bmi(self):
        """Calculate Body Mass Index."""
        if self.weight and self.height:
            height_m = float(self.height) / 100  # Convert cm to m
            return round(float(self.weight) / (height_m ** 2), 1)
        return None
