"""
HealthSphere AI - Enhanced Triage Service (Ollama-powered)
==========================================================

Advanced AI service for emergency triage prioritization.
Combines rule-based ESI clinical algorithms with Ollama LLM enrichment.

Features:
- Clinical triage algorithms (ESI 1-5 scoring)
- Vital signs & symptom risk analysis
- Ollama-powered clinical narrative and enriched recommendations
- Graceful fallback to rule-based only when Ollama is unavailable
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from .gemini_client import generate_text, is_available

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Rule-based helpers (always run, fast, no LLM dependency)
# ---------------------------------------------------------------------------

def _estimate_los(esi_level: int) -> str:
    """Estimate length of stay based on ESI level."""
    return {
        1: "6-12 hours (ICU admission likely)",
        2: "4-8 hours (admission likely)",
        3: "2-4 hours",
        4: "1-2 hours",
        5: "30-60 minutes",
    }.get(esi_level, "2-4 hours")


def _estimate_resources(esi_level: int) -> List[str]:
    """Estimate resource needs based on ESI level."""
    return {
        1: ["ICU bed", "Multiple specialists", "Advanced diagnostics", "Continuous monitoring"],
        2: ["Telemetry bed", "Specialist consult", "Lab work", "Imaging"],
        3: ["ED bed", "Basic monitoring", "Possible imaging"],
        4: ["Fast track", "Basic assessment"],
        5: ["Clinic setting", "Minimal resources"],
    }.get(esi_level, ["Standard ED care"])


def _get_diagnostic_suggestions(symptoms: list, vital_signs: dict) -> List[str]:
    """Rule-based diagnostic suggestions from presenting symptoms."""
    suggestions = []
    symptom_str = str(symptoms).lower()
    if 'chest pain' in symptom_str:
        suggestions.extend(["Rule out MI", "12-lead ECG", "Cardiac enzymes / Troponin"])
    if 'shortness of breath' in symptom_str:
        suggestions.extend(["Chest X-ray", "ABG / SpO2 monitoring", "BNP"])
    if vital_signs.get('temperature', 37) > 38.3:
        suggestions.extend(["Blood cultures", "CBC with differential", "Urinalysis"])
    if vital_signs.get('oxygen_saturation', 99) < 92:
        suggestions.append("Immediate oxygen therapy")
    return suggestions[:6]


def _assess_risk_factors(triage_data: dict) -> List[str]:
    """Identify patient risk factors from triage data."""
    risk_factors = []
    age = triage_data.get('age', 0)
    medical_history = triage_data.get('medical_history', [])

    if age > 75:
        risk_factors.append("Advanced age (>75)")
    elif age > 65:
        risk_factors.append("Elderly (65–75)")

    high_risk_conditions = ['diabetes', 'heart disease', 'copd', 'kidney disease', 'cancer']
    for condition in medical_history:
        if any(hrc in condition.lower() for hrc in high_risk_conditions):
            risk_factors.append(f"History of {condition}")

    return risk_factors


def _get_monitoring_requirements(esi_level: int) -> str:
    """Get monitoring requirements based on ESI level."""
    return {
        1: "Continuous cardiac, BP, SpO2; vitals q5min",
        2: "Cardiac monitor; vitals q15min",
        3: "Vitals q30min; PRN monitoring",
        4: "Vitals q1h",
        5: "Initial vitals; PRN",
    }.get(esi_level, "Standard monitoring")


def _rule_based_triage(triage_data: dict) -> dict:
    """
    Pure rule-based ESI triage scoring (fast, no LLM).
    Returns a complete triage result dict.
    """
    patient = triage_data.get('patient')
    vital_signs = triage_data.get('vital_signs', {})
    symptoms = triage_data.get('symptoms', [])
    pain_score = triage_data.get('pain_score', 0)
    age = (
        triage_data.get('age')
        or (getattr(getattr(patient, 'profile', None), 'age', None))
        or 50
    )

    base_score = 50

    hr = vital_signs.get('heart_rate', 70)
    systolic_bp = vital_signs.get('systolic_bp', 120)
    temp = vital_signs.get('temperature', 37.0)
    o2_sat = vital_signs.get('oxygen_saturation', 98)

    # Vital signs scoring
    if hr > 120 or hr < 50:
        base_score += 20
    if systolic_bp > 180 or systolic_bp < 90:
        base_score += 25
    if temp > 39.0 or temp < 35.0:
        base_score += 15
    if o2_sat < 92:
        base_score += 30

    # Symptom scoring
    critical_symptoms = ['chest pain', 'shortness of breath', 'severe headache', 'altered mental status']
    for symptom in symptoms:
        if any(cs in symptom.lower() for cs in critical_symptoms):
            base_score += 15

    # Age / pain adjustments
    if age > 65:
        base_score += 10
    if age < 2:
        base_score += 15
    if pain_score >= 8:
        base_score += 10

    triage_score = max(1, min(100, base_score))

    if triage_score >= 85:
        esi_level, priority, color = 1, "Critical", "#dc3545"
    elif triage_score >= 70:
        esi_level, priority, color = 2, "Emergent", "#fd7e14"
    elif triage_score >= 50:
        esi_level, priority, color = 3, "Urgent", "#ffc107"
    elif triage_score >= 30:
        esi_level, priority, color = 4, "Less Urgent", "#28a745"
    else:
        esi_level, priority, color = 5, "Non-urgent", "#17a2b8"

    # Recommendations
    recommended_actions = []
    if esi_level <= 2:
        recommended_actions.extend(["Immediate physician evaluation", "Continuous monitoring", "IV access"])
    elif esi_level == 3:
        recommended_actions.extend(["Physician evaluation within 30 minutes", "Vital signs q15min"])
    else:
        recommended_actions.extend(["Nurse practitioner evaluation", "Vital signs on arrival"])

    red_flags = []
    if o2_sat < 90:
        red_flags.append("Severe hypoxemia — immediate oxygen required")
    if systolic_bp < 80:
        red_flags.append("Severe hypotension — consider shock")
    if temp > 40.0:
        red_flags.append("Hyperthermia — urgent cooling measures")
    if hr > 150:
        red_flags.append("Severe tachycardia — cardiac monitoring required")

    return {
        'score': int(triage_score),
        'esi_level': esi_level,
        'priority': priority,
        'color': color,
        'estimated_los': _estimate_los(esi_level),
        'resource_needs': _estimate_resources(esi_level),
        'diagnostic_suggestions': _get_diagnostic_suggestions(symptoms, vital_signs),
        'red_flags': red_flags,
        'recommended_actions': recommended_actions,
        'risk_factors': _assess_risk_factors(triage_data),
        'monitoring_requirements': _get_monitoring_requirements(esi_level),
        'timestamp': datetime.now().isoformat(),
        'ai_powered': False,
        'ai_narrative': None,
    }


# ---------------------------------------------------------------------------
# Ollama enrichment
# ---------------------------------------------------------------------------

def _build_triage_prompt(triage_data: dict, rule_result: dict) -> str:
    """Build a structured clinical prompt for the LLM triage narrative."""
    vital_signs = triage_data.get('vital_signs', {})
    symptoms = triage_data.get('symptoms', [])
    chief_complaint = triage_data.get('chief_complaint', 'Not specified')
    medical_history = triage_data.get('medical_history', [])
    age = triage_data.get('age', 'Unknown')
    pain_score = triage_data.get('pain_score', 'Not reported')

    vit_str = (
        f"HR {vital_signs.get('heart_rate', 'N/A')} bpm | "
        f"BP {vital_signs.get('systolic_bp', 'N/A')}/{vital_signs.get('diastolic_bp', 'N/A')} mmHg | "
        f"Temp {vital_signs.get('temperature', 'N/A')}°C | "
        f"SpO2 {vital_signs.get('oxygen_saturation', 'N/A')}%"
    )

    return f"""You are a senior emergency medicine physician reviewing a triage assessment.

