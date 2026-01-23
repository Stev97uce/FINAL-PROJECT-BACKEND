# Supervision Service - UCE Psychology System

## Descripción

El Supervision Service gestiona la supervisión académica entre estudiantes de psicología y supervisores. Proporciona retroalimentación estructurada sobre notas de sesiones clínicas, gestiona asignaciones de supervisión y programación de reuniones de supervisión.

## Características

- ✅ Gestión de asignaciones estudiante-supervisor
- ✅ Retroalimentación estructurada sobre notas clínicas
- ✅ Programación de sesiones de supervisión
- ✅ Integración con Clinical Service (consume eventos)
- ✅ Publicación de eventos para Notification Service
- ✅ Autenticación JWT con control de acceso basado en roles
- ✅ PostgreSQL para almacenamiento relacional
- ✅ Redis para caché
- ✅ RabbitMQ para comunicación asíncrona
- ✅ Principios SOLID aplicados

## Stack Tecnológico

- **Lenguaje:** Python 3.11
- **Framework:** FastAPI 0.115.6
- **Base de Datos:** PostgreSQL 14
- **Caché:** Redis 7
- **Message Broker:** RabbitMQ 3.12
- **ORM:** SQLAlchemy 2.0.36
- **Puerto:** 8006

## Arquitectura SOLID

Este servicio aplica los principios SOLID:

### Single Responsibility Principle (SRP)
- Cada modelo tiene una responsabilidad clara:
  - `SupervisionAssignment`: Gestión de asignaciones
  - `SupervisionFeedback`: Almacenamiento de retroalimentación
  - `SupervisionSession`: Programación de reuniones
- Cada ruta maneja un solo tipo de recurso

### Open/Closed Principle (OCP)
- Sistema extensible para nuevos roles sin modificar código existente
- Nuevas rutas pueden agregarse sin afectar las existentes

### Liskov Substitution Principle (LSP)
- Los schemas Pydantic pueden sustituirse entre operaciones CRUD
- Response models heredan correctamente de BaseModel

### Interface Segregation Principle (ISP)
- Schemas específicos para cada operación (Create, Update, Response)
- No hay clientes obligados a depender de interfaces que no usan

### Dependency Inversion Principle (DIP)
- Dependencias inyectadas vía FastAPI Depends
- Servicios dependen de abstracciones (Session de SQLAlchemy)
- Eventos desacoplados mediante RabbitMQ

## Modelos de Datos

### SupervisionAssignment
Asignación de estudiante a supervisor
```python
{
    "id": int,
    "student_user_id": int,        # ID del estudiante (User Service)
    "supervisor_user_id": int,     # ID del supervisor (User Service)
    "specialty_area": str,          # Área de especialidad
    "start_date": datetime,
    "end_date": datetime,
    "status": str,                  # active, completed, cancelled
    "notes": str
}
```

### SupervisionFeedback
Retroalimentación del supervisor sobre nota de sesión
```python
{
    "id": int,
    "assignment_id": int,
    "session_note_id": str,         # MongoDB ObjectId del Clinical Service
    "supervisor_id": int,
    "student_id": int,
    "feedback_text": str,
    "strengths": List[str],
    "areas_for_improvement": List[str],
    "recommendations": str,
    "rating": int,                  # 1-5
    "is_read_by_student": bool,
    "read_at": datetime,
    "reviewed_at": datetime
}
```

### SupervisionSession
Sesión de supervisión programada
```python
{
    "id": int,
    "assignment_id": int,
    "scheduled_date": datetime,
    "duration_minutes": int,
    "topic": str,
    "meeting_notes": str,
    "status": str,                  # scheduled, completed, cancelled, rescheduled
    "attendance_confirmed": bool
}
```

## API Endpoints

### Supervision Assignments

| Método | Endpoint | Descripción | Rol Requerido |
|--------|----------|-------------|---------------|
| POST | `/api/v1/assignments` | Crear asignación | admin, coordinador |
| GET | `/api/v1/assignments` | Listar asignaciones | todos (filtrado por rol) |
| GET | `/api/v1/assignments/{id}` | Obtener asignación | todos (permisos verificados) |
| PUT | `/api/v1/assignments/{id}` | Actualizar asignación | admin, coordinador |
| PATCH | `/api/v1/assignments/{id}/deactivate` | Desactivar asignación | admin, coordinador |
| DELETE | `/api/v1/assignments/{id}` | Eliminar asignación | admin |

### Supervision Feedback

