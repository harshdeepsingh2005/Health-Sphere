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
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # ==========================================================================
    # PATIENT MANAGEMENT
    # ==========================================================================
    path('patients/', views.PatientManagementView.as_view(), name='patients'),
    path('patients/<int:patient_id>/', views.PatientDetailView.as_view(), name='patient_detail'),

    # ==========================================================================
    # RESOURCE MANAGEMENT
    # ==========================================================================
    path('resources/', views.ResourceMonitoringView.as_view(), name='resources'),

    # ==========================================================================
    # ADMISSIONS (P2)
    # ==========================================================================
    path('admissions/', views.AdmissionsView.as_view(), name='admissions'),
    path('admissions/<int:pk>/', views.AdmissionDetailView.as_view(), name='admission_detail'),

    # ==========================================================================
    # STAFF MANAGEMENT (P2)
    # ==========================================================================
    path('staff/', views.StaffManagementView.as_view(), name='staff'),
    path('staff/<int:staff_id>/', views.StaffDetailView.as_view(), name='staff_detail'),
    path('staff/schedule/', views.StaffScheduleView.as_view(), name='staff_schedule'),

    # ==========================================================================
    # ANALYTICS
    # ==========================================================================
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
]
