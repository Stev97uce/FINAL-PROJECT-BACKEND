# Notification Service - UCE Psychology System

## 📋 Descripción

El Notification Service es el microservicio centralizado para gestión de notificaciones multi-canal (Email, WhatsApp, Internal, MQTT push) en el sistema de gestión de consultantes de la Universidad Central del Ecuador.

**Patrón arquitectónico:** KISS (Keep It Simple, Stupid) - Implementación simple y directa.

## ✨ Características

- ✅ **Multi-canal:** Email (SendGrid), WhatsApp (Twilio), notificaciones internas, MQTT push
- ✅ **Event-driven:** Consume eventos de Auth, Appointment, Clinical y Supervision services
- ✅ **Sistema de templates:** Jinja2 para personalización con variables
- ✅ **Rate limiting:** Control de frecuencia por canal (Redis)
- ✅ **Retry logic:** Reintentos automáticos con exponential backoff
- ✅ **User preferences:** Preferencias por usuario y canal
- ✅ **MongoDB + Beanie ODM:** Almacenamiento flexible de logs, templates y notificaciones internas
- ✅ **JWT authentication:** Integración con Auth Service
- ✅ **Health checks:** Monitoreo de salud del servicio

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python 3.11+
- **Framework:** FastAPI
- **Base de datos:** MongoDB 6.0 (Beanie ODM)
- **Cache:** Redis 7.0
- **Mensajería:** RabbitMQ 3.12 + MQTT (Mosquitto)
- **External APIs:**
  - SendGrid (Email SMTP)
  - Twilio (WhatsApp)
- **Testing:** pytest + pytest-asyncio

## 📡 Canales de Notificación

| Canal | Proveedor | Uso | Rate Limit |
|-------|-----------|-----|------------|
| **Email** | SendGrid SMTP | Verificación, confirmaciones, recordatorios | 100/usuario/día |
| **WhatsApp** | Twilio API | Confirmaciones de citas importantes | 50/usuario/día |
| **Internal** | MongoDB | Notificaciones in-app persistentes | 200/usuario/día |
| **MQTT** | Mosquitto | Push real-time a topics `uce/notifications/{user_id}` | Sin límite |

## 📥 Eventos Consumidos (RabbitMQ)

El servicio escucha y procesa los siguientes eventos:

| Evento | Origen | Acción |
|--------|--------|--------|
| `user.registered` | Auth Service | Envía email de verificación |
| `user.verified` | Auth Service | Envía email de bienvenida |
| `password.reset_requested` | Auth Service | Envía email con link de reset |
| `appointment.created` | Appointment Service | Confirmación email + WhatsApp + programa recordatorios |
| `appointment.confirmed` | Appointment Service | Notificación de confirmación |
| `appointment.cancelled` | Appointment Service | Notificación de cancelación |
| `clinical.session_recorded` | Clinical Service | Notifica a supervisor asignado |
| `supervision.feedback_added` | Supervision Service | Notifica a estudiante sobre feedback |

## 🗄️ Modelos de Datos (MongoDB)

### NotificationTemplate
```python
{
    "name": str,              # Unique: "email_verification"
    "channel": str,           # "email", "whatsapp", "internal", "mqtt"
    "event_type": str,        # "user.registered"
    "subject": str,           # Para emails (opcional)
    "body": str,              # Template Jinja2 con {{variables}}
    "variables": [str],       # ["user_name", "verification_link"]
    "active": bool,
    "created_at": datetime,
    "updated_at": datetime
}
```

### NotificationLog
```python
{
    "notification_id": str,    # UUID
    "user_id": int,
    "channel": str,
    "event_type": str,
    "status": str,             # "pending", "sent", "delivered", "failed"
    "template_id": str,
    "recipient": str,          # Email o teléfono
    "subject": str,
    "body": str,
    "sent_at": datetime,
    "delivered_at": datetime,
    "error_message": str,
    "retry_count": int,
    "max_retries": int,        # Default: 3
    "next_retry_at": datetime,
    "metadata": dict,
    "created_at": datetime
}
```

### UserPreferences
```python
{
    "user_id": int,            # Unique
    "email_enabled": bool,     # Default: true
    "whatsapp_enabled": bool,
    "internal_enabled": bool,
    "push_enabled": bool,
    "quiet_hours_enabled": bool,
    "quiet_hours_start": str,  # "22:00"
    "quiet_hours_end": str,    # "08:00"
    "created_at": datetime,
    "updated_at": datetime
}
```

