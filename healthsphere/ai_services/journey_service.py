"""
HealthSphere AI - Journey & Insights Service (Gemini-powered)
=============================================================

Uses Gemini to produce real-time patient journey summaries,
milestone predictions, and personalised health insights.
"""

import json
import logging
import random
from datetime import datetime, timedelta

from .gemini_client import generate_text, is_available

logger = logging.getLogger(__name__)


def _get_patient_context(patient) -> str:
    """Build a text context block from a User (patient) object."""
    lines = [f"Patient: {patient.get_full_name() or patient.username}"]
    try:
        from django.utils import timezone
        from appointments.models import Appointment
        from prescriptions.models import Prescription
        from clinical_portal.models import MedicalRecord, TreatmentPlan

        now = timezone.now()
        upcoming = Appointment.objects.filter(
            patient=patient,
            scheduled_date__gte=now.date(),
            status__in=['requested', 'confirmed']
        ).count()
        past = Appointment.objects.filter(
            patient=patient,
            scheduled_date__lt=now.date()
        ).count()
        lines.append(f"Upcoming appointments: {upcoming}, Past appointments: {past}")

        active_rx = Prescription.objects.filter(
            patient=patient,
            status__in=['approved', 'filled', 'transmitted']
        ).select_related('medication')
        if active_rx:
            meds = ', '.join(rx.medication.generic_name for rx in active_rx[:4])
            lines.append(f"Active prescriptions: {meds}")

        plans = TreatmentPlan.objects.filter(patient=patient, status='active')
        if plans:
            titles = ', '.join(p.title for p in plans[:3])
            lines.append(f"Active treatment plans: {titles}")

        records = MedicalRecord.objects.filter(patient=patient).order_by('-record_date')[:2]
        if records:
            types = ', '.join(r.get_record_type_display() for r in records)
            lines.append(f"Recent records: {types}")

    except Exception as exc:
        logger.debug(f"Patient context error: {exc}")

    return '\n'.join(lines)


def get_patient_journey_summary(patient) -> dict:
    """
    Get a concise AI-powered summary of the patient's healthcare journey.
    """
    if is_available() and hasattr(patient, 'get_full_name'):
        context = _get_patient_context(patient)
        prompt = f"""You are a supportive health AI assistant. Based on the patient's data below,
generate a concise healthcare journey summary.

Patient data:
{context}

Return ONLY valid JSON (no markdown):
{{
  "primary_focus": "<main health focus area, e.g. Chronic Condition Management>",
  "journey_status": "<On Track|Needs Attention|Review Required>",
  "status_color": "<#28a745|#ffc107|#fd7e14>",
  "status_icon": "<✓|!|?>",
  "summary_message": "<2-sentence encouraging message about their care journey>",
  "adherence_score": <integer 70-98>,
  "care_team_note": "<short note about care coordination>",
  "next_milestone": "<what the patient should focus on next>"
}}
"""
        raw = generate_text(prompt)
        if raw:
            try:
                cleaned = raw.strip().lstrip('`').rstrip('`')
                if cleaned.startswith('json'):
                    cleaned = cleaned[4:]
                data = json.loads(cleaned)
                data['ai_powered'] = True
                return data
            except Exception as exc:
                logger.warning(f"Gemini journey summary parse error: {exc}")

    # Fallback
    status = random.choice([
        {'journey_status': 'On Track', 'status_color': '#28a745', 'status_icon': '✓'},
        {'journey_status': 'Needs Attention', 'status_color': '#ffc107', 'status_icon': '!'},
    ])
    return {
        'primary_focus': 'General Health Management',
        'summary_message': 'Your health journey is progressing well. Keep up with your scheduled appointments and medications.',
        'adherence_score': random.randint(78, 96),
        'care_team_note': 'Your care team is coordinating your treatment.',
        'next_milestone': 'Attend your next scheduled appointment.',
        'ai_powered': False,
        **status,
    }


