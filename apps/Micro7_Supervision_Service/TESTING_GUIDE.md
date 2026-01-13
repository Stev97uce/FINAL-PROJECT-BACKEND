# 🏥 Supervision Service - Guía Rápida de Testing

## 🚀 Inicio Rápido

### 1. Verificar Servicio

```bash
# Health check
curl http://localhost:8006/health

# Info del servicio
curl http://localhost:8006/
```

### 2. Generar Tokens JWT

```bash
cd apps/Micro7_Supervision_Service
python generate_token.py
```

Copia los tokens generados para usarlos en Postman.

## 📋 Flujo de Testing Completo

### Paso 1: Crear Asignación Supervisor-Estudiante

**Endpoint:** `POST http://localhost:8006/api/v1/assignments`  
**Token:** Coordinador o Admin  
**Body:**
```json
{
    "student_user_id": 3,
    "supervisor_user_id": 2,
    "specialty_area": "Psicología Clínica",
    "start_date": "2025-01-15T00:00:00",
    "notes": "Supervisión para prácticas clínicas de terapia cognitiva"
}
```

**Response esperado:** 201 Created
```json
{
    "id": 1,
    "student_user_id": 3,
    "supervisor_user_id": 2,
    "specialty_area": "Psicología Clínica",
    "start_date": "2025-01-15T00:00:00",
    "end_date": null,
    "status": "active",
    "notes": "Supervisión para prácticas clínicas de terapia cognitiva",
    "created_at": "2025-01-13T...",
    "updated_at": "2025-01-13T..."
}
```

### Paso 2: Crear Retroalimentación sobre Nota de Sesión

**Prerequisito:** Tener un `session_note_id` del Clinical Service (MongoDB ObjectId)

**Endpoint:** `POST http://localhost:8006/api/v1/feedback`  
**Token:** Supervisor  
**Body:**
```json
{
    "assignment_id": 1,
    "session_note_id": "6964fe374f1147f710343c14",
    "student_id": 3,
    "feedback_text": "Excelente trabajo en la aplicación de técnicas cognitivas. Se observa buen rapport con el consultante y adecuada escucha activa.",
    "strengths": [
        "Buena escucha activa y empatía",
        "Aplicación correcta de técnicas cognitivas",
        "Registro detallado de la sesión"
    ],
    "areas_for_improvement": [
        "Profundizar en la exploración de emociones subyacentes",
        "Mejorar el registro de observaciones no verbales"
    ],
    "recommendations": "Revisar literatura sobre técnicas de exploración emocional de Beck y Ellis",
    "rating": 4
}
```

**Response esperado:** 201 Created + Evento `supervision.feedback_added` publicado

### Paso 3: Listar Asignaciones (Como Estudiante)

**Endpoint:** `GET http://localhost:8006/api/v1/assignments`  
**Token:** Estudiante  

**Response esperado:** Solo asignaciones donde el estudiante está involucrado

### Paso 4: Ver Feedback (Como Estudiante)

**Endpoint:** `GET http://localhost:8006/api/v1/feedback`  
**Token:** Estudiante  
**Query params opcionales:** `?student_id=3`

### Paso 5: Marcar Feedback como Leído

**Endpoint:** `PATCH http://localhost:8006/api/v1/feedback/1/mark-read`  
**Token:** Estudiante  

**Response esperado:**
```json
{
    "message": "Feedback marked as read"
}
```

### Paso 6: Programar Sesión de Supervisión

**Endpoint:** `POST http://localhost:8006/api/v1/sessions`  
**Token:** Supervisor  
**Body:**
```json
{
    "assignment_id": 1,
    "scheduled_date": "2025-01-20T10:00:00",
    "duration_minutes": 60,
    "topic": "Revisión de casos clínicos y retroalimentación de sesiones"
}
```

### Paso 7: Confirmar Asistencia a Sesión

**Endpoint:** `PATCH http://localhost:8006/api/v1/sessions/1/confirm`  
**Token:** Estudiante o Supervisor  

### Paso 8: Completar Sesión de Supervisión

**Endpoint:** `PATCH http://localhost:8006/api/v1/sessions/1/complete`  
**Token:** Supervisor  

## 🔗 Integración con Clinical Service

### Test de Integración Completo:

1. **Clinical Service** → Crear session note (estudiante)
   ```
   POST http://localhost:8005/api/v1/session-notes
   ```

2. **Clinical Service** → Emite evento `clinical.session_recorded`

3. **Supervision Service** → Consume evento, identifica supervisor

4. **Supervision Service** → Supervisor crea feedback
   ```
   POST http://localhost:8006/api/v1/feedback
   ```