### InternalNotification
```python
{
    "user_id": int,
    "title": str,
    "body": str,
    "category": str,           # "appointment", "supervision", "system"
    "priority": str,           # "low", "medium", "high"
    "is_read": bool,
    "read_at": datetime,
    "action_url": str,         # Link para "Ver detalles"
    "metadata": dict,
    "created_at": datetime,
    "expires_at": datetime     # TTL para auto-limpieza (30 días)
}
```

## 🔌 API Endpoints

### Usuario (Autenticado)

#### Notificaciones Internas
```http
GET    /api/v1/notifications              # Listar notificaciones
GET    /api/v1/notifications/{id}         # Detalle de notificación
GET    /api/v1/notifications/unread-count # Contador de no leídas
PATCH  /api/v1/notifications/{id}/read    # Marcar como leída
PATCH  /api/v1/notifications/read-all     # Marcar todas como leídas
DELETE /api/v1/notifications/{id}         # Eliminar notificación
```

#### Preferencias
```http
GET    /api/v1/preferences                # Obtener preferencias
PUT    /api/v1/preferences                # Actualizar preferencias
```

### Admin (Rol: administrador)

#### Templates
```http
GET    /api/v1/admin/templates            # Listar templates
POST   /api/v1/admin/templates            # Crear template
PUT    /api/v1/admin/templates/{id}       # Actualizar template
```

#### Envío Manual
```http
POST   /api/v1/admin/send                 # Enviar notificación manual
```

#### Logs y Estadísticas
```http
GET    /api/v1/admin/delivery-logs        # Historial de envíos
GET    /api/v1/admin/stats                # Estadísticas
```

### Sistema
```http
GET    /health                            # Health check
GET    /                                  # Root info
```

## 🔧 Variables de Entorno

```bash
# Service
SERVICE_NAME=notification-service
SERVICE_PORT=8007
DEBUG=False

# MongoDB
MONGODB_URL=mongodb://root:rootpassword@mongodb:27017
MONGODB_DB_NAME=notification_db

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_EXCHANGE=uce_events

# MQTT (Opcional para desarrollo local)
MQTT_BROKER_HOST=mqtt
MQTT_BROKER_PORT=1883
MQTT_CLIENT_ID=notification-service

# SendGrid (Email) - Configurar con credenciales reales
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@uce.edu.ec
SENDGRID_FROM_NAME=UCE Psychology System

# Twilio (WhatsApp) - Configurar con credenciales reales
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_WHATSAPP_FROM=whatsapp:+1234567890

# Auth Service Integration
AUTH_SERVICE_URL=http://auth-service:8000
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# Rate Limiting
RATE_LIMIT_EMAIL_PER_USER_DAY=100
RATE_LIMIT_WHATSAPP_PER_USER_DAY=50
RATE_LIMIT_INTERNAL_PER_USER_DAY=200

# Retry Configuration
MAX_RETRY_ATTEMPTS=3

# Notification Expiry
INTERNAL_NOTIFICATION_EXPIRY_DAYS=30
```

## 🐳 Docker

### Construir imagen
```bash
cd apps/Micro8_Notification_Service
docker build -t stevxd97/uce-notification-service:latest .
```

### Ejecutar con docker-compose (desde raíz del proyecto)
```bash
# Levantar todas las dependencias + notification service
docker-compose up -d mongodb redis rabbitmq notification-service

# Ver logs
docker-compose logs -f notification-service

# Detener
docker-compose stop notification-service
```

### Health Check
```bash
curl http://localhost:8007/health
```

## 🧪 Testing

