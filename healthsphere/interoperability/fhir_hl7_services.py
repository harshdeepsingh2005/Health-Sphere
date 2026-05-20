"""
HealthSphere AI - FHIR/HL7 Integration Services
==============================================

Healthcare interoperability services for FHIR R4 and HL7 v2.x messaging.
Provides seamless integration with external healthcare systems and EHRs.

Features:
- FHIR R4 resource CRUD operations
- HL7 v2.x message processing and routing
- Healthcare data transformation and mapping
- Consent management and privacy controls
- Integration monitoring and audit trails
"""

import json
import uuid
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from typing import Dict, List, Optional, Tuple, Any
import logging

from .models import (
    ExternalSystem, FHIRResource, HL7Message,
    DataMapping, IntegrationTransaction, ConsentManagement
)

logger = logging.getLogger(__name__)
User = get_user_model()


class FHIRClient:
    """
    FHIR R4 client for interacting with external FHIR servers.
    Provides standardized FHIR operations with authentication and error handling.
    """
    
    def __init__(self, external_system: ExternalSystem):
        self.system = external_system
        self.base_url = external_system.base_url.rstrip('/')
        self.session = requests.Session()
        self._configure_authentication()
    
    def _configure_authentication(self):
        """Configure session authentication based on system settings."""
        auth_config = self.system.auth_config
        
        if self.system.auth_type == 'basic':
            username = auth_config.get('username')
            password = auth_config.get('password')
            if username and password:
                self.session.auth = (username, password)
        
        elif self.system.auth_type == 'bearer_token':
            token = auth_config.get('token')
            if token:
                self.session.headers.update({'Authorization': f'Bearer {token}'})
        
        # Set common headers
        self.session.headers.update({
            'Accept': 'application/fhir+json',
            'Content-Type': 'application/fhir+json',
            'User-Agent': 'HealthSphere-AI/1.0'
        })
    
    def read_resource(self, resource_type: str, resource_id: str, 
                     user: Optional[User] = None) -> Tuple[bool, Dict]:
        """
        Read a FHIR resource by ID.
        
        Args:
            resource_type: FHIR resource type (e.g., 'Patient', 'Observation')
            resource_id: Resource ID
            user: User making the request
        
        Returns:
            Tuple of (success, resource_data or error_info)
        """
        transaction = None
        
        try:
            # Create transaction record
            transaction = IntegrationTransaction.objects.create(
                transaction_type='fhir_read',
                external_system=self.system,
                endpoint_url=f"{self.base_url}/{resource_type}/{resource_id}",
                http_method='GET',
                initiated_by=user
            )
            
            # Make FHIR request
            url = f"{self.base_url}/{resource_type}/{resource_id}"
            response = self.session.get(url)
            
            # Process response
            if response.status_code == 200:
                resource_data = response.json()
                
                # Store FHIR resource
                fhir_resource = FHIRResource.objects.create(
                    resource_type=resource_type,
                    resource_data=resource_data,
                    source_system=self.system,
                    related_patient=self._extract_patient_reference(resource_data, user)
                )
                fhir_resource.validate_fhir_resource()
                
                transaction.complete_transaction(
                    status_code=response.status_code,
                    response_data=resource_data
                )
                
                logger.info(f"Successfully read {resource_type}/{resource_id} from {self.system.name}")
                return True, resource_data
            
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'error': response.text}
                transaction.complete_transaction(
                    status_code=response.status_code,
                    response_data=error_data,
                    error_message=f"FHIR read failed: {response.status_code}"
                )
                
                logger.error(f"Failed to read {resource_type}/{resource_id}: HTTP {response.status_code}")
                return False, error_data
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Exception reading FHIR resource: {error_msg}")
            
            if transaction:
                transaction.complete_transaction(
                    status_code=500,
                    error_message=error_msg
                )
            
            return False, {'error': error_msg}
    
    def create_resource(self, resource_data: Dict, user: Optional[User] = None) -> Tuple[bool, Dict]:
        """
        Create a new FHIR resource.
        
        Args:
            resource_data: FHIR resource data
            user: User making the request
        
        Returns:
            Tuple of (success, created_resource or error_info)
        """
        transaction = None
        resource_type = resource_data.get('resourceType')
        
        try:
            if not resource_type:
                return False, {'error': 'Missing resourceType in resource data'}
            
            # Check consent if patient-related
            patient = self._extract_patient_reference(resource_data, user)
            if patient and not self._check_consent(patient, 'data_sharing'):
                return False, {'error': 'Patient consent not granted for data sharing'}
            
            # Create transaction record
            transaction = IntegrationTransaction.objects.create(
                transaction_type='fhir_create',
                external_system=self.system,
                endpoint_url=f"{self.base_url}/{resource_type}",
                http_method='POST',
                request_data=resource_data,
                initiated_by=user,
                related_patient=patient
            )
            
            # Make FHIR request
            url = f"{self.base_url}/{resource_type}"
            response = self.session.post(url, json=resource_data)
            
            # Process response
            if response.status_code in [201, 200]:
                created_resource = response.json()
                
                # Store FHIR resource
                fhir_resource = FHIRResource.objects.create(
                    resource_type=resource_type,
                    resource_data=created_resource,
                    source_system=self.system,
                    related_patient=patient
                )
                fhir_resource.validate_fhir_resource()
                
                transaction.complete_transaction(
                    status_code=response.status_code,
                    response_data=created_resource,
                    related_fhir_resource=fhir_resource
                )
                
                logger.info(f"Successfully created {resource_type} on {self.system.name}")
                return True, created_resource
            
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'error': response.text}
                transaction.complete_transaction(
                    status_code=response.status_code,
                    response_data=error_data,
                    error_message=f"FHIR create failed: {response.status_code}"
                )
                
                logger.error(f"Failed to create {resource_type}: HTTP {response.status_code}")
                return False, error_data
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Exception creating FHIR resource: {error_msg}")
            
            if transaction:
                transaction.complete_transaction(
                    status_code=500,
                    error_message=error_msg
                )
            
            return False, {'error': error_msg}
    
    def search_resources(self, resource_type: str, search_params: Dict, 
                        user: Optional[User] = None) -> Tuple[bool, Dict]:
        """
        Search for FHIR resources.
        
        Args:
            resource_type: FHIR resource type
            search_params: Search parameters
            user: User making the request
        
        Returns:
            Tuple of (success, search_bundle or error_info)
        """
        transaction = None
        
        try:
            # Create transaction record
            transaction = IntegrationTransaction.objects.create(
                transaction_type='fhir_search',
                external_system=self.system,
                endpoint_url=f"{self.base_url}/{resource_type}",
                http_method='GET',
                request_data=search_params,
                initiated_by=user
            )
            
            # Make FHIR search request
            url = f"{self.base_url}/{resource_type}"
            response = self.session.get(url, params=search_params)
            
            # Process response
            if response.status_code == 200:
                search_results = response.json()
                
                # Store found resources
                if search_results.get('resourceType') == 'Bundle':
                    entries = search_results.get('entry', [])
                    for entry in entries[:10]:  # Limit to first 10 results
                        resource_data = entry.get('resource', {})
                        if resource_data:
                            fhir_resource = FHIRResource.objects.create(
                                resource_type=resource_data.get('resourceType', resource_type),
                                resource_data=resource_data,
                                source_system=self.system,
                                related_patient=self._extract_patient_reference(resource_data, user)
                            )
                            fhir_resource.validate_fhir_resource()
                
                transaction.complete_transaction(
                    status_code=response.status_code,
                    response_data=search_results
                )
                
                logger.info(f"Successfully searched {resource_type} on {self.system.name}")
                return True, search_results
            
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'error': response.text}
                transaction.complete_transaction(
                    status_code=response.status_code,
                    response_data=error_data,
                    error_message=f"FHIR search failed: {response.status_code}"
                )
                
                logger.error(f"Failed to search {resource_type}: HTTP {response.status_code}")
                return False, error_data
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Exception searching FHIR resources: {error_msg}")
            
            if transaction:
                transaction.complete_transaction(
                    status_code=500,
                    error_message=error_msg
                )
            
            return False, {'error': error_msg}
    
    def _extract_patient_reference(self, resource_data: Dict, user: Optional[User] = None) -> Optional[User]:
        """Extract patient reference from FHIR resource."""
        # Simple implementation - in practice would need more sophisticated patient matching
        if resource_data.get('resourceType') == 'Patient':
            # Try to match patient by identifier or name
            identifiers = resource_data.get('identifier', [])
            for identifier in identifiers:
                system = identifier.get('system', '')
                value = identifier.get('value', '')
                if 'mrn' in system.lower() or 'patient-id' in system.lower():
                    # Try to find user by custom identifier
                    # This is a simplified example
                    pass
        
        # Return the requesting user as fallback
        return user
    
    def _check_consent(self, patient: User, consent_type: str) -> bool:
        """Check if patient has granted consent for the operation."""
        try:
            consent = ConsentManagement.objects.get(
                patient=patient,
                consent_type=consent_type
            )
            return consent.is_valid()
        except ConsentManagement.DoesNotExist:
            return False


