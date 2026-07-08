from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.calls.webhook_views import ElevenLabsWebhookView

urlpatterns = [
    # Dashboard web — va primero para que '/' muestre el panel
    path('', include('apps.dashboard.urls')),

    # API REST
    path('api/auth/', include('apps.auth_app.urls')),
    path('api/clients/', include('apps.clients.urls')),
    path('api/calls/', include('apps.calls.urls')),

    # Admin y webhooks
    path('admin/', admin.site.urls),
    path('webhooks/elevenlabs/', ElevenLabsWebhookView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
