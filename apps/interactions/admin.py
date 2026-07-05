from django.contrib import admin
from .models import Enrollment, Interaction


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'grade', 'completed_at', 'semester')
    list_filter = ('semester',)
    search_fields = ('student__email', 'course__code')


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'clicks', 'time_spent_seconds', 'last_accessed')
    search_fields = ('student__email', 'course__code')
