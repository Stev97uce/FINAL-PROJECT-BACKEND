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
      Environment = "QA"
      ManagedBy   = "Terraform"
      Account     = "Account-07-Microservices-1"
      Owner       = "UCE-DevOps-Team"
    }
  }
}