class HL7MessageProcessor:
    """
    HL7 v2.x message processor for healthcare data exchange.
    Handles parsing, routing, and processing of HL7 messages.
    """
    
    def __init__(self):
        self.message_handlers = {
            'ADT': self._handle_adt_message,
            'ORM': self._handle_orm_message,
            'ORU': self._handle_oru_message,
            'SIU': self._handle_siu_message,
        }
    
    def process_inbound_message(self, raw_message: str, source_system: ExternalSystem) -> Tuple[bool, str]:
        """
        Process inbound HL7 message.
        
        Args:
            raw_message: Raw HL7 message
            source_system: Source system that sent the message
        
        Returns:
            Tuple of (success, acknowledgment_message)
        """
        try:
            # Parse message header to get message type and control ID
            message_info = self._parse_message_header(raw_message)
            
            # Create HL7Message record
            hl7_message = HL7Message.objects.create(
                message_type=message_info.get('message_type', 'OTHER'),
                trigger_event=message_info.get('trigger_event', ''),
                direction='inbound',
                control_id=message_info.get('control_id', str(uuid.uuid4())),
                raw_message=raw_message,
                source_system=source_system,
                status='processing'
            )
            
            # Parse the message
            if hl7_message.parse_hl7_message():
                # Process based on message type
                handler = self.message_handlers.get(hl7_message.message_type)
                if handler:
                    success = handler(hl7_message)
                    if success:
                        hl7_message.status = 'processed'
                        hl7_message.processed_at = timezone.now()
                        ack_code = 'AA'  # Application Accept
                    else:
                        hl7_message.status = 'error'
                        ack_code = 'AE'  # Application Error
                else:
                    hl7_message.status = 'error'
                    hl7_message.processing_errors.append(f"No handler for message type: {hl7_message.message_type}")
                    ack_code = 'AR'  # Application Reject
            else:
                hl7_message.status = 'error'
                ack_code = 'AR'  # Application Reject
            
            hl7_message.save()
            
            # Generate ACK message
            ack_message = hl7_message.generate_ack(ack_code)
            
            logger.info(f"Processed HL7 message {hl7_message.control_id}: {hl7_message.status}")
            return hl7_message.status == 'processed', ack_message
        
        except Exception as e:
            logger.error(f"Error processing HL7 message: {str(e)}")
            return False, f"MSH|^~\&|||||||ACK|{uuid.uuid4()}|P|2.5\r\nMSA|AR|ERROR|{str(e)}\r\n"
    
    def send_outbound_message(self, message_data: Dict, destination_system: ExternalSystem,
                             user: Optional[User] = None) -> Tuple[bool, str]:
        """
        Send outbound HL7 message.
        
        Args:
            message_data: Message data to send
            destination_system: Destination system
            user: User sending the message
        
        Returns:
            Tuple of (success, response_message)
        """
        try:
            # Generate HL7 message
            raw_message = self._generate_hl7_message(message_data)
            
            # Create HL7Message record
            hl7_message = HL7Message.objects.create(
                message_type=message_data.get('message_type', 'OTHER'),
                trigger_event=message_data.get('trigger_event', ''),
                direction='outbound',
                control_id=str(uuid.uuid4()),
                raw_message=raw_message,
                destination_system=destination_system,
                status='processing'
            )
            
            # Create integration transaction
            transaction = IntegrationTransaction.objects.create(
                transaction_type='hl7_send',
                external_system=destination_system,
                endpoint_url=destination_system.hl7_endpoint or 'N/A',
                http_method='POST',
                request_data=message_data,
                initiated_by=user,
                related_hl7_message=hl7_message
            )
            
            # Send message (simulation - in practice would use MLLP protocol)
            success = self._send_hl7_message(raw_message, destination_system)
            
            if success:
                hl7_message.status = 'processed'
                hl7_message.processed_at = timezone.now()
                transaction.complete_transaction(status_code=200, response_data={'status': 'sent'})
                return True, "Message sent successfully"
            else:
                hl7_message.status = 'error'
                transaction.complete_transaction(status_code=500, error_message="Failed to send message")
                return False, "Failed to send message"
            
        except Exception as e:
            logger.error(f"Error sending HL7 message: {str(e)}")
            return False, str(e)
    
    def _parse_message_header(self, raw_message: str) -> Dict:
        """Parse HL7 message header (MSH segment)."""
        lines = raw_message.split('\r\n')
        msh_line = next((line for line in lines if line.startswith('MSH')), '')
        
        if not msh_line:
            return {}
        
        fields = msh_line.split('|')
        
        return {
            'message_type': fields[8].split('^')[0] if len(fields) > 8 else 'OTHER',
            'trigger_event': fields[8].split('^')[1] if len(fields) > 8 and '^' in fields[8] else '',
            'control_id': fields[9] if len(fields) > 9 else str(uuid.uuid4()),
            'processing_id': fields[10] if len(fields) > 10 else 'P',
            'version': fields[11] if len(fields) > 11 else '2.5'
        }
    
    def _handle_adt_message(self, hl7_message: HL7Message) -> bool:
        """Handle ADT (Admit/Discharge/Transfer) messages."""
        try:
            # Extract patient information from PID segment
            parsed = hl7_message.parsed_message
            pid_data = parsed.get('PID', [])
            
            if pid_data:
                patient_id = pid_data[2] if len(pid_data) > 2 else 'Unknown'
                patient_name = pid_data[5] if len(pid_data) > 5 else 'Unknown'
                
                hl7_message.processing_log.append(f"Processed ADT for patient: {patient_name} ({patient_id})")
                
                # Here you would typically:
                # 1. Match or create patient record
                # 2. Update patient demographics
                # 3. Create/update encounter record
                # 4. Trigger workflows based on trigger event
                
                return True
            
            return False
            
        except Exception as e:
            hl7_message.processing_errors.append(f"ADT processing error: {str(e)}")
            return False
    
    def _handle_orm_message(self, hl7_message: HL7Message) -> bool:
        """Handle ORM (Order) messages."""
        try:
            # Process order information
            parsed = hl7_message.parsed_message
            orc_data = parsed.get('ORC', [])
            
            if orc_data:
                order_control = orc_data[0] if len(orc_data) > 0 else 'Unknown'
                hl7_message.processing_log.append(f"Processed ORM with order control: {order_control}")
                
                # Here you would typically:
                # 1. Create or update order records
                # 2. Trigger ordering workflows
                # 3. Update order status
                
                return True
            
            return False
            
        except Exception as e:
            hl7_message.processing_errors.append(f"ORM processing error: {str(e)}")
            return False
    
    def _handle_oru_message(self, hl7_message: HL7Message) -> bool:
        """Handle ORU (Observation Result) messages."""
        try:
            # Process observation results
            parsed = hl7_message.parsed_message
            obr_data = parsed.get('OBR', [])
            
            if obr_data:
                report_id = obr_data[2] if len(obr_data) > 2 else 'Unknown'
                hl7_message.processing_log.append(f"Processed ORU for report: {report_id}")
                
                # Here you would typically:
                # 1. Create diagnostic report
                # 2. Store observation values
                # 3. Alert clinicians if abnormal
                
                return True
            
            return False
            
        except Exception as e:
            hl7_message.processing_errors.append(f"ORU processing error: {str(e)}")
            return False
    
    def _handle_siu_message(self, hl7_message: HL7Message) -> bool:
        """Handle SIU (Scheduling) messages."""
        try:
            # Process scheduling information
            parsed = hl7_message.parsed_message
            sch_data = parsed.get('SCH', [])
            
            if sch_data:
                appointment_id = sch_data[1] if len(sch_data) > 1 else 'Unknown'
                hl7_message.processing_log.append(f"Processed SIU for appointment: {appointment_id}")
                
                # Here you would typically:
                # 1. Create or update appointment
                # 2. Update schedules
                # 3. Send notifications
                
                return True
            
            return False
            
        except Exception as e:
            hl7_message.processing_errors.append(f"SIU processing error: {str(e)}")
            return False
    
    def _generate_hl7_message(self, message_data: Dict) -> str:
        """Generate HL7 message from data."""
        # Basic HL7 message generation (simplified)
        control_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        message_type = message_data.get('message_type', 'ADT')
        trigger_event = message_data.get('trigger_event', 'A01')
        
        msh = f"MSH|^~\&|||HealthSphere||{timestamp}||{message_type}^{trigger_event}^{message_type}_{trigger_event}|{control_id}|P|2.5"
        
        # Add additional segments based on message type
        segments = [msh]
        
        if message_type == 'ADT':
            # Add EVN and PID segments
            segments.append(f"EVN||{timestamp}")
            segments.append("PID|1||123456789||Doe^John^M||19800101|M|||123 Main St^^City^ST^12345")
        
        return '\r\n'.join(segments) + '\r\n'
    
    def _send_hl7_message(self, raw_message: str, destination_system: ExternalSystem) -> bool:
        """Send HL7 message via MLLP (simulation)."""
        # In practice, this would establish an MLLP connection and send the message
        # For simulation, we'll just return True
        logger.info(f"Simulating HL7 message send to {destination_system.name}")
        return True


