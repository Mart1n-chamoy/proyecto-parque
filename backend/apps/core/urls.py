from rest_framework.routers import DefaultRouter
from apps.clients.views import ClientViewSet
from apps.calls.views import CallBatchViewSet, CallViewSet

# Crear el router predeterminado
router = DefaultRouter()

# Registrar los ViewSets
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'call-batches', CallBatchViewSet, basename='call-batch')
router.register(r'calls', CallViewSet, basename='call')

# Las URLs se incluyen en proyecto_cobranza/urls.py
urlpatterns = router.urls
