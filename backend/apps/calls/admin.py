from django.contrib import admin
from .models import CallBatch, Call


@admin.register(CallBatch)
class CallBatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'total_clients', 'processed_clients', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'started_at', 'completed_at')


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ('get_client_phone', 'status', 'duration', 'created_at')
    list_filter = ('status', 'batch', 'created_at')
    search_fields = ('client__phone', 'batch__name')
    readonly_fields = ('created_at', 'started_at', 'completed_at')

    def get_client_phone(self, obj):
        return obj.client.phone
    get_client_phone.short_description = 'Clientes'
