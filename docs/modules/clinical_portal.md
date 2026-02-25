# Clinical Portal Module Documentation

The `clinical_portal` module is designed for doctors and nurses. It handles medical records, treatment plans, vital sign tracking, and integrates directly with the AI services for diagnostic and triage assistance.

## Tech Stack
- **Framework**: Django
- **Access Control**: Custom `@clinical_staff_required` decorator verifying `User.is_clinical_staff()`.
- **Integrations**: Heavily integrated with `ai_services` (`diagnostic_ai`, `triage_service`, `journey_service`).

## Key Files & Functions

### `models.py`
- **`MedicalRecord`**: Core model storing patient medical history, clinical notes, lab results, and imaging reports. Created by clinical staff during encounters.
- **`TreatmentPlan`**: Defines prescriptions, procedures, and follow-up care instructions.
  - `is_active()`: Checks date boundaries to see if the treatment is ongoing.
  - `duration_days()`: Subtracts start from end date.
- **`VitalRecord`**: Records patient vital signs measurements (BP, heart rate, temperature, weight, O2).
  - `blood_pressure()`: Returns formatted BP string (systolic/diastolic).
  - `bmi()`: Calculates standard Body Mass Index if weight and height are provided.

### `views.py`
All views require clinical staff access.
- **`DashboardView`**: The primary hub showing recent activities, patient overview, and quick actions.
- **`RiskInsightsView`**: Displays AI-powered patient risk assessments (powered by `risk_service`).
- **`TreatmentJourneyView`**: Visualizes a patient's treatment journey, timelines, and milestones (powered by `journey_service`).
- **`TriageDashboardView`**: Emergency triage support with AI prioritization based on severity (powered by `triage_service`).
- **`PatientListView` & `PatientDetailView`**: Browse registered patients, acts as the gateway to a specific patient's medical records.
- **`MedicalRecordsView` & `RecordDetailView`**: List, filter, create, and view detailed medical records.
- **`TreatmentPlansView` & `TreatmentPlanDetailView`**: Manage active and historical treatment plans and prescriptions.
