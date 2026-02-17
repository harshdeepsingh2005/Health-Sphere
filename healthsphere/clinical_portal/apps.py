"""
HealthSphere AI - Clinical Portal App Configuration
==================================================
"""

from django.apps import AppConfig


class ClinicalPortalConfig(AppConfig):
    """Configuration for the Clinical Portal application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clinical_portal'
    verbose_name = 'Clinical Portal (Doctors & Nurses)'
