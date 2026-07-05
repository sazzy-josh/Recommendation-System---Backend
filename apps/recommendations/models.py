from django.db import models
from apps.users.models import User
from apps.courses.models import Course


class RecommendationResult(models.Model):
    class RecommendationType(models.TextChoices):
        CF = 'CF', 'Collaborative Filtering'
        CBF = 'CBF', 'Content-Based Filtering'
        HYBRID = 'HYBRID', 'Hybrid'

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='recommendations')
    score = models.FloatField()
    rank = models.PositiveIntegerField()
    recommendation_type = models.CharField(max_length=10, choices=RecommendationType.choices)
    w_weight = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommendation_results'
        ordering = ['rank']

    def __str__(self):
        return f"Rec#{self.rank} for {self.student.email}: {self.course.code}"


class Feedback(models.Model):
    class Rating(models.IntegerChoices):
        POSITIVE = 1, 'Helpful'
        NEGATIVE = -1, 'Not helpful'

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    recommendation = models.ForeignKey(RecommendationResult, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.SmallIntegerField(choices=Rating.choices)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feedbacks'
        unique_together = ('student', 'recommendation')


class EngineSettings(models.Model):
    hybrid_weight = models.FloatField(default=0.6)
    top_n = models.PositiveIntegerField(default=5)
    cold_start_threshold = models.PositiveIntegerField(default=3)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'engine_settings'

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj
