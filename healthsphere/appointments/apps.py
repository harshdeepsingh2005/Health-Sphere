from django.apps import AppConfig


class AppointmentsConfig(AppConfig):
    """
    Appointments App Configuration
    =============================
    
    Configures the appointments app for HealthSphere AI.
    Handles appointment scheduling, management, and reminders.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appointments'
    verbose_name = 'Appointment Management'
    
    def ready(self):
        """Import signals when app is ready."""
        import appointments.signals