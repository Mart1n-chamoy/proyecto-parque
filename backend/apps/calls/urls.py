from rest_framework.routers import DefaultRouter
from . import views

app_name = 'calls'

router = DefaultRouter()
router.register(r'batches', views.CallBatchViewSet, basename='call-batch')
router.register(r'', views.CallViewSet, basename='call')

urlpatterns = router.urls
