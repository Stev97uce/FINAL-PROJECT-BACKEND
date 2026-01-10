# CONTEXTO DEL PROYECTO - Sistema de Gestión de Consultantes UCE

## 📋 INFORMACIÓN GENERAL

**Proyecto:** Sistema de Gestión de Consultantes y Agendamiento para la Facultad de Psicología
**Institución:** Universidad Central del Ecuador
**Tipo:** Sistema de Microservicios en AWS
**Estado Actual:** Fase de Infraestructura (Terraform)

---

## 🎯 OBJETIVO DEL PROYECTO

Desarrollar un sistema integral de gestión de consultantes y agendamiento para servicios de atención psicológica, implementado como arquitectura de microservicios desplegada en AWS con alta disponibilidad, seguridad y escalabilidad.

---

## 🏗️ ARQUITECTURA GENERAL

### Estilo Arquitectónico
- **Microservicios:** 10 servicios independientes
- **Event-Driven:** Comunicación asíncrona con RabbitMQ
- **CQRS:** Separación de comandos y consultas
- **Layered Architecture:** 4 capas por microservicio (API, Service, Domain, Infrastructure)

### Patrones de Diseño
- **SOLID:** Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **DRY:** Don't Repeat Yourself
- **KISS:** Keep It Simple, Stupid
- **YAGNI:** You Aren't Gonna Need It

---

## 🔢 LOS 10 MICROSERVICIOS

| # | Servicio | Lenguaje | Base de Datos | Responsabilidad |
|---|----------|----------|---------------|-----------------|
| 1 | Auth Service | Python/FastAPI | MySQL + Redis | Autenticación, JWT, verificación email |
| 2 | User Service | Python/FastAPI | PostgreSQL | Perfiles de usuario, roles, permisos |
| 3 | Patient Service | Python/FastAPI | PostgreSQL | Gestión de consultantes, expedientes |
| 4 | Appointment Service | Go/Gin | PostgreSQL + Redis | Agendamiento, calendario, disponibilidad |
| 5 | Room Service | Go/Gin | PostgreSQL + Redis | Gestión de espacios físicos, consultorios |
| 6 | Clinical Service | Python/FastAPI | MongoDB | Notas de sesión, objetivos terapéuticos |
| 7 | Supervision Service | Go/Gin | PostgreSQL | Supervisión académica estudiante-supervisor |
| 8 | Notification Service | Python/FastAPI | MongoDB + Redis | Email, WhatsApp, notificaciones internas |
| 9 | Reporting Service | Python/FastAPI | PostgreSQL | Reportes operativos, exportación |
| 10 | Analytics Service | Go/Gin | MongoDB + Redis | Dashboards, métricas, visualizaciones |

---

## 🗄️ BASES DE DATOS

### MySQL 8.0
- **Uso:** Auth Service
- **Ubicación:** Cuenta 1, IP Elástica 10.1.0.10:3306
- **Propósito:** Datos transaccionales críticos de autenticación

### PostgreSQL 14+
- **Uso:** User, Patient, Appointment, Room, Supervision, Reporting Services
- **Ubicación:** Cuenta 1, IP Elástica 10.1.0.11:5432
- **Propósito:** Datos relacionales estructurados con búsquedas complejas

### MongoDB 6.0
- **Uso:** Clinical, Notification, Analytics Services
- **Ubicación:** Cuenta 1, IP Elástica 10.1.0.12:27017
- **Propósito:** Documentos flexibles sin esquema rígido

### Redis 7.0
- **Uso:** Todos los servicios (caché)
- **Ubicación:** Cuenta 1, IP Elástica 10.1.0.13:6379
- **Propósito:** Caché de alta velocidad, colas en memoria, rate limiting

---

## 📡 PROTOCOLOS DE COMUNICACIÓN

### 1. REST API
- Comunicación síncrona cliente-servidor
- Endpoints versionados: `/api/v1/...`
- Autenticación: JWT en header `Authorization: Bearer {token}`

