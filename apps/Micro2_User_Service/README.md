# User Service - UCE Sistema de Gestión

Microservicio de gestión de perfiles de usuario para el sistema de gestión de consultantes UCE.

## Descripción

Este microservicio gestiona:
- Perfiles extendidos de usuario
- Información personal complementaria
- Contactos de emergencia
- Historial de actividad
- Preferencias de usuario

## Stack Tecnológico

- Python 3.11
- FastAPI
- PostgreSQL 14
- SQLAlchemy
- RabbitMQ (eventos)
- Redis (caché)

## Prerequisitos

- Python 3.11+
- PostgreSQL 14+
- Docker y Docker Compose

## Instalación Local

### 1. Configurar Variables de Entorno

```bash
cp .env.template .env
# Editar .env con tus credenciales
```

### 2. Crear Base de Datos

```bash
# Conectar a PostgreSQL
docker exec -it uce_postgresql psql -U root -d postgres

# Ejecutar script
\i /docker-entrypoint-initdb.d/user_service_setup.sql
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar Servicio

```bash
python run.py
```

El servicio estará disponible en http://localhost:8001

## Instalación con Docker

```bash
# Desde la raíz del proyecto
docker-compose up -d uce_user_service
```

## API Endpoints

### Perfil de Usuario

#### POST /api/users/profile
Crear perfil de usuario

**Request:**
```json
{
  "direccion": "Av. Principal 123",
  "ciudad": "Quito",
  "pais": "Ecuador",
  "fecha_nacimiento": "1990-05-15",
  "genero": "masculino",
  "telefono_alternativo": "+593987654321",
  "contacto_emergencia_nombre": "María García",
  "contacto_emergencia_telefono": "+593912345678",
  "ocupacion": "Estudiante",
  "institucion": "UCE",
  "preferencias": {
    "notificaciones_email": true,
    "notificaciones_sms": false
  }
}
```

**Response:** 201 Created

#### GET /api/users/profile
Obtener perfil del usuario actual

**Headers:**
```
Authorization: Bearer {token}
```

**Response:** 200 OK

#### PUT /api/users/profile
Actualizar perfil del usuario actual

**Headers:**
```
Authorization: Bearer {token}
```

**Request:** (campos opcionales)
```json
{
  "ciudad": "Guayaquil",
  "ocupacion": "Profesional"
}
```

**Response:** 200 OK

#### GET /api/users/profile/{user_id}
Obtener perfil de cualquier usuario (admin/supervisor)

**Headers:**
```
Authorization: Bearer {token}
```

**Roles:** administrador, supervisor

**Response:** 200 OK

#### GET /api/users/complete/{user_id}
Obtener información completa del usuario (auth + profile)

**Headers:**
```
Authorization: Bearer {token}
```

**Roles:** administrador, supervisor

**Response:** 200 OK

### Actividad

#### GET /api/users/activity
Obtener logs de actividad del usuario actual

**Headers:**
```
Authorization: Bearer {token}
```

**Query Params:**
- limit (default: 50)

**Response:** 200 OK

#### GET /api/users/activity/{user_id}
Obtener logs de actividad de cualquier usuario (admin)

**Headers:**
```
Authorization: Bearer {token}
```

**Roles:** administrador

**Response:** 200 OK

#### POST /api/users/activity
Crear log de actividad manual

**Headers:**
```
Authorization: Bearer {token}
```

**Request:**
```json
{
  "accion": "documento_descargado",
  "descripcion": "Usuario descargó reporte mensual"
}
```

**Response:** 201 Created

## Eventos Publicados

El servicio publica los siguientes eventos a RabbitMQ:

- `user.profile_created`: Cuando se crea un perfil
- `user.profile_updated`: Cuando se actualiza un perfil

## Autenticación

Este servicio valida tokens JWT contra el auth-service. Todos los endpoints (excepto /health) requieren autenticación.

## Base de Datos

### Tablas

#### user_profiles
- id (SERIAL PRIMARY KEY)
- user_id (INTEGER UNIQUE)
- direccion, ciudad, pais
- fecha_nacimiento, genero
- telefono_alternativo
- contacto_emergencia_nombre, contacto_emergencia_telefono
- ocupacion, institucion
- notas_medicas
- preferencias (JSONB)
- created_at, updated_at

#### activity_logs
- id (SERIAL PRIMARY KEY)
- user_id (INTEGER)
- accion (VARCHAR)
- descripcion (TEXT)
- ip_address, user_agent
- created_at

## Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app
```

## Deployment

### Docker Build

```bash
docker build -t uce-user-service:latest .
```

### Docker Run

```bash
docker run -d \
  --name uce_user_service \
  --network uce_network \
  -p 8001:8001 \
  --env-file .env \
  uce-user-service:latest
```

## Dependencias con Otros Servicios

- **auth-service:** Validación de tokens JWT
- **RabbitMQ:** Publicación de eventos
- **PostgreSQL:** Almacenamiento de datos
- **Redis:** Caché (futuro)

## Monitoreo

- Health check: GET /health
- Metrics: (por implementar)
- Logs: stdout/stderr

## Troubleshooting

### Error: "Profile already exists"
- El usuario ya tiene un perfil creado
- Usar PUT /api/users/profile para actualizar

### Error: "Token validation failed"
- Verificar que el auth-service esté corriendo
- Verificar que el token sea válido
- Verificar JWT_SECRET_KEY coincida con auth-service

### Error: "Connection refused" (PostgreSQL)
- Verificar que PostgreSQL esté corriendo
- Verificar credenciales en .env
- Verificar red Docker

## Licencia

MIT
