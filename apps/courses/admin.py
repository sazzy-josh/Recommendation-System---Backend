from django.contrib import admin
from .models import Department, Course


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'department', 'credits', 'level', 'is_active')
    list_filter = ('is_active', 'level', 'department')
    search_fields = ('code', 'title', 'description')
    filter_horizontal = ('prerequisites',)
