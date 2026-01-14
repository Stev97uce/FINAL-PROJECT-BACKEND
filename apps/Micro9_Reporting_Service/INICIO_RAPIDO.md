# 🚀 INICIO RÁPIDO - Reporting Service

Guía para levantar y probar el servicio de reportes en **5 minutos**.

## 📋 Prerrequisitos

✅ Docker y Docker Compose instalados  
✅ Puerto 8008 disponible  
✅ Otros microservicios corriendo (especialmente Auth Service para JWT)

## 🔧 Configuración Inicial

### 1. Variables de Entorno

```bash
# Copiar ejemplo
cp .env.example .env

# Editar si es necesario (opcional para desarrollo)
notepad .env
```

Las variables por defecto funcionan con docker-compose del proyecto.

### 2. Crear Base de Datos PostgreSQL

```sql
-- Ejecutar en PostgreSQL (puerto 5432)
CREATE DATABASE reporting_db;
```

O con docker:
```bash
docker exec -it uce_postgresql psql -U postgres -c "CREATE DATABASE reporting_db;"
```

## 🐳 Levantar con Docker Compose (RECOMENDADO)

### Opción A: Solo Reporting Service

```bash
# Desde el directorio raíz del proyecto
docker-compose up -d reporting-service
```

Este comando automáticamente levanta todas las dependencias (PostgreSQL, Redis, RabbitMQ, otros microservicios).

### Opción B: Todos los Servicios

```bash
# Levantar todo el ecosistema
docker-compose up -d

# Ver logs del Reporting Service
docker-compose logs -f reporting-service
```

## 🏃 Levantar en Desarrollo Local (Sin Docker)

### 1. Instalar Dependencias

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Linux/Mac)
source venv/bin/activate

# Instalar paquetes
pip install -r requirements.txt
```

### 2. Ejecutar Migraciones

```bash
# Crear tablas
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

### 3. Iniciar Servidor

```bash
# Desarrollo con recarga automática
uvicorn app.main:app --host 0.0.0.0 --port 8008 --reload

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8008 --workers 4
```

## ✅ Verificar Instalación

### 1. Health Check

```bash
# PowerShell
Invoke-WebRequest http://localhost:8008/health | ConvertFrom-Json

# Bash/curl
curl http://localhost:8008/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "service": "reporting-service",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected",
  "rabbitmq": "unknown",
  "timestamp": "2026-01-14T12:00:00Z"
}
```

### 2. Servicio Info

```bash
curl http://localhost:8008/
```

**Respuesta:**
```json
{
  "service": "UCE Reporting Service",
  "version": "1.0.0",
  "status": "running"
}
```

## 🔑 Obtener Tokens JWT

### Opción A: Script de Generación

```bash
# Generar tokens de prueba
python get_tokens.py
```

Obtendrás 4 tokens para diferentes roles:
- 🔴 **ADMINISTRADOR**: Acceso total
- 🟡 **COORDINADOR**: Acceso administrativo limitado
- 🟢 **PSICÓLOGO SUPERVISOR**: Acceso a reportes clínicos
- 🔵 **ESTUDIANTE**: Acceso limitado

### Opción B: Login en Auth Service

```bash
# Login como admin
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@uce.edu.ec",
    "password": "Admin123!"
  }'
```

Copia el `access_token` de la respuesta.

## 🧪 Pruebas Básicas

### 1. Listar Reportes (Requiere Token)

```bash
# PowerShell
$token = "TU_TOKEN_AQUI"
Invoke-WebRequest -Uri "http://localhost:8008/api/v1/reports" `
  -Headers @{Authorization="Bearer $token"} | ConvertFrom-Json

# Bash
curl http://localhost:8008/api/v1/reports \
  -H "Authorization: Bearer $token"
```

### 2. Listar Templates Disponibles

```bash
# PowerShell
Invoke-WebRequest -Uri "http://localhost:8008/api/v1/reports/templates/available" `
  -Headers @{Authorization="Bearer $token"} | ConvertFrom-Json

# Bash
curl http://localhost:8008/api/v1/reports/templates/available \
  -H "Authorization: Bearer $token"
```

### 3. Ver Estadísticas (Solo Admin)

```bash
# PowerShell
Invoke-WebRequest -Uri "http://localhost:8008/api/v1/admin/stats" `
  -Headers @{Authorization="Bearer $token"} | ConvertFrom-Json

# Bash
curl http://localhost:8008/api/v1/admin/stats \
  -H "Authorization: Bearer $token"
