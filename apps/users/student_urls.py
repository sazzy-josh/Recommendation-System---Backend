from django.urls import path
from .views import (
    StudentMeView, StudentEnrollmentsView,
    StudentEnrollmentDeleteView, StudentInteractionsView,
)

urlpatterns = [
    path('me/', StudentMeView.as_view(), name='student-me'),
    path('me/enrollments/', StudentEnrollmentsView.as_view(), name='student-enrollments'),
    path('me/enrollments/<int:course_id>/', StudentEnrollmentDeleteView.as_view(), name='student-enrollment-delete'),
    path('me/interactions/', StudentInteractionsView.as_view(), name='student-interactions'),
]
