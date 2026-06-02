# 🔐 Autenticación JWT - Proyecto-Parque

Implementación completa de autenticación con tokens JWT (JSON Web Token).

## 📚 Tabla de Contenidos

- [Backend](#backend)
- [Frontend](#frontend)
- [API Endpoints](#api-endpoints)
- [Flujo de Autenticación](#flujo-de-autenticación)
- [Configuración](#configuración)
- [Troubleshooting](#troubleshooting)

## 🔙 Backend

### Instalación

```bash
cd backend
pip install -r requirements.txt
```

JWT ya está incluído en `requirements.txt`:
```
djangorestframework-simplejwt==5.3.2
```

### Configuración en `settings.py`

```python
from datetime import timedelta

INSTALLED_APPS = [
    # ...
    'rest_framework',
    'apps.auth_app',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### Endpoints de Autenticación

```
POST /api/auth/register/      - Registrar nuevo usuario
POST /api/auth/login/         - Iniciar sesión
POST /api/auth/refresh/       - Refrescar access token
POST /api/auth/logout/        - Cerrar sesión
GET  /api/auth/me/            - Obtener datos del usuario
PUT  /api/auth/me/            - Actualizar perfil
```

### Vistas Disponibles

**RegisterView** (`POST /api/auth/register/`)
```json
{
  "username": "juan_perez",
  "email": "juan@example.com",
  "password": "mi_contraseña",
  "password2": "mi_contraseña",
  "first_name": "Juan",
  "last_name": "Perez"
}
```

Respuesta:
```json
{
  "user": {
    "id": 1,
    "username": "juan_perez",
    "email": "juan@example.com"
  },
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc..."
}
```

**LoginView** (`POST /api/auth/login/`)
```json
{
  "username": "juan_perez",
  "password": "mi_contraseña"
}
```

**RefreshTokenView** (`POST /api/auth/refresh/`)
```json
{
  "refresh": "eyJhbGc..."
}
```

Respuesta:
```json
{
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc..."
}
```

**MeView** (`GET /api/auth/me/`)
Requiere: `Authorization: Bearer <access_token>`

Respuesta:
```json
{
  "id": 1,
  "username": "juan_perez",
  "email": "juan@example.com",
  "first_name": "Juan",
  "last_name": "Perez"
}
```

## 🎨 Frontend

### Instalación

```bash
cd frontend
npm install
```

### Estructura de Archivos

```
frontend/src/
├── pages/
│   ├── Login.jsx          - Página de inicio de sesión
│   ├── Register.jsx       - Página de registro
│   └── ...
├── components/
│   ├── ProtectedRoute.jsx - Rutas protegidas
│   └── layout/
│       └── Header.jsx     - Header con logout
├── api/
│   └── client.js          - Cliente HTTP con interceptores
└── App.jsx                - Rutas y protección
```

### Componentes Principales

#### ProtectedRoute

Protege rutas que requieren autenticación:

```jsx
<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  }
/>
```

#### Login.jsx

- Formulario de inicio de sesión
- Guardar tokens en localStorage
- Validación de errores
- Toggle mostrar/ocultar contraseña

#### Register.jsx

- Formulario de registro
- Validación de coincidencia de contraseñas
- Crear usuario automáticamente
- Redirigir a dashboard después del registro

### Cliente HTTP (`api/client.js`)

#### Interceptores

**Request Interceptor:**
- Agrega `Authorization: Bearer <token>` a cada petición

**Response Interceptor:**
- Captura errores 401 (no autorizado)
- Intenta refrescar el token automáticamente
- Si falla, redirige a login

#### Métodos de Autenticación

```javascript
import { authAPI } from './src/api/client'

// Registrarse
authAPI.register({
  username: 'juan',
  email: 'juan@example.com',
  password: 'pass123',
  password2: 'pass123'
})

// Iniciar sesión
authAPI.login({
  username: 'juan',
  password: 'pass123'
})

// Refrescar token
authAPI.refresh(refreshToken)

// Obtener datos del usuario
authAPI.me()

// Actualizar perfil
authAPI.updateProfile({
  first_name: 'Juan',
  last_name: 'Perez'
})

// Logout
authAPI.logout()
```

### Manejo de Tokens

Los tokens se guardan en localStorage:

```javascript
// Guardar tokens después de login
localStorage.setItem('access_token', data.access)
localStorage.setItem('refresh_token', data.refresh)
localStorage.setItem('user', JSON.stringify(data.user))

// Obtener token
const token = localStorage.getItem('access_token')

// Limpiar tokens (logout)
localStorage.removeItem('access_token')
localStorage.removeItem('refresh_token')
localStorage.removeItem('user')
```

## 🔌 API Endpoints

### Autenticación

```bash
# Registro
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "email": "demo@example.com",
    "password": "demo123",
    "password2": "demo123"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'

# Obtener datos del usuario (requiere token)
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer <access_token>"

# Refrescar token
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'

# Logout
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer <access_token>"
```

### Acceder a Endpoints Protegidos

```bash
# Ejemplo: obtener clientes (requiere autenticación)
curl -X GET http://localhost:8000/api/clients/ \
  -H "Authorization: Bearer <access_token>"
```

## 🔄 Flujo de Autenticación

```
┌─────────┐
│ Usuario │
└────┬────┘
     │
     ├─→ [Inicia sesión / Registra]
     │
     ├─→ POST /api/auth/login/ o /register/
     │
     ├─→ Recibe: access_token + refresh_token
     │
     ├─→ Guarda en localStorage
     │
     ├─→ Redirige a /dashboard
     │
     ├─→ Access token se agrega en cada petición
     │
     ├─→ Si token expira (401)
     │
     ├─→ POST /api/auth/refresh/
     │
     ├─→ Obtiene nuevo access_token
     │
     └─→ Reintenta petición original
```

## ⚙️ Configuración

### Variables de Entorno

**Backend (.env)**
```env
DEBUG=True
SECRET_KEY=tu-clave-secreta
DATABASE_URL=postgresql://user:pass@localhost:5432/db
```

**Frontend (.env.local)**
```env
VITE_API_URL=http://localhost:8000/api
```

### Tiempos de Tokens

```python
ACCESS_TOKEN_LIFETIME = timedelta(minutes=60)      # Expira en 1 hora
REFRESH_TOKEN_LIFETIME = timedelta(days=7)         # Expira en 7 días
```

Modifica estos valores en `settings.py` según tus necesidades.

## 📊 Token Structure

JWT está compuesto por 3 partes:

```
Header.Payload.Signature

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Payload típico:**
```json
{
  "token_type": "access",
  "exp": 1234567890,
  "iat": 1234567800,
  "jti": "abc123",
  "user_id": 1,
  "username": "juan"
}
```

## 🔐 Seguridad

### Best Practices

1. **HTTPS en Producción**
   ```
   Los tokens deben enviarse solo por HTTPS
   ```

2. **Expiración de Tokens**
   ```
   Access: 1 hora (corta vida)
   Refresh: 7 días (larga vida)
   ```

3. **Almacenamiento Seguro**
   ```
   localStorage vs sessionStorage
   - localStorage: persiste entre sesiones
   - sessionStorage: se limpia al cerrar navegador
   ```

4. **CORS Configuration**
   ```python
   CORS_ALLOWED_ORIGINS = [
       'https://tudominio.com',
       'https://app.tudominio.com',
   ]
   ```

5. **Validación de Contraseñas**
   ```
   - Mínimo 8 caracteres
   - Mezcla de mayúsculas, minúsculas, números
   - Sin caracteres especiales peligrosos
   ```

## 🐛 Troubleshooting

### Error: "Invalid token"

```
Causa: Token expirado o inválido
Solución: 
1. Intenta refrescar el token
2. Si falla, redirige a login
3. Usuario debe iniciar sesión nuevamente
```

### Error: "Authentication credentials were not provided"

```
Causa: Token no incluído en header Authorization
Solución:
1. Verifica que el token esté en localStorage
2. Comprueba el formato: "Bearer <token>"
3. Revisa el interceptor de Axios
```

### Error: "Token is blacklisted"

```
Causa: Token fue revocado
Solución:
1. Limpia localStorage
2. Usuario debe iniciar sesión nuevamente
```

### Error: CORS

```
Causa: Frontend y backend en dominios diferentes
Solución:
1. Configura CORS_ALLOWED_ORIGINS en settings.py
2. Incluye credentials en requests si es necesario
```

### Error: "Refresh token expired"

```
Causa: Refresh token expiró (después de 7 días)
Solución:
1. Usuario debe iniciar sesión nuevamente
2. O extender REFRESH_TOKEN_LIFETIME en settings.py
```

## 📚 Referencias

- [Django REST Framework SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [JWT.io](https://jwt.io/)
- [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)

---

**Última actualización**: 2026-06-02
**Versión**: 1.0.0
