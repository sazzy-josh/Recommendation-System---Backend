from django.urls import path
from .views import CourseListCreateView, CourseDetailView, SyllabusUploadView, CourseStatsView, DepartmentListView

urlpatterns = [
    path('', CourseListCreateView.as_view(), name='course-list'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('<int:pk>/syllabus/', SyllabusUploadView.as_view(), name='course-syllabus'),
    path('<int:pk>/stats/', CourseStatsView.as_view(), name='course-stats'),
    path('departments/', DepartmentListView.as_view(), name='department-list'),
]
