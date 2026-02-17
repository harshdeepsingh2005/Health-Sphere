"""
HealthSphere AI - Patient Portal Admin Configuration
===================================================

Registers Patient Portal models with Django admin.
"""

from django.contrib import admin
from .models import PatientProfile, Appointment, HealthMetric


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    """Admin configuration for PatientProfile model."""
    
    list_display = (
        'user', 'primary_doctor', 'medical_record_number',
        'insurance_type', 'insurance_provider'
    )
    list_filter = ('insurance_type', 'communication_preference')
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name',
        'medical_record_number', 'insurance_provider'
    )
    ordering = ('user__last_name', 'user__first_name')
    
    fieldsets = (
        ('User Link', {
            'fields': ('user', 'primary_doctor', 'medical_record_number')
        }),
        ('Insurance', {
            'fields': ('insurance_type', 'insurance_provider', 'insurance_policy_number')
        }),
        ('Preferences', {
            'fields': ('preferred_pharmacy', 'communication_preference')
        }),
        ('Consent', {
            'fields': ('consent_to_research', 'consent_to_marketing')
        }),
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin configuration for Appointment model."""
    
    list_display = (
        'patient', 'doctor', 'appointment_type', 'appointment_date',
        'appointment_time', 'status', 'is_telemedicine'
    )
    list_filter = ('appointment_type', 'status', 'is_telemedicine', 'appointment_date')
    search_fields = (
        'patient__username', 'patient__first_name', 'patient__last_name',
        'doctor__first_name', 'doctor__last_name', 'reason'
    )
    ordering = ('-appointment_date', '-appointment_time')
    date_hierarchy = 'appointment_date'
    
    fieldsets = (
        ('Participants', {
            'fields': ('patient', 'doctor')
        }),
        ('Appointment Details', {
            'fields': (
                'appointment_type', 'appointment_date', 'appointment_time',
                'duration_minutes', 'status'
            )
        }),
        ('Additional Information', {
            'fields': ('reason', 'notes', 'location')
        }),
        ('Telemedicine', {
            'fields': ('is_telemedicine', 'meeting_link'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HealthMetric)
class HealthMetricAdmin(admin.ModelAdmin):
    """Admin configuration for HealthMetric model."""
    
    list_display = (
        'patient', 'metric_type', 'value', 'secondary_value',
        'source', 'recorded_at'
    )
    list_filter = ('metric_type', 'source', 'recorded_at')
    search_fields = (
        'patient__username', 'patient__first_name', 'patient__last_name',
        'notes'
    )
    ordering = ('-recorded_at',)
    date_hierarchy = 'recorded_at'
