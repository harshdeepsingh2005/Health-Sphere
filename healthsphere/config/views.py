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
    # Minimal settings placeholder
    return render(request, 'settings.html', {})
