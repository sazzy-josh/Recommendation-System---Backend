from django.urls import path
from .views import RecommendationsView, RefreshRecommendationsView, FeedbackView, RecommendationHistoryView

urlpatterns = [
    path('', RecommendationsView.as_view(), name='recommendations'),
    path('refresh/', RefreshRecommendationsView.as_view(), name='recommendations-refresh'),
    path('<int:pk>/feedback/', FeedbackView.as_view(), name='recommendation-feedback'),
    path('history/', RecommendationHistoryView.as_view(), name='recommendations-history'),
]
