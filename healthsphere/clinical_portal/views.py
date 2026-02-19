"""
HealthSphere AI - Clinical Portal Views
=======================================

Views for the clinical portal used by doctors and nurses.
Provides patient care management, risk insights, and treatment tracking.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.db.models import Q, Avg
from django.utils import timezone

from .models import MedicalRecord, TreatmentPlan, VitalRecord
from admin_portal.models import AdmissionRecord
from users.models import User, Role

# Import AI services for risk prediction and triage
from ai_services.risk_service import predict_risk, get_risk_factors
from ai_services.triage_service import calculate_triage_score, get_triage_recommendation
from ai_services.journey_service import get_treatment_journey, predict_journey_milestones


def clinical_staff_required(view_func):
    """
    Decorator to restrict access to clinical staff (doctors and nurses) only.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        if not request.user.is_clinical_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('users:redirect_after_login')
        return view_func(request, *args, **kwargs)
    return wrapper


@method_decorator([login_required, clinical_staff_required], name='dispatch')
class DashboardView(View):
    """
    Clinical Dashboard View
    =======================
    
    Main dashboard for doctors and nurses.
    Shows patient overview, recent activities, and quick actions.
    """
    
    template_name = 'clinical_portal/dashboard.html'
    
    def get(self, request):
        """Render the clinical dashboard."""
        user = request.user
        
        # Get currently admitted patients
        active_admissions = AdmissionRecord.objects.filter(
            status='admitted'
        ).select_related('patient', 'attending_doctor')
        
        # If user is a doctor, show their assigned patients first
        if user.is_doctor:
            my_patients = active_admissions.filter(attending_doctor=user)
            other_patients = active_admissions.exclude(attending_doctor=user)
        else:
            my_patients = active_admissions
            other_patients = AdmissionRecord.objects.none()
        
        # Recent medical records (created by this user)
        recent_records = MedicalRecord.objects.filter(
            created_by=user
        ).select_related('patient').order_by('-created_at')[:5]
        
        # Active treatment plans
        active_plans = TreatmentPlan.objects.filter(
            status='active'
        ).select_related('patient').order_by('-updated_at')[:5]
        
        # Recent vital records
        recent_vitals = VitalRecord.objects.select_related(
            'patient'
        ).order_by('-recorded_at')[:5]
        
        # Statistics
        stats = {
            'total_admitted': active_admissions.count(),
            'my_patients': my_patients.count() if user.is_doctor else active_admissions.count(),
            'pending_reviews': TreatmentPlan.objects.filter(
                next_review_date__lte=timezone.now().date()
            ).count(),
            'critical_patients': MedicalRecord.objects.filter(
                severity='critical',
                record_date__date=timezone.now().date()
            ).values('patient').distinct().count(),
        }
        
        # Patients needing attention (high risk or critical)
        high_risk_patients = MedicalRecord.objects.filter(
            severity__in=['high', 'critical']
        ).select_related('patient').order_by('-record_date')[:5]
        
        context = {
            'my_patients': my_patients[:10],
            'other_patients': other_patients[:5],
            'recent_records': recent_records,
            'active_plans': active_plans,
            'recent_vitals': recent_vitals,
            'stats': stats,
            'high_risk_patients': high_risk_patients,
            # Template expects these variables
            'critical_alerts': [],
            'todays_appointments_list': [],
        }
        
        return render(request, self.template_name, context)


@method_decorator([login_required, clinical_staff_required], name='dispatch')
class RiskInsightsView(View):
    """
    Risk Insights View
    ==================
    
    Display AI-powered patient risk assessments.
    Uses simulated AI service for risk prediction.
    """
    
    template_name = 'clinical_portal/risk.html'
    
    def get(self, request):
        """Display risk insights dashboard."""
        # Get patient ID from query params for individual patient view
        patient_id = request.GET.get('patient_id')
        
        if patient_id:
            # Individual patient risk assessment
            patient = get_object_or_404(User, id=patient_id, role__name=Role.PATIENT)
            
            # Get patient's recent vitals
            recent_vitals = VitalRecord.objects.filter(
                patient=patient
            ).order_by('-recorded_at').first()
            
            # Get patient's medical history
            medical_history = MedicalRecord.objects.filter(
                patient=patient
            ).order_by('-record_date')[:10]
            
            # Prepare data for AI risk prediction
            patient_data = {
                'age': patient.date_of_birth,
                'vitals': recent_vitals,
                'medical_history': medical_history,
            }
            
            # Get AI risk prediction (simulated)
            risk_assessment = predict_risk(patient_data)
            risk_factors = get_risk_factors(patient_data)
            
            context = {
                'view_mode': 'individual',
                'patient': patient,
                'recent_vitals': recent_vitals,
                'medical_history': medical_history,
                'risk_assessment': risk_assessment,
                'risk_factors': risk_factors,
            }
        else:
            # Overview of all patients with risk scores
            patients = User.objects.filter(role__name=Role.PATIENT)
            
            # Calculate risk scores for each patient (simulated)
            patient_risks = []
            for patient in patients[:20]:  # Limit for performance
                recent_record = MedicalRecord.objects.filter(
                    patient=patient
                ).order_by('-record_date').first()
                
                risk_data = predict_risk({'patient': patient})
                patient_risks.append({
                    'patient': patient,
                    'risk_score': risk_data['risk_score'],
                    'risk_level': risk_data['risk_level'],
                    'last_record': recent_record,
                })
            
            # Sort by risk score (highest first)
            patient_risks.sort(key=lambda x: x['risk_score'], reverse=True)
            
            context = {
                'view_mode': 'overview',
                'patient_risks': patient_risks,
            }
        
        return render(request, self.template_name, context)


