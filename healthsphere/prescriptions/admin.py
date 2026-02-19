"""
HealthSphere AI - E-Prescriptions Admin Interface
=================================================

Django admin configuration for prescription management.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from .models import (
    MedicationDatabase,
    DrugAllergy,
    Prescription,
    Pharmacy,
    PrescriptionRefill,
    DrugInteraction,
    PrescriptionAuditLog
)


@admin.register(MedicationDatabase)
class MedicationDatabaseAdmin(admin.ModelAdmin):
    """Admin interface for medication database."""
    
    list_display = [
        'generic_name', 'brand_name', 'strength', 'dosage_form',
        'drug_class', 'controlled_substance_schedule', 'is_active'
    ]
    list_filter = [
        'dosage_form', 'drug_class', 'controlled_substance_schedule',
        'fda_approved', 'requires_prescription', 'is_active'
    ]
    search_fields = ['generic_name', 'brand_name', 'ndc_code', 'manufacturer']
    ordering = ['generic_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('generic_name', 'brand_name'),
                ('ndc_code', 'rxnorm_code'),
                ('strength', 'dosage_form'),
                'route_of_administration',
                'manufacturer'
            )
        }),
        ('Classification', {
            'fields': (
                'drug_class',
                'controlled_substance_schedule',
                'therapeutic_class',
                'pharmacologic_class'
            )
        }),
        ('Regulatory Information', {
            'fields': (
                ('fda_approved', 'requires_prescription', 'otc_available'),
                ('black_box_warning', 'pregnancy_category')
            )
        }),
        ('Status', {
            'fields': (
                'is_active',
                ('created_at', 'updated_at')
            )
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(DrugAllergy)
class DrugAllergyAdmin(admin.ModelAdmin):
    """Admin interface for drug allergies."""
    
    list_display = [
        'patient_name', 'get_drug_name', 'reaction_type', 'severity', 'is_active'
    ]
    list_filter = ['reaction_type', 'severity', 'is_active', 'date_identified']
    search_fields = [
        'patient__username', 'patient__email', 'patient__first_name', 'patient__last_name',
        'medication__generic_name', 'medication__brand_name', 'drug_class'
    ]
    autocomplete_fields = ['patient', 'medication', 'verified_by_doctor']
    readonly_fields = ['date_identified', 'created_at', 'updated_at']
    
    def patient_name(self, obj):
        return obj.patient.get_full_name()
    patient_name.short_description = 'Patient'
    
    def get_drug_name(self, obj):
        if obj.medication:
            return str(obj.medication)
        return obj.drug_class or 'Unknown'
    get_drug_name.short_description = 'Drug/Class'


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    """Admin interface for prescriptions."""
    
    list_display = [
        'prescription_display', 'patient_name', 'prescriber_name',
        'medication_name', 'status', 'priority', 'date_prescribed'
    ]
    list_filter = [
        'status', 'priority', 'electronically_signed',
        'allergy_checked', 'interaction_checked', 'date_prescribed'
    ]
    search_fields = [
        'prescription_id', 'rx_number',
        'patient__username', 'patient__email',
        'prescriber__username', 'prescriber__email',
        'medication__generic_name', 'medication__brand_name'
    ]
    autocomplete_fields = ['patient', 'prescriber', 'medication', 'pharmacy']
    readonly_fields = [
        'prescription_id', 'date_prescribed', 'created_at', 'updated_at',
        'signature_timestamp', 'transmitted_at'
    ]
    date_hierarchy = 'date_prescribed'
    
    fieldsets = (
        ('Prescription Information', {
            'fields': (
                'prescription_id',
                ('patient', 'prescriber'),
                'medication',
                ('status', 'priority')
            )
        }),
        ('Dosing & Supply', {
            'fields': (
                'dosage_instructions',
                ('quantity', 'days_supply'),
                ('refills_authorized', 'refills_used')
            )
        }),
        ('Clinical Information', {
            'fields': (
                ('diagnosis_code', 'diagnosis_description'),
                'indication'
            )
        }),
        ('Dates', {
            'fields': (
                'date_prescribed',
                ('effective_date', 'expiration_date'),
                'last_filled_date'
            )
        }),
        ('Pharmacy & Transmission', {
            'fields': (
                'pharmacy',
                'transmitted_at'
            )
        }),
        ('Safety Checks', {
            'fields': (
                ('allergy_checked', 'interaction_checked', 'duplicate_therapy_checked')
            )
        }),
        ('Electronic Signature', {
            'fields': (
                ('electronically_signed', 'signature_timestamp')
            )
        }),
        ('Notes & Instructions', {
            'fields': (
                'pharmacy_notes',
                'patient_instructions',
                'prescriber_notes'
            )
        }),
        ('Audit Trail', {
            'fields': (
                ('created_at', 'updated_at')
            )
        })
    )
    
    def prescription_display(self, obj):
        return str(obj.prescription_id)[:8] + "..."
    prescription_display.short_description = 'Prescription ID'
    
    def patient_name(self, obj):
        return obj.patient.get_full_name()
    patient_name.short_description = 'Patient'
    
    def prescriber_name(self, obj):
        return obj.prescriber.get_full_name()
    prescriber_name.short_description = 'Prescriber'
    
    def medication_name(self, obj):
        return str(obj.medication)
    medication_name.short_description = 'Medication'


@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    """Admin interface for pharmacies."""
    
    list_display = [
        'name', 'pharmacy_type', 'city', 'state',
        'accepts_electronic_prescriptions', 'is_active'
    ]
    list_filter = [
        'pharmacy_type', 'state', 'accepts_electronic_prescriptions',
        'supports_controlled_substances', 'is_preferred_network', 'is_active'
    ]
    search_fields = ['name', 'ncpdp_id', 'city', 'state', 'zip_code']
    readonly_fields = ['created_at', 'updated_at', 'verified_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('name', 'pharmacy_type'),
                ('ncpdp_id', 'npi_number', 'dea_number')
            )
        }),
        ('Contact Information', {
            'fields': (
                ('phone', 'fax'),
                ('email', 'website')
            )
        }),
        ('Address', {
            'fields': (
                'address_line_1',
                'address_line_2',
                ('city', 'state', 'zip_code')
            )
        }),
        ('Capabilities', {
            'fields': (
                ('accepts_electronic_prescriptions', 'supports_controlled_substances'),
                ('is_preferred_network', 'is_active')
            )
        }),
        ('Operational Details', {
            'fields': (
                'hours_of_operation',
                'insurance_networks'
            )
        }),
        ('Audit Information', {
            'fields': (
                'verified_date',
                ('created_at', 'updated_at')
            )
        })
    )


@admin.register(PrescriptionRefill)
class PrescriptionRefillAdmin(admin.ModelAdmin):
    """Admin interface for prescription refills."""
    
    list_display = [
        'prescription_display', 'refill_number', 'status',
        'requested_by_name', 'request_date', 'approved_date'
    ]
    list_filter = ['status', 'request_method', 'request_date']
    search_fields = [
        'prescription__prescription_id',
        'requested_by__username', 'requested_by__email'
    ]
    autocomplete_fields = ['prescription', 'requested_by', 'approved_by', 'pharmacy']
    readonly_fields = ['request_date', 'created_at', 'updated_at']
    
    def prescription_display(self, obj):
        return str(obj.prescription.prescription_id)[:8] + "..."
    prescription_display.short_description = 'Prescription'
    
    def requested_by_name(self, obj):
        return obj.requested_by.get_full_name()
    requested_by_name.short_description = 'Requested By'


@admin.register(DrugInteraction)
class DrugInteractionAdmin(admin.ModelAdmin):
    """Admin interface for drug interactions."""
    
    list_display = [
        'get_drug1_name', 'get_drug2_name', 'interaction_level',
        'interaction_type', 'evidence_level', 'is_active'
    ]
    list_filter = [
        'interaction_level', 'evidence_level', 'interaction_type', 'is_active'
    ]
    search_fields = [
        'medication_1__generic_name', 'medication_1__brand_name',
        'medication_2__generic_name', 'medication_2__brand_name'
    ]
    autocomplete_fields = ['medication_1', 'medication_2']
    readonly_fields = ['last_reviewed', 'created_at', 'updated_at']
    
    def get_drug1_name(self, obj):
        return str(obj.medication_1)
    get_drug1_name.short_description = 'Drug 1'
    
    def get_drug2_name(self, obj):
        return str(obj.medication_2)
    get_drug2_name.short_description = 'Drug 2'


@admin.register(PrescriptionAuditLog)
class PrescriptionAuditLogAdmin(admin.ModelAdmin):
    """Admin interface for prescription audit logs."""
    
    list_display = [
        'prescription_display', 'user_name', 'action', 'timestamp', 'ip_address'
    ]
    list_filter = ['action', 'timestamp']
    search_fields = [
        'prescription__prescription_id',
        'user__username', 'user__email',
        'ip_address'
    ]
    readonly_fields = [
        'prescription', 'user', 'action', 'field_changes',
        'previous_values', 'new_values', 'ip_address', 'user_agent',
        'session_key', 'timestamp'
    ]
    
    def prescription_display(self, obj):
        return str(obj.prescription.prescription_id)[:8] + "..."
    prescription_display.short_description = 'Prescription'
    
    def user_name(self, obj):
        return obj.user.get_full_name() if obj.user else 'System'
    user_name.short_description = 'User'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
