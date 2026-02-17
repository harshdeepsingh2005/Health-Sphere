"""
HealthSphere AI - Admin Portal URL Configuration
================================================

URL patterns for the hospital administration portal.
"""

from django.urls import path
from . import views

# Namespace for the admin portal app
app_name = 'admin_portal'

urlpatterns = [
    # ==========================================================================
    # DASHBOARD
    # ==========================================================================
    
    # Main admin dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # ==========================================================================
    # PATIENT MANAGEMENT
    # ==========================================================================
    
    # Patient list and management
    path('patients/', views.PatientManagementView.as_view(), name='patients'),
    
    # ==========================================================================
    # RESOURCE MANAGEMENT
    # ==========================================================================
    
    # Resource monitoring
    path('resources/', views.ResourceMonitoringView.as_view(), name='resources'),
    
    # ==========================================================================
    # ANALYTICS
    # ==========================================================================
    
    # Analytics dashboard
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
]
