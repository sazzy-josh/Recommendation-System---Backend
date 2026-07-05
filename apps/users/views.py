from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .models import StudentProfile
from .serializers import (
    RegisterSerializer, UserSerializer,
    CustomTokenObtainPairSerializer, StudentProfileSerializer,
)
from apps.interactions.models import Enrollment, Interaction
from apps.interactions.serializers import EnrollmentSerializer, InteractionSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Placeholder — sends email with reset token in production
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentMeView(generics.RetrieveUpdateAPIView):
    serializer_class = StudentProfileSerializer

    def get_object(self):
        profile, _ = StudentProfile.objects.get_or_create(
            user=self.request.user,
            defaults={'program': '', 'level': 'undergraduate'},
        )
        return profile

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Mark onboarding complete if interests and program are set
        if instance.interests and instance.program:
            instance.onboarding_complete = True
            instance.save(update_fields=['onboarding_complete'])

        # Trigger recommendation refresh
        from tasks.recommendation import generate_recommendations_for_student
        generate_recommendations_for_student.delay(request.user.id)

        return Response(serializer.data)


class StudentEnrollmentsView(APIView):
    def get(self, request):
        enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
        return Response(EnrollmentSerializer(enrollments, many=True).data)

    def post(self, request):
        data = request.data.copy()
        data['student'] = request.user.id
        serializer = EnrollmentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(student=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StudentEnrollmentDeleteView(APIView):
    def delete(self, request, course_id):
        Enrollment.objects.filter(student=request.user, course_id=course_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentInteractionsView(APIView):
    def get(self, request):
        interactions = Interaction.objects.filter(student=request.user).select_related('course')
        return Response(InteractionSerializer(interactions, many=True).data)

    def post(self, request):
        course_id = request.data.get('course_id')
        clicks = request.data.get('clicks', 0)
        time_spent = request.data.get('time_spent_seconds', 0)

        interaction, _ = Interaction.objects.get_or_create(
            student=request.user,
            course_id=course_id,
            defaults={'clicks': 0, 'time_spent_seconds': 0},
        )
        interaction.clicks += int(clicks)
        interaction.time_spent_seconds += int(time_spent)
        from django.utils import timezone
        interaction.last_accessed = timezone.now()
        interaction.save()
        return Response(InteractionSerializer(interaction).data)
