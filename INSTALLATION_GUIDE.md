# 🚀 Guía de Instalación y Uso - Proyecto-Parque

## 📋 Requisitos Previos

- **Node.js** 16+ (descargar desde [nodejs.org](https://nodejs.org))
- **Python** 3.11+ (para el backend)
- **Docker & Docker Compose** (para correr servicios)
- **Git** (para clonar el repositorio)

## 🎯 Instalación Completa

### 1️⃣ Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/proyecto-parque.git
cd proyecto-parque
```

### 2️⃣ Backend (Django)

#### Crear Entorno Virtual

```bash
cd backend
python -m venv venv

# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate
```

#### Instalar Dependencias

```bash
pip install -r requirements.txt
```

#### Configurar Base de Datos

```bash
python manage.py migrate
python manage.py createsuperuser
```

#### Crear variables de entorno

```bash
# Crear archivo backend/.env
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=postgresql://user:password@localhost:5432/proyecto_parque
REDIS_URL=redis://localhost:6379
ELEVENLABS_API_KEY=tu-api-key-aqui
```

#### Correr Servidor de Desarrollo

```bash
python manage.py runserver
# El servidor está en http://localhost:8000
```

### 3️⃣ Frontend (React)

#### Instalar Dependencias

```bash
cd frontend
npm install
```

#### Variables de Entorno

```bash
# Crear archivo frontend/.env.local
VITE_API_URL=http://localhost:8000/api
```

#### Correr Servidor de Desarrollo

```bash
npm run dev
# El servidor está en http://localhost:5173
```

### 4️⃣ Docker Compose (Alternativa - Recomendado)

#### Crear archivo `.env`

```bash
# En la raíz del proyecto
DEBUG=False
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=postgresql://postgres:postgres@db:5432/proyecto_parque
REDIS_URL=redis://redis:6379
ELEVENLABS_API_KEY=tu-api-key-aqui
```

#### Iniciar Servicios

```bash
docker-compose up -d

# Ver logs
docker-compose logs -f web
docker-compose logs -f celery

# Detener servicios
docker-compose down
```

## ✅ Verificación de Instalación

### Backend

```bash
curl http://localhost:8000/api/
# Respuesta esperada: JSON con links a endpoints
```

### Frontend

```bash
# Abre http://localhost:5173 en tu navegador
# Deberías ver el Dashboard
```

## 📚 Estructura del Proyecto

```
proyecto-parque/
├── backend/
│   ├── apps/
│   │   ├── clients/
│   │   ├── calls/
│   │   ├── core/
│   │   └── __init__.py
│   ├── proyecto_cobranza/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── __init__.py
│   ├── manage.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── store/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── .env.local
├── docker-compose.yml
├── README.md
└── .gitignore
```

## 🔧 Comandos Útiles

### Backend

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Shell interactivo
python manage.py shell

# Tests
python manage.py test

# Limpiar base de datos
python manage.py flush
```

### Frontend

```bash
# Desarrollo
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview

# Linter (ESLint)
npm run lint
```

### Docker

```bash
# Iniciar en background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ejecutar comando en contenedor
docker-compose exec web python manage.py migrate

# Detener
docker-compose down

# Limpiar todo (también volumes)
docker-compose down -v
```

## 🔑 API Endpoints Principales

### Clientes
- `GET /api/clients/` - Listar clientes
- `POST /api/clients/` - Crear cliente
- `GET /api/clients/{id}/` - Obtener cliente
- `PUT /api/clients/{id}/` - Actualizar cliente
- `DELETE /api/clients/{id}/` - Eliminar cliente
- `POST /api/clients/{id}/activate/` - Activar cliente
- `POST /api/clients/{id}/deactivate/` - Desactivar cliente

### Lotes
- `GET /api/calls/batches/` - Listar lotes
- `POST /api/calls/batches/` - Crear lote
- `GET /api/calls/batches/{id}/` - Obtener lote
- `POST /api/calls/batches/{id}/start/` - Iniciar lote
- `POST /api/calls/batches/{id}/complete/` - Completar lote

### Llamadas
- `GET /api/calls/` - Listar llamadas
- `POST /api/calls/` - Crear llamada
- `GET /api/calls/{id}/` - Obtener llamada
- `POST /api/calls/{id}/retry/` - Reintentar llamada

## 🔐 Variables de Entorno

### Backend

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@host:port/dbname
REDIS_URL=redis://host:port
ELEVENLABS_API_KEY=your-api-key
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend

```env
VITE_API_URL=http://localhost:8000/api
```

## 🐛 Solución de Problemas

### Error: "Connection refused"
- Verifica que el backend esté corriendo
- Verifica que PostgreSQL y Redis estén accesibles

### Error: CORS
- Verifica `ALLOWED_HOSTS` en `settings.py`
- Verifica `CORS_ALLOWED_ORIGINS`

### Error: "Module not found"
- Ejecuta `npm install` (frontend) o `pip install -r requirements.txt` (backend)

### Limpiar Cache
```bash
# Frontend
rm -rf node_modules
npm install

# Backend
pip install --upgrade pip
pip install -r requirements.txt
```

## 📊 Testing

### Backend

```bash
# Ejecutar todos los tests
python manage.py test

# Tests específicos
python manage.py test apps.clients.tests
```

### Frontend

```bash
# Próximamente
npm run test
```

## 🚀 Deployment

### Backend (Gunicorn + Nginx)

```bash
# Instalar gunicorn
pip install gunicorn

# Correr con gunicorn
gunicorn proyecto_cobranza.wsgi --bind 0.0.0.0:8000
```

### Frontend (Vercel / Netlify)

1. Push código a GitHub
2. Conecta repositorio en Vercel/Netlify
3. Configura variables de entorno
4. Deploy automático

## 📝 Logging

### Ver logs en Docker

```bash
docker-compose logs -f web      # Django
docker-compose logs -f celery   # Celery
docker-compose logs -f db       # PostgreSQL
```

### Ver logs locales

```bash
# Backend (Django)
tail -f logs/django.log

# Frontend (navegador)
F12 → Console
```

## 🆘 Contacto y Soporte

- 📧 Email: support@proyecto-parque.com
- 📋 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

**Última actualización**: 2026-06-02
**Versión**: 1.0.0
