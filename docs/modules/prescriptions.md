# Prescriptions Module Documentation

The `prescriptions` module manages electronic prescriptions, medication catalogs, pharmacy integration, and refill requests.

## Tech Stack
- **Framework**: Django
- **Database**: SQLite
- **Architecture**: Standard Django models with robust state tracking.

## Key Files & Functions

### `models.py`
- **`MedicationDatabase`**: Digital catalog of medications, ND codes, strength, and formulations.
  - `is_controlled_substance()`: Checks if the drug is schedule II-V.
  - `full_name()`: Returns formatted string combining drug properties.
- **`DrugAllergy`**: Patient drug allergies and adverse reactions to prevent harmful prescribing.
- **`Prescription`**: Electronic prescription record tracking state (draft, approved, transmitted, filled, etc.).
  - `is_expired()`, `has_refills_remaining()`, `can_be_refilled()`: Business logic regarding prescription lifecycle thresholds.
- **`Pharmacy`**: Directory of pharmacies for prescription transmission.
- **`PrescriptionRefill`**: Requests for prescription refills requiring doctor approval.

### `views.py`
- **`prescriptions_dashboard`**: The core dashboard view that aggregates active prescriptions, pending refills, and historical data, filtering access securely based on whether the requester is a doctor or a patient.
