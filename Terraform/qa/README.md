# 🚀 TERRAFORM - AMBIENTE QA

## 📋 Descripción General

Configuraciones de Terraform para desplegar el **ambiente de QA** del Sistema UCE Psychology en AWS. El sistema está distribuido en **5 cuentas AWS** para separar responsabilidades y mejorar la seguridad.

## 🏗️ Arquitectura de Cuentas

```
┌─────────────────────────────────────────────────────────────┐
│                   CUENTA 10: INFRAESTRUCTURA                │
│  • Bastion (Túnel SSH para todas las cuentas)              │
│  • NGINX Load Balancer (Punto de entrada principal)        │
│  • API Gateway QA (Kong)                                    │
│  • API Gateway PROD (Kong - standby)                        │
│  • RabbitMQ + MQTT                                          │
│  • Kafka                                                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   CUENTA 1: BASES DE DATOS                  │
│  • MySQL (Auth Service)                                     │
│  • PostgreSQL (User, Patient, Appointment, Room, etc.)     │
│  • MongoDB (Clinical, Notification, Analytics)             │
│  • Redis (Caché compartido)                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              CUENTA 7: MICROSERVICIOS (Grupo 1)             │
│  • Auth Service (8000)                                      │
│  • User Service (8001)                                      │
│  • Patient Service (8002)                                   │
│  • Appointment Service (8003)                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              CUENTA 8: MICROSERVICIOS (Grupo 2)             │
│  • Room Service (8004)                                      │
│  • Clinical Service (8005)                                  │
│  • Supervision Service (8006)                               │
│  • Notification Service (8007)                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│          CUENTA 9: MICROSERVICIOS (Grupo 3) + MONITORING    │
│  • Reporting Service (8008)                                 │
│  • Analytics Service (8009)                                 │
│  • Grafana (puerto 3000)                                    │
│  • Prometheus (puerto 9090)                                 │
└─────────────────────────────────────────────────────────────┘
```

## 📂 Estructura de Directorios

```
qa/
├── account-10-infrastructure/   # ⭐ DESPLEGAR PRIMERO
│   ├── providers.tf
│   ├── variables.tf
│   ├── vpc.tf
│   ├── keypair.tf              # Genera finalkey.pem
│   ├── security-groups.tf
│   ├── bastion.tf
│   ├── kafka.tf
│   ├── rabbitmq.tf
│   ├── api-gateway.tf
│   ├── nginx.tf
│   ├── outputs.tf
│   ├── user-data/
│   └── README.md
│
├── account-01-databases/        # DESPLEGAR SEGUNDO
│   └── (Por implementar)
│
├── account-07-microservices/    # DESPLEGAR TERCERO
│   └── (Por implementar)
│
├── account-08-microservices/    # DESPLEGAR CUARTO
│   └── (Por implementar)
│
├── account-09-microservices/    # DESPLEGAR QUINTO
│   └── (Por implementar)
│
├── shared/
│   ├── finalkey.pem            # Generado automáticamente
│   └── finalkey.pub            # Generado automáticamente
│
└── README.md                    # Este archivo
```

## 🔑 Key Pair Compartida

Todas las cuentas comparten la **misma key pair** llamada `finalkey`:

- **Ubicación**: `shared/finalkey.pem`
- **Generación**: Automática por Terraform en la Cuenta 10
- **Uso**: SSH a todas las instancias EC2 en todas las cuentas
- **Seguridad**: ⚠️ NO subir a Git (ya excluida en .gitignore)

```bash
# Comando SSH genérico
ssh -i shared/finalkey.pem ubuntu@<IP_INSTANCIA>

# Via Bastion (para instancias privadas)
ssh -i shared/finalkey.pem -J ubuntu@<BASTION_IP> ubuntu@<PRIVATE_IP>
```

## 🚀 Orden de Despliegue

### 1️⃣ CUENTA 10 - INFRAESTRUCTURA (OBLIGATORIO PRIMERO)

```bash
cd account-10-infrastructure
terraform init
terraform plan
terraform apply
```

**Outputs importantes:**
- Bastion Public IP
- finalkey.pem path
- RabbitMQ connection string
- Kafka bootstrap servers
- NGINX URL (punto de entrada)

### 2️⃣ CUENTA 1 - BASES DE DATOS

```bash
cd account-01-databases
terraform init
terraform plan
terraform apply
```

### 3️⃣ CUENTA 7 - MICROSERVICIOS (Grupo 1)

```bash
cd account-07-microservices
terraform init
terraform plan
terraform apply
```

### 4️⃣ CUENTA 8 - MICROSERVICIOS (Grupo 2)

```bash
cd account-08-microservices
terraform init
terraform plan
terraform apply
```

### 5️⃣ CUENTA 9 - MICROSERVICIOS (Grupo 3) + MONITORING

```bash
cd account-09-microservices
terraform init
terraform plan
terraform apply
```

## 🌐 CIDRs de las VPCs

