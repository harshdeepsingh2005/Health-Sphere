"""
HealthSphere AI - E-Prescriptions Views
=======================================

Views for the prescriptions management dashboard.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from .models import Prescription, MedicationDatabase, PrescriptionRefill


@login_required
def prescriptions_dashboard(request):
    """E-prescriptions dashboard — connected to real database."""
    user = request.user

    # Build base queryset depending on role
    if user.is_patient:
        base_qs = Prescription.objects.filter(patient=user)
    elif user.is_doctor:
        base_qs = Prescription.objects.filter(prescriber=user)
    else:
        base_qs = Prescription.objects.all()

    # Stats
    active_prescriptions = base_qs.filter(
        status__in=['approved', 'transmitted', 'filled']
    ).select_related('medication', 'patient', 'prescriber', 'pharmacy').order_by('-date_prescribed')

    pending_refills = PrescriptionRefill.objects.filter(
        prescription__in=base_qs,
        status='requested'
    ).count()

    medication_count = MedicationDatabase.objects.count()

    recent_prescriptions = base_qs.select_related(
        'medication', 'patient', 'prescriber', 'pharmacy'
    ).order_by('-date_prescribed')[:10]

    past_prescriptions = base_qs.filter(
        status__in=['expired', 'cancelled', 'denied']
    ).select_related('medication', 'patient', 'prescriber').order_by('-date_prescribed')[:10]

    context = {
        'active_count': active_prescriptions.count(),
        'pending_refills': pending_refills,
        'medication_count': medication_count,
        'active_prescriptions': active_prescriptions[:5],
        'recent_prescriptions': recent_prescriptions,
        'past_prescriptions': past_prescriptions,
    }
    return render(request, 'prescriptions/dashboard.html', context)