| Método | Endpoint | Descripción | Rol Requerido |
|--------|----------|-------------|---------------|
| POST | `/api/v1/feedback` | Crear retroalimentación | psicologo_supervisor, admin |
| GET | `/api/v1/feedback` | Listar retroalimentación | todos (filtrado por rol) |
| GET | `/api/v1/feedback/{id}` | Obtener retroalimentación | todos (permisos verificados) |
| PUT | `/api/v1/feedback/{id}` | Actualizar retroalimentación | psicologo_supervisor, admin |
| PATCH | `/api/v1/feedback/{id}/mark-read` | Marcar como leído | estudiante, admin |
| DELETE | `/api/v1/feedback/{id}` | Eliminar retroalimentación | admin |

### Supervision Sessions

| Método | Endpoint | Descripción | Rol Requerido |
|--------|----------|-------------|---------------|
| POST | `/api/v1/sessions` | Crear sesión | psicologo_supervisor, admin |
| GET | `/api/v1/sessions` | Listar sesiones | todos (filtrado por rol) |
| GET | `/api/v1/sessions/{id}` | Obtener sesión | todos (permisos verificados) |
| PUT | `/api/v1/sessions/{id}` | Actualizar sesión | psicologo_supervisor, admin |
| PATCH | `/api/v1/sessions/{id}/confirm` | Confirmar asistencia | estudiante, psicologo_supervisor, admin |
| PATCH | `/api/v1/sessions/{id}/complete` | Marcar como completada | psicologo_supervisor, admin |
| DELETE | `/api/v1/sessions/{id}` | Eliminar sesión | psicologo_supervisor, admin |

### Health Check

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Estado del servicio |
| GET | `/` | Información del servicio |

## Eventos

### Eventos Consumidos

#### clinical.session_recorded
Emitido por Clinical Service cuando un estudiante completa una nota de sesión.

**Payload:**
```json
{
    "session_note_id": "string",
    "session_id": "string",
    "student_id": int,
    "clinical_record_id": "string",
    "recorded_at": "datetime"
}
```

**Acción:** Identifica el supervisor asignado al estudiante para notificarle.

### Eventos Publicados

#### supervision.feedback_added
Emitido cuando un supervisor agrega retroalimentación.

**Payload:**
```json
{
    "feedback_id": int,
    "session_note_id": "string",
    "supervisor_id": int,
    "student_id": int,
    "assignment_id": int,
    "reviewed_at": "datetime"
}
```

**Consumido por:**
- Clinical Service: Vincula feedback a session_note
- Notification Service: Notifica al estudiante

## Integración con Clinical Service

El Supervision Service se integra con el Clinical Service de las siguientes formas:

1. **Consumo de Eventos:**
   - Escucha `clinical.session_recorded` para identificar notas nuevas
   - Encuentra supervisor asignado automáticamente

2. **Actualización de Notas:**
   - Al crear feedback, actualiza `session_note.supervisor_feedback_id` en Clinical Service
   - Usa HTTP PATCH a `http://clinical_service:8005/api/v1/session-notes/{id}/feedback`

3. **Publicación de Eventos:**
   - Emite `supervision.feedback_added` para que Clinical Service vincule feedback

## Instalación y Configuración

### Variables de Entorno

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@postgresql:5432/supervision_db

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_EXCHANGE=uce_events

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Con Docker Compose

```bash
# Levantar servicio
docker-compose up -d supervision_service

# Ver logs
docker-compose logs -f supervision_service

# Reconstruir
docker-compose build supervision_service
docker-compose up -d supervision_service
```

### Desarrollo Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
.\venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar servicio
uvicorn app.main:app --reload --port 8006
```

## Testing

### Generar Tokens JWT

```bash
python generate_token.py
```

Esto generará tokens para:
- Admin
- Supervisor
- Estudiante
- Coordinador

### Pruebas con Postman

#### 1. Crear Asignación Supervisor-Estudiante

```http
POST http://localhost:8006/api/v1/assignments
Authorization: Bearer {COORDINADOR_TOKEN}
Content-Type: application/json

{
    "student_user_id": 3,
    "supervisor_user_id": 2,
    "specialty_area": "Psicología Clínica",
    "start_date": "2025-01-15T00:00:00",
    "notes": "Supervisión para prácticas clínicas"
}
```

#### 2. Crear Retroalimentación sobre Nota de Sesión

```http
POST http://localhost:8006/api/v1/feedback
Authorization: Bearer {SUPERVISOR_TOKEN}
Content-Type: application/json

{
    "assignment_id": 1,
    "session_note_id": "6964fe374f1147f710343c14",
    "student_id": 3,
    "feedback_text": "Excelente trabajo en la aplicación de técnicas cognitivas. Se observa buen rapport con el consultante.",
    "strengths": [
        "Buena escucha activa",
        "Aplicación correcta de técnicas",
        "Empatía con el consultante"
    ],
    "areas_for_improvement": [
        "Profundizar en la exploración de emociones",
        "Mejorar el registro de observaciones no verbales"
    ],
    "recommendations": "Revisar literatura sobre técnicas de exploración emocional",
    "rating": 4
}
```

#### 3. Listar Asignaciones (Estudiante)

```http
GET http://localhost:8006/api/v1/assignments
Authorization: Bearer {STUDENT_TOKEN}
```

#### 4. Marcar Feedback como Leído

```http
PATCH http://localhost:8006/api/v1/feedback/1/mark-read
Authorization: Bearer {STUDENT_TOKEN}
```

#### 5. Programar Sesión de Supervisión

```http
POST http://localhost:8006/api/v1/sessions
Authorization: Bearer {SUPERVISOR_TOKEN}
Content-Type: application/json

