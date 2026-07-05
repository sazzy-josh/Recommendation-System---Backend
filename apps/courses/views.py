from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Course, Department
from .serializers import CourseSerializer, CourseDetailSerializer, DepartmentSerializer
from .filters import CourseFilter
from apps.recommendations.permissions import IsAdminUser


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.filter(is_active=True).select_related('department')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CourseFilter
    search_fields = ['title', 'code', 'description', 'tags']
    ordering_fields = ['title', 'credits', 'created_at']

    def get_serializer_class(self):
        return CourseSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.select_related('department').prefetch_related('prerequisites')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CourseDetailSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])


class SyllabusUploadView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        file = request.FILES.get('syllabus')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        course.syllabus_file = file
        course.save(update_fields=['syllabus_file'])

        # Extract text and update
        try:
            import pdfplumber
            with pdfplumber.open(file) as pdf:
                text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
            course.syllabus_text = text
            course.save(update_fields=['syllabus_text'])
        except Exception:
            pass

        return Response({'status': 'uploaded', 'course_id': course.id})


class CourseStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'course_id': course.id,
            'enrollment_count': course.enrollments.count(),
            'recommendation_count': course.recommendations.count(),
        })


class DepartmentListView(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
