from rest_framework import serializers
from .models import Department, Course, CourseModule, CourseActivity


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


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseActivity
        fields = ('id', 'title', 'activity_type', 'content', 'url', 'order', 'duration_minutes')


class ModuleSerializer(serializers.ModelSerializer):
    activities = ActivitySerializer(many=True, read_only=True)
    activity_count = serializers.SerializerMethodField()

    class Meta:
        model = CourseModule
        fields = ('id', 'title', 'description', 'order', 'activities', 'activity_count')

    def get_activity_count(self, obj):
        return obj.activities.count()


class CourseDetailSerializer(CourseSerializer):
    syllabus_text_excerpt = serializers.SerializerMethodField()
    modules = ModuleSerializer(many=True, read_only=True)
    prerequisites = serializers.SerializerMethodField()

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ('syllabus_text_excerpt', 'modules', 'prerequisites')

    def get_syllabus_text_excerpt(self, obj):
        return obj.syllabus_text[:300] if obj.syllabus_text else ''

    def get_prerequisites(self, obj):
        return [{'id': p.id, 'code': p.code, 'title': p.title} for p in obj.prerequisites.all()]


class CourseStatsSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    enrollment_count = serializers.IntegerField()
    recommendation_count = serializers.IntegerField()
