# AI Services Module Documentation

The `ai_services` module is the intelligence hub of HealthSphere. It centralizes all Large Language Model (LLM) interactions used to assist doctors and empower patients with personalized insights.

## Tech Stack
- **Framework**: Django
- **LLM Integration**: `ollama` Python client (drop-in replacement for Google Gemini API interface).
- **Default Model**: `gpt-oss:120b-cloud` (configurable via `OLLAMA_MODEL` in `.env`).

## Key Files & Functions

### `gemini_client.py`
Serves as an adapter/client for the local or remote Ollama model, maintaining a Gemini-like public API.
- `_probe()`: Checks if the Ollama service is available.
- `generate_text()`: Sends a prompt (and optional history/system instruction) to the LLM and returns the generated text.
- `is_available()`: Returns the availability status of the LLM.

### `diagnostic_ai.py`
Advanced AI-powered diagnostic assistance and clinical decision support tool for clinical staff.
- `generate_diagnostic_suggestions()`: Main interface; takes patient data and returns differential diagnoses.
- `_analyze_vital_signs()`: Analyzes vitals and flags abnormalities.
- `_interpret_lab_results()`: Interprets lab results and identifies critical/abnormal values.
- `_get_treatment_protocol()`: Recommends treatment guidelines based on likely diagnoses.
- `_identify_red_flags()`: Identifies critical symptoms requiring immediate attention.

### `triage_service.py`
Emergency triage algorithm combining rule-based heuristics with LLM enrichment.
- `calculate_triage_score()`: Calculates Emergency Severity Index (ESI) levels based on vital signs and symptoms.
- `_rule_based_triage()`: Fast, pure rule-based ESI scoring.
- `_build_triage_prompt()` & `_parse_llm_triage_response()`: Uses LLM to write a clinical narrative and recommend immediate actions based on the rule-based findings.

### `risk_service.py`
Predictive service for identifying patient health risks.
- `predict_risk()`: Generates a personalized risk assessment including risk level, contributing factors, and recommendations. Falls back to heuristics if LLM is offline.
- `get_risk_factors()`: Extracts detailed risk factors from patient history.

### `journey_service.py`
Generates real-time patient journey summaries and health insights.
- `get_patient_journey_summary()`: Produces an AI-powered summary of the patient's holistic healthcare journey.
- `get_patient_ai_insights()`: Generates actionable, personalized AI health insights for the patient portal dashboard.
- `predict_journey_milestones()`: Predicts upcoming milestones in the patient's treatment.

### `report_explainer.py`
Translates clinical reports into patient-friendly language.
- `extract_pdf_text()`: Utility to extract raw text from uploaded PDF lab reports.
- `explain_report()`: Connects to the LLM to summarize the report, extract key findings, and add a patient-friendly summary.
- `simplify_medical_terms()`: Converts tough clinical jargon into plain English.
- `generate_questions()`: Suggests customized questions for the patient to ask their doctor at the next consultation.
