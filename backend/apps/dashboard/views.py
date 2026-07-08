"""
apps/dashboard/views.py

Views para el frontend web del sistema de cobranzas.
Agregar en settings.py INSTALLED_APPS: 'apps.dashboard'
Agregar en proyecto_cobranza/urls.py:
    path('', include('apps.dashboard.urls')),
"""

import io
import logging
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.http import JsonResponse

from apps.calls.models import CallBatch, Call
from apps.clients.models import Client
from apps.calls.tasks import process_call_batch

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {"phone_number", "name", "amount"}


class DashboardView(View):
    """GET / — pantalla principal con stats y últimas campañas"""

    def get(self, request):
        batches = CallBatch.objects.order_by("-created_at")[:10]
        total_calls     = Call.objects.count()
        completed_calls = Call.objects.filter(status="completed").count()
        failed_calls    = Call.objects.filter(status="failed").count()

        return render(request, "dashboard/index.html", {
            "batches": batches,
            "stats": {
                "total_batches":  CallBatch.objects.count(),
                "total_calls":    total_calls,
                "completed_calls": completed_calls,
                "failed_calls":   failed_calls,
            },
        })


class CampaignNewView(View):
    """GET/POST /campaigns/new/ — crear campaña y subir CSV"""

    def get(self, request):
        return render(request, "dashboard/campaign_new.html")

    def post(self, request):
        name   = request.POST.get("name", "").strip()
        action = request.POST.get("action", "save")
        file   = request.FILES.get("file")

        if not name:
            messages.error(request, "El nombre de la campaña es obligatorio.")
            return render(request, "dashboard/campaign_new.html")

        if not file:
            messages.error(request, "Debés subir un archivo CSV o Excel.")
            return render(request, "dashboard/campaign_new.html")

        # Leer archivo
        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(file.read()))
            else:
                df = pd.read_excel(io.BytesIO(file.read()))
        except Exception as e:
            messages.error(request, f"No se pudo leer el archivo: {e}")
            return render(request, "dashboard/campaign_new.html")

        # Validar columnas
        missing = REQUIRED_COLUMNS - set(df.columns.str.lower())
        if missing:
            messages.error(request, f"Faltan columnas en el archivo: {', '.join(missing)}")
            return render(request, "dashboard/campaign_new.html")

        df.columns = df.columns.str.lower()

        # Crear el lote
        batch = CallBatch.objects.create(
            name=name,
            status="pending",
            total_clients=len(df),
        )

        # Crear clientes y llamadas
        calls_created = 0
        for _, row in df.iterrows():
            phone = str(row["phone_number"]).strip()
            if not phone:
                continue

            # Obtener o crear cliente
            client, _ = Client.objects.get_or_create(
                phone=phone,
                defaults={
                    "name":        str(row.get("name", "")).strip(),
                    "debt_amount": row.get("amount", 0),
                }
            )
            # Actualizar deuda si el cliente ya existía
            client.debt_amount = row.get("amount", client.debt_amount)
            client.save(update_fields=["debt_amount"])

            Call.objects.create(
                batch=batch,
                client=client,
                status="pending",
            )
            calls_created += 1

        batch.total_clients = calls_created
        batch.save(update_fields=["total_clients"])

        messages.success(request, f"Campaña creada con {calls_created} clientes.")

        # Si eligieron lanzar ahora, encolar la tarea Celery
        if action == "launch":
            process_call_batch.delay(batch.id)
            messages.success(request, "Las llamadas se están iniciando en background.")

        return redirect(f"/campaigns/{batch.id}/")


class CampaignDetailView(View):
    """GET /campaigns/{id}/ — detalle de campaña con llamadas"""

    def get(self, request, pk):
        batch = get_object_or_404(CallBatch, pk=pk)
        calls = Call.objects.filter(batch=batch).select_related("client").order_by("id")

        completed = calls.filter(status="completed").count()
        failed    = calls.filter(status="failed").count()
        pending   = calls.filter(status__in=["pending", "in_progress"]).count()

        return render(request, "dashboard/campaign_detail.html", {
            "batch": batch,
            "calls": calls,
            "stats": {
                "completed": completed,
                "failed":    failed,
                "pending":   pending,
            },
        })


class CampaignLaunchView(View):
    """POST /campaigns/{id}/launch/ — lanzar lote a ElevenLabs"""

    def post(self, request, pk):
        batch = get_object_or_404(CallBatch, pk=pk)

        if batch.status not in ("pending", "failed"):
            messages.error(request, f"El lote no se puede lanzar en estado '{batch.status}'.")
            return redirect(f"/campaigns/{batch.id}/")

        process_call_batch.delay(batch.id)
        messages.success(request, "Llamadas iniciadas. Los resultados se actualizarán automáticamente.")
        return redirect(f"/campaigns/{batch.id}/")


class CampaignStatusView(View):
    """GET /campaigns/{id}/status/ — fragmento HTMX con tabla actualizada"""

    def get(self, request, pk):
        batch = get_object_or_404(CallBatch, pk=pk)
        calls = Call.objects.filter(batch=batch).select_related("client").order_by("id")

        completed = calls.filter(status="completed").count()
        failed    = calls.filter(status="failed").count()
        pending   = calls.filter(status__in=["pending", "in_progress"]).count()

        return render(request, "dashboard/campaign_detail.html", {
            "batch": batch,
            "calls": calls,
            "stats": {
                "completed": completed,
                "failed":    failed,
                "pending":   pending,
            },
        })
