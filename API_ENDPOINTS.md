# Documentación de APIs REST - proyecto-parque

## 📋 Resumen de Endpoints

### Clientes
- `GET    /api/clients/` - Listar todos los clientes (con filtros y búsqueda)
- `POST   /api/clients/` - Crear un nuevo cliente
- `GET    /api/clients/{id}/` - Obtener detalles de un cliente
- `PUT    /api/clients/{id}/` - Actualizar completamente un cliente
- `PATCH  /api/clients/{id}/` - Actualizar parcialmente un cliente
- `DELETE /api/clients/{id}/` - Eliminar un cliente
- `GET    /api/clients/active/` - Listar solo clientes activos
- `GET    /api/clients/inactive/` - Listar solo clientes inactivos
- `POST   /api/clients/{id}/activate/` - Activar un cliente
- `POST   /api/clients/{id}/deactivate/` - Desactivar un cliente

### Lotes de Llamadas
- `GET    /api/calls/batches/` - Listar todos los lotes
- `POST   /api/calls/batches/` - Crear un nuevo lote
- `GET    /api/calls/batches/{id}/` - Obtener detalles de un lote
- `PUT    /api/calls/batches/{id}/` - Actualizar completamente un lote
- `PATCH  /api/calls/batches/{id}/` - Actualizar parcialmente un lote
- `DELETE /api/calls/batches/{id}/` - Eliminar un lote
- `GET    /api/calls/batches/pending/` - Listar lotes pendientes
- `GET    /api/calls/batches/processing/` - Listar lotes en procesamiento
- `POST   /api/calls/batches/{id}/start/` - Iniciar procesamiento de un lote
- `POST   /api/calls/batches/{id}/complete/` - Marcar lote como completado

### Llamadas
- `GET    /api/calls/` - Listar todas las llamadas
- `POST   /api/calls/` - Crear una nueva llamada
- `GET    /api/calls/{id}/` - Obtener detalles de una llamada
- `PUT    /api/calls/{id}/` - Actualizar completamente una llamada
- `PATCH  /api/calls/{id}/` - Actualizar parcialmente una llamada
- `DELETE /api/calls/{id}/` - Eliminar una llamada
- `GET    /api/calls/pending/` - Listar llamadas pendientes
- `GET    /api/calls/completed/` - Listar llamadas completadas
- `GET    /api/calls/failed/` - Listar llamadas fallidas
- `POST   /api/calls/{id}/retry/` - Reintentar una llamada fallida

## 🔍 Filtros y Búsqueda

### Clientes
- Filtros: `?is_active=true` (true/false)
- Búsqueda: `?search=nombre|apellido|teléfono|email`
- Ordenamiento: `?ordering=created_at|-debt_amount`

### Lotes de Llamadas
- Filtros: `?status=pending|processing|completed|failed`
- Búsqueda: `?search=nombre|descripción`
- Ordenamiento: `?ordering=created_at|-total_clients`

### Llamadas
- Filtros: `?status=pending|in_progress|completed|failed&batch=id&client=id`
- Búsqueda: `?search=teléfono|transcripción|nombre_lote`
- Ordenamiento: `?ordering=created_at|-duration`

## 📌 Ejemplos de Uso

### Crear un Cliente
```bash
POST /api/clients/
Content-Type: application/json

{
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone": "+54911234567",
  "email": "juan@example.com",
  "debt_amount": "5000.00",
  "is_active": true
}
```

### Crear un Lote de Llamadas
```bash
POST /api/calls/batches/
Content-Type: application/json

{
  "name": "Lote de Cobranza Enero",
  "description": "Clientes con deuda mayor a $1000",
  "total_clients": 150
}
```

### Crear una Llamada
```bash
POST /api/calls/
Content-Type: application/json

{
  "batch": 1,
  "client": 1,
  "status": "pending"
}
```

### Listar Clientes Activos
```bash
GET /api/clients/active/
```

### Listar Lotes Pendientes
```bash
GET /api/calls/batches/pending/
```

### Reintentar una Llamada Fallida
```bash
POST /api/calls/123/retry/
```

## ⚙️ Configuración Utilizada

- **Django REST Framework 3.14.0** - Framework REST
- **Django Filter 24.1** - Filtrado de querysets
- **Paginación**: 10 items por página por defecto
- **CORS**: Configurado para localhost:3000, localhost:8000

## 📝 Notas Importantes

1. Los serializers validan automáticamente:
   - Unicidad de teléfono en clientes
   - Montos de deuda positivos
   
2. Los ViewSets incluyen acciones personalizadas para casos de uso comunes

3. Todos los endpoints retornan timestamps de creación y actualización

4. Las llamadas están vinculadas a clientes y lotes automáticamente
