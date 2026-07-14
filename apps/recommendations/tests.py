from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status

from apps.users.models import User, StudentProfile
from apps.courses.models import Department, Course
from apps.interactions.models import Interaction
from .models import RecommendationResult, EngineSettings
from engine.hybrid import blend_scores
from tasks.recommendation import generate_recommendations_for_student


def make_student(email='student@example.com', interests=None, completed=None):
    user = User.objects.create_user(email=email, password='testpass123', full_name='Test Student')
    StudentProfile.objects.filter(user=user).delete()
    profile = StudentProfile.objects.create(
        user=user,
        program='MIT',
        level='postgraduate',
        interests=interests or ['machine learning'],
        completed_course_ids=completed or [],
        onboarding_complete=False,  # keep the post_save signal quiet during setup
    )
    return user, profile


def make_courses():
    dept = Department.objects.create(name='Information Technology', code='IT')
    ml = Course.objects.create(
        code='IT801', title='Advanced Machine Learning',
        description='deep learning neural networks machine learning',
        credits=3, department=dept, level='postgraduate',
        tags=['machine learning', 'neural networks'],
    )
    db = Course.objects.create(
        code='IT802', title='Database Systems',
        description='relational databases sql query optimisation',
        credits=3, department=dept, level='postgraduate',
        tags=['databases'],
    )
    acc = Course.objects.create(
        code='BUS101', title='Accounting Basics',
        description='accounting finance bookkeeping business',
        credits=2, department=dept, level='undergraduate',
        tags=['finance'],
    )
    return ml, db, acc


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class RecommendationEngineTaskTests(TestCase):
    def test_cold_start_uses_cbf_only(self):
        user, _ = make_student()
        make_courses()
        # No interactions at all → below cold-start threshold (default 3)
        generate_recommendations_for_student.apply(args=[user.id])

        results = RecommendationResult.objects.filter(student=user)
        self.assertTrue(results.exists())
        for rec in results:
            self.assertEqual(rec.w_weight, 0.0)
            self.assertEqual(rec.recommendation_type, 'CBF')

    def test_recommendations_exclude_completed_courses(self):
        ml, db, acc = make_courses()
        user, profile = make_student(completed=[ml.id])
        generate_recommendations_for_student.apply(args=[user.id])

        recommended_ids = set(
            RecommendationResult.objects.filter(student=user).values_list('course_id', flat=True)
        )
        self.assertNotIn(ml.id, recommended_ids)

    def test_hybrid_blend_respects_weight(self):
        cf = [{'course_id': 1, 'cf_score': 1.0}, {'course_id': 2, 'cf_score': 0.0}]
        cbf = [{'course_id': 1, 'cbf_score': 0.0}, {'course_id': 2, 'cbf_score': 1.0}]
        # w=1.0 → pure CF: course 1 must rank first
        results = blend_scores(cf, cbf, w=1.0, top_n=2)
        self.assertEqual(results[0]['course_id'], 1)
        # w=0.0 → pure CBF: course 2 must rank first
        results = blend_scores(cf, cbf, w=0.0, top_n=2)
        self.assertEqual(results[0]['course_id'], 2)
        # Formula: S = w*cf + (1-w)*cbf
        results = blend_scores(cf, cbf, w=0.6, top_n=2)
        by_id = {r['course_id']: r for r in results}
        self.assertAlmostEqual(by_id[1]['hybrid_score'], 0.6)
        self.assertAlmostEqual(by_id[2]['hybrid_score'], 0.4)


class RecommendationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user, self.profile = make_student()
        self.client.force_authenticate(user=self.user)

    def test_refresh_endpoint_triggers_celery_task(self):
        with patch('tasks.recommendation.generate_recommendations_for_student.delay') as mock_delay:
            mock_delay.return_value.id = 'fake-task-id'
            response = self.client.post('/api/v1/recommendations/refresh/')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        mock_delay.assert_called_once_with(self.user.id)

    def test_get_recommendations_shape(self):
        ml, _, _ = make_courses()
        RecommendationResult.objects.create(
            student=self.user, course=ml, score=0.9, rank=1,
            recommendation_type='CBF', w_weight=0.0,
        )
        response = self.client.get('/api/v1/recommendations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in ('student_id', 'is_cold_start', 'w_weight', 'generated_at', 'recommendations'):
            self.assertIn(key, response.data)
        self.assertEqual(len(response.data['recommendations']), 1)
