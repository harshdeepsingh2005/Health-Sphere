"""
HealthSphere AI - Users App Configuration
=========================================
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration for the Users application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'User Management'
    
    def ready(self):
        """
        Called when the app is ready.
        This is a good place to import signals.
        """
        pass  # Add signal imports here if needed
