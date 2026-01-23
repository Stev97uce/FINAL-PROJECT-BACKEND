# ============================================================
# OUTPUTS - CUENTA 7 (MICROSERVICIOS GRUPO 1)
# ============================================================

# VPC Information
output "vpc_id" {
  description = "VPC ID for Microservices Account 7"
  value       = aws_vpc.microservices_1.id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.microservices_1.cidr_block
}

# Subnet Information
output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

# Auth Service
output "auth_service_info" {
  description = "Auth Service information"
  value = {
    private_ip  = aws_instance.auth_service.private_ip
    instance_id = aws_instance.auth_service.id
    port        = 8000
    database    = "MySQL (${var.mysql_host})"
    url         = "http://${aws_instance.auth_service.private_ip}:8000"
  }
}

# User Service
output "user_service_info" {
  description = "User Service information"
  value = {
    private_ip  = aws_instance.user_service.private_ip
    instance_id = aws_instance.user_service.id
    port        = 8001
    database    = "PostgreSQL (${var.postgresql_host})"
    url         = "http://${aws_instance.user_service.private_ip}:8001"
  }
}

# Patient Service
output "patient_service_info" {
  description = "Patient Service information"
  value = {
    private_ip  = aws_instance.patient_service.private_ip
    instance_id = aws_instance.patient_service.id
    port        = 8002
    database    = "PostgreSQL (${var.postgresql_host})"
    url         = "http://${aws_instance.patient_service.private_ip}:8002"
  }
}

# Appointment Service
output "appointment_service_info" {
  description = "Appointment Service information"
  value = {
    private_ip  = aws_instance.appointment_service.private_ip
    instance_id = aws_instance.appointment_service.id
    port        = 8003
    database    = "PostgreSQL (${var.postgresql_host})"
    url         = "http://${aws_instance.appointment_service.private_ip}:8003"
  }
}

# All Microservices IPs
output "microservices_ips" {
  description = "All microservices private IPs"
  value = {
    auth        = aws_instance.auth_service.private_ip
    user        = aws_instance.user_service.private_ip
    patient     = aws_instance.patient_service.private_ip
    appointment = aws_instance.appointment_service.private_ip
  }
}

# VPC Peering Information
output "vpc_peering_connections" {
  description = "VPC peering connection IDs and statuses"
  value = {
    to_infrastructure = var.enable_vpc_peering && var.account_10_vpc_id != "" ? {
      id     = aws_vpc_peering_connection.to_infrastructure[0].id
      status = aws_vpc_peering_connection.to_infrastructure[0].accept_status
    } : null
    to_databases = var.enable_vpc_peering && var.account_01_vpc_id != "" ? {
      id     = aws_vpc_peering_connection.to_databases[0].id
      status = aws_vpc_peering_connection.to_databases[0].accept_status
    } : null
  }
}

# Key Pair
output "key_pair_name" {
  description = "SSH key pair name"
  value       = aws_key_pair.finalkey.key_name
}

# Connection Strings for Bastion
output "ssh_commands" {
  description = "SSH commands to access microservices via Bastion"
  value = {
    bastion_ip  = var.bastion_ip
    auth        = "ssh -i ../shared/finalkey.pem -J ubuntu@${var.bastion_ip} ubuntu@${aws_instance.auth_service.private_ip}"
    user        = "ssh -i ../shared/finalkey.pem -J ubuntu@${var.bastion_ip} ubuntu@${aws_instance.user_service.private_ip}"
    patient     = "ssh -i ../shared/finalkey.pem -J ubuntu@${var.bastion_ip} ubuntu@${aws_instance.patient_service.private_ip}"
    appointment = "ssh -i ../shared/finalkey.pem -J ubuntu@${var.bastion_ip} ubuntu@${aws_instance.appointment_service.private_ip}"
  }
}

# Summary
output "microservices_summary" {
  description = "Complete summary of microservices deployment"
  value = <<EOT

╔══════════════════════════════════════════════════════════════════╗
║      CUENTA 7 - MICROSERVICIOS GRUPO 1 - QA ENVIRONMENT         ║
╚══════════════════════════════════════════════════════════════════╝

🔐 AUTH SERVICE:
   IP: ${aws_instance.auth_service.private_ip}:8000
   URL: http://${aws_instance.auth_service.private_ip}:8000
   Database: MySQL (${var.mysql_host}:3306)
   SSH: ssh -i ../shared/finalkey.pem -J ubuntu@${var.bastion_ip} ubuntu@${aws_instance.auth_service.private_ip}

👤 USER SERVICE:
   IP: ${aws_instance.user_service.private_ip}:8001
   URL: http://${aws_instance.user_service.private_ip}:8001
   Database: PostgreSQL (${var.postgresql_host}:5432)
   Cache: Redis (${var.redis_host}:6379)
   SSH: ssh -i ../shared/finalkey.pem -J ubuntu@${var.bastion_ip} ubuntu@${aws_instance.user_service.private_ip}

🏥 PATIENT SERVICE:
   IP: ${aws_instance.patient_service.private_ip}:8002
   URL: http://${aws_instance.patient_service.private_ip}:8002
   Database: PostgreSQL (${var.postgresql_host}:5432)
   Cache: Redis (${var.redis_host}:6379)
   SSH: ssh -i ../shared/finalkey.pem -J ubuntu@${var.bastion_ip} ubuntu@${aws_instance.patient_service.private_ip}

📅 APPOINTMENT SERVICE:
   IP: ${aws_instance.appointment_service.private_ip}:8003
   URL: http://${aws_instance.appointment_service.private_ip}:8003
   Database: PostgreSQL (${var.postgresql_host}:5432)
   Cache: Redis (${var.redis_host}:6379)
   SSH: ssh -i ../shared/finalkey.pem -J ubuntu@${var.bastion_ip} ubuntu@${aws_instance.appointment_service.private_ip}

📨 MESSAGE BROKER:
   RabbitMQ: ${var.rabbitmq_host}:5672

🌍 VPC:
   ID: ${aws_vpc.microservices_1.id}
   CIDR: ${aws_vpc.microservices_1.cidr_block}

🔗 VPC PEERING:
   ${var.enable_vpc_peering && var.account_10_vpc_id != "" ? "✅ Cuenta 10 (Infrastructure) - Pending Acceptance" : "⚠️  Cuenta 10 - Not Configured"}
   ${var.enable_vpc_peering && var.account_01_vpc_id != "" ? "✅ Cuenta 1 (Databases) - Pending Acceptance" : "⚠️  Cuenta 1 - Not Configured"}

🔑 KEY PAIR:
   Nombre: ${aws_key_pair.finalkey.key_name}
   Archivo: ../shared/finalkey.pem

═══════════════════════════════════════════════════════════════════
💡 PRÓXIMOS PASOS:
1. Aceptar VPC Peering en Cuentas 10 y 1
2. Verificar que los containers estén corriendo
3. Probar endpoints de salud (/health)
4. Configurar API Gateway para enrutar a estos servicios
═══════════════════════════════════════════════════════════════════

EOT
}
