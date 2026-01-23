# 🏗️ CUENTA 10 - INFRAESTRUCTURA (QA)

## 📋 Descripción

Esta configuración de Terraform despliega la **infraestructura base** para el sistema UCE Psychology en el ambiente de QA. Incluye todos los servicios de infraestructura compartidos necesarios para soportar los microservicios.

## 🎯 Componentes Desplegados

| Componente | Instancia | Descripción | Puerto Principal |
|------------|-----------|-------------|------------------|
| **Bastion** | t3.micro | Túnel SSH para acceso a todas las cuentas | 22 |
| **NGINX** | t3.small | Load Balancer principal (punto de entrada) | 80, 443 |
| **API Gateway QA** | t3.small | Kong API Gateway para QA | 80, 8001 |
| **API Gateway PROD** | t3.small | Kong API Gateway (standby para futuro) | 80 |
| **RabbitMQ + MQTT** | t3.medium | Message Broker con soporte MQTT | 5672, 1883, 15672 |
| **Kafka** | t3.medium | Event Streaming Platform | 9092, 2181 |

## 🌐 Arquitectura de Red

```
VPC: 10.10.0.0/16

├── Subnets Públicas
│   ├── 10.10.1.0/24 (us-east-1a) - Bastion, NGINX, API Gateways
│   └── 10.10.2.0/24 (us-east-1b) - Redundancia
│
└── Subnets Privadas
    ├── 10.10.11.0/24 (us-east-1a) - Kafka, RabbitMQ
    └── 10.10.12.0/24 (us-east-1b) - Redundancia
```

## 🔧 Prerequisitos

1. **Terraform** >= 1.0
   ```bash
   # Windows (con Chocolatey)
   choco install terraform
   
   # O descargar desde: https://www.terraform.io/downloads
   ```

2. **AWS CLI** configurado
   ```bash
   aws configure
   # Ingresar Access Key ID y Secret Access Key
   ```

3. **Credenciales AWS** de la Cuenta 10 (Infraestructura)

## 🚀 Despliegue

### 1. Configurar Credenciales

```bash
# Opción A: Variables de entorno (recomendado para cuentas institucionales)
export AWS_ACCESS_KEY_ID="tu_access_key_id"
export AWS_SECRET_ACCESS_KEY="tu_secret_access_key"
export AWS_DEFAULT_REGION="us-east-1"

# Opción B: AWS CLI
aws configure
```

### 2. Configurar Variables

```bash
# Copiar template de variables
cp terraform.tfvars.example terraform.tfvars

# Editar terraform.tfvars con tus valores específicos
# IMPORTANTE: Cambiar allowed_ssh_cidrs a tu IP pública
```

### 3. Inicializar Terraform

```bash
terraform init
```

### 4. Revisar Plan

```bash
terraform plan
```

### 5. Aplicar Configuración

```bash
terraform apply
```

Terraform te mostrará los cambios y pedirá confirmación. Escribe `yes` para proceder.

## 📤 Outputs Importantes

Después del despliegue, Terraform mostrará:

- **NGINX Load Balancer** - URL principal del sistema
- **Bastion Host** - IP y comando SSH para conexión
- **API Gateway QA** - URL y Admin API
- **RabbitMQ Management** - URL y credenciales
- **Kafka Broker** - Connection string
- **Key Pair Path** - Ubicación de finalkey.pem

Puedes ver estos outputs en cualquier momento:

```bash
terraform output
terraform output infrastructure_summary
```

## 🔐 Key Pair (finalkey)

Terraform generará automáticamente el key pair `finalkey` y lo guardará en:
```
../shared/finalkey.pem
```

**IMPORTANTE:** 
- ⚠️ NO subir este archivo a Git (.gitignore ya lo excluye)
- Guardar en un lugar seguro
- Compartir de forma segura con el equipo
- Usar para conectarse a todas las instancias

## 🔗 Conexión a Instancias

### Bastion (Público)
```bash
ssh -i ../shared/finalkey.pem ubuntu@<BASTION_PUBLIC_IP>
```

