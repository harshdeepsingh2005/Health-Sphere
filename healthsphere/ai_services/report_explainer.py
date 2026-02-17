"""
HealthSphere AI - Report Explainer Service
==========================================

Simulated AI service for explaining medical reports to patients.
Returns simplified explanations of medical terminology and reports.

In a real implementation, this would use:
- Natural Language Processing (NLP) models
- Medical ontologies (SNOMED CT, ICD-10)
- Large Language Models (GPT, BERT variants)

Author: HealthSphere AI Team
Version: 1.0.0 (Academic Prototype)
"""

import random
from datetime import datetime


def explain_report(report_text):
    """
    Generate a patient-friendly explanation of a medical report.
    
    This is a SIMULATED function for academic demonstration.
    In production, this would use NLP models to analyze and explain reports.
    
    Args:
        report_text (str): The original medical report text
    
    Returns:
        dict: Explanation containing:
            - summary: Brief overview in simple terms
            - sections: Explained sections of the report
            - key_findings: Important findings highlighted
            - action_items: What the patient should do next
    """
    
    # Simulated report explanation
    # In a real system, this would analyze the actual report text
    
    summaries = [
        "Your test results show that most values are within normal ranges. "
        "There are a few items that need attention, which are explained below.",
        
        "Overall, your health indicators look good. Some values are slightly "
        "outside the normal range, but nothing that requires immediate concern.",
        
        "Your report indicates generally healthy results. Your doctor may want "
        "to discuss a few findings with you at your next appointment.",
        
        "The results show some areas that are doing well and a few that we "
        "should keep an eye on. Regular monitoring is recommended.",
    ]
    
    section_explanations = [
        {
            "title": "Blood Cell Counts",
            "original": "WBC: 7.2 x10^9/L, RBC: 4.8 x10^12/L, Platelets: 245 x10^9/L",
            "explanation": "Your blood cell counts are normal. White blood cells help "
                          "fight infection, red blood cells carry oxygen, and platelets "
                          "help your blood clot properly."
        },
        {
            "title": "Metabolic Panel",
            "original": "Glucose: 95 mg/dL, Creatinine: 0.9 mg/dL, BUN: 15 mg/dL",
            "explanation": "Your blood sugar and kidney function tests look healthy. "
                          "This means your body is processing sugars and filtering waste "
                          "properly."
        },
        {
            "title": "Lipid Panel",
            "original": "Total Cholesterol: 195 mg/dL, HDL: 55 mg/dL, LDL: 120 mg/dL",
            "explanation": "Your cholesterol levels are in an acceptable range. HDL is "
                          "the 'good' cholesterol that protects your heart, while LDL "
                          "should be kept low."
        },
        {
            "title": "Liver Function",
            "original": "ALT: 25 U/L, AST: 28 U/L, Bilirubin: 0.8 mg/dL",
            "explanation": "Your liver is working well. These enzymes show that your "
                          "liver is healthy and processing nutrients properly."
        },
    ]
    
    key_findings = [
        {
            "finding": "Slightly elevated cholesterol",
            "significance": "Minor - Monitor with diet changes",
            "action": "Consider reducing saturated fat intake"
        },
        {
            "finding": "Vitamin D slightly low",
            "significance": "Minor - Common finding",
            "action": "Your doctor may recommend a supplement"
        },
        {
            "finding": "Blood pressure within normal range",
            "significance": "Positive - Keep up the good work",
            "action": "Continue current lifestyle habits"
        },
    ]
    
    action_items = [
        "Schedule a follow-up appointment in 6 months for routine monitoring",
        "Continue taking any prescribed medications as directed",
        "Maintain a balanced diet and regular exercise routine",
        "Discuss any questions about these results with your doctor",
        "Keep a copy of this report for your personal health records",
    ]
    
    # Select random elements for this explanation
    selected_sections = random.sample(section_explanations, random.randint(2, 4))
    selected_findings = random.sample(key_findings, random.randint(1, 3))
    selected_actions = random.sample(action_items, random.randint(3, 5))
    
    return {
        "summary": random.choice(summaries),
        "sections": selected_sections,
        "key_findings": selected_findings,
        "action_items": selected_actions,
        "generated_at": datetime.now().isoformat(),
        "disclaimer": "This is an AI-generated explanation for educational purposes. "
                     "Please consult your healthcare provider for medical advice.",
    }


