"""
HealthSphere AI - User Views
============================

This module contains views for user authentication and profile management.
Includes login, logout, registration, and role-based redirection.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View, TemplateView
from django.utils.decorators import method_decorator

from .forms import LoginForm, UserRegistrationForm, UserProfileForm, UserUpdateForm
from .models import Role, UserProfile


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
            messages.success(
                request,
                f'Welcome to HealthSphere AI, {user.get_full_name()}! '
                'Your account has been created successfully.'
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
