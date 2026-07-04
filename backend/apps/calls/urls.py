from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views
from .views_batch import BatchStartView, BatchStatusView, BatchResultsView, ManualFetchResultView

app_name = 'calls'

router = DefaultRouter()
router.register(r'batches', views.CallBatchViewSet, basename='call-batch')
router.register(r'', views.CallViewSet, basename='call')

urlpatterns = router.urls + [
    # Acciones de lotes — ElevenLabs
    path('batches/<int:pk>/start/',    BatchStartView.as_view(),   name='batch-start'),
    path('batches/<int:pk>/status/',   BatchStatusView.as_view(),  name='batch-status'),
    path('batches/<int:pk>/results/',  BatchResultsView.as_view(), name='batch-results'),

    # Acciones de llamadas individuales
    path('<int:pk>/fetch-results/',    ManualFetchResultView.as_view(), name='call-fetch-results'),
]
