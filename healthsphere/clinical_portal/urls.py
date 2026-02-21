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
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # ==========================================================================
    # PATIENT LIST (P1)
    # ==========================================================================
    path('patients/', views.PatientListView.as_view(), name='patients'),
    path('patients/<int:patient_id>/', views.PatientDetailView.as_view(), name='patient_detail'),

    # ==========================================================================
    # MEDICAL RECORDS (P1)
    # ==========================================================================
    path('records/', views.MedicalRecordsView.as_view(), name='records'),
    path('records/<int:pk>/', views.RecordDetailView.as_view(), name='record_detail'),

    # ==========================================================================
    # TREATMENT PLANS (P1)
    # ==========================================================================
    path('treatment-plans/', views.TreatmentPlansView.as_view(), name='treatment_plans'),
    path('treatment-plans/<int:pk>/', views.TreatmentPlanDetailView.as_view(), name='treatment_plan_detail'),

    # ==========================================================================
    # VITALS (P1)
    # ==========================================================================
    path('vitals/', views.VitalsView.as_view(), name='vitals'),
    path('vitals/<int:patient_id>/', views.PatientVitalsView.as_view(), name='patient_vitals'),

    # ==========================================================================
    # RISK INSIGHTS
    # ==========================================================================
    path('risk/', views.RiskInsightsView.as_view(), name='risk'),

    # ==========================================================================
    # TREATMENT JOURNEY
    # ==========================================================================
    path('journey/', views.TreatmentJourneyView.as_view(), name='journey'),

    # ==========================================================================
    # TRIAGE
    # ==========================================================================
    path('triage/', views.TriageDashboardView.as_view(), name='triage'),

    # ==========================================================================
    # PATIENT EDIT & DISCHARGE
    # ==========================================================================
    path('patients/<int:patient_id>/edit/', views.EditPatientView.as_view(), name='edit_patient'),
    path('patients/<int:patient_id>/discharge/', views.DischargePatientView.as_view(), name='discharge_patient'),

    # ==========================================================================
    # ADMISSIONS (doctors & nurses)
    # ==========================================================================
    path('admissions/', views.AdmissionsView.as_view(), name='admissions'),
]