@method_decorator([login_required, clinical_staff_required], name='dispatch')
class TreatmentJourneyView(View):
    """
    Treatment Journey View
    ======================
    
    Visualize patient treatment journey and progress.
    Shows timeline of treatments, milestones, and outcomes.
    """
    
    template_name = 'clinical_portal/journey.html'
    
    def get(self, request):
        """Display treatment journey."""
        patient_id = request.GET.get('patient_id')
        
        if patient_id:
            # Individual patient journey
            patient = get_object_or_404(User, id=patient_id, role__name=Role.PATIENT)
            
            # Get all medical records for timeline
            medical_records = MedicalRecord.objects.filter(
                patient=patient
            ).order_by('record_date')
            
            # Get treatment plans
            treatment_plans = TreatmentPlan.objects.filter(
                patient=patient
            ).order_by('start_date')
            
            # Get admissions
            admissions = AdmissionRecord.objects.filter(
                patient=patient
            ).order_by('admission_date')
            
            # Build timeline
            timeline_events = []
            
            for admission in admissions:
                timeline_events.append({
                    'date': admission.admission_date,
                    'type': 'admission',
                    'title': f'Hospital Admission ({admission.get_admission_type_display()})',
                    'description': admission.diagnosis or 'No diagnosis recorded',
                    'status': admission.status,
                })
                if admission.discharge_date:
                    timeline_events.append({
                        'date': admission.discharge_date,
                        'type': 'discharge',
                        'title': 'Discharged',
                        'description': f'Length of stay: {admission.length_of_stay} days',
                        'status': 'completed',
                    })
            
            for record in medical_records:
                timeline_events.append({
                    'date': record.record_date,
                    'type': 'record',
                    'title': record.title,
                    'description': record.description[:200] + '...' if len(record.description) > 200 else record.description,
                    'status': record.severity,
                })
            
            for plan in treatment_plans:
                timeline_events.append({
                    'date': plan.start_date,
                    'type': 'treatment',
                    'title': plan.title,
                    'description': plan.diagnosis,
                    'status': plan.status,
                })
            
            # Sort timeline by date
            timeline_events.sort(key=lambda x: x['date'], reverse=True)
            
            # Get AI journey insights (simulated)
            journey_insights = get_treatment_journey({'patient': patient})
            milestones = predict_journey_milestones({'patient': patient})
            
            context = {
                'patient': patient,
                'timeline_events': timeline_events,
                'treatment_plans': treatment_plans,
                'journey_insights': journey_insights,
                'milestones': milestones,
            }
        else:
            # List of patients for selection
            patients = User.objects.filter(
                role__name=Role.PATIENT
            ).order_by('last_name', 'first_name')
            
            context = {
                'patients': patients,
            }
        
        return render(request, self.template_name, context)


@method_decorator([login_required, clinical_staff_required], name='dispatch')
class TriageDashboardView(View):
    """
    Triage Dashboard View
    =====================
    
    Emergency triage support with AI-powered prioritization.
    Helps clinical staff prioritize patients based on severity.
    """
    
    template_name = 'clinical_portal/triage.html'
    
    def get(self, request):
        """Display triage dashboard."""
        # Get currently admitted emergency patients
        emergency_admissions = AdmissionRecord.objects.filter(
            admission_type='emergency',
            status='admitted'
        ).select_related('patient', 'attending_doctor')
        
        # Calculate triage scores for each patient (simulated)
        triage_queue = []
        for admission in emergency_admissions:
            # Get latest vitals
            latest_vitals = VitalRecord.objects.filter(
                patient=admission.patient
            ).order_by('-recorded_at').first()
            
            # Get triage score from AI service
            triage_data = {
                'patient': admission.patient,
                'vitals': latest_vitals,
                'admission': admission,
            }
            triage_result = calculate_triage_score(triage_data)
            recommendation = get_triage_recommendation(triage_data)
            
            triage_queue.append({
                'admission': admission,
                'patient': admission.patient,
                'vitals': latest_vitals,
                'triage_score': triage_result['score'],
                'triage_level': triage_result['level'],
                'triage_color': triage_result['color'],
                'recommendation': recommendation,
                'wait_time': admission.length_of_stay,
            })
        
        # Sort by triage score (highest priority first)
        triage_queue.sort(key=lambda x: x['triage_score'], reverse=True)
        
        # Statistics
        stats = {
            'total_emergency': len(triage_queue),
            'critical': sum(1 for t in triage_queue if t['triage_level'] == 'Critical'),
            'urgent': sum(1 for t in triage_queue if t['triage_level'] == 'Urgent'),
            'standard': sum(1 for t in triage_queue if t['triage_level'] == 'Standard'),
        }
        
        context = {
            'triage_queue': triage_queue,
            'stats': stats,
        }
        
        return render(request, self.template_name, context)
