# 📊 ANÁLISIS COMPLETO - REPORTING SERVICE (Micro9)

## 🎯 PROPÓSITO Y RESPONSABILIDAD

El **Reporting Service** es el microservicio encargado de **generar, gestionar y exportar reportes operativos** del sistema UCE Psychology. Su función principal es consolidar datos de múltiples microservicios para producir informes analíticos, estadísticos y operacionales en diversos formatos.

### Funciones Clave:
1. **Generación de Reportes:** Crear informes programados o bajo demanda
2. **Exportación Multi-formato:** PDF, Excel (XLSX), CSV, JSON
3. **Consolidación de Datos:** Agregar información de todos los microservicios
4. **Reportes Predefinidos:** Templates configurables para reportes frecuentes
5. **Programación:** Reportes automáticos (diarios, semanales, mensuales)
6. **Historial:** Almacenar reportes generados para consulta posterior
7. **Permisos:** Control de acceso basado en roles
8. **Notificaciones:** Avisar cuando un reporte esté listo

---

## 🏗️ ARQUITECTURA Y TECNOLOGÍA

### Stack Tecnológico Definido
- **Lenguaje:** Python 3.11+
- **Framework:** FastAPI 0.109.0+
- **Base de Datos:** PostgreSQL 14+ (relacional, ideal para reportes estructurados)
- **Cache:** Redis 7.0 (caché de reportes frecuentes)
- **Event Bus:** RabbitMQ (consumir eventos de otros servicios)
- **Puerto:** 8008
- **Patrón:** **KISS** (Keep It Simple, Stupid) - Prioridad en simplicidad y mantenibilidad

### ¿Por qué PostgreSQL?
- Excelente para consultas analíticas complejas (JOINs, agregaciones)
- Soporte para JSON (reportes metadata)
- Vistas materializadas para reportes pesados
- Transacciones ACID
- Índices optimizados para lecturas

### ¿Por qué KISS Pattern?
- Reportes deben ser **predecibles y fáciles de mantener**
- Evitar complejidad innecesaria en generación de PDFs/Excel
- Separación clara: Consulta → Procesamiento → Exportación
- Configuración sobre código (templates de reportes)

---

## 🔗 INTEGRACIONES CON OTROS MICROSERVICIOS

El Reporting Service **NO** almacena datos transaccionales, sino que **consulta y agrega** datos de otros servicios:

### Relaciones Directas (via REST API):

#### 1. **Auth Service (Micro1)** - Puerto 8000
- **Consulta:** Información de usuarios para reportes de actividad
- **Datos:** Usuarios registrados, roles, verificaciones
- **Reportes:** "Usuarios Nuevos por Mes", "Distribución de Roles"

#### 2. **User Service (Micro2)** - Puerto 8001
- **Consulta:** Perfiles completos, logs de actividad
- **Datos:** Datos demográficos, historial de cambios
- **Reportes:** "Perfil Demográfico", "Actividad de Usuarios"

#### 3. **Patient Service (Micro3)** - Puerto 8002
- **Consulta:** Consultantes, expedientes clínicos
- **Datos:** Estadísticas de consultantes, expedientes activos/cerrados
- **Reportes:** "Expedientes por Estado", "Motivos de Consulta"

#### 4. **Appointment Service (Micro4)** - Puerto 8003
- **Consulta:** Citas agendadas, asistencia, cancelaciones
- **Datos:** Ocupación de agenda, tiempos de espera
- **Reportes:** "Citas Atendidas vs Canceladas", "Ocupación por Sala"

#### 5. **Room Service (Micro5)** - Puerto 8004
- **Consulta:** Uso de consultorios, disponibilidad
- **Datos:** Horas de uso, salas más/menos utilizadas
- **Reportes:** "Utilización de Espacios", "Disponibilidad por Horario"

