# Patient Portal Module Documentation

The `patient_portal` module provides self-service features for patients. It allows users to view their medical records, self-report health metrics, upload external reports, process AI-driven insights, and book appointments.

## Tech Stack
- **Framework**: Django
- **Access Control**: Custom `@patient_required` decorator verifying `User.is_patient()`.
- **Integrations**: Syncs with `appointments` (bookings) and `ai_services` (report translation and insights).

## Key Files & Functions

### `models.py`
- **`PatientProfile`**: Extended profile information unique to patients (blood type, allergies, emergency contacts, insurance details), supplementing the core `UserProfile`.
- **`Appointment`**: Legacy/patient-scoped appointment model (though the app is moving to query `appointments.models.Appointment` directly for centralized booking).
  - `datetime()`, `is_upcoming()`, `is_today()`: Temporal helpers.
- **`HealthMetric`**: Stores self-reported health data (weight, blood glucose, blood pressure) entered by patients to track trends over time.

### `views.py`
Views are restricted to patients via the `@patient_required` decorator.
- **`patient_dashboard`**: The main function-based view serving the dashboard. Fetches appointments, treatment plans, and calculates health scores.
- Helper Functions:
  - `calculate_health_score()`: Derives a score from recent vitals.
  - `calculate_health_trend()`: Determines if health metrics are improving or declining.
  - `calculate_wellness_streak()`: Calculates consecutive days the patient has interacted/logged data.
- **`ReportUploadView`**: Allows patients to upload PDF medical reports. It uses AI (`report_explainer`) to extract text and generate a patient-friendly summary.
- **`RiskScoreView`**: Translates complex clinical risk assessments into an easy-to-understand score for the patient.
- **`AppointmentPlannerView` & `book_appointment`**: Interfaces for scheduling and managing consultations.
- **`AIAssistantView`**: Conversational interface for the patient.
- **`health_details_view` & `medications_view`**: Dedicated pages for charting trends and listing active prescriptions.
