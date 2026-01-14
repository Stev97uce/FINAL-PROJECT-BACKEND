# Analytics Service - UCE Psychology System

Analytics Service (Micro10) es el microservicio de **dashboards, métricas y visualizaciones** del Sistema de Gestión de Consultantes UCE. Proporciona APIs para consultar métricas agregadas, crear dashboards personalizados y visualizar datos analíticos del sistema.

## Tecnologías

- **Lenguaje:** Go 1.22
- **Framework:** Gin Web Framework
- **Base de Datos:** MongoDB 6.0
- **Caché:** Redis 7.0
- **Mensajería:** RabbitMQ 3.12
- **Contenedor:** Docker + Docker Compose
- **Autenticación:** JWT (golang-jwt/jwt/v5)

## Características Principales

- Almacenamiento de métricas en MongoDB
- Caché de consultas frecuentes en Redis
- Dashboards personalizables por usuario
- Métricas agregadas de todos los microservicios
- APIs RESTful con autenticación JWT
- Control de acceso basado en roles (RBAC)
- Health checks y monitoreo

## Arquitectura

```
┌─────────────────┐
│  Gin Router     │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Handler │
    └────┬────┘
         │
    ┌────┴────────┐
    │  Service    │
    └────┬────────┘
         │
    ┌────┴──────────┐
    │  Repository   │
    └────┬──────────┘
         │
    ┌────┴────┐
    │ MongoDB │
    │  Redis  │
    └─────────┘
```

## Estructura del Proyecto

```
Micro10_Analytics_Service/
├── cmd/
│   ├── main.go              # Entry point
│   └── main_test.go         # Tests
├── pkg/
│   ├── config/
│   │   └── config.go        # Configuration
│   └── database/
│       └── database.go      # MongoDB & Redis
├── internal/
│   ├── models/
│   │   ├── metric.go        # Data models
│   │   └── dto.go           # Request/Response DTOs
│   ├── repository/
│   │   ├── metric_repository.go
│   │   └── dashboard_repository.go
│   ├── services/
│   │   ├── metric_service.go
│   │   └── dashboard_service.go
│   ├── handlers/
│   │   ├── metric_handler.go
│   │   └── dashboard_handler.go
│   └── middleware/
│       ├── auth.go          # JWT authentication
│       └── logger.go        # Request logging
├── .env.example             # Environment template
├── Dockerfile
├── docker-compose.yml
├── go.mod
├── go.sum
├── generate_token.py        # JWT token generator
└── README.md
```

## Instalación

### Requisitos

- Go 1.22+
- Docker & Docker Compose
- MongoDB 6.0+ (si se ejecuta localmente)
- Redis 7.0+ (si se ejecuta localmente)

### 1. Clonar el Repositorio

```bash
git clone <repo-url>
cd FINAL-PROJECT-BACKEND/apps/Micro10_Analytics_Service
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env con las credenciales correctas
```

### 3. Opción A: Docker Compose (Recomendado)

```bash
docker-compose up -d
```

Esto levantará:
- Analytics Service en puerto 8009
- MongoDB en puerto 27017
- Redis en puerto 6379
- RabbitMQ en puerto 5672 (Management UI: 15672)

### 4. Opción B: Ejecución Local

```bash
# Instalar dependencias
go mod download

# Ejecutar
go run cmd/main.go
```

## API Endpoints

### Health Check

```http
GET /health
```

Respuesta:
```json
{
  "status": "healthy",
  "service": "Analytics Service",
  "version": "1.0.0",
  "mongodb": "connected",
  "redis": "connected"
}
```

### Métricas

#### Crear Métrica

```http
POST /api/v1/metrics
Authorization: Bearer {token}
Content-Type: application/json
```

Body:
```json
{
  "metric_type": "appointment_stats",
  "data": {
    "total": 150,
    "completed": 120,
    "cancelled": 20,
    "pending": 10
  },
  "period": "2026-01"
}
```

#### Obtener Métricas

```http
GET /api/v1/metrics?metric_type=appointment_stats&limit=100
Authorization: Bearer {token}
```

Filtros:
- `metric_type`: Tipo de métrica (requerido)
- `start_date`: Fecha inicio (YYYY-MM-DD)
- `end_date`: Fecha fin (YYYY-MM-DD)
- `limit`: Número de resultados (default: 100)

#### Obtener Última Métrica

```http
GET /api/v1/metrics/latest/:type
Authorization: Bearer {token}
```

#### Resumen Dashboard

```http
GET /api/v1/metrics/summary
Authorization: Bearer {token}
```

Respuesta:
```json
{
  "success": true,
  "data": {
    "total_appointments": 150,
    "total_users": 45,
    "total_patients": 80,
    "total_sessions": 120,
    "room_utilization": 75.5,
    "appointment_rate": 85.2,
    "active_users": 38,
    "completion_rate": 92.3
  }
}
```

### Dashboards

#### Crear Dashboard

```http
POST /api/v1/dashboards
Authorization: Bearer {token}
Content-Type: application/json
```

Body:
```json
{
  "name": "Dashboard Principal",
  "description": "Métricas generales del sistema",
  "is_public": false,
  "widgets": [
    {
      "id": "widget-1",
      "title": "Citas del Mes",
      "type": "bar_chart",
      "metric_type": "appointment_stats",
      "position": {
        "x": 0,
        "y": 0,
        "width": 6,
        "height": 4
      }
    }
  ]
}
```

#### Listar Dashboards

```http
GET /api/v1/dashboards
Authorization: Bearer {token}
```

#### Obtener Dashboard

