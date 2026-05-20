from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('insights/', views.ai_insights_view, name='insights'),
    path('assistant/', views.ai_assistant_view, name='assistant'),

    # AJAX endpoints
    path('api/chat/', views.ai_chat_api, name='chat_api'),
    path('api/explain-report/', views.explain_report_api, name='explain_report_api'),
    path('api/risk-assessment/', views.risk_assessment_api, name='risk_assessment_api'),
    path('api/health-insights/', views.health_insights_api, name='health_insights_api'),
]
