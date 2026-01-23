# 🏥 Patient Service - Guía Rápida

## 🚀 Inicio Rápido

### 1. Instalar dependencias
```bash
cd apps/Micro3_Patient_Service
pip install -r requirements.txt -r requirements-dev.txt
```

### 2. Configurar entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 3. Ejecutar el servicio
```bash
# Desarrollo
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

# Producción
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### 4. Ejecutar tests
```bash
python -m pytest tests/ -v --cov=app
```

## 📊 Endpoints Principales

### Pacientes
- `POST /api/v1/patients/` - Crear paciente (recepcionista)
- `GET /api/v1/patients/` - Listar pacientes (recepcionista)
- `GET /api/v1/patients/{id}` - Ver paciente (staff)
- `PUT /api/v1/patients/{id}` - Actualizar paciente (recepcionista)

### Expedientes
- `POST /api/v1/expedientes/` - Crear expediente (psicólogo)
- `GET /api/v1/expedientes/` - Listar expedientes (psicólogo)
- `GET /api/v1/expedientes/{id}` - Ver expediente (psicólogo)
- `PUT /api/v1/expedientes/{id}` - Actualizar expediente (psicólogo)
- `POST /api/v1/expedientes/{id}/close` - Cerrar expediente (psicólogo)

## 🔐 Autenticación

Todos los endpoints requieren JWT token en el header:
```
Authorization: Bearer {token}
```

## 🐳 Docker

```bash
# Construir imagen
docker build -t stevxd97/uce-patient-service:latest .

# Ejecutar con docker-compose
docker-compose up -d

# Ver logs
docker-compose logs -f patient-service
```

## 📊 Coverage Actual

- **9 tests pasando** ✅
- **Coverage: 74%**

## 🔗 Integraciones

- **Auth Service** (puerto 8000): Validación JWT
- **User Service** (puerto 8001): Perfiles de usuarios
- **RabbitMQ**: Eventos (patient.created, expediente.created, etc.)
- **PostgreSQL**: Base de datos
- **Redis**: Caché

## 📝 Roles Permitidos

- **recepcionista**: CRUD pacientes
- **estudiante**: Ver pacientes, gestionar expedientes propios
- **psicologo_supervisor**: Ver todo, gestionar expedientes
- **administrador**: Acceso total

## 🎯 Próximos Pasos

1. ✅ Estructura base creada
2. ✅ Modelos y schemas definidos
3. ✅ Endpoints implementados
4. ✅ Tests pasando
5. ✅ CI/CD configurado
6. 🔄 Pendiente: Integrar con Auth/User Services
7. 🔄 Pendiente: Desplegar en AWS

---

**Puerto:** 8002  
**Docs:** http://localhost:8002/docs  
**Health:** http://localhost:8002/health
