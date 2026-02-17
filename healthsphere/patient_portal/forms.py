"""
HealthSphere AI - Patient Portal Forms
======================================

Forms for patient self-service features.
"""

from django import forms
from django.utils import timezone
from .models import Appointment, HealthMetric
from users.models import User, Role


class AppointmentForm(forms.ModelForm):
    """
    Appointment Booking Form
    ========================
    
    Form for patients to book appointments.
    """
    
    class Meta:
        model = Appointment
        fields = [
            'doctor', 'appointment_type', 'appointment_date',
            'appointment_time', 'reason', 'is_telemedicine'
        ]
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'appointment_type': forms.Select(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'appointment_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Please describe the reason for your visit...'
            }),
            'is_telemedicine': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show doctors in the dropdown
        self.fields['doctor'].queryset = User.objects.filter(
            role__name=Role.DOCTOR,
            is_active=True
        ).order_by('last_name', 'first_name')
        self.fields['doctor'].label_from_instance = lambda obj: f"Dr. {obj.get_full_name()}"
    
    def clean_appointment_date(self):
        """Validate appointment date is in the future."""
        date = self.cleaned_data.get('appointment_date')
        if date and date < timezone.now().date():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        return date


class HealthMetricForm(forms.ModelForm):
    """
    Health Metric Entry Form
    ========================
    
    Form for patients to log health metrics.
    """
    
    class Meta:
        model = HealthMetric
        fields = ['metric_type', 'value', 'secondary_value', 'notes']
        widgets = {
            'metric_type': forms.Select(attrs={'class': 'form-control'}),
            'value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Enter value'
            }),
            'secondary_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Secondary value (optional)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any additional notes...'
            }),
        }
    
    def clean(self):
        """Validate metric values."""
        cleaned_data = super().clean()
        metric_type = cleaned_data.get('metric_type')
        value = cleaned_data.get('value')
        secondary_value = cleaned_data.get('secondary_value')
        
        # Blood pressure requires two values
        if metric_type == 'blood_pressure' and not secondary_value:
            raise forms.ValidationError(
                "Blood pressure requires both systolic and diastolic values."
            )
        
        # Validate reasonable ranges
        if value is not None:
            if metric_type == 'weight' and (value < 1 or value > 500):
                raise forms.ValidationError("Please enter a valid weight in kg.")
            elif metric_type == 'heart_rate' and (value < 20 or value > 300):
                raise forms.ValidationError("Please enter a valid heart rate.")
            elif metric_type == 'temperature' and (value < 30 or value > 45):
                raise forms.ValidationError("Please enter a valid temperature in Celsius.")
        
        return cleaned_data


class ReportUploadForm(forms.Form):
    """
    Report Upload Form
    ==================
    
    Form for uploading medical reports for AI analysis.
    """
    
    report_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
        }),
        help_text='Upload your medical report (PDF, Image, or Document)'
    )
    
    report_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Or paste the text from your medical report here...'
        }),
        help_text='Alternatively, paste the report text directly'
    )
    
    report_type = forms.ChoiceField(
        choices=[
            ('lab', 'Lab Results'),
            ('imaging', 'Imaging Report'),
            ('prescription', 'Prescription'),
            ('discharge', 'Discharge Summary'),
            ('other', 'Other'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        """Ensure either file or text is provided."""
        cleaned_data = super().clean()
        report_file = cleaned_data.get('report_file')
        report_text = cleaned_data.get('report_text')
        
        if not report_file and not report_text:
            raise forms.ValidationError(
                "Please either upload a file or paste the report text."
            )
        
        return cleaned_data
