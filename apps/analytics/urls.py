from django.urls import path
from .views import (
    AnalyticsView, AdminSettingsView, RetrainView,
    AdminStudentsView, AdminRecommendationAuditView,
)

urlpatterns = [
    path('analytics/', AnalyticsView.as_view(), name='admin-analytics'),
    path('analytics/recommendations/', AdminRecommendationAuditView.as_view(), name='admin-rec-audit'),
    path('settings/', AdminSettingsView.as_view(), name='admin-settings'),
    path('engine/retrain/', RetrainView.as_view(), name='admin-retrain'),
    path('students/', AdminStudentsView.as_view(), name='admin-students'),
]
