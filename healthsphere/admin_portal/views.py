"""
HealthSphere AI - Admin Portal Views
====================================

Views for the hospital administration portal.
Provides dashboards for resource management, patient tracking, and analytics.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View, ListView, DetailView
from django.utils.decorators import method_decorator
from django.db.models import Count, Q
from django.utils import timezone

from .models import HospitalResource, AdmissionRecord, StaffSchedule
from users.models import User, Role


def admin_required(view_func):
    """
    Decorator to restrict access to admin users only.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        if not request.user.is_admin:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('users:redirect_after_login')
        return view_func(request, *args, **kwargs)
    return wrapper


@method_decorator([login_required, admin_required], name='dispatch')
class DashboardView(View):
    """
    Admin Dashboard View
    ====================
    
    Main dashboard for hospital administrators.
    Shows overview of resources, admissions, and key metrics.
    """
    
    template_name = 'admin_portal/dashboard.html'
    
    def get(self, request):
        """Render the admin dashboard."""
        
        # Dashboard statistics
        today = timezone.now().date()
        this_month = timezone.now().replace(day=1).date()
        
        # Get counts for dashboard cards
        total_patients = User.objects.filter(role__name='patient').count()
        total_staff = User.objects.filter(role__name__in=['doctor', 'nurse']).count()
        total_admissions = AdmissionRecord.objects.count()
        
        # Today's metrics
        today_admissions = AdmissionRecord.objects.filter(
            admission_date__date=today
        ).count()
        
        # Monthly metrics
        monthly_admissions_count = AdmissionRecord.objects.filter(
            admission_date__date__gte=this_month
        ).count()
        
        # Active admissions (currently in hospital)
        active_admissions = AdmissionRecord.objects.filter(
            status='admitted'
        ).count()
        
        # Resource availability
        total_beds = HospitalResource.objects.filter(
            resource_type='bed'
        ).count()
        
        available_beds = HospitalResource.objects.filter(
            resource_type='bed',
            status='available'
        ).count()
        
        bed_occupancy_rate = ((total_beds - available_beds) / total_beds * 100) if total_beds > 0 else 0
        
        # Recent admissions
        recent_admissions = AdmissionRecord.objects.select_related(
            'patient', 'attending_doctor'
        ).order_by('-admission_date')[:8]
        
        # Staff schedule for today
        today_staff = StaffSchedule.objects.filter(
            date=today
        ).select_related('staff_member').order_by('start_time')[:10]
        
        # Department breakdown
        department_stats = User.objects.filter(
            role__name__in=['doctor', 'nurse'],
            profile__department__isnull=False
        ).values('profile__department').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Weekly admission trend
        weekly_admissions = []
        for i in range(7):
            date = today - timezone.timedelta(days=i)
            count = AdmissionRecord.objects.filter(
                admission_date=date
            ).count()
            weekly_admissions.append({
                'date': date.strftime('%m/%d'),
                'count': count
            })
        weekly_admissions.reverse()
        
        total_doctors = User.objects.filter(role__name=Role.DOCTOR).count()
        total_nurses  = User.objects.filter(role__name=Role.NURSE).count()

        from appointments.models import Appointment
        from analytics.models import ClinicalOutcomePrediction

        consultations_today = Appointment.objects.filter(
            scheduled_date=today,
            status__in=['confirmed', 'completed']
        ).count()

        # Total appointments today (denominator for completion rate)
        total_appts_today = Appointment.objects.filter(
            scheduled_date=today
        ).count()
        consultations_completion_pct = (
            round(consultations_today * 100 / total_appts_today)
            if total_appts_today > 0 else 0
        )

        predictions_count = ClinicalOutcomePrediction.objects.count()

        context = {
            'total_patients': total_patients,
            'total_staff': total_staff,
            'total_doctors': total_doctors,
            'total_nurses': total_nurses,
            'total_admissions': total_admissions,
            'today_admissions': today_admissions,
            'monthly_admissions': monthly_admissions_count,
            'active_admissions': active_admissions,
            'available_beds': available_beds,
            'total_beds': total_beds,
            'bed_occupancy_rate': round(bed_occupancy_rate, 1),
            'recent_admissions': recent_admissions,
            'today_staff': today_staff,
            'department_stats': department_stats,
            'weekly_admissions': weekly_admissions,
            'consultations_today': consultations_today,
            'consultations_completion_pct': consultations_completion_pct,
            'predictions_count': predictions_count,
        }

        return render(request, self.template_name, context)


