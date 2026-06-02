from rest_framework import serializers
from .models import CallBatch, Call
from apps.clients.serializers import ClientSerializer


class CallBatchSerializer(serializers.ModelSerializer):
    """Serializer para el modelo CallBatch"""
    calls_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CallBatch
        fields = [
            'id',
            'name',
            'description',
            'status',
            'total_clients',
            'processed_clients',
            'calls_count',
            'created_at',
            'started_at',
            'completed_at',
        ]
        read_only_fields = ['id', 'processed_clients', 'created_at', 'started_at', 'completed_at']
    
    def get_calls_count(self, obj):
        """Obtener el número de llamadas en el lote"""
        return obj.calls.count()


class CallSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Call"""
    client_details = ClientSerializer(source='client', read_only=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    
    class Meta:
        model = Call
        fields = [
            'id',
            'batch',
            'batch_name',
            'client',
            'client_details',
            'status',
            'duration',
            'transcript',
            'audio_file',
            'error_message',
            'created_at',
            'started_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'duration',
            'transcript',
            'audio_file',
            'error_message',
            'created_at',
            'started_at',
            'completed_at',
        ]
