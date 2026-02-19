"""
HealthSphere AI - Prescriptions App Configuration
===============================================

Application configuration for the E-Prescriptions system.
"""

from django.apps import AppConfig


class PrescriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prescriptions'
    verbose_name = 'E-Prescriptions'
    
    def ready(self):
        """Import signal handlers when the app is ready."""
        try:
            import prescriptions.signals  # noqa
        except ImportError:
            pass
