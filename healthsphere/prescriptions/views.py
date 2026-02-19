from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def prescriptions_dashboard(request):
    """E-prescriptions dashboard."""
    return render(request, 'prescriptions/dashboard.html')
