from django.test import TestCase
from .content_based import compute_cbf_scores
from .hybrid import normalize_scores, blend_scores
from .utils import compute_implicit_score


class CBFTests(TestCase):
    def test_cbf_scores_ranked_correctly(self):
        courses = [
            {'id': 1, 'combined_text': 'machine learning neural networks deep learning'},
            {'id': 2, 'combined_text': 'accounting finance business management'},
            {'id': 3, 'combined_text': 'machine learning python data science'},
        ]
        scores = compute_cbf_scores(['machine learning', 'deep learning'], courses, [])
        self.assertEqual(scores[0]['course_id'], 1)

    def test_normalize_scores_range(self):
        scores = [{'course_id': i, 'cf_score': float(i)} for i in range(1, 6)]
        normalized = normalize_scores(scores, 'cf_score')
        norms = [s['cf_score_norm'] for s in normalized]
        self.assertAlmostEqual(min(norms), 0.0)
        self.assertAlmostEqual(max(norms), 1.0)

    def test_blend_scores_formula(self):
        cf = [{'course_id': 1, 'cf_score': 1.0}, {'course_id': 2, 'cf_score': 0.5}]
        cbf = [{'course_id': 1, 'cbf_score': 0.8}, {'course_id': 2, 'cbf_score': 0.9}]
        results = blend_scores(cf, cbf, w=0.5, top_n=2)
        self.assertEqual(len(results), 2)
        self.assertGreaterEqual(results[0]['hybrid_score'], results[1]['hybrid_score'])

    def test_cold_start_w_equals_zero(self):
        cf = [{'course_id': 1, 'cf_score': 0.9}]
        cbf = [{'course_id': 1, 'cbf_score': 0.5}]
        results = blend_scores(cf, cbf, w=0.0, top_n=1)
        self.assertEqual(results[0]['recommendation_type'], 'CBF')

    def test_implicit_score_normalized(self):
        score = compute_implicit_score(clicks=50, time_spent_seconds=1800)
        self.assertAlmostEqual(score, 1.0)
        score_zero = compute_implicit_score(0, 0)
        self.assertAlmostEqual(score_zero, 0.0)
