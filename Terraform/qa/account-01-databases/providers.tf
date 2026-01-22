# ============================================================
# PROVIDERS - CUENTA 1 (DATABASES)
# ============================================================

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "UCE-Psychology-System"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Account     = "Account-01-Databases"
      Owner       = "UCE-DevOps-Team"
    }
  }
}
