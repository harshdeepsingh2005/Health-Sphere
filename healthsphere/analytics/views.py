"""
HealthSphere AI - Analytics Views
=================================

Views for predictive analytics dashboard, reports, and API endpoints.
Provides comprehensive analytics interface for healthcare insights.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, View
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json

from .models import (
    PredictiveModel, PatientFlowPrediction, ClinicalOutcomePrediction,
    AnalyticsReport, DataQualityMetric
)
from .predictive_analytics import (
    create_patient_flow_prediction, create_clinical_outcome_prediction,
    assess_data_quality
)


class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    """Main analytics dashboard with key metrics and insights."""
    
    template_name = 'analytics/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Key performance indicators
        context.update({
            'total_models': PredictiveModel.objects.filter(is_active=True).count(),
            'production_models': PredictiveModel.objects.filter(
                is_active=True, is_production_ready=True
            ).count(),
            'recent_predictions': ClinicalOutcomePrediction.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
            'high_risk_patients': ClinicalOutcomePrediction.objects.filter(
                risk_level__in=['high', 'critical'],
                created_at__gte=timezone.now() - timedelta(days=1)
            ).count(),
        })
        
        # Recent activity
        context['recent_flow_predictions'] = PatientFlowPrediction.objects.select_related(
            'model'
        ).order_by('-prediction_date')[:10]
        
        context['recent_outcome_predictions'] = ClinicalOutcomePrediction.objects.select_related(
            'model', 'patient'
        ).order_by('-created_at')[:10]
        
        # Data quality alerts
        context['data_quality_alerts'] = DataQualityMetric.objects.filter(
            alert_triggered=True, alert_acknowledged=False
        ).count()
        
        return context


class PatientFlowDashboardView(LoginRequiredMixin, TemplateView):
    """Patient flow analytics dashboard."""
    
    template_name = 'analytics/patient_flow_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Current date for predictions
        now = timezone.now()
        
        # Get recent predictions by department
        departments = ['emergency', 'icu', 'general_ward', 'surgery']
        predictions_by_dept = {}
        
        for dept in departments:
            predictions_by_dept[dept] = PatientFlowPrediction.objects.filter(
                department=dept,
                target_date__gte=now,
                target_date__lte=now + timedelta(hours=24)
            ).order_by('target_date')[:12]
        
        context['predictions_by_department'] = predictions_by_dept
        
        # Capacity utilization summary
        context['capacity_alerts'] = PatientFlowPrediction.objects.filter(
            target_date__gte=now,
            target_date__lte=now + timedelta(hours=12),
            predicted_capacity_utilization__gte=0.9
        ).select_related('model').order_by('-predicted_capacity_utilization')[:10]
        
        return context


class ClinicalOutcomesDashboardView(LoginRequiredMixin, TemplateView):
    """Clinical outcomes analytics dashboard."""
    
    template_name = 'analytics/clinical_outcomes_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Risk level distribution
        risk_distribution = ClinicalOutcomePrediction.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).values('risk_level').annotate(count=Count('id'))
        
        context['risk_distribution'] = {item['risk_level']: item['count'] for item in risk_distribution}
        
        # High-risk patients requiring attention
        context['high_risk_patients'] = ClinicalOutcomePrediction.objects.filter(
            risk_level__in=['high', 'critical'],
            created_at__gte=timezone.now() - timedelta(days=1)
        ).select_related('patient', 'model').order_by('-risk_score')[:20]
        
        # Outcome type distribution
        outcome_distribution = ClinicalOutcomePrediction.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).values('outcome_type').annotate(count=Count('id'))
        
        context['outcome_distribution'] = {item['outcome_type']: item['count'] for item in outcome_distribution}
        
        return context


class ReportsDashboardView(LoginRequiredMixin, ListView):
    """Analytics reports dashboard."""
    
    model = AnalyticsReport
    template_name = 'analytics/reports_dashboard.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        return AnalyticsReport.objects.select_related(
            'generated_by'
        ).order_by('-report_date')


class DataQualityDashboardView(LoginRequiredMixin, TemplateView):
    """Data quality monitoring dashboard."""
    
    template_name = 'analytics/data_quality_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Recent quality metrics
        context['recent_metrics'] = DataQualityMetric.objects.order_by(
            'data_source', '-metric_date'
        ).distinct('data_source')[:20]
        
        # Active alerts
        context['active_alerts'] = DataQualityMetric.objects.filter(
            alert_triggered=True, alert_acknowledged=False
        ).order_by('-metric_date')
        
        # Quality trends
        context['quality_trends'] = DataQualityMetric.objects.filter(
            metric_date__gte=timezone.now() - timedelta(days=30)
        ).values('metric_type').annotate(
            avg_score=Avg('score')
        ).order_by('metric_type')
        
        return context


class ModelsListView(LoginRequiredMixin, ListView):
    """List of predictive models."""
    
    model = PredictiveModel
    template_name = 'analytics/models_list.html'
    context_object_name = 'models'
    paginate_by = 20
    
    def get_queryset(self):
        return PredictiveModel.objects.select_related('created_by').order_by('-created_at')


class ModelDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a predictive model."""
    
    model = PredictiveModel
    template_name = 'analytics/model_detail.html'
    context_object_name = 'model'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_obj = self.get_object()
        
        # Model performance metrics
        if model_obj.model_type == 'patient_flow':
            recent_predictions = model_obj.flow_predictions.order_by('-prediction_date')[:20]
        else:
            recent_predictions = model_obj.outcome_predictions.order_by('-created_at')[:20]
        
        context['recent_predictions'] = recent_predictions
        return context


