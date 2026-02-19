from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('insights/', views.AIInsightsView.as_view(), name='insights'),
    path('assistant/', views.AIAssistantView.as_view(), name='assistant'),
]
