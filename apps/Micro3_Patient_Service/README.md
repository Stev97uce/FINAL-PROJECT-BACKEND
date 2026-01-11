# 🏥 Patient Service - Gestión de Consultantes y Expedientes

Microservicio para la gestión de pacientes/consultantes y sus expedientes clínicos en el sistema UCE de Psicología.

## 📋 Características

- **Gestión de Pacientes/Consultantes**: CRUD completo con validaciones
- **Expedientes Clínicos**: Creación y seguimiento de historias clínicas
- **Roles y Permisos**: Control de acceso basado en roles (recepcionista, estudiante, supervisor, administrador)
- **Eventos**: Publicación de eventos en RabbitMQ para arquitectura event-driven
- **API REST**: Endpoints versionados y documentados con OpenAPI/Swagger
- **Testing**: Suite completa de tests con pytest

## 🚀 Tecnologías

- **FastAPI** 0.109.0 - Framework web moderno y rápido
- **Python** 3.11+ - Lenguaje de programación
- **PostgreSQL** 14+ - Base de datos relacional
- **SQLAlchemy** 2.0 - ORM
- **Pydantic** 2.5 - Validación de datos
- **Redis** 7.0 - Caché
- **RabbitMQ** 3 - Message broker
- **JWT** - Autenticación con tokens
- **Docker** - Containerización
- **pytest** - Testing framework

## 📁 Estructura del Proyecto

```
Micro3_Patient_Service/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación FastAPI
│   ├── config.py            # Configuración
│   ├── database.py          # Conexión a base de datos
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Schemas Pydantic
│   ├── security.py          # Autenticación JWT
│   ├── dependencies.py      # Dependencias
│   ├── events.py            # RabbitMQ publisher
│   └── routes/
│       ├── __init__.py
│       ├── patients.py      # Endpoints de pacientes
│       └── expedientes.py   # Endpoints de expedientes
├── tests/
│   └── test_api.py          # Tests unitarios
├── requirements.txt         # Dependencias
├── requirements-dev.txt     # Dependencias de desarrollo
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker Compose
├── package.json            # Scripts npm/TurboRepo
├── .env.example            # Variables de entorno ejemplo
├── .gitignore              # Git ignore
└── README.md               # Este archivo
```

## 🔧 Instalación

### Prerrequisitos

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- RabbitMQ 3+

### Configuración Local

1. **Clonar el repositorio**

```bash
cd apps/Micro3_Patient_Service
```

2. **Crear entorno virtual**

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. **Configurar variables de entorno**

```bash
cp .env.example .env
# Editar .env con tus valores
```

5. **Crear base de datos**

```sql
CREATE DATABASE patient_db;
```

6. **Ejecutar el servicio**

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

La API estará disponible en: http://localhost:8002

- Docs interactivos: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc
- Health check: http://localhost:8002/health

## 🐳 Docker

### Construir imagen

```bash
docker build -t stevxd97/uce-patient-service:latest .
```

### Ejecutar con Docker Compose

```bash
docker-compose up -d
```

Esto levantará:
- Patient Service (puerto 8002)
- PostgreSQL (puerto 5433)
- Redis (puerto 6380)
- RabbitMQ (puertos 5673, 15673)

## 🧪 Testing

### Ejecutar todos los tests

```bash
pytest tests/ -v
```

### Con cobertura

```bash
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html
```

### Tests en watch mode

```bash
pytest tests/ -v --cov=app -f
```

## 📡 API Endpoints

### Pacientes

| Método | Endpoint | Descripción | Rol Requerido |
|--------|----------|-------------|---------------|
| POST | `/api/v1/patients/` | Crear paciente | recepcionista, admin |
| GET | `/api/v1/patients/` | Listar pacientes | recepcionista, admin |
| GET | `/api/v1/patients/{id}` | Obtener paciente | estudiante, supervisor, admin |
| GET | `/api/v1/patients/by-user/{user_id}` | Obtener por user_id | consultante (propio), staff |
| GET | `/api/v1/patients/by-cedula/{cedula}` | Obtener por cédula | recepcionista, admin |
| PUT | `/api/v1/patients/{id}` | Actualizar paciente | recepcionista, admin |
| DELETE | `/api/v1/patients/{id}` | Desactivar paciente | recepcionista, admin |

### Expedientes

| Método | Endpoint | Descripción | Rol Requerido |
|--------|----------|-------------|---------------|
| POST | `/api/v1/expedientes/` | Crear expediente | estudiante, supervisor, admin |
| GET | `/api/v1/expedientes/` | Listar expedientes | estudiante (propios), supervisor, admin |
| GET | `/api/v1/expedientes/{id}` | Obtener expediente | estudiante (propio), supervisor, admin |
| GET | `/api/v1/expedientes/by-patient/{patient_id}` | Por paciente | estudiante (propios), supervisor, admin |
| GET | `/api/v1/expedientes/by-codigo/{codigo}` | Por código | estudiante (propio), supervisor, admin |
| PUT | `/api/v1/expedientes/{id}` | Actualizar expediente | estudiante (propio), supervisor, admin |
| POST | `/api/v1/expedientes/{id}/close` | Cerrar expediente | estudiante (propio), supervisor, admin |

### Health Check

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Estado del servicio |
| GET | `/` | Info del servicio |

## 🔐 Autenticación

Todos los endpoints (excepto `/health` y `/`) requieren autenticación JWT.

**Header requerido:**
```
Authorization: Bearer {jwt_token}
```

El token debe contener:
- `user_id`: ID del usuario
- `email`: Email del usuario
- `role`: Rol del usuario (consultante, recepcionista, estudiante, psicologo_supervisor, administrador)
- `is_verified`: Boolean indicando si el email está verificado

