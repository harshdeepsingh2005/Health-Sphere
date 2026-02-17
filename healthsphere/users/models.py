"""
HealthSphere AI - User Models
=============================

This module defines the User model and related models for authentication
and role-based access control in the HealthSphere AI platform.

Models:
- Role: Defines user roles (Admin, Doctor, Nurse, Patient)
- User: Custom user model extending Django's AbstractUser
- UserProfile: Extended user information
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Role(models.Model):
    """
    Role Model
    ==========
    
    Defines the different user roles in the healthcare system.
    Each user is assigned one role that determines their portal access.
    
    Roles:
    - ADMIN: Hospital administrators
    - DOCTOR: Medical doctors
    - NURSE: Nursing staff
    - PATIENT: Registered patients
    """
    
    # Role choices as constants for easy reference
    ADMIN = 'admin'
    DOCTOR = 'doctor'
    NURSE = 'nurse'
    PATIENT = 'patient'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrator'),
        (DOCTOR, 'Doctor'),
        (NURSE, 'Nurse'),
        (PATIENT, 'Patient'),
    ]
    
    # Fields
    name = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        unique=True,
        help_text='The role name'
    )
    description = models.TextField(
        blank=True,
        help_text='Description of the role and its permissions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['name']
    
    def __str__(self):
        """String representation of the role."""
        return self.get_name_display()


class User(AbstractUser):
    """
    Custom User Model
    =================
    
    Extends Django's AbstractUser to add healthcare-specific fields.
    This is the main authentication model for HealthSphere AI.
    
    Additional Fields:
    - role: The user's role in the system
    - phone: Contact phone number
    - date_of_birth: User's date of birth
    - is_verified: Whether the account is verified
    """
    
    # Link to the Role model
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        help_text='The role assigned to this user'
    )
    
    # Additional user fields
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text='Contact phone number'
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text='Date of birth'
    )
    address = models.TextField(
        blank=True,
        help_text='Home address'
    )
    is_verified = models.BooleanField(
        default=False,
        help_text='Whether the user account is verified'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        """String representation of the user."""
        return f"{self.get_full_name()} ({self.username})"
    
    def get_full_name(self):
        """Return the user's full name."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username
    
    @property
    def is_admin(self):
        """Check if user is an administrator."""
        return self.role and self.role.name == Role.ADMIN
    
    @property
    def is_doctor(self):
        """Check if user is a doctor."""
        return self.role and self.role.name == Role.DOCTOR
    
    @property
    def is_nurse(self):
        """Check if user is a nurse."""
        return self.role and self.role.name == Role.NURSE
    
    @property
    def is_patient(self):
        """Check if user is a patient."""
        return self.role and self.role.name == Role.PATIENT
    
    @property
    def is_clinical_staff(self):
        """Check if user is clinical staff (doctor or nurse)."""
        return self.is_doctor or self.is_nurse
    
    def get_dashboard_url(self):
        """
        Get the appropriate dashboard URL based on user role.
        
        Returns:
            str: URL path to the user's dashboard
        """
        if self.is_admin:
            return '/admin-portal/dashboard/'
        elif self.is_clinical_staff:
            return '/clinical/dashboard/'
        elif self.is_patient:
            return '/patient/dashboard/'
        else:
            return '/users/profile/'


class UserProfile(models.Model):
    """
    User Profile Model
    ==================
    
    Stores extended information about users that doesn't fit
    in the main User model. This allows for flexible additional
    data without modifying the core user model.
    
    Fields vary based on user role:
    - Staff: employee ID, department, specialization
    - Patients: emergency contact, blood type, allergies
    """
    
    # Link to the User model (one-to-one relationship)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text='The user this profile belongs to'
    )
    
    # Profile picture
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text='Profile picture'
    )
    
    # Staff-specific fields
    employee_id = models.CharField(
        max_length=50,
        blank=True,
        help_text='Employee ID (for staff)'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text='Department (for staff)'
    )
    specialization = models.CharField(
        max_length=100,
        blank=True,
        help_text='Medical specialization (for doctors)'
    )
    
    # Patient-specific fields
    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Emergency contact name'
    )
    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text='Emergency contact phone'
    )
    blood_type = models.CharField(
        max_length=10,
        blank=True,
        help_text='Blood type (e.g., A+, B-, O+)'
    )
    allergies = models.TextField(
        blank=True,
        help_text='Known allergies'
    )
    medical_notes = models.TextField(
        blank=True,
        help_text='Additional medical notes'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        """String representation of the profile."""
        return f"Profile for {self.user.username}"
