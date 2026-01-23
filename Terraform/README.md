# 🏗️ TERRAFORM - INFRAESTRUCTURA UCE PSYCHOLOGY SYSTEM

## 📋 Descripción

Configuraciones completas de **Terraform** para desplegar el Sistema UCE Psychology en AWS. Incluye configuraciones para **ambientes QA y Producción**, distribuidos en **5 cuentas AWS**.

```
terraform/
├── qa/                          # ⭐ Ambiente de QA (USAR ESTE PRIMERO)
│   ├── account-10-infrastructure/  # Bastion, NGINX, API Gateway, RabbitMQ, Kafka
│   ├── account-01-databases/       # MySQL, PostgreSQL, MongoDB, Redis
│   ├── account-07-microservices/   # Auth, User, Patient, Appointment
│   ├── account-08-microservices/   # Room, Clinical, Supervision, Notification
│   ├── account-09-microservices/   # Reporting, Analytics, Grafana, Prometheus
│   ├── shared/
│   │   └── finalkey.pem         # ⚠️ NO SUBIR A GIT
│   ├── deploy.sh
│   └── README.md
│
├── prod/                        # Ambiente de Producción (PARA FUTURO)
│   └── (Misma estructura que qa/)
│
├── CREDENTIALS_SETUP.md         # ⭐ IMPORTANTE: Leer primero
├── .gitignore
└── README.md                    # Este archivo
```

## 🎯 Arquitectura General

### 5 Cuentas AWS

| Cuenta | Nombre | Propósito | VPC CIDR |
|--------|--------|-----------|----------|
| **10** | Infraestructura | Bastion, NGINX, API Gateway, Message Brokers | 10.10.0.0/16 |
| **1**  | Bases de Datos | MySQL, PostgreSQL, MongoDB, Redis | 10.1.0.0/16 |
| **7**  | Microservicios 1 | Auth, User, Patient, Appointment | 10.7.0.0/16 |
| **8**  | Microservicios 2 | Room, Clinical, Supervision, Notification | 10.8.0.0/16 |
| **9**  | Microservicios 3 + Monitoring | Reporting, Analytics, Grafana, Prometheus | 10.9.0.0/16 |

### Flujo de Tráfico

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │
       ↓
