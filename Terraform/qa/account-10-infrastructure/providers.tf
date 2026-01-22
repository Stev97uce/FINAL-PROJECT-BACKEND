# ============================================================
# PROVIDERS - CUENTA 10 (INFRAESTRUCTURA)
# ============================================================
# Bastion, Kafka, API Gateway QA/Prod, RabbitMQ+MQTT, NGINX
# ============================================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }

  # Backend remoto (opcional - comentar si no usas S3 backend)
  # backend "s3" {
  #   bucket = "uce-terraform-state"
  #   key    = "qa/account-10/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

# Provider para Cuenta 10 (Infraestructura)
provider "aws" {
  region = var.aws_region
  
  # Estas credenciales se pasan desde variables de entorno o archivo terraform.tfvars
  # export AWS_ACCESS_KEY_ID="tu_access_key"
  # export AWS_SECRET_ACCESS_KEY="tu_secret_key"
  
  default_tags {
    tags = {
      Project     = "UCE-Psychology-System"
      Environment = "QA"
      Account     = "Account-10-Infrastructure"
      ManagedBy   = "Terraform"
      Owner       = "UCE-DevOps-Team"
    }
  }
}
