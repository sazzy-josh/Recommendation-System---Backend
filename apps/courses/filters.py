import django_filters
from .models import Course


class CourseFilter(django_filters.FilterSet):
    department = django_filters.NumberFilter(field_name='department__id')
    level = django_filters.CharFilter(field_name='level', lookup_expr='iexact')
    credits = django_filters.NumberFilter(field_name='credits')
    credits_min = django_filters.NumberFilter(field_name='credits', lookup_expr='gte')
    credits_max = django_filters.NumberFilter(field_name='credits', lookup_expr='lte')

    class Meta:
        model = Course
        fields = ['department', 'level', 'credits']