@method_decorator([login_required, admin_required], name='dispatch')
class PatientManagementView(View):
    """
    Patient Management View
    =======================
    
    View and manage all registered patients.
    """
    
    template_name = 'admin_portal/patients.html'
    
    def get(self, request):
        """Display patient list with real demographics from DB."""
        from django.utils import timezone as tz

        # Get all patients
        all_patients = User.objects.filter(role__name=Role.PATIENT).select_related('role')

        # Search functionality
        search_query = request.GET.get('search', '')
        patients = all_patients.order_by('-created_at')
        if search_query:
            patients = patients.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query)
            )

        # Admission stats
        total_patients = all_patients.count()
        currently_admitted = AdmissionRecord.objects.filter(
            status='admitted'
        ).values('patient').distinct().count()

        # Real age demographics
        today = tz.now().date()
        ages = [
            (today - p.date_of_birth).days // 365
            for p in all_patients
            if p.date_of_birth
        ]
        patients_with_dob = len(ages)
        def pct(n): return round(n * 100 / patients_with_dob) if patients_with_dob else 0
        age_18_30 = pct(sum(1 for a in ages if 18 <= a <= 30))
        age_31_50 = pct(sum(1 for a in ages if 31 <= a <= 50))
        age_51_plus = pct(sum(1 for a in ages if a > 50))

        # New patients this month
        first_of_month = today.replace(day=1)
        new_this_month = all_patients.filter(created_at__date__gte=first_of_month).count()

        context = {
            'patients': patients,
            'search_query': search_query,
            'total_patients': total_patients,
            'currently_admitted': currently_admitted,
            'new_this_month': new_this_month,
            'demographics': {
                'age_18_30': age_18_30,
                'age_31_50': age_31_50,
                'age_51_plus': age_51_plus,
            },
        }

        return render(request, self.template_name, context)


@method_decorator([login_required, admin_required], name='dispatch')
class ResourceMonitoringView(View):
    """
    Resource Monitoring View
    ========================
    
    Monitor and manage hospital resources.
    """
    
    template_name = 'admin_portal/resources.html'
    
    def get(self, request):
        """Display resource overview."""
        # Get all resources grouped by type
        resources = HospitalResource.objects.all().order_by('resource_type', 'name')
        
        # Filter by type if specified
        resource_type = request.GET.get('type', '')
        if resource_type:
            resources = resources.filter(resource_type=resource_type)
        
        # Filter by status if specified
        status_filter = request.GET.get('status', '')
        if status_filter:
            resources = resources.filter(status=status_filter)
        
        # Calculate statistics
        stats = {
            'total': HospitalResource.objects.count(),
            'available': HospitalResource.objects.filter(status='available').count(),
            'in_use': HospitalResource.objects.filter(status='in_use').count(),
            'maintenance': HospitalResource.objects.filter(status='maintenance').count(),
        }
        
        # Resource type choices for filter dropdown
        resource_types = HospitalResource.RESOURCE_TYPES
        status_choices = HospitalResource.STATUS_CHOICES
        
        context = {
            'resources': resources,
            'stats': stats,
            'resource_types': resource_types,
            'status_choices': status_choices,
            'selected_type': resource_type,
            'selected_status': status_filter,
        }
        
        return render(request, self.template_name, context)


@method_decorator([login_required, admin_required], name='dispatch')
class AnalyticsView(View):
    """
    Analytics View
    ==============
    
    Redirects to the unified HealthSphere Analytics dashboard.
    """
    
    def get(self, request):
        """Redirect to the unified analytics dashboard."""
        return redirect('analytics:dashboard')


# =============================================================================
# P2 NEW VIEWS — Per UX Blueprint
# =============================================================================

@method_decorator([login_required, admin_required], name='dispatch')
class PatientDetailView(View):
    """Admin view of a single patient's record."""

    template_name = 'admin_portal/patient_detail.html'

    def get(self, request, patient_id):
        patient = get_object_or_404(User, id=patient_id, role__name=Role.PATIENT)
        admissions = AdmissionRecord.objects.filter(
            patient=patient
        ).select_related('attending_doctor').order_by('-admission_date')

        context = {
            'patient': patient,
            'admissions': admissions,
            'current_admission': admissions.filter(status='admitted').first(),
        }
        return render(request, self.template_name, context)