class PatientFlowPredictionsView(LoginRequiredMixin, ListView):
    """List of patient flow predictions."""
    
    model = PatientFlowPrediction
    template_name = 'analytics/patient_flow_predictions.html'
    context_object_name = 'predictions'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = PatientFlowPrediction.objects.select_related('model').order_by('-prediction_date')
        
        # Filter by department if specified
        department = self.request.GET.get('department')
        if department:
            queryset = queryset.filter(department=department)
        
        # Filter by date range if specified
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(target_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(target_date__lte=date_to)
        
        return queryset


class ClinicalOutcomePredictionsView(LoginRequiredMixin, ListView):
    """List of clinical outcome predictions."""
    
    model = ClinicalOutcomePrediction
    template_name = 'analytics/clinical_outcome_predictions.html'
    context_object_name = 'predictions'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = ClinicalOutcomePrediction.objects.select_related(
            'model', 'patient'
        ).order_by('-created_at')
        
        # Filter by risk level if specified
        risk_level = self.request.GET.get('risk_level')
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        
        # Filter by outcome type if specified
        outcome_type = self.request.GET.get('outcome_type')
        if outcome_type:
            queryset = queryset.filter(outcome_type=outcome_type)
        
        return queryset


class ReportDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of an analytics report."""
    
    model = AnalyticsReport
    template_name = 'analytics/report_detail.html'
    context_object_name = 'report'


class ReportDownloadView(LoginRequiredMixin, View):
    """Download analytics report."""
    
    def get(self, request, pk):
        report = get_object_or_404(AnalyticsReport, pk=pk)
        
        # Generate report content
        content = json.dumps(report.data, indent=2)
        
        response = HttpResponse(content, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{report.name}_{report.report_date.strftime("%Y%m%d")}.json"'
        
        return response


# API Views
class PatientFlowPredictionAPIView(LoginRequiredMixin, View):
    """API endpoint for patient flow predictions."""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            department = data.get('department')
            prediction_horizon = data.get('prediction_horizon', '24_hours')
            target_date = datetime.fromisoformat(data.get('target_date', timezone.now().isoformat()))
            
            if not department:
                return JsonResponse({'error': 'Department is required'}, status=400)
            
            # Create prediction
            prediction = create_patient_flow_prediction(
                department=department,
                prediction_horizon=prediction_horizon,
                target_date=target_date
            )
            
            return JsonResponse({
                'success': True,
                'prediction': prediction
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class ClinicalOutcomePredictionAPIView(LoginRequiredMixin, View):
    """API endpoint for clinical outcome predictions."""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            patient_data = data.get('patient_data', {})
            outcome_type = data.get('outcome_type')
            
            if not outcome_type:
                return JsonResponse({'error': 'Outcome type is required'}, status=400)
            
            # Create prediction
            prediction = create_clinical_outcome_prediction(
                patient_data=patient_data,
                outcome_type=outcome_type
            )
            
            return JsonResponse({
                'success': True,
                'prediction': prediction
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class GenerateReportAPIView(LoginRequiredMixin, View):
    """API endpoint for generating analytics reports."""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            report_type = data.get('report_type')
            period_start = datetime.fromisoformat(data.get('period_start'))
            period_end = datetime.fromisoformat(data.get('period_end'))
            
            if not all([report_type, period_start, period_end]):
                return JsonResponse({'error': 'Report type and date range are required'}, status=400)
            
            # Generate report data based on type
            report_data = self._generate_report_data(report_type, period_start, period_end)
            
            # Create report record
            report = AnalyticsReport.objects.create(
                name=f"{report_type.replace('_', ' ').title()} Report",
                report_type=report_type,
                frequency='ad_hoc',
                period_start=period_start,
                period_end=period_end,
                data=report_data,
                generated_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'report_id': report.id,
                'report_data': report_data
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _generate_report_data(self, report_type, period_start, period_end):
        """Generate report data based on type and date range."""
        if report_type == 'patient_flow':
            return self._generate_patient_flow_report(period_start, period_end)
        elif report_type == 'clinical_outcomes':
            return self._generate_clinical_outcomes_report(period_start, period_end)
        elif report_type == 'operational_kpis':
            return self._generate_operational_kpis_report(period_start, period_end)
        else:
            return {'message': 'Report data generation not implemented for this type'}
    
    def _generate_patient_flow_report(self, start_date, end_date):
        """Generate patient flow analytics report."""
        predictions = PatientFlowPrediction.objects.filter(
            prediction_date__range=[start_date, end_date]
        )
        
        return {
            'total_predictions': predictions.count(),
            'departments': list(predictions.values('department').distinct()),
            'avg_capacity_utilization': predictions.aggregate(
                avg=Avg('predicted_capacity_utilization')
            )['avg'],
            'high_capacity_alerts': predictions.filter(
                predicted_capacity_utilization__gte=0.9
            ).count()
        }
    
    def _generate_clinical_outcomes_report(self, start_date, end_date):
        """Generate clinical outcomes analytics report."""
        predictions = ClinicalOutcomePrediction.objects.filter(
            created_at__range=[start_date, end_date]
        )
        
        return {
            'total_predictions': predictions.count(),
            'risk_distribution': dict(predictions.values('risk_level').annotate(
                count=Count('id')
            ).values_list('risk_level', 'count')),
            'outcome_distribution': dict(predictions.values('outcome_type').annotate(
                count=Count('id')
            ).values_list('outcome_type', 'count')),
            'avg_risk_score': predictions.aggregate(avg=Avg('risk_score'))['avg']
        }
    
    def _generate_operational_kpis_report(self, start_date, end_date):
        """Generate operational KPIs report."""
        return {
            'active_models': PredictiveModel.objects.filter(is_active=True).count(),
            'predictions_generated': (
                PatientFlowPrediction.objects.filter(
                    prediction_date__range=[start_date, end_date]
                ).count() +
                ClinicalOutcomePrediction.objects.filter(
                    created_at__range=[start_date, end_date]
                ).count()
            ),
            'data_quality_score': DataQualityMetric.objects.filter(
                metric_date__range=[start_date, end_date]
            ).aggregate(avg=Avg('score'))['avg'] or 0
        }


class DataQualityAssessmentAPIView(LoginRequiredMixin, View):
    """API endpoint for data quality assessment."""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            data_source = data.get('data_source')
            data_sample = data.get('data_sample', {})
            
            if not data_source:
                return JsonResponse({'error': 'Data source is required'}, status=400)
            
            # Perform quality assessment
            assessment = assess_data_quality(data_source, data_sample)
            
            return JsonResponse({
                'success': True,
                'assessment': assessment
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