#### 6. **Clinical Service (Micro6)** - Puerto 8005
- **Consulta:** Notas clínicas, sesiones registradas
- **Datos:** Número de sesiones, técnicas aplicadas
- **Reportes:** "Sesiones por Psicólogo", "Técnicas Terapéuticas Más Usadas"

#### 7. **Supervision Service (Micro7)** - Puerto 8006
- **Consulta:** Supervisiones, feedbacks, estudiantes
- **Datos:** Desempeño de estudiantes, frecuencia de supervisiones
- **Reportes:** "Supervisiones por Estudiante", "Calidad de Feedbacks"

#### 8. **Notification Service (Micro8)** - Puerto 8007
- **Consulta:** Notificaciones enviadas, tasas de apertura
- **Datos:** Canales usados, delivery logs
- **Reportes:** "Efectividad de Notificaciones", "Canales Preferidos"

### Relaciones Indirectas (via RabbitMQ Events):

El Reporting Service **consume eventos** para mantener datos agregados actualizados:

- `user.registered` → Actualizar contador de usuarios nuevos
- `appointment.completed` → Incrementar métricas de citas
- `clinical.session_recorded` → Actualizar estadísticas de sesiones
- `supervision.feedback_added` → Contabilizar supervisiones
- `notification.sent` → Registrar métricas de comunicación

**Ventaja:** No necesita hacer polling constante, los datos se actualizan en tiempo real.

---

## 📊 TIPOS DE REPORTES

### 1. Reportes Operacionales (Diarios/Semanales)
- **Citas del Día/Semana:** Lista de citas programadas
- **Ocupación de Consultorios:** Horas utilizadas vs disponibles
- **Usuarios Nuevos:** Registros recientes

### 2. Reportes Analíticos (Mensuales/Anuales)
- **Dashboard Ejecutivo:** KPIs principales (citas, usuarios, sesiones)
- **Análisis de Demanda:** Horarios más solicitados, especialidades populares
- **Performance de Estudiantes:** Supervisiones, sesiones completadas

### 3. Reportes Clínicos (Por Solicitud)
- **Expediente Completo:** Todo el historial de un consultante (PDF)
- **Sesiones por Consultante:** Notas clínicas agregadas
- **Plan de Tratamiento:** Objetivos vs progreso

### 4. Reportes Administrativos (Trimestrales)
- **Utilización de Recursos:** Salas, psicólogos, horarios
- **Métricas de Calidad:** Satisfacción, tiempos de espera
- **Estadísticas de Notificaciones:** Efectividad de comunicaciones

### 5. Reportes Personalizados
- **Constructor de Reportes:** Usuarios avanzados pueden definir filtros personalizados
- **Exportación Flexible:** Elegir columnas, formato, período

---

## 💾 MODELO DE DATOS (PostgreSQL)

### Tabla: `reports`
Almacena metadatos de reportes generados.

```sql
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL, -- 'operational', 'analytical', 'clinical', 'administrative', 'custom'
    format VARCHAR(10) NOT NULL, -- 'pdf', 'xlsx', 'csv', 'json'
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    file_path TEXT, -- S3 URL o ruta local
    file_size_bytes BIGINT,
    generated_by INTEGER NOT NULL, -- user_id
    parameters JSONB, -- Filtros aplicados
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    error_message TEXT
);

CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_generated_by ON reports(generated_by);
CREATE INDEX idx_reports_created_at ON reports(created_at DESC);
CREATE INDEX idx_reports_type ON reports(type);
```

### Tabla: `report_templates`
Templates predefinidos para reportes frecuentes.