PATIENT PRESENTATION:
- Age: {age}
- Chief Complaint: {chief_complaint}
- Symptoms: {', '.join(symptoms) or 'None listed'}
- Vital Signs: {vit_str}
- Pain Score: {pain_score}/10
- Medical History: {', '.join(medical_history) or 'None'}

RULE-BASED ASSESSMENT:
- ESI Level: {rule_result['esi_level']} ({rule_result['priority']})
- Triage Score: {rule_result['score']}/100
- Red Flags: {', '.join(rule_result['red_flags']) or 'None identified'}
- Initial Recommendations: {', '.join(rule_result['recommended_actions'])}

Please provide:
1. A concise 2-3 sentence clinical narrative summarising this patient's picture and priority rationale.
2. 3-5 specific, actionable recommended steps for the triage nurse and attending physician.

Format your response as:
NARRATIVE: <your clinical narrative>
ACTIONS:
- <action 1>
- <action 2>
- <action 3>
"""


def _parse_llm_triage_response(llm_text: str) -> tuple[str, List[str]]:
    """Parse the LLM narrative + actions from the structured response."""
    narrative = ""
    actions = []

    lines = llm_text.strip().split('\n')
    in_actions = False

    for line in lines:
        line = line.strip()
        if line.upper().startswith('NARRATIVE:'):
            narrative = line[len('NARRATIVE:'):].strip()
        elif line.upper().startswith('ACTIONS:'):
            in_actions = True
        elif in_actions and line.startswith('- '):
            actions.append(line[2:].strip())
        elif in_actions and line and not line.startswith('-'):
            # continuation of narrative or ignore
            pass

    return narrative, actions


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def calculate_triage_score(triage_data: dict) -> dict:
    """
    Calculate an enhanced emergency triage score.

    1. Always runs fast rule-based ESI scoring.
    2. When Ollama is available, enriches with a clinical narrative and
       AI-generated action list (ai_narrative, recommended_actions).

    Args:
        triage_data: dict with keys: patient, vital_signs, symptoms,
                     chief_complaint, medical_history, pain_score, age.

    Returns:
        dict with: score, esi_level, priority, color, estimated_los,
                   resource_needs, diagnostic_suggestions, red_flags,
                   recommended_actions, risk_factors, monitoring_requirements,
                   ai_narrative, ai_powered, timestamp.
    """
    result = _rule_based_triage(triage_data)

    if not is_available():
        logger.debug("Ollama unavailable — returning rule-based triage only.")
        return result

    try:
        prompt = _build_triage_prompt(triage_data, result)
        llm_text = generate_text(
            prompt=prompt,
            system_instruction=(
                "You are a board-certified emergency medicine physician. "
                "Provide concise, actionable clinical guidance. "
                "Do not diagnose — support triage decision-making."
            ),
        )

        if llm_text:
            narrative, ai_actions = _parse_llm_triage_response(llm_text)
            result['ai_narrative'] = narrative or llm_text.strip()
            if ai_actions:
                result['recommended_actions'] = ai_actions
            result['ai_powered'] = True
            logger.info(f"Ollama triage enrichment successful (ESI {result['esi_level']}).")

    except Exception as exc:
        logger.error(f"Ollama triage enrichment failed: {exc} — using rule-based result.")

    return result


def get_triage_recommendation(triage_data: dict) -> dict:
    """Alias for calculate_triage_score (backwards compatibility)."""
    return calculate_triage_score(triage_data)


def mock_ai_analysis(symptoms_data) -> dict:
    """Legacy function for backwards compatibility."""
    return calculate_triage_score({'symptoms': symptoms_data})
