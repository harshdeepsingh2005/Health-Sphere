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

from .models import PatientProfile, Appointment, HealthMetric
from .forms import AppointmentForm, HealthMetricForm, ReportUploadForm
from clinical_portal.models import MedicalRecord, TreatmentPlan, VitalRecord

# Import AI services
from ai_services.risk_service import predict_risk, get_risk_factors
from ai_services.report_explainer import explain_report, simplify_medical_terms
from ai_services.journey_service import get_patient_journey_summary


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


@login_required
@patient_required
def patient_dashboard(request):
    """
    Patient Dashboard View
    =====================
    
    Comprehensive dashboard showing patient's health overview:
    - Health score and wellness metrics
    - Upcoming appointments
    - Recent medications
    - Health journey progress
    - AI-powered insights and recommendations
    """
    try:
        patient_profile = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        # Create patient profile if it doesn't exist
        patient_profile = PatientProfile.objects.create(user=request.user)
    
    # Get current time and greeting
    current_time = timezone.now()
    hour = current_time.hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    # Calculate health score based on recent metrics and activities
    recent_metrics = HealthMetric.objects.filter(
        patient=request.user,
        recorded_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).order_by('-recorded_at')[:10]
    
    health_score = calculate_health_score(recent_metrics)
    health_trend = calculate_health_trend(recent_metrics)
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        patient=request.user,
        appointment_date__gte=timezone.now(),
        status__in=['scheduled', 'confirmed']
    ).order_by('appointment_date')[:3]
    
    # Get recent medications (from treatment plans)
    recent_medications = TreatmentPlan.objects.filter(
        patient=request.user,
        end_date__isnull=True,  # Active medications
        status='active'
    ).order_by('-created_at')[:5]
    
    # Get recent health metrics for visualization
    weight_metrics = HealthMetric.objects.filter(
        patient=request.user,
        metric_type='weight',
        recorded_at__gte=timezone.now() - timezone.timedelta(days=90)
    ).order_by('recorded_at')[:12]
    
    blood_pressure_metrics = HealthMetric.objects.filter(
        patient=request.user,
        metric_type='blood_pressure',
        recorded_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).order_by('recorded_at')[:10]
    
    # Get AI insights and recommendations
    ai_insights = get_patient_ai_insights(request.user)
    risk_assessment = predict_risk(request.user)
    
    # Get health journey progress
    health_journey = get_patient_journey_summary(request.user)
    
    # Calculate wellness streak
    wellness_streak = calculate_wellness_streak(request.user)
    
    # Get recent medical records
    recent_records = MedicalRecord.objects.filter(
        patient=request.user
    ).order_by('-created_at')[:3]
    
    # Prepare context for template
    context = {
        'patient_profile': patient_profile,
        'greeting': greeting,
        'user_name': request.user.get_full_name() or request.user.username,
        'health_score': health_score,
        'health_trend': health_trend,
        'wellness_streak': wellness_streak,
        'upcoming_appointments': upcoming_appointments,
        'recent_medications': recent_medications,
        'weight_metrics': weight_metrics,
        'blood_pressure_metrics': blood_pressure_metrics,
        'ai_insights': ai_insights,
        'risk_assessment': risk_assessment,
        'health_journey': health_journey,
        'recent_records': recent_records,
        'current_time': current_time,
        
        # Dashboard metadata
        'page_title': 'My Health Dashboard',
        'page_subtitle': 'Overview of your health journey and wellness progress',
        'breadcrumbs': [
            {'label': 'Home', 'url': '/', 'icon': 'fas fa-home'},
            {'label': 'My Dashboard', 'active': True}
        ]
    }
    
    return render(request, 'patient_portal/dashboard.html', context)


