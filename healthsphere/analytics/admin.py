"""
HealthSphere AI - Analytics Admin Interface
==========================================

Django admin configuration for predictive analytics models.
Provides comprehensive management interface for analytics models, predictions, and reports.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.forms import TextInput, Textarea
import json

from .models import (
    PredictiveModel,
    PatientFlowPrediction, 
    ClinicalOutcomePrediction,
    AnalyticsReport,
    DataQualityMetric
)


@admin.register(PredictiveModel)
class PredictiveModelAdmin(admin.ModelAdmin):
    """Admin interface for predictive models."""
    
    list_display = [
        'name', 'model_type', 'algorithm', 'version', 
        'accuracy_display', 'is_active', 'is_production_ready',
        'trained_at', 'next_retrain_due'
    ]
    list_filter = [
        'model_type', 'algorithm', 'is_active', 'is_production_ready',
        'trained_at', 'created_at'
    ]
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'trained_at']
    
    fieldsets = [
        ('Model Information', {
            'fields': ['name', 'model_type', 'algorithm', 'version', 'description']
        }),
        ('Performance Metrics', {
            'fields': ['accuracy', 'precision', 'recall', 'f1_score'],
            'classes': ['collapse']
        }),
        ('Configuration', {
            'fields': ['parameters', 'training_data_summary'],
            'classes': ['collapse']
        }),
        ('Lifecycle Management', {
            'fields': ['is_active', 'is_production_ready', 'last_retrained', 'next_retrain_due']
        }),
        ('Metadata', {
            'fields': ['created_by', 'created_at', 'updated_at', 'trained_at'],
            'classes': ['collapse']
        })
    ]
    
    formfield_overrides = {
        models.JSONField: {'widget': Textarea(attrs={'rows': 4, 'cols': 80})},
    }
    
    def accuracy_display(self, obj):
        """Display accuracy with color coding."""
        if obj.accuracy is not None:
            color = 'green' if obj.accuracy >= 0.9 else 'orange' if obj.accuracy >= 0.8 else 'red'
            return format_html(
                '<span style="color: {};">{:.1%}</span>',
                color, obj.accuracy
            )
        return '-'
    accuracy_display.short_description = 'Accuracy'
    accuracy_display.admin_order_field = 'accuracy'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(PatientFlowPrediction)
class PatientFlowPredictionAdmin(admin.ModelAdmin):
    """Admin interface for patient flow predictions."""
    
    list_display = [
        'department', 'target_date', 'prediction_horizon',
        'predicted_bed_occupancy', 'capacity_utilization_display',
        'confidence_display', 'accuracy_display'
    ]
    list_filter = [
        'department', 'prediction_horizon', 'prediction_date',
        'target_date'
    ]
    search_fields = ['department']
    readonly_fields = ['created_at', 'prediction_error']
    date_hierarchy = 'target_date'
    
    fieldsets = [
        ('Prediction Details', {
            'fields': [
                'model', 'department', 'prediction_horizon', 'target_date',
                'prediction_date'
            ]
        }),
        ('Predicted Values', {
            'fields': [
                'predicted_admissions', 'predicted_discharges', 
                'predicted_bed_occupancy', 'predicted_capacity_utilization'
            ]
        }),
        ('Confidence & Uncertainty', {
            'fields': [
                'confidence_score', 'prediction_interval_lower', 
                'prediction_interval_upper'
            ],
            'classes': ['collapse']
        }),
        ('Additional Predictions', {
            'fields': ['predicted_staff_needed', 'predicted_resource_demand'],
            'classes': ['collapse']
        }),
        ('Actual Values & Validation', {
            'fields': [
                'actual_admissions', 'actual_discharges', 
                'actual_bed_occupancy', 'prediction_error'
            ],
            'classes': ['collapse']
        })
    ]
    
    def capacity_utilization_display(self, obj):
        """Display capacity utilization with color coding."""
        utilization = obj.predicted_capacity_utilization
        if utilization >= 1.0:
            color = 'red'
            icon = '⚠️'
        elif utilization >= 0.9:
            color = 'orange'
            icon = '⚡'
        elif utilization >= 0.7:
            color = 'green'
            icon = '✅'
        else:
            color = 'blue'
            icon = '📉'
        
        return format_html(
            '{} <span style="color: {};">{:.1%}</span>',
            icon, color, utilization
        )
    capacity_utilization_display.short_description = 'Capacity'
    capacity_utilization_display.admin_order_field = 'predicted_capacity_utilization'
    
    def confidence_display(self, obj):
        """Display confidence score with color coding."""
        confidence = obj.confidence_score
        color = 'green' if confidence >= 0.8 else 'orange' if confidence >= 0.6 else 'red'
        return format_html(
            '<span style="color: {};">{:.1%}</span>',
            color, confidence
        )
    confidence_display.short_description = 'Confidence'
    confidence_display.admin_order_field = 'confidence_score'
    
    def accuracy_display(self, obj):
        """Display prediction accuracy if available."""
        if obj.actual_bed_occupancy is not None:
            accuracy = obj.calculate_accuracy()
            if accuracy is not None:
                color = 'green' if accuracy >= 0.9 else 'orange' if accuracy >= 0.7 else 'red'
                return format_html(
                    '<span style="color: {};">{:.1%}</span>',
                    color, accuracy
                )
        return '-'
    accuracy_display.short_description = 'Actual Accuracy'


@admin.register(ClinicalOutcomePrediction)
class ClinicalOutcomePredictionAdmin(admin.ModelAdmin):
    """Admin interface for clinical outcome predictions."""
    
    list_display = [
        'patient_name', 'outcome_type', 'risk_level_display', 
        'risk_score', 'confidence_display', 'created_at',
        'actual_outcome_display'
    ]
    list_filter = [
        'outcome_type', 'risk_level', 'created_at',
        'actual_outcome', 'prediction_horizon_days'
    ]
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = [
        ('Prediction Details', {
            'fields': [
                'model', 'patient', 'outcome_type', 'risk_level', 'risk_score',
                'predicted_date', 'prediction_horizon_days'
            ]
        }),
        ('Risk Assessment', {
            'fields': ['risk_factors', 'protective_factors', 'confidence_score'],
            'classes': ['collapse']
        }),
        ('Clinical Context', {
            'fields': [
                'diagnosis_codes', 'current_medications', 
                'vital_signs_at_prediction', 'lab_values_at_prediction'
            ],
            'classes': ['collapse']
        }),
        ('Recommendations', {
            'fields': [
                'explanation', 'recommended_interventions', 
                'monitoring_recommendations'
            ],
            'classes': ['collapse']
        }),
        ('Outcome Tracking', {
            'fields': [
                'actual_outcome', 'actual_outcome_date', 'outcome_notes'
            ],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['created_by', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def patient_name(self, obj):
        """Display patient name with link to patient."""
        if obj.patient:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:users_user_change', args=[obj.patient.pk]),
                obj.patient.get_full_name()
            )
        return '-'
    patient_name.short_description = 'Patient'
    patient_name.admin_order_field = 'patient__last_name'
    
    def risk_level_display(self, obj):
        """Display risk level with color coding."""
        colors = {
            'low': 'green',
            'moderate': 'orange', 
            'high': 'red',
            'critical': 'darkred'
        }
        icons = {
            'low': '🟢',
            'moderate': '🟡',
            'high': '🔴',
            'critical': '🚨'
        }
        
        color = colors.get(obj.risk_level, 'gray')
        icon = icons.get(obj.risk_level, '❓')
        
        return format_html(
            '{} <span style="color: {}; font-weight: bold;">{}</span>',
            icon, color, obj.risk_level.upper()
        )
    risk_level_display.short_description = 'Risk Level'
    risk_level_display.admin_order_field = 'risk_level'
    
    def confidence_display(self, obj):
        """Display confidence score with color coding."""
        confidence = obj.confidence_score
        color = 'green' if confidence >= 0.8 else 'orange' if confidence >= 0.6 else 'red'
        return format_html(
            '<span style="color: {};">{:.1%}</span>',
            color, confidence
        )
    confidence_display.short_description = 'Confidence'
    confidence_display.admin_order_field = 'confidence_score'
    
    def actual_outcome_display(self, obj):
        """Display actual outcome with status."""
        if obj.actual_outcome is not None:
            if obj.actual_outcome:
                return format_html('<span style="color: red;">❌ Occurred</span>')
            else:
                return format_html('<span style="color: green;">✅ Avoided</span>')
        return format_html('<span style="color: gray;">⏳ Pending</span>')
    actual_outcome_display.short_description = 'Actual Outcome'
    actual_outcome_display.admin_order_field = 'actual_outcome'


@admin.register(AnalyticsReport)
class AnalyticsReportAdmin(admin.ModelAdmin):
    """Admin interface for analytics reports."""
    
    list_display = [
        'name', 'report_type', 'frequency', 'report_date',
        'period_display', 'status', 'generated_by'
    ]
    list_filter = [
        'report_type', 'frequency', 'status', 'is_scheduled',
        'is_public', 'generated_at'
    ]
    search_fields = ['name']
    readonly_fields = ['generated_at']
    date_hierarchy = 'report_date'
    
    fieldsets = [
        ('Report Information', {
            'fields': ['name', 'report_type', 'frequency', 'status']
        }),
        ('Time Period', {
            'fields': ['report_date', 'period_start', 'period_end']
        }),
        ('Report Data', {
            'fields': ['data', 'charts', 'kpis'],
            'classes': ['collapse']
        }),
        ('Access & Distribution', {
            'fields': ['is_public', 'is_scheduled', 'shared_with'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['generated_by', 'generated_at'],
            'classes': ['collapse']
        })
    ]
    
    filter_horizontal = ['shared_with']
    
    def period_display(self, obj):
        """Display report period in readable format."""
        return obj.get_period_display()
    period_display.short_description = 'Period'


@admin.register(DataQualityMetric)
class DataQualityMetricAdmin(admin.ModelAdmin):
    """Admin interface for data quality metrics."""
    
    list_display = [
        'data_source', 'metric_type', 'score_display',
        'threshold_status', 'metric_date', 'alert_status'
    ]
    list_filter = [
        'metric_type', 'alert_triggered', 'alert_acknowledged',
        'metric_date'
    ]
    search_fields = ['data_source']
    readonly_fields = ['created_at']
    date_hierarchy = 'metric_date'
    
    fieldsets = [
        ('Metric Information', {
            'fields': ['data_source', 'metric_type', 'metric_date']
        }),
        ('Quality Assessment', {
            'fields': [
                'score', 'threshold', 'total_records', 
                'passed_records', 'failed_records'
            ]
        }),
        ('Details & Issues', {
            'fields': ['details', 'issues_identified'],
            'classes': ['collapse']
        }),
        ('Alert Management', {
            'fields': [
                'alert_triggered', 'alert_acknowledged', 'acknowledged_by'
            ],
            'classes': ['collapse']
        })
    ]
    
    def score_display(self, obj):
        """Display quality score with color coding."""
        score = obj.score
        color = 'green' if score >= obj.threshold else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1%}</span>',
            color, score
        )
    score_display.short_description = 'Quality Score'
    score_display.admin_order_field = 'score'
    
    def threshold_status(self, obj):
        """Display threshold status."""
        if obj.score >= obj.threshold:
            return format_html('<span style="color: green;">✅ Pass</span>')
        else:
            return format_html('<span style="color: red;">❌ Fail</span>')
    threshold_status.short_description = 'Threshold'
    
    def alert_status(self, obj):
        """Display alert status."""
        if obj.alert_triggered:
            if obj.alert_acknowledged:
                return format_html('<span style="color: blue;">🔔 Acknowledged</span>')
            else:
                return format_html('<span style="color: red;">🚨 Active Alert</span>')
        return format_html('<span style="color: green;">✅ Normal</span>')
    alert_status.short_description = 'Alert Status'


# Customize admin site headers
admin.site.site_header = "HealthSphere AI - Analytics Administration"
admin.site.site_title = "Analytics Admin"
admin.site.index_title = "Predictive Analytics Management"
