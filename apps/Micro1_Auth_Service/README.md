# Sistema UCE - Microservicio de Autenticacion

Sistema de gestión de consultantes y agendamiento para la Facultad de Psicología UCE.

## Estructura del Proyecto

```
auth-service/
├── app/              # Codigo fuente
│   ├── routes/      # Endpoints
│   ├── models.py    # Modelos SQLAlchemy
│   ├── schemas.py   # Schemas Pydantic
│   ├── security.py  # JWT y BCrypt
│   └── events.py    # RabbitMQ publisher
├── *.py             # Scripts de utilidad
├── *.md             # Documentacion
└── *.sql            # Scripts de BD
```

## Estado del Proyecto

### BACKEND - Completado
- [x] Arquitectura REST + Event-Driven
- [x] 8 endpoints de autenticacion
- [x] Base de datos MySQL con 3 tablas
- [x] JWT + BCrypt para seguridad
- [x] Integracion con RabbitMQ
- [x] Validacion de roles y permisos
- [x] Documentacion Swagger automatica
- [x] Coleccion de Postman para pruebas
- [x] Docker ready

### FRONTEND - Pendiente
- [ ] Interfaz de usuario
- [ ] Formularios de registro/login
- [ ] Dashboard de usuario
- [ ] (Se desarrollara despues de probar el backend)

## Tecnologias

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

## Documentacion

- **[README2.md](README2.md)** - Documentacion tecnica completa
- **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** - Guia de inicio rapido
- **[database_setup.sql](database_setup.sql)** - Script de BD
- **Swagger UI**: http://localhost:8000/docs (despues de iniciar)

## Inicio Rapido

### 1. Configurar Base de Datos
```sql
mysql -u root -p < database_setup.sql
```

### 2. Configurar Variables de Entorno
```powershell
# Copiar el template y editar con tus credenciales
cp .env.template .env
```

### 3. Iniciar el Servidor
```powershell
python run.py
```

### 4. Probar la API
- Swagger UI: http://localhost:8000/docs
- Importar coleccion Postman si existe
- Ejecutar Health Check

## Credenciales de Prueba

**Usuario Administrador** (pre-configurado):
- Email: `admin@uce.edu.ec`
- Password: `Admin123`
- Rol: `administrador`

## Endpoints Principales

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
| `/api/auth/logout` | POST | Cerrar sesion |

## Roles de Usuario

1. **consultante** - Auto-registro permitido
2. **recepcionista** - Registro por admin
3. **estudiante** - Registro por admin
4. **psicologo_supervisor** - Registro por admin
5. **administrador** - Registro por admin

## Eventos Emitidos

El microservicio emite eventos a traves de RabbitMQ:

1. `user.registered` - Cuando un usuario se registra
2. `user.verified` - Cuando se verifica el email
3. `password.reset_requested` - Cuando se solicita recuperacion

Estos eventos seran consumidos por otros microservicios (Notification Service, User Service, etc.)

## Pruebas

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
python get_tokens.py verify  # Ver ultimo token de verificacion
python get_tokens.py users   # Listar usuarios
```

## Troubleshooting

Ver **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** para solucion de problemas comunes.

## Proximos Pasos

1. [x] Probar todos los endpoints
2. [ ] Verificar logs y comportamiento
3. [ ] Optimizar rendimiento si es necesario
4. [ ] Integrar con otros microservicios
5. [ ] Desplegar en AWS

## Desarrollo

Este es el **Microservicio #1** de un sistema de 10 microservicios.

**Principios de diseno:**
- KISS (Keep It Simple, Stupid)
- Separacion de responsabilidades
- Event-Driven Architecture
- RESTful API
- Seguridad por diseno

## Contacto

Para dudas o problemas, revisar la documentacion en los archivos MD incluidos.

---

**Estado**: Backend Listo para Pruebas | Frontend Pendiente
