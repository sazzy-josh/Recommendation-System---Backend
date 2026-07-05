from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.utils import timezone

from .models import RecommendationResult, Feedback, EngineSettings
from .serializers import RecommendationResultSerializer, FeedbackSerializer, EngineSettingsSerializer
from apps.interactions.models import Interaction


class RecommendationsView(APIView):
    def get(self, request):
        results = RecommendationResult.objects.filter(
            student=request.user
        ).select_related('course', 'course__department').prefetch_related('feedbacks')

        settings = EngineSettings.get_settings()
        interaction_count = Interaction.objects.filter(student=request.user).count()
        is_cold_start = interaction_count < settings.cold_start_threshold

        latest = results.first()
        generated_at = latest.created_at.isoformat() if latest else timezone.now().isoformat()
        w_weight = latest.w_weight if latest else settings.hybrid_weight

        return Response({
            'student_id': request.user.id,
            'is_cold_start': is_cold_start,
            'w_weight': w_weight,
            'generated_at': generated_at,
            'recommendations': RecommendationResultSerializer(results, many=True).data,
        })


class RefreshRecommendationsView(APIView):
    def post(self, request):
        from tasks.recommendation import generate_recommendations_for_student
        task = generate_recommendations_for_student.delay(request.user.id)
        return Response({'task_id': task.id, 'status': 'queued'}, status=status.HTTP_202_ACCEPTED)


class FeedbackView(APIView):
    def post(self, request, pk):
        try:
            rec = RecommendationResult.objects.get(pk=pk, student=request.user)
        except RecommendationResult.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feedback, _ = Feedback.objects.update_or_create(
            student=request.user,
            recommendation=rec,
            defaults={
                'rating': serializer.validated_data['rating'],
                'comment': serializer.validated_data.get('comment', ''),
            }
        )
        return Response(FeedbackSerializer(feedback).data, status=status.HTTP_201_CREATED)


class RecommendationHistoryView(APIView):
    def get(self, request):
        results = RecommendationResult.objects.filter(
            student=request.user
        ).select_related('course').prefetch_related('feedbacks').order_by('-created_at')[:50]
        return Response(RecommendationResultSerializer(results, many=True).data)