```http
GET /api/v1/dashboards/:id
Authorization: Bearer {token}
```

#### Actualizar Dashboard

```http
PUT /api/v1/dashboards/:id
Authorization: Bearer {token}
Content-Type: application/json
```

#### Eliminar Dashboard

```http
DELETE /api/v1/dashboards/:id
Authorization: Bearer {token}
```

Roles requeridos: `admin`, `coordinador`

## Tipos de Métricas

### appointment_stats
Estadísticas de citas del sistema

```json
{
  "total": 150,
  "completed": 120,
  "cancelled": 20,
  "pending": 10,
  "by_status": {
    "scheduled": 50,
    "confirmed": 40,
    "completed": 120,
    "cancelled": 20
  }
}
```

### user_activity
Actividad de usuarios

```json
{
  "total_users": 45,
  "active_users": 38,
  "by_role": {
    "admin": 2,
    "coordinador": 3,
    "psicologo": 10,
    "estudiante": 30
  },
  "new_users": 5
}
```

### room_utilization
Utilización de consultorios

```json
{
  "total_rooms": 10,
  "available_rooms": 6,
  "occupied_rooms": 4,
  "utilization": 75.5
}
```

### session_stats
Estadísticas de sesiones clínicas

```json
{
  "total": 120,
  "completed": 115,
  "pending": 5,
  "average_duration": 60
}
```

### supervision_stats
Métricas de supervisión académica

```json
{
  "total_supervisions": 50,
  "pending_feedback": 10,
  "completed_feedback": 40
}
```

### system_performance
Rendimiento del sistema

```json
{
  "response_time_ms": 150,
  "requests_per_second": 45,
  "error_rate": 0.5
}
```

## Roles y Permisos

| Rol | Crear Métrica | Ver Métricas | Crear Dashboard | Ver Dashboard | Eliminar Dashboard |
|-----|---------------|--------------|-----------------|---------------|-------------------|
| admin | ✅ | ✅ | ✅ | ✅ | ✅ |
| coordinador | ✅ | ✅ | ✅ | ✅ | ✅ |
| psicologo | ❌ | ✅ | ✅ | ✅ | ❌ |
| estudiante | ❌ | ✅ | ✅ | ✅ (propios) | ❌ |

## Generar Token JWT

```bash
python generate_token.py
```

Esto generará tokens para 4 roles:
- admin
- coordinador
- psicologo
- estudiante

## Testing

```bash
# Ejecutar tests
go test ./... -v

# Con coverage
go test ./... -v -coverprofile=coverage.out

# Ver coverage
go tool cover -html=coverage.out
```

## Docker

### Build

```bash
docker build -t stevxd97/uce-analytics-service:latest .
```

### Run

```bash
docker run -d \
  -p 8009:8009 \
  -e MONGODB_HOST=mongodb \
  -e REDIS_HOST=redis \
  --name analytics-service \
  stevxd97/uce-analytics-service:latest
```

## Comandos Útiles

```bash
# Logs
docker-compose logs -f analytics-service

# Reiniciar servicio
docker-compose restart analytics-service

# Detener todo
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Ver estado
docker-compose ps
```

## Integración con Otros Servicios

Analytics Service consume datos de:
- Auth Service (8000): Métricas de usuarios
- Appointment Service (8003): Métricas de citas
- Room Service (8004): Utilización de salas
- Clinical Service (8005): Métricas de sesiones
- Supervision Service (8006): Métricas de supervisión
- Notification Service (8007): Estadísticas de notificaciones
- Reporting Service (8008): Métricas de reportes

## Variables de Entorno

```bash
# Server
APP_NAME=Analytics Service
APP_VERSION=1.0.0
ENVIRONMENT=development
PORT=8009
DEBUG=true

# MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USER=root
MONGODB_PASSWORD=root123
MONGODB_DATABASE=analytics_db
MONGODB_AUTH_SOURCE=admin

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256

# Services URLs
AUTH_SERVICE_URL=http://localhost:8000
APPOINTMENT_SERVICE_URL=http://localhost:8003
ROOM_SERVICE_URL=http://localhost:8004
# ...
```

## Troubleshooting

### Error: Cannot connect to MongoDB

```bash
# Verificar que MongoDB esté corriendo
docker-compose ps mongodb

# Ver logs de MongoDB
docker-compose logs mongodb
```

### Error: Cannot connect to Redis

```bash
# Verificar Redis
docker-compose ps redis

# Ver logs de Redis
docker-compose logs redis
```

### Error: Invalid JWT token

Verificar que:
1. El token esté en el header: `Authorization: Bearer {token}`
2. El secreto JWT sea el mismo en todos los servicios
3. El token no haya expirado

## Monitoreo

### Health Check

```bash
curl http://localhost:8009/health
```

### Métricas de Redis

```bash
# Conectar a Redis
docker exec -it uce_redis_analytics redis-cli

# Ver keys
> KEYS *

# Ver TTL de cache
> TTL metrics:appointment_stats:latest:100
```

### MongoDB Stats

```bash
# Conectar a MongoDB
docker exec -it uce_mongodb_analytics mongosh -u root -p root123

# Ver colecciones
use analytics_db
show collections

# Contar métricas
db.metrics.countDocuments()
```

## Contribuir

1. Fork el proyecto
2. Crear branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'feat: agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## Licencia

Universidad Central del Ecuador - Facultad de Psicología

## Autor

Sistema de Gestión de Consultantes UCE - Proyecto de Sistemas Distribuidos

## Versión

1.0.0 - Enero 2026
