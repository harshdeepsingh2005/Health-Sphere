"""
HealthSphere AI - Interoperability Admin Interface
=================================================

Django admin configuration for healthcare interoperability models.
Provides comprehensive management interface for FHIR/HL7 integration.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.forms import TextInput, Textarea
import json

from .models import (
    ExternalSystem, FHIRResource, HL7Message, 
    DataMapping, IntegrationTransaction, ConsentManagement
)


@admin.register(ExternalSystem)
class ExternalSystemAdmin(admin.ModelAdmin):
    """Admin interface for external healthcare systems."""
    
    list_display = [
        'name', 'system_type', 'fhir_version', 'connection_status_display',
        'supports_hl7', 'is_active', 'last_successful_connection'
    ]
    list_filter = [
        'system_type', 'fhir_version', 'connection_status', 
        'supports_hl7', 'is_active', 'created_at'
    ]
    search_fields = ['name', 'description', 'base_url']
    readonly_fields = ['created_at', 'updated_at', 'last_successful_connection']
    
    fieldsets = [
        ('System Information', {
            'fields': ['name', 'system_type', 'description', 'is_active']
        }),
        ('FHIR Configuration', {
            'fields': ['base_url', 'fhir_version', 'supported_resources', 'supported_operations']
        }),
        ('Authentication', {
            'fields': ['auth_type', 'auth_config'],
            'classes': ['collapse']
        }),
        ('HL7 Configuration', {
            'fields': ['supports_hl7', 'hl7_version', 'hl7_endpoint'],
            'classes': ['collapse']
        }),
        ('Connection Status', {
            'fields': ['connection_status', 'last_successful_connection'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['created_by', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    formfield_overrides = {
        models.JSONField: {'widget': Textarea(attrs={'rows': 4, 'cols': 80})},
    }
    
    actions = ['test_connection', 'activate_systems', 'deactivate_systems']
    
    def connection_status_display(self, obj):
        """Display connection status with color coding."""
        colors = {
            'connected': 'green',
            'disconnected': 'orange',
            'error': 'red',
            'unknown': 'gray'
        }
        icons = {
            'connected': '✅',
            'disconnected': '⚠️',
            'error': '❌',
            'unknown': '❓'
        }
        
        color = colors.get(obj.connection_status, 'gray')
        icon = icons.get(obj.connection_status, '❓')
        
        return format_html(
            '{} <span style="color: {};">{}</span>',
            icon, color, obj.get_connection_status_display()
        )
    connection_status_display.short_description = 'Connection Status'
    connection_status_display.admin_order_field = 'connection_status'
    
    def test_connection(self, request, queryset):
        """Test connection for selected systems."""
        tested = 0
        successful = 0
        
        for system in queryset:
            if system.test_connection():
                successful += 1
            tested += 1
        
        self.message_user(
            request,
            f"Tested {tested} systems. {successful} successful connections."
        )
    test_connection.short_description = "Test connection to selected systems"
    
    def activate_systems(self, request, queryset):
        """Activate selected systems."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Activated {updated} systems.")
    activate_systems.short_description = "Activate selected systems"
    
    def deactivate_systems(self, request, queryset):
        """Deactivate selected systems."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {updated} systems.")
    deactivate_systems.short_description = "Deactivate selected systems"


@admin.register(FHIRResource)
class FHIRResourceAdmin(admin.ModelAdmin):
    """Admin interface for FHIR resources."""
    
    list_display = [
        'resource_display', 'resource_type', 'source_system', 
        'validation_status', 'related_patient_display', 'last_updated'
    ]
    list_filter = [
        'resource_type', 'is_valid', 'source_system',
        'last_updated', 'created_at'
    ]
    search_fields = ['resource_id', 'resource_type']
    readonly_fields = ['resource_id', 'created_at', 'last_updated']
    date_hierarchy = 'last_updated'
    
    fieldsets = [
        ('Resource Information', {
            'fields': ['resource_id', 'resource_type', 'version_id', 'source_system']
        }),
        ('FHIR Resource Data', {
            'fields': ['resource_data'],
            'classes': ['collapse']
        }),
        ('Validation', {
            'fields': ['is_valid', 'validation_errors'],
            'classes': ['collapse']
        }),
        ('Relationships', {
            'fields': ['related_patient'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['created_at', 'last_updated'],
            'classes': ['collapse']
        })
    ]
    
    actions = ['validate_resources', 'export_fhir_bundle']
    
    def resource_display(self, obj):
        """Display resource with type and ID."""
        return f"{obj.resource_type}/{obj.resource_id}"
    resource_display.short_description = 'Resource'
    resource_display.admin_order_field = 'resource_type'
    
    def validation_status(self, obj):
        """Display validation status."""
        if obj.is_valid:
            return format_html('<span style="color: green;">✅ Valid</span>')
        else:
            error_count = len(obj.validation_errors)
            return format_html(
                '<span style="color: red;">❌ Invalid ({})</span>',
                f"{error_count} errors"
            )
    validation_status.short_description = 'Validation'
    validation_status.admin_order_field = 'is_valid'
    
    def related_patient_display(self, obj):
        """Display related patient with link."""
        if obj.related_patient:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:users_user_change', args=[obj.related_patient.pk]),
                obj.related_patient.get_full_name()
            )
        return '-'
    related_patient_display.short_description = 'Patient'
    related_patient_display.admin_order_field = 'related_patient__last_name'
    
    def validate_resources(self, request, queryset):
        """Validate selected FHIR resources."""
        validated = 0
        valid = 0
        
        for resource in queryset:
            if resource.validate_fhir_resource():
                valid += 1
            validated += 1
        
        self.message_user(
            request,
            f"Validated {validated} resources. {valid} are valid."
        )
    validate_resources.short_description = "Validate selected resources"
    
    def export_fhir_bundle(self, request, queryset):
        """Export selected resources as FHIR Bundle."""
        # Implementation would create a FHIR Bundle
        self.message_user(
            request,
            f"Export functionality would create FHIR Bundle with {queryset.count()} resources."
        )
    export_fhir_bundle.short_description = "Export as FHIR Bundle"


@admin.register(HL7Message)
class HL7MessageAdmin(admin.ModelAdmin):
    """Admin interface for HL7 messages."""
    
    list_display = [
        'message_display', 'direction', 'status_display', 
        'source_system', 'related_patient_display', 'received_at'
    ]
    list_filter = [
        'message_type', 'direction', 'status', 
        'source_system', 'received_at'
    ]
    search_fields = ['control_id', 'message_type', 'trigger_event']
    readonly_fields = ['message_id', 'received_at', 'processed_at', 'created_at']
    date_hierarchy = 'received_at'
    
    fieldsets = [
        ('Message Information', {
            'fields': [
                'message_id', 'control_id', 'message_type', 
                'trigger_event', 'direction', 'status'
            ]
        }),
        ('Message Content', {
            'fields': ['raw_message', 'parsed_message'],
            'classes': ['collapse']
        }),
        ('Processing', {
            'fields': [
                'processing_errors', 'processing_log'
            ],
            'classes': ['collapse']
        }),
        ('System Integration', {
            'fields': ['source_system', 'destination_system'],
            'classes': ['collapse']
        }),
        ('Relationships', {
            'fields': ['related_patient'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['received_at', 'processed_at', 'created_at'],
            'classes': ['collapse']
        })
    ]
    
    actions = ['reprocess_messages', 'generate_ack_messages']
    
    def message_display(self, obj):
        """Display message type and control ID."""
        return f"{obj.message_type}^{obj.trigger_event} - {obj.control_id}"
    message_display.short_description = 'Message'
    message_display.admin_order_field = 'message_type'
    
    def status_display(self, obj):
        """Display processing status with color coding."""
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'processed': 'green',
            'error': 'red',
            'rejected': 'darkred'
        }
        icons = {
            'pending': '⏳',
            'processing': '⚙️',
            'processed': '✅',
            'error': '❌',
            'rejected': '🚫'
        }
        
        color = colors.get(obj.status, 'gray')
        icon = icons.get(obj.status, '❓')
        
        return format_html(
            '{} <span style="color: {};">{}</span>',
            icon, color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def related_patient_display(self, obj):
        """Display related patient with link."""
        if obj.related_patient:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:users_user_change', args=[obj.related_patient.pk]),
                obj.related_patient.get_full_name()
            )
        return '-'
    related_patient_display.short_description = 'Patient'
    
    def reprocess_messages(self, request, queryset):
        """Reprocess selected messages."""
        # Implementation would reprocess messages
        updated = queryset.filter(status='error').update(status='pending')
        self.message_user(request, f"Marked {updated} messages for reprocessing.")
    reprocess_messages.short_description = "Reprocess selected messages"
    
    def generate_ack_messages(self, request, queryset):
        """Generate ACK messages for selected inbound messages."""
        inbound_count = queryset.filter(direction='inbound').count()
        self.message_user(
            request,
            f"Would generate ACK messages for {inbound_count} inbound messages."
        )
    generate_ack_messages.short_description = "Generate ACK messages"


@admin.register(DataMapping)
class DataMappingAdmin(admin.ModelAdmin):
    """Admin interface for data mappings."""
    
    list_display = [
        'name', 'mapping_type', 'source_system', 'target_system',
        'is_active', 'test_status', 'last_tested'
    ]
    list_filter = [
        'mapping_type', 'is_active', 'source_system', 
        'target_system', 'last_tested'
    ]
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'last_tested']
    
    fieldsets = [
        ('Mapping Information', {
            'fields': ['name', 'mapping_type', 'description', 'is_active']
        }),
        ('Source Configuration', {
            'fields': ['source_system', 'source_format', 'source_schema']
        }),
        ('Target Configuration', {
            'fields': ['target_system', 'target_format', 'target_schema']
        }),
        ('Mapping Rules', {
            'fields': ['mapping_rules', 'transformation_code'],
            'classes': ['collapse']
        }),
        ('Testing', {
            'fields': ['last_tested', 'test_results'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['created_by', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    actions = ['test_mappings', 'activate_mappings', 'deactivate_mappings']
    
    def test_status(self, obj):
        """Display test status."""
        if not obj.last_tested:
            return format_html('<span style="color: gray;">Not tested</span>')
        
        test_results = obj.test_results or {}
        status = test_results.get('status', 'unknown')
        
        if status == 'success':
            return format_html('<span style="color: green;">✅ Passed</span>')
        elif status == 'error':
            return format_html('<span style="color: red;">❌ Failed</span>')
        else:
            return format_html('<span style="color: orange;">❓ Unknown</span>')
    test_status.short_description = 'Test Status'
    
    def test_mappings(self, request, queryset):
        """Test selected data mappings."""
        tested = 0
        passed = 0
        
        for mapping in queryset:
            success, _ = mapping.test_mapping({'test': 'data'})
            if success:
                passed += 1
            tested += 1
        
        self.message_user(
            request,
            f"Tested {tested} mappings. {passed} passed."
        )
    test_mappings.short_description = "Test selected mappings"
    
    def activate_mappings(self, request, queryset):
        """Activate selected mappings."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Activated {updated} mappings.")
    activate_mappings.short_description = "Activate selected mappings"
    
    def deactivate_mappings(self, request, queryset):
        """Deactivate selected mappings."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {updated} mappings.")
    deactivate_mappings.short_description = "Deactivate selected mappings"


@admin.register(IntegrationTransaction)
class IntegrationTransactionAdmin(admin.ModelAdmin):
    """Admin interface for integration transactions."""
    
    list_display = [
        'transaction_display', 'external_system', 'status_display',
        'duration_display', 'related_patient_display', 'started_at'
    ]
    list_filter = [
        'transaction_type', 'status', 'external_system',
        'status_code', 'started_at'
    ]
    search_fields = ['transaction_id', 'endpoint_url']
    readonly_fields = [
        'transaction_id', 'started_at', 'completed_at', 
        'duration_ms', 'status_code'
    ]
    date_hierarchy = 'started_at'
    
    fieldsets = [
        ('Transaction Information', {
            'fields': [
                'transaction_id', 'transaction_type', 'external_system',
                'endpoint_url', 'http_method', 'status', 'status_code'
            ]
        }),
        ('Request/Response Data', {
            'fields': [
                'request_data', 'response_data',
                'request_headers', 'response_headers'
            ],
            'classes': ['collapse']
        }),
        ('Error Information', {
            'fields': ['error_message'],
            'classes': ['collapse']
        }),
        ('Performance', {
            'fields': ['started_at', 'completed_at', 'duration_ms'],
            'classes': ['collapse']
        }),
        ('Relationships', {
            'fields': [
                'related_patient', 'related_fhir_resource', 
                'related_hl7_message'
            ],
            'classes': ['collapse']
        }),
        ('Audit Information', {
            'fields': ['initiated_by', 'ip_address', 'user_agent'],
            'classes': ['collapse']
        })
    ]
    
    def transaction_display(self, obj):
        """Display transaction type and ID."""
        return f"{obj.get_transaction_type_display()} ({str(obj.transaction_id)[:8]}...)"
    transaction_display.short_description = 'Transaction'
    transaction_display.admin_order_field = 'transaction_type'
    
    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'initiated': 'blue',
            'in_progress': 'orange',
            'completed': 'green',
            'failed': 'red',
            'cancelled': 'gray',
            'timeout': 'darkred'
        }
        icons = {
            'initiated': '🔄',
            'in_progress': '⚙️',
            'completed': '✅',
            'failed': '❌',
            'cancelled': '🚫',
            'timeout': '⏰'
        }
        
        color = colors.get(obj.status, 'gray')
        icon = icons.get(obj.status, '❓')
        
        return format_html(
            '{} <span style="color: {};">{}</span>',
            icon, color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def duration_display(self, obj):
        """Display transaction duration."""
        return obj.get_duration_display()
    duration_display.short_description = 'Duration'
    duration_display.admin_order_field = 'duration_ms'
    
    def related_patient_display(self, obj):
        """Display related patient with link."""
        if obj.related_patient:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:users_user_change', args=[obj.related_patient.pk]),
                obj.related_patient.get_full_name()
            )
        return '-'
    related_patient_display.short_description = 'Patient'


@admin.register(ConsentManagement)
class ConsentManagementAdmin(admin.ModelAdmin):
    """Admin interface for consent management."""
    
    list_display = [
        'patient_display', 'consent_type', 'status_display',
        'validity_display', 'granted_at', 'expires_at'
    ]
    list_filter = [
        'consent_type', 'status', 'granted_at', 
        'expires_at', 'created_at'
    ]
    search_fields = ['patient__first_name', 'patient__last_name', 'purpose']
    readonly_fields = [
        'created_at', 'updated_at', 'granted_at', 
        'withdrawn_at'
    ]
    date_hierarchy = 'granted_at'
    
    fieldsets = [
        ('Patient & Consent', {
            'fields': ['patient', 'consent_type', 'status', 'purpose']
        }),
        ('Scope & Authorization', {
            'fields': ['scope', 'authorized_systems', 'authorized_purposes'],
            'classes': ['collapse']
        }),
        ('Consent Lifecycle', {
            'fields': [
                'granted_at', 'expires_at', 'withdrawn_at', 
                'withdrawal_reason'
            ],
            'classes': ['collapse']
        }),
        ('Legal & Compliance', {
            'fields': ['legal_basis', 'consent_document', 'signature_data'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['created_by', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    filter_horizontal = ['authorized_systems']
    actions = ['withdraw_consents', 'extend_consents']
    
    def patient_display(self, obj):
        """Display patient with link."""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:users_user_change', args=[obj.patient.pk]),
            obj.patient.get_full_name()
        )
    patient_display.short_description = 'Patient'
    patient_display.admin_order_field = 'patient__last_name'
    
    def status_display(self, obj):
        """Display consent status with color coding."""
        colors = {
            'granted': 'green',
            'denied': 'red',
            'withdrawn': 'orange',
            'expired': 'gray',
            'pending': 'blue'
        }
        icons = {
            'granted': '✅',
            'denied': '❌',
            'withdrawn': '⚠️',
            'expired': '🕒',
            'pending': '⏳'
        }
        
        color = colors.get(obj.status, 'gray')
        icon = icons.get(obj.status, '❓')
        
        return format_html(
            '{} <span style="color: {};">{}</span>',
            icon, color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def validity_display(self, obj):
        """Display consent validity."""
        if obj.is_valid():
            return format_html('<span style="color: green;">✅ Valid</span>')
        else:
            return format_html('<span style="color: red;">❌ Invalid</span>')
    validity_display.short_description = 'Validity'
    
    def withdraw_consents(self, request, queryset):
        """Withdraw selected consents."""
        withdrawn = 0
        for consent in queryset.filter(status='granted'):
            consent.withdraw_consent(reason="Admin withdrawal", withdrawn_by=request.user)
            withdrawn += 1
        
        self.message_user(request, f"Withdrew {withdrawn} consents.")
    withdraw_consents.short_description = "Withdraw selected consents"
    
    def extend_consents(self, request, queryset):
        """Extend selected consents by 1 year."""
        from datetime import timedelta
        from django.utils import timezone
        
        extended = 0
        new_expiry = timezone.now() + timedelta(days=365)
        
        for consent in queryset.filter(status='granted'):
            consent.extend_consent(new_expiry)
            extended += 1
        
        self.message_user(request, f"Extended {extended} consents by 1 year.")
    extend_consents.short_description = "Extend selected consents by 1 year"


# Customize admin site headers
admin.site.site_header = "HealthSphere AI - Interoperability Administration"
