from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_recommendation_email(user_id: int):
    from apps.users.models import User
    try:
        user = User.objects.get(id=user_id)
        send_mail(
            subject='Your new course recommendations are ready',
            message='Log in to ESCRS to view your personalized course recommendations.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except User.DoesNotExist:
        pass
