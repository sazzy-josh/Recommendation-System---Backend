"""
Celery tasks for generating and refreshing recommendations.
"""

from __future__ import annotations

import logging
from celery import shared_task

logger = logging.getLogger(__name__)


def run_recommendations_sync(student_id: int) -> dict:
    """
    Core recommendation logic — runs synchronously without Celery.
    Called directly by the view when no broker is available, and by
    the Celery task when a worker is running.
    """
    from apps.users.models import User
    from apps.courses.models import Course
    from apps.interactions.models import Interaction, Enrollment
    from apps.recommendations.models import RecommendationResult, EngineSettings
    from engine.content_based import compute_cbf_scores
    from engine.collaborative import get_cf_scores_for_student
    from engine.hybrid import blend_scores

    settings = EngineSettings.get_settings()
    top_n = settings.top_n
    cold_start_threshold = settings.cold_start_threshold
    base_w = settings.hybrid_weight

    try:
        user = User.objects.select_related('student_profile').get(id=student_id)
    except User.DoesNotExist:
        logger.warning(f"Student {student_id} not found; skipping.")
        return {'error': 'student_not_found'}

    profile = getattr(user, 'student_profile', None)
    interests = profile.interests if profile else []
    completed_ids = set(profile.completed_course_ids if profile else [])

    enrolled_ids = set(
        Enrollment.objects.filter(student=user).values_list('course_id', flat=True)
    )
    exclude_ids = completed_ids | enrolled_ids

    interaction_count = Interaction.objects.filter(student=user).count()
    is_cold_start = interaction_count < cold_start_threshold
    w = 0.0 if is_cold_start else base_w

    active_courses = Course.objects.filter(is_active=True).select_related('department')
    course_dicts = []
    completed_texts = []
    for c in active_courses:
        tags_str = ' '.join(c.tags) if isinstance(c.tags, list) else ''
        combined = f"{c.title} {c.description} {c.syllabus_text} {tags_str}".strip()
        course_dicts.append({'id': c.id, 'combined_text': combined})
        if c.id in completed_ids:
            completed_texts.append(combined)

    cbf_scores = compute_cbf_scores(interests, course_dicts, completed_texts)
    cbf_scores = [s for s in cbf_scores if s['course_id'] not in exclude_ids]

    all_interactions = list(
        Interaction.objects.all().values('student_id', 'course_id', 'clicks', 'time_spent_seconds')
    )
    cf_scores = get_cf_scores_for_student(
        target_student_id=student_id,
        interactions=all_interactions,
        exclude_course_ids=list(exclude_ids),
    )

    blended = blend_scores(cf_scores, cbf_scores, w=w, top_n=top_n)

    if not blended:
        logger.info(f"No recommendations generated for student {student_id}.")
        return {'student_id': student_id, 'count': 0, 'w_weight': w, 'is_cold_start': is_cold_start}

    RecommendationResult.objects.filter(student=user).delete()
    new_results = [
        RecommendationResult(
            student=user,
            course_id=item['course_id'],
            score=item['hybrid_score'],
            rank=rank,
            recommendation_type=item['recommendation_type'],
            w_weight=w,
        )
        for rank, item in enumerate(blended, start=1)
    ]
    RecommendationResult.objects.bulk_create(new_results)

    logger.info(
        f"Generated {len(new_results)} recommendations for student {student_id} "
        f"(w={w}, cold_start={is_cold_start})."
    )
    return {'student_id': student_id, 'count': len(new_results), 'w_weight': w, 'is_cold_start': is_cold_start}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_recommendations_for_student(self, student_id: int) -> dict:
    try:
        return run_recommendations_sync(student_id)
    except Exception as exc:
        logger.error(f"Error generating recommendations for student {student_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@shared_task
def retrain_all_students() -> dict:
    """
    Fan-out recommendation generation for every active student.

    Dispatches one `generate_recommendations_for_student` task per student
    so they run in parallel across Celery workers.

    Returns a summary dict with the number of tasks queued.
    """
    from apps.users.models import User

    student_ids = list(
        User.objects.filter(role='student', is_active=True).values_list('id', flat=True)
    )

    for sid in student_ids:
        generate_recommendations_for_student.delay(sid)

    logger.info(f"Queued recommendation refresh for {len(student_ids)} students.")
    return {'queued': len(student_ids)}
