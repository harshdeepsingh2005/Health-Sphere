# Apps Reference — HealthSphere AI

Complete reference for all Django apps in HealthSphere AI — their models, views, URLs, and how they connect.

---

## `users` — Authentication & Roles

**URL prefix:** `/users/`

### Models
| Model | Purpose |
|-------|---------|
| `Role` | Named roles: admin, doctor, nurse, patient, staff |
| `User` | Custom user extending AbstractUser; has `role` FK |
| `UserProfile` | Extended profile: avatar, department, specialization, bio |
| `TwoFactorAuth` | Optional TOTP two-factor auth per user |
| `AuditLog` | Tracks all significant user actions with timestamps |

### Key Views
| URL | View | Description |
|-----|------|-------------|
| `/users/login/` | `LoginView` | Login page |
| `/users/logout/` | `LogoutView` | Logout |
| `/users/register/` | `RegisterView` | New user registration |
| `/users/profile/` | `ProfileView` | View/edit profile |
| `/users/change-password/` | `ChangePasswordView` | Password change |

---

## `admin_portal` — Hospital Administration

**URL prefix:** `/admin-portal/`

### Models
| Model | Purpose |
|-------|---------|
| `HospitalResource` | Beds, ICU, ventilators, rooms, ambulances — status & quantity |
| `AdmissionRecord` | Patient admission/discharge records with ward, room, bed, attending doctor |
| `StaffSchedule` | Work schedules: shift type, date, department, status |

### Key Views
| URL | Description |
|-----|-------------|
| `/admin-portal/` | Main admin dashboard |
| `/admin-portal/patients/` | Patient list |
| `/admin-portal/admissions/` | Admission records |
| `/admin-portal/resources/` | Hospital resources |
| `/admin-portal/staff/` | Staff directory |
| `/admin-portal/schedules/` | Staff schedules |
| `/admin-portal/analytics/` | Admin analytics view |

### Admission Status Flow
```
admitted → discharged
admitted → transferred
admitted → deceased
```

---

## `patient_portal` — Patient Self-Service

**URL prefix:** `/patient/`

### Features
- Personal health dashboard with AI risk score
- Book and manage appointments
- View medical history and prescriptions
- Upload and get AI analysis of lab reports/X-rays
- AI Health Assistant (Gemini-powered chat)
- Medication tracking
- Health journey visualization

### Key Views
| URL | Description |
|-----|-------------|
| `/patient/dashboard/` | Patient home with health summary |
| `/patient/ai-assistant/` | Gemini AI chat for health questions |
| `/patient/book-appointment/` | Appointment booking flow |
| `/patient/appointments/` | My appointments list |
| `/patient/report/` | Upload medical report for AI analysis |
| `/patient/records/` | Medical history |
| `/patient/medications/` | Medication list |
| `/patient/risk/` | AI-generated risk assessment |

---

## `clinical_portal` — Doctor/Clinical Workflows

**URL prefix:** `/clinical/`

### Models
| Model | Purpose |
|-------|---------|
| `MedicalRecord` | Patient records: type, diagnosis_code, severity, attachments, AI recommendations |
| `VitalRecord` | Vital signs: heart_rate, blood_pressure, temperature, oxygen_saturation, weight |
| `TreatmentPlan` | Care plans: goals, interventions, created_by, status |

### Key Views
| URL | Description |
|-----|-------------|
| `/clinical/` | Clinical dashboard |
| `/clinical/patients/` | Patient list for clinical staff |
| `/clinical/patients/<id>/` | Patient detail with full history |
| `/clinical/records/` | All medical records |
| `/clinical/records/<id>/` | Record detail |
| `/clinical/records/create/` | Add new medical record |
| `/clinical/vitals/` | Vitals monitor — all patients |
| `/clinical/vitals/<id>/` | Patient vitals history |
| `/clinical/treatment-plans/` | Treatment plan list |

### Record Types
`consultation`, `diagnosis`, `lab_result`, `imaging`, `procedure`, `discharge_summary`, `other`

### Severity Levels
`low`, `medium`, `high`, `critical`

---

## `appointments` — Scheduling

**URL prefix:** `/appointments/`

### Models
| Model | Purpose |
|-------|---------|
| `AppointmentType` | Types: consultation, follow_up, emergency, telemedicine, routine_checkup, specialist |
| `DoctorSchedule` | Doctor availability by day of week and time slots |
| `Appointment` | Full appointment: patient, doctor, type, date, time, status, notes |
| `AppointmentReminder` | Automated reminders (email/SMS) linked to appointments |

