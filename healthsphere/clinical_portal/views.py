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
from appointments.models import Appointment

# Import AI services for risk prediction, triage, and diagnostic support
from ai_services.risk_service import predict_risk, get_risk_factors
from ai_services.triage_service import calculate_triage_score, get_triage_recommendation
from ai_services.journey_service import get_treatment_journey, predict_journey_milestones
from ai_services.diagnostic_ai import generate_diagnostic_suggestions


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
        
        # Today's appointments for the logged-in doctor
        today = timezone.now().date()
        todays_appointments = Appointment.objects.filter(
            doctor=user,
            scheduled_date=today,
        ).exclude(status__in=['cancelled', 'no_show']).select_related(
            'patient', 'appointment_type'
        ).order_by('scheduled_time')

        # Critical alerts — high/critical severity records created today
        critical_alerts = MedicalRecord.objects.filter(
            severity__in=['high', 'critical'],
            record_date__date=today,
        ).select_related('patient').order_by('-record_date')[:5]

        stats['appointments_today'] = todays_appointments.count()

        context = {
            'my_patients': my_patients[:10],
            'other_patients': other_patients[:5],
            'recent_records': recent_records,
            'active_plans': active_plans,
            'recent_vitals': recent_vitals,
            'stats': stats,
            'high_risk_patients': high_risk_patients,
            'critical_alerts': critical_alerts,
            'todays_appointments_list': todays_appointments,
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
        
        # Calculate triage scores for each patient using Ollama-enhanced service
        triage_queue = []
        for admission in emergency_admissions:
            # Get latest vitals
            latest_vitals = VitalRecord.objects.filter(
                patient=admission.patient
            ).order_by('-recorded_at').first()

            # Build triage data including vital signs from VitalRecord if available
            triage_data = {
                'patient': admission.patient,
                'chief_complaint': admission.diagnosis or '',
                'age': getattr(getattr(admission.patient, 'profile', None), 'age', None),
                'vital_signs': {
                    'heart_rate': getattr(latest_vitals, 'heart_rate', 70),
                    'systolic_bp': getattr(latest_vitals, 'systolic_bp', 120),
                    'diastolic_bp': getattr(latest_vitals, 'diastolic_bp', 80),
                    'temperature': getattr(latest_vitals, 'temperature', 37.0),
                    'oxygen_saturation': getattr(latest_vitals, 'oxygen_saturation', 98),
                } if latest_vitals else {},
                'symptoms': [],
                'medical_history': [],
                'pain_score': 0,
            }
            triage_result = calculate_triage_score(triage_data)

            triage_queue.append({
                'admission': admission,
                'patient': admission.patient,
                'vitals': latest_vitals,
                'triage_score': triage_result['score'],
                'triage_level': triage_result.get('priority', 'Standard'),
                'triage_color': triage_result.get('color', '#28a745'),
                'esi_level': triage_result.get('esi_level', 5),
                'recommended_actions': triage_result.get('recommended_actions', []),
                'ai_narrative': triage_result.get('ai_narrative'),
                'ai_powered': triage_result.get('ai_powered', False),
                'red_flags': triage_result.get('red_flags', []),
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


# =============================================================================
# P1 NEW VIEWS — Per UX Blueprint
# =============================================================================

@method_decorator([login_required, clinical_staff_required], name='dispatch')
class PatientListView(View):
    """
    Patient List View
    =================
    Clinical staff can browse all registered patients and search/filter by
    various criteria. Gateway to per-patient detail, records, and plans.
    """

    template_name = 'clinical_portal/patients.html'

    def get(self, request):
        """Display patient list."""
        patients = User.objects.filter(
            role__name=Role.PATIENT
        ).select_related('role').order_by('last_name', 'first_name')

        search_query = request.GET.get('search', '')
        if search_query:
            patients = patients.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query)
            )

        # Annotate each patient with their latest admission status
        patient_data = []
        for patient in patients[:50]:
            latest_admission = patient.admissions.order_by('-admission_date').first()
            latest_record = MedicalRecord.objects.filter(patient=patient).order_by('-record_date').first()
            patient_data.append({
                'patient': patient,
                'admission': latest_admission,
                'latest_record': latest_record,
                'is_admitted': latest_admission and latest_admission.status == 'admitted',
            })

        context = {
            'patient_data': patient_data,
            'search_query': search_query,
            'total_patients': patients.count(),
        }
        return render(request, self.template_name, context)


@method_decorator([login_required, clinical_staff_required], name='dispatch')
class PatientDetailView(View):
    """Single patient overview for clinical staff."""

    template_name = 'clinical_portal/patient_detail.html'

    def get(self, request, patient_id):
        patient = get_object_or_404(User, id=patient_id, role__name=Role.PATIENT)
        records = MedicalRecord.objects.filter(patient=patient).order_by('-record_date')[:10]
        plans = TreatmentPlan.objects.filter(patient=patient).order_by('-created_at')
        vitals = VitalRecord.objects.filter(patient=patient).order_by('-recorded_at')[:10]
        latest_vitals = vitals.first()
        admissions = patient.admissions.order_by('-admission_date')[:5]

        # Build patient_data for Ollama Diagnostic AI
        symptoms = list(
            records.values_list('title', flat=True)[:5]
        )  # Use record titles as symptom proxies
        medical_history = list(
            records.values_list('description', flat=True)[:3]
        )
        patient_data = {
            'age': getattr(getattr(patient, 'profile', None), 'age', None) or 30,
            'gender': getattr(getattr(patient, 'profile', None), 'gender', 'unknown') or 'unknown',
            'symptoms': symptoms,
            'medical_history': medical_history,
            'vital_signs': {
                'heart_rate': getattr(latest_vitals, 'heart_rate', None),
                'systolic_bp': getattr(latest_vitals, 'systolic_bp', None),
                'temperature': getattr(latest_vitals, 'temperature', None),
                'oxygen_saturation': getattr(latest_vitals, 'oxygen_saturation', None),
            } if latest_vitals else {},
            'lab_results': {},
        }
        diagnostic_result = generate_diagnostic_suggestions(patient_data)

        context = {
            'patient': patient,
            'records': records,
            'plans': plans,
            'vitals': vitals,
            'admissions': admissions,
            'diagnostic_ai': diagnostic_result,
        }
        return render(request, self.template_name, context)


@method_decorator([login_required, clinical_staff_required], name='dispatch')
class MedicalRecordsView(View):
    """
    Medical Records View
    ====================
    List all medical records. Can filter by patient, type, and severity.
    Supports POST to create a new record.
    """

    template_name = 'clinical_portal/records.html'

    def _get_context(self, request, patient_id='', record_type='', severity='', search=''):
        records = MedicalRecord.objects.select_related('patient', 'created_by').order_by('-record_date')

        if patient_id:
            records = records.filter(patient_id=patient_id)
        if record_type:
            records = records.filter(record_type=record_type)
        if severity:
            records = records.filter(severity=severity)
        if search:
            records = records.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        patients = User.objects.filter(role__name=Role.PATIENT).order_by('last_name')

        return {
            'records': records[:50],
            'patients': patients,
            'record_types': MedicalRecord.RECORD_TYPES,
            'severity_choices': [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
            'selected_patient': patient_id,
            'selected_type': record_type,
            'selected_severity': severity,
            'search_query': search,
        }

    def get(self, request):
        context = self._get_context(
            request,
            patient_id=request.GET.get('patient_id', ''),
            record_type=request.GET.get('type', ''),
            severity=request.GET.get('severity', ''),
            search=request.GET.get('search', ''),
        )
        return render(request, self.template_name, context)

    def post(self, request):
        patient_id = request.POST.get('patient')
        record_type = request.POST.get('record_type', 'consultation')
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        severity = request.POST.get('severity', 'low')
        diagnosis_code = request.POST.get('diagnosis_code', '').strip()
        is_confidential = request.POST.get('is_confidential') == 'on'

        # Validate
        if not patient_id or not title or not description:
            messages.error(request, 'Patient, title, and description are required.')
            return render(request, self.template_name, self._get_context(request))

        try:
            patient = User.objects.get(id=patient_id, role__name=Role.PATIENT)
        except User.DoesNotExist:
            messages.error(request, 'Invalid patient selected.')
            return render(request, self.template_name, self._get_context(request))

        MedicalRecord.objects.create(
            patient=patient,
            created_by=request.user,
            record_type=record_type,
            title=title,
            description=description,
            severity=severity,
            diagnosis_code=diagnosis_code,
            is_confidential=is_confidential,
        )

        messages.success(request, f'Medical record "{title}" created for {patient.get_full_name()}.')
        return redirect('clinical_portal:records')


@method_decorator([login_required, clinical_staff_required], name='dispatch')
class RecordDetailView(View):
    """Single medical record detail."""

    template_name = 'clinical_portal/record_detail.html'

    def get(self, request, pk):
        record = get_object_or_404(MedicalRecord, pk=pk)
        context = {'record': record}
        return render(request, self.template_name, context)


@method_decorator([login_required, clinical_staff_required], name='dispatch')
class TreatmentPlansView(View):
    """
    Treatment Plans View
    ====================
    List and manage all active and historical treatment plans.
    """

    template_name = 'clinical_portal/treatment_plans.html'

    def get(self, request):
        plans = TreatmentPlan.objects.select_related('patient', 'created_by').order_by('-created_at')

        status_filter = request.GET.get('status', '')
        patient_id = request.GET.get('patient_id', '')
        search = request.GET.get('search', '')

        if status_filter:
            plans = plans.filter(status=status_filter)
        if patient_id:
            plans = plans.filter(patient_id=patient_id)
        if search:
            plans = plans.filter(
                Q(title__icontains=search) | Q(diagnosis__icontains=search)
            )

        patients = User.objects.filter(role__name=Role.PATIENT).order_by('last_name')
        stats = {
            'active': TreatmentPlan.objects.filter(status='active').count(),
            'completed': TreatmentPlan.objects.filter(status='completed').count(),
            'pending_review': TreatmentPlan.objects.filter(
                next_review_date__lte=timezone.now().date()
            ).count(),
        }

        context = {
            'plans': plans[:50],
            'patients': patients,
            'status_choices': TreatmentPlan.STATUS_CHOICES,
            'stats': stats,
            'selected_status': status_filter,
            'selected_patient': patient_id,
            'search_query': search,
        }
        return render(request, self.template_name, context)


@method_decorator([login_required, clinical_staff_required], name='dispatch')
class TreatmentPlanDetailView(View):
    """Single treatment plan detail."""

    template_name = 'clinical_portal/treatment_plan_detail.html'

    def get(self, request, pk):
        plan = get_object_or_404(TreatmentPlan, pk=pk)
        context = {'plan': plan}
        return render(request, self.template_name, context)


@method_decorator([login_required, clinical_staff_required], name='dispatch')
class VitalsView(View):
    """
    Vitals Monitoring View
    ======================
    Overview of recent vital sign recordings across all patients.
    Highlights out-of-range values.
    """

    template_name = 'clinical_portal/vitals.html'

    def get(self, request):
        vitals = VitalRecord.objects.select_related('patient', 'recorded_by').order_by('-recorded_at')

        patient_id = request.GET.get('patient_id', '')
        if patient_id:
            vitals = vitals.filter(patient_id=patient_id)

        patients = User.objects.filter(role__name=Role.PATIENT).order_by('last_name')

        context = {
            'vitals': vitals[:60],
            'patients': patients,
            'selected_patient': patient_id,
            'total_vitals': vitals.count(),
        }
        return render(request, self.template_name, context)


@method_decorator([login_required, clinical_staff_required], name='dispatch')
class PatientVitalsView(View):
    """Vitals trend for a single patient."""

    template_name = 'clinical_portal/patient_vitals.html'

    def get(self, request, patient_id):
        patient = get_object_or_404(User, id=patient_id, role__name=Role.PATIENT)
        vitals = VitalRecord.objects.filter(patient=patient).order_by('-recorded_at')[:30]

        context = {
            'patient': patient,
            'vitals': vitals,
        }
        return render(request, self.template_name, context)


@method_decorator([login_required, clinical_staff_required], name='dispatch')
class EditPatientView(View):
    """
    Edit Patient Details
    ====================
    Allows clinical staff to update a patient's core info (name, phone,
    email) and their UserProfile (blood type, allergies, emergency contact).
    Handles POST only; redirects back to patient_detail on success.
    """

    def post(self, request, patient_id):
        patient = get_object_or_404(User, id=patient_id, role__name=Role.PATIENT)
        profile, _ = patient.profile.__class__.objects.get_or_create(user=patient)

        # -- User model fields --
        patient.first_name = request.POST.get('first_name', patient.first_name).strip()
        patient.last_name  = request.POST.get('last_name',  patient.last_name).strip()
        patient.email      = request.POST.get('email',      patient.email).strip()
        patient.phone      = request.POST.get('phone',      patient.phone or '').strip()
        dob = request.POST.get('date_of_birth', '')
        if dob:
            patient.date_of_birth = dob
        patient.save()

        # -- UserProfile fields --
        profile.blood_type              = request.POST.get('blood_type', profile.blood_type or '').strip()
        profile.allergies               = request.POST.get('allergies',  profile.allergies or '').strip()
        profile.emergency_contact_name  = request.POST.get('emergency_contact_name',  profile.emergency_contact_name or '').strip()
        profile.emergency_contact_phone = request.POST.get('emergency_contact_phone', profile.emergency_contact_phone or '').strip()
        profile.medical_notes           = request.POST.get('medical_notes', profile.medical_notes or '').strip()
        profile.save()

        messages.success(request, f"Patient details for {patient.get_full_name()} updated successfully.")
        return redirect('clinical_portal:patient_detail', patient_id=patient_id)


@method_decorator([login_required, clinical_staff_required], name='dispatch')
class DischargePatientView(View):
    """
    Discharge Patient
    =================
    Marks the patient's active admission as discharged and auto-creates
    a MedicalRecord of type 'discharge' with the doctor's summary.
    """

    def post(self, request, patient_id):
        patient = get_object_or_404(User, id=patient_id, role__name=Role.PATIENT)

        # Find the active admission (most recent 'admitted')
        active_admission = patient.admissions.filter(status='admitted').order_by('-admission_date').first()

        discharge_summary  = request.POST.get('discharge_summary', '').strip()
        discharge_diagnosis = request.POST.get('discharge_diagnosis', '').strip()
        follow_up_instructions = request.POST.get('follow_up_instructions', '').strip()
        discharge_type = request.POST.get('discharge_type', 'discharged')  # discharged / transferred

        if not discharge_summary:
            messages.error(request, "Discharge summary is required.")
            return redirect('clinical_portal:patient_detail', patient_id=patient_id)

        if active_admission:
            active_admission.status = discharge_type
            active_admission.discharge_date = timezone.now()
            active_admission.notes = (
                f"Discharge summary: {discharge_summary}\n"
                f"Follow-up: {follow_up_instructions}"
            )
            active_admission.save()

        # Create a discharge MedicalRecord
        MedicalRecord.objects.create(
            patient=patient,
            created_by=request.user,
            record_type='discharge',
            title=f"Discharge Summary — {timezone.now().strftime('%d %b %Y')}",
            description=(
                f"Primary Diagnosis: {discharge_diagnosis}\n\n"
                f"Discharge Summary:\n{discharge_summary}\n\n"
                f"Follow-up Instructions:\n{follow_up_instructions}"
            ),
            severity='low',
        )

        messages.success(
            request,
            f"{patient.get_full_name()} has been discharged successfully. "
            "A discharge summary record has been created."
        )
        return redirect('clinical_portal:patient_detail', patient_id=patient_id)


@method_decorator([login_required, clinical_staff_required], name='dispatch')
class AdmissionsView(View):
    """
    Admissions Management (Clinical Portal)
    ========================================
    Doctors and nurses can view all admissions and admit new patients.
    When the logged-in user is a doctor they are pre-set as the attending
    physician. Nurses must pick a doctor from the dropdown.
    """

    template_name = 'clinical_portal/admissions.html'

    def _get_context(self, request, status_filter='', admission_type='', search='', my_patients_only=False):
        user = request.user
        today = timezone.now().date()

        admissions = AdmissionRecord.objects.select_related(
            'patient', 'attending_doctor'
        ).order_by('-admission_date')

        if my_patients_only and user.is_doctor:
            admissions = admissions.filter(attending_doctor=user)
        if status_filter:
            admissions = admissions.filter(status=status_filter)
        if admission_type:
            admissions = admissions.filter(admission_type=admission_type)
        if search:
            admissions = admissions.filter(
                Q(patient__first_name__icontains=search) |
                Q(patient__last_name__icontains=search) |
                Q(diagnosis__icontains=search) |
                Q(ward__icontains=search)
            )

        stats = {
            'total': AdmissionRecord.objects.filter(status='admitted').count(),
            'today': AdmissionRecord.objects.filter(admission_date__date=today).count(),
            'discharged_today': AdmissionRecord.objects.filter(discharge_date__date=today).count(),
            'my_patients': AdmissionRecord.objects.filter(
                attending_doctor=user, status='admitted'
            ).count() if user.is_doctor else 0,
        }

        return {
            'admissions': admissions[:80],
            'stats': stats,
            'status_choices': AdmissionRecord.STATUS_CHOICES,
            'admission_types': AdmissionRecord.ADMISSION_TYPES,
            'selected_status': status_filter,
            'selected_type': admission_type,
            'search_query': search,
            'my_patients_only': my_patients_only,
            'all_patients': User.objects.filter(role__name=Role.PATIENT).order_by('last_name', 'first_name'),
            'all_doctors': User.objects.filter(role__name=Role.DOCTOR).order_by('last_name', 'first_name'),
            'current_user_is_doctor': user.is_doctor,
        }

    def get(self, request):
        context = self._get_context(
            request,
            status_filter=request.GET.get('status', ''),
            admission_type=request.GET.get('type', ''),
            search=request.GET.get('search', ''),
            my_patients_only=request.GET.get('mine', '') == '1',
        )
        return render(request, self.template_name, context)

    def post(self, request):
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('attending_doctor')
        admission_type = request.POST.get('admission_type', 'scheduled')
        diagnosis = request.POST.get('diagnosis', '').strip()
        notes = request.POST.get('notes', '').strip()
        ward = request.POST.get('ward', '').strip()
        room_number = request.POST.get('room_number', '').strip()
        bed_number = request.POST.get('bed_number', '').strip()

        if not patient_id:
            messages.error(request, 'Please select a patient.')
            return render(request, self.template_name, self._get_context(request))

        try:
            patient = User.objects.get(id=patient_id, role__name=Role.PATIENT)
        except User.DoesNotExist:
            messages.error(request, 'Invalid patient selected.')
            return render(request, self.template_name, self._get_context(request))

        # Determine attending doctor: logged-in doctor OR chosen from dropdown
        attending_doctor = None
        if request.user.is_doctor:
            attending_doctor = request.user
        elif doctor_id:
            try:
                attending_doctor = User.objects.get(id=doctor_id, role__name=Role.DOCTOR)
            except User.DoesNotExist:
                pass

        AdmissionRecord.objects.create(
            patient=patient,
            attending_doctor=attending_doctor,
            admission_type=admission_type,
            diagnosis=diagnosis,
            notes=notes,
            ward=ward,
            room_number=room_number,
            bed_number=bed_number,
            status='admitted',
        )

        messages.success(request, f'{patient.get_full_name()} has been admitted successfully.')
        return redirect('clinical_portal:admissions')
