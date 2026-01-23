# Clinical Service - UCE Mental Health Platform

Microservicio de Gestión Clínica para la plataforma de salud mental de la UCE.

## Descripción

El Clinical Service gestiona los registros clínicos, sesiones terapéuticas, notas de sesión y objetivos terapéuticos. Integra MongoDB para almacenamiento flexible de datos clínicos y emite eventos para integración con otros servicios.

## Características

- ✅ Gestión de expedientes clínicos
- ✅ Registro de sesiones terapéuticas
- ✅ Notas de sesión detalladas
- ✅ Objetivos terapéuticos con seguimiento
- ✅ Autenticación JWT
- ✅ MongoDB para almacenamiento flexible
- ✅ Redis para caché
- ✅ RabbitMQ para eventos
- ✅ API RESTful con FastAPI
- ✅ Documentación automática con Swagger

## Tecnologías

- **Python**: 3.11+
- **Framework**: FastAPI 0.109.0
- **Base de datos**: MongoDB 6.0
- **Caché**: Redis 7
- **Mensajería**: RabbitMQ 3.12
- **ODM**: Beanie 1.24.0
- **Autenticación**: JWT (PyJWT 2.8.0)

## Requisitos Previos

- Python 3.11 o superior
- Docker y Docker Compose
- MongoDB 6.0
- Redis 7
- RabbitMQ 3.12

## Instalación

### 1. Clonar el repositorio

```bash
cd apps/Micro6_Clinical_Service
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para desarrollo
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

## Configuración

### Variables de Entorno

```env
# Service
SERVICE_NAME=clinical-service
PORT=8005
DEBUG=false

# MongoDB
MONGODB_URL=mongodb://root:rootpassword@localhost:27017
MONGODB_DB_NAME=clinical_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_EXCHANGE=uce_events

# JWT
SECRET_KEY=Q7v1P7Rp-vglhy04pduFZ0LeHW-_z9eBqSPwEV_2Ea4
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Uso

### Desarrollo Local

**IMPORTANTE**: Este servicio se ejecuta integrado con el resto de microservicios. Usa el docker-compose.yml principal en la raíz del proyecto.

```bash
# Desde la raíz del proyecto (FINAL-PROJECT-BACKEND)
# Levantar todos los servicios
docker-compose up -d

# O solo el Clinical Service con sus dependencias
docker-compose up -d mongodb redis rabbitmq clinical_service

# Ver logs del Clinical Service
docker-compose logs -f clinical_service

# Detener el servicio
docker-compose stop clinical_service
```

### Desarrollo sin Docker (opcional)

Si deseas ejecutar solo este servicio localmente para desarrollo:

```bash
cd apps/Micro6_Clinical_Service

# Asegurarse de que MongoDB, Redis y RabbitMQ estén corriendo
# (puedes levantarlos desde el docker-compose principal)
docker-compose up -d mongodb redis rabbitmq

# Ejecutar el servicio
python -m uvicorn app.main:app --reload --port 8005

# O directamente
python app/main.py
```

### Docker (Construcción manual - no recomendado)

```bash
# Desde el directorio del microservicio
docker build -t clinical-service .

# Ejecutar contenedor (asegúrate de que las dependencias estén corriendo)
docker run -p 8005:8005 --env-file .env --network uce_network clinical-service
```

## API Endpoints

### Clinical Records

- `POST /api/v1/clinical-records` - Crear expediente clínico
- `GET /api/v1/clinical-records` - Listar expedientes
- `GET /api/v1/clinical-records/{id}` - Obtener expediente
- `PUT /api/v1/clinical-records/{id}` - Actualizar expediente
- `PATCH /api/v1/clinical-records/{id}/close` - Cerrar expediente
- `DELETE /api/v1/clinical-records/{id}` - Eliminar expediente

### Sessions

- `POST /api/v1/sessions` - Crear sesión
- `GET /api/v1/sessions` - Listar sesiones
- `GET /api/v1/sessions/{id}` - Obtener sesión
- `PUT /api/v1/sessions/{id}` - Actualizar sesión
- `DELETE /api/v1/sessions/{id}` - Eliminar sesión

