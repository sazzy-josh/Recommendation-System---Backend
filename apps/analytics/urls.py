from django.urls import path
from .views import (
    AnalyticsView, AdminSettingsView, RetrainView,
    AdminStudentsView, AdminRecommendationAuditView,
    AdminStudentInteractionsView, AdminStudentDetailView,
    AdminStudentEnrollmentsView,
)

urlpatterns = [
    path('analytics/', AnalyticsView.as_view(), name='admin-analytics'),
    path('analytics/recommendations/', AdminRecommendationAuditView.as_view(), name='admin-rec-audit'),
    path('settings/', AdminSettingsView.as_view(), name='admin-settings'),
    path('engine/retrain/', RetrainView.as_view(), name='admin-retrain'),
    path('students/', AdminStudentsView.as_view(), name='admin-students'),
    path('students/<int:student_id>/', AdminStudentDetailView.as_view(), name='admin-student-detail'),
    path('students/<int:student_id>/interactions/', AdminStudentInteractionsView.as_view(), name='admin-student-interactions'),
    path('students/<int:student_id>/enrollments/', AdminStudentEnrollmentsView.as_view(), name='admin-student-enrollments'),
]