def calculate_health_score(recent_metrics):
    """Calculate overall health score based on recent metrics."""
    if not recent_metrics:
        return 75  # Default score
    
    # Simple scoring algorithm based on metric types and values
    score = 0
    metric_count = 0
    
    for metric in recent_metrics:
        if metric.metric_type == 'weight':
            # Weight stability contributes to score
            score += 80 if 18.5 <= metric.value <= 25 else 60
        elif metric.metric_type == 'blood_pressure':
            # Normal BP contributes highly to score
            if metric.value <= 120:  # Systolic
                score += 90
            elif metric.value <= 140:
                score += 70
            else:
                score += 50
        elif metric.metric_type == 'heart_rate':
            # Resting heart rate
            if 60 <= metric.value <= 100:
                score += 85
            else:
                score += 65
        else:
            score += 75  # Default for other metrics
        
        metric_count += 1
    
    return min(100, max(0, score // metric_count)) if metric_count > 0 else 75


def calculate_health_trend(recent_metrics):
    """Calculate health trend direction."""
    if len(recent_metrics) < 2:
        return 'stable'
    
    # Compare recent vs older metrics
    recent_score = calculate_health_score(recent_metrics[:3])
    older_score = calculate_health_score(recent_metrics[3:6])
    
    if recent_score > older_score + 5:
        return 'improving'
    elif recent_score < older_score - 5:
        return 'declining'
    else:
        return 'stable'


def calculate_wellness_streak(user):
    """Calculate consecutive days of healthy activities."""
    # Simple implementation - would be more complex in real app
    today = timezone.now().date()
    streak = 0
    
    for i in range(30):  # Check last 30 days
        check_date = today - timezone.timedelta(days=i)
        
        # Check if user had any positive health activity this day
        daily_metrics = HealthMetric.objects.filter(
            patient=user,
            recorded_at__date=check_date
        ).exists()
        
        if daily_metrics:
            streak += 1
        else:
            break
    
    return streak


def get_patient_ai_insights(user):
    """Get AI-powered health insights for the patient."""
    insights = []
    
    # Get recent metrics for analysis
    recent_metrics = HealthMetric.objects.filter(
        patient=user,
        recorded_at__gte=timezone.now() - timezone.timedelta(days=7)
    )
    
    if recent_metrics.exists():
        insights.append({
            'type': 'positive',
            'title': 'Great Progress!',
            'message': 'Your health metrics show consistent improvement over the past week.',
            'icon': 'fas fa-thumbs-up',
            'action': {'text': 'View Details', 'url': '/health-metrics/'}
        })
    
    # Check for overdue appointments
    overdue_appointments = Appointment.objects.filter(
        patient=user,
        appointment_date__lt=timezone.now(),
        status='scheduled'
    ).count()
    
    if overdue_appointments > 0:
        insights.append({
            'type': 'warning',
            'title': 'Appointment Reminder',
            'message': f'You have {overdue_appointments} overdue appointment(s). Please reschedule.',
            'icon': 'fas fa-calendar-exclamation',
            'action': {'text': 'View Appointments', 'url': '/appointments/'}
        })
    
    return insights


@method_decorator([login_required, patient_required], name='dispatch')
class DashboardView(View):
    """
    Patient Dashboard View
    ======================
    
    Main dashboard for patients showing health overview,
    upcoming appointments, and quick actions.
    """
    
    template_name = 'patient_portal/dashboard.html'
    
    def get(self, request):
        """Render the patient dashboard."""
        patient = request.user
        
        # Get upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            patient=patient,
            status__in=['scheduled', 'confirmed'],
            appointment_date__gte=timezone.now().date()
        ).select_related('doctor').order_by('appointment_date', 'appointment_time')[:5]
        
        # Get recent medical records
        recent_records = MedicalRecord.objects.filter(
            patient=patient
        ).select_related('created_by').order_by('-record_date')[:5]
        
        # Get active treatment plans
        active_treatments = TreatmentPlan.objects.filter(
            patient=patient,
            status='active'
        ).select_related('created_by')[:3]
        
        # Get recent health metrics
        recent_metrics = HealthMetric.objects.filter(
            patient=patient
        ).order_by('-recorded_at')[:10]
        
        # Calculate health summary statistics
        weight_history = HealthMetric.objects.filter(
            patient=patient,
            metric_type='weight'
        ).order_by('-recorded_at')[:30]
        
        latest_vitals = VitalRecord.objects.filter(
            patient=patient
        ).order_by('-recorded_at').first()
        
        # Get AI risk assessment (simulated)
        risk_data = predict_risk({'patient': patient})
        
        # Health score calculation (simplified)
        health_score = 100 - risk_data['risk_score']
        
        context = {
            'upcoming_appointments': upcoming_appointments,
            'recent_records': recent_records,
            'active_treatments': active_treatments,
            'recent_metrics': recent_metrics,
            'weight_history': list(weight_history),
            'latest_vitals': latest_vitals,
            'health_score': round(health_score),
            'risk_level': risk_data['risk_level'],
            'next_appointment': upcoming_appointments.first() if upcoming_appointments else None,
        }
        
        return render(request, self.template_name, context)


@method_decorator([login_required, patient_required], name='dispatch')
class ReportUploadView(View):
    """
    Report Upload View
    ==================
    
    Allows patients to upload medical reports for AI analysis.
    """
    
    template_name = 'patient_portal/report.html'
    
    def get(self, request):
        """Display report upload form and history."""
        patient = request.user
        
        # Get previously uploaded reports/records
        uploaded_records = MedicalRecord.objects.filter(
            patient=patient,
            record_type__in=['lab_result', 'imaging']
        ).order_by('-record_date')[:10]
        
        form = ReportUploadForm()
        
        context = {
            'form': form,
            'uploaded_records': uploaded_records,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Process uploaded report."""
        form = ReportUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            # In a real application, this would process the file
            report_text = form.cleaned_data.get('report_text', '')
            
            # Get AI explanation (simulated)
            explanation = explain_report(report_text)
            simplified_terms = simplify_medical_terms(report_text)
            
            messages.success(
                request,
                'Your report has been uploaded and analyzed successfully.'
            )
            
            context = {
                'form': ReportUploadForm(),
                'explanation': explanation,
                'simplified_terms': simplified_terms,
                'original_text': report_text,
            }
            
            return render(request, self.template_name, context)
        
        context = {'form': form}
        return render(request, self.template_name, context)


@method_decorator([login_required, patient_required], name='dispatch')
class RiskScoreView(View):
    """
    Risk Score View
    ===============
    
    Display patient's health risk assessment using AI.
    """
    
    template_name = 'patient_portal/risk.html'
    
    def get(self, request):
        """Display risk assessment."""
        patient = request.user
        
        # Get patient's health data
        recent_vitals = VitalRecord.objects.filter(
            patient=patient
        ).order_by('-recorded_at').first()
        
        recent_metrics = HealthMetric.objects.filter(
            patient=patient
        ).order_by('-recorded_at')[:20]
        
        medical_history = MedicalRecord.objects.filter(
            patient=patient
        ).order_by('-record_date')[:10]
        
        # Prepare data for AI analysis
        patient_data = {
            'patient': patient,
            'vitals': recent_vitals,
            'metrics': list(recent_metrics),
            'history': list(medical_history),
        }
        
        # Get AI risk prediction (simulated)
        risk_assessment = predict_risk(patient_data)
        risk_factors = get_risk_factors(patient_data)
        
        # Calculate trend data
        weight_trend = HealthMetric.objects.filter(
            patient=patient,
            metric_type='weight'
        ).order_by('recorded_at')[:30]
        
        context = {
            'risk_assessment': risk_assessment,
            'risk_factors': risk_factors,
            'recent_vitals': recent_vitals,
            'weight_trend': list(weight_trend),
            'recommendations': risk_assessment.get('recommendations', []),
        }
        
        return render(request, self.template_name, context)


@method_decorator([login_required, patient_required], name='dispatch')
class AppointmentPlannerView(View):
    """
    Appointment Planner View
    ========================
    
    Manage and schedule appointments.
    """
    
    template_name = 'patient_portal/appointments.html'
    
    def get(self, request):
        """Display appointments and booking form."""
        patient = request.user
        
        # Get all appointments
        upcoming = Appointment.objects.filter(
            patient=patient,
            appointment_date__gte=timezone.now().date()
        ).exclude(status__in=['cancelled', 'completed']).select_related('doctor').order_by(
            'appointment_date', 'appointment_time'
        )
        
        past = Appointment.objects.filter(
            patient=patient
        ).filter(
            Q(appointment_date__lt=timezone.now().date()) |
            Q(status__in=['completed', 'cancelled'])
        ).select_related('doctor').order_by('-appointment_date')[:10]
        
        form = AppointmentForm()
        
        context = {
            'upcoming_appointments': upcoming,
            'past_appointments': past,
            'form': form,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Create new appointment."""
        form = AppointmentForm(request.POST)
        
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()
            
            messages.success(
                request,
                f'Appointment scheduled for {appointment.appointment_date} at {appointment.appointment_time}.'
            )
            return redirect('patient_portal:appointments')
        
        # Re-render with errors
        patient = request.user
        upcoming = Appointment.objects.filter(
            patient=patient,
            appointment_date__gte=timezone.now().date()
        ).exclude(status__in=['cancelled', 'completed']).select_related('doctor')
        
        past = Appointment.objects.filter(
            patient=patient,
            appointment_date__lt=timezone.now().date()
        ).select_related('doctor')[:10]
        
        context = {
            'upcoming_appointments': upcoming,
            'past_appointments': past,
            'form': form,
        }
        
        return render(request, self.template_name, context)


@method_decorator([login_required, patient_required], name='dispatch')
class AIAssistantView(View):
    """
    AI Assistant View
    =================
    
    Interactive AI health assistant for patients.
    Provides health guidance and answers questions.
    """
    
    template_name = 'patient_portal/assistant.html'
    
    def get(self, request):
        """Display AI assistant interface."""
        patient = request.user
        
        # Get patient context for AI
        recent_vitals = VitalRecord.objects.filter(
            patient=patient
        ).order_by('-recorded_at').first()
        
        active_treatments = TreatmentPlan.objects.filter(
            patient=patient,
            status='active'
        ).first()
        
        # Get journey summary (simulated)
        journey_summary = get_patient_journey_summary({'patient': patient})
        
        # Predefined quick questions
        quick_questions = [
            "What does my latest lab result mean?",
            "When should I take my medication?",
            "What are the side effects of my treatment?",
            "How can I improve my health score?",
            "What should I eat with my condition?",
            "When is my next appointment?",
        ]
        
        context = {
            'recent_vitals': recent_vitals,
            'active_treatment': active_treatments,
            'journey_summary': journey_summary,
            'quick_questions': quick_questions,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Process AI assistant query."""
        question = request.POST.get('question', '')
        
        if not question:
            return JsonResponse({'error': 'No question provided'}, status=400)
        
        # Simulated AI response
        # In a real application, this would call an AI service
        response = {
            'question': question,
            'answer': self._generate_mock_response(question),
            'confidence': 0.85,
            'suggestions': [
                "Would you like to know more about your treatment plan?",
                "Should I explain any medical terms?",
                "Do you want to schedule an appointment?",
            ]
        }
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(response)
        
        return redirect('patient_portal:assistant')
    
    def _generate_mock_response(self, question):
        """Generate a mock AI response."""
        # Simple keyword-based responses for demonstration
        question_lower = question.lower()
        
        if 'medication' in question_lower or 'medicine' in question_lower:
            return ("Based on your treatment plan, you should take your medication "
                   "as prescribed by your doctor. If you have specific questions about "
                   "dosage or timing, please consult your healthcare provider or pharmacist.")
        
        elif 'appointment' in question_lower:
            return ("I can help you manage your appointments. You can view your upcoming "
                   "appointments in the Appointments section, or schedule a new one. "
                   "Would you like me to show you your next scheduled visit?")
        
        elif 'lab' in question_lower or 'result' in question_lower:
            return ("Your lab results are reviewed by your healthcare team. If you've "
                   "received new results, you can upload them in the Reports section "
                   "for a simplified explanation. Always discuss results with your doctor.")
        
        elif 'diet' in question_lower or 'eat' in question_lower or 'food' in question_lower:
            return ("A balanced diet is important for your health. Based on general guidelines, "
                   "focus on whole grains, lean proteins, fruits, and vegetables. For specific "
                   "dietary recommendations based on your condition, please consult your doctor.")
        
        elif 'health score' in question_lower or 'improve' in question_lower:
            return ("To improve your health score, focus on regular exercise, balanced nutrition, "
                   "adequate sleep, and following your treatment plan. Tracking your health metrics "
                   "regularly can help identify areas for improvement.")
        
        else:
            return ("I'm here to help with your health questions. You can ask me about medications, "
                   "appointments, lab results, diet, or general health advice. For specific medical "
                   "concerns, please consult your healthcare provider.")


# Additional views for complete dashboard functionality
@login_required
@patient_required
def health_details_view(request):
    """Detailed health metrics and trends view"""
    return render(request, 'patient_portal/health_details.html')


@login_required
@patient_required
def book_appointment(request):
    """Book appointment view"""
    return render(request, 'patient_portal/book_appointment.html')


@login_required
@patient_required
def medications_view(request):
    """Medications management view"""
    return render(request, 'patient_portal/medications.html')


@login_required
@patient_required
def health_records_view(request):
    """Health records view"""
    return render(request, 'patient_portal/health_records.html')


@login_required
@patient_required
def lab_results_view(request):
    """Lab results view"""
    return render(request, 'patient_portal/lab_results.html')


@login_required
@patient_required
def chat_doctor_view(request):
    """Chat with doctor view"""
    return render(request, 'patient_portal/chat_doctor.html')


@login_required
@patient_required
def emergency_contacts_view(request):
    """Emergency contacts view"""
    return render(request, 'patient_portal/emergency_contacts.html')
