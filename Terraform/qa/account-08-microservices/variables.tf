variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.8.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.8.1.0/24", "10.8.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.8.11.0/24", "10.8.12.0/24"]
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# Microservices Configuration
variable "room_service_ip" {
  description = "Private IP for Room Service"
  type        = string
  default     = "10.8.11.10"
}

variable "clinical_service_ip" {
  description = "Private IP for Clinical Service"
  type        = string
  default     = "10.8.11.11"
}

variable "supervision_service_ip" {
  description = "Private IP for Supervision Service"
  type        = string
  default     = "10.8.11.12"
}

variable "notification_service_ip" {
  description = "Private IP for Notification Service"
  type        = string
  default     = "10.8.11.13"
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
    room        = "stevxd97/uce-room-service:latest"
    clinical    = "stevxd97/uce-clinical-service:latest"
    supervision = "stevxd97/uce-supervision-service:latest"
    notification = "stevxd97/uce-notification-service:latest"
  }
}

# Database Configuration (from Account 01)
variable "postgresql_host" {
  description = "PostgreSQL host IP"
  type        = string
  default     = "10.1.11.20"
}

variable "mongodb_host" {
  description = "MongoDB host IP"
  type        = string
  default     = "10.1.11.30"
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
variable "postgresql_password" {
  description = "PostgreSQL password"
  type        = string
  default     = "PostgreSQL_UCE_2026_Secure!"
  sensitive   = true
}

variable "mongodb_password" {
  description = "MongoDB password"
  type        = string
  default     = "MongoDB_UCE_2026_Secure!"
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

# Service URLs (for inter-service communication)
variable "auth_service_url" {
  description = "Auth Service URL"
  type        = string
  default     = "http://10.7.11.10:8000"
}

variable "clinical_service_url" {
  description = "Clinical Service URL (for Supervision Service)"
  type        = string
  default     = "http://10.8.11.11:8005"
}