| Cuenta | Nombre | CIDR |
|--------|--------|------|
| 10 | Infraestructura | 10.10.0.0/16 |
| 1  | Bases de Datos  | 10.1.0.0/16  |
| 7  | Microservicios 1 | 10.7.0.0/16  |
| 8  | Microservicios 2 | 10.8.0.0/16  |
| 9  | Microservicios 3 + Monitoring | 10.9.0.0/16  |

## 🔐 Comunicación Entre Cuentas

### Opción: Bastion Host como Túnel SSH

Todas las cuentas se comunican a través del **Bastion Host** en la Cuenta 10:

- **No se usa VPC Peering** (como especificado por el usuario)
- **Bastion actúa como jump host** para acceso SSH
- **Security Groups** permiten tráfico desde todas las VPCs
- **SSH Tunneling** para comunicación entre servicios

### Ejemplo: Microservicio accede a Base de Datos

```bash
# Desde Microservicio (Cuenta 7) a PostgreSQL (Cuenta 1)
# El tráfico pasa por:
# Microservicio → Bastion → Base de Datos
```

## 📋 Prerequisitos Globales

### Software Requerido

1. **Terraform** >= 1.0
   ```bash
   # Windows
   choco install terraform
   
   # Mac
   brew install terraform
   
   # Linux
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

2. **AWS CLI** v2
   ```bash
   # Verificar instalación
   aws --version
   
   # Configurar (por cada cuenta)
   aws configure
   ```

3. **Git** (para clonar el repositorio)

### Credenciales AWS

Para cada cuenta, configurar credenciales:

```bash
# Opción A: Variables de entorno (recomendado para cuentas institucionales)
export AWS_ACCESS_KEY_ID="tu_access_key"
export AWS_SECRET_ACCESS_KEY="tu_secret_key"
export AWS_DEFAULT_REGION="us-east-1"

# Opción B: AWS CLI profiles
aws configure --profile cuenta-10-infra
aws configure --profile cuenta-01-databases
# etc.
```

## 📊 Verificación del Despliegue

Después de desplegar todas las cuentas:

### 1. Verificar Acceso al Sistema

```bash
# Acceso a NGINX (punto de entrada principal)
curl http://<NGINX_PUBLIC_IP>/health

# Debería retornar: healthy
```

### 2. Verificar Bastion

```bash
ssh -i shared/finalkey.pem ubuntu@<BASTION_IP>
# Debería conectar exitosamente
```

### 3. Verificar RabbitMQ

```bash
# Abrir en navegador:
http://<RABBITMQ_PUBLIC_IP>:15672
# Usuario: uce_admin
# Password: UCE_RabbitMQ_2026_Secure!
```

### 4. Verificar API Gateway

```bash
curl http://<API_GATEWAY_QA_IP>/health
```

## 🔄 Actualización del Ambiente

```bash
# En cada carpeta de cuenta:
terraform plan    # Ver cambios
terraform apply   # Aplicar cambios
```

## 🗑️ Destrucción del Ambiente

⚠️ **CUIDADO: Esto eliminará TODA la infraestructura**

```bash
# ORDEN INVERSO al despliegue:

# 1. Cuenta 9
cd account-09-microservices
terraform destroy

# 2. Cuenta 8
cd ../account-08-microservices
terraform destroy

# 3. Cuenta 7
cd ../account-07-microservices
terraform destroy

# 4. Cuenta 1
cd ../account-01-databases
terraform destroy

# 5. Cuenta 10 (ÚLTIMO)
cd ../account-10-infrastructure
terraform destroy
```

## 📝 Variables de Entorno Recomendadas

Crear un archivo `env.sh` (NO subir a Git):

```bash
#!/bin/bash
# Credenciales para todas las cuentas

# Cuenta 10 - Infraestructura
export CUENTA_10_ACCESS_KEY="..."
export CUENTA_10_SECRET_KEY="..."

# Cuenta 1 - Bases de Datos
export CUENTA_01_ACCESS_KEY="..."
export CUENTA_01_SECRET_KEY="..."

# ... etc
```

Usar:
```bash
source env.sh
```

## 🐛 Troubleshooting

### Error: "No valid credential sources found"
```bash
# Verificar credenciales
aws sts get-caller-identity

# Reconfigurar
aws configure
```

### Error: finalkey.pem no encontrada
```bash
# Verificar que existe
ls -la shared/finalkey.pem

# Si no existe, ejecutar primero Cuenta 10
cd account-10-infrastructure
terraform apply
```

### Error: No se puede conectar a instancias privadas
```bash
# Usar Bastion como jump host
ssh -i shared/finalkey.pem -J ubuntu@<BASTION_IP> ubuntu@<PRIVATE_IP>
```

## 📞 Soporte

Para problemas:
1. Ver README específico de cada cuenta
2. Verificar logs: `/var/log/user-data.log` en las instancias
3. Revisar Security Groups
4. Verificar conectividad de red

## 🔗 Enlaces Útiles

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/)
- [Kong API Gateway](https://docs.konghq.com/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)

## 📄 Licencia

MIT - Universidad Central del Ecuador

---

**Ambiente:** QA  
**Versión:** 1.0.0  
**Última Actualización:** Enero 2026
