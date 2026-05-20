from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def telemedicine_dashboard(request):
    """Telemedicine dashboard."""
    return render(request, 'telemedicine/dashboard.html')
