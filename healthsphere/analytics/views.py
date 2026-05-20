"""
HealthSphere AI - Analytics Views
=================================

Views for the analytics dashboard, connected to real application data:
- Patient statistics from the User model
- Appointment metrics from the Appointment model
- Admission/Discharge data from AdmissionRecord
- Clinical records from MedicalRecord, VitalRecord, TreatmentPlan
- Resource utilization from HospitalResource
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, DetailView, View
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Avg, Q, Sum
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json

# Real data models
from users.models import User
from appointments.models import Appointment
from admin_portal.models import AdmissionRecord, HospitalResource, StaffSchedule
from clinical_portal.models import MedicalRecord, VitalRecord, TreatmentPlan

from .models import (
    PredictiveModel, PatientFlowPrediction, ClinicalOutcomePrediction,
    AnalyticsReport, DataQualityMetric
)
from users.models import Role


class AnalyticsAccessMixin(UserPassesTestMixin):
    """Mixin to restrict access to Admins and Doctors only."""
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.role and self.request.user.role.name in [Role.ADMIN, Role.DOCTOR]

    def handle_no_permission(self):
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(self.request, 'You do not have permission to access the analytics dashboard.')
        return redirect('users:redirect_after_login')


class AnalyticsDashboardView(AnalyticsAccessMixin, TemplateView):
    """Main analytics dashboard with real data metrics."""

    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # ── Core patient stats ──────────────────────────────────
        try:
            total_patients = User.objects.filter(role__name='patient').count()
            total_doctors = User.objects.filter(role__name='doctor').count()
        except Exception:
            total_patients = User.objects.filter(is_staff=False).count()
            total_doctors = 0

        # ── Appointment stats ───────────────────────────────────
        total_appointments = Appointment.objects.count()
        appointments_today = Appointment.objects.filter(scheduled_date=today).count()
        appointments_this_week = Appointment.objects.filter(
            scheduled_date__gte=today - timedelta(days=7)
        ).count()
        completed_appointments = Appointment.objects.filter(status='completed').count()
        pending_appointments = Appointment.objects.filter(
            status__in=['requested', 'confirmed'],
            scheduled_date__gte=today
        ).count()
        cancelled_appointments = Appointment.objects.filter(status='cancelled').count()
        completion_rate = round(
            (completed_appointments / total_appointments * 100) if total_appointments else 0, 1
        )

        # Appointment status breakdown
        appt_status_breakdown = dict(
            Appointment.objects.values('status').annotate(c=Count('id')).values_list('status', 'c')
        )

        # Appointments by day (last 7 days)
        appt_by_day = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            count = Appointment.objects.filter(scheduled_date=d).count()
            appt_by_day.append({'date': d.strftime('%a'), 'count': count})

        # ── Admission stats ─────────────────────────────────────
        total_admissions = AdmissionRecord.objects.count()
        current_admissions = AdmissionRecord.objects.filter(status='admitted').count()
        discharges_this_week = AdmissionRecord.objects.filter(
            status='discharged',
            discharge_date__gte=week_ago
        ).count()
        admissions_this_week = AdmissionRecord.objects.filter(
            admission_date__gte=week_ago
        ).count()

        # Average length of stay
        discharged = AdmissionRecord.objects.filter(
            status='discharged',
            discharge_date__isnull=False
        ).select_related('patient')[:50]
        avg_los = 0
        if discharged:
            total_days = sum(r.length_of_stay for r in discharged)
            avg_los = round(total_days / len(discharged), 1)

        # Admissions by type
        admission_type_breakdown = dict(
            AdmissionRecord.objects.values('admission_type').annotate(c=Count('id')).values_list('admission_type', 'c')
        )

        # ── Resource stats ──────────────────────────────────────
        total_beds = HospitalResource.objects.filter(
            resource_type__in=['bed', 'icu_bed']
        ).aggregate(total=Sum('quantity'))['total'] or 0
        available_beds = HospitalResource.objects.filter(
            resource_type__in=['bed', 'icu_bed'],
            status='available'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        occupied_beds = total_beds - available_beds

        # ── Clinical stats ──────────────────────────────────────
        total_records = MedicalRecord.objects.count()
        records_this_week = MedicalRecord.objects.filter(
            created_at__gte=week_ago
        ).count()
        total_vitals = VitalRecord.objects.count()
        total_treatment_plans = TreatmentPlan.objects.count()

        # Recent activity
        recent_admissions = AdmissionRecord.objects.select_related(
            'patient', 'attending_doctor'
        ).order_by('-admission_date')[:8]

        recent_appointments = Appointment.objects.select_related(
            'patient', 'doctor', 'appointment_type'
        ).order_by('-scheduled_date', '-scheduled_time')[:8]

        context.update({
            # Patients
            'total_patients': total_patients,
            'total_doctors': total_doctors,
            # Appointments
            'total_appointments': total_appointments,
            'appointments_today': appointments_today,
            'appointments_this_week': appointments_this_week,
            'completed_appointments': completed_appointments,
            'pending_appointments': pending_appointments,
            'cancelled_appointments': cancelled_appointments,
            'completion_rate': completion_rate,
            'appt_status_breakdown': appt_status_breakdown,
            'appt_by_day': appt_by_day,
            # Admissions
            'total_admissions': total_admissions,
            'current_admissions': current_admissions,
            'discharges_this_week': discharges_this_week,
            'admissions_this_week': admissions_this_week,
            'avg_los': avg_los,
            'admission_type_breakdown': admission_type_breakdown,
            # Resources
            'total_beds': total_beds,
            'available_beds': available_beds,
            'occupied_beds': occupied_beds,
            'bed_occupancy_rate': round((occupied_beds / total_beds * 100) if total_beds else 0, 1),
            # Clinical
            'total_records': total_records,
            'records_this_week': records_this_week,
            'total_vitals': total_vitals,
            'total_treatment_plans': total_treatment_plans,
            # Recent activity
            'recent_admissions': recent_admissions,
            'recent_appointments': recent_appointments,
            # Predictive models (may be empty)
            'total_models': PredictiveModel.objects.filter(is_active=True).count(),
            'data_quality_alerts': DataQualityMetric.objects.filter(
                alert_triggered=True, alert_acknowledged=False
            ).count(),
        })

        return context


class PatientFlowDashboardView(AnalyticsAccessMixin, TemplateView):
    """Patient flow analytics - admissions, discharges, appointments."""

    template_name = 'analytics/patient_flow_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        today = now.date()

        # Admissions per day (last 14 days)
        admissions_trend = []
        for i in range(13, -1, -1):
            d = today - timedelta(days=i)
            count = AdmissionRecord.objects.filter(
                admission_date__date=d
            ).count()
            admissions_trend.append({'date': d.strftime('%b %d'), 'count': count})

        # Discharges per day (last 14 days)
        discharges_trend = []
        for i in range(13, -1, -1):
            d = today - timedelta(days=i)
            count = AdmissionRecord.objects.filter(
                discharge_date__date=d
            ).count()
            discharges_trend.append({'date': d.strftime('%b %d'), 'count': count})

        # Appointments per day (last 14 days)
        appointments_trend = []
        for i in range(13, -1, -1):
            d = today - timedelta(days=i)
            count = Appointment.objects.filter(scheduled_date=d).count()
            appointments_trend.append({'date': d.strftime('%b %d'), 'count': count})

        # Current active admissions
        active_admissions = AdmissionRecord.objects.filter(
            status='admitted'
        ).select_related('patient', 'attending_doctor').order_by('-admission_date')[:20]

        # Today's appointments breakdown
        todays_appointments = Appointment.objects.filter(
            scheduled_date=today
        ).select_related('patient', 'doctor', 'appointment_type').order_by('scheduled_time')

        # Summary numbers
        total_admissions = AdmissionRecord.objects.count()
        total_discharges = AdmissionRecord.objects.filter(status='discharged').count()
        current_inpatients = AdmissionRecord.objects.filter(status='admitted').count()
        todays_appts = Appointment.objects.filter(scheduled_date=today).count()

        # Admission type breakdown
        admission_types = list(
            AdmissionRecord.objects.values('admission_type').annotate(count=Count('id')).order_by('-count')
        )

        # Ward breakdown
        ward_breakdown = list(
            AdmissionRecord.objects.filter(status='admitted').exclude(ward='')
            .values('ward').annotate(count=Count('id')).order_by('-count')[:8]
        )

        context.update({
            'total_admissions': total_admissions,
            'total_discharges': total_discharges,
            'current_inpatients': current_inpatients,
            'todays_appts': todays_appts,
            'admissions_trend': json.dumps(admissions_trend),
            'discharges_trend': json.dumps(discharges_trend),
            'appointments_trend': json.dumps(appointments_trend),
            'active_admissions': active_admissions,
            'todays_appointments': todays_appointments,
            'admission_types': admission_types,
            'ward_breakdown': ward_breakdown,
        })

        return context


class ClinicalOutcomesDashboardView(AnalyticsAccessMixin, TemplateView):
    """Clinical outcomes analytics from real medical records."""

    template_name = 'analytics/clinical_outcomes_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # Medical records stats
        total_records = MedicalRecord.objects.count()
        records_this_month = MedicalRecord.objects.filter(created_at__gte=month_ago).count()

        # Treatment plan stats
        total_plans = TreatmentPlan.objects.count()
        active_plans = TreatmentPlan.objects.filter(status='active').count() if hasattr(TreatmentPlan, 'status') else total_plans
        completed_plans = TreatmentPlan.objects.filter(status='completed').count() if hasattr(TreatmentPlan, 'status') else 0

        # Vital records stats
        total_vitals = VitalRecord.objects.count()
        vitals_this_week = VitalRecord.objects.filter(recorded_at__gte=week_ago).count() if hasattr(VitalRecord, 'recorded_at') else VitalRecord.objects.filter(created_at__gte=week_ago).count()

        # Appointment completion stats
        completed_appts = Appointment.objects.filter(status='completed').count()
        total_appts = Appointment.objects.count()
        no_show_appts = Appointment.objects.filter(status='no_show').count()
        cancelled_appts = Appointment.objects.filter(status='cancelled').count()

        # Admission outcomes
        discharged_count = AdmissionRecord.objects.filter(status='discharged').count()
        admitted_count = AdmissionRecord.objects.filter(status='admitted').count()
        transferred_count = AdmissionRecord.objects.filter(status='transferred').count()

        # Recent medical records
        recent_records = MedicalRecord.objects.select_related(
            'patient', 'created_by'
        ).order_by('-created_at')[:10]

        # Recent treatment plans
        recent_plans = TreatmentPlan.objects.select_related(
            'patient', 'created_by'
        ).order_by('-created_at')[:10]

        # Appointment type breakdown
        appt_type_breakdown = list(
            Appointment.objects.values('appointment_type__name').annotate(
                count=Count('id')
            ).order_by('-count')[:6]
        )

        context.update({
            # Medical records
            'total_records': total_records,
            'records_this_month': records_this_month,
            # Treatment plans
            'total_plans': total_plans,
            'active_plans': active_plans,
            'completed_plans': completed_plans,
            # Vitals
            'total_vitals': total_vitals,
            'vitals_this_week': vitals_this_week,
            # Appointment outcomes
            'completed_appts': completed_appts,
            'total_appts': total_appts,
            'no_show_appts': no_show_appts,
            'cancelled_appts': cancelled_appts,
            'completion_rate': round((completed_appts / total_appts * 100) if total_appts else 0, 1),
            'no_show_rate': round((no_show_appts / total_appts * 100) if total_appts else 0, 1),
            # Admissions
            'discharged_count': discharged_count,
            'admitted_count': admitted_count,
            'transferred_count': transferred_count,
            # Recent data
            'recent_records': recent_records,
            'recent_plans': recent_plans,
            'appt_type_breakdown': appt_type_breakdown,
        })

        return context


class ReportsDashboardView(AnalyticsAccessMixin, TemplateView):
    """Operational reports using real data."""

    template_name = 'analytics/reports_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        today = now.date()

        # Summary numbers for reports
        context.update({
            'total_patients': User.objects.filter(role__name='patient').count() if True else User.objects.filter(is_staff=False).count(),
            'total_appointments': Appointment.objects.count(),
            'total_admissions': AdmissionRecord.objects.count(),
            'total_records': MedicalRecord.objects.count(),
            'total_resources': HospitalResource.objects.count(),
            'active_resources': HospitalResource.objects.filter(status='available').count(),
            # Report sub-sections with real data
            'saved_reports': AnalyticsReport.objects.select_related('generated_by').order_by('-report_date')[:20],
        })

        return context


class DataQualityDashboardView(AnalyticsAccessMixin, TemplateView):
    """Data quality: checks for missing or incomplete data across the system."""

    template_name = 'analytics/data_quality_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check for patients without profiles
        try:
            patients = User.objects.filter(role__name='patient')
        except Exception:
            patients = User.objects.filter(is_staff=False)

        patients_count = patients.count()
        patients_no_phone = patients.filter(Q(phone='') | Q(phone__isnull=True)).count()
        patients_no_dob = patients.filter(date_of_birth__isnull=True).count()
        patients_no_address = patients.filter(Q(address='') | Q(address__isnull=True)).count()

        # Appointments without notes
        appts_no_notes = Appointment.objects.filter(Q(notes='') | Q(notes__isnull=True)).count()
        total_appts = Appointment.objects.count()

        # Admissions without diagnosis
        admissions_no_diagnosis = AdmissionRecord.objects.filter(
            Q(diagnosis='') | Q(diagnosis__isnull=True)
        ).count()
        total_admissions = AdmissionRecord.objects.count()

        # Medical records with incomplete data (using diagnosis_code field)
        records_no_diagnosis = MedicalRecord.objects.filter(
            Q(diagnosis_code='') | Q(diagnosis_code__isnull=True)
        ).count() if MedicalRecord.objects.count() else 0
        total_records = MedicalRecord.objects.count()

        # Data quality scores (percentage complete)
        def quality_score(missing, total):
            if total == 0:
                return 100
            return round((1 - missing / total) * 100, 1)

        metrics = [
            {
                'name': 'Patient Phone Numbers',
                'score': quality_score(patients_no_phone, patients_count),
                'missing': patients_no_phone,
                'total': patients_count,
            },
            {
                'name': 'Patient Date of Birth',
                'score': quality_score(patients_no_dob, patients_count),
                'missing': patients_no_dob,
                'total': patients_count,
            },
            {
                'name': 'Patient Address',
                'score': quality_score(patients_no_address, patients_count),
                'missing': patients_no_address,
                'total': patients_count,
            },
            {
                'name': 'Appointment Notes',
                'score': quality_score(appts_no_notes, total_appts),
                'missing': appts_no_notes,
                'total': total_appts,
            },
            {
                'name': 'Admission Diagnosis',
                'score': quality_score(admissions_no_diagnosis, total_admissions),
                'missing': admissions_no_diagnosis,
                'total': total_admissions,
            },
            {
                'name': 'Medical Record Diagnosis',
                'score': quality_score(records_no_diagnosis, total_records),
                'missing': records_no_diagnosis,
                'total': total_records,
            },
        ]

        overall_score = round(sum(m['score'] for m in metrics) / len(metrics), 1) if metrics else 100

        context.update({
            'metrics': metrics,
            'overall_score': overall_score,
            'patients_count': patients_count,
            'total_appts': total_appts,
            'total_admissions': total_admissions,
            'total_records': total_records,
            # Analytics-specific quality metrics
            'active_alerts': DataQualityMetric.objects.filter(
                alert_triggered=True, alert_acknowledged=False
            ).order_by('-metric_date'),
        })

        return context


class ModelsListView(AnalyticsAccessMixin, ListView):
    """List of predictive models."""
    model = PredictiveModel
    template_name = 'analytics/models_list.html'
    context_object_name = 'models'
    paginate_by = 20

    def get_queryset(self):
        return PredictiveModel.objects.select_related('created_by').order_by('-created_at')


class ModelDetailView(AnalyticsAccessMixin, DetailView):
    """Detailed view of a predictive model."""
    model = PredictiveModel
    template_name = 'analytics/model_detail.html'
    context_object_name = 'model'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_obj = self.get_object()
        if model_obj.model_type == 'patient_flow':
            context['recent_predictions'] = model_obj.flow_predictions.order_by('-prediction_date')[:20]
        else:
            context['recent_predictions'] = model_obj.outcome_predictions.order_by('-created_at')[:20]
        return context


class PatientFlowPredictionsView(AnalyticsAccessMixin, ListView):
    model = PatientFlowPrediction
    template_name = 'analytics/patient_flow_predictions.html'
    context_object_name = 'predictions'
    paginate_by = 25

    def get_queryset(self):
        return PatientFlowPrediction.objects.select_related('model').order_by('-prediction_date')


class ClinicalOutcomePredictionsView(AnalyticsAccessMixin, ListView):
    model = ClinicalOutcomePrediction
    template_name = 'analytics/clinical_outcome_predictions.html'
    context_object_name = 'predictions'
    paginate_by = 25

    def get_queryset(self):
        return ClinicalOutcomePrediction.objects.select_related('model', 'patient').order_by('-created_at')


class ReportDetailView(AnalyticsAccessMixin, DetailView):
    model = AnalyticsReport
    template_name = 'analytics/report_detail.html'
    context_object_name = 'report'


class ReportDownloadView(AnalyticsAccessMixin, View):
    def get(self, request, pk):
        report = get_object_or_404(AnalyticsReport, pk=pk)
        content = json.dumps(report.data, indent=2)
        response = HttpResponse(content, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{report.name}_{report.report_date.strftime("%Y%m%d")}.json"'
        return response


# API Views (kept for future predictive analytics integration)
class PatientFlowPredictionAPIView(AnalyticsAccessMixin, View):
    def post(self, request):
        return JsonResponse({'error': 'Predictive API not yet configured'}, status=501)


class ClinicalOutcomePredictionAPIView(AnalyticsAccessMixin, View):
    def post(self, request):
        return JsonResponse({'error': 'Predictive API not yet configured'}, status=501)


class GenerateReportAPIView(AnalyticsAccessMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            report_type = data.get('report_type', 'operational_kpis')
            report = AnalyticsReport.objects.create(
                name=f"{report_type.replace('_', ' ').title()} Report",
                report_type=report_type,
                frequency='ad_hoc',
                period_start=timezone.now() - timedelta(days=30),
                period_end=timezone.now(),
                data={
                    'total_patients': User.objects.filter(role__name='patient').count(),
                    'total_appointments': Appointment.objects.count(),
                    'total_admissions': AdmissionRecord.objects.count(),
                    'generated_at': timezone.now().isoformat(),
                },
                generated_by=request.user
            )
            return JsonResponse({'success': True, 'report_id': report.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class DataQualityAssessmentAPIView(AnalyticsAccessMixin, View):
    def post(self, request):
        return JsonResponse({'success': True, 'message': 'Assessment not yet implemented'})
