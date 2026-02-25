# Appointments Module Documentation

The `appointments` module handles scheduling, doctor availability calendars, and automated reminders for the platform.

## Tech Stack
- **Framework**: Django
- **Database**: SQLite
- **Architecture**: Standard Django MVT (Model-View-Template) with class-based views.

## Key Files & Functions

### `models.py`
- **`AppointmentType`**: Defines categories of appointments (Consultation, Follow-up, Telemedicine) along with typical durations and base prices.
- **`DoctorSchedule`**: Defines the weekly availability schedule for doctors, including working hours, break times, and maximum daily appointments.
  - `clean()`: Enforces validation on schedule times (start/end boundaries).
- **`Appointment`**: The core model linking a Patient, Doctor, and Appointment Type. Includes state management (Requested, Confirmed, Completed, Cancelled).
  - `cancel()`, `confirm()`, `complete()`, `start()`: State transition methods.
  - `is_past_due()`, `can_be_cancelled()`, `can_be_rescheduled()`: Business logic helpers regarding temporal rules.
- **`AppointmentReminder`**: Tracks SMS/Email reminders scheduled or sent to patients prior to their appointments.

### `views.py`
Provides CRUD operations for appointments and schedules. Many views override `get_queryset()` to ensure patients only see their own appointments, while doctors/admins see all relevant ones.
- **`AppointmentListView`**: Lists appointments, heavily filtered by the requestor's user role.
- **`AppointmentCalendarView`**: Renders a calendar view for appointments, formatting data to be consumed by front-end calendar libraries.
- **`AppointmentCreateView`, `AppointmentUpdateView`, `AppointmentDeleteView`**: Django generic edit views enforcing access control.
- **`DoctorScheduleView`**, **`DoctorScheduleCreateView`**, **`DoctorScheduleUpdateView`**, **`DoctorScheduleDeleteView`**: Views for managing clinical staff's recurring availability charts.
