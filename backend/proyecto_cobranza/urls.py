from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from apps.core.views import api_root

urlpatterns = [
    path('', api_root, name='api-root'),
    path('api/', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/clients/', include('apps.clients.urls')),
    path('api/calls/', include('apps.calls.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