{
    "assignment_id": 1,
    "scheduled_date": "2025-01-20T10:00:00",
    "duration_minutes": 60,
    "topic": "Revisión de casos clínicos y retroalimentación"
}
```

## Base de Datos

### Crear Base de Datos

```sql
-- Conectar a PostgreSQL
CREATE DATABASE supervision_db;

-- Las tablas se crean automáticamente al iniciar el servicio
```

### Estructura de Tablas

#### supervision_assignments
```sql
CREATE TABLE supervision_assignments (
    id SERIAL PRIMARY KEY,
    student_user_id INTEGER NOT NULL,
    supervisor_user_id INTEGER NOT NULL,
    specialty_area VARCHAR(100),
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_student_user ON supervision_assignments(student_user_id);
CREATE INDEX idx_supervisor_user ON supervision_assignments(supervisor_user_id);
```

#### supervision_feedbacks
```sql
CREATE TABLE supervision_feedbacks (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES supervision_assignments(id),
    session_note_id VARCHAR(50) NOT NULL,
    supervisor_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    feedback_text TEXT NOT NULL,
    strengths JSONB,
    areas_for_improvement JSONB,
    recommendations TEXT,
    rating INTEGER,
    is_read_by_student BOOLEAN NOT NULL DEFAULT FALSE,
    read_at TIMESTAMP,
    reviewed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_assignment ON supervision_feedbacks(assignment_id);
CREATE INDEX idx_session_note ON supervision_feedbacks(session_note_id);
```

#### supervision_sessions
```sql
CREATE TABLE supervision_sessions (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES supervision_assignments(id),
    scheduled_date TIMESTAMP NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 60,
    topic VARCHAR(200),
    meeting_notes TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    attendance_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_assignment_session ON supervision_sessions(assignment_id);
CREATE INDEX idx_scheduled_date ON supervision_sessions(scheduled_date);
```

## Documentación API

Acceder a la documentación interactiva:

- **Swagger UI:** http://localhost:8006/docs
- **ReDoc:** http://localhost:8006/redoc

## Logs

```bash
# Ver logs en tiempo real
docker logs -f uce_supervision_service

# Ver últimas 100 líneas
docker logs --tail 100 uce_supervision_service
```

## Troubleshooting

### Error: Connection refused (PostgreSQL)

```bash
# Verificar que PostgreSQL esté corriendo
docker ps | grep postgresql

# Verificar logs
docker logs uce_postgresql

# Recrear servicio
docker-compose restart postgresql
```

### Error: Connection refused (RabbitMQ)

```bash
# Verificar RabbitMQ
docker ps | grep rabbitmq

# Acceder a management UI
http://localhost:15672 (guest/guest)

# Verificar exchange 'uce_events' existe
```

### Eventos no se consumen

```bash
# Verificar consumer logs
docker logs uce_supervision_service | grep "Consumer"

# Debería mostrar:
# "Consumer connected to RabbitMQ"
# "Listening for events: clinical.session_recorded"
```

## Seguridad

- ✅ JWT authentication requerido en todos los endpoints
- ✅ Control de acceso basado en roles (RBAC)
- ✅ Validación de datos con Pydantic
- ✅ Prepared statements (SQL injection protection)
- ✅ Non-root user en Docker
- ✅ Secretos externalizados en variables de entorno

## Roles y Permisos

| Rol | Permisos |
|-----|----------|
| **admin** | Acceso completo a todos los recursos |
| **coordinador** | Crear/actualizar asignaciones, ver todo |
| **psicologo_supervisor** | Crear feedback, ver sus asignaciones, programar sesiones |
| **estudiante** | Ver sus asignaciones, ver su feedback, confirmar asistencia |

## Métricas

- Health check endpoint: `/health`
- Logs estructurados con timestamps
- Redis para caché de consultas frecuentes
- Health checks en Docker Compose

## Contribución

Este servicio es parte del Sistema UCE Psicología. Para contribuir:

1. Seguir principios SOLID
2. Mantener cobertura de tests
3. Documentar cambios en README
4. Usar conventional commits

## Versión

**v1.0.0** - Enero 2025

## Contacto

Universidad Central del Ecuador - Facultad de Psicología

## Licencia

Uso académico - UCE 2025
