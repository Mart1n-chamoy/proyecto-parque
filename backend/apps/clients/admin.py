from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'debt_amount', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('first_name', 'last_name', 'phone')
    readonly_fields = ('created_at', 'updated_at')
