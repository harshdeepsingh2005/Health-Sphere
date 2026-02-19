"""
HealthSphere AI - AI Services Views (Ollama-powered)
=====================================================

Provides:
  - AI Insights dashboard
  - AI Assistant (Ollama chat, AJAX endpoint)
  - Health risk analysis API
  - Report explanation API
"""

import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .gemini_client import generate_text, is_available, quota_status
from .risk_service import predict_risk, get_risk_factors
from .report_explainer import explain_report, simplify_medical_terms
from .journey_service import get_patient_ai_insights, get_patient_journey_summary

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# System prompt for the HealthSphere AI assistant
# ---------------------------------------------------------------------------

ASSISTANT_SYSTEM_PROMPT = """You are HealthSphere Assistant, a compassionate and knowledgeable AI health companion integrated into the HealthSphere hospital management platform.

Your role:
- Provide general health information and guidance to patients
- Help patients understand their symptoms (but always recommend seeing a doctor for diagnosis)
- Explain medical terms in plain English
- Give wellness tips and lifestyle advice
- Help patients prepare questions for their doctor
- Remind patients about the importance of medication adherence

Important rules:
- NEVER diagnose specific conditions or replace professional medical advice
- Always recommend consulting a doctor for serious symptoms
- Be warm, empathetic, and encouraging
- Keep responses concise (2-4 paragraphs max)
- Use bullet points for lists
- If asked about HealthSphere features, explain them helpfully

You have access to the HealthSphere platform which includes: appointment booking, prescription management, vital records, medical records, and AI health insights.
"""


# ---------------------------------------------------------------------------
# HTML Views
# ---------------------------------------------------------------------------

@login_required
def ai_insights_view(request):
    """AI Insights dashboard page."""
    user = request.user
    qs = quota_status()

    # Gather real insights
    ai_insights = get_patient_ai_insights(user)
    risk_data = predict_risk(user)
    risk_factors = get_risk_factors(user)
    journey = get_patient_journey_summary(user)

    context = {
        'page_title': 'AI Health Insights',
        'gemini_available': is_available(),
        'gemini_configured': qs['configured'],
        'gemini_quota_exhausted': qs['quota_exhausted'],
        'ai_insights': ai_insights,
        'risk_data': risk_data,
        'risk_factors': risk_factors,
        'journey': journey,
        'current_time': timezone.now(),
    }
    return render(request, 'ai_services/insights.html', context)



@login_required
def ai_assistant_view(request):
    """AI Assistant chat interface."""
    qs = quota_status()
    context = {
        'page_title': 'HealthSphere AI Assistant',
        'gemini_available': is_available(),
        'gemini_configured': qs['configured'],
        'gemini_quota_exhausted': qs['quota_exhausted'],
        'assistant_features': [
            {'icon': 'fas fa-stethoscope', 'title': 'Symptom Guidance', 'desc': 'Describe symptoms and get general guidance'},
            {'icon': 'fas fa-pills', 'title': 'Medication Info', 'desc': 'Learn about your medications and dosages'},
            {'icon': 'fas fa-flask', 'title': 'Report Explanation', 'desc': 'Understand your lab results in plain English'},
            {'icon': 'fas fa-heartbeat', 'title': 'Health Tips', 'desc': 'Personalised wellness and lifestyle advice'},
            {'icon': 'fas fa-calendar-check', 'title': 'Appointment Prep', 'desc': 'Prepare questions for your doctor visit'},
            {'icon': 'fas fa-brain', 'title': 'Risk Insights', 'desc': 'Understand your health risk factors'},
        ],
    }
    return render(request, 'ai_services/assistant.html', context)



# ---------------------------------------------------------------------------
# AJAX Endpoints
# ---------------------------------------------------------------------------

@login_required
@require_http_methods(['POST'])
def ai_chat_api(request):
    """
    AJAX endpoint for the AI assistant chat.
    POST body: { "message": "<user message>", "history": [{"role": "...", "text": "..."}] }
    Response: { "reply": "<assistant reply>", "ai_powered": true }
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        history = data.get('history', [])

        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        if not is_available():
            msg = (
                "⚠️ The AI service (Ollama) is not reachable right now. "
                "Make sure Ollama is running locally.\n\n"
                "In the meantime, here are some quick health tips:\n"
                "• 💧 Stay hydrated — aim for 8 glasses of water daily\n"
                "• 💊 Take medications as prescribed without skipping doses\n"
                "• 📅 Book upcoming appointments via the Appointments section\n"
                "• 🏃 Even a 20-minute walk can significantly boost your health\n\n"
                "For urgent medical concerns, please contact your healthcare provider directly."
            )
            return JsonResponse({'reply': msg, 'ai_powered': False})



        # Build patient context for the system prompt
        user = request.user
        system = (
            ASSISTANT_SYSTEM_PROMPT
            + f"\n\nCurrent patient: {user.get_full_name() or user.username}."
        )

        # Use Ollama's native multi-turn history (pass last 10 turns)
        reply = generate_text(
            prompt=user_message,
            system_instruction=system,
            history=history[-10:],
        )

        if not reply:
            reply = (
                "I'm having trouble connecting to the AI service right now. "
                "Please try again in a moment, or contact your healthcare team for assistance."
            )

        return JsonResponse({'reply': reply.strip(), 'ai_powered': True})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as exc:
        logger.error(f"AI chat error: {exc}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
@require_http_methods(['POST'])
def explain_report_api(request):
    """
    AJAX endpoint to explain a medical report.
    POST body: { "report_text": "<medical report text>" }
    """
    try:
        data = json.loads(request.body)
        report_text = data.get('report_text', '').strip()

        if not report_text:
            return JsonResponse({'error': 'report_text is required'}, status=400)

        result = explain_report(report_text)
        return JsonResponse(result)

    except Exception as exc:
        logger.error(f"Explain report error: {exc}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
@require_http_methods(['GET'])
def risk_assessment_api(request):
    """
    AJAX endpoint to get the current user's risk assessment.
    """
    try:
        result = predict_risk(request.user)
        return JsonResponse(result)
    except Exception as exc:
        logger.error(f"Risk assessment error: {exc}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
@require_http_methods(['GET'])
def health_insights_api(request):
    """
    AJAX endpoint to get AI health insights for the current user.
    """
    try:
        insights = get_patient_ai_insights(request.user)
        journey = get_patient_journey_summary(request.user)
        return JsonResponse({'insights': insights, 'journey': journey})
    except Exception as exc:
        logger.error(f"Health insights error: {exc}")
        return JsonResponse({'error': 'Internal server error'}, status=500)
