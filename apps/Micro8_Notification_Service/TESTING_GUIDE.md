# Notification Service Testing Guide

## 🧪 Guía de Testing - Notification Service

Este documento proporciona una guía paso a paso para probar el Notification Service.

## Prerequisitos

1. **Infraestructura corriendo:**
```bash
docker-compose up -d mongodb redis rabbitmq
```

2. **Servicio corriendo:**
```bash
docker-compose up -d notification-service
# O localmente:
cd apps/Micro8_Notification_Service
uvicorn app.main:app --reload --port 8007
```

3. **Tokens JWT:**
```bash
python get_tokens.py
```

Copiar los tokens generados para usarlos en las pruebas.

## 📋 Tests Básicos

### 1. Health Check
```bash
curl http://localhost:8007/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "service": "notification-service",
  "timestamp": "2024-01-12T10:30:00"
}
```

### 2. Root Endpoint
```bash
curl http://localhost:8007/
```

**Respuesta esperada:**
```json
{
  "service": "notification-service",
  "version": "1.0.0",
  "status": "running"
}
```

## 👤 Tests de Usuario (Autenticado)

Usar el **USER TOKEN** generado.

### 3. Listar Notificaciones Internas
```bash
curl -X GET http://localhost:8007/api/v1/notifications \
  -H "Authorization: Bearer <USER_TOKEN>"
```

### 4. Contador de No Leídas
```bash
curl -X GET http://localhost:8007/api/v1/notifications/unread-count \
  -H "Authorization: Bearer <USER_TOKEN>"
```

### 5. Obtener Preferencias
```bash
curl -X GET http://localhost:8007/api/v1/preferences \
  -H "Authorization: Bearer <USER_TOKEN>"
```

### 6. Actualizar Preferencias
```bash
curl -X PUT http://localhost:8007/api/v1/preferences \
  -H "Authorization: Bearer <USER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "email_enabled": true,
    "whatsapp_enabled": true,
    "internal_enabled": true,
    "push_enabled": true,
    "quiet_hours_enabled": false
  }'
```

### 7. Marcar Todas como Leídas
```bash
curl -X PATCH http://localhost:8007/api/v1/notifications/read-all \
  -H "Authorization: Bearer <USER_TOKEN>"
```

## 👨‍💼 Tests de Admin

Usar el **ADMIN TOKEN** generado.

### 8. Crear Templates Predeterminados
```bash
# Desde el directorio del servicio
python create_templates.py
```

### 9. Listar Templates
```bash
curl -X GET http://localhost:8007/api/v1/admin/templates \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

### 10. Crear Nuevo Template
```bash
curl -X POST http://localhost:8007/api/v1/admin/templates \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_template",
    "channel": "internal",
    "event_type": "test.event",
    "subject": "Test Notification",
    "body": "Hello {{user_name}}, this is a test.",
    "variables": ["user_name"],
    "active": true
  }'
```

### 11. Enviar Notificación Manual (Email)
```bash
curl -X POST http://localhost:8007/api/v1/admin/send \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "channel": "email",
    "template_name": "welcome_email",
    "variables": {
      "user_name": "Juan Pérez"
    },
    "recipient": "test@example.com"
  }'
```

**Nota:** Para que el email se envíe realmente, debes configurar `SENDGRID_API_KEY` en el .env

### 12. Enviar Notificación Interna
```bash
curl -X POST http://localhost:8007/api/v1/admin/send \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "channel": "internal",
    "template_name": "test_template",
    "variables": {
      "user_name": "Juan Pérez"
    }
  }'
```

### 13. Ver Logs de Envío
```bash
curl -X GET "http://localhost:8007/api/v1/admin/delivery-logs?limit=10" \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

### 14. Ver Estadísticas
```bash
curl -X GET http://localhost:8007/api/v1/admin/stats \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

## 📡 Tests de Eventos RabbitMQ

### 15. Simular Evento user.registered

**Opción A: Usar Auth Service** (si está corriendo)
```bash
# Registrar un nuevo usuario en Auth Service
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nuevo@example.com",
    "password": "Password123!",
    "nombres": "Nuevo",
    "apellidos": "Usuario",
    "cedula": "1234567890",
    "telefono": "+593999999999",
    "rol": "consultante"
  }'