class DataTransformationService:
    """
    Service for transforming data between different formats and systems.
    Handles mapping between internal models and external system formats.
    """
    
    def __init__(self):
        pass
    
    def transform_to_fhir_patient(self, user: User) -> Dict:
        """Transform internal User to FHIR Patient resource."""
        try:
            patient_resource = {
                "resourceType": "Patient",
                "id": str(user.id),
                "active": user.is_active,
                "name": [{
                    "use": "official",
                    "family": user.last_name,
                    "given": [user.first_name]
                }],
                "gender": getattr(user.profile, 'gender', 'unknown') if hasattr(user, 'profile') else 'unknown',
                "birthDate": getattr(user.profile, 'date_of_birth', None).strftime('%Y-%m-%d') if hasattr(user, 'profile') and user.profile.date_of_birth else None,
                "telecom": [
                    {
                        "system": "email",
                        "value": user.email,
                        "use": "home"
                    }
                ],
                "identifier": [{
                    "use": "usual",
                    "system": "http://healthsphere.ai/patient-id",
                    "value": str(user.id)
                }],
                "meta": {
                    "lastUpdated": timezone.now().isoformat(),
                    "profile": ["http://hl7.org/fhir/StructureDefinition/Patient"]
                }
            }
            
            # Add phone number if available
            if hasattr(user, 'profile') and user.profile.phone:
                patient_resource["telecom"].append({
                    "system": "phone",
                    "value": user.profile.phone,
                    "use": "home"
                })
            
            return patient_resource
            
        except Exception as e:
            logger.error(f"Error transforming user to FHIR Patient: {str(e)}")
            return {}
    
    def transform_from_fhir_patient(self, patient_resource: Dict) -> Dict:
        """Transform FHIR Patient resource to internal format."""
        try:
            internal_data = {
                'first_name': '',
                'last_name': '',
                'email': '',
                'profile': {}
            }
            
            # Extract name
            names = patient_resource.get('name', [])
            if names:
                name = names[0]
                internal_data['first_name'] = ' '.join(name.get('given', []))
                internal_data['last_name'] = name.get('family', '')
            
            # Extract email
            telecoms = patient_resource.get('telecom', [])
            for telecom in telecoms:
                if telecom.get('system') == 'email':
                    internal_data['email'] = telecom.get('value', '')
                    break
                elif telecom.get('system') == 'phone':
                    internal_data['profile']['phone'] = telecom.get('value', '')
            
            # Extract demographics
            internal_data['profile']['gender'] = patient_resource.get('gender', 'unknown')
            
            birth_date = patient_resource.get('birthDate')
            if birth_date:
                internal_data['profile']['date_of_birth'] = birth_date
            
            return internal_data
            
        except Exception as e:
            logger.error(f"Error transforming FHIR Patient to internal format: {str(e)}")
            return {}
    
    def apply_data_mapping(self, source_data: Dict, mapping: DataMapping) -> Dict:
        """Apply data mapping transformation."""
        try:
            if not mapping.mapping_rules:
                return source_data
            
            transformed_data = {}
            
            for source_field, target_config in mapping.mapping_rules.items():
                if isinstance(target_config, str):
                    # Simple field mapping
                    if source_field in source_data:
                        transformed_data[target_config] = source_data[source_field]
                
                elif isinstance(target_config, dict):
                    # Complex mapping with transformation
                    target_field = target_config.get('field')
                    transform_type = target_config.get('transform')
                    
                    if source_field in source_data and target_field:
                        source_value = source_data[source_field]
                        
                        if transform_type == 'uppercase':
                            transformed_data[target_field] = str(source_value).upper()
                        elif transform_type == 'lowercase':
                            transformed_data[target_field] = str(source_value).lower()
                        elif transform_type == 'date_format':
                            # Handle date transformation
                            try:
                                from datetime import datetime
                                dt = datetime.fromisoformat(str(source_value))
                                transformed_data[target_field] = dt.strftime(target_config.get('format', '%Y-%m-%d'))
                            except:
                                transformed_data[target_field] = source_value
                        else:
                            transformed_data[target_field] = source_value
            
            return transformed_data
            
        except Exception as e:
            logger.error(f"Error applying data mapping: {str(e)}")
            return source_data


def get_fhir_client(system_name: str) -> Optional[FHIRClient]:
    """Get FHIR client for external system."""
    try:
        system = ExternalSystem.objects.get(name=system_name, is_active=True)
        return FHIRClient(system)
    except ExternalSystem.DoesNotExist:
        logger.error(f"External system not found: {system_name}")
        return None


def get_hl7_processor() -> HL7MessageProcessor:
    """Get HL7 message processor instance."""
    return HL7MessageProcessor()


def get_data_transformer() -> DataTransformationService:
    """Get data transformation service instance."""
    return DataTransformationService()