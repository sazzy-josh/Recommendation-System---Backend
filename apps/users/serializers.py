from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, StudentProfile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('email', 'password', 'full_name')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        StudentProfile.objects.create(user=user, program='', level='undergraduate')
        return user


class UserSerializer(serializers.ModelSerializer):
    onboarding_complete = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'role', 'onboarding_complete')

    def get_onboarding_complete(self, obj):
        if hasattr(obj, 'student_profile'):
            return obj.student_profile.onboarding_complete
        return False


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['user'] = {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'onboarding_complete': (
                hasattr(user, 'student_profile') and user.student_profile.onboarding_complete
            ),
        }
        return data


class StudentProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    interaction_count = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = (
            'id', 'email', 'full_name', 'role',
            'program', 'level', 'interests', 'gpa',
            'completed_course_ids', 'onboarding_complete', 'interaction_count',
        )
        read_only_fields = ('id', 'email', 'full_name', 'role', 'onboarding_complete', 'interaction_count')

    def get_interaction_count(self, obj):
        return obj.user.interactions.count()
