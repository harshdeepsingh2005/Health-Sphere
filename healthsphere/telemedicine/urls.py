"""
HealthSphere AI - Telemedicine URL Configuration
===============================================

URL patterns for telemedicine platform.
"""

from django.urls import path
from . import views

app_name = 'telemedicine'

urlpatterns = [
    # Telemedicine dashboard
    path('', views.telemedicine_dashboard, name='dashboard'),
]