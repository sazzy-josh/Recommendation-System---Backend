from rest_framework import serializers
from .models import Department, Course


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name', 'code')


class CourseSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source='department', write_only=True
    )
    prerequisite_ids = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), many=True, source='prerequisites', required=False
    )

    class Meta:
        model = Course
        fields = (
            'id', 'code', 'title', 'description', 'credits', 'level',
            'department', 'department_id', 'tags', 'prerequisite_ids',
            'is_active', 'created_at',
        )
        read_only_fields = ('id', 'created_at')


class CourseDetailSerializer(CourseSerializer):
    syllabus_text_excerpt = serializers.SerializerMethodField()

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ('syllabus_text_excerpt',)

    def get_syllabus_text_excerpt(self, obj):
        return obj.syllabus_text[:300] if obj.syllabus_text else ''


class CourseStatsSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    enrollment_count = serializers.IntegerField()
    recommendation_count = serializers.IntegerField()
