"""
HealthSphere AI - ASGI Configuration
====================================

ASGI (Asynchronous Server Gateway Interface) is the successor to WSGI,
providing support for asynchronous Python web applications.

This file exposes the ASGI callable as a module-level variable named 'application'.

For more information, see:
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the ASGI application object
application = get_asgi_application()
