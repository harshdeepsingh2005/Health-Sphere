"""
HealthSphere AI - WSGI Configuration
====================================

WSGI (Web Server Gateway Interface) is the Python standard for web servers
to communicate with web applications.

This file exposes the WSGI callable as a module-level variable named 'application'.

For more information, see:
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the WSGI application object
application = get_wsgi_application()
