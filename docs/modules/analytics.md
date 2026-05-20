# Analytics Module Documentation

The `analytics` module acts as the business intelligence engine for HealthSphere. It provides data visualization, reporting, and predictive models to improve hospital operations and clinical outcomes.

## Tech Stack
- **Framework**: Django
- **Predictive Engine**: Custom Python logic (`predictive_analytics.py`) handling heuristic modeling, time series forecasting, and risk categorizations.
- **Access Control**: Custom `AnalyticsAccessMixin` restricting views to Admins and Doctors.

## Key Files & Functions

### `models.py`
- **`PredictiveModel`**: Base model storing metadata (version, accuracy, last trained) for predictive analytics models.
- **`PatientFlowPrediction`**: Stores predictions for patient volume over different time horizons (e.g., next hour, 24 hours). Useful for staffing and capacity planning.
- **`ClinicalOutcomePrediction`**: Stores clinical predictions like mortality risk, readmission risk, and length of stay for individual patients.
  - `get_risk_color()`: Returns a color code based on the risk level (e.g., 'critical' -> 'danger').
  - `is_high_risk()`: Helper to flag critical patients.
- **`AnalyticsReport`**: Tracks generated scheduled reports and dashboards.
- **`DataQualityMetric`**: Tracks the completeness and accuracy of data feeding into the analytics system to ensure reliable predictions.

### `predictive_analytics.py`
Houses the core forecasting classes:
- **`PatientFlowPredictor`**: Analyzes historical admission data to predict resource demand and staff needs.
  - `predict_patient_flow()`: Core functional API.
  - `_calculate_seasonal_factor()`, `_calculate_trend_factor()`: Internals for time series predictions.
  - `_predict_staff_needs()`, `_predict_resource_demand()`: Translation of volume to resource requirements.
- **`ClinicalOutcomePredictor`**: Calculates various clinical risks based on patient demographics, vitals, and medical history.
  - `predict_clinical_outcome()`: Core functional API.
  - `_predict_readmission_risk()`, `_predict_mortality_risk()`, `_predict_complication_risk()`, `_predict_length_of_stay()`: Specific clinical scoring heuristic algorithms.

### `views.py`
Features comprehensive dashboards powered by real application data.
- **`AnalyticsDashboardView`**: Master dashboard combining various metrics.
- **`PatientFlowDashboardView`**: Dashboard specifically focused on admissions, discharges, and appointments.
- **`ClinicalOutcomesDashboardView`**: Visualizes predictions for clinical risks and outcomes drawn from `MedicalRecord`s.
- **`ReportsDashboardView`**: Operational reports overview.
- **`DataQualityDashboardView`**: Shows metrics on missing or incomplete data across the platform.
- Various **Detail and List Views** (`ModelsListView`, `PatientFlowPredictionsView`, `ClinicalOutcomePredictionsView`) for exploring stored analytics data via Django standard Class-Based Views.
