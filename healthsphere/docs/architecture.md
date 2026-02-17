# HealthSphere AI - Architecture Documentation

## Overview

HealthSphere AI is a college-level healthcare platform built with Django that provides three separate portals for different user roles:

1. **Hospital Administration Portal** - For hospital administrators
2. **Clinical Portal** - For doctors and nurses  
3. **Patient Portal** - For patients

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Admin Portal│  │Clinical     │  │ Patient Portal          │ │
│  │ Dashboard   │  │Portal       │  │ Dashboard, Reports,     │ │
│  │ Patients    │  │Dashboard    │  │ Appointments, AI Chat   │ │
│  │ Resources   │  │Risk Insights│  └─────────────────────────┘ │
│  │ Analytics   │  │Treatment    │                              │
│  └─────────────┘  │Journey      │                              │
│                   │Triage       │                              │
│                   └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Django Framework                          ││
│  │  ┌─────────┐ ┌──────────────┐ ┌───────────────────────────┐ ││
│  │  │  Users  │ │ Admin Portal │ │ Clinical Portal           │ ││
│  │  │   App   │ │     App      │ │      App                  │ ││
│  │  └─────────┘ └──────────────┘ └───────────────────────────┘ ││
│  │  ┌─────────────────────┐ ┌──────────────────────────────┐  ││
│  │  │   Patient Portal    │ │      AI Services App         │  ││
│  │  │        App          │ │ (Simulated ML Functions)     │  ││
│  │  └─────────────────────┘ └──────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   SQLite Database                            ││
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐││
│  │  │    User     │ │   Role      │ │   UserProfile           │││
│  │  │   Models    │ │   Model     │ │      Model              │││
│  │  └─────────────┘ └─────────────┘ └─────────────────────────┘││
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐││
│  │  │  Hospital   │ │ Admission   │ │   StaffSchedule         │││
│  │  │  Resource   │ │   Record    │ │      Model              │││
│  │  └─────────────┘ └─────────────┘ └─────────────────────────┘││
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐││
│  │  │  Medical    │ │ Treatment   │ │   VitalRecord           │││
│  │  │   Record    │ │    Plan     │ │      Model              │││
│  │  └─────────────┘ └─────────────┘ └─────────────────────────┘││
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐││
│  │  │  Patient    │ │ Appointment │ │   HealthMetric          │││
│  │  │  Profile    │ │   Model     │ │      Model              │││
│  │  └─────────────┘ └─────────────┘ └─────────────────────────┘││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
healthsphere/
├── config/                     # Project configuration
│   ├── __init__.py
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL routing
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
│
├── users/                      # User management app
│   ├── models.py              # User, Role, UserProfile models
│   ├── views.py               # Authentication views
│   ├── forms.py               # Registration, login forms
│   ├── urls.py                # Auth URL patterns
│   ├── admin.py               # Admin configuration
│   └── apps.py                # App configuration
│
├── admin_portal/               # Hospital admin app
│   ├── models.py              # HospitalResource, AdmissionRecord, StaffSchedule
│   ├── views.py               # Admin dashboard views
│   ├── urls.py                # Admin portal URLs
│   ├── admin.py               # Model admin registration
│   └── apps.py                # App configuration
│
├── clinical_portal/            # Doctor/Nurse app
│   ├── models.py              # MedicalRecord, TreatmentPlan, VitalRecord
│   ├── views.py               # Clinical dashboard views
│   ├── urls.py                # Clinical portal URLs
│   ├── admin.py               # Model admin registration
│   └── apps.py                # App configuration
│
├── patient_portal/             # Patient app
│   ├── models.py              # PatientProfile, Appointment, HealthMetric
│   ├── views.py               # Patient dashboard views
│   ├── forms.py               # Appointment, metric forms
│   ├── urls.py                # Patient portal URLs
│   ├── admin.py               # Model admin registration
│   └── apps.py                # App configuration
│
├── ai_services/                # AI/ML services (simulated)
│   ├── __init__.py
│   ├── risk_service.py        # Risk prediction functions
│   ├── triage_service.py      # Triage scoring functions
│   ├── report_explainer.py    # Report explanation functions
│   └── journey_service.py     # Treatment journey functions
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── navbar.html            # Navigation bar
│   ├── sidebar.html           # Sidebar navigation
│   ├── users/                 # User templates
│   ├── admin_portal/          # Admin portal templates
│   ├── clinical_portal/       # Clinical portal templates
│   └── patient_portal/        # Patient portal templates
│
├── static/                     # Static files
│   ├── css/
│   │   └── styles.css         # Main stylesheet
│   └── js/
│       └── main.js            # Main JavaScript
│
├── docs/                       # Documentation
│   ├── architecture.md        # This file
│   ├── features.md            # Feature documentation
│   └── setup.md               # Setup instructions
│
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
└── README.md                   # Project readme
```

## Django Apps

### 1. Users App (`users/`)
- **Purpose**: Handle authentication and user management
- **Models**:
  - `Role`: Define user roles (Admin, Doctor, Nurse, Patient)
  - `User`: Custom user model with role assignment
  - `UserProfile`: Extended user information
- **Key Features**:
  - Custom user registration with role selection
  - Role-based login redirect
  - Profile management

### 2. Admin Portal App (`admin_portal/`)
- **Purpose**: Hospital administration features
- **Models**:
  - `HospitalResource`: Track beds, equipment, rooms
  - `AdmissionRecord`: Patient admission/discharge records
  - `StaffSchedule`: Staff scheduling and shift management
- **Key Features**:
  - Dashboard with hospital statistics
  - Patient management
  - Resource monitoring
  - Analytics views

### 3. Clinical Portal App (`clinical_portal/`)
- **Purpose**: Doctor and nurse clinical tools
- **Models**:
  - `MedicalRecord`: Patient medical records
  - `TreatmentPlan`: Treatment plans with medications
  - `VitalRecord`: Vital sign recordings
- **Key Features**:
  - Patient risk insights (AI-powered)
  - Treatment journey visualization
  - Triage dashboard
  - Vital signs monitoring

### 4. Patient Portal App (`patient_portal/`)
- **Purpose**: Patient self-service features
- **Models**:
  - `PatientProfile`: Extended patient information
  - `Appointment`: Appointment scheduling
  - `HealthMetric`: Self-reported health metrics
- **Key Features**:
  - Personal health dashboard
  - Appointment booking
  - Report upload with AI explanations
  - Health risk score viewer
  - AI health assistant chat

### 5. AI Services App (`ai_services/`)
- **Purpose**: Simulated AI/ML functionality
- **Services**:
  - `risk_service.py`: Patient risk prediction
  - `triage_service.py`: Emergency triage scoring
  - `report_explainer.py`: Medical report explanations
  - `journey_service.py`: Treatment journey predictions
- **Note**: All AI functions are simulated with random/mock data for demonstration

## Data Flow

### Authentication Flow
```
User Login → Check Credentials → Determine Role → Redirect to Portal
     ↓
   Admin → Admin Portal Dashboard
   Doctor/Nurse → Clinical Portal Dashboard
   Patient → Patient Portal Dashboard
