"""
HealthSphere AI - User Admin Configuration
==========================================

Registers User models with Django admin for easy management.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, UserProfile


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin configuration for Role model."""
    
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile within User admin."""
    
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model."""
    
    # Display these fields in the user list
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'role', 'is_verified', 'is_active', 'created_at'
    )
    
    # Filter options in the sidebar
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff', 'created_at')
    
    # Search fields
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    
    # Ordering
    ordering = ('-created_at',)
    
    # Add the profile inline
    inlines = [UserProfileInline]
    
    # Fieldsets for the edit page
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'address')
        }),
        ('Role & Status', {
            'fields': ('role', 'is_verified')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets for the add user page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'role', 'password1', 'password2'
            ),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model."""
    
    list_display = ('user', 'department', 'specialization', 'blood_type', 'created_at')
    list_filter = ('department', 'blood_type')
    search_fields = ('user__username', 'user__email', 'department', 'specialization')
    ordering = ('-created_at',)
