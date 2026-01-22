# ============================================================
# VARIABLES - CUENTA 10 (INFRAESTRUCTURA)
# ============================================================

# ===== GENERAL =====
variable "aws_region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Ambiente de despliegue"
  type        = string
  default     = "qa"
}

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
  default     = "uce-psychology"
}

# ===== NETWORKING =====
variable "vpc_cidr" {
  description = "CIDR block para VPC de Infraestructura"
  type        = string
  default     = "10.10.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks para subnets públicas"
  type        = list(string)
  default     = ["10.10.1.0/24", "10.10.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks para subnets privadas"
  type        = list(string)
  default     = ["10.10.11.0/24", "10.10.12.0/24"]
}

variable "availability_zones" {
  description = "Zonas de disponibilidad"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# ===== KEY PAIR =====
variable "key_name" {
  description = "Nombre de la key pair para todas las instancias"
  type        = string
  default     = "finalkey"
}

# ===== INSTANCIAS EC2 =====
variable "instance_type_bastion" {
  description = "Tipo de instancia para Bastion"
  type        = string
  default     = "t3.micro"
}

variable "instance_type_kafka" {
  description = "Tipo de instancia para Kafka"
  type        = string
  default     = "t3.medium"
}

variable "instance_type_api_gateway" {
  description = "Tipo de instancia para API Gateway"
  type        = string
  default     = "t3.small"
}

variable "instance_type_rabbitmq" {
  description = "Tipo de instancia para RabbitMQ + MQTT"
  type        = string
  default     = "t3.medium"
}

variable "instance_type_nginx" {
  description = "Tipo de instancia para NGINX Load Balancer"
  type        = string
  default     = "t3.small"
}

# ===== AMI IDs =====
# Ubuntu 22.04 LTS con Docker preinstalado
variable "ami_ubuntu_docker" {
  description = "AMI ID de Ubuntu 22.04 con Docker"
  type        = string
  default     = "ami-0c7217cdde317cfec" # Ubuntu 22.04 LTS en us-east-1
}

# ===== ALLOWED IPS PARA BASTION =====
variable "allowed_ssh_cidrs" {
  description = "CIDRs permitidos para acceso SSH al Bastion"
  type        = list(string)
  default     = ["0.0.0.0/0"] # CAMBIAR EN PRODUCCIÓN
}

# ===== CIDRS DE OTRAS CUENTAS (para permitir comunicación) =====
variable "account_01_cidr" {
  description = "CIDR de Account 1 (Databases)"
  type        = string
  default     = "10.1.0.0/16"
}

variable "account_07_cidr" {
  description = "CIDR de Account 7 (Microservices)"
  type        = string
  default     = "10.7.0.0/16"
}

variable "account_08_cidr" {
  description = "CIDR de Account 8 (Microservices)"
  type        = string
  default     = "10.8.0.0/16"
}

variable "account_09_cidr" {
  description = "CIDR de Account 9 (Microservices + Monitoring)"
  type        = string
  default     = "10.9.0.0/16"
}

# ===== ACCOUNT IDs Y VPC IDs PARA VPC PEERING =====
variable "account_01_id" {
  description = "AWS Account ID de Cuenta 1 (Databases) - Obtener con: aws sts get-caller-identity"
  type        = string
  default     = ""  # COMPLETAR con el Account ID real
}

variable "account_01_vpc_id" {
  description = "VPC ID de Cuenta 1 (Databases) - Se obtiene después de crear la VPC"
  type        = string
  default     = ""  # COMPLETAR después de terraform apply en Cuenta 1
}

variable "account_07_id" {
  description = "AWS Account ID de Cuenta 7 (Microservices 1)"
  type        = string
  default     = ""  # COMPLETAR con el Account ID real
}

variable "account_07_vpc_id" {
  description = "VPC ID de Cuenta 7 - Se obtiene después de crear la VPC"
  type        = string
  default     = ""  # COMPLETAR después de terraform apply en Cuenta 7
}

variable "account_08_id" {
  description = "AWS Account ID de Cuenta 8 (Microservices 2)"
  type        = string
  default     = ""  # COMPLETAR con el Account ID real
}

variable "account_08_vpc_id" {
  description = "VPC ID de Cuenta 8 - Se obtiene después de crear la VPC"
  type        = string
  default     = ""  # COMPLETAR después de terraform apply en Cuenta 8
}

variable "account_09_id" {
  description = "AWS Account ID de Cuenta 9 (Microservices 3 + Monitoring)"
  type        = string
  default     = ""  # COMPLETAR con el Account ID real
}

variable "account_09_vpc_id" {
  description = "VPC ID de Cuenta 9 - Se obtiene después de crear la VPC"
  type        = string
  default     = ""  # COMPLETAR después de terraform apply en Cuenta 9
}

# ===== VPC PEERING CONFIGURATION =====
variable "enable_vpc_peering" {
  description = "Habilitar VPC Peering entre cuentas"
  type        = bool
  default     = true
}

variable "auto_accept_peering" {
  description = "Auto-aceptar peering (solo funciona si las cuentas están en la misma AWS Organization)"
  type        = bool
  default     = false
}

# ===== PUERTOS =====
variable "kafka_ports" {
  description = "Puertos de Kafka"
  type        = map(number)
  default = {
    broker      = 9092
    zookeeper   = 2181
    jmx         = 9999
  }
}

variable "rabbitmq_ports" {
  description = "Puertos de RabbitMQ y MQTT"
  type        = map(number)
  default = {
    amqp           = 5672
    management     = 15672
    mqtt           = 1883
    mqtt_ws        = 15675
    stomp          = 61613
  }
}

variable "api_gateway_ports" {
  description = "Puertos de API Gateway"
  type        = map(number)
  default = {
    http  = 80
    https = 443
    admin = 8001
  }
}

# ===== DOCKER IMAGES =====
variable "docker_images" {
  description = "Imágenes Docker de los servicios"
  type        = map(string)
  default = {
    kafka      = "bitnami/kafka:3.6"
    zookeeper  = "bitnami/zookeeper:3.9.2"
    rabbitmq   = "rabbitmq:3.12-management-alpine"
    nginx      = "nginx:1.25-alpine"
  }
}