### Ejecutar tests
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_models.py -v
pytest tests/test_api.py -v
```

### Tests incluidos
- ✅ `test_models.py` - Validación de modelos Beanie
- ✅ `test_schemas.py` - Validación de schemas Pydantic
- ✅ `test_api.py` - Tests de endpoints HTTP
- ✅ `test_services.py` - Tests de servicios (template rendering, etc.)

## 📊 Integraciones

### Con otros microservicios

| Microservicio | Relación | Eventos |
|---------------|----------|---------|
| Auth Service | Consume eventos | user.registered, user.verified, password.reset_requested |
| Appointment Service | Consume eventos | appointment.created, appointment.confirmed, appointment.cancelled |
| Clinical Service | Consume eventos | clinical.session_recorded |
| Supervision Service | Consume eventos | supervision.feedback_added |

### APIs Externas

#### SendGrid (Email)
- **Uso:** Envío de emails transaccionales
- **Docs:** https://sendgrid.com/docs/api-reference/
- **Configuración:** Requiere API Key
- **Límites:** Según plan (Free tier: 100 emails/día)

#### Twilio (WhatsApp)
- **Uso:** Mensajes WhatsApp
- **Docs:** https://www.twilio.com/docs/whatsapp
- **Configuración:** Requiere Account SID, Auth Token y WhatsApp número aprobado
- **Límites:** Según plan y plantillas aprobadas

## 📁 Estructura del Proyecto

```
Micro8_Notification_Service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Settings (Pydantic)
│   ├── database.py             # MongoDB + Redis connection
│   ├── dependencies.py         # JWT auth dependencies
│   ├── models.py               # Beanie ODM models
│   ├── schemas.py              # Pydantic schemas
│   ├── consumer.py             # RabbitMQ event consumer
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py           # Health check
│   │   ├── notifications.py   # User notifications endpoints
│   │   ├── preferences.py     # User preferences endpoints
│   │   └── admin.py            # Admin endpoints (templates, logs, stats)
│   └── services/
│       ├── __init__.py
│       ├── email_service.py    # SendGrid integration
│       ├── whatsapp_service.py # Twilio integration
│       ├── mqtt_service.py     # MQTT publisher
│       ├── template_service.py # Jinja2 rendering
│       └── notification_service.py  # Core business logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Test configuration
│   ├── test_models.py
│   ├── test_schemas.py
│   ├── test_api.py
│   └── test_services.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🚀 Deployment

### Local Development
```bash
# 1. Levantar infraestructura
docker-compose up -d mongodb redis rabbitmq

# 2. Instalar dependencias
cd apps/Micro8_Notification_Service
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 4. Ejecutar servicio
uvicorn app.main:app --reload --port 8007
```

### Docker Production
```bash
# 1. Build
docker build -t stevxd97/uce-notification-service:v1.0.0 .

# 2. Tag
docker tag stevxd97/uce-notification-service:v1.0.0 stevxd97/uce-notification-service:latest

# 3. Push to DockerHub
docker push stevxd97/uce-notification-service:v1.0.0
docker push stevxd97/uce-notification-service:latest

# 4. Deploy with docker-compose
docker-compose up -d notification-service
```

## 📝 Ejemplo de Uso

### 1. Enviar Notificación Manual (Admin)
```bash
curl -X POST http://localhost:8007/api/v1/admin/send \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "channel": "email",
    "template_name": "appointment_confirmation",
    "variables": {
      "user_name": "Juan Pérez",
      "appointment_date": "2024-01-20",
      "appointment_time": "10:00"
    },
    "recipient": "juan.perez@example.com"
  }'
```

### 2. Listar Notificaciones Internas (Usuario)
```bash
curl -X GET http://localhost:8007/api/v1/notifications \
  -H "Authorization: Bearer <user_token>"
```

### 3. Actualizar Preferencias
```bash
curl -X PUT http://localhost:8007/api/v1/preferences \
  -H "Authorization: Bearer <user_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email_enabled": true,
    "whatsapp_enabled": false,
    "quiet_hours_enabled": true,
    "quiet_hours_start": "22:00",
    "quiet_hours_end": "08:00"
  }'
```

## 🔍 Troubleshooting

### MongoDB no conecta
```bash
# Verificar que MongoDB está corriendo
docker ps | grep mongodb

# Ver logs de MongoDB
docker logs uce_mongodb

# Verificar credenciales en .env
```

### SendGrid no envía emails
```bash
# Verificar API Key en .env
echo $SENDGRID_API_KEY

# Verificar límites de cuenta SendGrid
# Free tier: 100 emails/día

# Ver logs del servicio
docker logs uce_notification_service | grep SendGrid
```

### RabbitMQ no consume eventos
```bash
# Verificar que RabbitMQ está corriendo
docker ps | grep rabbitmq

# Ver colas en RabbitMQ Management
# http://localhost:15672 (guest/guest)

# Verificar binding de routing keys
```

## 📚 Recursos

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Beanie ODM:** https://beanie-odm.dev/
- **SendGrid API:** https://sendgrid.com/docs/
- **Twilio WhatsApp:** https://www.twilio.com/docs/whatsapp
- **MQTT Paho:** https://www.eclipse.org/paho/
- **MongoDB:** https://www.mongodb.com/docs/

## 📄 Licencia

Universidad Central del Ecuador - Proyecto Académico 2025

---

**Desarrollado con patrón KISS para máxima simplicidad y mantenibilidad** 🚀
