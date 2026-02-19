"""
Vercel Serverless Entry Point for HealthSphere AI (Django)
==========================================================
This file is the serverless function entry point for Vercel.
It adds the 'healthsphere' Django project directory to the Python path
so that Django's settings module can be resolved correctly.
"""

import sys
import os
from pathlib import Path

# Add the 'healthsphere' directory (where manage.py lives) to sys.path
# so `config.settings`, `config.urls`, etc. can all be imported.
healthsphere_dir = Path(__file__).resolve().parent.parent / "healthsphere"
sys.path.insert(0, str(healthsphere_dir))

# Point Django at the correct settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Import and expose the WSGI application
from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()

# Vercel expects a callable named 'app' or 'application' at module level
app = application
