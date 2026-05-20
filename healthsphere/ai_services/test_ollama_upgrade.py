#!/usr/bin/env python
"""
Smoke test for Ollama-upgraded triage and diagnostic AI services.
Run from the healthsphere/ directory:
    python ai_services/test_ollama_upgrade.py
"""
import os
import sys
import django

# Bootstrap Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from ai_services.triage_service import calculate_triage_score
from ai_services.diagnostic_ai import generate_diagnostic_suggestions, interpret_lab_results


def sep(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


# ---- 1. High-risk triage patient ----
sep("TEST 1: Triage — High-Risk Chest Pain Patient")

triage_data = {
    'age': 68,
    'chief_complaint': 'Severe chest pain radiating to left arm',
    'symptoms': ['chest pain', 'shortness of breath', 'diaphoresis'],
    'vital_signs': {
        'heart_rate': 118,
        'systolic_bp': 88,
        'diastolic_bp': 55,
        'temperature': 37.2,
        'oxygen_saturation': 91,
    },
    'pain_score': 9,
    'medical_history': ['diabetes', 'hypertension'],
}

result = calculate_triage_score(triage_data)
print(f"ESI Level     : {result['esi_level']} ({result['priority']})")
print(f"Score         : {result['score']}/100")
print(f"AI Powered    : {result['ai_powered']}")
print(f"Red Flags     : {result['red_flags']}")
print(f"Recommended   : {result['recommended_actions']}")
if result['ai_narrative']:
    print(f"\n🤖 AI Narrative:\n{result['ai_narrative']}")
else:
    print("⚠️  No AI narrative (Ollama may be unavailable)")


# ---- 2. Diagnostic suggestions — chest pain ----
sep("TEST 2: Diagnostic AI — Chest Pain + Fever")

patient_data = {
    'age': 72,
    'gender': 'male',
    'symptoms': ['chest pain', 'fever', 'shortness of breath'],
    'vital_signs': {
        'heart_rate': 105,
        'systolic_bp': 145,
        'temperature': 38.8,
        'oxygen_saturation': 93,
    },
    'medical_history': ['diabetes', 'heart disease'],
    'lab_results': {
        'troponin': 0.15,
        'white_blood_cells': 14500,
        'creatinine': 1.6,
    },
}

diag = generate_diagnostic_suggestions(patient_data)
print(f"AI Powered    : {diag['ai_powered']}")
print(f"Differentials : {[d['diagnosis'] for d in diag['differential_diagnosis']]}")
print(f"Risk Level    : {diag['risk_assessment']['risk_level']}")

if diag['ai_summary']:
    print(f"\n🤖 AI Summary:\n{diag['ai_summary']}")
if diag['ai_reasoning']:
    print(f"\n🤖 AI Reasoning:\n{diag['ai_reasoning']}")
if diag['ai_next_steps']:
    print(f"\n🤖 AI Next Steps:")
    for step in diag['ai_next_steps']:
        print(f"  • {step}")


# ---- 3. Lab result interpretation ----
sep("TEST 3: Lab Interpretation — Elevated Troponin + High WBC")

labs = {
    'troponin': 2.5,        # Very high
    'white_blood_cells': 18000,  # High
    'potassium': 6.2,       # Critical high
    'hemoglobin': 7.8,      # Low
}

lab_result = interpret_lab_results(labs)
print(f"AI Powered    : {lab_result.get('ai_powered')}")
print(f"Abnormal Labs : {[(a['test'], a['status']) for a in lab_result['abnormal_values']]}")
print(f"Critical Labs : {[c['test'] for c in lab_result['critical_values']]}")
if lab_result.get('ai_narrative'):
    print(f"\n🤖 AI Narrative:\n{lab_result['ai_narrative']}")
else:
    print("⚠️  No AI narrative (Ollama may be unavailable)")

print("\n\n✅ Smoke tests complete.")
