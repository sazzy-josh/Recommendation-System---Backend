from django.db import models
from apps.users.models import User
from apps.courses.models import Course


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    completed_at = models.DateField(null=True, blank=True)
    semester = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'enrollments'
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.email} → {self.course.code}"


class Interaction(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='interactions')
    clicks = models.PositiveIntegerField(default=0)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interactions'
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.email} ↔ {self.course.code}"