```

## 📊 Generar un Reporte

### 1. Crear Template (Solo Admin)

```bash
# PowerShell
$body = @{
  name = "Reporte de Citas Mensual"
  report_type = "appointments"
  description = "Estadísticas de citas del mes"
  query_template = @{
    date_range = "last_30_days"
    include_cancelled = $true
  }
  required_roles = @("administrador", "coordinador")
  output_formats = @("pdf", "excel")
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8008/api/v1/admin/templates" `
  -Method POST `
  -Headers @{Authorization="Bearer $token"; "Content-Type"="application/json"} `
  -Body $body | ConvertFrom-Json

# Bash
curl -X POST http://localhost:8008/api/v1/admin/templates \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Reporte de Citas Mensual",
    "report_type": "appointments",
    "description": "Estadísticas de citas del mes",
    "query_template": {
      "date_range": "last_30_days",
      "include_cancelled": true
    },
    "required_roles": ["administrador", "coordinador"],
    "output_formats": ["pdf", "excel"]
  }'
```

Copia el `id` del template creado.

### 2. Generar Reporte desde Template

```bash
# PowerShell
$templateId = 1  # ID del template creado
$body = @{
  template_id = $templateId
  report_format = "pdf"
  parameters = @{
    start_date = "2026-01-01"
    end_date = "2026-01-31"
  }
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8008/api/v1/reports/generate" `
  -Method POST `
  -Headers @{Authorization="Bearer $token"; "Content-Type"="application/json"} `
  -Body $body | ConvertFrom-Json

# Bash
curl -X POST http://localhost:8008/api/v1/reports/generate \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": 1,
    "report_format": "pdf",
    "parameters": {
      "start_date": "2026-01-01",
      "end_date": "2026-01-31"
    }
  }'
```

El servicio procesará el reporte en background y retornará el `report_id`.

### 3. Descargar Reporte

```bash
# Esperar ~10-30 segundos para generación

# PowerShell
$reportId = 1  # ID del reporte generado
Invoke-WebRequest -Uri "http://localhost:8008/api/v1/reports/$reportId/download" `
  -Headers @{Authorization="Bearer $token"} `
  -OutFile "reporte.pdf"

# Bash
curl http://localhost:8008/api/v1/reports/1/download \
  -H "Authorization: Bearer $token" \
  -o reporte.pdf
```

## 📝 Logs y Debugging

### Ver Logs en Docker

```bash
# Logs en tiempo real
docker-compose logs -f reporting-service

# Últimas 100 líneas
docker-compose logs --tail=100 reporting-service

# Buscar errores
docker-compose logs reporting-service | grep -i error
```

### Entrar al Contenedor

```bash
docker exec -it uce_reporting_service /bin/sh

# Ver archivos generados
ls -la /app/reports/

# Ver variables de entorno
env | grep DATABASE
```

## 🔍 Troubleshooting

### Error: "Database connection failed"

```bash
# Verificar PostgreSQL
docker exec -it uce_postgresql psql -U postgres -c "\l"

# Crear la base de datos
docker exec -it uce_postgresql psql -U postgres -c "CREATE DATABASE reporting_db;"

# Verificar desde el contenedor
docker exec -it uce_reporting_service python -c "from app.database import engine; import asyncio; asyncio.run(engine.connect())"
```

### Error: "Redis connection failed"

```bash
# Verificar Redis
docker exec -it uce_redis redis-cli ping

# Debería responder: PONG
```

### Error: "Unauthorized" (401)

```bash
# Verificar token
python -c "import jwt; print(jwt.decode('TU_TOKEN', options={'verify_signature': False}))"

# Generar nuevo token
python get_tokens.py
```

### Error: "Template not found"

```bash
# Listar templates existentes
curl http://localhost:8008/api/v1/admin/templates \
  -H "Authorization: Bearer $token"

# Crear template si no existe (ver sección "Generar un Reporte")
```

### Puerto 8008 en Uso

```bash
# Verificar qué proceso usa el puerto
netstat -ano | findstr :8008

# Matar el proceso (Windows)
taskkill /PID <PID> /F

# En Linux/Mac
lsof -ti:8008 | xargs kill -9
```

## 📚 Próximos Pasos

1. ✅ **Explorar la API**: Ver [README.md](README.md#-api-endpoints) para todos los endpoints
2. ✅ **Crear Templates**: Personalizar reportes para tu organización
3. ✅ **Probar Formatos**: PDF, Excel, CSV, JSON
4. ✅ **Integrar con Frontend**: Usar la API desde tu aplicación web
5. ✅ **Configurar Celery**: Para reportes muy grandes (opcional)

## 🆘 Ayuda Adicional

- **Documentación Completa**: [README.md](README.md)
- **Análisis Técnico**: [ANALYSIS.md](ANALYSIS.md)
- **API Interactiva**: http://localhost:8008/docs (Swagger UI)
- **API Alternativa**: http://localhost:8008/redoc (ReDoc)

---

**✨ ¡Listo! Tu Reporting Service está funcionando.**
