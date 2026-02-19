from django.views.generic import TemplateView

class AIInsightsView(TemplateView):
    template_name = "ai_services/insights.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["insights"] = [
            "AI-powered patient risk prediction",
            "Automated triage recommendations",
            "Clinical decision support",
        ]
        return context


class AIAssistantView(TemplateView):
    template_name = "ai_services/assistant.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assistant_features'] = [
            'Symptom checker',
            'Medication guidance',
            'Appointment triage helper',
        ]
        return context
