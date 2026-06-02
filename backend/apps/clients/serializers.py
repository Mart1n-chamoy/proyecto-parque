from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Client"""
    
    class Meta:
        model = Client
        fields = [
            'id',
            'first_name',
            'last_name',
            'phone',
            'email',
            'debt_amount',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def validate_phone(self, value):
        """Validar que el teléfono sea único en CREATE, pero permitir en UPDATE"""
        if self.instance is None:  # Es un CREATE
            if Client.objects.filter(phone=value).exists():
                raise serializers.ValidationError("Este teléfono ya está registrado.")
        return value
    
    def validate_debt_amount(self, value):
        """Validar que el monto de deuda sea positivo"""
        if value < 0:
            raise serializers.ValidationError("El monto de deuda debe ser mayor a 0.")
        return value
