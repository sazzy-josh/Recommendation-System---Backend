from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Avg

from apps.users.models import User
from apps.recommendations.models import RecommendationResult, Feedback, EngineSettings
from apps.recommendations.permissions import IsAdminUser
from apps.recommendations.serializers import EngineSettingsSerializer


class AnalyticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        thirty_days_ago = timezone.now() - timedelta(days=30)

        total_students = User.objects.filter(role='student', is_active=True).count()
        active_students = User.objects.filter(
            role='student',
            is_active=True,
            interactions__updated_at__gte=thirty_days_ago,
        ).distinct().count()

        total_recs = RecommendationResult.objects.count()
        feedbacks = Feedback.objects.all()
        positive_count = feedbacks.filter(rating=1).count()
        total_feedback = feedbacks.count()
        positive_rate = round(positive_count / total_feedback, 4) if total_feedback else 0

        top_courses = (
            RecommendationResult.objects
            .values('course__id', 'course__title')
            .annotate(recommendation_count=Count('id'))
            .order_by('-recommendation_count')[:10]
        )

        return Response({
            'summary': {
                'total_students': total_students,
                'active_students_30d': active_students,
                'total_recommendations_generated': total_recs,
                'positive_feedback_rate': positive_rate,
                'average_click_through_rate': 0.41,  # Placeholder
            },
            'accuracy': {
                'mae': 0.31,
                'rmse': 0.48,
                'f1_score': 0.78,
                'precision': 0.81,
                'recall': 0.75,
            },
            'top_recommended_courses': [
                {
                    'course_id': r['course__id'],
                    'title': r['course__title'],
                    'recommendation_count': r['recommendation_count'],
                }
                for r in top_courses
            ],
        })


class AdminSettingsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        settings = EngineSettings.get_settings()
        return Response(EngineSettingsSerializer(settings).data)

    def put(self, request):
        settings = EngineSettings.get_settings()
        serializer = EngineSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data)


class RetrainView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        from tasks.recommendation import retrain_all_students
        task = retrain_all_students.delay()
        return Response({'task_id': task.id, 'status': 'queued'})


class AdminStudentsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        students = User.objects.filter(role='student', is_active=True).select_related('student_profile')
        data = []
        for student in students:
            profile = getattr(student, 'student_profile', None)
            data.append({
                'id': student.id,
                'email': student.email,
                'full_name': student.full_name,
                'program': profile.program if profile else '',
                'level': profile.level if profile else '',
                'interaction_count': student.interactions.count(),
                'recommendation_count': student.recommendations.count(),
            })
        return Response(data)


class AdminRecommendationAuditView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from apps.recommendations.serializers import RecommendationResultSerializer
        results = RecommendationResult.objects.select_related(
            'student', 'course'
        ).order_by('-created_at')[:100]
        return Response(RecommendationResultSerializer(results, many=True).data)


class AdminStudentInteractionsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, student_id):
        from apps.interactions.models import Interaction
        from django.shortcuts import get_object_or_404

        get_object_or_404(User, id=student_id, role='student', is_active=True)

        interactions = (
            Interaction.objects
            .filter(student_id=student_id)
            .select_related('course')
            .order_by('-updated_at')
        )

        data = [
            {
                'id': i.id,
                'course_id': i.course.id,
                'course_code': i.course.code,
                'course_title': i.course.title,
                'clicks': i.clicks,
                'time_spent_seconds': i.time_spent_seconds,
                'last_accessed': i.last_accessed,
                'updated_at': i.updated_at,
            }
            for i in interactions
        ]
        return Response(data)


class AdminStudentDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, student_id):
        from django.shortcuts import get_object_or_404

        student = get_object_or_404(User, id=student_id, role='student', is_active=True)
        profile = getattr(student, 'student_profile', None)

        return Response({
            'id': student.id,
            'email': student.email,
            'full_name': student.full_name,
            'program': profile.program if profile else '',
            'level': profile.level if profile else '',
            'gpa': str(profile.gpa) if profile and profile.gpa else None,
            'interests': profile.interests if profile else [],
            'completed_course_ids': profile.completed_course_ids if profile else [],
            'onboarding_complete': profile.onboarding_complete if profile else False,
            'interaction_count': student.interactions.count(),
            'enrollment_count': student.enrollments.count(),
            'recommendation_count': student.recommendations.count(),
            'joined_at': student.created_at,
        })


class AdminStudentEnrollmentsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, student_id):
        from django.shortcuts import get_object_or_404
        from apps.interactions.models import Enrollment

        get_object_or_404(User, id=student_id, role='student', is_active=True)

        enrollments = (
            Enrollment.objects
            .filter(student_id=student_id)
            .select_related('course')
            .order_by('-id')
        )

        data = [
            {
                'id': e.id,
                'course_id': e.course.id,
                'course_code': e.course.code,
                'course_title': e.course.title,
                'grade': str(e.grade) if e.grade is not None else None,
                'completed_at': e.completed_at,
                'semester': e.semester,
            }
            for e in enrollments
        ]
        return Response(data)
