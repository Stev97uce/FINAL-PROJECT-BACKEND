# 🏥 Sistema UCE - Microservicio de Autenticación

Sistema de gestión de consultantes y agendamiento para la Facultad de Psicología UCE.

## 📁 Estructura del Proyecto

```
Micro1_Auth/
├── BACKEND/           # Microservicio de autenticación (FastAPI + MySQL)
│   ├── app/          # Código fuente
│   ├── *.py          # Scripts de utilidad
│   ├── *.md          # Documentación
│   └── *.json        # Colección de Postman
│
└── FRONTEND/         # Interface de usuario (En desarrollo)
```

## 🚀 Estado del Proyecto

### ✅ BACKEND - Completado
- [x] Arquitectura REST + Event-Driven
- [x] 8 endpoints de autenticación
- [x] Base de datos MySQL con 3 tablas
- [x] JWT + BCrypt para seguridad
- [x] Integración con RabbitMQ
- [x] Validación de roles y permisos
- [x] Documentación Swagger automática
- [x] Colección de Postman para pruebas
- [x] Docker ready

### 🔜 FRONTEND - Pendiente
- [ ] Interfaz de usuario
- [ ] Formularios de registro/login
- [ ] Dashboard de usuario
- [ ] (Se desarrollará después de probar el backend)

## 🛠️ Tecnologías

### Backend
- **Python 3.11+**
- **FastAPI** - Framework web moderno
- **MySQL 8.0** - Base de datos relacional
- **RabbitMQ** - Message broker (eventos)
- **JWT** - Autenticación con tokens
- **BCrypt** - Hashing de contraseñas
- **SQLAlchemy** - ORM
- **Pydantic** - Validación de datos

### Infraestructura
- **Docker** - Containerización
- **Docker Compose** - Orquestación local
- **AWS** - Despliegue en producción (futuro)

## 📖 Documentación

- **[BACKEND/README.md](BACKEND/README.md)** - Documentación técnica completa
- **[BACKEND/GUIA_RAPIDA.md](BACKEND/GUIA_RAPIDA.md)** - Guía de inicio rápido
- **[BACKEND/database_setup.sql](BACKEND/database_setup.sql)** - Script de BD
- **Swagger UI**: http://localhost:8000/docs (después de iniciar)

## ⚡ Inicio Rápido

### 1. Configurar Base de Datos
```sql
mysql -u root -p < BACKEND/database_setup.sql
```

### 2. Configurar Variables de Entorno
```powershell
cd BACKEND
# Editar .env con tus credenciales de MySQL
```

### 3. Iniciar el Servidor
```powershell
cd BACKEND
python run.py
```

### 4. Probar con Postman
1. Importar `BACKEND/UCE_Auth_Service.postman_collection.json`
2. Ejecutar "Health Check"
3. Seguir la guía de pruebas

## 🔐 Credenciales de Prueba

**Usuario Administrador** (pre-configurado):
- Email: `admin@uce.edu.ec`
- Password: `Admin123`
- Rol: `administrador`

## 📡 Endpoints Principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/auth/register` | POST | Registrar consultante |
| `/api/auth/register-staff` | POST | Registrar personal (requiere admin) |
| `/api/auth/verify-email/{token}` | GET | Verificar email |
| `/api/auth/login` | POST | Iniciar sesión |
| `/api/auth/validate` | GET | Validar token |
| `/api/auth/forgot-password` | POST | Recuperar contraseña |
| `/api/auth/reset-password` | POST | Restablecer contraseña |
| `/api/auth/refresh` | POST | Renovar access token |
| `/api/auth/logout` | POST | Cerrar sesión |

## 🎯 Roles de Usuario

1. **consultante** - Auto-registro permitido
2. **recepcionista** - Registro por admin
3. **estudiante** - Registro por admin
4. **psicologo_supervisor** - Registro por admin
5. **administrador** - Registro por admin

## 📊 Eventos Emitidos

El microservicio emite eventos a través de RabbitMQ:

1. `user.registered` - Cuando un usuario se registra
2. `user.verified` - Cuando se verifica el email
3. `password.reset_requested` - Cuando se solicita recuperación

Estos eventos serán consumidos por otros microservicios (Notification Service, User Service, etc.)

## 🧪 Pruebas

### Con Postman
1. Importar colección
2. Ejecutar requests en orden
3. Los tokens se guardan automáticamente

### Con Swagger UI
1. Ir a http://localhost:8000/docs
2. Usar interfaz interactiva
3. Autenticación con botón "Authorize"

### Con Script Python
```powershell
cd BACKEND
python get_tokens.py verify  # Ver último token de verificación
python get_tokens.py users   # Listar usuarios
```

## 🐛 Troubleshooting

Ver **[BACKEND/GUIA_RAPIDA.md](BACKEND/GUIA_RAPIDA.md)** para solución de problemas comunes.

## 📝 Próximos Pasos

1. ✅ Probar todos los endpoints con Postman
2. ⏳ Verificar logs y comportamiento
3. ⏳ Optimizar rendimiento si es necesario
4. ⏳ Desarrollar Frontend (cuando tú lo indiques)
5. ⏳ Integrar con otros microservicios
6. ⏳ Desplegar en AWS

## 👨‍💻 Desarrollo

Este es el **Microservicio #1** de un sistema de 10 microservicios.

**Principios de diseño:**
- ✅ KISS (Keep It Simple, Stupid)
- ✅ Separación de responsabilidades
- ✅ Event-Driven Architecture
- ✅ RESTful API
- ✅ Seguridad por diseño

## 📧 Contacto

Para dudas o problemas, revisar la documentación en `BACKEND/README.md` o `BACKEND/GUIA_RAPIDA.md`.

---

**Estado**: 🟢 Backend Listo para Pruebas | 🟡 Frontend Pendiente
