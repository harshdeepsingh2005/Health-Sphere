"""
HealthSphere AI - AI Services App Configuration
==============================================
"""

from django.apps import AppConfig


class AiServicesConfig(AppConfig):
    """Configuration for the AI Services application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_services'
    verbose_name = 'AI Services (Simulated)'
