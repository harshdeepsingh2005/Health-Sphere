"""
HealthSphere AI - Clinical Portal URL Configuration
==================================================

URL patterns for the clinical portal (doctors and nurses).
"""

from django.urls import path
from . import views

# Namespace for the clinical portal app
app_name = 'clinical_portal'

urlpatterns = [
    # ==========================================================================
    # DASHBOARD
    # ==========================================================================
    
    # Main clinical dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # ==========================================================================
    # RISK INSIGHTS
    # ==========================================================================
    
    # AI-powered risk assessment
    path('risk/', views.RiskInsightsView.as_view(), name='risk'),
    
    # ==========================================================================
    # TREATMENT JOURNEY
    # ==========================================================================
    
    # Patient treatment journey visualization
    path('journey/', views.TreatmentJourneyView.as_view(), name='journey'),
    
    # ==========================================================================
    # TRIAGE
    # ==========================================================================
    
    # Emergency triage dashboard
    path('triage/', views.TriageDashboardView.as_view(), name='triage'),
]