5. **Supervision Service** → Actualiza Clinical Service
   ```
   PATCH http://localhost:8005/api/v1/session-notes/{id}/feedback
   ```

6. **Supervision Service** → Emite evento `supervision.feedback_added`

7. **Clinical Service** → Vincula feedback_id a session_note

## 🔍 Verificación de Datos

### Ver Asignaciones en PostgreSQL

```bash
docker exec -it uce_postgresql psql -U postgres -d supervision_db
```

```sql
-- Ver asignaciones
SELECT * FROM supervision_assignments;

-- Ver feedback
SELECT id, session_note_id, supervisor_id, student_id, rating 
FROM supervision_feedbacks;

-- Ver sesiones programadas
SELECT * FROM supervision_sessions;
```

### Ver Logs en Tiempo Real

```bash
docker logs -f uce_supervision_service
```

Deberías ver:
- ✅ "Connected to RabbitMQ"
- ✅ "Listening for events: clinical.session_recorded"
- ✅ "Started consuming messages"

## 🧪 Tests de Roles y Permisos

### Admin
- ✅ Puede crear asignaciones
- ✅ Puede ver todas las asignaciones
- ✅ Puede crear y editar feedback de cualquier supervisor
- ✅ Puede eliminar recursos

### Coordinador
- ✅ Puede crear asignaciones
- ✅ Puede actualizar asignaciones
- ✅ Puede ver todas las asignaciones
- ❌ No puede crear feedback (no es supervisor)

### Supervisor (psicologo_supervisor)
- ✅ Puede ver sus asignaciones
- ✅ Puede crear feedback para sus estudiantes
- ✅ Puede programar sesiones de supervisión
- ✅ Puede actualizar su propio feedback
- ❌ No puede ver feedback de otros supervisores
- ❌ No puede crear asignaciones

### Estudiante
- ✅ Puede ver sus asignaciones
- ✅ Puede ver su feedback
- ✅ Puede marcar feedback como leído
- ✅ Puede confirmar asistencia a sesiones
- ❌ No puede crear asignaciones
- ❌ No puede crear feedback
- ❌ No puede ver feedback de otros estudiantes

## 📊 Casos de Prueba

### Test 1: Supervisor Intenta Dar Feedback sin Asignación
```
POST /api/v1/feedback
Assignment_id: 999 (no existe)
Esperado: 404 Not Found
```

### Test 2: Estudiante Intenta Ver Feedback de Otro Estudiante
```
GET /api/v1/feedback/1
Token: estudiante_juan (student_id=3)
Feedback.student_id: 4
Esperado: 403 Forbidden
```

### Test 3: Supervisor Intenta Dar Feedback a Estudiante No Asignado
```
POST /api/v1/feedback
Assignment_id: 2 (supervisor diferente)
Token: supervisor_maria
Esperado: 403 Forbidden
```

### Test 4: Crear Feedback con Rating Inválido
```
POST /api/v1/feedback
rating: 6 (debe ser 1-5)
Esperado: 422 Validation Error
```

### Test 5: MongoDB ObjectId Inválido
```
POST /api/v1/feedback
session_note_id: "invalid-id"
Esperado: 422 Validation Error (debe ser 24 caracteres)
```

## 🎯 Resultados Esperados

Al completar el flujo completo:

1. ✅ 1 asignación creada en `supervision_assignments`
2. ✅ 1 feedback creado en `supervision_feedbacks`
3. ✅ 1 sesión programada en `supervision_sessions`
4. ✅ Evento `supervision.feedback_added` publicado a RabbitMQ
5. ✅ Clinical Service actualizado con `supervisor_feedback_id`
6. ✅ Estudiante puede ver su feedback
7. ✅ Feedback marcado como leído

## 🐛 Troubleshooting

### Error: "Assignment not found"
- Verificar que el `assignment_id` existe
- Verificar que el assignment está activo (`status='active'`)

### Error: "Only the assigned supervisor can provide feedback"
- Verificar que el token del supervisor coincide con `assignment.supervisor_user_id`

### Error: "Invalid MongoDB ObjectId format"
- Verificar que `session_note_id` tiene exactamente 24 caracteres hexadecimales

### Eventos no se consumen
```bash
# Verificar consumer logs
docker logs uce_supervision_service | grep "Consumer"

# Verificar RabbitMQ
http://localhost:15672 (guest/guest)
# Ir a Queues → supervision_service_queue
```

## 📚 Documentación Adicional

- **Swagger UI:** http://localhost:8006/docs
- **ReDoc:** http://localhost:8006/redoc
- **RabbitMQ Management:** http://localhost:15672
- **Adminer (DB):** http://localhost:8080