```

### AI Service Integration
```
View Request → Call AI Service → Generate Mock Response → Render Template
```

Example:
```
Patient Risk View → risk_service.predict_risk() → Mock Risk Data → Display Score
```

## Security Considerations

### Role-Based Access Control
- Each portal has a decorator that checks user role
- `@admin_required` - Admin portal access
- `@clinical_staff_required` - Clinical portal access (Doctor/Nurse)
- Patient portal uses `@login_required` with patient role check

### Data Protection
- CSRF protection enabled on all forms
- Password hashing using Django's default
- Session-based authentication

## Database Schema

### Users Domain
- `Role` (id, name, description)
- `User` (id, username, email, password, role_fk, phone, dob, address)
- `UserProfile` (id, user_fk, avatar, bio, specialization, department)

### Hospital Administration Domain
- `HospitalResource` (id, name, type, location, status, capacity)
- `AdmissionRecord` (id, patient_fk, admission_date, discharge_date, ward, diagnosis)
- `StaffSchedule` (id, staff_fk, date, shift, department)

### Clinical Domain
- `MedicalRecord` (id, patient_fk, record_type, title, description, ai_risk_score)
- `TreatmentPlan` (id, record_fk, medications, procedures, status)
- `VitalRecord` (id, patient_fk, bp, heart_rate, temperature, oxygen)

### Patient Domain
- `PatientProfile` (id, user_fk, blood_type, allergies, insurance)
- `Appointment` (id, patient_fk, doctor_fk, date, type, status)
- `HealthMetric` (id, patient_fk, metric_type, value, unit)

## Future Enhancements

1. **Real AI/ML Integration**: Replace mock services with actual ML models
2. **REST API**: Add DRF for mobile app support
3. **Real-time Features**: WebSocket for live notifications
4. **File Storage**: Cloud storage for medical documents
5. **Two-Factor Auth**: Enhanced security
6. **Audit Logging**: Track all data access
7. **Multi-tenancy**: Support for multiple hospitals
