"""
HealthSphere AI - Authentication Middleware
==========================================

Middleware for handling 2FA requirements and audit logging.
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest
from users.models import AuditLog


class TwoFactorAuthMiddleware(MiddlewareMixin):
    """
    Middleware to enforce 2FA for users who have it enabled.
    """
    
    # URLs that don't require 2FA verification
    EXEMPT_URLS = [
        '/users/login/',
        '/users/logout/',
        '/users/2fa-setup/',
        '/users/2fa-verify/',
        '/admin/login/',
        '/static/',
        '/media/',
    ]
    
    def process_request(self, request):
        """Check if 2FA verification is required."""
        if not request.user.is_authenticated:
            return None
        
        # Skip 2FA check for exempt URLs
        path = request.path
        for exempt_url in self.EXEMPT_URLS:
            if path.startswith(exempt_url):
                return None
        
        # Check if user has 2FA enabled
        if hasattr(request.user, 'two_factor_auth'):
            two_factor = request.user.two_factor_auth
            if two_factor.is_enabled:
                # Check if user has completed 2FA verification in this session
                if not request.session.get('2fa_verified', False):
                    messages.warning(
                        request,
                        'Two-factor authentication is required. Please verify your identity.'
                    )
                    return redirect('users:2fa_verify')
        
        return None


class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log user actions for audit purposes.
    """
    
    def process_request(self, request):
        """Set up request context for audit logging."""
        # Store the current user in the request for signal handlers
        if hasattr(request, 'user') and request.user.is_authenticated:
            request._audit_user = request.user
            request._audit_ip = self.get_client_ip(request)
            request._audit_user_agent = request.META.get('HTTP_USER_AGENT', '')
        return None
    
    def process_response(self, request, response):
        """Log successful requests."""
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Log certain actions based on HTTP method and path
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                action_map = {
                    'POST': 'CREATE',
                    'PUT': 'UPDATE',
                    'PATCH': 'UPDATE',
                    'DELETE': 'DELETE'
                }
                
                action = action_map.get(request.method, 'READ')
                
                # Determine resource type from URL path
                resource_type = self.get_resource_type_from_path(request.path)
                
                # Only log if we can determine the resource type
                if resource_type:
                    AuditLog.objects.create(
                        user=request.user,
                        action=action,
                        resource_type=resource_type,
                        description=f"{action} action on {resource_type} via {request.method} {request.path}",
                        ip_address=self.get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        success=(200 <= response.status_code < 400)
                    )
        
        return response
    
    def get_client_ip(self, request):
        """Get the client's IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_resource_type_from_path(self, path):
        """Determine resource type from URL path."""
        path_mappings = {
            '/admin-portal/': 'Admin',
            '/clinical/': 'Clinical',
            '/patient/': 'Patient',
            '/appointments/': 'Appointment',
            '/users/': 'User',
        }
        
        for url_pattern, resource_type in path_mappings.items():
            if path.startswith(url_pattern):
                return resource_type
        
        return None