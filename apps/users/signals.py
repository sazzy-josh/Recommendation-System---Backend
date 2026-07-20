"""
Signal handlers for the users app.

Per the build spec (section 8), recommendation generation is triggered by a
post_save signal on StudentProfile — covering both first onboarding completion
and any subsequent profile/interest update.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import StudentProfile

logger = logging.getLogger(__name__)


@receiver(post_save, sender=StudentProfile)
def trigger_recommendations_on_profile_save(sender, instance, **kwargs):
    if not instance.onboarding_complete:
        return

    from tasks.recommendation import generate_recommendations_for_student

    try:
        generate_recommendations_for_student.delay(instance.user_id)
    except Exception as exc:  # broker unavailable — don't block the request
        logger.warning(
            f"Could not queue recommendation refresh for user {instance.user_id}: {exc}"
        )
