"""
HealthSphere AI - Appointment Management URLs
============================================

URL patterns for appointment scheduling and management.
"""

from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Appointment list and calendar views
    path('', views.AppointmentListView.as_view(), name='list'),
    path('calendar/', views.AppointmentCalendarView.as_view(), name='calendar'),
    
    # Appointment CRUD operations
    path('create/', views.AppointmentCreateView.as_view(), name='create'),
    path('<int:pk>/', views.AppointmentDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.AppointmentDeleteView.as_view(), name='delete'),
    
    # Appointment status management
    path('<int:pk>/confirm/', views.appointment_confirm, name='confirm'),
    path('<int:pk>/cancel/', views.appointment_cancel, name='cancel'),
    path('<int:pk>/start/', views.appointment_start, name='start'),
    path('<int:pk>/complete/', views.appointment_complete, name='complete'),
    
    # Doctor schedule management
    path('schedule/', views.DoctorScheduleView.as_view(), name='schedule'),
    path('schedule/create/', views.DoctorScheduleCreateView.as_view(), name='schedule_create'),
    path('schedule/<int:pk>/edit/', views.DoctorScheduleUpdateView.as_view(), name='schedule_update'),
    path('schedule/<int:pk>/delete/', views.DoctorScheduleDeleteView.as_view(), name='schedule_delete'),
    
    # API endpoints for AJAX requests
    path('api/available-slots/', views.get_available_slots, name='api_available_slots'),
    path('api/doctor-schedule/', views.get_doctor_schedule, name='api_doctor_schedule'),
]