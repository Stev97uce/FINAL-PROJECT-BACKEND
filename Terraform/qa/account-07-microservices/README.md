# 🚀 Cuenta 7 - Microservicios Grupo 1 (QA)

Terraform para desplegar Auth, User, Patient y Appointment services en AWS QA environment.

## 📋 Descripción

Esta configuración de Terraform despliega 4 microservicios en la Cuenta 7:
- **Auth Service** (10.7.11.10:8000) - Autenticación y autorización
- **User Service** (10.7.11.11:8001) - Gestión de usuarios
- **Patient Service** (10.7.11.12:8002) - Gestión de pacientes
- **Appointment Service** (10.7.11.13:8003) - Gestión de citas

## 🏗️ Arquitectura

```
Cuenta 7 (10.7.0.0/16)
├── VPC con 4 subnets (2 públicas + 2 privadas)
├── NAT Gateway + Internet Gateway
├── 4 EC2 Instances (t3.small) en subnets privadas
├── 4 Security Groups (uno por servicio)
└── VPC Peering:
    ├── Cuenta 10 (Infraestructura) - RabbitMQ, API Gateway
    └── Cuenta 1 (Databases) - MySQL, PostgreSQL, Redis
```

## 📦 Recursos Creados

- 1 VPC (10.7.0.0/16)
- 4 Subnets (2 públicas + 2 privadas)
- 1 Internet Gateway
- 1 NAT Gateway + Elastic IP
- 2 Route Tables
- 4 Security Groups
- 4 EC2 Instances (t3.small, Ubuntu 22.04)
- 1 Key Pair (importado)
- 2 VPC Peering Connections

**Total: ~25 recursos**

## 🔧 Prerequisitos

### 1. Docker Images en DockerHub

**⚠️ IMPORTANTE:** Las imágenes Docker deben estar construidas y pusheadas a DockerHub ANTES de ejecutar Terraform.

```bash
# Desde el root del proyecto

# Auth Service
cd apps/Micro1_Auth_Service
docker build -t stevxd97/uce-auth-service:qa .
docker push stevxd97/uce-auth-service:qa

# User Service
cd ../Micro2_User_Service
docker build -t stevxd97/uce-user-service:qa .
docker push stevxd97/uce-user-service:qa

# Patient Service
cd ../Micro3_Patient_Service
docker build -t stevxd97/uce-patient-service:qa .
docker push stevxd97/uce-patient-service:qa

# Appointment Service
cd ../Micro4_Appointment_Service
docker build -t stevxd97/uce-appointment-service:qa .
docker push stevxd97/uce-appointment-service:qa
```

### 2. Infraestructura Previa

Deben estar desplegadas:
- ✅ **Cuenta 10 (Infraestructura)** - Bastion, RabbitMQ, API Gateway
- ✅ **Cuenta 1 (Databases)** - MySQL, PostgreSQL, Redis

### 3. Credenciales AWS

Configurar credenciales para la Cuenta 7 (Microservicios 1).

## 🚀 Deployment

### Paso 1: Configurar Terraform

```bash
cd terraform/qa/account-07-microservices
```

### Paso 2: Inicializar Terraform

```bash
terraform init
```

### Paso 3: Revisar Variables

Verificar `terraform.tfvars`:
- VPC IDs de Cuentas 10 y 1
- Account IDs correctos
- IPs de bases de datos y servicios
- Nombres de imágenes Docker

### Paso 4: Plan

```bash
# Configurar credenciales AWS para Cuenta 7
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."

# Ejecutar plan
terraform plan -out=tfplan
```

### Paso 5: Revisar el Plan

Verificar que se van a crear:
- 4 EC2 instances con IPs correctas
- Security groups con reglas apropiadas
- VPC peering connections
- Rutas correctas

### Paso 6: Apply

```bash
terraform apply tfplan
```

**Tiempo estimado:** 5-7 minutos

## 🔗 Post-Deployment

### 1. Aceptar VPC Peering

#### En Cuenta 10 (Infraestructura):

```bash
cd terraform/qa/account-10-infrastructure

# Editar terraform.tfvars
account_07_id = "..." # Account ID de Cuenta 7
account_07_vpc_id = "vpc-..." # VPC ID de Cuenta 7

# Re-aplicar
terraform apply
```

#### En Cuenta 1 (Databases):

```bash
cd terraform/qa/account-01-databases

# Editar terraform.tfvars (si no está ya)
account_07_id = "..." # Account ID de Cuenta 7
account_07_vpc_id = "vpc-..." # VPC ID de Cuenta 7

# Re-aplicar
terraform apply
```

### 2. Verificar Microservicios

SSH al Bastion:
```bash
ssh -i ../shared/finalkey.pem ubuntu@34.199.65.203
```

Desde el Bastion, verificar cada microservicio:

```bash
# Auth Service
ssh ubuntu@10.7.11.10
docker ps
docker logs auth-service-uce --tail 50
curl http://localhost:8000/health

# User Service
ssh ubuntu@10.7.11.11
docker ps
docker logs user-service-uce --tail 50
curl http://localhost:8001/health

# Patient Service
ssh ubuntu@10.7.11.12
docker ps
docker logs patient-service-uce --tail 50
curl http://localhost:8002/health

# Appointment Service
ssh ubuntu@10.7.11.13
docker ps
docker logs appointment-service-uce --tail 50
curl http://localhost:8003/health
```

### 3. Probar Conectividad

```bash
# Desde Auth Service, probar MySQL
ssh ubuntu@10.7.11.10
nc -zv 10.1.11.10 3306

# Desde User Service, probar PostgreSQL y Redis
ssh ubuntu@10.7.11.11
nc -zv 10.1.11.20 5432
nc -zv 10.1.11.40 6379

# Probar RabbitMQ desde cualquier microservicio
nc -zv 10.10.11.50 5672
```

