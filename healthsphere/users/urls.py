"""
HealthSphere AI - User URL Configuration
========================================

URL patterns for user authentication and profile management.
"""

from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

# Namespace for the users app
app_name = 'users'

urlpatterns = [
    # ==========================================================================
    # AUTHENTICATION
    # ==========================================================================
    
    # Login page
    path('login/', views.LoginView.as_view(), name='login'),
    
    # Logout
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Password reset URLs (using Django's built-in views)
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset_form.html',
        email_template_name='users/password_reset_email.html',
        subject_template_name='users/password_reset_subject.txt',
        success_url='/users/password_reset/done/'
    ), name='password_reset'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
        success_url='/users/reset/done/'
    ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Registration
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # ==========================================================================
    # TWO-FACTOR AUTHENTICATION
    # ==========================================================================
    
    # 2FA Setup and Management
    path('2fa-setup/', views.TwoFactorSetupView.as_view(), name='2fa_setup'),
    
    # 2FA Verification
    path('2fa-verify/', views.TwoFactorVerifyView.as_view(), name='2fa_verify'),
    
    # ==========================================================================
    # PROFILE
    # ==========================================================================
    
    # User profile page
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # ==========================================================================
    # AUDIT & SECURITY
    # ==========================================================================
    
    # Audit log for users and admins
    path('audit-log/', views.AuditLogView.as_view(), name='audit_log'),
    
    # ==========================================================================
    # REDIRECTION
    # ==========================================================================
    
    # Role-based redirect after login
    path('redirect/', views.redirect_after_login, name='redirect_after_login'),
]