def simplify_medical_terms(text):
    """
    Convert medical terminology to patient-friendly language.
    
    This is a SIMULATED function for academic demonstration.
    In production, this would use medical NLP models.
    
    Args:
        text (str): Text containing medical terminology
    
    Returns:
        list: List of term definitions
    """
    
    # Medical term dictionary (simulated)
    medical_terms = {
        "hypertension": {
            "term": "Hypertension",
            "simple": "High Blood Pressure",
            "explanation": "A condition where the force of blood against your artery "
                          "walls is too high. It can lead to heart problems if not managed."
        },
        "hyperlipidemia": {
            "term": "Hyperlipidemia",
            "simple": "High Cholesterol",
            "explanation": "Having too much fat (lipids) in your blood. This can increase "
                          "the risk of heart disease."
        },
        "tachycardia": {
            "term": "Tachycardia",
            "simple": "Fast Heart Rate",
            "explanation": "When your heart beats faster than normal at rest (over 100 "
                          "beats per minute)."
        },
        "bradycardia": {
            "term": "Bradycardia",
            "simple": "Slow Heart Rate",
            "explanation": "When your heart beats slower than normal (under 60 beats per "
                          "minute). Sometimes normal for athletes."
        },
        "anemia": {
            "term": "Anemia",
            "simple": "Low Red Blood Cells",
            "explanation": "Not having enough healthy red blood cells to carry adequate "
                          "oxygen to your body's tissues."
        },
        "edema": {
            "term": "Edema",
            "simple": "Swelling",
            "explanation": "Swelling caused by excess fluid trapped in your body's tissues."
        },
        "dyspnea": {
            "term": "Dyspnea",
            "simple": "Shortness of Breath",
            "explanation": "Difficulty breathing or feeling like you can't get enough air."
        },
        "benign": {
            "term": "Benign",
            "simple": "Not Cancer",
            "explanation": "A growth or tumor that is not cancerous and does not spread "
                          "to other parts of the body."
        },
        "malignant": {
            "term": "Malignant",
            "simple": "Cancerous",
            "explanation": "A growth that is cancerous and can spread to other parts of "
                          "the body."
        },
        "chronic": {
            "term": "Chronic",
            "simple": "Long-lasting",
            "explanation": "A condition that persists for a long time or keeps coming back."
        },
        "acute": {
            "term": "Acute",
            "simple": "Sudden/Short-term",
            "explanation": "A condition that comes on quickly and may be intense but "
                          "doesn't last long."
        },
        "prognosis": {
            "term": "Prognosis",
            "simple": "Expected Outcome",
            "explanation": "The likely course and outcome of a disease or condition."
        },
    }
    
    # Return a selection of common terms (simulated detection)
    num_terms = random.randint(4, 8)
    selected_terms = random.sample(list(medical_terms.values()), num_terms)
    
    return selected_terms


def generate_questions(report_data):
    """
    Generate suggested questions for the patient to ask their doctor.
    
    This is a SIMULATED function for academic demonstration.
    
    Args:
        report_data (dict): Report analysis data
    
    Returns:
        list: List of suggested questions
    """
    
    questions = [
        "What do these results mean for my overall health?",
        "Are there any lifestyle changes I should make?",
        "Do I need any follow-up tests?",
        "How often should I have this test done?",
        "Are any of my medications affecting these results?",
        "What is the normal range for these values?",
        "Should I be concerned about any of these findings?",
        "What can I do to improve these numbers?",
        "When should I schedule my next check-up?",
        "Are there any symptoms I should watch for?",
    ]
    
    return random.sample(questions, random.randint(4, 6))