### 2. RabbitMQ (Event-Driven)
- Comunicación asíncrona entre microservicios
- Exchange: `uce_events` (type: topic, durable: true)
- Routing keys: `{aggregate}.{action}` (ej: `user.registered`)
- Ubicación: Cuenta 1, 10.1.0.14:5672

### 3. MQTT (Mosquitto)
- Notificaciones en tiempo real
- Topics: `uce/notifications/{user_id}`
- Ubicación: Cuenta 1, 10.1.0.15:1883

### 4. Webhooks
- Integraciones con sistemas externos
- Retry con backoff exponencial
- Firma HMAC para autenticidad

---

## ☁️ INFRAESTRUCTURA AWS - ESTRATEGIA MULTI-CUENTA

### CUENTA 1: Bases de Datos (Permanente, Sin Terraform)
- **EC2:** 6 instancias con IPs Elásticas fijas
  - MySQL (t3.medium)
  - PostgreSQL (t3.medium)
  - MongoDB (t3.medium)
  - Redis (t3.small)
  - RabbitMQ (t3.small)
  - MQTT/Mosquitto (t3.small)
- **Configuración:** Manual, nunca se destruyen
- **Volúmenes:** EBS 50GB GP3 para datos persistentes

### CUENTAS 2-6: Producción (Con Terraform)
Cada cuenta aloja 2 microservicios con alta disponibilidad:

**Configuración por microservicio:**
- 3 EC2 instancias (t3.small) en Auto Scaling Group
- 1 Application Load Balancer
- Subnet pública (ALB) + Subnet privada (EC2s)
- Desired: 2, Min: 1, Max: 3 instancias
- Scaling: CPU > 70% → +1 instancia, CPU < 30% → -1 instancia

**Distribución:**
- **Cuenta 2:** Auth Service + User Service
- **Cuenta 3:** Patient Service + Appointment Service
- **Cuenta 4:** Room Service + Clinical Service
- **Cuenta 5:** Supervision Service + Notification Service
- **Cuenta 6:** Reporting Service + Analytics Service

### CUENTAS 7-9: QA (Con Terraform, Sin Alta Disponibilidad)
- **Cuenta 7:** 4 microservicios (1 EC2 c/u): Auth, User, Patient, Appointment
- **Cuenta 8:** 4 microservicios (1 EC2 c/u): Room, Clinical, Supervision, Notification
- **Cuenta 9:** 2 microservicios (1 EC2 c/u): Reporting, Analytics
- Sin ALB, sin ASG, configuración simplificada

### CUENTA 10: Infraestructura Compartida
- **EC2-1:** NGINX API Gateway (Producción) - IP Elástica
- **EC2-2:** NGINX API Gateway (QA) - IP Elástica
- **EC2-3:** Prometheus (métricas)
- **EC2-4:** Grafana (dashboards)
- **EC2-5:** Bastion Host (SSH acceso seguro) - IP Elástica
- **EC2-6:** Site 24x7 Agent (monitoreo externo)

### CUENTAS 11-15: Reserva
- Disaster recovery
- Staging adicional
- Escalamiento futuro

---

## 🌐 ARQUITECTURA DE RED

### VPC Producción (10.0.0.0/16)
- **Subnet Pública (10.0.1.0/24):** ALBs, NAT Gateway
- **Subnet Privada (10.0.10.0/24):** EC2 microservicios
- **Internet Gateway:** Acceso a Internet
- **NAT Gateway:** Salida desde subnet privada
- **Route Tables:** Routing diferenciado público/privado

### VPC QA (10.1.0.0/16)
- **Subnet Pública (10.1.1.0/24):** EC2 microservicios
- **Subnet Privada (10.1.10.0/24):** Acceso a bases de datos
- Configuración simplificada

### VPC Peering
- VPC Producción ↔ Cuenta 1 (Databases)
- VPC QA ↔ Cuenta 1 (Databases)
- VPC Producción ↔ Cuenta 10 (Monitoring)
- VPC QA ↔ Cuenta 10 (Monitoring)

---

## 🔒 SEGURIDAD

