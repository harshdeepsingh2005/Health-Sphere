"""
HealthSphere AI - Admin Portal App Configuration
================================================
"""

from django.apps import AppConfig


class AdminPortalConfig(AppConfig):
    """Configuration for the Admin Portal application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_portal'
    verbose_name = 'Hospital Administration Portal'
