# ============================================================
# OUTPUTS - CUENTA 8 (MICROSERVICIOS GRUPO 2)
# ============================================================

# VPC Information
output "vpc_id" {
  description = "VPC ID for Microservices Account 8"
  value       = aws_vpc.microservices_2.id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.microservices_2.cidr_block
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

# Room Service
output "room_service_info" {
  description = "Room Service information"
  value = {
    private_ip  = aws_instance.room_service.private_ip
    instance_id = aws_instance.room_service.id
    port        = 8004
    database    = "PostgreSQL (${var.postgresql_host})"
    url         = "http://${aws_instance.room_service.private_ip}:8004"
  }
}

# Clinical Service
output "clinical_service_info" {
  description = "Clinical Service information"
  value = {
    private_ip  = aws_instance.clinical_service.private_ip
    instance_id = aws_instance.clinical_service.id
    port        = 8005
    database    = "MongoDB (${var.mongodb_host})"
    url         = "http://${aws_instance.clinical_service.private_ip}:8005"
  }
}

# Supervision Service
output "supervision_service_info" {
  description = "Supervision Service information"
  value = {
    private_ip  = aws_instance.supervision_service.private_ip
    instance_id = aws_instance.supervision_service.id
    port        = 8006
    database    = "PostgreSQL (${var.postgresql_host})"
    url         = "http://${aws_instance.supervision_service.private_ip}:8006"
  }
}

# Notification Service
output "notification_service_info" {
  description = "Notification Service information"
  value = {
    private_ip  = aws_instance.notification_service.private_ip
    instance_id = aws_instance.notification_service.id
    port        = 8007
    database    = "MongoDB (${var.mongodb_host})"
    url         = "http://${aws_instance.notification_service.private_ip}:8007"
  }
}

# All Microservices IPs
output "microservices_ips" {
  description = "All microservices private IPs"
  value = {
    room        = aws_instance.room_service.private_ip
    clinical    = aws_instance.clinical_service.private_ip
    supervision = aws_instance.supervision_service.private_ip
    notification = aws_instance.notification_service.private_ip
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
    room        = "ssh -i ../shared/finalkey.pem -J ubuntu@${var.bastion_ip} ubuntu@${aws_instance.room_service.private_ip}"
    clinical    = "ssh -i ../shared/finalkey.pem -J ubuntu@${var.bastion_ip} ubuntu@${aws_instance.clinical_service.private_ip}"
    supervision = "ssh -i ../shared/finalkey.pem -J ubuntu@${var.bastion_ip} ubuntu@${aws_instance.supervision_service.private_ip}"
    notification = "ssh -i ../shared/finalkey.pem -J ubuntu@${var.bastion_ip} ubuntu@${aws_instance.notification_service.private_ip}"
  }
}

# Summary
output "microservices_summary" {
  description = "Complete summary of microservices deployment"
  value = <<EOT

╔══════════════════════════════════════════════════════════════════╗
║      CUENTA 8 - MICROSERVICIOS GRUPO 2 - QA ENVIRONMENT         ║
╚══════════════════════════════════════════════════════════════════╝

🏠 ROOM SERVICE:
   IP: ${aws_instance.room_service.private_ip}:8004
   URL: http://${aws_instance.room_service.private_ip}:8004
   Database: PostgreSQL (${var.postgresql_host}:5432)
   Cache: Redis (${var.redis_host}:6379)
   SSH: ssh -i ../shared/finalkey.pem -J ubuntu@${var.bastion_ip} ubuntu@${aws_instance.room_service.private_ip}

🏥 CLINICAL SERVICE:
   IP: ${aws_instance.clinical_service.private_ip}:8005
   URL: http://${aws_instance.clinical_service.private_ip}:8005
   Database: MongoDB (${var.mongodb_host}:27017)
   Cache: Redis (${var.redis_host}:6379)
   SSH: ssh -i ../shared/finalkey.pem -J ubuntu@${var.bastion_ip} ubuntu@${aws_instance.clinical_service.private_ip}

👨‍🏫 SUPERVISION SERVICE:
   IP: ${aws_instance.supervision_service.private_ip}:8006
   URL: http://${aws_instance.supervision_service.private_ip}:8006
   Database: PostgreSQL (${var.postgresql_host}:5432)
   Cache: Redis (${var.redis_host}:6379)
   SSH: ssh -i ../shared/finalkey.pem -J ubuntu@${var.bastion_ip} ubuntu@${aws_instance.supervision_service.private_ip}

📧 NOTIFICATION SERVICE:
   IP: ${aws_instance.notification_service.private_ip}:8007
   URL: http://${aws_instance.notification_service.private_ip}:8007
   Database: MongoDB (${var.mongodb_host}:27017)
   Cache: Redis (${var.redis_host}:6379)
   SSH: ssh -i ../shared/finalkey.pem -J ubuntu@${var.bastion_ip} ubuntu@${aws_instance.notification_service.private_ip}

📨 MESSAGE BROKER:
   RabbitMQ: ${var.rabbitmq_host}:5672

🌍 VPC:
   ID: ${aws_vpc.microservices_2.id}
   CIDR: ${aws_vpc.microservices_2.cidr_block}

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
