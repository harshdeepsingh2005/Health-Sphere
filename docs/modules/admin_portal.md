# Admin Portal Module Documentation

The `admin_portal` module is designed for hospital administrators to manage hospital resources, track patient admissions, and oversee staff schedules.

## Tech Stack
- **Framework**: Django
- **Models & Database**: SQLite (via Django ORM)
- **Security Check**: Custom `@admin_required` decorator checks `request.user.is_admin()`

## Key Files & Functions

### `models.py`
- **`HospitalResource`**: Tracks physical resources like beds, equipment, and rooms.
  - `is_available()`: Checks if the resource is currently available (not in maintenance or use).
- **`AdmissionRecord`**: Tracks patient admissions and discharges (links patient to hospital stay information).
  - `is_active()`: Returns boolean if the admission is currently active.
  - `length_of_stay()`: Calculates the total days a patient has stayed or stayed previously.
- **`StaffSchedule`**: Manages work schedules for clinical staff (doctors, nurses). Supports shift-based scheduling.

### `views.py`
All views require admin access, often enforced via the `@admin_required` decorator or Django's `UserPassesTestMixin`.
- **`DashboardView`**: Renders the main admin dashboard, showing an overview of resources, admissions, and metrics.
- **`PatientManagementView` & `PatientDetailView`**: Views for managing and displaying the list of registered patients and their individual demographic records.
- **`ResourceMonitoringView`**: Dashboard for administrators to monitor hospital resources and their statuses.
- **`AdmissionsView` & `AdmissionDetailView`**: Manages hospital admissions, filters by status, type, and allows creation of new admission records.
- **`StaffManagementView` & `StaffDetailView`**: Oversees clinical staff, their roles, departments, and schedule summaries.
- **`StaffScheduleView`**: Provides a visual weekly schedule and calendar overview for all staff.
- **`AnalyticsView`**: Acts as a redirect wrapper to send admins to the main unified analytics dashboard.
