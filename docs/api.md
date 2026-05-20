# API Reference — HealthSphere AI

This document covers all HTTP endpoints exposed by HealthSphere AI, including both browser-rendered views and JSON API endpoints.

> All endpoints require login unless marked **public**. Authentication is session-based (cookie).

---

## Authentication Endpoints

| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| GET | `/users/login/` | Login page | Public |
| POST | `/users/login/` | Submit login credentials | Public |
| GET/POST | `/users/logout/` | Logout | Required |
| GET | `/users/register/` | Registration page | Public |
| POST | `/users/register/` | Submit registration | Public |
| GET/POST | `/users/profile/` | View/edit profile | Required |
| POST | `/users/change-password/` | Change password | Required |

---

## Admin Portal Endpoints

**Base:** `/admin-portal/` | **Role:** admin, staff

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/admin-portal/` | Admin dashboard |
| GET | `/admin-portal/patients/` | All patients list |
| GET | `/admin-portal/admissions/` | Admission records |
| POST | `/admin-portal/admissions/create/` | Create admission |
| POST | `/admin-portal/admissions/<id>/discharge/` | Discharge patient |
| GET | `/admin-portal/resources/` | Hospital resources |
| POST | `/admin-portal/resources/create/` | Add resource |
| GET | `/admin-portal/staff/` | Staff directory |
| GET | `/admin-portal/schedules/` | Staff schedules |

---

## Patient Portal Endpoints

**Base:** `/patient/` | **Role:** patient

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/patient/dashboard/` | Patient dashboard |
| GET | `/patient/ai-assistant/` | AI chat page |
| POST | `/patient/ai-assistant/` | Send message to AI (returns JSON) |
| GET | `/patient/book-appointment/` | Booking form |
| POST | `/patient/book-appointment/` | Submit appointment |
| GET | `/patient/appointments/` | My appointments |
| GET | `/patient/report/` | Report upload page |
| POST | `/patient/report/` | Upload report for AI analysis |
| GET | `/patient/records/` | Medical history |
| GET | `/patient/medications/` | Medication list |
| GET | `/patient/risk/` | Risk assessment page |

### AI Assistant — JSON Response Format
```
POST /patient/ai-assistant/
Content-Type: application/json

Request:
{ "message": "What does a high blood sugar level mean?" }

Response:
{
  "response": "High blood sugar (hyperglycemia) can indicate...",
  "success": true
}
```

### Report Analysis — JSON Response Format
```
POST /patient/report/
Content-Type: multipart/form-data
Body: file=<uploaded_file>

Response:
{
  "explanation": "Your CBC report shows...",
  "findings": [...],
  "success": true
}
```

---

## Clinical Portal Endpoints

**Base:** `/clinical/` | **Role:** doctor, nurse, admin

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/clinical/` | Clinical dashboard |
| GET | `/clinical/patients/` | Patient list |
| GET | `/clinical/patients/<id>/` | Patient detail |
| GET | `/clinical/records/` | All records |
| GET | `/clinical/records/<id>/` | Record detail |
| GET/POST | `/clinical/records/create/` | Create record |
| GET/POST | `/clinical/records/<id>/edit/` | Edit record |
| GET | `/clinical/vitals/` | Vitals monitor |
| GET | `/clinical/vitals/<id>/` | Patient vitals |
| POST | `/clinical/vitals/record/` | Record vital signs |
| GET | `/clinical/treatment-plans/` | Treatment plans |
| GET/POST | `/clinical/treatment-plans/create/` | Create plan |

---

## Appointments Endpoints

**Base:** `/appointments/` | **Role:** all (filtered by role)

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/appointments/` | Appointment list |
| GET | `/appointments/calendar/` | Calendar view |
| GET | `/appointments/<id>/` | Appointment detail |
| GET/POST | `/appointments/create/` | Create appointment |
| POST | `/appointments/<id>/confirm/` | Confirm |
| POST | `/appointments/<id>/cancel/` | Cancel |
| POST | `/appointments/<id>/complete/` | Mark complete |
| GET | `/appointments/doctor-slots/<doctor_id>/` | Available slots (JSON) |

### Doctor Slots — JSON Response
```
GET /appointments/doctor-slots/<doctor_id>/?date=2026-02-20

Response:
{
  "slots": ["09:00", "09:30", "10:00", "14:00"],
  "doctor": "Dr. Sarah Johnson"
}
```

---

## Prescriptions Endpoints

**Base:** `/prescriptions/` | **Role:** doctor, admin, patient (read-only)

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/prescriptions/` | Prescription list |
| GET | `/prescriptions/<id>/` | Prescription detail |
| GET/POST | `/prescriptions/create/` | Create prescription |
| GET | `/prescriptions/medications/` | Medication catalog |
| GET | `/prescriptions/<id>/print/` | Print-ready view |

---

## Analytics Endpoints

**Base:** `/analytics/` | **Role:** admin

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/analytics/` | Analytics overview |
| GET | `/analytics/patient-flow/` | Patient flow dashboard |
| GET | `/analytics/clinical-outcomes/` | Clinical outcomes |
| GET | `/analytics/data-quality/` | Data quality scores |
| GET | `/analytics/reports/` | Reports list |
| GET | `/analytics/reports/<id>/` | Report detail |
| GET | `/analytics/reports/<id>/download/` | Download as JSON |
| GET | `/analytics/models/` | ML models list |
| GET | `/analytics/models/<id>/` | Model detail |

### Analytics JSON API Endpoints
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/analytics/api/predict/patient-flow/` | Generate flow prediction |
| POST | `/analytics/api/predict/clinical-outcome/` | Generate outcome prediction |
| POST | `/analytics/api/reports/generate/` | Generate a report |
| POST | `/analytics/api/quality/assess/` | Run quality assessment |

---

## Interoperability Endpoints

**Base:** `/interoperability/` | **Role:** admin

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/interoperability/` | Interoperability dashboard |
| GET | `/interoperability/systems/` | External systems |
| GET | `/interoperability/systems/<id>/` | System detail |
| GET | `/interoperability/fhir/` | FHIR resources |
| GET | `/interoperability/hl7/` | HL7 messages |
| GET | `/interoperability/mappings/` | Data mappings |
| GET | `/interoperability/transactions/` | Transaction log |
| GET | `/interoperability/consents/` | Consent records |

---

## Common Query Parameters

Many list views accept filter query parameters:

```
# Appointments
GET /appointments/?status=confirmed&date_from=2026-02-01&date_to=2026-02-28

# HL7 Messages
GET /interoperability/hl7/?status=pending&direction=inbound&type=ADT_A01

# Integration Transactions  
GET /interoperability/transactions/?status=failed&system=1&date_from=2026-02-01

# Analytics Appointments Trend
GET /analytics/patient-flow/?days=30
```

---

## Error Responses

All JSON API endpoints return errors in this format:

```json
{
  "error": "Description of what went wrong",
  "success": false
}
```

HTTP status codes:
- `200` — success
- `400` — bad request (missing/invalid parameters)
- `401` — not authenticated
- `403` — forbidden (wrong role)
- `404` — resource not found
- `500` — server error

---

## Django Admin

The standard Django admin interface is available at `/django-admin/` for superusers. It provides direct database access to all models.
