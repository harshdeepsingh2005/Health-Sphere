"""
HealthSphere AI - Prescriptions URL Configuration
================================================

URL patterns for e-prescriptions system.
"""

from django.urls import path
from . import views

app_name = 'prescriptions'

urlpatterns = [
    # Prescriptions dashboard
    path('', views.prescriptions_dashboard, name='dashboard'),
]