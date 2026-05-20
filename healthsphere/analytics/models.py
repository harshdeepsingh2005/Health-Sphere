"""
HealthSphere AI - Analytics Models
==================================

Predictive analytics and business intelligence models for healthcare insights.
Provides patient flow prediction, resource optimization, and clinical outcome forecasting.

Features:
- Patient flow prediction with bed occupancy forecasting
- Resource optimization and staff allocation
- Clinical outcome prediction and risk assessment
- Operational analytics and KPI tracking
- Financial analytics and cost prediction
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import datetime, timedelta
import json

User = get_user_model()


class PredictiveModel(models.Model):
    """
    Base model for storing predictive analytics models and their metadata.
    Supports multiple ML model types and versioning.
    """
    
    MODEL_TYPES = [
        ('patient_flow', 'Patient Flow Prediction'),
        ('bed_occupancy', 'Bed Occupancy Forecasting'),
        ('resource_demand', 'Resource Demand Prediction'),
        ('readmission_risk', 'Readmission Risk Assessment'),
        ('length_of_stay', 'Length of Stay Prediction'),
        ('clinical_outcome', 'Clinical Outcome Prediction'),
        ('cost_prediction', 'Cost and Financial Forecasting'),
        ('staff_optimization', 'Staff Allocation Optimization'),
        ('equipment_maintenance', 'Equipment Maintenance Prediction'),
        ('supply_chain', 'Supply Chain Optimization'),
    ]
    
    ALGORITHM_TYPES = [
        ('linear_regression', 'Linear Regression'),
        ('random_forest', 'Random Forest'),
        ('gradient_boosting', 'Gradient Boosting'),
        ('neural_network', 'Neural Network'),
        ('time_series', 'Time Series (ARIMA/LSTM)'),
        ('clustering', 'Clustering (K-Means)'),
        ('classification', 'Classification (SVM/Logistic)'),
        ('ensemble', 'Ensemble Methods'),
    ]
    
    name = models.CharField(max_length=200, help_text="Model name")
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    algorithm = models.CharField(max_length=50, choices=ALGORITHM_TYPES)
    version = models.CharField(max_length=20, default="1.0.0")
    
    # Model performance metrics
    accuracy = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True, blank=True,
        help_text="Model accuracy (0-1)"
    )
    precision = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True, blank=True
    )
    recall = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True, blank=True
    )
    f1_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True, blank=True
    )
    
    # Model configuration and parameters
    parameters = models.JSONField(
        default=dict, blank=True,
        help_text="Model hyperparameters and configuration"
    )
    training_data_summary = models.JSONField(
        default=dict, blank=True,
        help_text="Summary of training data used"
    )
    
    # Model lifecycle
    is_active = models.BooleanField(default=True)
    is_production_ready = models.BooleanField(default=False)
    trained_at = models.DateTimeField(auto_now_add=True)
    last_retrained = models.DateTimeField(null=True, blank=True)
    next_retrain_due = models.DateTimeField(null=True, blank=True)
    
    # Model metadata
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_predictive_model'
        unique_together = ['name', 'version']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model_type', 'is_active']),
            models.Index(fields=['is_production_ready']),
            models.Index(fields=['next_retrain_due']),
        ]
    
    def __str__(self):
        return f"{self.name} v{self.version} ({self.get_model_type_display()})"
    
    def get_performance_summary(self):
        """Get formatted performance metrics summary."""
        metrics = {}
        if self.accuracy is not None:
            metrics['accuracy'] = f"{self.accuracy:.2%}"
        if self.precision is not None:
            metrics['precision'] = f"{self.precision:.2%}"
        if self.recall is not None:
            metrics['recall'] = f"{self.recall:.2%}"
        if self.f1_score is not None:
            metrics['f1_score'] = f"{self.f1_score:.3f}"
        return metrics


class PatientFlowPrediction(models.Model):
    """
    Store patient flow predictions for different time horizons.
    Helps with staffing, resource allocation, and capacity planning.
    """
    
    PREDICTION_HORIZONS = [
        ('1_hour', '1 Hour'),
        ('4_hours', '4 Hours'),
        ('12_hours', '12 Hours'),
        ('24_hours', '24 Hours'),
        ('48_hours', '48 Hours'),
        ('7_days', '7 Days'),
        ('30_days', '30 Days'),
    ]
    
    DEPARTMENTS = [
        ('emergency', 'Emergency Department'),
        ('icu', 'Intensive Care Unit'),
        ('general_ward', 'General Ward'),
        ('surgery', 'Surgery'),
        ('maternity', 'Maternity'),
        ('pediatrics', 'Pediatrics'),
        ('cardiology', 'Cardiology'),
        ('oncology', 'Oncology'),
        ('outpatient', 'Outpatient Clinic'),
    ]
    
    model = models.ForeignKey(PredictiveModel, on_delete=models.CASCADE, related_name='flow_predictions')
    
    # Prediction metadata
    prediction_date = models.DateTimeField(default=timezone.now)
    prediction_horizon = models.CharField(max_length=20, choices=PREDICTION_HORIZONS)
    target_date = models.DateTimeField(help_text="Date/time for which prediction is made")
    department = models.CharField(max_length=50, choices=DEPARTMENTS)
    
    # Predicted values
    predicted_admissions = models.PositiveIntegerField(default=0)
    predicted_discharges = models.PositiveIntegerField(default=0)
    predicted_bed_occupancy = models.PositiveIntegerField(default=0)
    predicted_capacity_utilization = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(2)],
        help_text="Capacity utilization ratio (0-2, >1 indicates overcapacity)"
    )
    
    # Confidence and uncertainty
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Model confidence in prediction (0-1)"
    )
    prediction_interval_lower = models.FloatField(null=True, blank=True)
    prediction_interval_upper = models.FloatField(null=True, blank=True)
    
    # Additional predictions
    predicted_staff_needed = models.JSONField(
        default=dict, blank=True,
        help_text="Predicted staffing needs by role"
    )
    predicted_resource_demand = models.JSONField(
        default=dict, blank=True,
        help_text="Predicted resource requirements"
    )
    
    # Actual values for validation
    actual_admissions = models.PositiveIntegerField(null=True, blank=True)
    actual_discharges = models.PositiveIntegerField(null=True, blank=True)
    actual_bed_occupancy = models.PositiveIntegerField(null=True, blank=True)
    
    # Model performance tracking
    prediction_error = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_patient_flow_prediction'
        ordering = ['-prediction_date', 'target_date']
        indexes = [
            models.Index(fields=['department', 'target_date']),
            models.Index(fields=['prediction_horizon', 'prediction_date']),
            models.Index(fields=['target_date']),
        ]
    
    def __str__(self):
        return f"{self.department} flow prediction for {self.target_date.strftime('%Y-%m-%d %H:%M')}"
    
    def calculate_accuracy(self):
        """Calculate prediction accuracy if actual values are available."""
        if self.actual_bed_occupancy is not None and self.predicted_bed_occupancy:
            error = abs(self.actual_bed_occupancy - self.predicted_bed_occupancy)
            accuracy = max(0, 1 - (error / max(self.actual_bed_occupancy, 1)))
            self.prediction_error = error
            return accuracy
        return None


class ClinicalOutcomePrediction(models.Model):
    """
    Store predictions for clinical outcomes and patient risk assessments.
    Supports risk stratification and early warning systems.
    """
    
    OUTCOME_TYPES = [
        ('mortality_risk', 'Mortality Risk'),
        ('readmission_risk', 'Readmission Risk'),
        ('complication_risk', 'Complication Risk'),
        ('length_of_stay', 'Length of Stay'),
        ('icu_admission', 'ICU Admission Risk'),
        ('surgery_outcome', 'Surgical Outcome'),
        ('medication_response', 'Medication Response'),
        ('infection_risk', 'Healthcare-Associated Infection Risk'),
    ]
    
    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('moderate', 'Moderate Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]
    
    model = models.ForeignKey(PredictiveModel, on_delete=models.CASCADE, related_name='outcome_predictions')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='outcome_predictions')
    
    # Prediction details
    outcome_type = models.CharField(max_length=50, choices=OUTCOME_TYPES)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)
    risk_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Risk score (0-1, higher is riskier)"
    )
    
    # Time-based predictions
    predicted_date = models.DateTimeField(null=True, blank=True)
    prediction_horizon_days = models.PositiveIntegerField(
        default=30,
        help_text="Prediction horizon in days"
    )
    
    # Contributing factors
    risk_factors = models.JSONField(
        default=list, blank=True,
        help_text="Key risk factors identified by the model"
    )
    protective_factors = models.JSONField(
        default=list, blank=True,
        help_text="Protective factors that reduce risk"
    )
    
    # Clinical context
    diagnosis_codes = models.JSONField(default=list, blank=True)
    current_medications = models.JSONField(default=list, blank=True)
    vital_signs_at_prediction = models.JSONField(default=dict, blank=True)
    lab_values_at_prediction = models.JSONField(default=dict, blank=True)
    
    # Model confidence and interpretability
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Model confidence in prediction"
    )
    explanation = models.TextField(blank=True, help_text="Human-readable explanation")
    
    # Recommendations
    recommended_interventions = models.JSONField(
        default=list, blank=True,
        help_text="Recommended clinical interventions"
    )
    monitoring_recommendations = models.JSONField(
        default=list, blank=True,
        help_text="Recommended monitoring protocols"
    )
    
    # Outcome tracking
    actual_outcome = models.BooleanField(null=True, blank=True)
    actual_outcome_date = models.DateTimeField(null=True, blank=True)
    outcome_notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_outcome_predictions'
    )
    
    class Meta:
        db_table = 'analytics_clinical_outcome_prediction'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'outcome_type']),
            models.Index(fields=['risk_level', 'created_at']),
            models.Index(fields=['predicted_date']),
            models.Index(fields=['outcome_type', 'risk_score']),
        ]
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.get_outcome_type_display()} ({self.risk_level})"
    
    def get_risk_color(self):
        """Get color code for risk level visualization."""
        colors = {
            'low': '#28a745',      # Green
            'moderate': '#ffc107',  # Yellow
            'high': '#fd7e14',     # Orange
            'critical': '#dc3545'  # Red
        }
        return colors.get(self.risk_level, '#6c757d')
    
    def is_high_risk(self):
        """Check if patient is in high or critical risk category."""
        return self.risk_level in ['high', 'critical']


class AnalyticsReport(models.Model):
    """
    Store generated analytics reports and dashboards.
    Supports scheduled reporting and key performance indicators.
    """
    
    REPORT_TYPES = [
        ('patient_flow', 'Patient Flow Analytics'),
        ('resource_utilization', 'Resource Utilization Report'),
        ('clinical_outcomes', 'Clinical Outcomes Analysis'),
        ('financial_analytics', 'Financial Performance Report'),
        ('quality_metrics', 'Quality Metrics Dashboard'),
        ('operational_kpis', 'Operational KPIs'),
        ('predictive_insights', 'Predictive Analytics Insights'),
        ('department_performance', 'Department Performance Report'),
    ]
    
    REPORT_FREQUENCIES = [
        ('real_time', 'Real-time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
        ('ad_hoc', 'Ad-hoc'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    frequency = models.CharField(max_length=20, choices=REPORT_FREQUENCIES)
    
    # Report data and visualization
    data = models.JSONField(default=dict, help_text="Report data and metrics")
    charts = models.JSONField(default=list, blank=True, help_text="Chart configurations")
    kpis = models.JSONField(default=dict, blank=True, help_text="Key performance indicators")
    
    # Time period
    report_date = models.DateTimeField(default=timezone.now)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Report metadata
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # Distribution and access
    shared_with = models.ManyToManyField(
        User, blank=True, related_name='accessible_reports',
        help_text="Users who have access to this report"
    )
    is_public = models.BooleanField(default=False)
    is_scheduled = models.BooleanField(default=False)
    
    # Report status
    status = models.CharField(
        max_length=20,
        choices=[
            ('generating', 'Generating'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('archived', 'Archived'),
        ],
        default='completed'
    )
    
    class Meta:
        db_table = 'analytics_report'
        ordering = ['-report_date']
        indexes = [
            models.Index(fields=['report_type', 'report_date']),
            models.Index(fields=['frequency', 'is_scheduled']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.report_date.strftime('%Y-%m-%d')})"
    
    def get_period_display(self):
        """Get formatted display of report period."""
        start = self.period_start.strftime('%Y-%m-%d')
        end = self.period_end.strftime('%Y-%m-%d')
        return f"{start} to {end}"


class DataQualityMetric(models.Model):
    """
    Track data quality metrics for analytics models.
    Ensures reliable predictions by monitoring data completeness, accuracy, and consistency.
    """
    
    METRIC_TYPES = [
        ('completeness', 'Data Completeness'),
        ('accuracy', 'Data Accuracy'),
        ('consistency', 'Data Consistency'),
        ('timeliness', 'Data Timeliness'),
        ('validity', 'Data Validity'),
        ('uniqueness', 'Data Uniqueness'),
    ]
    
    data_source = models.CharField(max_length=100, help_text="Source system or table")
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    
    # Metric values
    score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Quality score (0-1, higher is better)"
    )
    threshold = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        default=0.95,
        help_text="Quality threshold for alerting"
    )
    
    # Metric details
    total_records = models.PositiveIntegerField(default=0)
    passed_records = models.PositiveIntegerField(default=0)
    failed_records = models.PositiveIntegerField(default=0)
    
    # Context
    metric_date = models.DateTimeField(default=timezone.now)
    details = models.JSONField(default=dict, blank=True)
    issues_identified = models.JSONField(default=list, blank=True)
    
    # Alert status
    alert_triggered = models.BooleanField(default=False)
    alert_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_data_quality_metric'
        ordering = ['-metric_date']
        indexes = [
            models.Index(fields=['data_source', 'metric_type']),
            models.Index(fields=['alert_triggered', 'alert_acknowledged']),
            models.Index(fields=['metric_date']),
        ]
    
    def __str__(self):
        return f"{self.data_source} - {self.get_metric_type_display()}: {self.score:.2%}"
    
    def check_threshold_breach(self):
        """Check if metric breaches quality threshold."""
        if self.score < self.threshold and not self.alert_triggered:
            self.alert_triggered = True
            self.save()
            return True
        return False
