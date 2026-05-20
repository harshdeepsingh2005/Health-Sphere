# Telemedicine Module Documentation

The `telemedicine` module provides the groundwork for virtual consultations, video conferencing, virtual waiting rooms, and remote patient monitoring devices.

## Tech Stack
- **Framework**: Django
- **Future Integration Points**: Designed to integrate real-time WebRTC/messaging channels in the future (implied by models).

## Key Files & Functions

### `models.py`
- **`TelemedicineSession`**: Manages virtual consultations (video/phone) between patients and providers.
  - `is_active()`, `can_start()`, `is_overdue()`: Temporal and state logic for the session window.
  - `start_session()`, `end_session()`: Lifecycle management.
- **`VirtualWaitingRoom`**: Holds patients before the provider joins the call.
  - `wait_time_minutes()`: Measures current wait duration.
- **`TelemedicineMessage`**: Chat model for in-session messaging (text, images, files, clinical notes).
  - `mark_as_read()`: Read receipt mechanism.
- **`RemoteMonitoringDevice`**: Tracks IoT medical devices distributed to patients (BP monitors, glucose meters, pulse oximeters, smartwatches).
  - `needs_calibration()`, `is_online()`: Hardware status checks.

### `views.py`
- **`telemedicine_dashboard`**: A placeholder view returning the telemedicine dashboard template, currently serving as a landing page for future dynamic telemedicine features.
