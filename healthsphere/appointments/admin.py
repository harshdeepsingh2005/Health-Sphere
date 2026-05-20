"""
HealthSphere AI - Appointment Management Admin
=============================================

Django admin configuration for appointment management models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import AppointmentType, DoctorSchedule, Appointment, AppointmentReminder


@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    """Admin interface for AppointmentType model."""
    
    list_display = ['name', 'duration_minutes', 'color_preview', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'description', 'is_active']
        }),
        ('Scheduling', {
            'fields': ['duration_minutes', 'color_code']
        }),
    ]
    
    def color_preview(self, obj):
        """Show color preview in admin list."""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.color_code
        )
    color_preview.short_description = 'Color'


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    """Admin interface for DoctorSchedule model."""
    
    list_display = [
        'doctor_name', 'day_name', 'start_time', 'end_time', 
        'break_times', 'max_appointments', 'is_active'
    ]
    list_filter = ['day_of_week', 'is_active', 'created_at']
    search_fields = ['doctor__first_name', 'doctor__last_name', 'doctor__username']
    ordering = ['doctor', 'day_of_week', 'start_time']
    
    fieldsets = [
        ('Doctor & Day', {
            'fields': ['doctor', 'day_of_week']
        }),
        ('Working Hours', {
            'fields': ['start_time', 'end_time']
        }),
        ('Break Times', {
            'fields': ['break_start_time', 'break_end_time'],
            'description': 'Optional break time during working hours'
        }),
        ('Settings', {
            'fields': ['max_appointments', 'is_active']
        }),
    ]
    
    def doctor_name(self, obj):
        """Display doctor name."""
        return obj.doctor.get_full_name()
    doctor_name.short_description = 'Doctor'
    
    def day_name(self, obj):
        """Display day name."""
        return dict(obj.WEEKDAY_CHOICES)[obj.day_of_week]
    day_name.short_description = 'Day'
    
    def break_times(self, obj):
        """Display break times if set."""
        if obj.break_start_time and obj.break_end_time:
            return f"{obj.break_start_time} - {obj.break_end_time}"
        return "No break"
    break_times.short_description = 'Break'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin interface for Appointment model."""
    
    list_display = [
        'id', 'patient_name', 'doctor_name', 'appointment_type',
        'scheduled_date', 'scheduled_time', 'status_colored',
        'is_telemedicine', 'created_at'
    ]
    list_filter = [
        'status', 'appointment_type', 'is_telemedicine',
        'scheduled_date', 'created_at'
    ]
    search_fields = [
        'patient__first_name', 'patient__last_name', 'patient__username',
        'doctor__first_name', 'doctor__last_name', 'doctor__username',
        'reason'
    ]
    ordering = ['-scheduled_date', '-scheduled_time']
    date_hierarchy = 'scheduled_date'
    
    fieldsets = [
        ('Appointment Details', {
            'fields': ['patient', 'doctor', 'appointment_type']
        }),
        ('Scheduling', {
            'fields': ['scheduled_date', 'scheduled_time', 'duration_minutes']
        }),
        ('Information', {
            'fields': ['reason', 'notes', 'doctor_notes']
        }),
        ('Status & Settings', {
            'fields': ['status', 'is_telemedicine', 'video_room_id', 'send_reminder']
        }),
        ('Cancellation Info', {
            'fields': ['cancelled_by', 'cancellation_reason', 'cancelled_at'],
            'classes': ['collapse']
        }),
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'cancelled_at']
    
    actions = ['confirm_appointments', 'cancel_appointments', 'send_reminders']
    
    def patient_name(self, obj):
        """Display patient name with link."""
        url = reverse('admin:users_user_change', args=[obj.patient.pk])
        return format_html('<a href="{}">{}</a>', url, obj.patient.get_full_name())
    patient_name.short_description = 'Patient'
    
    def doctor_name(self, obj):
        """Display doctor name with link."""
        url = reverse('admin:users_user_change', args=[obj.doctor.pk])
        return format_html('<a href="{}">{}</a>', url, obj.doctor.get_full_name())
    doctor_name.short_description = 'Doctor'
    
    def status_colored(self, obj):
        """Display status with color coding."""
        colors = {
            'requested': '#ffc107',
            'confirmed': '#28a745',
            'in_progress': '#17a2b8',
            'completed': '#6c757d',
            'cancelled': '#dc3545',
            'no_show': '#fd7e14',
            'rescheduled': '#6f42c1'
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'
    
    def confirm_appointments(self, request, queryset):
        """Bulk action to confirm appointments."""
        count = 0
        for appointment in queryset.filter(status='requested'):
            try:
                appointment.confirm()
                count += 1
            except ValidationError:
                pass
        self.message_user(request, f"Confirmed {count} appointments.")
    confirm_appointments.short_description = "Confirm selected appointments"
    
    def cancel_appointments(self, request, queryset):
        """Bulk action to cancel appointments."""
        count = 0
        for appointment in queryset:
            if appointment.can_be_cancelled:
                try:
                    appointment.cancel(request.user, "Cancelled via admin")
                    count += 1
                except ValidationError:
                    pass
        self.message_user(request, f"Cancelled {count} appointments.")
    cancel_appointments.short_description = "Cancel selected appointments"


@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    """Admin interface for AppointmentReminder model."""
    
    list_display = [
        'appointment_link', 'reminder_type', 'scheduled_time',
        'is_sent', 'sent_at', 'delivery_status'
    ]
    list_filter = ['reminder_type', 'is_sent', 'delivery_status', 'scheduled_time']
    search_fields = [
        'appointment__patient__first_name',
        'appointment__patient__last_name',
        'appointment__doctor__first_name',
        'appointment__doctor__last_name'
    ]
    ordering = ['scheduled_time']
    date_hierarchy = 'scheduled_time'
    
    readonly_fields = ['sent_at', 'created_at', 'updated_at']
    
    def appointment_link(self, obj):
        """Display appointment with link."""
        url = reverse('admin:appointments_appointment_change', args=[obj.appointment.pk])
        return format_html('<a href="{}">{}</a>', url, str(obj.appointment))
    appointment_link.short_description = 'Appointment'