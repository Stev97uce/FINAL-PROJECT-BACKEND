# ============================================================
# VARIABLES - CUENTA 1 (DATABASES)
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
  description = "CIDR block para VPC de Databases"
  type        = string
  default     = "10.1.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks para subnets públicas"
  type        = list(string)
  default     = ["10.1.1.0/24", "10.1.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks para subnets privadas"
  type        = list(string)
  default     = ["10.1.11.0/24", "10.1.12.0/24"]
}

variable "availability_zones" {
  description = "Zonas de disponibilidad"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# ===== KEY PAIR =====
variable "key_name" {
  description = "Nombre de la key pair (debe ser la misma que en Cuenta 10)"
  type        = string
  default     = "finalkey"
}

variable "key_pair_public_key" {
  description = "Clave pública SSH (copiar de Cuenta 10)"
  type        = string
  default     = ""  # Se llenará desde el archivo
}

# ===== INSTANCIAS EC2 =====
variable "instance_type_mysql" {
  description = "Tipo de instancia para MySQL"
  type        = string
  default     = "t3.medium"
}

variable "instance_type_postgresql" {
  description = "Tipo de instancia para PostgreSQL"
  type        = string
  default     = "t3.medium"
}

variable "instance_type_mongodb" {
  description = "Tipo de instancia para MongoDB"
  type        = string
  default     = "t3.medium"
}

variable "instance_type_redis" {
  description = "Tipo de instancia para Redis"
  type        = string
  default     = "t3.small"
}

# ===== AMI =====
variable "ami_ubuntu_docker" {
  description = "AMI ID de Ubuntu 22.04 con Docker"
  type        = string
  default     = "ami-0c7217cdde317cfec" # Ubuntu 22.04 LTS en us-east-1
}

# ===== SEGURIDAD =====
variable "bastion_ip" {
  description = "IP del Bastion Host de la Cuenta 10"
  type        = string
  default     = "34.199.65.203"  # Actualizar con la IP real del Bastion
}

# ===== CIDRs DE OTRAS CUENTAS =====
variable "account_10_cidr" {
  description = "CIDR de Account 10 (Infrastructure)"
  type        = string
  default     = "10.10.0.0/16"
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

# ===== VPC PEERING =====
variable "account_10_id" {
  description = "AWS Account ID de Cuenta 10 (Infrastructure)"
  type        = string
  default     = "005804858815"
}

variable "account_10_vpc_id" {
  description = "VPC ID de Cuenta 10 (obtener después de crear)"
  type        = string
  default     = "vpc-0eaed73e095dfc670"  # VPC ID de la Cuenta 10 ya creada
}

variable "enable_vpc_peering" {
  description = "Habilitar VPC Peering con Cuenta 10 y Cuenta 7"
  type        = bool
  default     = true
}

variable "account_07_id" {
  description = "AWS Account ID de Cuenta 7 (Microservices 1)"
  type        = string
  default     = "756857881991"
}

variable "account_07_vpc_id" {
  description = "VPC ID de Cuenta 7 (obtener después de crear)"
  type        = string
  default     = ""
}

variable "account_08_id" {
  description = "AWS Account ID de Cuenta 8 (Microservices 2)"
  type        = string
  default     = "356703566425"
}

variable "account_08_vpc_id" {
  description = "VPC ID de Cuenta 8 (obtener después de crear)"
  type        = string
  default     = ""
}

# ===== VOLÚMENES DE DATOS =====
variable "mysql_data_volume_size" {
  description = "Tamaño del volumen de datos de MySQL (GB)"
  type        = number
  default     = 50
}

variable "postgresql_data_volume_size" {
  description = "Tamaño del volumen de datos de PostgreSQL (GB)"
  type        = number
  default     = 100
}

variable "mongodb_data_volume_size" {
  description = "Tamaño del volumen de datos de MongoDB (GB)"
  type        = number
  default     = 100
}

variable "redis_data_volume_size" {
  description = "Tamaño del volumen de datos de Redis (GB)"
  type        = number
  default     = 20
}

# ===== CREDENCIALES DE BASES DE DATOS =====
variable "mysql_root_password" {
  description = "Contraseña root de MySQL"
  type        = string
  sensitive   = true
  default     = "MySQL_UCE_2026_Secure!"
}

variable "postgresql_password" {
  description = "Contraseña de PostgreSQL"
  type        = string
  sensitive   = true
  default     = "PostgreSQL_UCE_2026_Secure!"
}

variable "mongodb_root_password" {
  description = "Contraseña root de MongoDB"
  type        = string
  sensitive   = true
  default     = "MongoDB_UCE_2026_Secure!"
}

variable "redis_password" {
  description = "Contraseña de Redis"
  type        = string
  sensitive   = true
  default     = "Redis_UCE_2026_Secure!"
}