┌──────────────────┐
│  NGINX (Cuenta 10│  ← Punto de entrada principal
│  IP Pública      │
└────────┬─────────┘
         │
         ↓
┌────────────────────────┐
│ API Gateway QA (Kong)  │
│ Cuenta 10              │
└────────┬───────────────┘
         │
         ├──→ Microservicios (Cuentas 7, 8, 9)
         │
         └──→ Bases de Datos (Cuenta 1)
              ↕
         RabbitMQ + Kafka (Cuenta 10)
```

## 🚀 Quick Start

### 1. Prerequisitos

```bash
# Instalar Terraform
# Windows: choco install terraform
# Mac: brew install terraform
# Linux: sudo apt-get install terraform

# Instalar AWS CLI
# https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

# Verificar instalaciones
terraform version
aws --version
```

### 2. Configurar Credenciales

⚠️ **MUY IMPORTANTE**: Leer `CREDENTIALS_SETUP.md` primero

```powershell
# Windows PowerShell
$env:AWS_ACCESS_KEY_ID="tu_access_key"
$env:AWS_SECRET_ACCESS_KEY="tu_secret_key"
$env:AWS_DEFAULT_REGION="us-east-1"

# Verificar
aws sts get-caller-identity
```

### 3. Desplegar Infraestructura

#### Opción A: Script Automático (Recomendado)

```bash
cd qa
./deploy.sh
# Seguir las instrucciones del menú
```

#### Opción B: Manual

```bash
# 1. Cuenta 10 - Infraestructura
cd qa/account-10-infrastructure
terraform init
terraform plan
terraform apply

# 2. Cuenta 1 - Bases de Datos
cd ../account-01-databases
# Configurar credenciales de Cuenta 1
terraform init
terraform plan
terraform apply

# 3-5. Repetir para las demás cuentas
```

## 🔑 Key Pair (finalkey)

- **Generación**: Automática por Terraform en Cuenta 10
- **Ubicación**: `qa/shared/finalkey.pem`
- **Uso**: SSH a TODAS las instancias en TODAS las cuentas
- **Seguridad**: ⚠️ NO subir a Git (ya en `.gitignore`)

```bash
# Permisos en Linux/Mac
chmod 400 qa/shared/finalkey.pem

# Uso
ssh -i qa/shared/finalkey.pem ubuntu@<IP_INSTANCE>
```

## 📊 Recursos Desplegados

### Cuenta 10 (Infraestructura)

- **1x Bastion Host** (t3.micro) - Túnel SSH
- **1x NGINX** (t3.small) - Load Balancer
- **1x API Gateway QA** (t3.small) - Kong
- **1x API Gateway PROD** (t3.small) - Kong (standby)
- **1x RabbitMQ** (t3.medium) - Message Broker + MQTT
- **1x Kafka** (t3.medium) - Event Streaming
- **VPC** + Subnets + NAT Gateway + Internet Gateway
- **Security Groups** configurados para todas las cuentas
- **6x Elastic IPs** (una por servicio)

### Cuenta 1 (Bases de Datos)

- MySQL 8.0 (Auth Service)
- PostgreSQL 14 (6 microservicios)
- MongoDB 6.0 (3 microservicios)
- Redis 7.0 (Caché compartido)

### Cuentas 7, 8, 9 (Microservicios)

- 10 microservicios en total
- Cada uno con su Docker image
- Configuración automática vía user-data
- IPs elásticas para cada uno

### Cuenta 9 (Extra: Monitoring)

- Grafana (3000)
- Prometheus (9090)
- IP elástica

## 💰 Costos Estimados (QA)

### Por Cuenta

| Cuenta | EC2 | EBS | EIP | Total/mes (aprox) |
|--------|-----|-----|-----|-------------------|
| Cuenta 10 | ~$50 | ~$10 | ~$36 | ~$96 |
| Cuenta 1 | ~$30 | ~$20 | ~$24 | ~$74 |
| Cuenta 7 | ~$40 | ~$15 | ~$24 | ~$79 |
| Cuenta 8 | ~$40 | ~$15 | ~$24 | ~$79 |
| Cuenta 9 | ~$35 | ~$15 | ~$18 | ~$68 |
| **TOTAL** | | | | **~$396/mes** |

*Precios estimados para us-east-1. Pueden variar.*

### Optimización de Costos

1. **Parar instancias cuando no se usen**:
   ```bash
   aws ec2 stop-instances --instance-ids <ID>
   ```

2. **Liberar EIPs no usadas**: Se cobran si no están asociadas

3. **Usar Free Tier**: Algunas instancias t3.micro califican

## 🔄 Actualización

```bash
cd qa/account-10-infrastructure
terraform plan
terraform apply
```

## 🗑️ Destrucción

⚠️ **ORDEN INVERSO al despliegue**

```bash
# 1. Cuenta 9
cd qa/account-09-microservices
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

## 🐛 Troubleshooting

### 1. Error de Credenciales

```bash
# Verificar
aws sts get-caller-identity

# Reconfigurar
aws configure
```

### 2. finalkey.pem no encontrada

```bash
# Asegurarse que Cuenta 10 fue desplegada primero
cd qa/account-10-infrastructure
terraform apply
```

### 3. Límites de AWS

```bash
# Ver límites de la cuenta
aws service-quotas list-service-quotas --service-code ec2

# Solicitar aumento de EIPs si es necesario
```

### 4. Instancia no inicia

```bash
# Conectarse y ver logs
ssh -i qa/shared/finalkey.pem ubuntu@<IP>
sudo tail -f /var/log/user-data.log
```

## 📝 Best Practices

1. ✅ Siempre ejecutar `terraform plan` antes de `apply`
2. ✅ Revisar outputs después de cada deploy
3. ✅ Mantener `finalkey.pem` segura y fuera de Git
4. ✅ Usar mismo formato de tags en todos los recursos
5. ✅ Documentar cambios en variables
6. ✅ Hacer backup del state file (si no usas S3 backend)
7. ✅ Rotar credenciales regularmente
8. ✅ Parar instancias cuando no se usen (ahorro de costos)

## 📚 Documentación Adicional

- `qa/README.md` - Detalles del ambiente QA
- `qa/account-10-infrastructure/README.md` - Detalles de Cuenta 10
- `CREDENTIALS_SETUP.md` - Configuración de credenciales
- Cada cuenta tiene su propio README

## 🔗 Enlaces Útiles

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS CLI User Guide](https://docs.aws.amazon.com/cli/)
- [Kong Documentation](https://docs.konghq.com/)
- [NGINX Documentation](https://nginx.org/en/docs/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Kafka Documentation](https://kafka.apache.org/documentation/)

## 🆘 Soporte

Para problemas o preguntas:

1. Verificar logs de user-data en instancias
2. Revisar Security Groups
3. Verificar conectividad de red
4. Consultar README específico de cada cuenta

## 📄 Licencia

MIT - Universidad Central del Ecuador

---

**Proyecto:** UCE Psychology System  
**Versión:** 1.0.0  
**Última Actualización:** Enero 2026  
**Ambiente:** QA (Producción pendiente)

---

## 👥 Equipo

Universidad Central del Ecuador - Facultad de Psicología  
Sistemas Distribuidos - 2026

**Desarrollado con ❤️ usando Terraform + AWS**
