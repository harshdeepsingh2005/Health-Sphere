#!/usr/bin/env python
"""
HealthSphere AI - Django Management Script
==========================================

This is the main entry point for Django management commands.
Run with: python manage.py <command>

Common commands:
- runserver: Start development server
- migrate: Apply database migrations
- createsuperuser: Create admin user
- makemigrations: Create new migrations
"""
import os
import sys


def main():
    """Run administrative tasks."""
    # Set the default settings module for Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
