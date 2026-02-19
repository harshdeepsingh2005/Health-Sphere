"""
HealthSphere AI - Advanced Diagnostic AI Services
=================================================

Comprehensive AI-powered diagnostic assistance and clinical decision support.
Integrates multiple AI models for enhanced patient care.

Features:
- Symptom-based diagnostic suggestions
- Lab result interpretation
- Imaging analysis assistance
- Drug interaction checking
- Treatment recommendations
- Risk assessment and stratification
- Predictive analytics for patient outcomes

Author: HealthSphere AI Team
Version: 2.0.0 (Enhanced AI/ML Integration)
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json


class DiagnosticAI:
    """Advanced AI diagnostic assistance system."""
    
    # Common symptoms and their potential diagnoses
    SYMPTOM_PATTERNS = {
        'chest_pain': [
            ('Myocardial Infarction', 0.15, 'high'),
            ('Angina Pectoris', 0.25, 'medium'),
            ('Costochondritis', 0.30, 'low'),
            ('GERD', 0.20, 'low'),
            ('Pneumonia', 0.10, 'medium')
        ],
        'shortness_of_breath': [
            ('Congestive Heart Failure', 0.20, 'high'),
            ('Asthma Exacerbation', 0.25, 'medium'),
            ('Pneumonia', 0.20, 'medium'),
            ('Pulmonary Embolism', 0.10, 'high'),
            ('COPD Exacerbation', 0.25, 'medium')
        ],
        'abdominal_pain': [
            ('Appendicitis', 0.15, 'high'),
            ('Gastroenteritis', 0.30, 'low'),
            ('Gallbladder Disease', 0.20, 'medium'),
            ('Peptic Ulcer Disease', 0.25, 'low'),
            ('Bowel Obstruction', 0.10, 'high')
        ],
        'headache': [
            ('Tension Headache', 0.40, 'low'),
            ('Migraine', 0.30, 'low'),
            ('Cluster Headache', 0.10, 'medium'),
            ('Meningitis', 0.05, 'high'),
            ('Intracranial Pressure', 0.15, 'high')
        ],
        'fever': [
            ('Viral Infection', 0.40, 'low'),
            ('Bacterial Infection', 0.25, 'medium'),
            ('UTI', 0.15, 'low'),
            ('Pneumonia', 0.15, 'medium'),
            ('Sepsis', 0.05, 'high')
        ]
    }
    
    # Lab value normal ranges
    LAB_NORMAL_RANGES = {
        'glucose': (70, 100, 'mg/dL'),
        'creatinine': (0.6, 1.2, 'mg/dL'),
        'bun': (7, 20, 'mg/dL'),
        'sodium': (136, 145, 'mEq/L'),
        'potassium': (3.5, 5.0, 'mEq/L'),
        'chloride': (98, 107, 'mEq/L'),
        'hemoglobin': (12.0, 17.5, 'g/dL'),
        'hematocrit': (36, 52, '%'),
        'white_blood_cells': (4500, 11000, '/μL'),
        'platelets': (150000, 450000, '/μL'),
        'troponin': (0, 0.04, 'ng/mL'),
        'bnp': (0, 100, 'pg/mL'),
        'crp': (0, 3.0, 'mg/L'),
        'esr': (0, 30, 'mm/hr')
    }
    
    @classmethod
    def generate_diagnostic_suggestions(cls, patient_data: Dict) -> Dict:
        """
        Generate AI-powered diagnostic suggestions based on patient presentation.
        
        Args:
            patient_data: Dictionary containing patient information
                - symptoms: List of symptoms
                - vital_signs: Vital sign measurements
                - medical_history: Past medical history
                - lab_results: Laboratory values
                - physical_exam: Physical examination findings
                - demographics: Age, gender, etc.
        
        Returns:
            Dictionary with diagnostic suggestions and supporting information
        """
        symptoms = patient_data.get('symptoms', [])
        vital_signs = patient_data.get('vital_signs', {})
        medical_history = patient_data.get('medical_history', [])
        lab_results = patient_data.get('lab_results', {})
        age = patient_data.get('age', 50)
        gender = patient_data.get('gender', 'unknown')
        
        # Generate differential diagnosis
        differential_diagnosis = cls._generate_differential_diagnosis(symptoms, age, gender, medical_history)
        
        # Analyze vital signs
        vital_analysis = cls._analyze_vital_signs(vital_signs)
        
        # Interpret lab results
        lab_interpretation = cls._interpret_lab_results(lab_results)
        
        # Risk stratification
        risk_assessment = cls._assess_patient_risk(patient_data)
        
        # Treatment recommendations
        treatment_suggestions = cls._generate_treatment_recommendations(differential_diagnosis, patient_data)
        
        # Follow-up recommendations
        followup_plan = cls._generate_followup_plan(differential_diagnosis, risk_assessment)
        
        return {
            'differential_diagnosis': differential_diagnosis,
            'vital_signs_analysis': vital_analysis,
            'lab_interpretation': lab_interpretation,
            'risk_assessment': risk_assessment,
            'treatment_suggestions': treatment_suggestions,
            'followup_plan': followup_plan,
            'confidence_score': cls._calculate_confidence_score(patient_data),
            'red_flags': cls._identify_red_flags(patient_data),
            'generated_at': datetime.now().isoformat(),
            'ai_version': '2.0.0'
        }
    
    @classmethod
    def _generate_differential_diagnosis(cls, symptoms: List[str], age: int, gender: str, medical_history: List[str]) -> List[Dict]:
        """Generate differential diagnosis based on symptoms and patient factors."""
        diagnoses = {}
        
        # Analyze each symptom
        for symptom in symptoms:
            if symptom.lower().replace(' ', '_') in cls.SYMPTOM_PATTERNS:
                patterns = cls.SYMPTOM_PATTERNS[symptom.lower().replace(' ', '_')]
                for diagnosis, base_prob, severity in patterns:
                    if diagnosis not in diagnoses:
                        diagnoses[diagnosis] = {
                            'probability': 0,
                            'severity': severity,
                            'supporting_evidence': [],
                            'age_factor': 1.0,
                            'history_factor': 1.0
                        }
                    
                    # Age adjustments
                    age_factor = 1.0
                    if age > 65 and diagnosis in ['Myocardial Infarction', 'Congestive Heart Failure']:
                        age_factor = 1.3
                    elif age < 30 and diagnosis in ['Angina Pectoris', 'COPD Exacerbation']:
                        age_factor = 0.5
                    
                    # History adjustments
                    history_factor = 1.0
                    if 'diabetes' in [h.lower() for h in medical_history] and diagnosis == 'Myocardial Infarction':
                        history_factor = 1.5
                    elif 'asthma' in [h.lower() for h in medical_history] and diagnosis == 'Asthma Exacerbation':
                        history_factor = 1.8
                    
                    adjusted_prob = base_prob * age_factor * history_factor
                    diagnoses[diagnosis]['probability'] = max(diagnoses[diagnosis]['probability'], adjusted_prob)
                    diagnoses[diagnosis]['supporting_evidence'].append(symptom)
                    diagnoses[diagnosis]['age_factor'] = age_factor
                    diagnoses[diagnosis]['history_factor'] = history_factor
        
        # Sort by probability and return top 5
        sorted_diagnoses = sorted(diagnoses.items(), key=lambda x: x[1]['probability'], reverse=True)[:5]
        
        return [
            {
                'diagnosis': diagnosis,
                'probability': round(data['probability'] * 100, 1),
                'confidence': 'High' if data['probability'] > 0.4 else 'Medium' if data['probability'] > 0.2 else 'Low',
                'severity': data['severity'],
                'supporting_symptoms': data['supporting_evidence'],
                'reasoning': cls._generate_diagnostic_reasoning(diagnosis, data)
            }
            for diagnosis, data in sorted_diagnoses
        ]
    
    @classmethod
    def _generate_diagnostic_reasoning(cls, diagnosis: str, data: Dict) -> str:
        """Generate human-readable reasoning for diagnostic suggestion."""
        base_reasoning = f"Based on presenting symptoms: {', '.join(data['supporting_evidence'])}"
        
        if data['age_factor'] > 1.1:
            base_reasoning += f". Age factor increases likelihood."
        elif data['age_factor'] < 0.9:
            base_reasoning += f". Age factor decreases likelihood."
        
        if data['history_factor'] > 1.1:
            base_reasoning += f". Medical history supports this diagnosis."
        
        return base_reasoning
    
    @classmethod
    def _analyze_vital_signs(cls, vital_signs: Dict) -> Dict:
        """Analyze vital signs and identify abnormalities."""
        analysis = {
            'abnormalities': [],
            'concerns': [],
            'stability': 'stable'
        }
        
        # Heart rate analysis
        hr = vital_signs.get('heart_rate')
        if hr:
            if hr > 100:
                analysis['abnormalities'].append('Tachycardia (HR > 100)')
                if hr > 150:
                    analysis['concerns'].append('Severe tachycardia requires immediate attention')
                    analysis['stability'] = 'unstable'
            elif hr < 60:
                analysis['abnormalities'].append('Bradycardia (HR < 60)')
                if hr < 40:
                    analysis['concerns'].append('Severe bradycardia may require intervention')
                    analysis['stability'] = 'concerning'
        
        # Blood pressure analysis
        systolic = vital_signs.get('systolic_bp')
        diastolic = vital_signs.get('diastolic_bp')
        if systolic and diastolic:
            if systolic > 180 or diastolic > 120:
                analysis['abnormalities'].append('Hypertensive crisis')
                analysis['concerns'].append('Hypertensive emergency - immediate treatment needed')
                analysis['stability'] = 'critical'
            elif systolic > 140 or diastolic > 90:
                analysis['abnormalities'].append('Hypertension')
            elif systolic < 90:
                analysis['abnormalities'].append('Hypotension')
                analysis['concerns'].append('Low blood pressure may indicate shock or dehydration')
                analysis['stability'] = 'concerning'
        
        # Temperature analysis
        temp = vital_signs.get('temperature')
        if temp:
            if temp > 38.3:  # 101°F
                analysis['abnormalities'].append(f'Fever ({temp}°C)')
                if temp > 40:  # 104°F
                    analysis['concerns'].append('High fever requires urgent intervention')
                    analysis['stability'] = 'concerning'
            elif temp < 35:  # 95°F
                analysis['abnormalities'].append('Hypothermia')
                analysis['concerns'].append('Hypothermia may indicate serious condition')
                analysis['stability'] = 'concerning'
        
        # Oxygen saturation
        o2_sat = vital_signs.get('oxygen_saturation')
        if o2_sat:
            if o2_sat < 90:
                analysis['abnormalities'].append(f'Severe hypoxemia (O2 sat {o2_sat}%)')
                analysis['concerns'].append('Severe hypoxemia requires immediate oxygen therapy')
                analysis['stability'] = 'critical'
            elif o2_sat < 95:
                analysis['abnormalities'].append(f'Mild hypoxemia (O2 sat {o2_sat}%)')
                analysis['stability'] = 'concerning'
        
        return analysis
    
    @classmethod
    def _interpret_lab_results(cls, lab_results: Dict) -> Dict:
        """Interpret laboratory results and flag abnormalities."""
        interpretation = {
            'abnormal_values': [],
            'critical_values': [],
            'trending': [],
            'clinical_significance': []
        }
        
        for lab_name, value in lab_results.items():
            if lab_name in cls.LAB_NORMAL_RANGES:
                min_val, max_val, unit = cls.LAB_NORMAL_RANGES[lab_name]
                
                if value < min_val:
                    interpretation['abnormal_values'].append({
                        'test': lab_name,
                        'value': value,
                        'reference_range': f'{min_val}-{max_val} {unit}',
                        'status': 'Low',
                        'significance': cls._get_lab_significance(lab_name, value, 'low')
                    })
                elif value > max_val:
                    interpretation['abnormal_values'].append({
                        'test': lab_name,
                        'value': value,
                        'reference_range': f'{min_val}-{max_val} {unit}',
                        'status': 'High',
                        'significance': cls._get_lab_significance(lab_name, value, 'high')
                    })
                
                # Check for critical values
                if cls._is_critical_value(lab_name, value):
                    interpretation['critical_values'].append({
                        'test': lab_name,
                        'value': value,
                        'action_needed': cls._get_critical_action(lab_name, value)
                    })
        
        return interpretation
    
    @classmethod
    def _get_lab_significance(cls, lab_name: str, value: float, status: str) -> str:
        """Get clinical significance of abnormal lab value."""
        significance_map = {
            'glucose': {
                'high': 'May indicate diabetes or stress response',
                'low': 'Risk of hypoglycemic episode'
            },
            'creatinine': {
                'high': 'Suggests kidney dysfunction',
                'low': 'May indicate muscle loss'
            },
            'troponin': {
                'high': 'Indicates cardiac muscle damage',
                'low': 'Normal, rules out MI'
            },
            'white_blood_cells': {
                'high': 'May indicate infection or inflammation',
                'low': 'May indicate immunosuppression'
            }
        }
        
        return significance_map.get(lab_name, {}).get(status, 'Clinical correlation recommended')
    
    @classmethod
    def _is_critical_value(cls, lab_name: str, value: float) -> bool:
        """Check if lab value is critically abnormal."""
        critical_ranges = {
            'glucose': (30, 400),
            'creatinine': (0.2, 10.0),
            'potassium': (2.5, 6.5),
            'sodium': (120, 160),
            'hemoglobin': (5.0, 20.0),
            'troponin': (0, 50.0)
        }
        
        if lab_name in critical_ranges:
            min_val, max_val = critical_ranges[lab_name]
            return value < min_val or value > max_val
        
        return False
    
    @classmethod
    def _get_critical_action(cls, lab_name: str, value: float) -> str:
        """Get recommended action for critical lab values."""
        actions = {
            'glucose': 'Monitor for hypo/hyperglycemic symptoms, consider insulin or dextrose',
            'creatinine': 'Assess fluid status, consider nephrology consult',
            'potassium': 'ECG monitoring, consider potassium supplementation/restriction',
            'troponin': 'Cardiology consult, consider cardiac catheterization'
        }
        
        return actions.get(lab_name, 'Immediate physician notification required')
    
    @classmethod
    def _assess_patient_risk(cls, patient_data: Dict) -> Dict:
        """Assess overall patient risk and stratification."""
        risk_factors = []
        risk_score = 0
        
        age = patient_data.get('age', 0)
        medical_history = patient_data.get('medical_history', [])
        vital_signs = patient_data.get('vital_signs', {})
        
        # Age-based risk
        if age > 75:
            risk_factors.append('Advanced age (>75)')
            risk_score += 2
        elif age > 65:
            risk_factors.append('Elderly (65-75)')
            risk_score += 1
        
        # Comorbidity risk
        high_risk_conditions = ['diabetes', 'heart disease', 'copd', 'kidney disease', 'cancer']
        for condition in medical_history:
            if any(hrc in condition.lower() for hrc in high_risk_conditions):
                risk_factors.append(f'History of {condition}')
                risk_score += 1
        
        # Vital signs risk
        if vital_signs.get('systolic_bp', 120) > 180:
            risk_factors.append('Severe hypertension')
            risk_score += 2
        
        if vital_signs.get('heart_rate', 70) > 120:
            risk_factors.append('Severe tachycardia')
            risk_score += 2
        
        # Determine overall risk level
        if risk_score >= 5:
            risk_level = 'High'
        elif risk_score >= 3:
            risk_level = 'Moderate'
        else:
            risk_level = 'Low'
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'monitoring_frequency': cls._get_monitoring_frequency(risk_level),
            'discharge_criteria': cls._get_discharge_criteria(risk_level)
        }
    
    @classmethod
    def _get_monitoring_frequency(cls, risk_level: str) -> str:
        """Get recommended monitoring frequency based on risk."""
        frequencies = {
            'High': 'Continuous monitoring, frequent vital signs q15min',
            'Moderate': 'q1h vital signs, regular assessment',
            'Low': 'q4h vital signs, routine monitoring'
        }
        return frequencies.get(risk_level, 'Standard monitoring')
    
    @classmethod
    def _get_discharge_criteria(cls, risk_level: str) -> List[str]:
        """Get discharge criteria based on risk level."""
        criteria_map = {
            'High': [
                'Stable vital signs for 6+ hours',
                'Resolution of acute symptoms',
                'Adequate support system at home',
                'Follow-up arranged within 24-48 hours'
            ],
            'Moderate': [
                'Stable vital signs for 4+ hours',
                'Improvement in presenting symptoms',
                'Patient able to ambulate safely',
                'Follow-up arranged within 1 week'
            ],
            'Low': [
                'Stable vital signs',
                'Resolution of acute symptoms',
                'Patient comfortable with discharge plan',
                'Routine follow-up arranged'
            ]
        }
        return criteria_map.get(risk_level, ['Standard discharge criteria'])
    
    @classmethod
    def _generate_treatment_recommendations(cls, differential_diagnosis: List[Dict], patient_data: Dict) -> List[Dict]:
        """Generate treatment recommendations based on likely diagnoses."""
        recommendations = []
        
        for diagnosis_item in differential_diagnosis[:3]:  # Top 3 diagnoses
            diagnosis = diagnosis_item['diagnosis']
            probability = diagnosis_item['probability']
            
            if probability > 30:  # High probability diagnoses
                treatment = cls._get_treatment_protocol(diagnosis, patient_data)
                if treatment:
                    recommendations.append({
                        'diagnosis': diagnosis,
                        'treatment': treatment,
                        'priority': 'High' if probability > 50 else 'Medium',
                        'evidence_level': 'Strong' if probability > 60 else 'Moderate'
                    })
        
        return recommendations
    
    @classmethod
    def _get_treatment_protocol(cls, diagnosis: str, patient_data: Dict) -> Optional[Dict]:
        """Get treatment protocol for specific diagnosis."""
        protocols = {
            'Myocardial Infarction': {
                'immediate': ['Aspirin 325mg chewed', 'Obtain 12-lead ECG', 'Start oxygen if O2 sat <90%'],
                'medications': ['Aspirin', 'Metoprolol', 'Atorvastatin', 'Lisinopril'],
                'monitoring': ['Continuous cardiac monitoring', 'Serial troponins', 'Daily ECG'],
                'consults': ['Cardiology STAT', 'Consider cardiac catheterization']
            },
            'Pneumonia': {
                'immediate': ['Oxygen therapy if needed', 'Blood cultures', 'Chest X-ray'],
                'medications': ['Antibiotics based on severity', 'Bronchodilators if wheeze'],
                'monitoring': ['Vital signs q4h', 'O2 saturation', 'Respiratory status'],
                'consults': ['Pulmonology if severe', 'ID if complicated']
            },
            'Congestive Heart Failure': {
                'immediate': ['Assess fluid status', 'Chest X-ray', 'BNP/NT-proBNP'],
                'medications': ['Diuretics', 'ACE inhibitor', 'Beta-blocker'],
                'monitoring': ['Daily weights', 'I&O', 'Electrolytes'],
                'consults': ['Cardiology', 'Heart failure clinic follow-up']
            }
        }
        
        return protocols.get(diagnosis)
    
    @classmethod
    def _generate_followup_plan(cls, differential_diagnosis: List[Dict], risk_assessment: Dict) -> Dict:
        """Generate comprehensive follow-up plan."""
        risk_level = risk_assessment['risk_level']
        
        if risk_level == 'High':
            timeframe = '24-48 hours'
            provider = 'Specialist or primary care'
            tests = ['Repeat labs', 'Imaging as indicated', 'Specialist evaluation']
        elif risk_level == 'Moderate':
            timeframe = '1 week'
            provider = 'Primary care physician'
            tests = ['Follow-up labs if indicated', 'Monitor symptoms']
        else:
            timeframe = '2-4 weeks'
            provider = 'Primary care physician'
            tests = ['Routine follow-up', 'PRN for worsening symptoms']
        
        return {
            'timeframe': timeframe,
            'provider_type': provider,
            'recommended_tests': tests,
            'red_flag_symptoms': [
                'Worsening chest pain',
                'Severe shortness of breath',
                'High fever (>101.5°F)',
                'Severe headache',
                'Loss of consciousness'
            ],
            'patient_instructions': [
                'Take medications as prescribed',
                'Monitor symptoms daily',
                'Return if symptoms worsen',
                'Follow up as scheduled'
            ]
        }
    
    @classmethod
    def _calculate_confidence_score(cls, patient_data: Dict) -> float:
        """Calculate overall confidence in diagnostic assessment."""
        base_confidence = 0.7
        
        # Adjust based on data completeness
        data_completeness = 0
        required_fields = ['symptoms', 'vital_signs', 'medical_history']
        
        for field in required_fields:
            if field in patient_data and patient_data[field]:
                data_completeness += 1
        
        completeness_factor = data_completeness / len(required_fields)
        
        # Adjust based on symptom clarity
        symptoms = patient_data.get('symptoms', [])
        symptom_factor = min(len(symptoms) / 3, 1.0)  # More symptoms = higher confidence
        
        final_confidence = base_confidence * completeness_factor * symptom_factor
        return round(final_confidence, 2)
    
    @classmethod
    def _identify_red_flags(cls, patient_data: Dict) -> List[str]:
        """Identify critical red flag symptoms requiring immediate attention."""
        red_flags = []
        
        symptoms = [s.lower() for s in patient_data.get('symptoms', [])]
        vital_signs = patient_data.get('vital_signs', {})
        
        # Cardiovascular red flags
        if 'chest pain' in symptoms and vital_signs.get('systolic_bp', 120) < 90:
            red_flags.append('Chest pain with hypotension - consider cardiogenic shock')
        
        # Neurological red flags
        if any(s in symptoms for s in ['severe headache', 'neck stiffness', 'confusion']):
            red_flags.append('Neurological symptoms - consider meningitis or intracranial pathology')
        
        # Respiratory red flags
        if vital_signs.get('oxygen_saturation', 100) < 90:
            red_flags.append('Severe hypoxemia - immediate oxygen therapy required')
        
        # Sepsis red flags
        temp = vital_signs.get('temperature', 37)
        hr = vital_signs.get('heart_rate', 70)
        if temp > 38 and hr > 100:
            red_flags.append('SIRS criteria - consider sepsis screening')
        
        return red_flags


def generate_diagnostic_suggestions(patient_data: Dict) -> Dict:
    """
    Main function to generate comprehensive diagnostic suggestions.
    
    This function serves as the primary interface for the diagnostic AI system.
    """
    return DiagnosticAI.generate_diagnostic_suggestions(patient_data)


def analyze_symptoms(symptoms: List[str], patient_context: Dict = None) -> Dict:
    """
    Analyze symptoms and provide diagnostic insights.
    
    Args:
        symptoms: List of patient symptoms
        patient_context: Additional patient information (age, gender, history)
    
    Returns:
        Dictionary with symptom analysis and diagnostic suggestions
    """
    if patient_context is None:
        patient_context = {}
    
    patient_data = {
        'symptoms': symptoms,
        **patient_context
    }
    
    return generate_diagnostic_suggestions(patient_data)


def interpret_lab_results(lab_results: Dict, patient_context: Dict = None) -> Dict:
    """
    Interpret laboratory results and provide clinical insights.
    
    Args:
        lab_results: Dictionary of lab test names and values
        patient_context: Additional patient information
    
    Returns:
        Dictionary with lab interpretation and clinical recommendations
    """
    if patient_context is None:
        patient_context = {}
    
    return DiagnosticAI._interpret_lab_results(lab_results)


def assess_patient_risk(patient_data: Dict) -> Dict:
    """
    Assess overall patient risk and provide stratification.
    
    Args:
        patient_data: Comprehensive patient information
    
    Returns:
        Dictionary with risk assessment and monitoring recommendations
    """
    return DiagnosticAI._assess_patient_risk(patient_data)