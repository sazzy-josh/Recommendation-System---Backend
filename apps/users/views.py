from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

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


PASSWORD_RESET_SALT = 'escrs-password-reset'
PASSWORD_RESET_MAX_AGE = 3600  # 1 hour


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        if email:
            try:
                user = User.objects.get(email=email, is_active=True)
                token = signing.dumps({'uid': user.pk}, salt=PASSWORD_RESET_SALT)
                send_mail(
                    subject='ESCRS password reset',
                    message=(
                        'Use this token to reset your password (valid for 1 hour):\n\n'
                        f'{token}'
                    ),
                    from_email=None,  # DEFAULT_FROM_EMAIL
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except User.DoesNotExist:
                pass  # Always return 204 to avoid leaking which emails exist
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('token', '')
        password = request.data.get('password', '')
        if not token or not password:
            return Response(
                {'error': 'token and password are required', 'code': 'invalid_request'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            payload = signing.loads(token, salt=PASSWORD_RESET_SALT, max_age=PASSWORD_RESET_MAX_AGE)
            user = User.objects.get(pk=payload['uid'], is_active=True)
        except (signing.BadSignature, User.DoesNotExist, KeyError):
            return Response(
                {'error': 'Invalid or expired reset token', 'code': 'invalid_token'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(password, user=user)
        except ValidationError as exc:
            return Response(
                {'error': 'Invalid password', 'detail': exc.messages, 'code': 'invalid_password'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(password)
        user.save(update_fields=['password'])
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

        # Mark onboarding complete if interests and program are set.
        # The StudentProfile post_save signal queues the recommendation refresh.
        if instance.interests and instance.program:
            instance.onboarding_complete = True
            instance.save(update_fields=['onboarding_complete'])

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
