# Users Module Documentation

The `users` module handles authentication, role-based access control, user profiles, and security compliance (HIPAA auditing) for the HealthSphere platform.

## Tech Stack
- **Framework**: Django
- **Database**: SQLite (default Django ORM)
- **Authentication**: Django standard authentication (`AbstractUser`), Custom Roles.
- **Security**: `pyotp` (for Two-Factor Authentication TOTP), custom middleware for 2FA enforcement and Audit Logging.

## Key Files & Functions

### `models.py`
- **`Role`**: Defines roles like Admin, Doctor, Nurse, Patient to determine portal access.
- **`User`**: Custom user model extending `AbstractUser`.
  - `is_admin()`, `is_doctor()`, `is_nurse()`, `is_patient()`, `is_clinical_staff()`: Role checking helpers.
  - `get_dashboard_url()`: Returns corresponding dashboard URL path based on the user's role.
- **`UserProfile`**: Stores extended demographic and medical information.
- **`TwoFactorAuth`**: Handles 2FA settings and backup codes.
  - `generate_backup_codes()`: Creates recovery codes.
  - `generate_qr_code()`: Generates QR code for authenticator apps.
  - `verify_token()`: Verifies TOTP tokens.
- **`AuditLog`**: Tracks all user actions (LOGIN, CREATE, UPDATE, etc.) for HIPAA compliance.

### `views.py`
- **`LoginView`**: Display and process the login form.
- **`LogoutView`**: Handle user logout.
- **`RegisterView`**: Handle new patient registrations and send welcome emails.
- **`redirect_after_login`**: Helper view that dynamically routes authenticated users to their specific portal dashboard based on role.
- **`ProfileView`**: View and update the current user's profile.
- **`TwoFactorSetupView`**: Setup page for enabling/disabling 2FA and generating QR codes.
- **`TwoFactorVerifyView`**: Page to verify 2FA token upon login if enabled.
- **`AuditLogView`**: Dashboard for administrators to view compliance logs.

### `middleware.py`
- **`TwoFactorAuthMiddleware`**: Enforces 2FA check on every request for users who have it enabled, redirecting them to the verification page if necessary.
- **`AuditLogMiddleware`**: Automatically logs user actions for audit purposes by intercepting HTTP requests (`POST`, `PUT`, `DELETE`, etc.), capturing the IP address, user agent, and resource type.
