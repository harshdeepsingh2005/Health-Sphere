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
import secrets
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import pyotp


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


class TwoFactorAuth(models.Model):
    """
    Two-Factor Authentication Model
    ===============================
    
    Handles 2FA settings and backup codes for users who enable
    two-factor authentication for enhanced security.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='two_factor_auth',
        help_text='User associated with this 2FA setup'
    )
    
    secret_key = models.CharField(
        max_length=32,
        help_text='Base32 encoded secret key for TOTP'
    )
    
    is_enabled = models.BooleanField(
        default=False,
        help_text='Whether 2FA is currently enabled for this user'
    )
    
    backup_codes = models.JSONField(
        default=list,
        help_text='List of backup codes for account recovery'
    )
    
    qr_code = models.ImageField(
        upload_to='qr_codes/',
        null=True,
        blank=True,
        help_text='QR code image for initial setup'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Two Factor Authentication'
        verbose_name_plural = 'Two Factor Authentications'
    
    def __str__(self):
        return f"2FA for {self.user.username} ({'Enabled' if self.is_enabled else 'Disabled'})"
    
    def save(self, *args, **kwargs):
        """Generate secret key and backup codes if not present."""
        if not self.secret_key:
            self.secret_key = pyotp.random_base32()
            self.generate_backup_codes()
        super().save(*args, **kwargs)
    
    def generate_backup_codes(self, count=10):
        """Generate backup codes for account recovery."""
        self.backup_codes = [secrets.token_hex(4).upper() for _ in range(count)]
    
    def generate_qr_code(self):
        """Generate QR code for authenticator app setup."""
        totp_uri = pyotp.totp.TOTP(self.secret_key).provisioning_uri(
            name=self.user.email,
            issuer_name="HealthSphere AI"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        file_name = f'qr_{self.user.username}_{secrets.token_hex(4)}.png'
        self.qr_code.save(file_name, File(buffer), save=False)
    
    def verify_token(self, token):
        """Verify TOTP token or backup code."""
        # Try TOTP first
        totp = pyotp.TOTP(self.secret_key)
        if totp.verify(token, valid_window=2):
            return True
        
        # Try backup codes
        if token.upper() in self.backup_codes:
            self.backup_codes.remove(token.upper())
            self.save()
            return True
        
        return False


class AuditLog(models.Model):
    """
    Audit Log Model
    ===============
    
    Tracks all user actions and data access for compliance
    and security monitoring. Critical for HIPAA compliance.
    """
    
    ACTION_CHOICES = [
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('CREATE', 'Record Created'),
        ('READ', 'Record Accessed'),
        ('UPDATE', 'Record Modified'),
        ('DELETE', 'Record Deleted'),
        ('EXPORT', 'Data Exported'),
        ('PRINT', 'Data Printed'),
        ('SHARE', 'Data Shared'),
        ('2FA_ENABLE', '2FA Enabled'),
        ('2FA_DISABLE', '2FA Disabled'),
        ('PASSWORD_CHANGE', 'Password Changed'),
        ('FAILED_LOGIN', 'Failed Login Attempt'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        help_text='User who performed the action'
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text='Type of action performed'
    )
    
    resource_type = models.CharField(
        max_length=50,
        blank=True,
        help_text='Type of resource accessed (e.g., Patient, Appointment)'
    )
    
    resource_id = models.CharField(
        max_length=50,
        blank=True,
        help_text='ID of the specific resource accessed'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Detailed description of the action'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address from which action was performed'
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text='User agent string from the request'
    )
    
    success = models.BooleanField(
        default=True,
        help_text='Whether the action was successful'
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text='When the action was performed'
    )
    
    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} by {self.user} at {self.timestamp}"