### Capas de Defensa
1. **CloudFlare WAF:** Protección perimetral (DDoS, SQL Injection, XSS)
2. **API Gateway (NGINX):** Rate limiting, validación
3. **Security Groups:** Firewall a nivel de red
4. **JWT Authentication:** Tokens firmados HS256
5. **Bastion Host:** Único punto acceso SSH

### Security Groups Principales

**SG-ALB-Prod:**
- Inbound: 80/TCP, 443/TCP from 0.0.0.0/0
- Outbound: 8000-8009/TCP to SG-Microservices

**SG-Microservices-Prod:**
- Inbound: 8000-8009/TCP from SG-ALB, 22/TCP from SG-Bastion
- Outbound: All to databases, RabbitMQ, Internet

**SG-Database:**
- Inbound: 3306/TCP (MySQL), 5432/TCP (PostgreSQL), 27017/TCP (MongoDB), 6379/TCP (Redis), 5672/TCP (RabbitMQ) from SG-Microservices
- Inbound: 22/TCP from SG-Bastion

**SG-Bastion:**
- Inbound: 22/TCP from IPs autorizadas (Universidad, desarrolladores)
- Outbound: 22/TCP to todos los SGs

---

## 🛠️ STACK TECNOLÓGICO

### Backend
- **Python 3.11+:** FastAPI framework
- **Go 1.21+:** Gin framework
- **Dependencias Python:** pydantic, sqlalchemy, aiomysql, pymongo, pika, redis, bcrypt, pyjwt
- **Dependencias Go:** gin, gorm, go-redis, amqp

### Bases de Datos
- MySQL 8.0, PostgreSQL 14, MongoDB 6.0, Redis 7.0

### Infraestructura
- **IaC:** Terraform 1.5+
- **Containerización:** Docker
- **Registry:** DockerHub
- **CI/CD:** GitHub Actions
- **Monorepo:** Turborepo

### Monitoreo
- **Métricas:** Prometheus
- **Visualización:** Grafana
- **Monitoreo Externo:** Site 24x7

### Notificaciones
- **Email:** SMTP (SendGrid)
- **WhatsApp:** Twilio API

---

## 📁 ESTRUCTURA DE REPOSITORIOS

### Monorepo Backend
```
backend-monorepo/
├── apps/
│   ├── auth-service/
│   ├── user-service/
│   ├── patient-service/
│   ├── appointment-service/
│   ├── room-service/
│   ├── clinical-service/
│   ├── supervision-service/
│   ├── notification-service/
│   ├── reporting-service/
│   └── analytics-service/
├── packages/
│   ├── shared-types/
│   ├── shared-utils/
│   └── shared-config/
├── infrastructure/
│   └── terraform/
│       ├── modules/
│       ├── production/
│       ├── qa/
│       └── infrastructure/
├── turbo.json
└── package.json

Ramas: main, qa, production
```

### Monorepo Frontend
```
frontend-monorepo/
├── apps/
│   ├── web/          (React/Next.js)
│   ├── mobile/       (React Native)
│   └── desktop/      (Electron/Tauri)
├── packages/
│   ├── ui-components/
│   ├── shared-hooks/
│   └── api-client/
├── turbo.json
└── package.json

Ramas: main, qa, production
```

---

## 🚀 TERRAFORM - ESTRUCTURA

### Estructura de Directorios
```
infrastructure/terraform/
├── modules/
│   ├── vpc/
│   ├── security-group/
│   ├── ec2-microservice/
│   ├── alb/
│   ├── asg/
│   ├── s3/
│   └── iam/
├── production/
│   ├── account-02-auth-user/
│   ├── account-03-patient-appointment/
│   ├── account-04-room-clinical/
│   ├── account-05-supervision-notification/
│   └── account-06-reporting-analytics/
├── qa/
│   ├── account-07/
│   ├── account-08/
│   └── account-09/
└── infrastructure/
    └── account-10-shared/
```

### Requisitos por Cuenta de Producción (2-6)

