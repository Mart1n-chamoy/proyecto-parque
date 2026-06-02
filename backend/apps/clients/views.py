from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Clientes.
    
    Soporta operaciones CRUD completas:
    - GET /clients/ - Lista todos los clientes
    - POST /clients/ - Crear un nuevo cliente
    - GET /clients/{id}/ - Obtener detalles de un cliente
    - PUT /clients/{id}/ - Actualizar un cliente
    - PATCH /clients/{id}/ - Actualizar parcialmente un cliente
    - DELETE /clients/{id}/ - Eliminar un cliente
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    ordering_fields = ['created_at', 'debt_amount']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Obtener solo los clientes activos"""
        active_clients = Client.objects.filter(is_active=True)
        serializer = self.get_serializer(active_clients, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def inactive(self, request):
        """Obtener solo los clientes inactivos"""
        inactive_clients = Client.objects.filter(is_active=False)
        serializer = self.get_serializer(inactive_clients, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Desactivar un cliente"""
        client = self.get_object()
        client.is_active = False
        client.save()
        serializer = self.get_serializer(client)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activar un cliente"""
        client = self.get_object()
        client.is_active = True
        client.save()
        serializer = self.get_serializer(client)
        return Response(serializer.data, status=status.HTTP_200_OK)