@method_decorator([login_required, admin_required], name='dispatch')
class AdmissionsView(View):
    """
    Admissions Management View
    ==========================
    View and manage all hospital admissions. Filter by status, type, date.
    Supports POST to create a new admission.
    """

    template_name = 'admin_portal/admissions.html'

    def _get_context(self, request, status_filter='', admission_type='', search=''):
        admissions = AdmissionRecord.objects.select_related(
            'patient', 'attending_doctor'
        ).order_by('-admission_date')

        if status_filter:
            admissions = admissions.filter(status=status_filter)
        if admission_type:
            admissions = admissions.filter(admission_type=admission_type)
        if search:
            admissions = admissions.filter(
                Q(patient__first_name__icontains=search) |
                Q(patient__last_name__icontains=search) |
                Q(diagnosis__icontains=search)
            )

        today = timezone.now().date()
        stats = {
            'total': AdmissionRecord.objects.count(),
            'admitted': AdmissionRecord.objects.filter(status='admitted').count(),
            'today': AdmissionRecord.objects.filter(admission_date=today).count(),
            'discharged_today': AdmissionRecord.objects.filter(discharge_date=today).count(),
        }

        return {
            'admissions': admissions[:60],
            'stats': stats,
            'status_choices': AdmissionRecord.STATUS_CHOICES,
            'admission_types': AdmissionRecord.ADMISSION_TYPES,
            'selected_status': status_filter,
            'selected_type': admission_type,
            'search_query': search,
            # For the "Admit Patient" modal form
            'all_patients': User.objects.filter(role__name=Role.PATIENT).order_by('last_name', 'first_name'),
            'all_doctors': User.objects.filter(role__name=Role.DOCTOR).order_by('last_name', 'first_name'),
        }

    def get(self, request):
        context = self._get_context(
            request,
            status_filter=request.GET.get('status', ''),
            admission_type=request.GET.get('type', ''),
            search=request.GET.get('search', ''),
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

        # Validate required fields
        if not patient_id:
            messages.error(request, 'Please select a patient.')
            return render(request, self.template_name, self._get_context(request))

        try:
            patient = User.objects.get(id=patient_id, role__name=Role.PATIENT)
        except User.DoesNotExist:
            messages.error(request, 'Invalid patient selected.')
            return render(request, self.template_name, self._get_context(request))

        attending_doctor = None
        if doctor_id:
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

        messages.success(
            request,
            f'{patient.get_full_name()} has been admitted successfully.'
        )
        return redirect('admin_portal:admissions')


@method_decorator([login_required, admin_required], name='dispatch')
class AdmissionDetailView(View):
    """Single admission record detail."""

    template_name = 'admin_portal/admission_detail.html'

    def get(self, request, pk):
        admission = get_object_or_404(AdmissionRecord, pk=pk)
        context = {'admission': admission}
        return render(request, self.template_name, context)


@method_decorator([login_required, admin_required], name='dispatch')
class StaffManagementView(View):
    """
    Staff Management View
    =====================
    View all clinical staff (doctors and nurses), their roles,
    departments, and schedule summaries.
    """

    template_name = 'admin_portal/staff.html'

    def get(self, request):
        staff = User.objects.filter(
            role__name__in=[Role.DOCTOR, Role.NURSE]
        ).select_related('role').order_by('role__name', 'last_name')

        search = request.GET.get('search', '')
        role_filter = request.GET.get('role', '')

        if search:
            staff = staff.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        if role_filter:
            staff = staff.filter(role__name=role_filter)

        today = timezone.now().date()
        stats = {
            'total': staff.count(),
            'doctors': User.objects.filter(role__name=Role.DOCTOR).count(),
            'nurses': User.objects.filter(role__name=Role.NURSE).count(),
            'on_duty_today': StaffSchedule.objects.filter(
                date=today, status='scheduled'
            ).count(),
        }

        context = {
            'staff': staff[:50],
            'stats': stats,
            'search_query': search,
            'selected_role': role_filter,
        }
        return render(request, self.template_name, context)


@method_decorator([login_required, admin_required], name='dispatch')
class StaffDetailView(View):
    """Single staff member profile for admin."""

    template_name = 'admin_portal/staff_detail.html'

    def get(self, request, staff_id):
        staff_member = get_object_or_404(User, id=staff_id, role__name__in=[Role.DOCTOR, Role.NURSE])
        schedules = StaffSchedule.objects.filter(
            staff_member=staff_member
        ).order_by('-date')[:14]

        assigned_patients = AdmissionRecord.objects.filter(
            attending_doctor=staff_member, status='admitted'
        ).select_related('patient')

        context = {
            'staff_member': staff_member,
            'schedules': schedules,
            'assigned_patients': assigned_patients,
        }
        return render(request, self.template_name, context)


@method_decorator([login_required, admin_required], name='dispatch')
class StaffScheduleView(View):
    """
    Staff Schedule Calendar View
    ============================
    Visual weekly schedule overview for all staff.
    Queries StaffSchedule model and groups by date for the calendar.
    """

    template_name = 'admin_portal/staff_schedule.html'

    def get(self, request):
        from collections import defaultdict
        today = timezone.now().date()

        # Allow week navigation via ?offset=N (N days from today)
        try:
            offset = int(request.GET.get('offset', 0))
        except ValueError:
            offset = 0

        week_start = today + timezone.timedelta(days=offset)
        week_dates = [week_start + timezone.timedelta(days=i) for i in range(7)]

        schedules = StaffSchedule.objects.filter(
            date__in=week_dates
        ).select_related('staff_member', 'staff_member__role').order_by('date', 'start_time')

        # Group by date for easy template iteration
        by_date = defaultdict(list)
        for s in schedules:
            by_date[s.date].append(s)

        # Stats
        total_today       = StaffSchedule.objects.filter(date=today, status='scheduled').count()
        total_on_duty     = schedules.filter(status='scheduled').count()
        doctors_today     = StaffSchedule.objects.filter(
            date=today, status='scheduled', staff_member__role__name='doctor'
        ).count()
        nurses_today      = StaffSchedule.objects.filter(
            date=today, status='scheduled', staff_member__role__name='nurse'
        ).count()

        context = {
            'week_dates':    week_dates,
            'schedules':     schedules,
            'by_date':       dict(by_date),
            'today':         today,
            'offset':        offset,
            'prev_offset':   offset - 7,
            'next_offset':   offset + 7,
            'stats': {
                'total_today':   total_today,
                'total_on_duty': total_on_duty,
                'doctors_today': doctors_today,
                'nurses_today':  nurses_today,
            },
        }
        return render(request, self.template_name, context)