### Session Notes

- `POST /api/v1/session-notes` - Crear nota de sesión
- `GET /api/v1/session-notes` - Listar notas
- `GET /api/v1/session-notes/{id}` - Obtener nota
- `PUT /api/v1/session-notes/{id}` - Actualizar nota
- `PATCH /api/v1/session-notes/{id}/feedback` - Agregar feedback de supervisor
- `DELETE /api/v1/session-notes/{id}` - Eliminar nota

### Therapeutic Goals

- `POST /api/v1/therapeutic-goals` - Crear objetivo terapéutico
- `GET /api/v1/therapeutic-goals` - Listar objetivos
- `GET /api/v1/therapeutic-goals/{id}` - Obtener objetivo
- `PUT /api/v1/therapeutic-goals/{id}` - Actualizar objetivo
- `POST /api/v1/therapeutic-goals/{id}/progress` - Agregar nota de progreso
- `DELETE /api/v1/therapeutic-goals/{id}` - Eliminar objetivo

### Salud

- `GET /health` - Estado del servicio
- `GET /` - Información del servicio

## Documentación API

Una vez iniciado el servicio, accede a:

- **Swagger UI**: http://localhost:8005/docs
- **ReDoc**: http://localhost:8005/redoc

## Autenticación

El servicio utiliza JWT para autenticación. Para generar un token de prueba:

```bash
python generate_token.py
```

Usa el token en el header de tus peticiones:

```
Authorization: Bearer <tu_token>
```

## Roles

- **admin**: Acceso completo
- **professional**: Crear y modificar registros clínicos
- **student**: Crear y ver registros clínicos
- **patient**: Ver solo sus propios registros (futuro)

## Modelos de Datos

### Clinical Record
- patient_id
- therapist_id
- status (activo, cerrado, en_pausa)
- diagnosis
- treatment_plan
- additional_notes

### Session
- clinical_record_id
- appointment_id
- session_number
- session_date
- duration_minutes
- session_type (individual, grupal, familiar)
- attendance_status

### Session Note
- session_id
- author_id
- presenting_problem
- session_summary
- techniques_used
- interventions
- homework_assigned
- progress_assessment
- next_session_plan

### Therapeutic Goal
- clinical_record_id
- goal_description
- target_date
- status (pending, in_progress, achieved, modified)
- progress_notes

## Eventos RabbitMQ

### Eventos Publicados

- `clinical.record.created` - Expediente creado
- `clinical.session.recorded` - Sesión registrada
- `clinical.note.created` - Nota de sesión creada
- `clinical.goal.achieved` - Objetivo alcanzado

## Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_clinical_records.py -v
```

## Desarrollo

### Formato de código

```bash
# Formatear con Black
black app/

# Linting con Flake8
flake8 app/

# Type checking con mypy
mypy app/
```

### Estructura del Proyecto

```
Micro6_Clinical_Service/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación FastAPI
│   ├── config.py            # Configuración
│   ├── database.py          # Conexiones MongoDB/Redis
│   ├── models.py            # Modelos Beanie
│   ├── schemas.py           # Esquemas Pydantic
│   ├── security.py          # JWT y autenticación
│   ├── dependencies.py      # Dependencias compartidas
│   ├── events.py            # RabbitMQ events
│   └── routes/
│       ├── __init__.py
│       ├── clinical_records.py
│       ├── sessions.py
│       ├── session_notes.py
│       └── therapeutic_goals.py
├── tests/
│   └── ...
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── generate_token.py
└── README.md
```

## Troubleshooting

### Error de conexión a MongoDB

```bash
# Verificar que MongoDB esté corriendo
docker ps | grep mongo

# Ver logs de MongoDB
docker logs uce_clinical_mongodb
```

### Error de conexión a RabbitMQ

```bash
# Verificar RabbitMQ
docker ps | grep rabbitmq

# Acceder a la consola de gestión
http://localhost:15672 (guest/guest)
```

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto es parte del sistema UCE Mental Health Platform.

## Contacto

Equipo de Desarrollo - UCE
