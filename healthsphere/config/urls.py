"""
HealthSphere AI - Main URL Configuration
========================================

This file defines the URL routing for the entire HealthSphere AI platform.
Each portal (Admin, Clinical, Patient) has its own URL namespace.

URL Structure:
- /                 → Landing page / Login redirect
- /users/           → Authentication (login, logout, profile)
- /admin-portal/    → Hospital administration portal
- /clinical/        → Doctor/Nurse clinical portal
- /patient/         → Patient portal
- /django-admin/    → Django built-in admin site
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from . import views as config_views


urlpatterns = [
    # ==========================================================================
    # HOME / ROOT URL
    # ==========================================================================
    # Redirect root URL to login page
    path('', RedirectView.as_view(url='/users/login/', permanent=False), name='home'),
    
    # ==========================================================================
    # DJANGO ADMIN (Built-in)
    # ==========================================================================
    # Using 'django-admin' to avoid confusion with our admin_portal
    path('django-admin/', admin.site.urls),
    
    # ==========================================================================
    # USER AUTHENTICATION
    # ==========================================================================
    path('users/', include('users.urls', namespace='users')),
    
    # ==========================================================================
    # ADMIN PORTAL (Hospital Administration)
    # ==========================================================================
    path('admin-portal/', include('admin_portal.urls', namespace='admin_portal')),
    
    # ==========================================================================
    # CLINICAL PORTAL (Doctors & Nurses)
    # ==========================================================================
    path('clinical/', include('clinical_portal.urls', namespace='clinical_portal')),
    
    # ==========================================================================
    # PATIENT PORTAL
    # ==========================================================================
    path('patient/', include('patient_portal.urls', namespace='patient_portal')),
    
    # ==========================================================================
    # APPOINTMENT MANAGEMENT
    # ==========================================================================
    path('appointments/', include('appointments.urls', namespace='appointments')),
    
    # ==========================================================================
    # E-PRESCRIPTIONS SYSTEM
    # ==========================================================================
    path('prescriptions/', include('prescriptions.urls', namespace='prescriptions')),
    
    # ==========================================================================
    # TELEMEDICINE PLATFORM
    # ==========================================================================
    path('telemedicine/', include('telemedicine.urls', namespace='telemedicine')),
    
    # ==========================================================================
    # PREDICTIVE ANALYTICS
    # ==========================================================================
    path('analytics/', include('analytics.urls', namespace='analytics')),
    
    # ==========================================================================
    # HEALTHCARE INTEROPERABILITY (FHIR/HL7)
    # ==========================================================================
    path('interoperability/', include('interoperability.urls', namespace='interoperability')),

    # ==========================================================================
    # AI SERVICES
    # ==========================================================================
    path('ai/', include('ai_services.urls', namespace='ai')),

    # Global site search (placeholder)
    path('search/', config_views.search, name='search'),
    # Global settings (placeholder)
    path('settings/', config_views.settings, name='settings'),
]

# =============================================================================
# STATIC AND MEDIA FILES (Development Only)
# =============================================================================
# In production, these would be served by a web server like Nginx
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# =============================================================================
# CUSTOMIZE DJANGO ADMIN SITE
# =============================================================================
admin.site.site_header = 'HealthSphere AI Administration'
admin.site.site_title = 'HealthSphere AI'
admin.site.index_title = 'System Administration'
