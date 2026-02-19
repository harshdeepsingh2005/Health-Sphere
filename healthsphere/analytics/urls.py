"""
HealthSphere AI - Analytics URLs
===============================

URL patterns for the analytics application.
Provides endpoints for predictive analytics, reports, and dashboards.
"""

from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'analytics'

# API patterns for predictive analytics
api_patterns = [
    path('predict/patient-flow/', views.PatientFlowPredictionAPIView.as_view(), name='api_patient_flow'),
    path('predict/clinical-outcome/', views.ClinicalOutcomePredictionAPIView.as_view(), name='api_clinical_outcome'),
    path('reports/generate/', views.GenerateReportAPIView.as_view(), name='api_generate_report'),
    path('quality/assess/', views.DataQualityAssessmentAPIView.as_view(), name='api_data_quality'),
]

# Main URL patterns
urlpatterns = [
    # Dashboard views
    path('', login_required(views.AnalyticsDashboardView.as_view()), name='dashboard'),
    path('patient-flow/', login_required(views.PatientFlowDashboardView.as_view()), name='patient_flow_dashboard'),
    path('clinical-outcomes/', login_required(views.ClinicalOutcomesDashboardView.as_view()), name='clinical_outcomes_dashboard'),
    path('reports/', login_required(views.ReportsDashboardView.as_view()), name='reports_dashboard'),
    path('data-quality/', login_required(views.DataQualityDashboardView.as_view()), name='data_quality_dashboard'),
    
    # Model management
    path('models/', login_required(views.ModelsListView.as_view()), name='models_list'),
    path('models/<int:pk>/', login_required(views.ModelDetailView.as_view()), name='model_detail'),
    
    # Prediction views
    path('predictions/patient-flow/', login_required(views.PatientFlowPredictionsView.as_view()), name='patient_flow_predictions'),
    path('predictions/clinical-outcomes/', login_required(views.ClinicalOutcomePredictionsView.as_view()), name='clinical_outcome_predictions'),
    
    # Report views
    path('reports/<int:pk>/', login_required(views.ReportDetailView.as_view()), name='report_detail'),
    path('reports/<int:pk>/download/', login_required(views.ReportDownloadView.as_view()), name='report_download'),
    
    # API endpoints
    path('api/', include(api_patterns)),
]