### Status Flow
```
requested → confirmed → in_progress → completed
          → cancelled
          → rescheduled
          → no_show
```

### Key Views
| URL | Description |
|-----|-------------|
| `/appointments/` | Appointment list |
| `/appointments/calendar/` | Calendar view |
| `/appointments/<id>/` | Appointment detail |
| `/appointments/create/` | Create appointment (admin/staff) |
| `/appointments/<id>/confirm/` | Confirm appointment |
| `/appointments/<id>/cancel/` | Cancel appointment |

---

## `prescriptions` — E-Prescriptions

**URL prefix:** `/prescriptions/`

### Models
| Model | Purpose |
|-------|---------|
| `Medication` | Drug catalog with name, dosage forms, controlled flag |
| `Prescription` | Header: patient, doctor, status, date, notes |
| `PrescriptionItem` | Line items: medication, dosage, frequency, duration |

### Key Views
| URL | Description |
|-----|-------------|
| `/prescriptions/` | Prescription list |
| `/prescriptions/<id>/` | Prescription detail |
| `/prescriptions/create/` | Create new prescription |
| `/prescriptions/medications/` | Medication catalog |

---

## `analytics` — Dashboards & Reporting

**URL prefix:** `/analytics/`

All views query **real app data** — not a separate data warehouse.

### Data Sources
- `User` → patient/doctor counts
- `Appointment` → volumes, completion rates, trends
- `AdmissionRecord` → patient flow, LOS, discharge stats
- `HospitalResource` → bed occupancy
- `MedicalRecord`, `VitalRecord`, `TreatmentPlan` → clinical metrics

### Views
| URL | Description |
|-----|-------------|
| `/analytics/` | Overview dashboard — all KPIs |
| `/analytics/patient-flow/` | 14-day admission/appointment trend charts |
| `/analytics/clinical-outcomes/` | Records, treatment plans, appointment outcomes |
| `/analytics/data-quality/` | Completeness/quality scores across all models |
| `/analytics/reports/` | Saved analytics reports |
| `/analytics/models/` | Predictive ML model registry |

---

## `interoperability` — FHIR & HL7

**URL prefix:** `/interoperability/`

### Models
| Model | Purpose |
|-------|---------|
| `ExternalSystem` | EHR/lab system integration configs |
| `FHIRResource` | FHIR R4 resources (Patient, Observation, etc.) |
| `HL7Message` | HL7 v2 messages with direction (inbound/outbound) and processing status |
| `DataMapping` | Field-level mapping configs between systems |
| `IntegrationTransaction` | Full audit log of every API call |
| `ConsentManagement` | HIPAA/GDPR patient consent records |

### External System Types
`ehr`, `lab`, `pharmacy`, `radiology`, `insurance`, `government`, `other`

### Views
| URL | Description |
|-----|-------------|
| `/interoperability/` | Integration dashboard |
| `/interoperability/systems/` | External systems list |
| `/interoperability/fhir/` | FHIR resources |
| `/interoperability/hl7/` | HL7 messages |
| `/interoperability/mappings/` | Data mappings |
| `/interoperability/transactions/` | Transaction log |
| `/interoperability/consents/` | Consent records |

---

## `ai_services` — AI Integration

Not a Django app with URLs — it's a Python package imported by other apps.

### Files
| File | Exports | Usage |
|------|---------|-------|
| `gemini_client.py` | `GeminiClient` | Wraps Gemini API for chat, analysis |
| `triage_service.py` | `triage_symptoms()` | Returns urgency level + recommended department |
| `risk_service.py` | `calculate_risk()` | Returns risk score + contributing factors |
| `journey_service.py` | `generate_journey()` | Patient health story narrative |

### Usage Example
```python
from ai_services.gemini_client import GeminiClient

client = GeminiClient()
response = client.chat(
    message="What does a high HbA1c level mean?",
    history=[]  # list of previous messages
)
```

---

## `telemedicine` — Video Consultations

**URL prefix:** `/telemedicine/`

Handles video-based appointments. Creates video room IDs stored in `Appointment.video_room_id`.

---

## `config` — Django Settings

Located in `config/`:
- `settings.py` — all Django settings, reads from `.env`
- `urls.py` — root URL routing
- `wsgi.py` / `asgi.py` — deployment entry points
