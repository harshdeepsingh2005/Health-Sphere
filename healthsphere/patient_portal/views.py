"""
HealthSphere AI - Patient Portal Views
======================================

Views for the patient self-service portal.
Provides health management, appointments, and AI insights.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.db.models import Avg, Max, Min, Q
from django.utils import timezone
from django.http import JsonResponse

from .models import PatientProfile, HealthMetric
from clinical_portal.models import MedicalRecord, TreatmentPlan, VitalRecord
from appointments.models import Appointment, AppointmentType
from prescriptions.models import Prescription

# Import AI services (Gemini-powered)
from ai_services.risk_service import predict_risk, get_risk_factors
from ai_services.report_explainer import explain_report, simplify_medical_terms
from ai_services.journey_service import get_patient_journey_summary, get_patient_ai_insights


def patient_required(view_func):
    """
    Decorator to restrict access to patients only.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        if not request.user.is_patient:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('users:redirect_after_login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def calculate_health_score(recent_metrics):
    """Calculate overall health score based on recent metrics."""
    if not recent_metrics:
        return 75  # Default score

    score = 0
    metric_count = 0

    for metric in recent_metrics:
        if metric.metric_type == 'weight':
            score += 80 if 18.5 <= metric.value <= 25 else 60
        elif metric.metric_type == 'blood_pressure':
            if metric.value <= 120:
                score += 90
            elif metric.value <= 140:
                score += 70
            else:
                score += 50
        elif metric.metric_type == 'heart_rate':
            if 60 <= metric.value <= 100:
                score += 85
            else:
                score += 65
        else:
            score += 75
        metric_count += 1

    return min(100, max(0, score // metric_count)) if metric_count > 0 else 75


def calculate_health_trend(recent_metrics):
    """Calculate health trend direction."""
    metrics_list = list(recent_metrics)
    if len(metrics_list) < 2:
        return 'stable'
    recent_score = calculate_health_score(metrics_list[:3])
    older_score = calculate_health_score(metrics_list[3:6])
    if recent_score > older_score + 5:
        return 'improving'
    elif recent_score < older_score - 5:
        return 'declining'
    return 'stable'


def calculate_wellness_streak(user):
    """Calculate consecutive days of logged health metrics."""
    today = timezone.now().date()
    streak = 0
    for i in range(30):
        check_date = today - timezone.timedelta(days=i)
        if HealthMetric.objects.filter(patient=user, recorded_at__date=check_date).exists():
            streak += 1
        else:
            break
    return streak



# get_patient_ai_insights is now imported from ai_services.journey_service (Gemini-powered)



# ---------------------------------------------------------------------------
# Primary dashboard (function-based, used by URL)
# ---------------------------------------------------------------------------

@login_required
@patient_required
def patient_dashboard(request):
    """
    Patient Dashboard — connects all real database data.
    """
    try:
        patient_profile = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        patient_profile = PatientProfile.objects.create(user=request.user)

    current_time = timezone.now()
    hour = current_time.hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    # --- Appointments (from appointments app) ---
    upcoming_appointments = Appointment.objects.filter(
        patient=request.user,
        scheduled_date__gte=timezone.now().date(),
        status__in=['requested', 'confirmed']
    ).select_related('doctor', 'appointment_type').order_by('scheduled_date', 'scheduled_time')[:5]

    # --- Prescriptions ---
    active_prescriptions = Prescription.objects.filter(
        patient=request.user,
        status__in=['approved', 'filled', 'transmitted']
    ).select_related('medication', 'prescriber').order_by('-effective_date')[:5]

    # --- Vitals ---
    latest_vitals = VitalRecord.objects.filter(
        patient=request.user
    ).order_by('-recorded_at').first()

    # --- Recent medical records ---
    recent_records = MedicalRecord.objects.filter(
        patient=request.user
    ).order_by('-record_date')[:3]

    # --- Active treatment plans ---
    active_treatments = TreatmentPlan.objects.filter(
        patient=request.user,
        status='active'
    ).select_related('created_by')[:3]

    # --- Health metrics ---
    recent_metrics = HealthMetric.objects.filter(
        patient=request.user,
        recorded_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).order_by('-recorded_at')[:10]

    health_score = calculate_health_score(recent_metrics)
    health_trend = calculate_health_trend(recent_metrics)
    wellness_streak = calculate_wellness_streak(request.user)

    weight_metrics = HealthMetric.objects.filter(
        patient=request.user,
        metric_type='weight',
        recorded_at__gte=timezone.now() - timezone.timedelta(days=90)
    ).order_by('recorded_at')[:12]

    # --- AI insights ---
    ai_insights = get_patient_ai_insights(request.user)
    risk_assessment = predict_risk(request.user)
    health_journey = get_patient_journey_summary(request.user)

    # Lab results count
    lab_count = MedicalRecord.objects.filter(
        patient=request.user,
        record_type__in=['lab_result', 'imaging']
    ).count()

    # --- Active admission status ---
    from admin_portal.models import AdmissionRecord as AR
    active_admission = AR.objects.filter(
        patient=request.user, status='admitted'
    ).order_by('-admission_date').first()

    context = {
        'patient_profile': patient_profile,
        'greeting': greeting,
        'user_name': request.user.get_full_name() or request.user.username,
        'health_score': health_score,
        'health_trend': health_trend,
        'wellness_streak': wellness_streak,
        'upcoming_appointments': upcoming_appointments,
        'next_appointment': upcoming_appointments.first() if upcoming_appointments else None,
        'active_prescriptions': active_prescriptions,
        'latest_vitals': latest_vitals,
        'recent_records': recent_records,
        'active_treatments': active_treatments,
        'recent_metrics': recent_metrics,
        'weight_metrics': weight_metrics,
        'ai_insights': ai_insights,
        'risk_assessment': risk_assessment,
        'health_journey': health_journey,
        'lab_count': lab_count,
        'current_time': current_time,
        'active_admission': active_admission,
        'page_title': 'My Health Dashboard',
    }

    return render(request, 'patient_portal/dashboard.html', context)


# ---------------------------------------------------------------------------
# Class-based Dashboard (kept for compatibility)
# ---------------------------------------------------------------------------

@method_decorator([login_required, patient_required], name='dispatch')
class DashboardView(View):
    template_name = 'patient_portal/dashboard.html'

    def get(self, request):
        return patient_dashboard(request)


# ---------------------------------------------------------------------------
# Report Upload
# ---------------------------------------------------------------------------

@method_decorator([login_required, patient_required], name='dispatch')
class ReportUploadView(View):
    template_name = 'patient_portal/report.html'

    def get(self, request):
        from .forms import ReportUploadForm
        uploaded_records = MedicalRecord.objects.filter(
            patient=request.user,
            record_type__in=['lab_result', 'imaging']
        ).order_by('-record_date')[:10]
        form = ReportUploadForm()
        return render(request, self.template_name, {'form': form, 'uploaded_records': uploaded_records})

    def post(self, request):
        from .forms import ReportUploadForm
        form = ReportUploadForm(request.POST, request.FILES)
        if form.is_valid():
            report_text = form.cleaned_data.get('report_text', '')
            explanation = explain_report(report_text)
            simplified_terms = simplify_medical_terms(report_text)
            messages.success(request, 'Your report has been analyzed successfully.')
            return render(request, self.template_name, {
                'form': ReportUploadForm(),
                'explanation': explanation,
                'simplified_terms': simplified_terms,
                'original_text': report_text,
            })
        return render(request, self.template_name, {'form': form})


# ---------------------------------------------------------------------------
# Risk Score
# ---------------------------------------------------------------------------

@method_decorator([login_required, patient_required], name='dispatch')
class RiskScoreView(View):
    template_name = 'patient_portal/risk.html'

    def get(self, request):
        patient = request.user
        recent_vitals = VitalRecord.objects.filter(patient=patient).order_by('-recorded_at').first()
        recent_metrics = HealthMetric.objects.filter(patient=patient).order_by('-recorded_at')[:20]
        medical_history = MedicalRecord.objects.filter(patient=patient).order_by('-record_date')[:10]

        patient_data = {
            'patient': patient,
            'vitals': recent_vitals,
            'metrics': list(recent_metrics),
            'history': list(medical_history),
        }

        risk_assessment = predict_risk(patient_data)
        risk_factors = get_risk_factors(patient_data)

        weight_trend = HealthMetric.objects.filter(
            patient=patient, metric_type='weight'
        ).order_by('recorded_at')[:30]

        context = {
            'risk_assessment': risk_assessment,
            'risk_factors': risk_factors,
            'recent_vitals': recent_vitals,
            'weight_trend': list(weight_trend),
            'recommendations': risk_assessment.get('recommendations', []),
        }
        return render(request, self.template_name, context)


# ---------------------------------------------------------------------------
# Appointments — now querying appointments.models.Appointment
# ---------------------------------------------------------------------------

@method_decorator([login_required, patient_required], name='dispatch')
class AppointmentPlannerView(View):
    template_name = 'patient_portal/appointments.html'

    def get(self, request):
        patient = request.user
        today = timezone.now().date()

        upcoming = Appointment.objects.filter(
            patient=patient,
            scheduled_date__gte=today,
        ).exclude(status__in=['cancelled', 'completed']).select_related(
            'doctor', 'appointment_type'
        ).order_by('scheduled_date', 'scheduled_time')

        past = Appointment.objects.filter(
            patient=patient,
        ).filter(
            Q(scheduled_date__lt=today) | Q(status__in=['completed', 'cancelled', 'no_show'])
        ).select_related('doctor', 'appointment_type').order_by('-scheduled_date')[:15]

        context = {
            'upcoming_appointments': upcoming,
            'past_appointments': past,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Redirect to the dedicated booking view."""
        return redirect('patient_portal:book_appointment')


# ---------------------------------------------------------------------------
# AI Assistant
# ---------------------------------------------------------------------------

@method_decorator([login_required, patient_required], name='dispatch')
class AIAssistantView(View):
    template_name = 'patient_portal/assistant.html'

    def get(self, request):
        from ai_services.gemini_client import is_available, quota_status
        from ai_services.risk_service import predict_risk
        from ai_services.journey_service import get_patient_ai_insights

        user = request.user
        qs = quota_status()

        # Real patient data for context panels
        recent_vitals = VitalRecord.objects.filter(patient=user).order_by('-recorded_at').first()
        active_treatment = TreatmentPlan.objects.filter(patient=user, status='active').first()
        upcoming_appointments = Appointment.objects.filter(
            patient=user,
            scheduled_date__gte=timezone.now().date(),
            status__in=['requested', 'confirmed']
        ).order_by('scheduled_date')[:3]
        active_prescriptions = Prescription.objects.filter(
            patient=user,
            status__in=['approved', 'filled', 'transmitted']
        ).order_by('-effective_date')[:4]

        risk_data = predict_risk(user)
        ai_insights = get_patient_ai_insights(user)

        # Normalise factors so the template always has a safe 'display_value'
        for f in risk_data.get('factors', []):
            f['display_value'] = f.get('impact') or f.get('value') or f.get('status') or '—'
            f['display_severity'] = f.get('severity') or (
                'high' if (f.get('impact') or '') in ('High',) else
                'medium' if (f.get('impact') or '') in ('Moderate',) else 'low'
            )

        return render(request, self.template_name, {
            'gemini_available': is_available(),
            'gemini_configured': qs['configured'],
            'gemini_quota_exhausted': qs['quota_exhausted'],
            'recent_vitals': recent_vitals,
            'active_treatment': active_treatment,
            'upcoming_appointments': upcoming_appointments,
            'active_prescriptions': active_prescriptions,
            'risk_data': risk_data,
            'ai_insights': ai_insights,
            'quick_questions': [
                "What do my latest vitals mean?",
                "When should I take my medications?",
                "What are the side effects of my treatment?",
                "How can I improve my health score?",
                "What should I eat for my condition?",
                "When is my next appointment?",
                "Explain my risk score to me",
                "Give me 3 tips for better sleep",
            ],
        })




# ---------------------------------------------------------------------------
# Standalone function views
# ---------------------------------------------------------------------------

@login_required
@patient_required
def health_details_view(request):
    """Detailed health metrics and trends."""
    patient = request.user
    recent_metrics = HealthMetric.objects.filter(patient=patient).order_by('-recorded_at')[:20]
    latest_vitals = VitalRecord.objects.filter(patient=patient).order_by('-recorded_at').first()
    weight_history = HealthMetric.objects.filter(
        patient=patient, metric_type='weight'
    ).order_by('-recorded_at')[:12]
    bp_history = HealthMetric.objects.filter(
        patient=patient, metric_type='blood_pressure'
    ).order_by('-recorded_at')[:12]
    context = {
        'recent_metrics': recent_metrics,
        'latest_vitals': latest_vitals,
        'weight_history': weight_history,
        'bp_history': bp_history,
    }
    return render(request, 'patient_portal/health_details.html', context)


@login_required
@patient_required
def book_appointment(request):
    """Book a new appointment."""
    from users.models import User

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        appt_type_id = request.POST.get('appointment_type')
        scheduled_date = request.POST.get('scheduled_date')
        scheduled_time = request.POST.get('scheduled_time')
        reason = request.POST.get('reason', '')

        errors = []
        if not doctor_id:
            errors.append('Please select a doctor.')
        if not appt_type_id:
            errors.append('Please select an appointment type.')
        if not scheduled_date:
            errors.append('Please select a date.')
        if not scheduled_time:
            errors.append('Please select a time.')

        if not errors:
            try:
                doctor = User.objects.get(pk=doctor_id, role__name='doctor')
                appt_type = AppointmentType.objects.get(pk=appt_type_id)
                Appointment.objects.create(
                    patient=request.user,
                    doctor=doctor,
                    appointment_type=appt_type,
                    scheduled_date=scheduled_date,
                    scheduled_time=scheduled_time,
                    duration_minutes=appt_type.duration_minutes,
                    status='requested',
                    reason=reason,
                )
                messages.success(
                    request,
                    f'✅ Appointment requested with Dr. {doctor.get_full_name()} on {scheduled_date} at {scheduled_time}.'
                )
                return redirect('patient_portal:appointments')
            except Exception as e:
                errors.append(f'Could not book appointment: {e}')

        for err in errors:
            messages.error(request, err)

    doctors = User.objects.filter(role__name='doctor').select_related('role')
    appt_types = AppointmentType.objects.filter(is_active=True)
    upcoming = Appointment.objects.filter(
        patient=request.user,
        scheduled_date__gte=timezone.now().date(),
    ).exclude(status='cancelled').select_related('doctor', 'appointment_type').order_by('scheduled_date')[:5]

    context = {
        'doctors': doctors,
        'appointment_types': appt_types,
        'upcoming_appointments': upcoming,
    }
    return render(request, 'patient_portal/book_appointment.html', context)


@login_required
@patient_required
def medications_view(request):
    """Medications: shows both active prescriptions and active treatment plans."""
    active_prescriptions = Prescription.objects.filter(
        patient=request.user,
        status__in=['approved', 'filled', 'transmitted']
    ).select_related('medication', 'prescriber', 'pharmacy').order_by('-effective_date')

    past_prescriptions = Prescription.objects.filter(
        patient=request.user,
        status__in=['expired', 'cancelled', 'denied']
    ).select_related('medication', 'prescriber').order_by('-effective_date')[:10]

    active_treatments = TreatmentPlan.objects.filter(
        patient=request.user,
        status='active'
    ).select_related('created_by').order_by('-created_at')

    past_treatments = TreatmentPlan.objects.filter(
        patient=request.user,
        status__in=['completed', 'cancelled']
    ).select_related('created_by').order_by('-created_at')[:10]

    context = {
        'active_prescriptions': active_prescriptions,
        'past_prescriptions': past_prescriptions,
        'active_treatments': active_treatments,
        'past_treatments': past_treatments,
    }
    return render(request, 'patient_portal/medications.html', context)


@login_required
@patient_required
def health_records_view(request):
    """Health records view."""
    records = MedicalRecord.objects.filter(
        patient=request.user
    ).select_related('created_by').order_by('-record_date')
    return render(request, 'patient_portal/health_records.html', {'records': records})


@login_required
@patient_required
def lab_results_view(request):
    """Lab results view."""
    lab_records = MedicalRecord.objects.filter(
        patient=request.user,
        record_type__in=['lab_result', 'imaging']
    ).select_related('created_by').order_by('-record_date')
    recent_metrics = HealthMetric.objects.filter(
        patient=request.user
    ).order_by('-recorded_at')[:10]
    return render(request, 'patient_portal/lab_results.html', {
        'lab_records': lab_records,
        'recent_metrics': recent_metrics,
    })


@login_required
@patient_required
def chat_doctor_view(request):
    """Chat with doctor view — lists doctors from real appointments."""
    appointments = Appointment.objects.filter(
        patient=request.user,
        status__in=['requested', 'confirmed', 'completed']
    ).select_related('doctor').order_by('-scheduled_date')[:10]
    doctors = list({apt.doctor for apt in appointments if apt.doctor})
    return render(request, 'patient_portal/chat_doctor.html', {
        'appointments': appointments,
        'doctors': doctors,
    })


@login_required
@patient_required
def emergency_contacts_view(request):
    """Emergency contacts view."""
    try:
        patient_profile = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        patient_profile = PatientProfile.objects.create(user=request.user)
    return render(request, 'patient_portal/emergency_contacts.html', {
        'patient_profile': patient_profile,
    })
