# Architecture — HealthSphere AI

## Overview

HealthSphere AI is a multi-app Django monolith that follows a standard MVT (Model-View-Template) architecture. Each feature area is isolated into its own Django app with its own models, views, and URL namespace.

```
Browser
  │
  ▼
Django URL Router (config/urls.py)
  │
  ├── /admin-portal/   → admin_portal app
  ├── /patient/        → patient_portal app
  ├── /clinical/       → clinical_portal app
  ├── /appointments/   → appointments app
  ├── /prescriptions/  → prescriptions app
  ├── /analytics/      → analytics app
  ├── /interoperability/ → interoperability app
  ├── /users/          → users app
  └── /ai-insights/    → AI services layer
```

---

## App Dependency Map

```
users (auth foundation)
  │
  ├── admin_portal      (AdmissionRecord, HospitalResource, StaffSchedule)
  ├── patient_portal    (uses Appointment, MedicalRecord, PrescriptionRequest)
  ├── clinical_portal   (MedicalRecord, VitalRecord, TreatmentPlan)
  ├── appointments      (AppointmentType, DoctorSchedule, Appointment)
  ├── prescriptions     (Prescription, PrescriptionItem, Medication)
  ├── analytics         (PredictiveModel, AnalyticsReport + real data joins)
  ├── interoperability  (ExternalSystem, FHIRResource, HL7Message, ConsentManagement)
  ├── telemedicine      (TelemedicineSession)
  └── ai_services       (gemini_client, triage_service, risk_service, journey_service)
```

---

## Data Flow

### Patient Books Appointment
```
Patient → POST /patient/book-appointment/
  → patient_portal/views.py:book_appointment()
  → appointments/models.py:Appointment.objects.create()
  → AI triage via ai_services/triage_service.py
  → Email reminder (appointments/models.py:AppointmentReminder)
```

### AI Health Assistant Chat
```
Patient → POST /patient/ai-assistant/
  → patient_portal/views.py:ai_assistant()
  → ai_services/gemini_client.py:GeminiClient.chat()
  → Google Gemini API (gemini-2.0-flash)
  → JsonResponse streamed back to browser
```

### Automated Lab Report Analysis
```
Patient → POST /patient/report/ (Uploads PDF/Image)
  → patient_portal/views.py:upload_report()
  → pypdf extracts raw text from PDF
  → ai_services/gemini_client.py:GeminiClient.analyze_report()
  → Google Gemini API (gemini-2.0-flash) parses and normalizes medical text
  → MedicalRecord created with AI Findings
  → Doctor alerted via Clinical Portal
```

### FHIR Data Exchange
```
External EHR → POST /interoperability/api/fhir/
  → interoperability/views.py:FHIRResourceCreateView
  → interoperability/models.py:FHIRResource.objects.create()
  → IntegrationTransaction logged
  → ConsentManagement checked
```

---

## Authentication & Authorization

- **Authentication:** Django's built-in session-based auth (`django.contrib.auth`)  
- **Custom User Model:** `users.User` extends `AbstractUser` with a FK to `users.Role`
- **Roles:** `admin`, `doctor`, `nurse`, `patient`, `staff` — defined in `users.Role`
- **Access control:** Views use `LoginRequiredMixin` + `PermissionRequiredMixin` or manual `role` checks
- **2FA:** Optional two-factor auth via `users.TwoFactorAuth`
- **Audit log:** All significant actions logged to `users.AuditLog`

---

## Database Schema Summary

### Core Tables
| Model | App | Key fields |
|-------|-----|-----------|
| `User` | users | username, email, role FK, phone, date_of_birth |
| `Role` | users | name, permissions |
| `UserProfile` | users | user FK, avatar, department, specialization |

### Clinical
| Model | App | Key fields |
|-------|-----|-----------|
| `MedicalRecord` | clinical_portal | patient, created_by, record_type, diagnosis_code, severity |
| `VitalRecord` | clinical_portal | patient, heart_rate, blood_pressure, temperature, recorded_at |
| `TreatmentPlan` | clinical_portal | patient, created_by, goals, status |

### Operations
| Model | App | Key fields |
|-------|-----|-----------|
| `Appointment` | appointments | patient, doctor, appointment_type, scheduled_date, status |
| `AdmissionRecord` | admin_portal | patient, admission_type, ward, status, discharge_date |
| `HospitalResource` | admin_portal | name, resource_type, status, quantity |
| `Prescription` | prescriptions | patient, doctor, status, items |

### Interoperability
| Model | App | Key fields |
|-------|-----|-----------|
| `ExternalSystem` | interoperability | name, system_type, connection_status, base_url |
| `FHIRResource` | interoperability | resource_type, fhir_id, external_system, is_valid |
| `HL7Message` | interoperability | message_type, direction, processing_status |
| `ConsentManagement` | interoperability | patient, consent_type, status, expires_at |

---

## AI Services Layer

Located in `ai_services/`:

| File | Responsibility |
|------|---------------|
| `gemini_client.py` | Wraps Google Gemini API; Handles `chat()` and `analyze_report()` for interpreting complex lab PDFs |
| `triage_service.py` | Calculates ESI (Emergency Severity Index) based on vitals and symptoms using Gemini |
| `risk_service.py` | Patient data → risk score + risk factors |
| `journey_service.py` | Patient health journey narrative generation |

The Gemini client supports both `google-generativeai` and a fallback `ollama` local model.

---

## Static Files & Frontend

- All static files live in `static/css/`, `static/js/`, `static/images/`
- Key CSS: `base.css` (global), `bento-grid.css` (dashboard cards)
- No frontend framework — plain HTML + CSS + vanilla JS
- Font Awesome 6 icons via CDN
- Google Fonts (Inter) via CDN

---

## Settings

Config is split between `config/settings.py` and `.env`:

```python
# .env required keys
GEMINI_API_KEY=your_gemini_key
SECRET_KEY=your_django_secret
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3  # or postgres://...
```

---

## Running in Production

1. Set `DEBUG=False` and configure `ALLOWED_HOSTS`
2. Switch to PostgreSQL: set `DATABASE_URL`
3. Configure `STATIC_ROOT` and run `collectstatic`
4. Use gunicorn: `gunicorn config.wsgi:application`
5. Set up nginx as reverse proxy
6. Set all secrets as environment variables (never in code)