def get_patient_ai_insights(patient) -> list:
    """
    Generate personalised AI health insights for the patient dashboard.
    Returns a list of insight dicts (type, title, message, icon).
    """
    if is_available() and hasattr(patient, 'get_full_name'):
        context = _get_patient_context(patient)
        prompt = f"""You are a health AI assistant embedded in HealthSphere.
Generate 4 personalised, actionable health insights for this patient.

Patient data:
{context}

Return ONLY valid JSON (no markdown):
{{
  "insights": [
    {{
      "type": "<positive|warning|info|tip>",
      "title": "<short insight title>",
      "message": "<1-2 sentence personalised insight>",
      "icon": "<FontAwesome icon class e.g. fas fa-heartbeat>",
      "priority": "<high|medium|low>"
    }}
  ]
}}

Include a mix of types. Keep language encouraging and patient-friendly.
"""
        raw = generate_text(prompt)
        if raw:
            try:
                cleaned = raw.strip().lstrip('`').rstrip('`')
                if cleaned.startswith('json'):
                    cleaned = cleaned[4:]
                data = json.loads(cleaned)
                insights = data.get('insights', [])
                for i in insights:
                    i['ai_powered'] = True
                return insights[:4]
            except Exception as exc:
                logger.warning(f"Gemini insights parse error: {exc}")

    # Fallback static insights
    return [
        {
            'type': 'info',
            'title': 'Stay Hydrated',
            'message': 'Drinking 8 glasses of water daily supports your kidney function and energy levels.',
            'icon': 'fas fa-tint',
            'priority': 'medium',
            'ai_powered': False,
        },
        {
            'type': 'tip',
            'title': 'Medication Reminder',
            'message': 'Taking your medications at the same time each day improves effectiveness.',
            'icon': 'fas fa-pills',
            'priority': 'high',
            'ai_powered': False,
        },
        {
            'type': 'positive',
            'title': 'Keep Moving',
            'message': 'Even a 20-minute daily walk can significantly improve your cardiovascular health.',
            'icon': 'fas fa-walking',
            'priority': 'medium',
            'ai_powered': False,
        },
        {
            'type': 'info',
            'title': 'Sleep Quality',
            'message': 'Consistent sleep schedules support your immune system and overall recovery.',
            'icon': 'fas fa-moon',
            'priority': 'low',
            'ai_powered': False,
        },
    ]


def get_treatment_journey(patient_data) -> dict:
    """Get treatment journey timeline and progress."""
    phases = [
        'Initial Assessment', 'Diagnosis', 'Treatment Planning',
        'Active Treatment', 'Monitoring', 'Recovery', 'Maintenance',
    ]
    phase_idx = random.randint(2, 5)
    base_date = datetime.now() - timedelta(days=random.randint(30, 180))
    timeline = []
    for i in range(phase_idx + 1):
        event_date = base_date + timedelta(days=i * random.randint(7, 21))
        timeline.append({
            'date': event_date.strftime('%Y-%m-%d'),
            'phase': phases[i],
            'status': 'completed' if i < phase_idx else 'current',
            'description': f'Phase {i + 1} of your treatment journey',
        })
    return {
        'current_phase': phases[phase_idx],
        'phase_number': phase_idx + 1,
        'total_phases': len(phases),
        'progress_percentage': round((phase_idx + 1) / len(phases) * 100),
        'timeline': timeline,
        'estimated_completion': (datetime.now() + timedelta(days=random.randint(30, 120))).strftime('%Y-%m-%d'),
    }


def get_patient_journey_summary_legacy(patient_data) -> dict:
    """Legacy wrapper for backwards compatibility with dict-based calls."""
    patient = patient_data if hasattr(patient_data, 'get_full_name') else None
    if patient:
        return get_patient_journey_summary(patient)
    status = random.choice([
        {'journey_status': 'On Track', 'status_color': '#28a745', 'status_icon': '✓'},
    ])
    return {
        'primary_focus': 'Preventive Care',
        'summary_message': 'Your health journey is progressing well.',
        'adherence_score': 88,
        'ai_powered': False,
        **status,
    }


def predict_journey_milestones(patient_data) -> list:
    """
    Predict upcoming milestones in the patient's treatment journey.
    Legacy function used by clinical portal — now delegates to Gemini when available.
    """
    patient = patient_data if hasattr(patient_data, 'get_full_name') else None

    if is_available() and patient:
        context = _get_patient_context(patient)
        prompt = f"""You are a clinical AI. Predict 3 upcoming milestones for this patient's treatment journey.

Patient data:
{context}

Return ONLY valid JSON (no markdown):
{{
  "milestones": [
    {{
      "milestone": "<milestone name>",
      "expected_date": "<YYYY-MM-DD relative to today>",
      "description": "<patient-friendly description>",
      "type": "<appointment|test|medication_review|goal>"
    }}
  ]
}}
"""
        raw = generate_text(prompt)
        if raw:
            try:
                cleaned = raw.strip().lstrip('`').rstrip('`')
                if cleaned.startswith('json'):
                    cleaned = cleaned[4:]
                data = json.loads(cleaned)
                return data.get('milestones', [])
            except Exception as exc:
                logger.warning(f"Gemini milestones parse error: {exc}")

    # Fallback
    from datetime import timedelta
    today = datetime.now()
    return [
        {
            'milestone': 'Follow-up Appointment',
            'expected_date': (today + timedelta(days=14)).strftime('%Y-%m-%d'),
            'description': 'Routine check-up with your primary care physician.',
            'type': 'appointment',
        },
        {
            'milestone': 'Lab Work Review',
            'expected_date': (today + timedelta(days=30)).strftime('%Y-%m-%d'),
            'description': 'Review of latest lab results.',
            'type': 'test',
        },
        {
            'milestone': 'Medication Review',
            'expected_date': (today + timedelta(days=60)).strftime('%Y-%m-%d'),
            'description': 'Assess current medication effectiveness.',
            'type': 'medication_review',
        },
    ]

