variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.7.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.7.1.0/24", "10.7.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.7.11.0/24", "10.7.12.0/24"]
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# Microservices Configuration
variable "auth_service_ip" {
  description = "Private IP for Auth Service"
  type        = string
  default     = "10.7.11.10"
}

variable "user_service_ip" {
  description = "Private IP for User Service"
  type        = string
  default     = "10.7.11.11"
}

variable "patient_service_ip" {
  description = "Private IP for Patient Service"
  type        = string
  default     = "10.7.11.12"
}

variable "appointment_service_ip" {
  description = "Private IP for Appointment Service"
  type        = string
  default     = "10.7.11.13"
}

# Instance Configuration
variable "instance_type" {
  description = "EC2 instance type for microservices"
  type        = string
  default     = "t3.small"
}

variable "ami_id" {
  description = "AMI ID for EC2 instances (Ubuntu 22.04 LTS)"
  type        = string
  default     = "ami-0e2c8caa4b6378d8c"  # Ubuntu 22.04 LTS in us-east-1
}

# Key Pair
variable "key_name" {
  description = "Name of the SSH key pair"
  type        = string
  default     = "finalkey"
}

# VPC Peering Variables
variable "enable_vpc_peering" {
  description = "Enable VPC peering connections"
  type        = bool
  default     = true
}

variable "account_10_id" {
  description = "AWS Account ID for Account 10 (Infrastructure)"
  type        = string
  default     = "005804858815"
}

variable "account_10_vpc_id" {
  description = "VPC ID from Account 10 (Infrastructure)"
  type        = string
}

variable "account_01_id" {
  description = "AWS Account ID for Account 01 (Databases)"
  type        = string
  default     = "998193889598"
}

variable "account_01_vpc_id" {
  description = "VPC ID from Account 01 (Databases)"
  type        = string
}

# Docker Images
variable "docker_registry" {
  description = "Docker registry username"
  type        = string
  default     = "stevxd97"
}

variable "docker_images" {
  description = "Docker images for each microservice"
  type = map(string)
  default = {
    auth        = "stevxd97/uce-auth-service:latest"
    user        = "stevxd97/uce-user-service:latest"
    patient     = "stevxd97/uce-patient-service:latest"
    appointment = "stevxd97/uce-appointment-service:latest"
  }
}

# Database Configuration (from Account 01)
variable "mysql_host" {
  description = "MySQL host IP"
  type        = string
  default     = "10.1.11.10"
}

variable "postgresql_host" {
  description = "PostgreSQL host IP"
  type        = string
  default     = "10.1.11.20"
}

variable "redis_host" {
  description = "Redis host IP"
  type        = string
  default     = "10.1.11.40"
}

# Infrastructure Services (from Account 10)
variable "rabbitmq_host" {
  description = "RabbitMQ host IP"
  type        = string
  default     = "10.10.11.50"
}

variable "bastion_ip" {
  description = "Bastion host IP for SSH access"
  type        = string
  default     = "10.10.1.10"
}

# JWT Configuration
variable "jwt_secret_key" {
  description = "JWT secret key"
  type        = string
  default     = "UCE_Psychology_QA_2026_Super_Secret_Key_Change_In_Production!"
  sensitive   = true
}

# Database Credentials
variable "mysql_password" {
  description = "MySQL password"
  type        = string
  default     = "MySQL_UCE_Admin_2026!"
  sensitive   = true
}

variable "postgresql_password" {
  description = "PostgreSQL password"
  type        = string
  default     = "PostgreSQL_UCE_2026_Secure!"
  sensitive   = true
}

variable "redis_password" {
  description = "Redis password"
  type        = string
  default     = "Redis_UCE_2026_Secure!"
  sensitive   = true
}

variable "rabbitmq_password" {
  description = "RabbitMQ password"
  type        = string
  default     = "UCE_RabbitMQ_2026_Secure!"
  sensitive   = true
}
