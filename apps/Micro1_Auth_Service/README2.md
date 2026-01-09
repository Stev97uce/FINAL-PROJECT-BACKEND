# Auth Service - Sistema UCE

Microservicio de autenticación para el sistema de gestión de consultantes de la Facultad de Psicología UCE.

## 🚀 Stack Tecnológico

- **Python 3.11+**
- **FastAPI** - Framework web
- **MySQL 8.0** - Base de datos
- **RabbitMQ** - Message broker para eventos
- **JWT** - Autenticación con tokens
- **BCrypt** - Hashing de contraseñas (cost factor 12)

## 📋 Requisitos Previos

1. **Python 3.11 o superior**
2. **MySQL 8.0**
3. **RabbitMQ** (opcional para desarrollo)

## 🔧 Instalación

### 1. Crear entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copiar `.env.example` a `.env` y configurar:

```powershell
cp .env.example .env
```

Editar `.env` con tus credenciales:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=auth_service_db

JWT_SECRET_KEY=genera-una-clave-secreta-segura
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_EXCHANGE=uce_events
```

### 4. Crear base de datos MySQL

```sql
CREATE DATABASE auth_service_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Las tablas se crearán automáticamente al iniciar la aplicación.

## 🏃 Ejecución

### Modo desarrollo

```powershell
python run.py
```

O con uvicorn directamente:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La aplicación estará disponible en: `http://localhost:8000`

## 📚 Documentación API

Una vez iniciado el servidor, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Endpoints Principales

### Autenticación

- `POST /api/auth/register` - Registrar nuevo usuario
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/verify-email/{token}` - Verificar email
- `POST /api/auth/forgot-password` - Solicitar recuperación
- `POST /api/auth/reset-password` - Restablecer contraseña
- `POST /api/auth/refresh` - Renovar access token
- `POST /api/auth/logout` - Cerrar sesión
- `GET /api/auth/validate` - Validar token (interno)

### Health Check

- `GET /health` - Estado del servicio

## 🧪 Pruebas con Postman

### 1. Registrar usuario (Consultante)

```http
POST http://localhost:8000/api/auth/register
Content-Type: application/json

{
  "nombres": "Juan Pérez",
  "identificacion": "1234567890",
  "email": "juan@example.com",
  "telefono": "0999999999",
  "password": "Password123",
  "rol": "consultante"
}
```

### 2. Verificar email

```http
GET http://localhost:8000/api/auth/verify-email/{token}
```

### 3. Login

```http
POST http://localhost:8000/api/auth/login
Content-Type: application/json

{
  "email": "juan@example.com",
  "password": "Password123"
}
```

### 4. Validar token

```http
GET http://localhost:8000/api/auth/validate
Authorization: Bearer {access_token}
```

## 📦 Estructura del Proyecto

```
BACKEND/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación FastAPI
│   ├── config.py            # Configuración
│   ├── database.py          # Conexión a BD
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Schemas Pydantic
│   ├── security.py          # JWT y hashing
│   ├── events.py            # RabbitMQ events
│   ├── dependencies.py      # Dependencias FastAPI
│   └── routes/
│       ├── __init__.py
│       └── auth.py          # Rutas de autenticación
├── requirements.txt
├── .env.example
├── .gitignore
├── run.py
└── README.md
```

## 🔒 Seguridad

- Passwords hasheados con BCrypt (cost factor 12)
- JWT con expiración de 24 horas
- Refresh tokens con expiración de 7 días
- Tokens de verificación expiran en 24 horas
- Tokens de recuperación expiran en 1 hora
- Validación de contraseñas fuertes (8+ caracteres, mayúsculas, minúsculas, números)

## 🎯 Roles de Usuario

1. **consultante** - Puede auto-registrarse
2. **recepcionista** - Requiere registro por admin
3. **estudiante** - Requiere registro por admin
4. **psicologo_supervisor** - Requiere registro por admin
5. **administrador** - Requiere registro por admin

## 📡 Eventos Emitidos (RabbitMQ)

1. `user.registered` - Usuario registrado
2. `user.verified` - Email verificado
3. `password.reset_requested` - Recuperación de contraseña solicitada

## ⚠️ Notas Importantes

- El servicio NO maneja perfiles completos (eso es responsabilidad de User Service)
- Solo maneja autenticación y seguridad
- RabbitMQ es opcional para desarrollo local
- En producción, cambiar CORS origins y JWT_SECRET_KEY

## 🐛 Troubleshooting

### Error de conexión a MySQL

Verificar que MySQL esté corriendo y las credenciales sean correctas.

### Error de conexión a RabbitMQ

Si no tienes RabbitMQ instalado, los eventos no se publicarán pero el servicio funcionará.

### Error de importación

Asegúrate de estar en el entorno virtual:

```powershell
.\venv\Scripts\Activate.ps1
```
