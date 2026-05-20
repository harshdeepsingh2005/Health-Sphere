"""
HealthSphere AI - Interoperability URL Configuration
====================================================

URL patterns for healthcare interoperability management and monitoring.
Includes both web interface and API endpoints for FHIR/HL7 integration.
"""

from django.urls import path, include
from . import views

app_name = 'interoperability'

# Web interface URLs
urlpatterns = [
    # Dashboard and overview
    path('', views.interoperability_dashboard, name='dashboard'),
    
    # External systems management
    path('systems/', views.external_systems_list, name='external_systems_list'),
    path('systems/<int:system_id>/', views.external_system_detail, name='external_system_detail'),
    path('systems/<int:system_id>/test/', views.test_system_connection, name='test_system_connection'),
    
    # FHIR resources
    path('fhir/', views.fhir_resources_list, name='fhir_resources_list'),
    path('fhir/<int:resource_id>/', views.fhir_resource_detail, name='fhir_resource_detail'),
    
    # HL7 messages
    path('hl7/', views.hl7_messages_list, name='hl7_messages_list'),
    path('hl7/<int:message_id>/', views.hl7_message_detail, name='hl7_message_detail'),
    path('hl7/<int:message_id>/reprocess/', views.reprocess_hl7_message, name='reprocess_hl7_message'),
    
    # Data mappings
    path('mappings/', views.data_mappings_list, name='data_mappings_list'),
    path('mappings/<int:mapping_id>/test/', views.test_data_mapping, name='test_data_mapping'),
    
    # Integration transactions
    path('transactions/', views.integration_transactions_list, name='integration_transactions_list'),
    
    # Consent management
    path('consents/', views.consent_management_list, name='consent_management_list'),
    
    # API endpoints
    path('api/', include([
        # FHIR webhook for external notifications
        path('fhir/webhook/', views.api_fhir_webhook, name='api_fhir_webhook'),
        
        # HL7 message endpoint
        path('hl7/endpoint/', views.api_hl7_endpoint, name='api_hl7_endpoint'),
        
        # System status API
        path('status/', views.api_system_status, name='api_system_status'),
    ])),
]