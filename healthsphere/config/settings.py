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

# =============================================================================
# BASE CONFIGURATION
# =============================================================================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# In a real production environment, this should be stored in environment variables
SECRET_KEY = 'django-insecure-healthsphere-ai-development-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Hosts that are allowed to serve the application
ALLOWED_HOSTS = ['localhost', '127.0.0.1']


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
]

# Combine all apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',           # Security enhancements
    'django.contrib.sessions.middleware.SessionMiddleware',    # Session management
    'django.middleware.common.CommonMiddleware',               # Common HTTP features
    'django.middleware.csrf.CsrfViewMiddleware',              # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Authentication
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
