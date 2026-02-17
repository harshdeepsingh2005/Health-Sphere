"""
HealthSphere AI - User Forms
============================

This module contains Django forms for user authentication and registration.
Forms handle validation and cleaning of user input data.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Role, UserProfile

# Get the custom User model
User = get_user_model()


class LoginForm(AuthenticationForm):
    """
    Login Form
    ==========
    
    Custom login form with styled fields for the HealthSphere AI platform.
    Extends Django's built-in AuthenticationForm.
    """
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    # Remember me checkbox
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class UserRegistrationForm(UserCreationForm):
    """
    User Registration Form
    ======================
    
    Form for creating new user accounts.
    Includes fields for basic user information and role selection.
    """
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        empty_label='Select Role'
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone', 'role', 'password1', 'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add styling to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    
    def save(self, commit=True):
        """Save the user with additional fields."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data.get('phone', '')
        user.role = self.cleaned_data['role']
        
        if commit:
            user.save()
            # Create associated UserProfile
            UserProfile.objects.create(user=user)
        
        return user


class UserProfileForm(forms.ModelForm):
    """
    User Profile Form
    =================
    
    Form for editing user profile information.
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'employee_id', 'department', 'specialization',
            'emergency_contact_name', 'emergency_contact_phone',
            'blood_type', 'allergies', 'medical_notes'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_type': forms.TextInput(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medical_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class UserUpdateForm(forms.ModelForm):
    """
    User Update Form
    ================
    
    Form for updating basic user information.
    """
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
