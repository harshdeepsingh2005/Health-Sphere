"""
HealthSphere AI - Triage Service
================================

Simulated AI service for emergency triage prioritization.
Returns mock triage scores for demonstration purposes.

In a real implementation, this would use:
- Clinical triage algorithms (ESI, Manchester, etc.)
- ML models trained on emergency department data
- Real-time vital sign analysis

Author: HealthSphere AI Team
Version: 1.0.0 (Academic Prototype)
"""

import random
from datetime import datetime


def calculate_triage_score(triage_data):
    """
    Calculate emergency triage score for a patient.
    
    This is a SIMULATED function for academic demonstration.
    Uses the 5-level Emergency Severity Index (ESI) as a reference.
    
    Args:
        triage_data (dict): Patient triage information including:
            - patient: User object
            - vitals: VitalRecord object (optional)
            - admission: AdmissionRecord object (optional)
            - symptoms: List of symptoms (optional)
    
    Returns:
        dict: Triage assessment containing:
            - score: 1-100 (higher = more urgent)
            - level: ESI level (1-5, 1 being most urgent)
            - color: Triage color code
            - category: Urgency category
    """
    
    # Simulate triage score calculation
    # In a real system, this would analyze vital signs, symptoms, etc.
    
    # Generate mock triage score
    base_score = random.gauss(50, 25)
    triage_score = max(1, min(100, base_score))
    
    # Determine triage level based on score (ESI-like system)
    if triage_score >= 85:
        level = 1
        color = "#dc3545"  # Red - Immediate
        category = "Critical"
        wait_time = "Immediate"
    elif triage_score >= 70:
        level = 2
        color = "#fd7e14"  # Orange - Emergent
        category = "Urgent"
        wait_time = "< 15 minutes"
    elif triage_score >= 50:
        level = 3
        color = "#ffc107"  # Yellow - Urgent
        category = "Urgent"
        wait_time = "< 30 minutes"
    elif triage_score >= 30:
        level = 4
        color = "#28a745"  # Green - Less Urgent
        category = "Standard"
        wait_time = "< 60 minutes"
    else:
        level = 5
        color = "#17a2b8"  # Blue - Non-urgent
        category = "Standard"
        wait_time = "< 120 minutes"
    
    return {
        "score": round(triage_score, 1),
        "level": level,
        "color": color,
        "category": category,
        "recommended_wait_time": wait_time,
        "assessed_at": datetime.now().isoformat(),
    }


def get_triage_recommendation(triage_data):
    """
    Generate triage recommendations based on patient data.
    
    This is a SIMULATED function for academic demonstration.
    
    Args:
        triage_data (dict): Patient triage information
    
    Returns:
        dict: Recommendations including:
            - priority_actions: Immediate actions needed
            - assessments: Required assessments
            - resources: Resources to prepare
    """
    
    # Simulated recommendations based on common triage scenarios
    
    all_priority_actions = [
        "Establish IV access",
        "Continuous cardiac monitoring",
        "Oxygen supplementation",
        "Pain assessment and management",
        "Blood pressure monitoring",
        "Blood glucose check",
        "ECG if chest pain",
        "Neurological assessment",
        "Wound assessment and care",
        "Hydration assessment",
    ]
    
    all_assessments = [
        "Complete blood count (CBC)",
        "Basic metabolic panel",
        "Chest X-ray",
        "ECG/EKG",
        "Urinalysis",
        "Blood cultures",
        "CT scan if indicated",
        "Ultrasound assessment",
        "Point-of-care testing",
        "Medication reconciliation",
    ]
    
    all_resources = [
        "Resuscitation room standby",
        "Specialist consultation",
        "Pharmacy notification",
        "Lab priority processing",
        "Imaging department notification",
        "Isolation precautions if needed",
        "Social services consultation",
        "Interpreter services if needed",
    ]
    
    # Select random recommendations
    num_actions = random.randint(2, 4)
    num_assessments = random.randint(2, 4)
    num_resources = random.randint(1, 3)
    
    return {
        "priority_actions": random.sample(all_priority_actions, num_actions),
        "required_assessments": random.sample(all_assessments, num_assessments),
        "resources_needed": random.sample(all_resources, num_resources),
        "estimated_time_to_disposition": f"{random.randint(1, 6)} hours",
        "confidence": round(random.uniform(0.70, 0.90), 2),
    }


def predict_resource_needs(admission_data):
    """
    Predict resource needs based on triage assessment.
    
    This is a SIMULATED function for academic demonstration.
    
    Args:
        admission_data (dict): Admission and triage information
    
    Returns:
        dict: Predicted resource needs
    """
    
    return {
        "bed_type": random.choice(["Regular", "Monitored", "ICU"]),
        "expected_los_hours": random.randint(4, 72),
        "specialist_consults": random.randint(0, 3),
        "imaging_studies": random.randint(0, 2),
        "lab_tests": random.randint(2, 6),
        "procedures": random.randint(0, 2),
        "estimated_cost_range": f"${random.randint(500, 5000)} - ${random.randint(5000, 15000)}",
    }


def get_similar_cases(triage_data, num_cases=5):
    """
    Find similar historical cases for reference.
    
    This is a SIMULATED function for academic demonstration.
    In production, this would query a case database.
    
    Args:
        triage_data (dict): Current patient triage data
        num_cases (int): Number of similar cases to return
    
    Returns:
        list: List of similar historical cases
    """
    
    diagnoses = [
        "Chest pain - cardiac origin",
        "Chest pain - non-cardiac",
        "Respiratory distress",
        "Abdominal pain",
        "Trauma - minor",
        "Trauma - major",
        "Neurological symptoms",
        "Infectious disease",
        "Metabolic disorder",
        "Psychiatric emergency",
    ]
    
    outcomes = ["Discharged", "Admitted", "Transferred", "ICU Admission"]
    
    similar_cases = []
    for i in range(num_cases):
        similar_cases.append({
            "case_id": f"CASE-{random.randint(10000, 99999)}",
            "similarity_score": round(random.uniform(0.75, 0.95), 2),
            "diagnosis": random.choice(diagnoses),
            "outcome": random.choice(outcomes),
            "length_of_stay": f"{random.randint(1, 48)} hours",
            "triage_level": random.randint(1, 5),
        })
    
    # Sort by similarity score
    similar_cases.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    return similar_cases
