"""
HealthSphere AI - Appointment Management Views
=============================================

Views for appointment scheduling, management, and doctor availability.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta, date
import json

from .models import Appointment, AppointmentType, DoctorSchedule, AppointmentReminder
from users.models import User


class AppointmentListView(LoginRequiredMixin, ListView):
    """List view for appointments based on user role."""
    
    model = Appointment
    template_name = 'appointments/appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 20
    
    def get_queryset(self):
        """Filter appointments based on user role."""
        user = self.request.user
        queryset = Appointment.objects.select_related('patient', 'doctor', 'appointment_type')
        
        if user.is_patient:
            # Patients see only their own appointments
            queryset = queryset.filter(patient=user)
        elif user.is_doctor:
            # Doctors see their assigned appointments
            queryset = queryset.filter(doctor=user)
        elif user.is_admin:
            # Admins see all appointments
            pass
        else:
            # Other roles see no appointments
            queryset = queryset.none()
        
        # Apply filters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        date_from = self.request.GET.get('date_from')
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(scheduled_date__gte=date_from)
            except ValueError:
                pass
        
        return queryset.order_by('-scheduled_date', '-scheduled_time')
    
    def get_context_data(self, **kwargs):
        """Add filter options to context."""
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Appointment.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['current_date_from'] = self.request.GET.get('date_from', '')
        return context


class AppointmentCalendarView(LoginRequiredMixin, TemplateView):
    """Calendar view for appointments."""
    
    template_name = 'appointments/appointment_calendar.html'
    
    def get_context_data(self, **kwargs):
        """Add appointment data for calendar."""
        context = super().get_context_data(**kwargs)
        
        # Get appointments for current month
        today = timezone.now().date()
        start_date = today.replace(day=1)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)
        
        user = self.request.user
        appointments = Appointment.objects.filter(
            scheduled_date__gte=start_date,
            scheduled_date__lt=end_date
        ).select_related('patient', 'doctor', 'appointment_type')
        
        if user.is_patient:
            appointments = appointments.filter(patient=user)
        elif user.is_doctor:
            appointments = appointments.filter(doctor=user)
        
        # Convert appointments to calendar events format
        events = []
        for appointment in appointments:
            events.append({
                'id': appointment.id,
                'title': f"{appointment.patient.get_full_name()} - {appointment.appointment_type.get_name_display()}",
                'start': f"{appointment.scheduled_date}T{appointment.scheduled_time}",
                'end': (appointment.scheduled_datetime + timedelta(minutes=appointment.duration_minutes)).isoformat(),
                'color': appointment.appointment_type.color_code,
                'url': f"/appointments/{appointment.id}/",
            })
        
        context['events'] = json.dumps(events)
        return context


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a single appointment."""
    
    model = Appointment
    template_name = 'appointments/appointment_detail.html'
    context_object_name = 'appointment'
    
    def get_queryset(self):
        """Ensure users can only view appropriate appointments."""
        user = self.request.user
        queryset = Appointment.objects.select_related('patient', 'doctor', 'appointment_type')
        
        if user.is_patient:
            return queryset.filter(patient=user)
        elif user.is_doctor:
            return queryset.filter(doctor=user)
        elif user.is_admin:
            return queryset
        else:
            return queryset.none()


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    """Create view for new appointments."""
    
    model = Appointment
    template_name = 'appointments/appointment_form.html'
    fields = ['doctor', 'appointment_type', 'scheduled_date', 'scheduled_time', 'reason', 'notes']
    success_url = reverse_lazy('appointments:list')
    
    def form_valid(self, form):
        """Set the patient to current user if they are a patient."""
        if self.request.user.is_patient:
            form.instance.patient = self.request.user
        elif self.request.user.is_admin:
            # Admin needs to select a patient
            patient_id = self.request.POST.get('patient')
            if patient_id:
                form.instance.patient = get_object_or_404(User, pk=patient_id, role__name='patient')
        
        messages.success(self.request, 'Appointment request has been submitted successfully.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Add additional context for form."""
        context = super().get_context_data(**kwargs)
        context['appointment_types'] = AppointmentType.objects.filter(is_active=True)
        context['doctors'] = User.objects.filter(role__name='doctor')
        
        if self.request.user.is_admin:
            context['patients'] = User.objects.filter(role__name='patient')
        
        return context


class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    """Update view for existing appointments."""
    
    model = Appointment
    template_name = 'appointments/appointment_form.html'
    fields = ['doctor', 'appointment_type', 'scheduled_date', 'scheduled_time', 'reason', 'notes']
    success_url = reverse_lazy('appointments:list')
    
    def get_queryset(self):
        """Ensure users can only edit appropriate appointments."""
        user = self.request.user
        queryset = Appointment.objects.all()
        
        if user.is_patient:
            return queryset.filter(patient=user, status__in=['requested', 'confirmed'])
        elif user.is_doctor:
            return queryset.filter(doctor=user)
        elif user.is_admin:
            return queryset
        else:
            return queryset.none()
    
    def form_valid(self, form):
        """Handle appointment update."""
        messages.success(self.request, 'Appointment has been updated successfully.')
        return super().form_valid(form)


class AppointmentDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for appointments."""
    
    model = Appointment
    template_name = 'appointments/appointment_confirm_delete.html'
    success_url = reverse_lazy('appointments:list')
    
    def get_queryset(self):
        """Ensure users can only delete appropriate appointments."""
        user = self.request.user
        queryset = Appointment.objects.all()
        
        if user.is_patient:
            return queryset.filter(patient=user, status__in=['requested'])
        elif user.is_admin:
            return queryset
        else:
            return queryset.none()
    
    def delete(self, request, *args, **kwargs):
        """Handle appointment deletion."""
        messages.success(request, 'Appointment has been cancelled successfully.')
        return super().delete(request, *args, **kwargs)


# Doctor Schedule Views
class DoctorScheduleView(LoginRequiredMixin, ListView):
    """List view for doctor schedules."""
    
    model = DoctorSchedule
    template_name = 'appointments/doctor_schedule_list.html'
    context_object_name = 'schedules'
    
    def get_queryset(self):
        """Get schedules based on user role."""
        user = self.request.user
        
        if user.is_doctor:
            return DoctorSchedule.objects.filter(doctor=user)
        elif user.is_admin:
            return DoctorSchedule.objects.all().select_related('doctor')
        else:
            return DoctorSchedule.objects.none()


class DoctorScheduleCreateView(LoginRequiredMixin, CreateView):
    """Create view for doctor schedules."""
    
    model = DoctorSchedule
    template_name = 'appointments/doctor_schedule_form.html'
    fields = ['day_of_week', 'start_time', 'end_time', 'break_start_time', 'break_end_time', 'max_appointments']
    success_url = reverse_lazy('appointments:schedule')
    
    def form_valid(self, form):
        """Set the doctor to current user or selected doctor."""
        if self.request.user.is_doctor:
            form.instance.doctor = self.request.user
        elif self.request.user.is_admin:
            doctor_id = self.request.POST.get('doctor')
            if doctor_id:
                form.instance.doctor = get_object_or_404(User, pk=doctor_id, role__name='doctor')
        
        messages.success(self.request, 'Schedule has been created successfully.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Add doctors to context for admin users."""
        context = super().get_context_data(**kwargs)
        if self.request.user.is_admin:
            context['doctors'] = User.objects.filter(role__name='doctor')
        return context


class DoctorScheduleUpdateView(LoginRequiredMixin, UpdateView):
    """Update view for doctor schedules."""
    
    model = DoctorSchedule
    template_name = 'appointments/doctor_schedule_form.html'
    fields = ['day_of_week', 'start_time', 'end_time', 'break_start_time', 'break_end_time', 'max_appointments']
    success_url = reverse_lazy('appointments:schedule')
    
    def get_queryset(self):
        """Ensure users can only edit appropriate schedules."""
        user = self.request.user
        
        if user.is_doctor:
            return DoctorSchedule.objects.filter(doctor=user)
        elif user.is_admin:
            return DoctorSchedule.objects.all()
        else:
            return DoctorSchedule.objects.none()


class DoctorScheduleDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for doctor schedules."""
    
    model = DoctorSchedule
    template_name = 'appointments/doctor_schedule_confirm_delete.html'
    success_url = reverse_lazy('appointments:schedule')
    
    def get_queryset(self):
        """Ensure users can only delete appropriate schedules."""
        user = self.request.user
        
        if user.is_doctor:
            return DoctorSchedule.objects.filter(doctor=user)
        elif user.is_admin:
            return DoctorSchedule.objects.all()
        else:
            return DoctorSchedule.objects.none()


# Appointment Status Management Functions
@login_required
def appointment_confirm(request, pk):
    """Confirm an appointment request."""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Only doctors and admins can confirm appointments
    if not (request.user.is_doctor or request.user.is_admin):
        messages.error(request, 'You do not have permission to confirm appointments.')
        return redirect('appointments:list')
    
    try:
        appointment.confirm()
        messages.success(request, 'Appointment has been confirmed.')
    except Exception as e:
        messages.error(request, f'Error confirming appointment: {str(e)}')
    
    return redirect('appointments:detail', pk=pk)


@login_required
def appointment_cancel(request, pk):
    """Cancel an appointment."""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        try:
            appointment.cancel(request.user, reason)
            messages.success(request, 'Appointment has been cancelled.')
            return redirect('appointments:list')
        except Exception as e:
            messages.error(request, f'Error cancelling appointment: {str(e)}')
    
    return render(request, 'appointments/appointment_cancel.html', {'appointment': appointment})


@login_required
def appointment_start(request, pk):
    """Start an appointment."""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Only the assigned doctor can start the appointment
    if request.user != appointment.doctor:
        messages.error(request, 'Only the assigned doctor can start this appointment.')
        return redirect('appointments:list')
    
    try:
        appointment.start()
        messages.success(request, 'Appointment has been started.')
    except Exception as e:
        messages.error(request, f'Error starting appointment: {str(e)}')
    
    return redirect('appointments:detail', pk=pk)


@login_required
def appointment_complete(request, pk):
    """Complete an appointment."""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Only the assigned doctor can complete the appointment
    if request.user != appointment.doctor:
        messages.error(request, 'Only the assigned doctor can complete this appointment.')
        return redirect('appointments:list')
    
    if request.method == 'POST':
        doctor_notes = request.POST.get('doctor_notes', '')
        
        try:
            appointment.complete(doctor_notes)
            messages.success(request, 'Appointment has been completed.')
            return redirect('appointments:list')
        except Exception as e:
            messages.error(request, f'Error completing appointment: {str(e)}')
    
    return render(request, 'appointments/appointment_complete.html', {'appointment': appointment})


# API Views
@login_required
def get_available_slots(request):
    """AJAX endpoint to get available time slots for a doctor on a specific date."""
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    
    if not doctor_id or not date_str:
        return JsonResponse({'error': 'Missing doctor_id or date'}, status=400)
    
    try:
        doctor = User.objects.get(id=doctor_id, role__name='doctor')
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (User.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Invalid doctor or date'}, status=400)
    
    # Get doctor's schedule for this day
    day_of_week = appointment_date.weekday()
    
    try:
        schedule = DoctorSchedule.objects.get(doctor=doctor, day_of_week=day_of_week, is_active=True)
    except DoctorSchedule.DoesNotExist:
        return JsonResponse({'slots': []})
    
    # Generate time slots (30-minute intervals by default)
    slots = []
    current_time = datetime.combine(appointment_date, schedule.start_time)
    end_time = datetime.combine(appointment_date, schedule.end_time)
    
    while current_time < end_time:
        # Skip break time if it exists
        if (schedule.break_start_time and schedule.break_end_time and
            schedule.break_start_time <= current_time.time() < schedule.break_end_time):
            current_time += timedelta(minutes=30)
            continue
        
        # Check if slot is already booked
        existing_appointment = Appointment.objects.filter(
            doctor=doctor,
            scheduled_date=appointment_date,
            scheduled_time=current_time.time(),
            status__in=['requested', 'confirmed', 'in_progress']
        ).exists()
        
        if not existing_appointment:
            slots.append({
                'time': current_time.time().strftime('%H:%M'),
                'display': current_time.time().strftime('%I:%M %p')
            })
        
        current_time += timedelta(minutes=30)
    
    return JsonResponse({'slots': slots})


@login_required
def get_doctor_schedule(request):
    """AJAX endpoint to get a doctor's weekly schedule."""
    doctor_id = request.GET.get('doctor_id')
    
    if not doctor_id:
        return JsonResponse({'error': 'Missing doctor_id'}, status=400)
    
    try:
        doctor = User.objects.get(id=doctor_id, role__name='doctor')
        schedules = DoctorSchedule.objects.filter(doctor=doctor, is_active=True)
        
        schedule_data = []
        for schedule in schedules:
            schedule_data.append({
                'day_of_week': schedule.day_of_week,
                'day_name': dict(DoctorSchedule.WEEKDAY_CHOICES)[schedule.day_of_week],
                'start_time': schedule.start_time.strftime('%H:%M'),
                'end_time': schedule.end_time.strftime('%H:%M'),
                'break_start_time': schedule.break_start_time.strftime('%H:%M') if schedule.break_start_time else None,
                'break_end_time': schedule.break_end_time.strftime('%H:%M') if schedule.break_end_time else None,
                'max_appointments': schedule.max_appointments,
            })
        
        return JsonResponse({'schedule': schedule_data})
    
    except User.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found'}, status=404)