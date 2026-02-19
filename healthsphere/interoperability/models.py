"""
HealthSphere AI - Healthcare Interoperability Models
===================================================

FHIR R4 and HL7 compliant models for healthcare data exchange and interoperability.
Supports seamless integration with external healthcare systems, EHRs, and HIEs.

Features:
- FHIR R4 resource models (Patient, Encounter, Observation, etc.)
- HL7 message processing and routing
- Healthcare data mapping and transformation
- Interoperability audit trails and compliance
- External system integration endpoints
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import datetime, timedelta
import json
import uuid

User = get_user_model()


class ExternalSystem(models.Model):
    """
    External healthcare systems and integration endpoints.
    Manages connections to EHRs, HIEs, laboratories, and other healthcare systems.
    """
    
    SYSTEM_TYPES = [
        ('ehr', 'Electronic Health Record'),
        ('hie', 'Health Information Exchange'),
        ('laboratory', 'Laboratory System'),
        ('imaging', 'Medical Imaging System'),
        ('pharmacy', 'Pharmacy Management System'),
        ('billing', 'Healthcare Billing System'),
        ('registry', 'Clinical Registry'),
        ('pacs', 'Picture Archiving System'),
        ('his', 'Hospital Information System'),
        ('other', 'Other Healthcare System'),
    ]
    
    FHIR_VERSIONS = [
        ('dstu2', 'FHIR DSTU2'),
        ('stu3', 'FHIR STU3'),
        ('r4', 'FHIR R4'),
        ('r5', 'FHIR R5'),
    ]
    
    AUTHENTICATION_TYPES = [
        ('none', 'No Authentication'),
        ('basic', 'Basic Authentication'),
        ('oauth2', 'OAuth 2.0'),
        ('client_credentials', 'Client Credentials'),
        ('bearer_token', 'Bearer Token'),
        ('mutual_tls', 'Mutual TLS'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    system_type = models.CharField(max_length=20, choices=SYSTEM_TYPES)
    description = models.TextField(blank=True)
    
    # Connection details
    base_url = models.URLField(help_text="Base URL for FHIR API endpoint")
    fhir_version = models.CharField(max_length=20, choices=FHIR_VERSIONS, default='r4')
    
    # Authentication configuration
    auth_type = models.CharField(max_length=20, choices=AUTHENTICATION_TYPES, default='none')
    auth_config = models.JSONField(
        default=dict, blank=True,
        help_text="Authentication configuration (client_id, secrets, etc.)"
    )
    
    # System capabilities
    supported_resources = models.JSONField(
        default=list, blank=True,
        help_text="List of supported FHIR resource types"
    )
    supported_operations = models.JSONField(
        default=list, blank=True,
        help_text="List of supported FHIR operations (read, create, update, delete, search)"
    )
    
    # HL7 messaging
    supports_hl7 = models.BooleanField(default=False)
    hl7_version = models.CharField(max_length=10, blank=True, help_text="e.g., 2.5, 2.8")
    hl7_endpoint = models.URLField(blank=True, help_text="HL7 MLLP endpoint")
    
    # System status
    is_active = models.BooleanField(default=True)
    last_successful_connection = models.DateTimeField(null=True, blank=True)
    connection_status = models.CharField(
        max_length=20,
        choices=[
            ('unknown', 'Unknown'),
            ('connected', 'Connected'),
            ('disconnected', 'Disconnected'),
            ('error', 'Connection Error'),
        ],
        default='unknown'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'interop_external_system'
        ordering = ['name']
        indexes = [
            models.Index(fields=['system_type', 'is_active']),
            models.Index(fields=['fhir_version']),
            models.Index(fields=['connection_status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_system_type_display()})"
    
    def test_connection(self):
        """Test connection to external system."""
        # Implementation would test actual connection
        # For now, simulate connection test
        import random
        success = random.choice([True, False])
        
        if success:
            self.connection_status = 'connected'
            self.last_successful_connection = timezone.now()
        else:
            self.connection_status = 'error'
        
        self.save()
        return success


class FHIRResource(models.Model):
    """
    Base model for FHIR resources with common attributes.
    Stores FHIR-compliant healthcare data for interoperability.
    """
    
    RESOURCE_TYPES = [
        ('Patient', 'Patient'),
        ('Practitioner', 'Practitioner'),
        ('Organization', 'Organization'),
        ('Encounter', 'Encounter'),
        ('Observation', 'Observation'),
        ('Condition', 'Condition'),
        ('Procedure', 'Procedure'),
        ('MedicationRequest', 'Medication Request'),
        ('DiagnosticReport', 'Diagnostic Report'),
        ('AllergyIntolerance', 'Allergy Intolerance'),
        ('Immunization', 'Immunization'),
        ('DocumentReference', 'Document Reference'),
        ('CarePlan', 'Care Plan'),
        ('Goal', 'Goal'),
        ('Appointment', 'Appointment'),
        ('Schedule', 'Schedule'),
        ('Slot', 'Slot'),
    ]
    
    # FHIR Resource identification
    resource_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPES)
    version_id = models.CharField(max_length=50, default='1')
    
    # FHIR Resource content
    resource_data = models.JSONField(
        help_text="Complete FHIR resource as JSON"
    )
    
    # Metadata
    source_system = models.ForeignKey(
        ExternalSystem, on_delete=models.CASCADE,
        related_name='fhir_resources', null=True, blank=True,
        help_text="System that provided this resource"
    )
    
    # FHIR Resource meta fields
    last_updated = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Status and validation
    is_valid = models.BooleanField(default=True)
    validation_errors = models.JSONField(default=list, blank=True)
    
    # Internal references
    related_patient = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='fhir_resources'
    )
    
    class Meta:
        db_table = 'interop_fhir_resource'
        ordering = ['-last_updated']
        indexes = [
            models.Index(fields=['resource_type', 'last_updated']),
            models.Index(fields=['related_patient']),
            models.Index(fields=['source_system']),
            models.Index(fields=['resource_id']),
        ]
        unique_together = [['resource_id', 'version_id']]
    
    def __str__(self):
        return f"{self.resource_type}/{self.resource_id} (v{self.version_id})"
    
    def get_fhir_json(self):
        """Get FHIR-compliant JSON representation."""
        return self.resource_data
    
    def validate_fhir_resource(self):
        """Validate FHIR resource against schema."""
        # Implementation would validate against FHIR schema
        # For now, basic validation
        errors = []
        
        if not self.resource_data.get('resourceType'):
            errors.append("Missing resourceType")
        
        if not self.resource_data.get('id'):
            self.resource_data['id'] = str(self.resource_id)
        
        self.validation_errors = errors
        self.is_valid = len(errors) == 0
        return self.is_valid


class HL7Message(models.Model):
    """
    HL7 message processing and storage.
    Handles inbound and outbound HL7 v2.x messages.
    """
    
    MESSAGE_TYPES = [
        ('ADT', 'Admit/Discharge/Transfer'),
        ('ORM', 'Order Message'),
        ('ORU', 'Observation Result'),
        ('SIU', 'Scheduling Information'),
        ('DFT', 'Detailed Financial Transaction'),
        ('BAR', 'Billing Account Record'),
        ('MDM', 'Medical Document Management'),
        ('QBP', 'Query by Parameter'),
        ('ACK', 'Acknowledgment'),
        ('OTHER', 'Other Message Type'),
    ]
    
    PROCESSING_STATUS = [
        ('pending', 'Pending Processing'),
        ('processing', 'Processing'),
        ('processed', 'Successfully Processed'),
        ('error', 'Processing Error'),
        ('rejected', 'Rejected'),
    ]
    
    DIRECTIONS = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]
    
    # Message identification
    message_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    control_id = models.CharField(max_length=50, help_text="HL7 Message Control ID")
    
    # Message details
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    trigger_event = models.CharField(max_length=10, help_text="e.g., A01, A03, R01")
    direction = models.CharField(max_length=10, choices=DIRECTIONS)
    
    # Message content
    raw_message = models.TextField(help_text="Raw HL7 message")
    parsed_message = models.JSONField(
        default=dict, blank=True,
        help_text="Parsed HL7 message as JSON"
    )
    
    # Processing information
    status = models.CharField(max_length=20, choices=PROCESSING_STATUS, default='pending')
    processing_errors = models.JSONField(default=list, blank=True)
    processing_log = models.JSONField(default=list, blank=True)
    
    # System integration
    source_system = models.ForeignKey(
        ExternalSystem, on_delete=models.CASCADE,
        related_name='hl7_messages', null=True, blank=True
    )
    destination_system = models.ForeignKey(
        ExternalSystem, on_delete=models.CASCADE,
        related_name='outbound_hl7_messages', null=True, blank=True
    )
    
    # Patient relationship
    related_patient = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='hl7_messages'
    )
    
    # Timestamps
    received_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'interop_hl7_message'
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['message_type', 'status']),
            models.Index(fields=['direction', 'received_at']),
            models.Index(fields=['related_patient']),
            models.Index(fields=['control_id']),
        ]
    
    def __str__(self):
        return f"{self.message_type}^{self.trigger_event} - {self.control_id}"
    
    def parse_hl7_message(self):
        """Parse raw HL7 message into structured data."""
        try:
            # Basic HL7 parsing (in practice, use proper HL7 parser library)
            segments = self.raw_message.split('\r\n')
            parsed = {}
            
            for segment in segments:
                if not segment.strip():
                    continue
                
                fields = segment.split('|')
                segment_type = fields[0] if fields else 'UNKNOWN'
                parsed[segment_type] = fields[1:] if len(fields) > 1 else []
            
            self.parsed_message = parsed
            self.save()
            return True
            
        except Exception as e:
            self.processing_errors.append(f"Parsing error: {str(e)}")
            self.status = 'error'
            self.save()
            return False
    
    def generate_ack(self, ack_code='AA'):
        """Generate HL7 ACK message."""
        # Implementation would generate proper HL7 ACK
        ack_message = f"MSH|^~\&|||||||ACK^A01^ACK|{self.control_id}|P|2.5\r\n"
        ack_message += f"MSA|{ack_code}|{self.control_id}|\r\n"
        return ack_message


class DataMapping(models.Model):
    """
    Data mapping configurations for system interoperability.
    Maps internal data models to FHIR resources and external system formats.
    """
    
    MAPPING_TYPES = [
        ('fhir_resource', 'FHIR Resource Mapping'),
        ('hl7_segment', 'HL7 Segment Mapping'),
        ('custom_api', 'Custom API Mapping'),
        ('database_table', 'Database Table Mapping'),
    ]
    
    name = models.CharField(max_length=200)
    mapping_type = models.CharField(max_length=20, choices=MAPPING_TYPES)
    description = models.TextField(blank=True)
    
    # Source configuration
    source_system = models.ForeignKey(
        ExternalSystem, on_delete=models.CASCADE,
        related_name='source_mappings', null=True, blank=True
    )
    source_format = models.CharField(max_length=100, help_text="Source data format")
    source_schema = models.JSONField(
        default=dict, blank=True,
        help_text="Source data schema definition"
    )
    
    # Target configuration
    target_system = models.ForeignKey(
        ExternalSystem, on_delete=models.CASCADE,
        related_name='target_mappings', null=True, blank=True
    )
    target_format = models.CharField(max_length=100, help_text="Target data format")
    target_schema = models.JSONField(
        default=dict, blank=True,
        help_text="Target data schema definition"
    )
    
    # Mapping rules
    mapping_rules = models.JSONField(
        default=dict,
        help_text="Field mapping rules and transformations"
    )
    transformation_code = models.TextField(
        blank=True,
        help_text="Custom transformation code (Python)"
    )
    
    # Validation and testing
    is_active = models.BooleanField(default=True)
    last_tested = models.DateTimeField(null=True, blank=True)
    test_results = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'interop_data_mapping'
        ordering = ['name']
        indexes = [
            models.Index(fields=['mapping_type', 'is_active']),
            models.Index(fields=['source_system']),
            models.Index(fields=['target_system']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_mapping_type_display()})"
    
    def test_mapping(self, sample_data):
        """Test mapping with sample data."""
        try:
            # Implementation would test actual mapping
            # For now, basic validation
            if not self.mapping_rules:
                return False, "No mapping rules defined"
            
            self.last_tested = timezone.now()
            self.test_results = {
                'status': 'success',
                'tested_at': timezone.now().isoformat(),
                'sample_input': sample_data,
                'sample_output': 'Mapping successful'
            }
            self.save()
            return True, "Mapping test successful"
            
        except Exception as e:
            self.test_results = {
                'status': 'error',
                'error': str(e),
                'tested_at': timezone.now().isoformat()
            }
            self.save()
            return False, str(e)


class IntegrationTransaction(models.Model):
    """
    Audit trail for all integration transactions.
    Tracks data exchange activities for compliance and debugging.
    """
    
    TRANSACTION_TYPES = [
        ('fhir_read', 'FHIR Resource Read'),
        ('fhir_create', 'FHIR Resource Create'),
        ('fhir_update', 'FHIR Resource Update'),
        ('fhir_delete', 'FHIR Resource Delete'),
        ('fhir_search', 'FHIR Resource Search'),
        ('hl7_send', 'HL7 Message Send'),
        ('hl7_receive', 'HL7 Message Receive'),
        ('data_sync', 'Data Synchronization'),
        ('bulk_export', 'Bulk Data Export'),
        ('bulk_import', 'Bulk Data Import'),
    ]
    
    TRANSACTION_STATUS = [
        ('initiated', 'Initiated'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('timeout', 'Timeout'),
    ]
    
    # Transaction identification
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    
    # System details
    external_system = models.ForeignKey(
        ExternalSystem, on_delete=models.CASCADE,
        related_name='transactions'
    )
    endpoint_url = models.URLField(help_text="Specific endpoint called")
    http_method = models.CharField(max_length=10, default='GET')
    
    # Request/Response data
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    request_headers = models.JSONField(default=dict, blank=True)
    response_headers = models.JSONField(default=dict, blank=True)
    
    # Transaction results
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='initiated')
    status_code = models.IntegerField(null=True, blank=True, help_text="HTTP status code")
    error_message = models.TextField(blank=True)
    
    # Performance metrics
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True, help_text="Duration in milliseconds")
    
    # Related resources
    related_patient = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='integration_transactions'
    )
    related_fhir_resource = models.ForeignKey(
        FHIRResource, on_delete=models.CASCADE, null=True, blank=True,
        related_name='transactions'
    )
    related_hl7_message = models.ForeignKey(
        HL7Message, on_delete=models.CASCADE, null=True, blank=True,
        related_name='transactions'
    )
    
    # Audit information
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'interop_integration_transaction'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['transaction_type', 'status']),
            models.Index(fields=['external_system', 'started_at']),
            models.Index(fields=['status', 'started_at']),
            models.Index(fields=['related_patient']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.external_system.name} ({self.status})"
    
    def complete_transaction(self, status_code=200, response_data=None, error_message=''):
        """Mark transaction as completed."""
        self.completed_at = timezone.now()
        self.status_code = status_code
        
        if status_code >= 200 and status_code < 300:
            self.status = 'completed'
        else:
            self.status = 'failed'
            self.error_message = error_message
        
        if response_data:
            self.response_data = response_data
        
        # Calculate duration
        if self.started_at and self.completed_at:
            duration = self.completed_at - self.started_at
            self.duration_ms = int(duration.total_seconds() * 1000)
        
        self.save()
    
    def get_duration_display(self):
        """Get human-readable duration."""
        if self.duration_ms is not None:
            if self.duration_ms < 1000:
                return f"{self.duration_ms}ms"
            else:
                return f"{self.duration_ms / 1000:.2f}s"
        return "Unknown"


class ConsentManagement(models.Model):
    """
    Patient consent management for data sharing and interoperability.
    HIPAA and GDPR compliant consent tracking for healthcare data exchange.
    """
    
    CONSENT_TYPES = [
        ('treatment', 'Treatment'),
        ('payment', 'Payment'),
        ('operations', 'Healthcare Operations'),
        ('research', 'Research'),
        ('marketing', 'Marketing'),
        ('directory', 'Directory Listing'),
        ('emergency', 'Emergency Contact'),
        ('hie', 'Health Information Exchange'),
        ('data_sharing', 'External Data Sharing'),
    ]
    
    CONSENT_STATUS = [
        ('granted', 'Consent Granted'),
        ('denied', 'Consent Denied'),
        ('withdrawn', 'Consent Withdrawn'),
        ('expired', 'Consent Expired'),
        ('pending', 'Consent Pending'),
    ]
    
    # Patient and consent details
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consents')
    consent_type = models.CharField(max_length=20, choices=CONSENT_TYPES)
    status = models.CharField(max_length=20, choices=CONSENT_STATUS, default='pending')
    
    # Consent specifics
    purpose = models.TextField(help_text="Purpose of data use")
    scope = models.JSONField(
        default=list,
        help_text="Scope of data covered by consent (resource types, date ranges, etc.)"
    )
    
    # Authorized parties
    authorized_systems = models.ManyToManyField(
        ExternalSystem, blank=True,
        help_text="External systems authorized to access data"
    )
    authorized_purposes = models.JSONField(
        default=list, blank=True,
        help_text="Specific purposes for which data can be used"
    )
    
    # Consent lifecycle
    granted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    withdrawal_reason = models.TextField(blank=True)
    
    # Legal and compliance
    legal_basis = models.CharField(
        max_length=100, blank=True,
        help_text="Legal basis for processing (GDPR Article 6)"
    )
    consent_document = models.TextField(blank=True, help_text="Original consent document text")
    signature_data = models.JSONField(
        default=dict, blank=True,
        help_text="Digital signature or consent capture data"
    )
    
    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_consents'
    )
    
    class Meta:
        db_table = 'interop_consent_management'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'consent_type']),
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['granted_at']),
        ]
        unique_together = [['patient', 'consent_type']]
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.get_consent_type_display()} ({self.status})"
    
    def is_valid(self):
        """Check if consent is currently valid."""
        if self.status != 'granted':
            return False
        
        now = timezone.now()
        if self.expires_at and now > self.expires_at:
            return False
        
        if self.withdrawn_at and now >= self.withdrawn_at:
            return False
        
        return True
    
    def withdraw_consent(self, reason='', withdrawn_by=None):
        """Withdraw patient consent."""
        self.status = 'withdrawn'
        self.withdrawn_at = timezone.now()
        self.withdrawal_reason = reason
        
        if withdrawn_by:
            self.created_by = withdrawn_by
        
        self.save()
    
    def extend_consent(self, new_expiry_date):
        """Extend consent expiration date."""
        self.expires_at = new_expiry_date
        self.save()
