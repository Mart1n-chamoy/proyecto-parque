from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import CallBatch, Call
from .serializers import CallBatchSerializer, CallSerializer


class CallBatchViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Lotes de Llamadas (CallBatch).
    
    Operaciones CRUD:
    - GET /call-batches/ - Lista todos los lotes
    - POST /call-batches/ - Crear un nuevo lote
    - GET /call-batches/{id}/ - Obtener detalles de un lote
    - PUT /call-batches/{id}/ - Actualizar un lote
    - PATCH /call-batches/{id}/ - Actualizar parcialmente
    - DELETE /call-batches/{id}/ - Eliminar un lote
    """
    queryset = CallBatch.objects.all()
    serializer_class = CallBatchSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'total_clients']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Obtener lotes pendientes"""
        pending_batches = CallBatch.objects.filter(status='pending')
        serializer = self.get_serializer(pending_batches, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def processing(self, request):
        """Obtener lotes en procesamiento"""
        processing_batches = CallBatch.objects.filter(status='processing')
        serializer = self.get_serializer(processing_batches, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Iniciar el procesamiento de un lote"""
        from django.utils import timezone
        batch = self.get_object()
        if batch.status != 'pending':
            return Response(
                {'error': 'Solo se pueden iniciar lotes en estado pendiente'},
                status=status.HTTP_400_BAD_REQUEST
            )
        batch.status = 'processing'
        batch.started_at = timezone.now()
        batch.save()
        serializer = self.get_serializer(batch)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Marcar un lote como completado"""
        from django.utils import timezone
        batch = self.get_object()
        batch.status = 'completed'
        batch.completed_at = timezone.now()
        batch.save()
        serializer = self.get_serializer(batch)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CallViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Llamadas (Call).
    
    Operaciones CRUD:
    - GET /calls/ - Lista todas las llamadas
    - POST /calls/ - Crear una llamada
    - GET /calls/{id}/ - Obtener detalles de una llamada
    - PUT /calls/{id}/ - Actualizar una llamada
    - PATCH /calls/{id}/ - Actualizar parcialmente
    - DELETE /calls/{id}/ - Eliminar una llamada
    """
    queryset = Call.objects.all()
    serializer_class = CallSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'batch', 'client']
    search_fields = ['client__phone', 'transcript', 'batch__name']
    ordering_fields = ['created_at', 'duration']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Obtener llamadas pendientes"""
        pending_calls = Call.objects.filter(status='pending')
        serializer = self.get_serializer(pending_calls, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Obtener llamadas completadas"""
        completed_calls = Call.objects.filter(status='completed')
        serializer = self.get_serializer(completed_calls, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def failed(self, request):
        """Obtener llamadas fallidas"""
        failed_calls = Call.objects.filter(status='failed')
        serializer = self.get_serializer(failed_calls, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Reintentar una llamada fallida"""
        call = self.get_object()
        if call.status != 'failed':
            return Response(
                {'error': 'Solo se pueden reintentar llamadas fallidas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        call.status = 'pending'
        call.error_message = ''
        call.save()
        serializer = self.get_serializer(call)
        return Response(serializer.data, status=status.HTTP_200_OK)
