"""
python manage.py seed_interoperability

Seeds realistic demo data for all interoperability models:
  ExternalSystem, FHIRResource, HL7Message, DataMapping,
  IntegrationTransaction, ConsentManagement
"""

import uuid
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from interoperability.models import (
    ExternalSystem, FHIRResource, HL7Message,
    DataMapping, IntegrationTransaction, ConsentManagement,
)
from users.models import User, Role


class Command(BaseCommand):
    help = "Seed interoperability demo data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Clear existing interoperability data before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing interoperability data...')
            IntegrationTransaction.objects.all().delete()
            ConsentManagement.objects.all().delete()
            HL7Message.objects.all().delete()
            FHIRResource.objects.all().delete()
            DataMapping.objects.all().delete()
            ExternalSystem.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared.'))

        # ── Helpers ────────────────────────────────────────────────────────
        now = timezone.now()
        patients = list(User.objects.filter(role__name=Role.PATIENT)[:10])
        if not patients:
            self.stdout.write(self.style.WARNING('No patients found – FHIR/HL7 patient links will be skipped.'))

        # ── 1. External Systems ────────────────────────────────────────────
        self.stdout.write('Creating external systems...')
        systems_data = [
            {
                'name': 'Epic EHR – City General Hospital',
                'system_type': 'ehr',
                'description': 'Primary EHR integration with City General Hospital using FHIR R4.',
                'base_url': 'https://fhir.citygeneral.example.com/api/FHIR/R4',
                'fhir_version': 'r4',
                'auth_type': 'oauth2',
                'auth_config': {'client_id': 'hs-epic-001', 'token_url': 'https://fhir.citygeneral.example.com/oauth/token'},
                'supported_resources': ['Patient', 'Encounter', 'Observation', 'Condition', 'MedicationRequest'],
                'supported_operations': ['read', 'create', 'update', 'search'],
                'supports_hl7': True,
                'hl7_version': '2.5',
                'connection_status': 'connected',
                'last_successful_connection': now - timedelta(minutes=12),
            },
            {
                'name': 'Cerner PowerChart – North Medical Center',
                'system_type': 'ehr',
                'description': 'Cerner EHR integration for lab results and discharge summaries.',
                'base_url': 'https://fhir.northmedical.example.com/R4',
                'fhir_version': 'r4',
                'auth_type': 'bearer_token',
                'auth_config': {'header': 'Authorization', 'prefix': 'Bearer'},
                'supported_resources': ['Patient', 'DiagnosticReport', 'Observation', 'Procedure'],
                'supported_operations': ['read', 'search'],
                'supports_hl7': True,
                'hl7_version': '2.8',
                'connection_status': 'connected',
                'last_successful_connection': now - timedelta(hours=2),
            },
            {
                'name': 'LabCorp – National Lab Network',
                'system_type': 'laboratory',
                'description': 'Laboratory results exchange via HL7 ORU messages and FHIR DiagnosticReport.',
                'base_url': 'https://api.labcorp-interop.example.com/fhir/r4',
                'fhir_version': 'r4',
                'auth_type': 'client_credentials',
                'auth_config': {'client_id': 'hs-labcorp-prod', 'scope': 'system/DiagnosticReport.read'},
                'supported_resources': ['DiagnosticReport', 'Observation', 'Specimen'],
                'supported_operations': ['read', 'search'],
                'supports_hl7': True,
                'hl7_version': '2.5',
                'connection_status': 'connected',
                'last_successful_connection': now - timedelta(minutes=45),
            },
            {
                'name': 'Philips PACS – Radiology System',
                'system_type': 'pacs',
                'description': 'DICOM / FHIR ImagingStudy integration for radiology reports.',
                'base_url': 'https://pacs.healthsphere.example.com/wado-rs',
                'fhir_version': 'r4',
                'auth_type': 'mutual_tls',
                'auth_config': {'cert_path': '/certs/pacs-client.pem'},
                'supported_resources': ['ImagingStudy', 'DiagnosticReport'],
                'supported_operations': ['read'],
                'supports_hl7': False,
                'connection_status': 'connected',
                'last_successful_connection': now - timedelta(hours=1),
            },
            {
                'name': 'State Health Information Exchange',
                'system_type': 'hie',
                'description': 'Statewide HIE for care coordination and patient matching.',
                'base_url': 'https://hie.statehealthdata.example.gov/fhir/r4',
                'fhir_version': 'r4',
                'auth_type': 'oauth2',
                'auth_config': {'client_id': 'hs-state-hie', 'scope': 'patient/*.read'},
                'supported_resources': ['Patient', 'Encounter', 'Condition', 'AllergyIntolerance', 'Immunization'],
                'supported_operations': ['read', 'search'],
                'supports_hl7': True,
                'hl7_version': '2.5',
                'connection_status': 'disconnected',
                'last_successful_connection': now - timedelta(days=3),
            },
            {
                'name': 'Walgreens Pharmacy Network',
                'system_type': 'pharmacy',
                'description': 'E-prescription transmission and refill status via NCPDP/FHIR.',
                'base_url': 'https://api.walgreens-fhir.example.com/r4',
                'fhir_version': 'r4',
                'auth_type': 'bearer_token',
                'auth_config': {'header': 'Authorization', 'prefix': 'Bearer'},
                'supported_resources': ['MedicationRequest', 'MedicationDispense'],
                'supported_operations': ['read', 'create', 'search'],
                'supports_hl7': False,
                'connection_status': 'connected',
                'last_successful_connection': now - timedelta(minutes=5),
            },
        ]

        systems = []
        for data in systems_data:
            sys_obj, created = ExternalSystem.objects.get_or_create(
                name=data['name'],
                defaults=data,
            )
            systems.append(sys_obj)
            if created:
                self.stdout.write(f"  + {sys_obj.name}")

        # ── 2. FHIR Resources ─────────────────────────────────────────────
        self.stdout.write('Creating FHIR resources...')
        fhir_samples = [
            ('Patient', {
                'resourceType': 'Patient',
                'id': str(uuid.uuid4()),
                'meta': {'versionId': '1', 'lastUpdated': now.isoformat()},
                'identifier': [{'system': 'http://healthsphere.example.com/patient', 'value': 'PT-001'}],
                'name': [{'use': 'official', 'family': 'Johnson', 'given': ['Sarah', 'Marie']}],
                'gender': 'female',
                'birthDate': '1979-03-15',
                'address': [{'line': ['123 Oak Street'], 'city': 'Springfield', 'state': 'IL', 'postalCode': '62701'}],
            }),
            ('Observation', {
                'resourceType': 'Observation',
                'id': str(uuid.uuid4()),
                'status': 'final',
                'category': [{'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/observation-category', 'code': 'vital-signs'}]}],
                'code': {'coding': [{'system': 'http://loinc.org', 'code': '8480-6', 'display': 'Systolic blood pressure'}]},
                'valueQuantity': {'value': 128, 'unit': 'mmHg', 'system': 'http://unitsofmeasure.org', 'code': 'mm[Hg]'},
                'effectiveDateTime': now.isoformat(),
            }),
            ('Condition', {
                'resourceType': 'Condition',
                'id': str(uuid.uuid4()),
                'clinicalStatus': {'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/condition-clinical', 'code': 'active'}]},
                'code': {'coding': [{'system': 'http://snomed.info/sct', 'code': '44054006', 'display': 'Diabetes mellitus type 2'}]},
                'onsetDateTime': '2020-06-01',
            }),
            ('MedicationRequest', {
                'resourceType': 'MedicationRequest',
                'id': str(uuid.uuid4()),
                'status': 'active',
                'intent': 'order',
                'medicationCodeableConcept': {'coding': [{'system': 'http://www.nlm.nih.gov/research/umls/rxnorm', 'code': '860975', 'display': 'Metformin 500mg'}]},
                'dosageInstruction': [{'text': 'Take 500mg twice daily with meals', 'timing': {'repeat': {'frequency': 2, 'period': 1, 'periodUnit': 'd'}}}],
            }),
            ('DiagnosticReport', {
                'resourceType': 'DiagnosticReport',
                'id': str(uuid.uuid4()),
                'status': 'final',
                'category': [{'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v2-0074', 'code': 'LAB'}]}],
                'code': {'coding': [{'system': 'http://loinc.org', 'code': '58410-2', 'display': 'CBC panel'}]},
                'effectiveDateTime': now.isoformat(),
                'conclusion': 'Complete blood count within normal limits.',
            }),
            ('Encounter', {
                'resourceType': 'Encounter',
                'id': str(uuid.uuid4()),
                'status': 'finished',
                'class': {'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode', 'code': 'IMP', 'display': 'inpatient encounter'},
                'period': {'start': (now - timedelta(days=5)).isoformat(), 'end': (now - timedelta(days=3)).isoformat()},
            }),
            ('AllergyIntolerance', {
                'resourceType': 'AllergyIntolerance',
                'id': str(uuid.uuid4()),
                'clinicalStatus': {'coding': [{'code': 'active'}]},
                'type': 'allergy',
                'category': ['medication'],
                'criticality': 'high',
                'code': {'coding': [{'system': 'http://www.nlm.nih.gov/research/umls/rxnorm', 'code': '7980', 'display': 'Penicillin'}]},
                'reaction': [{'substance': {'coding': [{'display': 'Penicillin'}]}, 'manifestation': [{'coding': [{'display': 'Anaphylaxis'}]}], 'severity': 'severe'}],
            }),
            ('Immunization', {
                'resourceType': 'Immunization',
                'id': str(uuid.uuid4()),
                'status': 'completed',
                'vaccineCode': {'coding': [{'system': 'http://hl7.org/fhir/sid/cvx', 'code': '208', 'display': 'COVID-19 mRNA vaccine'}]},
                'occurrenceDateTime': '2021-04-15',
                'primarySource': True,
            }),
        ]

        fhir_objs = []
        for resource_type, resource_data in fhir_samples:
            patient = random.choice(patients) if patients else None
            source = random.choice(systems[:3])
            fhir_obj = FHIRResource.objects.create(
                resource_type=resource_type,
                resource_data=resource_data,
                source_system=source,
                related_patient=patient,
                last_updated=now - timedelta(hours=random.randint(1, 72)),
                is_valid=True,
            )
            fhir_objs.append(fhir_obj)
            self.stdout.write(f"  + FHIR {resource_type}")

        # ── 3. HL7 Messages ───────────────────────────────────────────────
        self.stdout.write('Creating HL7 messages...')
        hl7_samples = [
            ('ADT', 'A01', 'inbound', 'processed',
             'MSH|^~\\&|EPIC|CITYGENERAL|HEALTHSPHERE||202601151030||ADT^A01^ADT_A01|MSG001|P|2.5\r\n'
             'EVN|A01|202601151030\r\n'
             'PID|1||PT-001^^^CITYGENERAL||Johnson^Sarah^Marie||19790315|F|||123 Oak St^^Springfield^IL^62701\r\n'
             'PV1|1|I|ICU^101^A^CITYGENERAL|E|||DR-042^Smith^John^^^Dr.||||||A0|'),
            ('ORU', 'R01', 'inbound', 'processed',
             'MSH|^~\\&|LABCORP|LAB|HEALTHSPHERE||202601151200||ORU^R01^ORU_R01|MSG002|P|2.5\r\n'
             'PID|1||PT-002^^^LABCORP||Chen^Michael||19620508|M\r\n'
             'OBR|1|LAB-001|LAB-001|58410-2^CBC^LN|||202601151130\r\n'
             'OBX|1|NM|718-7^Hemoglobin^LN||14.2|g/dL|13.5-17.5|N|||F'),
            ('ADT', 'A03', 'outbound', 'processed',
             'MSH|^~\\&|HEALTHSPHERE||STATEHI||202601151800||ADT^A03^ADT_A03|MSG003|P|2.5\r\n'
             'EVN|A03|202601151800\r\n'
             'PID|1||PT-001^^^HS||Johnson^Sarah^Marie||19790315|F\r\n'
             'PV1|1|I|WARD-A^201^B^HS|E|||DR-010^Patel^Rajesh^^^Dr.'),
            ('ORM', 'O01', 'outbound', 'processed',
             'MSH|^~\\&|HEALTHSPHERE||WALGREENS||202601160900||ORM^O01^ORM_O01|MSG004|P|2.5\r\n'
             'PID|1||PT-003^^^HS||Rodriguez^Emily||19980122|F\r\n'
             'ORC|NW|RX-2025-001|||||^^^202601161200^^R\r\n'
             'RXO|860975^Metformin 500mg^RXNORM|||500|mg|PO||BID'),
            ('SIU', 'S12', 'inbound', 'processed',
             'MSH|^~\\&|EPIC|CITYGENERAL|HEALTHSPHERE||202601160800||SIU^S12^SIU_S12|MSG005|P|2.5\r\n'
             'SCH|APT-001||20260116103000|20260116110000|60|^^^DR-042^Smith\r\n'
             'PID|1||PT-004^^^CITYGENERAL||Ahmed^Fatima||19851010|F'),
            ('ORU', 'R01', 'inbound', 'error',
             'MSH|^~\\&|LABCORP|LAB|HEALTHSPHERE||202601161500||ORU^R01^ORU_R01|MSG006|P|2.5\r\n'
             'PID|1||PT-UNKNOWN^^^LABCORP||Unknown^Patient\r\n'
             'OBR|1|LAB-002|LAB-002|2823-3^Potassium^LN|||202601161400\r\n'
             'OBX|1|NM|2823-3^Potassium^LN||6.8|mEq/L|3.5-5.0|HH|||F'),
        ]

        hl7_objs = []
        for msg_type, trigger, direction, status, raw in hl7_samples:
            patient = random.choice(patients) if patients else None
            src_sys = random.choice(systems[:4]) if direction == 'inbound' else None
            dst_sys = random.choice(systems[:4]) if direction == 'outbound' else None
            ctrl_id = f"MSG{random.randint(10000, 99999)}"
            hl7_obj = HL7Message.objects.create(
                control_id=ctrl_id,
                message_type=msg_type,
                trigger_event=trigger,
                direction=direction,
                raw_message=raw,
                parsed_message={},
                status=status,
                source_system=src_sys,
                destination_system=dst_sys,
                related_patient=patient,
                received_at=now - timedelta(hours=random.randint(1, 48)),
                processed_at=now - timedelta(hours=random.randint(0, 47)) if status != 'pending' else None,
                processing_errors=['Patient ID not found in local registry'] if status == 'error' else [],
                processing_log=[
                    {'step': 'received', 'time': (now - timedelta(hours=2)).isoformat()},
                    {'step': 'parsed', 'time': (now - timedelta(hours=2, minutes=-1)).isoformat()},
                ] if status == 'processed' else [],
            )
            hl7_objs.append(hl7_obj)
            self.stdout.write(f"  + HL7 {msg_type}^{trigger} ({direction})")

        # ── 4. Data Mappings ──────────────────────────────────────────────
        self.stdout.write('Creating data mappings...')
        epic_sys = systems[0]
        cerner_sys = systems[1]
        lab_sys = systems[2]

        mappings_data = [
            {
                'name': 'Epic Patient → FHIR R4 Patient',
                'mapping_type': 'fhir_resource',
                'description': 'Maps Epic EHR patient demographics to FHIR R4 Patient resource.',
                'source_system': epic_sys,
                'source_format': 'Epic FHIR R4',
                'target_system': None,
                'target_format': 'HealthSphere Internal',
                'mapping_rules': {
                    'name[0].family': 'patient.last_name',
                    'name[0].given[0]': 'patient.first_name',
                    'birthDate': 'patient.date_of_birth',
                    'gender': 'patient.gender',
                    'identifier[0].value': 'patient.mrn',
                },
                'is_active': True,
                'last_tested': now - timedelta(days=1),
                'test_results': {'status': 'success', 'records_mapped': 124, 'errors': 0},
            },
            {
                'name': 'LabCorp ORU → FHIR DiagnosticReport',
                'mapping_type': 'hl7_segment',
                'description': 'Maps HL7 ORU R01 lab results to FHIR R4 DiagnosticReport and Observation.',
                'source_system': lab_sys,
                'source_format': 'HL7 v2.5 ORU^R01',
                'target_system': None,
                'target_format': 'FHIR R4 DiagnosticReport',
                'mapping_rules': {
                    'OBR.4': 'DiagnosticReport.code',
                    'OBX.3': 'Observation.code',
                    'OBX.5': 'Observation.valueQuantity.value',
                    'OBX.6': 'Observation.valueQuantity.unit',
                    'OBX.7': 'Observation.referenceRange',
                    'OBX.8': 'Observation.interpretation',
                },
                'is_active': True,
                'last_tested': now - timedelta(hours=6),
                'test_results': {'status': 'success', 'records_mapped': 842, 'errors': 3},
            },
            {
                'name': 'Cerner Encounter → FHIR R4 Encounter',
                'mapping_type': 'fhir_resource',
                'description': 'Maps Cerner PowerChart encounter data to FHIR R4 Encounter.',
                'source_system': cerner_sys,
                'source_format': 'Cerner FHIR R4',
                'target_system': None,
                'target_format': 'HealthSphere Internal',
                'mapping_rules': {
                    'status': 'encounter.status',
                    'class.code': 'encounter.encounter_type',
                    'period.start': 'encounter.start_time',
                    'period.end': 'encounter.end_time',
                    'participant[0].individual': 'encounter.practitioner',
                },
                'is_active': True,
                'last_tested': now - timedelta(days=2),
                'test_results': {'status': 'success', 'records_mapped': 367, 'errors': 1},
            },
            {
                'name': 'HealthSphere → State HIE Patient Index',
                'mapping_type': 'custom_api',
                'description': 'Bidirectional patient matching with State HIE master patient index.',
                'source_system': None,
                'source_format': 'HealthSphere Internal',
                'target_system': systems[4],
                'target_format': 'FHIR R4 Patient (HIE)',
                'mapping_rules': {
                    'patient.first_name': 'name[0].given[0]',
                    'patient.last_name': 'name[0].family',
                    'patient.date_of_birth': 'birthDate',
                    'patient.ssn_last4': 'identifier[ssn].value',
                },
                'is_active': False,
                'last_tested': now - timedelta(days=5),
                'test_results': {'status': 'warning', 'match_rate': 0.87, 'unmatched': 13},
            },
        ]

        for mdata in mappings_data:
            m, created = DataMapping.objects.get_or_create(
                name=mdata['name'],
                defaults=mdata,
            )
            if created:
                self.stdout.write(f"  + Mapping: {m.name}")

        # ── 5. Integration Transactions ───────────────────────────────────
        self.stdout.write('Creating integration transactions...')
        tx_templates = [
            ('fhir_read', 'GET', 200, 'completed', 142),
            ('fhir_create', 'POST', 201, 'completed', 230),
            ('fhir_search', 'GET', 200, 'completed', 89),
            ('hl7_receive', 'POST', 200, 'completed', 54),
            ('hl7_send', 'POST', 200, 'completed', 78),
            ('data_sync', 'POST', 200, 'completed', 512),
            ('fhir_read', 'GET', 404, 'failed', 88),
            ('fhir_update', 'PUT', 200, 'completed', 167),
            ('bulk_export', 'GET', 200, 'completed', 3421),
            ('fhir_search', 'GET', 500, 'failed', 30),
            ('hl7_send', 'POST', 408, 'timeout', 10000),
            ('fhir_create', 'POST', 422, 'failed', 195),
        ]

        for tx_type, method, status_code, status, duration in tx_templates:
            sys_obj = random.choice(systems)
            patient = random.choice(patients) if patients else None
            start_time = now - timedelta(hours=random.randint(1, 168))

            resource_type_map = {
                'fhir_read': 'Patient', 'fhir_create': 'Observation',
                'fhir_search': 'Condition', 'fhir_update': 'MedicationRequest',
                'bulk_export': 'Patient', 'data_sync': 'Encounter',
                'hl7_receive': 'ORU', 'hl7_send': 'ADT',
            }
            rt = resource_type_map.get(tx_type, 'Patient')

            IntegrationTransaction.objects.create(
                transaction_type=tx_type,
                external_system=sys_obj,
                endpoint_url=f"{sys_obj.base_url}/{rt}/{uuid.uuid4()}",
                http_method=method,
                status=status,
                status_code=status_code,
                error_message='Resource not found' if status_code == 404
                    else 'Internal server error' if status_code == 500
                    else 'Unprocessable entity – validation failed' if status_code == 422
                    else 'Gateway timeout' if status_code == 408
                    else '',
                duration_ms=duration,
                started_at=start_time,
                completed_at=start_time + timedelta(milliseconds=duration),
                related_patient=patient,
                request_data={'resourceType': rt, 'id': str(uuid.uuid4())} if method in ('POST', 'PUT') else {},
                response_data={'resourceType': rt, 'id': str(uuid.uuid4())} if status == 'completed' else {'error': 'See error_message'},
            )
        self.stdout.write(f"  + {len(tx_templates)} transactions")

        # ── 6. Consent Management ─────────────────────────────────────────
        self.stdout.write('Creating consent records...')
        if patients:
            consent_pairs = [
                ('hie', 'granted', 'Share records with State Health Information Exchange for care coordination.'),
                ('treatment', 'granted', 'Authorization for treatment and care delivery.'),
                ('research', 'denied', 'Participation in anonymised clinical research programme.'),
                ('data_sharing', 'granted', 'Share data with authorised external laboratory systems.'),
                ('marketing', 'denied', 'Use of health data for marketing and commercial offers.'),
                ('emergency', 'granted', 'Access to records in emergency situations without prior notice.'),
            ]

            for i, patient in enumerate(patients[:6]):
                consent_type, status_val, purpose = consent_pairs[i % len(consent_pairs)]

                # ConsentManagement has unique_together on (patient, consent_type),
                # so use get_or_create to avoid duplicates on re-run.
                granted_time = now - timedelta(days=random.randint(10, 365))
                c, created = ConsentManagement.objects.get_or_create(
                    patient=patient,
                    consent_type=consent_type,
                    defaults=dict(
                        status=status_val,
                        purpose=purpose,
                        scope=['Patient', 'Encounter', 'Observation', 'Condition'],
                        authorized_purposes=['treatment', 'care_coordination'],
                        granted_at=granted_time if status_val == 'granted' else None,
                        expires_at=granted_time + timedelta(days=365) if status_val == 'granted' else None,
                        legal_basis='HIPAA Authorization' if status_val == 'granted' else '',
                        consent_document=f"I, {patient.get_full_name()}, consent to the {purpose.lower()}",
                        signature_data={'method': 'electronic', 'captured_at': granted_time.isoformat()} if status_val == 'granted' else {},
                    )
                )
                if c and created:
                    c.authorized_systems.set(random.sample(systems[:3], k=min(2, len(systems))))
                    self.stdout.write(f"  + Consent: {patient.get_full_name()} – {consent_type} ({status_val})")

        # ── Summary ───────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Interoperability data seeded:\n"
            f"  {ExternalSystem.objects.count()} external systems\n"
            f"  {FHIRResource.objects.count()} FHIR resources\n"
            f"  {HL7Message.objects.count()} HL7 messages\n"
            f"  {DataMapping.objects.count()} data mappings\n"
            f"  {IntegrationTransaction.objects.count()} transactions\n"
            f"  {ConsentManagement.objects.count()} consent records"
        ))
