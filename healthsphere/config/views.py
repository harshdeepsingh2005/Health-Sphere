from django.shortcuts import render


def search(request):
    q = request.GET.get('q', '').strip()
    # Minimal placeholder search logic: echo query and return empty results
    results = []
    if q:
        # In future, plug real search here (database, elastic, etc.)
        results = []
    return render(request, 'search_results.html', {'query': q, 'results': results})


def settings(request):
    """Settings page — passes 2FA status for all roles."""
    from django.contrib.auth.decorators import login_required
    from users.models import TwoFactorAuth

    two_factor_auth = None
    if request.user.is_authenticated:
        two_factor_auth, _ = TwoFactorAuth.objects.get_or_create(user=request.user)
        # Ensure QR code exists if not yet set up
        if not two_factor_auth.qr_code:
            two_factor_auth.generate_qr_code()
            two_factor_auth.save()

    return render(request, 'settings.html', {
        'two_factor_auth': two_factor_auth,
        'backup_codes': two_factor_auth.backup_codes if two_factor_auth and two_factor_auth.is_enabled else [],
    })