## 📊 Modelos de Datos

### Patient (Consultante/Paciente)

```python
{
  "id": int,
  "user_id": int,  # FK a Auth/User Service
  "nombres": str,
  "apellidos": str,
  "cedula": str (10 dígitos),
  "fecha_nacimiento": date,
  "genero": Enum ["Masculino", "Femenino", "Otro", "Prefiero no decir"],
  "estado_civil": Enum ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a", "Unión libre"],
  "telefono": str (10 dígitos),
  "telefono_emergencia": str (opcional),
  "contacto_emergencia_nombre": str (opcional),
  "contacto_emergencia_relacion": str (opcional),
  "direccion": str,
  "ciudad": str,
  "provincia": str,
  "tipo_sangre": Enum ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Desconocido"],
  "alergias": str (opcional),
  "medicamentos_actuales": str (opcional),
  "condiciones_medicas": str (opcional),
  "ocupacion": str (opcional),
  "institucion": str (opcional),
  "motivo_consulta_inicial": str,
  "is_active": bool,
  "created_at": datetime,
  "updated_at": datetime,
  "created_by": int,
  "updated_by": int
}
```

### Expediente (Historia Clínica)

```python
{
  "id": int,
  "patient_id": int,  # FK a Patient
  "codigo_expediente": str,  # EXP-YYYY-NNNN (auto-generado)
  "fecha_apertura": date,
  "fecha_cierre": date (opcional),
  "estado": Enum ["Activo", "Inactivo", "Cerrado", "Archivado"],
  "psicologo_asignado_id": int (opcional),  # FK a User Service
  "supervisor_asignado_id": int (opcional),  # FK a User Service
  "diagnostico_inicial": str (opcional),
  "plan_tratamiento": str (opcional),
  "objetivos_terapeuticos": str (opcional),
  "observaciones_generales": str (opcional),
  "antecedentes_personales": str (opcional),
  "antecedentes_familiares": str (opcional),
  "numero_sesiones": int,
  "ultima_sesion_fecha": datetime (opcional),
  "motivo_cierre": str (opcional),
  "created_at": datetime,
  "updated_at": datetime,
  "created_by": int,
  "updated_by": int
}
```

## 📤 Eventos RabbitMQ

El servicio publica los siguientes eventos en el exchange `uce_events`:

### patient.created
```json
{
  "patient_id": 1,
  "user_id": 100,
  "nombres": "Juan",
  "apellidos": "Pérez",
  "cedula": "1234567890",
  "created_by": 5,
  "created_at": "2024-01-15T10:30:00"
}
```

### patient.updated
```json
{
  "patient_id": 1,
  "user_id": 100,
  "updated_by": 5,
  "updated_at": "2024-01-15T11:00:00"
}
```

### patient.deleted
```json
{
  "patient_id": 1,
  "user_id": 100,
  "deleted_by": 5,
  "deleted_at": "2024-01-15T12:00:00"
}
```

### expediente.created
```json
{
  "expediente_id": 1,
  "patient_id": 1,
  "codigo_expediente": "EXP-2024-0001",
  "psicologo_asignado_id": 10,
  "supervisor_asignado_id": 15,
  "created_by": 10,
  "created_at": "2024-01-15T10:00:00"
}
```

### expediente.updated
```json
{
  "expediente_id": 1,
  "patient_id": 1,
  "codigo_expediente": "EXP-2024-0001",
  "estado": "Activo",
  "updated_by": 10,
  "updated_at": "2024-01-15T11:00:00"
}
```

### expediente.closed
```json
{
  "expediente_id": 1,
  "patient_id": 1,
  "codigo_expediente": "EXP-2024-0001",
  "fecha_cierre": "2024-06-15",
  "motivo_cierre": "Alta por mejoría",
  "closed_by": 10
}
```

## 🔗 Integración con Otros Servicios

### Auth Service (puerto 8000)
- Validación de tokens JWT
- Verificación de usuarios

### User Service (puerto 8001)
- Obtención de perfiles de usuarios
- Verificación de roles y permisos
- Información de psicólogos y supervisores

## 🚀 CI/CD

El servicio utiliza GitHub Actions para:
- **Testing**: Ejecuta tests automáticamente en cada push/PR
- **Build**: Construye imagen Docker
- **Push**: Sube imagen a DockerHub
- **Deploy**: (Preparado para) Despliega en AWS ECS

Ver [.github/workflows/patient-service.yml](../../.github/workflows/patient-service.yml)

## 📝 Variables de Entorno

```bash
# Servidor
APP_NAME=Patient Service
APP_VERSION=1.0.0
HOST=0.0.0.0
PORT=8002
DEBUG=true
ENVIRONMENT=development

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=patient_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=2

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_EXCHANGE=uce_events

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256

# Servicios
AUTH_SERVICE_URL=http://localhost:8000
USER_SERVICE_URL=http://localhost:8001
```

## 🐛 Troubleshooting

### Error de conexión a PostgreSQL
```bash
# Verificar que PostgreSQL esté corriendo
psql -h localhost -U postgres -d patient_db

# Verificar variables de entorno
echo $DB_HOST $DB_PORT $DB_USER
```

### Error de conexión a RabbitMQ
```bash
# Verificar RabbitMQ
docker ps | grep rabbitmq
curl http://localhost:15672/  # Management UI
```

### Tests fallando
```bash
# Limpiar caché
pytest --cache-clear

# Verificar dependencias
pip install -r requirements-dev.txt
```

## 📄 Licencia

MIT

## 👥 Equipo

Universidad Central del Ecuador - Facultad de Psicología

---

**Puerto:** 8002  
**Versión:** 1.0.0  
**Estado:** ✅ En desarrollo
