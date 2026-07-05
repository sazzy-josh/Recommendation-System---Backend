from django.contrib import admin
from .models import RecommendationResult, Feedback, EngineSettings


@admin.register(RecommendationResult)
class RecommendationResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'rank', 'score', 'recommendation_type', 'created_at')
    list_filter = ('recommendation_type',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'recommendation', 'rating', 'created_at')
    list_filter = ('rating',)


@admin.register(EngineSettings)
class EngineSettingsAdmin(admin.ModelAdmin):
    list_display = ('hybrid_weight', 'top_n', 'cold_start_threshold', 'updated_at')
