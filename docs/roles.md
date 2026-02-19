# User Roles & Permissions — HealthSphere AI

## Role Overview

HealthSphere uses a custom role-based access control (RBAC) system. Each `User` has a FK to a `Role` object. Roles are stored in `users.Role`.

| Role | Portal Access | Description |
|------|--------------|-------------|
| `admin` | Admin Portal, Analytics, All | Hospital administrator — full system access |
| `doctor` | Clinical Portal, Appointments | Physicians and specialists |
| `nurse` | Clinical Portal (limited) | Nursing staff |
| `patient` | Patient Portal | Self-service patient access |
| `staff` | Admin Portal (limited) | Administrative/reception staff |

---

## Permission Matrix

### Admin Portal (`/admin-portal/`)
| Feature | admin | doctor | nurse | patient | staff |
|---------|-------|--------|-------|---------|-------|
| Dashboard | ✅ | ❌ | ❌ | ❌ | ✅ |
| Patient List | ✅ | ✅ | ✅ | ❌ | ✅ |
| Admission Management | ✅ | ❌ | ❌ | ❌ | ✅ |
| Resource Management | ✅ | ❌ | ❌ | ❌ | ✅ |
| Staff Schedules | ✅ | ❌ | ❌ | ❌ | ❌ |
| Analytics | ✅ | ❌ | ❌ | ❌ | ❌ |

### Patient Portal (`/patient/`)
| Feature | admin | doctor | nurse | patient | staff |
|---------|-------|--------|-------|---------|-------|
| Dashboard | ❌ | ❌ | ❌ | ✅ | ❌ |
| AI Health Assistant | ❌ | ❌ | ❌ | ✅ | ❌ |
| Book Appointment | ❌ | ❌ | ❌ | ✅ | ❌ |
| View Own Records | ❌ | ❌ | ❌ | ✅ | ❌ |
| Report Upload/Analysis | ❌ | ❌ | ❌ | ✅ | ❌ |

### Clinical Portal (`/clinical/`)
| Feature | admin | doctor | nurse | patient | staff |
|---------|-------|--------|-------|---------|-------|
| Patient List | ✅ | ✅ | ✅ | ❌ | ❌ |
| Medical Records | ✅ | ✅ | ✅ | ❌ | ❌ |
| Vitals | ✅ | ✅ | ✅ | ❌ | ❌ |
| Treatment Plans | ✅ | ✅ | ❌ | ❌ | ❌ |
| Create Records | ✅ | ✅ | ❌ | ❌ | ❌ |

### Appointments (`/appointments/`)
| Feature | admin | doctor | nurse | patient | staff |
|---------|-------|--------|-------|---------|-------|
| View Calendar | ✅ | ✅ | ✅ | ✅ | ✅ |
| Book Appointment | ✅ | ❌ | ❌ | ✅ | ✅ |
| Confirm/Cancel | ✅ | ✅ | ✅ | ✅* | ✅ |
| Doctor Availability | ✅ | ✅ | ❌ | ❌ | ✅ |

*Patients can cancel their own appointments only.

### Analytics (`/analytics/`)
| Feature | admin | doctor | nurse | patient | staff |
|---------|-------|--------|-------|---------|-------|
| All dashboards | ✅ | ❌ | ❌ | ❌ | ❌ |

### Interoperability (`/interoperability/`)
| Feature | admin | doctor | nurse | patient | staff |
|---------|-------|--------|-------|---------|-------|
| All pages | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## Implementation Details

### Role Model
```python
# users/models.py
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    # e.g. 'admin', 'doctor', 'nurse', 'patient', 'staff'

class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
```

### Checking Roles in Views
```python
# In a view:
if request.user.role and request.user.role.name == 'admin':
    # admin-only logic

# Or using LoginRequiredMixin:
class SomeView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        if not request.user.role or request.user.role.name not in ['admin', 'staff']:
            raise PermissionDenied
```

### Checking Roles in Templates
```html
{% if request.user.role.name == 'admin' %}
    <a href="{% url 'admin_portal:dashboard' %}">Admin Panel</a>
{% endif %}

{% if request.user.role.name == 'patient' %}
    <a href="{% url 'patient_portal:dashboard' %}">My Health</a>
{% endif %}
```

---

## Creating Users with Roles

### Via Django Admin (`/django-admin/`)
1. Create the user account
2. In the User form, set the `Role` field

### Via Management Command (if available)
```bash
python manage.py shell
>>> from users.models import User, Role
>>> patient_role = Role.objects.get(name='patient')
>>> User.objects.create_user('john_doe', 'john@example.com', 'pass123', role=patient_role)
```

---

## Two-Factor Authentication

Optional 2FA is available via `users.TwoFactorAuth`. When enabled for a user:
1. After password login, user is prompted for a TOTP code
2. On success, session is marked as fully authenticated

---

## Audit Logging

All significant actions (login, record creation, discharge, etc.) are automatically logged to `users.AuditLog`:

```python
# users/models.py
class AuditLog(models.Model):
    user = models.ForeignKey(User, ...)
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=50)
    resource_id = models.IntegerField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)
```