### Instancias Privadas (vía Bastion)
```bash
# Opción 1: Jump host (-J)
ssh -i ../shared/finalkey.pem -J ubuntu@<BASTION_IP> ubuntu@<PRIVATE_IP>

# Opción 2: Port forwarding (para servicios web)
ssh -i ../shared/finalkey.pem -L 15672:<RABBITMQ_PRIVATE_IP>:15672 ubuntu@<BASTION_IP>
# Luego acceder a: http://localhost:15672
```

## 📊 Monitoreo y Health Checks

| Servicio | Health Check URL |
|----------|------------------|
| NGINX | `http://<NGINX_IP>/health` |
| API Gateway QA | `http://<API_GATEWAY_IP>/health` |
| RabbitMQ | `http://<RABBITMQ_IP>:15672` |
| Kafka | `telnet <KAFKA_IP> 9092` |

## 🔄 Actualización

```bash
# Ver cambios
terraform plan

# Aplicar cambios
terraform apply

# Reconstruir instancia específica
terraform taint aws_instance.kafka
terraform apply
```

## 🗑️ Destrucción

**⚠️ CUIDADO: Esto eliminará TODA la infraestructura**

```bash
terraform destroy
```

## 📁 Estructura de Archivos

```
account-10-infrastructure/
├── providers.tf         # Configuración de providers (AWS, TLS, Local)
├── variables.tf         # Definición de variables
├── vpc.tf              # VPC, subnets, IGW, NAT Gateway
├── keypair.tf          # Generación de key pair finalkey
├── security-groups.tf  # Security groups para todas las instancias
├── bastion.tf          # Bastion Host
├── kafka.tf            # Kafka Cluster
├── rabbitmq.tf         # RabbitMQ + MQTT
├── api-gateway.tf      # API Gateways (QA y Prod)
├── nginx.tf            # NGINX Load Balancer
├── outputs.tf          # Outputs de la infraestructura
├── terraform.tfvars.example
├── user-data/          # Scripts de inicialización
│   ├── bastion.sh
│   ├── kafka.sh
│   ├── rabbitmq.sh
│   ├── api-gateway-qa.sh
│   ├── api-gateway-prod.sh
│   └── nginx.sh
└── README.md
```

## 🔒 Seguridad

### Security Groups
- **Bastion**: SSH desde anywhere, todo el tráfico desde otras cuentas
- **Kafka**: 9092 desde microservicios, 2181 interno, 9999 desde monitoring
- **RabbitMQ**: 5672 (AMQP), 15672 (Management), 1883 (MQTT) desde microservicios
- **API Gateways**: 80, 443 públicos; 8001 interno
- **NGINX**: 80, 443 públicos; 8080 interno

### Recomendaciones
1. ✅ Cambiar `allowed_ssh_cidrs` a tu IP específica en producción
2. ✅ Habilitar HTTPS con certificados SSL/TLS
3. ✅ Rotar credenciales de RabbitMQ
4. ✅ Configurar AWS Secrets Manager para credenciales
5. ✅ Habilitar CloudWatch Logs
6. ✅ Configurar backup de datos de Kafka y RabbitMQ

## 🐛 Troubleshooting

### Error: Credenciales AWS inválidas
```bash
aws sts get-caller-identity
# Verificar que las credenciales estén configuradas
```

### Error: AMI no encontrada
```bash
# Buscar AMI de Ubuntu 22.04 en tu región
aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].[ImageId,Name]' \
  --output table
```

### Error: No se puede conectar a instancia privada
- Verificar que estés usando Bastion como jump host
- Verificar security groups
- Verificar que la key finalkey.pem tenga permisos 400

### Servicios no inician automáticamente
```bash
# Conectarse a la instancia y verificar logs
ssh -i ../shared/finalkey.pem -J ubuntu@<BASTION_IP> ubuntu@<INSTANCE_IP>
sudo tail -f /var/log/user-data.log
docker ps
```

## 📞 Soporte

Para problemas o preguntas:
1. Verificar logs de user-data: `/var/log/user-data.log`
2. Verificar estado de Docker: `docker ps`
3. Ver logs de contenedores: `docker logs <container_name>`

## 🔗 Siguiente Paso

Después de desplegar esta infraestructura, proceder con:
- **Cuenta 1**: Bases de Datos (MySQL, PostgreSQL, MongoDB, Redis)

## 📄 Licencia

MIT - Universidad Central del Ecuador

---

**Desarrollado con ❤️ para UCE Psychology System**
