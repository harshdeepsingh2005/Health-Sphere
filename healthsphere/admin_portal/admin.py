"""
HealthSphere AI - Admin Portal Admin Configuration
=================================================

Registers Admin Portal models with Django admin.
"""

from django.contrib import admin
from .models import HospitalResource, AdmissionRecord, StaffSchedule


@admin.register(HospitalResource)
class HospitalResourceAdmin(admin.ModelAdmin):
    """Admin configuration for HospitalResource model."""
    
    list_display = (
        'name', 'resource_type', 'status', 'location',
        'quantity', 'next_maintenance'
    )
    list_filter = ('resource_type', 'status', 'location')
    search_fields = ('name', 'description', 'location')
    ordering = ('resource_type', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'resource_type', 'description')
        }),
        ('Location & Status', {
            'fields': ('location', 'status', 'quantity')
        }),
        ('Maintenance', {
            'fields': ('last_maintenance', 'next_maintenance')
        }),
    )


@admin.register(AdmissionRecord)
class AdmissionRecordAdmin(admin.ModelAdmin):
    """Admin configuration for AdmissionRecord model."""
    
    list_display = (
        'id', 'patient', 'admission_type', 'status',
        'admission_date', 'ward', 'attending_doctor'
    )
    list_filter = ('admission_type', 'status', 'ward')
    search_fields = (
        'patient__username', 'patient__first_name',
        'patient__last_name', 'diagnosis'
    )
    ordering = ('-admission_date',)
    date_hierarchy = 'admission_date'
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'attending_doctor')
        }),
        ('Admission Details', {
            'fields': ('admission_type', 'status', 'admission_date', 'discharge_date')
        }),
        ('Location', {
            'fields': ('ward', 'room_number', 'bed_number')
        }),
        ('Medical Information', {
            'fields': ('diagnosis', 'notes')
        }),
    )


@admin.register(StaffSchedule)
class StaffScheduleAdmin(admin.ModelAdmin):
    """Admin configuration for StaffSchedule model."""
    
    list_display = (
        'staff_member', 'date', 'shift', 'department',
        'status', 'start_time', 'end_time'
    )
    list_filter = ('shift', 'status', 'department', 'date')
    search_fields = (
        'staff_member__username', 'staff_member__first_name',
        'staff_member__last_name', 'department'
    )
    ordering = ('date', 'shift')
    date_hierarchy = 'date'
