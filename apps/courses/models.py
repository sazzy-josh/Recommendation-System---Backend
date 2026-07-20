from django.db import models
import numpy as np


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'departments'

    def __str__(self):
        return self.name


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    credits = models.PositiveIntegerField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='courses')
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='prerequisite_for')
    level = models.CharField(max_length=50)
    syllabus_text = models.TextField(blank=True)
    syllabus_vector = models.JSONField(default=list)
    syllabus_file = models.FileField(upload_to='syllabi/', null=True, blank=True)
    tags = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'

    def __str__(self):
        return f"{self.code} — {self.title}"

    def get_vector(self):
        return np.array(self.syllabus_vector) if self.syllabus_vector else np.array([])


class CourseModule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'course_modules'
        ordering = ['order']

    def __str__(self):
        return f"{self.course.code} › {self.title}"


class CourseActivity(models.Model):
    class ActivityType(models.TextChoices):
        QUIZ = 'quiz', 'Quiz'
        PAGE = 'page', 'Page'
        ASSIGNMENT = 'assignment', 'Assignment'
        URL = 'url', 'URL'

    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='activities')
    title = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    content = models.TextField(blank=True)
    url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'course_activities'
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} › {self.title}"
