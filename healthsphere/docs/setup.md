# HealthSphere AI - Setup Guide

## Prerequisites

Before setting up HealthSphere AI, ensure you have:

- Python 3.9 or higher
- pip (Python package manager)
- Git (optional, for cloning)
- A terminal/command prompt

## Quick Start

### 1. Clone or Download the Project

```bash
# Clone the repository
git clone https://github.com/yourusername/Health-Sphere.git

# Navigate to project directory
cd Health-Sphere/healthsphere
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up the Database

```bash
# Create database tables
python manage.py migrate

# Create a superuser (admin account)
python manage.py createsuperuser
```

### 5. Create Initial Data (Optional)

```bash
# Open Django shell
python manage.py shell

# Run these commands to create roles
from users.models import Role
Role.objects.create(name='admin', description='Hospital Administrator')
Role.objects.create(name='doctor', description='Medical Doctor')
Role.objects.create(name='nurse', description='Nursing Staff')
Role.objects.create(name='patient', description='Patient')
exit()
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

### 7. Access the Application

Open your browser and go to:
- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

---

## Configuration

### Database Settings

By default, HealthSphere AI uses SQLite. The database file is created at:
```
healthsphere/db.sqlite3
```

To use a different database (PostgreSQL, MySQL), modify `config/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'healthsphere_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Static Files

For development, static files are served automatically. For production:

```bash
python manage.py collectstatic
```

### Secret Key

For production, change the secret key in `config/settings.py`:

```python
SECRET_KEY = 'your-new-secret-key-here'
```

Generate a new key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Creating Test Users

### Using Django Admin

1. Log in to http://127.0.0.1:8000/admin/ with your superuser account
2. Go to Users → Add User
3. Fill in the details and select a role

### Using Django Shell

```bash
python manage.py shell
```

```python
from users.models import User, Role

# Get roles
admin_role = Role.objects.get(name='admin')
doctor_role = Role.objects.get(name='doctor')
patient_role = Role.objects.get(name='patient')

# Create admin user
admin_user = User.objects.create_user(
    username='admin1',
    email='admin@example.com',
    password='password123',
    first_name='John',
    last_name='Admin',
    role=admin_role
)

# Create doctor user
doctor_user = User.objects.create_user(
    username='doctor1',
    email='doctor@example.com',
    password='password123',
    first_name='Sarah',
    last_name='Smith',
    role=doctor_role
)

# Create patient user
patient_user = User.objects.create_user(
    username='patient1',
    email='patient@example.com',
    password='password123',
    first_name='Mike',
    last_name='Johnson',
    role=patient_role
)

exit()
```

---

## Project Structure Quick Reference

```
healthsphere/
├── config/           # Project settings
├── users/            # Authentication app
├── admin_portal/     # Hospital admin app
├── clinical_portal/  # Doctor/Nurse app
├── patient_portal/   # Patient app
├── ai_services/      # AI services (mocked)
├── templates/        # HTML templates
├── static/           # CSS, JavaScript
├── docs/             # Documentation
├── manage.py         # Django CLI
└── requirements.txt  # Dependencies
```

---

## Common Commands

```bash
# Run development server
python manage.py runserver

# Make migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Open Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic

# Run tests (if implemented)
python manage.py test
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'django'"
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

### "No such table" errors
- Run `python manage.py migrate`

### Static files not loading
- Check `STATIC_URL` and `STATICFILES_DIRS` in settings
- Run `python manage.py collectstatic`

### Can't create superuser
- Ensure database is migrated: `python manage.py migrate`

### Role-based redirect not working
- Ensure roles exist in database
- Check user has a role assigned

---

## Development Tips

### Adding New Features
1. Create/modify models in the appropriate app
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`
4. Add/modify views and templates
5. Update URLs as needed

### Adding New AI Service
1. Create a new file in `ai_services/`
2. Import and use in views
3. Mock data for demonstration

### Customizing Templates
1. Modify base templates for global changes
2. Override specific blocks in child templates
3. Keep CSS in `static/css/styles.css`

---

## Production Deployment Checklist

- [ ] Set `DEBUG = False` in settings
- [ ] Change `SECRET_KEY` to a secure value
- [ ] Configure production database
- [ ] Set `ALLOWED_HOSTS`
- [ ] Run `collectstatic`
- [ ] Set up HTTPS
- [ ] Configure proper web server (Gunicorn/uWSGI)
- [ ] Set up reverse proxy (Nginx/Apache)
- [ ] Enable database backups
- [ ] Set up logging
- [ ] Configure email settings

---

## Support

For questions or issues:
1. Check this documentation
2. Review Django documentation: https://docs.djangoproject.com/
3. Check for common errors in troubleshooting section

---

## License

This project is for educational purposes. See LICENSE file for details.
