"""
HealthSphere AI - Django Settings
=================================

This file contains all Django configuration settings for the HealthSphere AI platform.
It includes settings for database, authentication, static files, and installed apps.

For more information on Django settings, see:
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path

# Load environment variables from .env file (if present)
try:
    from dotenv import load_dotenv
    # settings.py lives at healthsphere/config/settings.py
    # .env lives at the project root (Health-Sphere/)
    load_dotenv(Path(__file__).resolve().parent.parent.parent / '.env')
except ImportError:
    pass  # python-dotenv not installed — use OS environment variables directly



# =============================================================================
# BASE CONFIGURATION
# =============================================================================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Set SECRET_KEY in your .env file.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-healthsphere-ai-development-key-change-in-production'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Hosts that are allowed to serve the application
_allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_env.split(',') if h.strip()]

# Allow all Vercel preview deployment domains automatically
if not DEBUG:
    ALLOWED_HOSTS += ['.vercel.app', '.now.sh']


# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

# Django built-in apps
DJANGO_APPS = [
    'django.contrib.admin',          # Django admin site
    'django.contrib.auth',           # Authentication framework
    'django.contrib.contenttypes',   # Content types framework
    'django.contrib.sessions',       # Session framework
    'django.contrib.messages',       # Messaging framework
    'django.contrib.staticfiles',    # Static files management
]

# Third-party apps (add any external packages here)
THIRD_PARTY_APPS = []

# HealthSphere AI custom apps
LOCAL_APPS = [
    'users.apps.UsersConfig',                    # User management and authentication
    'admin_portal.apps.AdminPortalConfig',       # Hospital administration portal
    'clinical_portal.apps.ClinicalPortalConfig', # Doctor/Nurse clinical portal
    'patient_portal.apps.PatientPortalConfig',   # Patient portal
    'ai_services.apps.AiServicesConfig',         # AI/ML placeholder services
    'appointments.apps.AppointmentsConfig',      # Appointment management system
    'prescriptions.apps.PrescriptionsConfig',    # E-Prescriptions system
    'telemedicine.apps.TelemedicineConfig',      # Telemedicine and remote monitoring
    'analytics.apps.AnalyticsConfig',            # Predictive analytics and insights
    'interoperability.apps.InteroperabilityConfig', # FHIR/HL7 healthcare interoperability
]

# Combine all apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',           # Security enhancements
    'whitenoise.middleware.WhiteNoiseMiddleware',              # Static file serving (Vercel)
    'django.contrib.sessions.middleware.SessionMiddleware',    # Session management
    'django.middleware.common.CommonMiddleware',               # Common HTTP features
    'django.middleware.csrf.CsrfViewMiddleware',              # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Authentication
    'users.middleware.AuditLogMiddleware',                     # Audit logging
    'users.middleware.TwoFactorAuthMiddleware',                # 2FA enforcement
    'django.contrib.messages.middleware.MessageMiddleware',    # Flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Clickjacking protection
]


# =============================================================================
# URL CONFIGURATION
# =============================================================================

ROOT_URLCONF = 'config.urls'


# =============================================================================
# TEMPLATE CONFIGURATION
# =============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Look for templates in the 'templates' directory
        'DIRS': [BASE_DIR / 'templates'],
        # Also look for templates in each app's 'templates' folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Required for auth
                'django.contrib.auth.context_processors.auth', # User context
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# =============================================================================
# WSGI CONFIGURATION
# =============================================================================

WSGI_APPLICATION = 'config.wsgi.application'


# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Using SQLite for simplicity in academic project
# In production, you would use PostgreSQL or MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =============================================================================
# AUTHENTICATION CONFIGURATION
# =============================================================================

# Custom user model for HealthSphere
AUTH_USER_MODEL = 'users.User'

# Password validation rules
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Login/Logout URLs
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'users:redirect_after_login'
LOGOUT_REDIRECT_URL = 'users:login'


# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# =============================================================================
# STATIC FILES CONFIGURATION
# =============================================================================

# URL prefix for static files
STATIC_URL = 'static/'

# Additional directories to look for static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Directory where collectstatic will gather static files (for production)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Use WhiteNoise's compressed manifest storage in production for cache busting
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# =============================================================================
# MEDIA FILES CONFIGURATION
# =============================================================================

# URL prefix for user-uploaded files
MEDIA_URL = 'media/'

# Directory to store uploaded files
MEDIA_ROOT = BASE_DIR / 'media'


# =============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# =============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================================
# HEALTHSPHERE AI CUSTOM SETTINGS
# =============================================================================

# Application name displayed in templates
APP_NAME = 'HealthSphere AI'

# Version number
APP_VERSION = '1.0.0'

# Enable/disable AI features (for demo purposes)
AI_FEATURES_ENABLED = True

# =============================================================================
# GEMINI AI CONFIGURATION
# =============================================================================

# Set your Gemini API key as an environment variable:
#   export GEMINI_API_KEY="your-key-here"
# Or hardcode it here for development (not recommended for production):
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Gemini model to use
# Gemini model to use
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')


# =============================================================================
# EMAIL CONFIGURATION (Gmail SMTP)
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = f'HealthSphere AI <{os.environ.get("EMAIL_HOST_USER", "noreply@healthsphere.ai")}>'
