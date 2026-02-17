"""
HealthSphere AI - Patient Portal URL Configuration
=================================================

URL patterns for the patient self-service portal.
"""

from django.urls import path
from . import views

# Namespace for the patient portal app
app_name = 'patient_portal'

urlpatterns = [
    # ==========================================================================
    # DASHBOARD
    # ==========================================================================
    
    # Main patient dashboard
    path('dashboard/', views.patient_dashboard, name='dashboard'),
    path('health-details/', views.health_details_view, name='health_details'),
    
    # ==========================================================================
    # APPOINTMENTS
    # ==========================================================================
    
    # Appointment management
    path('appointments/', views.AppointmentPlannerView.as_view(), name='appointments'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    
    # ==========================================================================
    # MEDICATIONS
    # ==========================================================================
    
    # Medication management
    path('medications/', views.medications_view, name='medications'),
    
    # ==========================================================================
    # HEALTH RECORDS
    # ==========================================================================
    
    # Health records and lab results
    path('health-records/', views.health_records_view, name='health_records'),
    path('lab-results/', views.lab_results_view, name='lab_results'),
    
    # ==========================================================================
    # COMMUNICATION
    # ==========================================================================
    
    # Chat with doctor
    path('chat-doctor/', views.chat_doctor_view, name='chat_doctor'),
    path('emergency-contacts/', views.emergency_contacts_view, name='emergency_contacts'),
    
    # ==========================================================================
    # REPORT UPLOAD
    # ==========================================================================
    
    # Upload and analyze medical reports
    path('report/', views.ReportUploadView.as_view(), name='report'),
    
    # ==========================================================================
    # RISK SCORE
    # ==========================================================================
    
    # View health risk assessment
    path('risk/', views.RiskScoreView.as_view(), name='risk'),
    
    # ==========================================================================
    # AI ASSISTANT
    # ==========================================================================
    
    # AI health assistant
    path('ai-assistant/', views.AIAssistantView.as_view(), name='assistant'),
]
