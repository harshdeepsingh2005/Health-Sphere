"""
HealthSphere AI - Patient Portal App Configuration
=================================================
"""

from django.apps import AppConfig


class PatientPortalConfig(AppConfig):
    """Configuration for the Patient Portal application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'patient_portal'
    verbose_name = 'Patient Portal'
