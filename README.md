# HealthSphere AI

> **A full-stack AI-powered hospital management & preventive healthcare platform built with Django.**

HealthSphere AI combines clinical management, patient self-service, predictive analytics, and FHIR-compliant data exchange in a single coherent platform. It uses Google Gemini for natural-language health reasoning and integrates ML-driven risk scoring, medical report analysis, and automated triage.

---

## Quick Start

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd Health-Sphere/healthsphere

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY, SECRET_KEY, etc.

# 5. Run migrations and seed data
python manage.py migrate
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## Feature Overview

| Module | Description |
|--------|-------------|
| 🏥 **Admin Portal** | Hospital dashboard, admissions, resource management, staff schedules |
| 👤 **Patient Portal** | Appointments, medical history, AI health assistant, risk analysis |
| 🩺 **Clinical Portal** | Doctor workflows, medical records, vitals, treatment plans |
| 📅 **Appointments** | Booking, calendar, telemedicine, reminders |
| 💊 **Prescriptions** | E-prescription management, medication tracking |
| 📊 **Analytics** | Real-time KPIs, patient flow, clinical outcomes, data quality |
| 🔗 **Interoperability** | FHIR R4, HL7 v2, external system integration, consent management |
| 🤖 **AI Insights** | Gemini-powered analysis, risk prediction, report interpretation |
| 👥 **Users** | Role-based access control (Admin, Doctor, Patient, Nurse, Staff) |

---

## Documentation

| File | Contents |
|------|----------|
| [architecture.md](docs/architecture.md) | System design, app structure, data flow |
| [apps.md](docs/apps.md) | Each Django app — models, views, URLs |
| [api.md](docs/api.md) | REST endpoints and API reference |
| [setup.md](docs/setup.md) | Full installation and configuration guide |
| [roles.md](docs/roles.md) | User roles and permission matrix |

---

## Tech Stack

- **Backend:** Django 4.x, Python 3.11+
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **AI:** Google Gemini API (`gemini-2.0-flash`)
- **Frontend:** Vanilla JS, CSS3, Font Awesome, Chart.js
- **Auth:** Django's built-in auth + custom RBAC
- **Healthcare Standards:** FHIR R4, HL7 v2
- **Environment:** `python-dotenv`, `django-environ`

---

## Project Structure

```
Health-Sphere/
├── healthsphere/          # Django project root
│   ├── config/            # Settings, WSGI, ASGI, URLs
│   ├── users/             # Auth, roles, profiles
│   ├── admin_portal/      # Hospital administration
│   ├── patient_portal/    # Patient self-service
│   ├── clinical_portal/   # Doctor/clinical workflows
│   ├── appointments/      # Scheduling system
│   ├── prescriptions/     # E-prescriptions
│   ├── analytics/         # Dashboards and reporting
│   ├── interoperability/  # FHIR, HL7, external systems
│   ├── ai_services/       # Gemini AI integration
│   ├── telemedicine/      # Video consultations
│   ├── templates/         # All HTML templates
│   └── static/            # CSS, JS, images
├── docs/                  # Project documentation
└── README.md
```

---

## License

MIT © HealthSphere AI