```sql
CREATE TABLE report_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,
    format VARCHAR(10) NOT NULL,
    query_template TEXT NOT NULL, -- SQL o JSON query
    default_parameters JSONB,
    required_roles TEXT[], -- ['administrador', 'coordinador']
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Tabla: `scheduled_reports`
Reportes programados automáticamente.

```sql
CREATE TABLE scheduled_reports (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES report_templates(id) ON DELETE CASCADE,
    schedule_cron VARCHAR(100) NOT NULL, -- '0 8 * * 1' (Lunes 8am)
    recipients TEXT[], -- Emails de destinatarios
    enabled BOOLEAN DEFAULT TRUE,
    last_run TIMESTAMP,
    next_run TIMESTAMP,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Tabla: `aggregated_metrics`
Métricas pre-calculadas para reportes rápidos (caché en BD).

```sql
CREATE TABLE aggregated_metrics (
    id SERIAL PRIMARY KEY,
    metric_type VARCHAR(100) NOT NULL, -- 'daily_appointments', 'monthly_users'
    metric_date DATE NOT NULL,
    metric_value JSONB NOT NULL, -- Datos agregados
    calculated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(metric_type, metric_date)
);

CREATE INDEX idx_aggregated_metrics_type_date ON aggregated_metrics(metric_type, metric_date DESC);
```

---

## 🔌 API ENDPOINTS

### Usuarios Generales

#### Listar Reportes
```http
GET /api/v1/reports
```
- **Query Params:** `status`, `type`, `limit`, `offset`
- **Roles:** Todos (filtrado por usuario)
- **Response:** Lista de reportes generados por el usuario

#### Obtener Reporte
```http
GET /api/v1/reports/{id}
```
- **Roles:** Todos (validar pertenencia)
- **Response:** Metadata del reporte

#### Descargar Reporte
```http
GET /api/v1/reports/{id}/download
```
- **Roles:** Todos (validar pertenencia)
- **Response:** Archivo PDF/Excel/CSV

#### Crear Reporte
```http
POST /api/v1/reports/generate
```
- **Body:**
```json
{
  "template_id": 1,
  "format": "pdf",
  "parameters": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "consultante_id": 123
  }
}
```
- **Roles:** Todos (según template)
- **Response:** ID del reporte creado (status: pending)

### Administración

#### Listar Templates
```http
GET /api/v1/admin/templates
```
- **Roles:** administrador, coordinador
- **Response:** Templates disponibles

#### Crear Template
```http
POST /api/v1/admin/templates
```
- **Roles:** administrador
- **Body:** Configuración del template

#### Actualizar Template
```http
PUT /api/v1/admin/templates/{id}
```
- **Roles:** administrador

#### Listar Reportes Programados
```http
GET /api/v1/admin/scheduled
```
- **Roles:** administrador, coordinador

#### Crear Reporte Programado
```http
POST /api/v1/admin/scheduled
```
- **Body:**
```json
{
  "template_id": 2,
  "schedule_cron": "0 8 * * 1",
  "recipients": ["admin@uce.edu.ec"]
}
```

#### Estadísticas de Uso
```http
GET /api/v1/admin/stats
```
- **Roles:** administrador
- **Response:** Métricas de reportes generados

### Sistema
```http
GET /health
GET /
```

---

## 📦 BIBLIOTECAS PYTHON REQUERIDAS

### Generación de Reportes
- **ReportLab:** PDFs complejos con gráficos
- **WeasyPrint:** HTML → PDF (alternativa)
- **openpyxl:** Archivos Excel (.xlsx)
- **pandas:** Manipulación de datos, exportación CSV
- **jinja2:** Templates para reportes

### Gráficos y Visualización
- **matplotlib:** Gráficos estáticos (barras, líneas, pie)
- **plotly:** Gráficos interactivos (opcional)

### Consultas y Datos
- **SQLAlchemy:** ORM para PostgreSQL
- **asyncpg:** Driver asíncrono PostgreSQL
- **httpx:** Llamadas HTTP a otros microservicios
- **pydantic:** Validación de schemas

### Tareas Asíncronas
- **Celery + Redis:** Procesar reportes pesados en background
- **APScheduler:** Cron jobs para reportes programados

### Otros
- **python-dateutil:** Manejo de fechas
- **python-magic:** Detección de tipo de archivo

---

## 🎨 FLUJO DE GENERACIÓN DE REPORTES

### Caso 1: Reporte Bajo Demanda

```
1. Usuario hace POST /api/v1/reports/generate
   ↓
2. Reporting Service valida permisos y template
   ↓
3. Crea registro en DB (status: pending)
   ↓
4. Encola tarea en Celery
   ↓
5. Worker Celery:
   a. Cambia status → processing
   b. Consulta microservicios relevantes (HTTP)
   c. Consolida datos en pandas DataFrame
   d. Genera gráficos con matplotlib
   e. Crea PDF con ReportLab o Excel con openpyxl
   f. Guarda archivo en disco/S3
   g. Actualiza registro (status: completed, file_path)
   ↓
6. Emite evento report.completed
   ↓
7. Notification Service envía email con link de descarga
   ↓
8. Usuario descarga con GET /api/v1/reports/{id}/download
```

### Caso 2: Reporte Programado

```
1. APScheduler ejecuta cron job (ej: Lunes 8am)
   ↓
2. Busca scheduled_reports con next_run <= now
   ↓
3. Para cada scheduled_report:
   a. Crea registro en reports (auto-generado)
   b. Sigue flujo de Caso 1
   c. Envía email a recipients
   d. Actualiza last_run y next_run
```

---

## 📨 EVENTOS RABBITMQ

### Eventos Consumidos

| Routing Key | Propósito | Acción |
|-------------|-----------|--------|
| `appointment.completed` | Actualizar métricas de citas | Incrementar contador diario |
| `clinical.session_recorded` | Actualizar métricas de sesiones | Agregar a aggregated_metrics |
| `user.registered` | Actualizar métricas de usuarios | Incrementar contador mensual |
| `supervision.feedback_added` | Actualizar métricas de supervisión | Contabilizar feedback |

### Eventos Publicados

| Routing Key | Propósito | Payload |
|-------------|-----------|---------|
| `report.generated` | Notificar reporte listo | `{ report_id, user_id, file_path, format }` |
| `report.failed` | Notificar error en generación | `{ report_id, error_message }` |

---

## 🔒 SEGURIDAD Y PERMISOS

### Control de Acceso por Rol

| Reporte | Admin | Coordinador | Psicólogo | Estudiante | Consultante |
|---------|-------|-------------|-----------|----------|-------------|
| Dashboard Ejecutivo | ✅ | ✅ | ❌ | ❌ | ❌ |
| Mis Citas | ✅ | ✅ | ✅ | ✅ | ✅ |
| Expediente Propio | ❌ | ❌ | ✅ | ❌ | ✅ |
| Todos los Expedientes | ✅ | ✅ | ❌ | ❌ | ❌ |
| Utilización de Salas | ✅ | ✅ | ❌ | ❌ | ❌ |
| Supervisiones | ✅ | ✅ | ✅ (supervisor) | ✅ (propias) | ❌ |

### Validaciones
1. **JWT Authentication:** Todos los endpoints requieren token
2. **Role Check:** Validar rol contra `required_roles` del template
3. **Data Filtering:** Usuarios solo ven sus propios reportes (excepto admin)
4. **GDPR Compliance:** Reportes con datos sensibles solo accesibles por autorizados
5. **Audit Log:** Registrar quién generó cada reporte y cuándo

---

## 🚀 CASOS DE USO ESPECÍFICOS

### 1. Reporte: "Expediente Clínico Completo"
**Usuario:** Psicólogo/Consultante
**Flujo:**
1. Usuario solicita expediente de consultante X
2. Service consulta Patient Service (datos demográficos)
3. Consulta Clinical Service (notas de sesiones)
4. Consulta Appointment Service (historial de citas)
5. Genera PDF con:
   - Portada (nombre, datos)
   - Resumen ejecutivo
   - Línea de tiempo de sesiones
   - Notas completas por sesión
   - Plan de tratamiento actual
6. PDF listo para descargar

### 2. Reporte: "Dashboard Mensual"
**Usuario:** Administrador/Coordinador
**Flujo:**
1. Scheduled report ejecuta automáticamente (1ro de cada mes)
2. Consulta aggregated_metrics de mes anterior
3. Genera gráficos:
   - Barras: Citas por día
   - Pie: Distribución de motivos de consulta
   - Línea: Tendencia de usuarios nuevos
4. Exporta Excel con:
   - Hoja 1: Resumen ejecutivo
   - Hoja 2: Datos de citas
   - Hoja 3: Datos de usuarios
   - Hoja 4: Gráficos embebidos
5. Envía email a lista de coordinadores

### 3. Reporte: "Exportación de Datos (CSV)"
**Usuario:** Investigador/Admin
**Flujo:**
1. Usuario define reporte custom con filtros
2. Service ejecuta query SQL directo a PostgreSQL
3. Resultados → pandas DataFrame
4. Export to CSV con encoding UTF-8
5. Descarga inmediata (archivo pequeño < 10MB)

---

## ⚡ OPTIMIZACIONES

### 1. Caché en Redis
- **Reportes Frecuentes:** Dashboard diario cacheado 1 hora
- **Métricas Agregadas:** Contadores en Redis, flush a DB cada hora
- **Keys:** `report:dashboard:2024-01-13`, `metrics:appointments:daily`

### 2. Vistas Materializadas (PostgreSQL)
```sql
CREATE MATERIALIZED VIEW mv_monthly_appointments AS
SELECT 
  DATE_TRUNC('month', fecha) AS mes,
  COUNT(*) AS total_citas,
  COUNT(*) FILTER (WHERE status = 'completed') AS completadas,
  COUNT(*) FILTER (WHERE status = 'cancelled') AS canceladas
FROM appointments
GROUP BY DATE_TRUNC('month', fecha);

CREATE UNIQUE INDEX ON mv_monthly_appointments(mes);
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_appointments;
```

### 3. Procesamiento Asíncrono
- **Reportes > 30 segundos:** Celery worker en background
- **Notificación:** Usuario recibe email cuando está listo
- **Queue Priority:** Reportes urgentes en cola high-priority

### 4. Paginación
- **Listas de Reportes:** 50 items por página
- **Datos de Consultas:** Limit en 1000 registros por query

---

## 🧪 TESTING

### Tests Unitarios (pytest)
- `test_models.py`: Modelos SQLAlchemy
- `test_schemas.py`: Validaciones Pydantic
- `test_generators.py`: Lógica de generación PDF/Excel
- `test_api.py`: Endpoints FastAPI

### Tests de Integración
- `test_microservice_calls.py`: HTTP calls a otros servicios
- `test_rabbitmq_consumer.py`: Procesamiento de eventos
- `test_report_generation.py`: Flujo completo end-to-end

### Tests de Carga
- **Locust:** 100 reportes simultáneos
- **Objetivo:** < 60s para reportes simples, < 5min para complejos

---

## 📈 MÉTRICAS Y MONITOREO

### Prometheus Metrics
- `reports_generated_total{type, format}`: Total de reportes
- `report_generation_duration_seconds{type}`: Tiempo de generación
- `report_generation_errors_total{type}`: Errores
- `reports_in_queue`: Reportes pendientes en Celery

### Health Check
```json
{
  "status": "healthy",
  "service": "reporting-service",
  "database": "connected",
  "redis": "connected",
  "rabbitmq": "connected",
  "celery_workers": 2,
  "reports_pending": 5
}
```

---

## 🎨 PATRÓN KISS APLICADO

### Principios:
1. **Separación Clara:** Consulta → Procesamiento → Exportación (3 capas)
2. **Templates Simples:** Configuración JSON/YAML, no código complejo
3. **Bibliotecas Maduras:** ReportLab, openpyxl (no reinventar rueda)
4. **SQL Directo:** Queries optimizadas, no ORM para reportes pesados
5. **Async Solo Donde Necesario:** Generación en background, API síncrona
6. **Logs Claros:** Cada paso registrado para debugging fácil

### Anti-Patrones a Evitar:
- ❌ Over-engineering: No crear DSL propio para reportes
- ❌ Premature Optimization: No cachear todo desde día 1
- ❌ Magic Numbers: Configuración explícita en variables
- ❌ God Class: Cada tipo de reporte en su módulo

---

## 🔧 DEPENDENCIAS DE OTROS SERVICIOS

### Críticas (Sin ellas, no funciona):
- **PostgreSQL:** Base de datos principal
- **Redis:** Caché y Celery broker
- **Auth Service:** Validación JWT

### Importantes (Funcionalidad limitada sin ellas):
- **Todos los microservicios:** Datos para reportes
- **RabbitMQ:** Eventos en tiempo real
- **Notification Service:** Avisos de reportes listos

### Opcionales:
- **S3 Storage:** Almacenamiento de archivos (alternativa: disco local)

---

## 📦 ESTRUCTURA DE DIRECTORIOS

```
apps/Micro9_Reporting_Service/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # Settings
│   ├── database.py                # SQLAlchemy
│   ├── dependencies.py            # JWT auth
│   ├── models.py                  # SQLAlchemy models
│   ├── schemas.py                 # Pydantic schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── reports.py             # User endpoints
│   │   ├── admin.py               # Admin endpoints
│   │   └── health.py              # Health check
│   ├── services/
│   │   ├── __init__.py
│   │   ├── report_service.py      # Lógica negocio
│   │   ├── pdf_generator.py       # ReportLab
│   │   ├── excel_generator.py     # openpyxl
│   │   ├── csv_generator.py       # pandas
│   │   ├── data_aggregator.py     # Consolidación datos
│   │   └── microservice_client.py # HTTP calls
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── celery_tasks.py        # Background jobs
│   ├── consumers/
│   │   ├── __init__.py
│   │   └── rabbitmq_consumer.py   # Event handlers
│   └── templates/
│       ├── report_base.html       # Base HTML → PDF
│       └── email_notification.html
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_schemas.py
│   ├── test_api.py
│   ├── test_generators.py
│   └── test_integration.py
├── reports/                       # Reportes generados (temporal)
├── Dockerfile
├── requirements.txt
├── .env.example
├── README.md
├── ANALYSIS.md                    # Este archivo
└── celeryconfig.py
```

---

## 🎯 PRÓXIMOS PASOS DE IMPLEMENTACIÓN

1. ✅ **Análisis Completo** - Este documento
2. ⏳ **Configuración Base:**
   - SQLAlchemy models
   - Pydantic schemas
   - FastAPI app con CORS
3. ⏳ **API Endpoints:**
   - CRUD de reportes
   - Download endpoint
   - Admin templates
4. ⏳ **Generadores:**
   - PDF con ReportLab
   - Excel con openpyxl
   - CSV con pandas
5. ⏳ **Celery Tasks:**
   - Background processing
   - Scheduled reports
6. ⏳ **RabbitMQ Consumer:**
   - Event handlers
   - Metrics aggregation
7. ⏳ **Integración:**
   - HTTP clients a microservicios
   - Redis caching
8. ⏳ **Testing:**
   - Unit tests
   - Integration tests
9. ⏳ **Docker:**
   - Multi-stage build
   - docker-compose integration
10. ⏳ **GitHub Actions:**
    - CI/CD workflow (QA only)
11. ⏳ **DockerHub:**
    - Push images

---

**Documento creado:** 2026-01-14
**Versión:** 1.0
**Patrón:** KISS (Keep It Simple, Stupid)
**Estado:** ✅ Listo para implementación
