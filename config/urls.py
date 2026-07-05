from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('auth/', include('apps.users.urls')),
        path('students/', include('apps.users.student_urls')),
        path('courses/', include('apps.courses.urls')),
        path('recommendations/', include('apps.recommendations.urls')),
        path('admin/', include('apps.analytics.urls')),
        # OpenAPI
        path('schema/', SpectacularAPIView.as_view(), name='schema'),
        path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    ])),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
