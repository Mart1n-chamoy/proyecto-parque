# 🧪 Guía de Pruebas - Proyecto-Parque

## Inicio Rápido

### Opción 1: Docker Compose (Recomendado)

```bash
cd proyecto-parque
docker-compose up -d
```

Espera 10-15 segundos y verifica que los servicios estén corriendo:

```bash
docker ps
```

Deberías ver 4 contenedores:
- `proyecto-parque-db-1` (PostgreSQL)
- `proyecto-parque-redis-1` (Redis)
- `proyecto-parque-web-1` (Django)
- `proyecto-parque-celery-1` (Celery)

### Opción 2: Django Local Dev Server

Si no tienes Docker, puedes ejecutar Django localmente:

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Nota: Necesitarás PostgreSQL y Redis corriendo localmente en puertos 5432 y 6379.

---

## 🧪 Ejecutar Pruebas

### Windows (PowerShell)

```powershell
# Desde la raíz del proyecto
.\test_endpoints.ps1
```

### Linux/Mac (Bash)

```bash
# Desde la raíz del proyecto
chmod +x test_endpoints.sh
./test_endpoints.sh
```

---

## 📊 Pruebas Individuales

### Crear un Cliente

```bash
curl -X POST http://localhost:8000/api/clients/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Juan",
    "last_name": "García",
    "phone": "+54911234567",
    "email": "juan@example.com",
    "debt_amount": "5000.00",
    "is_active": true
  }'
```

**Respuesta esperada**: 201 Created

### Listar Clientes

```bash
curl http://localhost:8000/api/clients/
```

**Respuesta esperada**: 200 OK con lista de clientes

### Crear Lote de Llamadas

```bash
curl -X POST http://localhost:8000/api/calls/batches/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Lote",
    "description": "Descripción del lote",
    "total_clients": 10
  }'
```

**Respuesta esperada**: 201 Created

### Crear Llamada

```bash
curl -X POST http://localhost:8000/api/calls/ \
  -H "Content-Type: application/json" \
  -d '{
    "batch": 1,
    "client": 1,
    "status": "pending"
  }'
```

**Respuesta esperada**: 201 Created

### Filtrar Clientes Activos

```bash
curl "http://localhost:8000/api/clients/?is_active=true"
```

### Buscar Clientes por Nombre

```bash
curl "http://localhost:8000/api/clients/?search=Juan"
```

### Listar Llamadas Pendientes

```bash
curl http://localhost:8000/api/calls/pending/
```

### Iniciar un Lote

```bash
curl -X POST http://localhost:8000/api/calls/batches/1/start/
```

**Respuesta esperada**: 200 OK con estado actualizado a "processing"

### Desactivar un Cliente

```bash
curl -X POST http://localhost:8000/api/clients/1/deactivate/
```

**Respuesta esperada**: 200 OK con is_active: false

---

## 🛑 Detener Servicios

### Docker

```bash
docker-compose down
```

Para limpiar también los volúmenes:

```bash
docker-compose down -v
```

### Django Local

Presiona `Ctrl+C` en la terminal

---

## 🔗 URLs Útiles

- **API Root**: http://localhost:8000/api/
- **Clients**: http://localhost:8000/api/clients/
- **Calls**: http://localhost:8000/api/calls/
- **Call Batches**: http://localhost:8000/api/calls/batches/
- **Admin Panel**: http://localhost:8000/admin/

---

## 📋 Checklist de Verificación

- [ ] Servicios levantados correctamente
- [ ] Crear cliente exitoso (201)
- [ ] Listar clientes exitoso (200)
- [ ] Crear lote exitoso (201)
- [ ] Crear llamada exitosa (201)
- [ ] Acciones personalizadas funcionan
- [ ] Filtros funcionan
- [ ] Búsqueda funciona
- [ ] No hay errores en los logs

---

## 🐛 Solución de Problemas

### Error: "Connection refused"
- Verifica que Docker esté corriendo
- Si usas local, verifica que PostgreSQL esté en puerto 5432

### Error: "Port already in use"
- El puerto 8000 ya está en uso
- Cambia el puerto en docker-compose.yml

### Error: "No such file or directory"
- Asegúrate de estar en la raíz del proyecto
- Verifica que .env existe

### Base de datos vacía después de reiniciar
- Es normal, Docker resetea los datos
- Para persistencia, modifica docker-compose.yml

---

## 📚 Recursos Adicionales

- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [API_ENDPOINTS.md](./API_ENDPOINTS.md) - Documentación detallada
- [docker-compose.yml](./docker-compose.yml) - Configuración de servicios

---

**Última actualización**: 2026-06-02