```

**Opción B: Publicar evento manualmente**
```python
# Script Python para publicar evento
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

event = {
    "user_id": 999,
    "email": "test@example.com",
    "nombres": "Test User",
    "rol": "consultante",
    "telefono": "+593999999999"
}

channel.basic_publish(
    exchange='uce_events',
    routing_key='user.registered',
    body=json.dumps(event)
)

print("Event published!")
connection.close()
```

### 16. Verificar Consumo de Eventos

Ver logs del servicio:
```bash
docker logs -f uce_notification_service
```

Buscar líneas como:
```
INFO - Received event: user.registered
INFO - Sent verification email to user 999
```

## 🧪 Tests Unitarios (pytest)

### 17. Ejecutar Tests
```bash
# En el directorio del servicio
pytest

# Con verbose
pytest -v

# Con coverage
pytest --cov=app --cov-report=html

# Solo un archivo
pytest tests/test_models.py -v
```

## 🔍 Verificación de Datos en MongoDB

### 18. Verificar Templates Creados
```bash
docker exec -it uce_mongodb mongosh -u root -p rootpassword

use notification_db
db.notification_templates.find().pretty()
```

### 19. Verificar Logs de Envío
```bash
db.notification_logs.find().pretty()
```

### 20. Verificar Notificaciones Internas
```bash
db.internal_notifications.find({user_id: 2}).pretty()
```

### 21. Verificar Preferencias de Usuario
```bash
db.user_preferences.find().pretty()
```

## 📊 Monitoreo

### 22. Ver Logs en Tiempo Real
```bash
# Docker
docker logs -f uce_notification_service

# Local
# Los logs se imprimen en la consola donde ejecutaste uvicorn
```

### 23. Verificar Conexiones

**RabbitMQ Management:**
- URL: http://localhost:15672
- User/Pass: guest/guest
- Ver: Queues → `notification_service_queue`

**Adminer (MongoDB):**
- URL: http://localhost:8080
- System: MongoDB
- Server: mongodb
- User: root
- Password: rootpassword

## ⚠️ Troubleshooting

### Error: "MongoDB connection failed"
```bash
# Verificar que MongoDB está corriendo
docker ps | grep mongodb

# Verificar logs
docker logs uce_mongodb

# Reiniciar MongoDB
docker-compose restart mongodb
```

### Error: "RabbitMQ connection failed"
```bash
# Verificar que RabbitMQ está corriendo
docker ps | grep rabbitmq

# Reiniciar RabbitMQ
docker-compose restart rabbitmq
```

### Error: "SendGrid API error"
```bash
# Verificar API Key
# 1. Ve a .env y verifica SENDGRID_API_KEY
# 2. Verifica que la API Key es válida en SendGrid dashboard
# 3. Para testing sin SendGrid, usa canal "internal" o "mqtt"
```

## ✅ Checklist de Testing Completo

- [ ] Health check funciona
- [ ] Root endpoint funciona
- [ ] Listar notificaciones (usuario autenticado)
- [ ] Obtener preferencias (usuario)
- [ ] Actualizar preferencias (usuario)
- [ ] Listar templates (admin)
- [ ] Crear template (admin)
- [ ] Enviar notificación manual (admin)
- [ ] Ver logs de envío (admin)
- [ ] Ver estadísticas (admin)
- [ ] Templates predeterminados creados
- [ ] Evento user.registered consumido
- [ ] Notificación interna creada
- [ ] Tests unitarios pasan (pytest)
- [ ] MongoDB almacena datos correctamente
- [ ] RabbitMQ consumer funciona

## 📝 Notas Importantes

1. **SendGrid y Twilio:** Para testing real de emails y WhatsApp, necesitas configurar credenciales válidas en .env
2. **Rate Limiting:** Los límites por defecto son 100 emails/día, 50 WhatsApp/día
3. **MQTT:** Opcional para desarrollo local, pero necesario en producción
4. **Templates:** Deben existir antes de enviar notificaciones (ejecutar `create_templates.py`)
5. **Tokens:** Los tokens expiran en 24 horas, regenerar si es necesario

---

**¡Happy Testing!** 🚀
