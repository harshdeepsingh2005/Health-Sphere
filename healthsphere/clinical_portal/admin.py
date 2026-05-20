"""
HealthSphere AI - Clinical Portal Admin Configuration
====================================================

Registers Clinical Portal models with Django admin.
"""

from django.contrib import admin
from .models import MedicalRecord, TreatmentPlan, VitalRecord


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    """Admin configuration for MedicalRecord model."""
    
    list_display = (
        'title', 'patient', 'record_type', 'severity',
        'created_by', 'record_date', 'ai_risk_score'
    )
    list_filter = ('record_type', 'severity', 'is_confidential', 'record_date')
    search_fields = (
        'title', 'description', 'diagnosis_code',
        'patient__username', 'patient__first_name', 'patient__last_name'
    )
    ordering = ('-record_date',)
    date_hierarchy = 'record_date'
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'created_by')
        }),
        ('Record Details', {
            'fields': ('record_type', 'title', 'description', 'severity')
        }),
        ('Medical Coding', {
            'fields': ('diagnosis_code', 'attachments', 'is_confidential')
        }),
        ('AI Insights', {
            'fields': ('ai_risk_score', 'ai_recommendations'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('record_date',),
        }),
    )


@admin.register(TreatmentPlan)
class TreatmentPlanAdmin(admin.ModelAdmin):
    """Admin configuration for TreatmentPlan model."""
    
    list_display = (
        'title', 'patient', 'status', 'created_by',
        'start_date', 'end_date', 'next_review_date'
    )
    list_filter = ('status', 'start_date', 'created_by')
    search_fields = (
        'title', 'diagnosis', 'medications',
        'patient__username', 'patient__first_name', 'patient__last_name'
    )
    ordering = ('-created_at',)
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'created_by', 'medical_record')
        }),
        ('Plan Details', {
            'fields': ('title', 'description', 'diagnosis', 'status')
        }),
        ('Treatment', {
            'fields': ('medications', 'procedures', 'lifestyle_recommendations')
        }),
        ('Follow-up', {
            'fields': ('follow_up_instructions', 'start_date', 'end_date', 'next_review_date')
        }),
    )


@admin.register(VitalRecord)
class VitalRecordAdmin(admin.ModelAdmin):
    """Admin configuration for VitalRecord model."""
    
    list_display = (
        'patient', 'recorded_at', 'recorded_by',
        'temperature', 'blood_pressure', 'heart_rate', 'oxygen_saturation'
    )
    list_filter = ('recorded_at', 'recorded_by')
    search_fields = (
        'patient__username', 'patient__first_name', 'patient__last_name',
        'notes'
    )
    ordering = ('-recorded_at',)
    date_hierarchy = 'recorded_at'
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'recorded_by', 'recorded_at')
        }),
        ('Vital Signs', {
            'fields': (
                'temperature',
                ('blood_pressure_systolic', 'blood_pressure_diastolic'),
                'heart_rate', 'respiratory_rate', 'oxygen_saturation'
            )
        }),
        ('Body Measurements', {
            'fields': ('weight', 'height', 'blood_glucose', 'pain_level')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
