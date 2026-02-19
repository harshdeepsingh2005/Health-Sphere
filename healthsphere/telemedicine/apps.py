"""
HealthSphere AI - Telemedicine App Configuration
==============================================

Application configuration for telemedicine and remote monitoring system.
"""

from django.apps import AppConfig


class TelemedicineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telemedicine'
    verbose_name = 'Telemedicine & Remote Monitoring'
    
    def ready(self):
        """Import signal handlers when the app is ready."""
        try:
            import telemedicine.signals  # noqa
        except ImportError:
            pass
