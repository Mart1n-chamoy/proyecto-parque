# proyecto-parque

Sistema automatizado de cobranza telefónica con IA (ElevenLabs) integrado en Django + React.

## 🚀 Inicio Rápido

### Con Docker (Recomendado)
```bash
docker-compose up -d
```

### Local
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 📋 Stack Tecnológico

- **Backend**: Django 4.2 + Django REST Framework
- **Frontend**: React (en carpeta frontend/)
- **Base de Datos**: PostgreSQL
- **Cache/Queue**: Redis + Celery
- **IA**: ElevenLabs API para síntesis de voz

## 📊 Estructura del Proyecto

```
proyecto-parque/
├── backend/
│   ├── apps/
│   │   ├── clients/      # Gestión de clientes
│   │   ├── calls/        # Gestión de llamadas
│   │   └── core/         # Configuración común
│   ├── requirements.txt
│   └── manage.py
├── frontend/             # React App
├── docker-compose.yml
└── README.md
```

## 🔌 Endpoints Disponibles

### Clientes
- `GET    /api/clients/` - Listar clientes
- `POST   /api/clients/` - Crear cliente
- `GET    /api/clients/{id}/` - Obtener cliente
- `PUT    /api/clients/{id}/` - Actualizar cliente
- `DELETE /api/clients/{id}/` - Eliminar cliente
- `GET    /api/clients/active/` - Clientes activos
- `POST   /api/clients/{id}/activate/` - Activar
- `POST   /api/clients/{id}/deactivate/` - Desactivar

### Llamadas
- `GET    /api/calls/` - Listar llamadas
- `POST   /api/calls/` - Crear llamada
- `GET    /api/calls/pending/` - Pendientes
- `GET    /api/calls/completed/` - Completadas
- `POST   /api/calls/{id}/retry/` - Reintentar

### Lotes de Llamadas
- `GET    /api/calls/batches/` - Listar lotes
- `POST   /api/calls/batches/` - Crear lote
- `GET    /api/calls/batches/pending/` - Pendientes
- `POST   /api/calls/batches/{id}/start/` - Iniciar
- `POST   /api/calls/batches/{id}/complete/` - Completar

Documentación completa: [API_ENDPOINTS.md](./API_ENDPOINTS.md)

## 🧪 Pruebas

### Ejecutar pruebas
```bash
# Windows
.\test_endpoints.ps1

# Linux/Mac
./test_endpoints.sh
```

Guía detallada: [TESTING_GUIDE.md](./TESTING_GUIDE.md)

## 📚 Documentación

- [API_ENDPOINTS.md](./API_ENDPOINTS.md) - Endpoints y ejemplos
- [TESTING_GUIDE.md](./TESTING_GUIDE.md) - Guía de pruebas
- [TEST_REPORT.md](./.copilot/session-state/*/files/TEST_REPORT.md) - Reporte de pruebas

## 🔐 Configuración

Crear archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

Editar valores:
- `DJANGO_SECRET_KEY` - Clave secreta
- `DB_PASSWORD` - Contraseña PostgreSQL
- `ELEVENLABS_API_KEY` - Tu API key de ElevenLabs

## 🛠️ Desarrollo

### Backend
```bash
cd backend
pip install -r requirements.txt
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## 🐳 Docker

```bash
# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f web

# Parar servicios
docker-compose down
```

## 📞 Características

- ✅ Gestión de clientes con deuda
- ✅ Creación de lotes de llamadas
- ✅ Registro de llamadas individuales
- ⏳ Integración con ElevenLabs (en desarrollo)
- ⏳ Sistema de audio/transcripción (en desarrollo)
- ⏳ Dashboard de analytics (en desarrollo)

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

MIT

## ✉️ Contacto

Luis Martín Chamoy - [@Mart1n-chamoy](https://github.com/Mart1n-chamoy)