**Recursos a crear con Terraform:**
1. **VPC:** CIDR 10.0.0.0/16
2. **Subnets:**
   - Pública: 10.0.1.0/24 (ALBs)
   - Privada: 10.0.10.0/24 (EC2s)
3. **Internet Gateway**
4. **NAT Gateway** con Elastic IP
5. **Route Tables:** Pública y Privada
6. **Security Groups:** SG-ALB, SG-Microservices
7. **2 Application Load Balancers** (1 por microservicio)
8. **2 Target Groups** (puerto 8000 y 8001)
9. **2 Auto Scaling Groups** (min: 1, desired: 2, max: 3)
10. **2 Launch Templates:**
    - AMI: Ubuntu 22.04 LTS
    - Instance Type: t3.small
    - User Data: instala Docker, pull imagen, run container
11. **CloudWatch Alarms:** CPU scaling policies
12. **S3 Buckets:** 
    - `uce-psicologia-terraform-state` (state backend)
    - `uce-psicologia-prod-static` (archivos)
    - `uce-psicologia-backups` (backups)

### Variables Clave
```hcl
variable "aws_region" {
  default = "us-east-1"
}

variable "environment" {
  description = "production | qa"
}

variable "account_number" {
  description = "02-06 for prod, 07-09 for qa"
}

variable "microservice_1_name" {
  description = "e.g. auth-service"
}

variable "microservice_1_port" {
  default = 8000
}

variable "microservice_1_docker_image" {
  description = "dockerhub-user/auth-service:latest"
}

variable "microservice_2_name" {
  description = "e.g. user-service"
}

variable "microservice_2_port" {
  default = 8001
}

variable "microservice_2_docker_image" {
  description = "dockerhub-user/user-service:latest"
}

# Database connection (from Cuenta 1)
variable "mysql_host" {
  default = "10.1.0.10"
}

variable "postgresql_host" {
  default = "10.1.0.11"
}

variable "mongodb_host" {
  default = "10.1.0.12"
}

variable "redis_host" {
  default = "10.1.0.13"
}

variable "rabbitmq_host" {
  default = "10.1.0.14"
}
```

---

## 📊 FLUJOS DE NEGOCIO PRINCIPALES

### Registro y Primera Cita
1. Consultante completa formulario → Auth Service
2. Auth valida datos únicos, hashea password, crea usuario pendiente
3. Emite evento `user.registered`
4. User Service crea perfil extendido
5. Notification Service envía email verificación
6. Consultante verifica email → Auth Service marca activo
7. Emite evento `user.verified`
8. Consultante completa perfil → User Service
9. Consultante accede a calendario → Appointment Service
10. Selecciona fecha/hora → Appointment crea cita
11. Emite evento `appointment.created`
12. Room Service asigna consultorio
13. Notification Service envía confirmación email + WhatsApp
14. 48h antes: recordatorio automático
15. 24h antes: segundo recordatorio

### Supervisión Clínica
1. Estudiante completa sesión, accede a Clinical Service
2. Selecciona plantilla, completa campos (resumen, técnicas, tareas)
3. Clinical Service valida completitud, guarda nota
4. Emite evento `clinical.session_recorded`
5. Supervision Service identifica supervisor asignado
6. Notification Service notifica a supervisor
7. Supervisor accede, lee nota y contexto
8. Supervisor agrega comentarios, fortalezas, áreas de mejora
9. Supervision Service guarda feedback, marca revisada
10. Emite evento `supervision.feedback_added`
11. Clinical Service vincula feedback a nota
12. Notification Service notifica a estudiante
13. Estudiante lee retroalimentación, marca como leída

---

## 🎨 FRONTEND (Multiplataforma)

### Web (React/Next.js)
- Responsive design
- Server-side rendering
- Optimizado SEO

### Mobile (React Native)
- iOS y Android nativo
- Notificaciones push
- Acceso offline limitado

### Desktop (Electron/Tauri)
- Windows, macOS, Linux
- Acceso a archivos locales
- Integración sistema operativo

---

## 🧪 TESTING

