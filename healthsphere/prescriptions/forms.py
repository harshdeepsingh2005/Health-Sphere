"""
HealthSphere AI - E-Prescriptions Forms
======================================

Django forms for prescription management and drug safety.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from .models import (
    MedicationDatabase,
    DrugAllergy,
    Prescription,
    Pharmacy,
    PrescriptionRefill,
    DrugInteraction
)

User = get_user_model()


class MedicationSearchForm(forms.Form):
    """Form for searching medications in the database."""
    
    search_query = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by drug name, NDC code, or manufacturer...',
            'class': 'form-control',
            'autofocus': True
        })
    )
    
    drug_class = forms.ChoiceField(
        choices=[('', 'All Classes')] + MedicationDatabase.DRUG_CLASSES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    dosage_form = forms.ChoiceField(
        choices=[('', 'All Forms')] + MedicationDatabase.DOSAGE_FORMS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    controlled_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Show only controlled substances"
    )


class DrugAllergyForm(forms.ModelForm):
    """Form for recording patient drug allergies."""
    
    class Meta:
        model = DrugAllergy
        fields = [
            'medication', 'drug_class', 'reaction_type', 'severity',
            'symptoms', 'notes'
        ]
        widgets = {
            'medication': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select medication...'
            }),
            'drug_class': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter drug class if no specific medication...'
            }),
            'reaction_type': forms.Select(attrs={'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the allergic reaction symptoms...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes...'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        medication = cleaned_data.get('medication')
        drug_class = cleaned_data.get('drug_class')
        
        if not medication and not drug_class:
            raise ValidationError(
                "Please specify either a specific medication or a drug class."
            )
        
        return cleaned_data


class PrescriptionForm(forms.ModelForm):
    """Form for creating and editing prescriptions."""
    
    class Meta:
        model = Prescription
        fields = [
            'patient', 'medication', 'dosage_instructions', 'quantity',
            'days_supply', 'refills_authorized', 'diagnosis_code',
            'diagnosis_description', 'indication', 'priority',
            'pharmacy', 'pharmacy_notes', 'patient_instructions'
        ]
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-control',
                'data-live-search': 'true'
            }),
            'medication': forms.Select(attrs={
                'class': 'form-control',
                'data-live-search': 'true'
            }),
            'dosage_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g., Take 1 tablet by mouth twice daily with food'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Quantity to dispense'
            }),
            'days_supply': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Expected days of therapy'
            }),
            'refills_authorized': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 5,
                'placeholder': 'Number of refills (0-5)'
            }),
            'diagnosis_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ICD-10 code (e.g., Z00.00)'
            }),
            'diagnosis_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Diagnosis description'
            }),
            'indication': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Medical reason for prescribing this medication'
            }),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'pharmacy': forms.Select(attrs={
                'class': 'form-control',
                'data-live-search': 'true'
            }),
            'pharmacy_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Special instructions for pharmacist'
            }),
            'patient_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Patient counseling and special instructions'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.prescriber = kwargs.pop('prescriber', None)
        super().__init__(*args, **kwargs)
        
        # Filter patients to only active patients
        self.fields['patient'].queryset = User.objects.filter(
            is_active=True, is_patient=True
        ).order_by('last_name', 'first_name')
        
        # Filter medications to only active ones
        self.fields['medication'].queryset = MedicationDatabase.objects.filter(
            is_active=True
        ).order_by('generic_name')
        
        # Filter pharmacies to only active ones
        self.fields['pharmacy'].queryset = Pharmacy.objects.filter(
            is_active=True
        ).order_by('name')
        
        # Set initial pharmacy to patient's preferred if available
        if self.instance.pk and hasattr(self.instance.patient, 'profile'):
            preferred_pharmacy = getattr(self.instance.patient.profile, 'preferred_pharmacy', None)
            if preferred_pharmacy:
                self.fields['pharmacy'].initial = preferred_pharmacy
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        return quantity
    
    def clean_days_supply(self):
        days_supply = self.cleaned_data.get('days_supply')
        if days_supply and days_supply <= 0:
            raise ValidationError("Days supply must be greater than zero.")
        return days_supply
    
    def clean_refills_authorized(self):
        refills = self.cleaned_data.get('refills_authorized')
        medication = self.cleaned_data.get('medication')
        
        if refills < 0:
            raise ValidationError("Refills cannot be negative.")
        
        if refills > 5:
            raise ValidationError("Maximum 5 refills allowed.")
        
        # Check controlled substance restrictions
        if medication and medication.is_controlled_substance:
            schedule = medication.controlled_substance_schedule
            if schedule in ['CI', 'CII'] and refills > 0:
                raise ValidationError(
                    f"Schedule {schedule} medications cannot have refills."
                )
            elif schedule in ['CIII', 'CIV', 'CV'] and refills > 5:
                raise ValidationError(
                    f"Schedule {schedule} medications limited to 5 refills."
                )
        
        return refills
    
    def clean(self):
        cleaned_data = super().clean()
        medication = cleaned_data.get('medication')
        patient = cleaned_data.get('patient')
        
        if medication and patient:
            # Check for drug allergies
            allergies = DrugAllergy.objects.filter(
                patient=patient,
                is_active=True
            )
            
            # Check specific medication allergy
            med_allergy = allergies.filter(medication=medication).first()
            if med_allergy:
                raise ValidationError(
                    f"Patient has a {med_allergy.severity} allergy to {medication}. "
                    f"Symptoms: {med_allergy.symptoms}"
                )
            
            # Check drug class allergies
            class_allergy = allergies.filter(
                drug_class__iexact=medication.drug_class
            ).first()
            if class_allergy:
                raise ValidationError(
                    f"Patient has a {class_allergy.severity} allergy to "
                    f"{class_allergy.drug_class} class medications."
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        prescription = super().save(commit=False)
        if self.prescriber:
            prescription.prescriber = self.prescriber
        
        # Set expiration date based on medication type
        if not prescription.expiration_date:
            if prescription.medication.is_controlled_substance:
                if prescription.medication.controlled_substance_schedule in ['CI', 'CII']:
                    prescription.expiration_date = timezone.now() + timedelta(days=90)
                else:
                    prescription.expiration_date = timezone.now() + timedelta(days=180)
            else:
                prescription.expiration_date = timezone.now() + timedelta(days=365)
        
        if commit:
            prescription.save()
        return prescription


class PrescriptionRefillForm(forms.ModelForm):
    """Form for prescription refill requests."""
    
    class Meta:
        model = PrescriptionRefill
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes about this refill request...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.prescription = kwargs.pop('prescription', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.prescription:
            if not self.prescription.can_be_refilled:
                if self.prescription.is_expired:
                    raise ValidationError(
                        "This prescription has expired. A new prescription is required."
                    )
                elif not self.prescription.has_refills_remaining:
                    raise ValidationError(
                        "No refills remaining. A new prescription is required."
                    )
                else:
                    raise ValidationError("This prescription cannot be refilled.")
        
        return cleaned_data


class PharmacyForm(forms.ModelForm):
    """Form for pharmacy information."""
    
    class Meta:
        model = Pharmacy
        fields = [
            'name', 'pharmacy_type', 'ncpdp_id', 'npi_number',
            'phone', 'fax', 'email', 'website',
            'address_line_1', 'address_line_2', 'city', 'state', 'zip_code',
            'accepts_electronic_prescriptions', 'supports_controlled_substances'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'pharmacy_type': forms.Select(attrs={'class': 'form-control'}),
            'ncpdp_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '7-digit NCPDP ID'
            }),
            'npi_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10-digit NPI number'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(555) 123-4567'
            }),
            'fax': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(555) 123-4567'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'pharmacy@example.com'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.pharmacy.com'
            }),
            'address_line_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address'
            }),
            'address_line_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Suite, unit, etc. (optional)'
            }),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State abbreviation (e.g., CA)'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345 or 12345-6789'
            }),
            'accepts_electronic_prescriptions': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'supports_controlled_substances': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_ncpdp_id(self):
        ncpdp_id = self.cleaned_data.get('ncpdp_id')
        if ncpdp_id and len(ncpdp_id) != 7:
            raise ValidationError("NCPDP ID must be exactly 7 digits.")
        return ncpdp_id
    
    def clean_npi_number(self):
        npi_number = self.cleaned_data.get('npi_number')
        if npi_number and len(npi_number) != 10:
            raise ValidationError("NPI number must be exactly 10 digits.")
        return npi_number


class InteractionCheckForm(forms.Form):
    """Form for checking drug-drug interactions."""
    
    medications = forms.ModelMultipleChoiceField(
        queryset=MedicationDatabase.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text="Select medications to check for interactions"
    )
    
    def __init__(self, *args, **kwargs):
        patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)
        
        if patient:
            # Pre-populate with patient's current prescriptions
            current_meds = Prescription.objects.filter(
                patient=patient,
                status__in=['approved', 'transmitted', 'filled']
            ).values_list('medication_id', flat=True)
            
            self.fields['medications'].initial = current_meds
    
    def clean_medications(self):
        medications = self.cleaned_data.get('medications')
        if len(medications) < 2:
            raise ValidationError("Select at least 2 medications to check for interactions.")
        return medications