from rest_framework import serializers
from .models import RecommendationResult, Feedback, EngineSettings
from apps.courses.models import Course


class RecommendedCourseSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='department.name', default='')

    class Meta:
        model = Course
        fields = ('id', 'code', 'title', 'credits', 'tags', 'department')


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('id', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'created_at')


class RecommendationResultSerializer(serializers.ModelSerializer):
    course = RecommendedCourseSerializer()
    feedback = serializers.SerializerMethodField()
    rationale = serializers.SerializerMethodField()

    class Meta:
        model = RecommendationResult
        fields = ('id', 'rank', 'score', 'recommendation_type', 'rationale', 'course', 'feedback', 'created_at')

    def get_feedback(self, obj):
        fb = obj.feedbacks.first()
        return FeedbackSerializer(fb).data if fb else None

    def get_rationale(self, obj):
        from engine.hybrid import generate_rationale
        return generate_rationale({'recommendation_type': obj.recommendation_type})


class EngineSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EngineSettings
        fields = ('hybrid_weight', 'top_n', 'cold_start_threshold', 'updated_at')
        read_only_fields = ('updated_at',)
