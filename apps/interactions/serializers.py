from rest_framework import serializers
from .models import Enrollment, Interaction
from apps.courses.serializers import CourseSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    course_detail = CourseSerializer(source='course', read_only=True)

    class Meta:
        model = Enrollment
        fields = ('id', 'course', 'course_detail', 'grade', 'completed_at', 'semester')
        read_only_fields = ('id',)


class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = ('id', 'course', 'clicks', 'time_spent_seconds', 'last_accessed', 'updated_at')
        read_only_fields = ('id', 'updated_at')
