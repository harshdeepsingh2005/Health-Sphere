"""
HealthSphere AI - E-Prescriptions Models
=======================================

Models for electronic prescriptions, medications, and pharmacy integration.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
import uuid

User = get_user_model()


class MedicationDatabase(models.Model):
    """
    Database of medications with NDC codes and drug information.
    """
    
    DOSAGE_FORMS = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('liquid', 'Liquid'),
        ('injection', 'Injection'),
        ('topical', 'Topical'),
        ('inhaler', 'Inhaler'),
        ('patch', 'Patch'),
        ('suppository', 'Suppository'),
        ('drops', 'Drops'),
        ('cream', 'Cream'),
        ('ointment', 'Ointment'),
        ('spray', 'Spray'),
    ]
    
    DRUG_CLASSES = [
        ('antibiotic', 'Antibiotic'),
        ('analgesic', 'Pain Reliever'),
        ('antihypertensive', 'Blood Pressure'),
        ('anticoagulant', 'Blood Thinner'),
        ('antidiabetic', 'Diabetes'),
        ('antidepressant', 'Antidepressant'),
        ('antihistamine', 'Allergy'),
        ('bronchodilator', 'Respiratory'),
        ('diuretic', 'Diuretic'),
        ('steroid', 'Corticosteroid'),
        ('vitamin', 'Vitamin/Supplement'),
        ('other', 'Other'),
    ]
    
    # Unique identifiers
    ndc_code = models.CharField(max_length=12, unique=True, help_text="National Drug Code")
    rxnorm_code = models.CharField(max_length=20, blank=True, null=True, help_text="RxNorm Concept ID")
    
    # Basic drug information
    generic_name = models.CharField(max_length=200, db_index=True)
    brand_name = models.CharField(max_length=200, blank=True)
    strength = models.CharField(max_length=100, help_text="e.g., '500mg', '10mg/5ml'")
    dosage_form = models.CharField(max_length=20, choices=DOSAGE_FORMS)
    route_of_administration = models.CharField(max_length=50, default='oral')
    
    # Classification
    drug_class = models.CharField(max_length=30, choices=DRUG_CLASSES)
    controlled_substance_schedule = models.CharField(
        max_length=5, blank=True, null=True,
        help_text="DEA schedule: CI, CII, CIII, CIV, CV"
    )
    
    # Clinical information
    therapeutic_class = models.CharField(max_length=100, blank=True)
    pharmacologic_class = models.CharField(max_length=100, blank=True)
    
    # Regulatory
    fda_approved = models.BooleanField(default=True)
    requires_prescription = models.BooleanField(default=True)
    otc_available = models.BooleanField(default=False, help_text="Over-the-counter available")
    
    # Safety information
    black_box_warning = models.BooleanField(default=False)
    pregnancy_category = models.CharField(max_length=5, blank=True, help_text="A, B, C, D, X")
    
    # Administrative
    manufacturer = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescriptions_medication_database'
        indexes = [
            models.Index(fields=['generic_name']),
            models.Index(fields=['brand_name']),
            models.Index(fields=['drug_class']),
            models.Index(fields=['controlled_substance_schedule']),
        ]
        verbose_name = "Medication"
        verbose_name_plural = "Medication Database"
    
    def __str__(self):
        name = self.brand_name if self.brand_name else self.generic_name
        return f"{name} {self.strength} ({self.dosage_form})"
    
    @property
    def is_controlled_substance(self):
        return bool(self.controlled_substance_schedule)
    
    @property
    def full_name(self):
        if self.brand_name and self.generic_name != self.brand_name:
            return f"{self.brand_name} ({self.generic_name})"
        return self.generic_name


class DrugAllergy(models.Model):
    """
    Patient drug allergies and adverse reactions.
    """
    
    SEVERITY_LEVELS = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('life_threatening', 'Life Threatening'),
    ]
    
    REACTION_TYPES = [
        ('allergic', 'Allergic Reaction'),
        ('intolerance', 'Drug Intolerance'),
        ('adverse_effect', 'Adverse Effect'),
        ('contraindication', 'Contraindication'),
    ]
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drug_allergies')
    medication = models.ForeignKey(MedicationDatabase, on_delete=models.CASCADE, blank=True, null=True)
    drug_class = models.CharField(max_length=100, blank=True, help_text="If allergy to entire drug class")
    
    reaction_type = models.CharField(max_length=20, choices=REACTION_TYPES, default='allergic')
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    symptoms = models.TextField(help_text="Description of allergic reaction symptoms")
    
    date_identified = models.DateField(auto_now_add=True)
    verified_by_doctor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='verified_allergies'
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescriptions_drug_allergy'
        unique_together = ['patient', 'medication']
        indexes = [
            models.Index(fields=['patient', 'is_active']),
        ]
    
    def __str__(self):
        drug = str(self.medication) if self.medication else self.drug_class
        return f"{self.patient.get_full_name()} - {drug} ({self.severity})"


class Prescription(models.Model):
    """
    Electronic prescription record.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('transmitted', 'Transmitted to Pharmacy'),
        ('filled', 'Filled by Pharmacy'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('denied', 'Denied'),
    ]
    
    PRIORITY_CHOICES = [
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('stat', 'STAT (Immediate)'),
    ]
    
    # Identifiers
    prescription_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    rx_number = models.CharField(max_length=20, unique=True, blank=True)  # Pharmacy RX number
    
    # Core prescription data
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions')
    prescriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescribed_medications')
    medication = models.ForeignKey(MedicationDatabase, on_delete=models.CASCADE)
    
    # Dosing information
    dosage_instructions = models.TextField(help_text="Complete dosing instructions")
    quantity = models.PositiveIntegerField(help_text="Quantity to dispense")
    days_supply = models.PositiveIntegerField(help_text="Expected days of therapy")
    refills_authorized = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(5)])
    refills_used = models.PositiveIntegerField(default=0)
    
    # Prescription details
    diagnosis_code = models.CharField(max_length=20, blank=True, help_text="ICD-10 code")
    diagnosis_description = models.CharField(max_length=200, blank=True)
    indication = models.TextField(blank=True, help_text="Reason for prescribing")
    
    # Administrative
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='routine')
    
    # Dates
    date_prescribed = models.DateTimeField(auto_now_add=True)
    effective_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField()  # Usually 1 year from prescribed date
    last_filled_date = models.DateTimeField(blank=True, null=True)
    
    # Pharmacy information
    pharmacy = models.ForeignKey('Pharmacy', on_delete=models.SET_NULL, null=True, blank=True)
    transmitted_at = models.DateTimeField(null=True, blank=True)
    
    # Safety and verification
    allergy_checked = models.BooleanField(default=False)
    interaction_checked = models.BooleanField(default=False)
    duplicate_therapy_checked = models.BooleanField(default=False)
    
    # Electronic signature
    electronically_signed = models.BooleanField(default=False)
    signature_timestamp = models.DateTimeField(null=True, blank=True)
    
    # Notes and special instructions
    pharmacy_notes = models.TextField(blank=True, help_text="Notes for pharmacist")
    patient_instructions = models.TextField(blank=True, help_text="Patient counseling notes")
    prescriber_notes = models.TextField(blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescriptions_prescription'
        ordering = ['-date_prescribed']
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['prescriber', 'date_prescribed']),
            models.Index(fields=['prescription_id']),
            models.Index(fields=['status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.expiration_date:
            # Set expiration to 1 year from effective date for most prescriptions
            self.expiration_date = self.effective_date + timedelta(days=365)
            
            # Controlled substances have shorter expiration periods
            if self.medication.is_controlled_substance:
                if self.medication.controlled_substance_schedule in ['CI', 'CII']:
                    # Schedule II: 90 days
                    self.expiration_date = self.effective_date + timedelta(days=90)
                else:
                    # Schedule III-V: 6 months
                    self.expiration_date = self.effective_date + timedelta(days=180)
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Rx {self.prescription_id}: {self.medication} for {self.patient.get_full_name()}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expiration_date
    
    @property
    def has_refills_remaining(self):
        return self.refills_used < self.refills_authorized
    
    @property
    def refills_remaining(self):
        return max(0, self.refills_authorized - self.refills_used)
    
    @property
    def can_be_refilled(self):
        return (
            self.status == 'filled' and
            self.has_refills_remaining and
            not self.is_expired
        )
    
    @property
    def requires_new_prescription(self):
        return (
            self.is_expired or
            not self.has_refills_remaining or
            self.medication.is_controlled_substance
        )


class Pharmacy(models.Model):
    """
    Pharmacy information for prescription transmission.
    """
    
    PHARMACY_TYPES = [
        ('retail', 'Retail Pharmacy'),
        ('hospital', 'Hospital Pharmacy'),
        ('mail_order', 'Mail Order'),
        ('specialty', 'Specialty Pharmacy'),
        ('compounding', 'Compounding Pharmacy'),
    ]
    
    # Basic information
    name = models.CharField(max_length=200)
    pharmacy_type = models.CharField(max_length=20, choices=PHARMACY_TYPES, default='retail')
    
    # Identifiers
    ncpdp_id = models.CharField(max_length=7, unique=True, help_text="NCPDP Provider ID")
    npi_number = models.CharField(max_length=10, blank=True, help_text="National Provider Identifier")
    dea_number = models.CharField(max_length=15, blank=True, help_text="DEA Registration Number")
    
    # Contact information
    phone = models.CharField(max_length=20)
    fax = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Address
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    
    # Operational details
    hours_of_operation = models.JSONField(default=dict, blank=True)
    accepts_electronic_prescriptions = models.BooleanField(default=True)
    supports_controlled_substances = models.BooleanField(default=True)
    
    # Network information
    is_preferred_network = models.BooleanField(default=False)
    insurance_networks = models.JSONField(default=list, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    verified_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescriptions_pharmacy'
        indexes = [
            models.Index(fields=['ncpdp_id']),
            models.Index(fields=['city', 'state']),
            models.Index(fields=['is_active']),
        ]
        verbose_name_plural = "Pharmacies"
    
    def __str__(self):
        return f"{self.name} - {self.city}, {self.state}"


class PrescriptionRefill(models.Model):
    """
    Prescription refill requests and tracking.
    """
    
    STATUS_CHOICES = [
        ('requested', 'Refill Requested'),
        ('approved', 'Approved by Doctor'),
        ('denied', 'Denied'),
        ('transmitted', 'Transmitted to Pharmacy'),
        ('filled', 'Filled'),
        ('picked_up', 'Picked Up'),
    ]
    
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='refills')
    refill_number = models.PositiveIntegerField()  # Which refill this is (1st, 2nd, etc.)
    
    # Request information
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refill_requests')
    request_date = models.DateTimeField(auto_now_add=True)
    request_method = models.CharField(
        max_length=20,
        choices=[
            ('patient', 'Patient Request'),
            ('pharmacy', 'Pharmacy Request'),
            ('automatic', 'Automatic Refill'),
            ('provider', 'Provider Initiated'),
        ],
        default='patient'
    )
    
    # Approval information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_refills'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    denial_reason = models.TextField(blank=True)
    
    # Fulfillment information
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.SET_NULL, null=True, blank=True)
    filled_date = models.DateTimeField(null=True, blank=True)
    picked_up_date = models.DateTimeField(null=True, blank=True)
    
    # Modified prescription details (if changed)
    quantity_dispensed = models.PositiveIntegerField(null=True, blank=True)
    days_supply_dispensed = models.PositiveIntegerField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescriptions_prescription_refill'
        unique_together = ['prescription', 'refill_number']
        ordering = ['-request_date']
    
    def __str__(self):
        return f"Refill #{self.refill_number} for {self.prescription}"


class DrugInteraction(models.Model):
    """
    Drug-drug interaction database and patient-specific interactions.
    """
    
    INTERACTION_LEVELS = [
        ('contraindicated', 'Contraindicated'),
        ('major', 'Major'),
        ('moderate', 'Moderate'),
        ('minor', 'Minor'),
    ]
    
    # Interacting medications
    medication_1 = models.ForeignKey(
        MedicationDatabase, on_delete=models.CASCADE,
        related_name='interactions_as_drug1'
    )
    medication_2 = models.ForeignKey(
        MedicationDatabase, on_delete=models.CASCADE,
        related_name='interactions_as_drug2'
    )
    
    # Interaction details
    interaction_level = models.CharField(max_length=20, choices=INTERACTION_LEVELS)
    interaction_type = models.CharField(max_length=100, help_text="e.g., Pharmacokinetic, Pharmacodynamic")
    
    # Clinical information
    clinical_effects = models.TextField(help_text="Description of interaction effects")
    mechanism = models.TextField(blank=True, help_text="Mechanism of interaction")
    management_strategy = models.TextField(blank=True, help_text="How to manage the interaction")
    
    # Evidence and sources
    evidence_level = models.CharField(
        max_length=20,
        choices=[
            ('established', 'Established'),
            ('probable', 'Probable'),
            ('suspected', 'Suspected'),
            ('possible', 'Possible'),
            ('unlikely', 'Unlikely'),
        ],
        default='probable'
    )
    
    # Administrative
    is_active = models.BooleanField(default=True)
    source = models.CharField(max_length=100, blank=True, help_text="Data source")
    last_reviewed = models.DateField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescriptions_drug_interaction'
        unique_together = ['medication_1', 'medication_2']
        indexes = [
            models.Index(fields=['interaction_level']),
            models.Index(fields=['medication_1', 'medication_2']),
        ]
    
    def __str__(self):
        return f"{self.medication_1} ↔ {self.medication_2} ({self.interaction_level})"


class PrescriptionAuditLog(models.Model):
    """
    Audit log for prescription changes and access (HIPAA compliance).
    """
    
    ACTION_CHOICES = [
        ('created', 'Prescription Created'),
        ('modified', 'Prescription Modified'),
        ('approved', 'Prescription Approved'),
        ('transmitted', 'Transmitted to Pharmacy'),
        ('cancelled', 'Prescription Cancelled'),
        ('refill_requested', 'Refill Requested'),
        ('refill_approved', 'Refill Approved'),
        ('filled', 'Prescription Filled'),
        ('viewed', 'Prescription Viewed'),
        ('printed', 'Prescription Printed'),
    ]
    
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    # Change tracking
    field_changes = models.JSONField(default=dict, blank=True, help_text="What fields were changed")
    previous_values = models.JSONField(default=dict, blank=True, help_text="Previous field values")
    new_values = models.JSONField(default=dict, blank=True, help_text="New field values")
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=100, blank=True)
    
    # Additional details
    reason = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'prescriptions_prescription_audit_log'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['prescription', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp}"
