#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the path
sys.path.append('/Users/harsheeepsingh/Documents/GitHub/Health-Sphere/healthsphere')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import Role

User = get_user_model()

# Check what roles exist
print('Available roles:')
for role in Role.objects.all():
    print(f'  {role.name}: {role.description}')

# Get our test user
try:
    user = User.objects.get(username='testpatient')
    print(f'\nCurrent user: {user.username}, Role: {user.role}')
    
    # Try to assign patient role
    try:
        patient_role = Role.objects.get(name='Patient')
        user.role = patient_role
        user.save()
        print(f'✅ Assigned Patient role to {user.username}')
    except Role.DoesNotExist:
        print('❌ Patient role does not exist, checking other roles...')
        # Try to create patient role or assign first available role
        if Role.objects.exists():
            first_role = Role.objects.first()
            user.role = first_role
            user.save()
            print(f'✅ Assigned {first_role.name} role to {user.username}')
        else:
            print('❌ No roles exist in database')
            
except User.DoesNotExist:
    print('❌ User testpatient does not exist')