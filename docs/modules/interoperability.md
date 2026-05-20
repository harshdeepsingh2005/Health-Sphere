# Interoperability Module Documentation

The `interoperability` module is responsible for exchanging healthcare data with external systems (like external EHRs or lab networks) using industry-standard protocols, primarily FHIR R4 and HL7 v2.x.

## Tech Stack
- **Framework**: Django
- **Standards Supported**: FHIR R4, HL7 v2.x
- **Services Engine**: Custom `FHIRClient` and `HL7MessageProcessor` acting as HTTP/MLLP orchestrators.
- **Security/Audit**: `IntegrationTransaction` logs every external call for compliance.

## Key Files & Functions

### `models.py`
- **`ExternalSystem`**: Configurations for external endpoints (API URLs, auth details, FHIR versions).
  - `test_connection()`: Pings the external service.
- **`FHIRResource`**: Local storage mirror for FHIR-compliant payloads (Patient, Observation, Condition, etc.).
  - `get_fhir_json()` & `validate_fhir_resource()`: JSON schema operations.
- **`HL7Message`**: Stores inbound/outbound HL7 raw text strings (e.g., ADT, ORU) and processing statuses.
  - `parse_hl7_message()`: Breaks down raw strings into Python dicts.
  - `generate_ack()`: Creates standard AA (Application Accept) acknowledgments.
- **`DataMapping`**: Stores rules for converting internal Django model fields into FHIR/HL7 structures, and vice versa.
- **`IntegrationTransaction`**: An exhaustive audit trail tracking every read/write to external networks to guarantee HIPAA compliance.

### `fhir_hl7_services.py`
The heavy-lifting logic tier for integration.
- **`FHIRClient`**: Handles FHIR REST operations (`read_resource`, `create_resource`, `search_resources`). Manages endpoint authentication and consent checking boundaries.
- **`HL7MessageProcessor`**:
  - `process_inbound_message()`: Ingests a raw HL7 string and routes it to specific handlers (`_handle_adt_message`, `_handle_oru_message`, etc.) based on the MSH segment.
  - `send_outbound_message()`: Constructs and "transmits" outgoing HL7 via simulated MLLP.

### `views.py`
Provides an administrative UI for IT teams to monitor integration health.
- **`interoperability_dashboard`**: Shows message volumes, failure rates, and system statuses.
- **`external_systems_list` / `external_system_detail`**: CRUD for endpoint configurations.
- **`fhir_resources_list` / `hl7_messages_list`**: View payload logs and inspect failed messages.
- **`reprocess_hl7_message`**: Action view to retry a failed HL7 payload.
- **API Webhooks (`api_fhir_webhook`, `api_hl7_endpoint`)**: Live endpoints meant to receive incoming push notifications or MLLP-over-HTTP payloads from external vendor networks.