### Tipos de Pruebas
- **Unitarias:** pytest (Python), testify (Go)
- **Integración:** Pruebas de API endpoints
- **Carga:** JMeter, Locust
- **E2E:** Playwright (frontend)

### Cobertura Objetivo
- Service Layer: 80%
- Domain Layer: 80%
- API Layer: 70%
- Infrastructure Layer: 60%

---

## 📦 CI/CD (GitHub Actions)

### Pipeline Backend
1. **Lint:** pylint, golangci-lint
2. **Test:** pytest, go test
3. **Build:** Docker build
4. **Push:** DockerHub
5. **Deploy QA:** Terraform apply (automático)
6. **Deploy Prod:** Terraform apply (manual approval)

### Stages
- **Develop → QA:** Automático
- **QA → Production:** Manual con aprobación

---

## 📝 CONVENCIONES

### Git
- **Conventional Commits:** `feat:`, `fix:`, `docs:`, `refactor:`
- **Branches:** `feature/`, `bugfix/`, `hotfix/`
- **Pull Requests:** Requeridos, al menos 1 aprobación

### Código
- **Python:** PEP 8, type hints, docstrings
- **Go:** gofmt, go vet, effective go
- **Naming:** snake_case (Python), camelCase (Go)

### APIs
- **Versionado:** `/api/v1/...`
- **Status Codes:** 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 404 (Not Found), 500 (Server Error)
- **Respuestas:**
```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful"
}
```

---

## 🎯 FASE ACTUAL: TERRAFORM INFRASTRUCTURE

### Objetivo Inmediato
Crear toda la infraestructura AWS funcional usando Terraform para ambientes de Producción (Cuentas 2-6) y QA (Cuentas 7-9).

### Entregables
1. Módulos reutilizables de Terraform
2. Configuración completa para Cuenta 2 (Auth + User)
3. VPC, Subnets, IGW, NAT Gateway
4. Security Groups configurados
5. ALBs y ASGs funcionales
6. Launch Templates con User Data
7. State backend en S3
8. Documentación de despliegue

### Próximos Pasos (después de infraestructura)
1. Desarrollo de Auth Service (Python/FastAPI)
2. Desarrollo de User Service (Python/FastAPI)
3. Implementación de RabbitMQ event bus
4. Configuración de bases de datos en Cuenta 1
5. CI/CD con GitHub Actions
6. Monitoreo con Prometheus/Grafana

---

## 📞 INFORMACIÓN IMPORTANTE

- **Región AWS:** us-east-1
- **AMI Base:** Ubuntu 22.04 LTS (ami-0c55b159cbfafe1f0 o similar)
- **Timezone:** America/Guayaquil (Ecuador)
- **Límites Académicos:** Máximo 6 EC2 por cuenta
- **Budget:** Recursos académicos gratuitos/subsidiados

---

## 🔗 RECURSOS Y DOCUMENTACIÓN

- AWS Free Tier: https://aws.amazon.com/free/
- Terraform AWS Provider: https://registry.terraform.io/providers/hashicorp/aws/
- FastAPI Docs: https://fastapi.tiangolo.com/
- Gin Framework: https://gin-gonic.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- GORM: https://gorm.io/
- RabbitMQ: https://www.rabbitmq.com/
- Prometheus: https://prometheus.io/

---

## ⚠️ CONSIDERACIONES IMPORTANTES

1. **Cuenta 1 es MANUAL:** No usar Terraform, IPs elásticas fijas
2. **Límite 6 EC2/cuenta:** Respetar estrictamente
3. **State S3:** Usar locking con DynamoDB
4. **Secrets:** Nunca commitear credenciales
5. **Costos:** Monitorear uso para mantenerse en free tier
6. **Backups:** Automatizar diariamente
7. **Security Groups:** Principio de mínimo privilegio
8. **Tags:** Todos los recursos deben tener tags (Environment, Project, ManagedBy)

---

**Última actualización:** 2024-12-30
**Versión:** 1.0
**Responsable:** Equipo de Desarrollo UCE Psicología