"""
HealthSphere AI - User Views
============================

This module contains views for user authentication and profile management.
Includes login, logout, registration, 2FA, and role-based redirection.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View, TemplateView
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings as django_settings
import json
import pyotp

from .forms import LoginForm, UserRegistrationForm, UserProfileForm, UserUpdateForm
from .models import Role, UserProfile, TwoFactorAuth, AuditLog


def _send_welcome_email(user):
    """Send a welcome / account-verified email using Gmail SMTP."""
    subject = '🎉 Welcome to HealthSphere AI!'
    message = (
        f'Hi {user.get_full_name()},\n\n'
        'Your HealthSphere AI account has been successfully created.\n\n'
        'You can now log in and access your personalised health dashboard.\n\n'
        'Stay healthy,\n'
        'The HealthSphere AI Team'
    )
    html_message = f"""
    <div style="font-family:Inter,sans-serif;max-width:560px;margin:0 auto;">
      <div style="background:linear-gradient(135deg,#6366f1,#3b82f6);padding:28px 32px;border-radius:12px 12px 0 0;">
        <h1 style="color:#fff;margin:0;font-size:1.4rem;">🏥 HealthSphere AI</h1>
      </div>
      <div style="background:#f8fafc;padding:28px 32px;border:1px solid #e2e8f0;border-top:0;border-radius:0 0 12px 12px;">
        <h2 style="color:#1e293b;margin-top:0;">Welcome, {user.get_full_name()}! 👋</h2>
        <p style="color:#475569;">Your account has been created successfully.</p>
        <p style="color:#475569;">You can now log in and access:</p>
        <ul style="color:#475569;line-height:1.8;">
          <li>Your personalised health dashboard</li>
          <li>AI-powered health insights</li>
          <li>Appointment booking</li>
          <li>Secure health records</li>
        </ul>
        <a href="http://localhost:8000/users/login/"
           style="display:inline-block;margin-top:16px;padding:12px 24px;
                  background:linear-gradient(135deg,#6366f1,#3b82f6);
                  color:#fff;text-decoration:none;border-radius:8px;
                  font-weight:600;">Sign In Now →</a>
        <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;">
        <p style="color:#94a3b8;font-size:.85rem;">
          If you didn't create this account, you can safely ignore this email.
        </p>
      </div>
    </div>
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        # Log the error but don't crash registration
        import logging
        logging.getLogger(__name__).warning('Welcome email failed: %s', e)


class LoginView(View):
    """
    Login View
    ==========
    
    Handles user authentication.
    Displays login form and processes login requests.
    """
    
    template_name = 'users/login.html'
    form_class = LoginForm
    
    def get(self, request):
        """Display the login form."""
        # Redirect if already logged in
        if request.user.is_authenticated:
            return redirect('users:redirect_after_login')
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        """Process the login form."""
        form = self.form_class(data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            
            # Handle "remember me" checkbox
            if not form.cleaned_data.get('remember_me'):
                # Session expires when browser closes
                request.session.set_expiry(0)
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            
            # Redirect to the intended page or dashboard
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('users:redirect_after_login')
        
        # Show error message
        messages.error(request, 'Invalid username or password.')
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    """
    Logout View
    ===========
    
    Handles user logout.
    """
    
    def get(self, request):
        """Log out the user."""
        if request.user.is_authenticated:
            messages.info(request, 'You have been logged out successfully.')
            logout(request)
        return redirect('users:login')
    
    def post(self, request):
        """Handle POST logout (for CSRF protection)."""
        return self.get(request)


class RegisterView(View):
    """
    Registration View
    =================
    
    Handles new user registration.
    """
    
    template_name = 'users/register.html'
    form_class = UserRegistrationForm
    
    def get(self, request):
        """Display the registration form."""
        if request.user.is_authenticated:
            return redirect('users:redirect_after_login')
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        """Process the registration form."""
        form = self.form_class(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)

            # Send welcome email (non-blocking — logs warning on failure)
            _send_welcome_email(user)

            messages.success(
                request,
                f'Welcome to HealthSphere AI, {user.get_full_name()}! '
                'Your account has been created. Check your email for confirmation.'
            )
            return redirect('users:redirect_after_login')
        
        return render(request, self.template_name, {'form': form})


@login_required
def redirect_after_login(request):
    """
    Redirect After Login
    ====================
    
    Redirects users to their appropriate dashboard based on their role.
    
    Role-based redirection:
    - Admin → Admin Portal Dashboard
    - Doctor/Nurse → Clinical Portal Dashboard
    - Patient → Patient Portal Dashboard
    """
    user = request.user
    
    if user.is_admin:
        return redirect('admin_portal:dashboard')
    elif user.is_clinical_staff:
        return redirect('clinical_portal:dashboard')
    elif user.is_patient:
        return redirect('patient_portal:dashboard')
    else:
        # Default fallback to profile page
        messages.warning(
            request,
            'Your account does not have a role assigned. '
            'Please contact an administrator.'
        )
        return redirect('users:profile')


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    """
    Profile View
    ============
    
    Displays and allows editing of the current user's profile.
    """
    
    template_name = 'users/profile.html'
    
    def get(self, request):
        """Display the user's profile."""
        # Ensure profile exists
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
        
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Update the user's profile."""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('users:profile')
        
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class TwoFactorSetupView(View):
    """
    Two-Factor Authentication Setup View
    ==================================
    
    Allows users to enable/disable 2FA and generate QR codes for authenticator apps.
    """
    
    template_name = 'users/2fa_setup.html'
    
    def get(self, request):
        """Display 2FA setup page."""
        two_factor_auth, created = TwoFactorAuth.objects.get_or_create(user=request.user)
        
        if created or not two_factor_auth.qr_code:
            two_factor_auth.generate_qr_code()
            two_factor_auth.save()
        
        context = {
            'two_factor_auth': two_factor_auth,
            'backup_codes': two_factor_auth.backup_codes if two_factor_auth.is_enabled else [],
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Handle 2FA enable/disable."""
        action = request.POST.get('action')
        two_factor_auth, _ = TwoFactorAuth.objects.get_or_create(user=request.user)
        
        if action == 'enable':
            token = request.POST.get('token')
            if two_factor_auth.verify_token(token):
                two_factor_auth.is_enabled = True
                two_factor_auth.save()
                
                # Log the 2FA enable action
                AuditLog.objects.create(
                    user=request.user,
                    action='2FA_ENABLE',
                    description='Two-factor authentication enabled',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    success=True
                )
                
                messages.success(request, 'Two-factor authentication has been enabled for your account.')
            else:
                messages.error(request, 'Invalid token. Please try again.')
        
        elif action == 'disable':
            if two_factor_auth.is_enabled:
                two_factor_auth.is_enabled = False
                two_factor_auth.save()
                
                # Clear 2FA verification from session
                request.session.pop('2fa_verified', None)
                
                # Log the 2FA disable action
                AuditLog.objects.create(
                    user=request.user,
                    action='2FA_DISABLE',
                    description='Two-factor authentication disabled',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    success=True
                )
                
                messages.success(request, 'Two-factor authentication has been disabled.')
        
        elif action == 'regenerate_codes':
            if two_factor_auth.is_enabled:
                two_factor_auth.generate_backup_codes()
                two_factor_auth.save()
                messages.success(request, 'New backup codes have been generated.')
        
        return redirect('users:2fa_setup')
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class TwoFactorVerifyView(View):
    """
    Two-Factor Authentication Verification View
    ==========================================
    
    Handles 2FA token verification for authenticated users.
    """
    
    template_name = 'users/2fa_verify.html'
    
    def get(self, request):
        """Display 2FA verification page."""
        if not request.user.is_authenticated:
            return redirect('users:login')
        
        # Check if user has 2FA enabled
        try:
            two_factor_auth = request.user.two_factor_auth
            if not two_factor_auth.is_enabled:
                return redirect('users:redirect_after_login')
        except TwoFactorAuth.DoesNotExist:
            return redirect('users:redirect_after_login')
        
        return render(request, self.template_name)
    
    def post(self, request):
        """Verify 2FA token."""
        if not request.user.is_authenticated:
            return redirect('users:login')
        
        token = request.POST.get('token')
        
        try:
            two_factor_auth = request.user.two_factor_auth
            
            if two_factor_auth.verify_token(token):
                # Mark 2FA as verified in session
                request.session['2fa_verified'] = True
                request.session.set_expiry(86400)  # 24 hours
                
                # Log successful 2FA verification
                AuditLog.objects.create(
                    user=request.user,
                    action='LOGIN',
                    description='Successful 2FA verification',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    success=True
                )
                
                messages.success(request, 'Two-factor authentication verified successfully.')
                return redirect('users:redirect_after_login')
            else:
                # Log failed 2FA attempt
                AuditLog.objects.create(
                    user=request.user,
                    action='FAILED_LOGIN',
                    description='Failed 2FA verification attempt',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    success=False
                )
                
                messages.error(request, 'Invalid token. Please try again.')
        
        except TwoFactorAuth.DoesNotExist:
            messages.error(request, 'Two-factor authentication is not set up for your account.')
            return redirect('users:2fa_setup')
        
        return render(request, self.template_name)
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@method_decorator(login_required, name='dispatch')
class AuditLogView(TemplateView):
    """
    Audit Log View
    =============
    
    Displays audit logs for administrators and allows users to view their own activity.
    """
    
    template_name = 'users/audit_log.html'
    
    def get_context_data(self, **kwargs):
        """Get audit log data."""
        context = super().get_context_data(**kwargs)
        
        # Only admins can view all logs, others can only see their own
        if self.request.user.is_admin:
            audit_logs = AuditLog.objects.all()[:100]  # Limit to recent 100 entries
        else:
            audit_logs = AuditLog.objects.filter(user=self.request.user)[:50]
        
        context['audit_logs'] = audit_logs
        context['is_admin'] = self.request.user.is_admin
        return context
