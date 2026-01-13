# Sistema UCE - Backend Microservicios

Sistema de gestión de consultantes y agendamiento para la Facultad de Psicología UCE.

## Descripción

Monorepo de microservicios construido con Turborepo, Python/FastAPI y Go/Gin para la gestión integral de consultantes, agendamiento y supervisión clínica.

## Estructura del Proyecto

```
FINAL-PROJECT-BACKEND/
├── apps/
│   ├── Micro1_Auth_Service/        ✅ Autenticación JWT (Python/FastAPI + MySQL)
│   ├── Micro2_User_Service/        ✅ Gestión de usuarios (Python/FastAPI + PostgreSQL)
│   ├── Micro3_Patient_Service/     ✅ Gestión de pacientes (Python/FastAPI + PostgreSQL)
│   ├── Micro4_Appointment_Service/ ✅ Agendamiento y citas (Go/Gin + PostgreSQL + Redis)
│   ├── Micro5_Room_Service/        ✅ Gestión de espacios (Go/Gin + PostgreSQL + Redis)
│   ├── Micro6_Clinical_Service/    ✅ Notas clínicas (Python/FastAPI + MongoDB)
│   └── Micro7_Supervision_Service/ ✅ Supervisión académica (Python/FastAPI + PostgreSQL)
├── packages/                       Paquetes compartidos (por implementar)
├── .github/workflows/              CI/CD con GitHub Actions
├── docker-compose.yml              Configuración Docker global
├── package.json                    Scripts de Turborepo
└── turbo.json                      Configuración de tareas
```

## Microservicios Implementados

| # | Servicio | Puerto | Estado | Tecnología | Base de Datos |
|---|----------|--------|--------|------------|---------------|
| 1 | Auth Service | 8000 | ✅ Completo | Python/FastAPI | MySQL 8.0 |
| 2 | User Service | 8001 | ✅ Completo | Python/FastAPI | PostgreSQL 14 |
| 3 | Patient Service | 8002 | ✅ Completo | Python/FastAPI | PostgreSQL 14 |
| 4 | Appointment Service | 8003 | ✅ Completo | Go/Gin | PostgreSQL 14 + Redis |
| 5 | Room Service | 8004 | ✅ Completo | Go/Gin | PostgreSQL 14 + Redis |
| 6 | Clinical Service | 8005 | ✅ Completo | Python/FastAPI | MongoDB 6.0 |
| 7 | Supervision Service | 8006 | ✅ Completo | Python/FastAPI | PostgreSQL 14 |
| 8 | Notification Service | 8007 | 🔄 Pendiente | Python/FastAPI | MongoDB 6.0 |
| 9 | Reporting Service | 8008 | 🔄 Pendiente | Python/FastAPI | PostgreSQL 14 |
| 10 | Analytics Service | 8009 | 🔄 Pendiente | Python/FastAPI | MongoDB 6.0 |

## Tecnologías

- **Turborepo** - Monorepo build system
- **Python 3.11+** / **FastAPI** - Microservicios Python
- **Go 1.21+** / **Gin** - Microservicios Go
- **MySQL 8.0** - Base de datos auth-service
- **PostgreSQL 14** - Base de datos servicios principales
- **MongoDB 6.0** - Base de datos documentos
- **Redis 7.0** - Cache y sesiones
- **RabbitMQ 3** - Message broker
- **Docker** - Containerización

## Instalación

### Prerequisitos

- Node.js 18+
- Python 3.11+
- Go 1.21+
- Docker Desktop

### Setup

```bash
# Instalar dependencias de Turborepo
npm install

# Configurar variables de entorno del auth-service
cd apps/auth-service
cp .env.template .env
# Editar .env con tus credenciales

# Levantar bases de datos
cd ../..
npm run docker:up
```

## Comandos Disponibles

### Desarrollo

```bash
# Ejecutar todos los servicios
npm run dev

# Ejecutar auth-service
npm run auth:dev

# O con Turbo directamente
turbo run dev --filter=auth-service
```

### Docker

```bash
# Levantar servicios
npm run docker:up

# Detener servicios
npm run docker:down

# Ver logs
npm run docker:logs

# Construir imágenes
npm run docker:build
```

### Testing

```bash
# Ejecutar tests
npm run test

# Tests de un servicio específico
turbo run test --filter=auth-service
```

### Linting y Formateo

```bash
npm run lint
npm run format
```

## Microservicios

### Implementados

1. **auth-service** (Python/FastAPI + MySQL)
   - Autenticación y autorización
   - Gestión de usuarios
   - JWT tokens
   - Verificación de email
   - Recuperación de contraseña

### Por Implementar

2. user-service (Python/FastAPI + PostgreSQL)
3. patient-service (Python/FastAPI + PostgreSQL)
4. appointment-service (Go/Gin + PostgreSQL)
5. room-service (Go/Gin + PostgreSQL)
6. clinical-service (Python/FastAPI + MongoDB)
7. supervision-service (Go/Gin + PostgreSQL)
8. notification-service (Python/FastAPI + MongoDB)
9. reporting-service (Python/FastAPI + PostgreSQL)
10. analytics-service (Go/Gin + MongoDB)

## Documentación

- Auth Service: [apps/auth-service/README.md](apps/auth-service/README.md)
- API Swagger: http://localhost:8000/docs (después de iniciar)

## Licencia

MIT
cd my-turborepo

# With [global `turbo`](https://turborepo.com/docs/getting-started/installation#global-installation) installed (recommended)
turbo login

# Without [global `turbo`](https://turborepo.com/docs/getting-started/installation#global-installation), use your package manager
npx turbo login
yarn exec turbo login
pnpm exec turbo login
```

This will authenticate the Turborepo CLI with your [Vercel account](https://vercel.com/docs/concepts/personal-accounts/overview).

Next, you can link your Turborepo to your Remote Cache by running the following command from the root of your Turborepo:

```
# With [global `turbo`](https://turborepo.com/docs/getting-started/installation#global-installation) installed (recommended)
turbo link

# Without [global `turbo`](https://turborepo.com/docs/getting-started/installation#global-installation), use your package manager
npx turbo link
yarn exec turbo link
pnpm exec turbo link
```

## Useful Links

Learn more about the power of Turborepo:

- [Tasks](https://turborepo.com/docs/crafting-your-repository/running-tasks)
- [Caching](https://turborepo.com/docs/crafting-your-repository/caching)
- [Remote Caching](https://turborepo.com/docs/core-concepts/remote-caching)
- [Filtering](https://turborepo.com/docs/crafting-your-repository/running-tasks#using-filters)
- [Configuration Options](https://turborepo.com/docs/reference/configuration)
- [CLI Usage](https://turborepo.com/docs/reference/command-line-reference)