## 📊 Arquitectura de Red

### Tabla de Routing

#### Private Subnet Route Table:
| Destination | Target | Purpose |
|-------------|--------|---------|
| 0.0.0.0/0 | NAT Gateway | Internet via NAT |
| 10.1.0.0/16 | VPC Peering | Databases |
| 10.10.0.0/16 | VPC Peering | Infrastructure |

#### Security Groups:

**Auth Service:**
- In: 8000 from 10.10.0.0/16, 10.7.0.0/16, 10.8.0.0/16, 10.9.0.0/16
- Out: 3306 to MySQL, 5672 to RabbitMQ

**User Service:**
- In: 8001 from 10.10.0.0/16, 10.7.0.0/16, 10.8.0.0/16, 10.9.0.0/16
- Out: 5432 to PostgreSQL, 6379 to Redis, 5672 to RabbitMQ, 8000 to Auth

**Patient Service:**
- In: 8002 from 10.10.0.0/16, 10.7.0.0/16, 10.8.0.0/16, 10.9.0.0/16
- Out: 5432 to PostgreSQL, 6379 to Redis, 5672 to RabbitMQ, 8000 to Auth, 8001 to User

**Appointment Service:**
- In: 8003 from 10.10.0.0/16, 10.7.0.0/16, 10.8.0.0/16, 10.9.0.0/16
- Out: 5432 to PostgreSQL, 6379 to Redis, 5672 to RabbitMQ, 8000-8002 to otros servicios

## 🔑 Variables de Entorno

Todas las variables de entorno están configuradas en los user-data scripts y se inyectan automáticamente a los containers Docker.

### Credenciales:
- MySQL: `uce_admin / MySQL_UCE_Admin_2026!`
- PostgreSQL: `uce_admin / PostgreSQL_UCE_2026_Secure!`
- Redis: `Redis_UCE_2026_Secure!`
- RabbitMQ: `uce_admin / UCE_RabbitMQ_2026_Secure!`
- JWT: `UCE_Psychology_QA_2026_Super_Secret_Key_Change_In_Production!`

## 🧪 Testing

### Health Checks

```bash
# Via Bastion
ssh -i ../shared/finalkey.pem ubuntu@34.199.65.203

# Desde Bastion
curl http://10.7.11.10:8000/health  # Auth
curl http://10.7.11.11:8001/health  # User
curl http://10.7.11.12:8002/health  # Patient
curl http://10.7.11.13:8003/health  # Appointment
```

### API Endpoints

```bash
# Auth - Login (crear usuario primero)
curl -X POST http://10.7.11.10:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@uce.edu.ec","password":"admin123"}'

# User - Get profile (requiere token)
curl http://10.7.11.11:8001/api/users/profile \
  -H "Authorization: Bearer <TOKEN>"

# Patient - List patients (requiere token)
curl http://10.7.11.12:8002/api/patients/ \
  -H "Authorization: Bearer <TOKEN>"

# Appointment - List appointments (requiere token)
curl http://10.7.11.13:8003/api/v1/appointments/ \
  -H "Authorization: Bearer <TOKEN>"
```

## 🗑️ Cleanup

Para destruir todos los recursos:

```bash
terraform destroy
```

**⚠️ ADVERTENCIA:** Esto eliminará todas las instancias y datos no persistidos.

## 📝 Notas Importantes

1. **Docker Images:** Las imágenes deben estar en DockerHub ANTES del deployment.

2. **VPC Peering:** Se crea automáticamente pero requiere aceptación manual en las otras cuentas.

3. **Security Groups:** Configurados para permitir comunicación entre todos los microservicios y con las bases de datos.

4. **NAT Gateway:** Permite que las instancias privadas accedan a Internet para pulls de Docker y updates.

5. **Key Pair:** Se usa la misma key (`finalkey`) compartida entre todas las cuentas.

6. **Redis DB Numbers:**
   - User Service: DB 1
   - Patient Service: DB 2
   - Appointment Service: DB 3

7. **PostgreSQL Shared:** User, Patient y Appointment comparten la misma instancia PostgreSQL pero usan esquemas/tablas separados.

8. **Room Service:** Appointment tiene referencia a Room Service (Cuenta 8) que se configurará después.

## 📚 Documentación Adicional

- [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md) - Plan detallado de deployment
- [../VPC_PEERING_SETUP.md](../VPC_PEERING_SETUP.md) - Guía de VPC Peering
- [../IP_ADDRESSING_PLAN.md](../../IP_ADDRESSING_PLAN.md) - Plan completo de IPs

## 🆘 Troubleshooting

### Problema: Container no inicia

```bash
ssh ubuntu@<IP_MICROSERVICIO>
docker logs <container-name> --tail 100
```

### Problema: No puede conectarse a la base de datos

```bash
# Verificar conectividad
nc -zv 10.1.11.10 3306  # MySQL
nc -zv 10.1.11.20 5432  # PostgreSQL
nc -zv 10.1.11.40 6379  # Redis

# Verificar VPC Peering
# Debe mostrar "active"
```

### Problema: Auth Service no responde

```bash
# Verificar que MySQL esté accesible
ssh ubuntu@10.7.11.10
nc -zv 10.1.11.10 3306

# Verificar logs
docker logs auth-service-uce
```

### Problema: RabbitMQ connection failed

```bash
# Verificar conectividad desde cualquier microservicio
nc -zv 10.10.11.50 5672

# Verificar VPC Peering con Cuenta 10
```

---

**Última Actualización:** 21 de Enero, 2026  
**Estado:** ✅ Listo para Deployment  
**Ambiente:** QA  
**Siguiente:** Desplegar Cuenta 8 (Microservicios Grupo 2)
