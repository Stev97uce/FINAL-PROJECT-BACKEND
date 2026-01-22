# ============================================================
# OUTPUTS - CUENTA 1 (DATABASES)
# ============================================================

output "databases_summary" {
  value = <<-EOT
  
  ╔══════════════════════════════════════════════════════════════════╗
  ║         CUENTA 1 - BASES DE DATOS - QA ENVIRONMENT              ║
  ╚══════════════════════════════════════════════════════════════════╝
  
  🗄️  MYSQL (Auth Service):
     IP Privada: ${aws_instance.mysql.private_ip}
     Puerto: 3306
     Usuario: admin
     Contraseña: Admin123!@#
     Base de datos: uce_psychology_auth
  
  🐘 POSTGRESQL (User, Patient, Appointment, Room, Supervision, Reporting):
     IP Privada: ${aws_instance.postgresql.private_ip}
     Puerto: 5432
     Usuario: admin
     Contraseña: Admin123!@#
     Base de datos: uce_psychology
  
  🍃 MONGODB (Clinical, Notification, Analytics):
     IP Privada: ${aws_instance.mongodb.private_ip}
     Puerto: 27017
     Usuario: admin
     Contraseña: Admin123!@#
  
  ⚡ REDIS (Cache para todos los servicios):
     IP Privada: ${aws_instance.redis.private_ip}
     Puerto: 6379
     Contraseña: Admin123!@#
  
  🔑 KEY PAIR:
     Nombre: ${data.aws_key_pair.finalkey.key_name}
     Archivo: ../shared/finalkey.pem
  
  🌍 VPC:
     ID: ${aws_vpc.databases.id}
     CIDR: ${aws_vpc.databases.cidr_block}
  
  🔗 VPC PEERING:
     ${var.enable_vpc_peering && var.account_10_vpc_id != "" ? "✅ Conectado con Cuenta 10 (Infrastructure)" : "⚠️  Pendiente: Esperar VPC Peering de Cuenta 10"}
  
  ═══════════════════════════════════════════════════════════════════
  🔐 ACCESO VÍA BASTION (SSH Tunneling):
  
  MySQL:
  ssh -i ../shared/finalkey.pem -L 3306:${aws_instance.mysql.private_ip}:3306 ubuntu@${var.bastion_ip}
  
  PostgreSQL:
  ssh -i ../shared/finalkey.pem -L 5432:${aws_instance.postgresql.private_ip}:5432 ubuntu@${var.bastion_ip}
  
  MongoDB:
  ssh -i ../shared/finalkey.pem -L 27017:${aws_instance.mongodb.private_ip}:27017 ubuntu@${var.bastion_ip}
  
  Redis:
  ssh -i ../shared/finalkey.pem -L 6379:${aws_instance.redis.private_ip}:6379 ubuntu@${var.bastion_ip}
  ═══════════════════════════════════════════════════════════════════
  
  EOT
  description = "Resumen completo de las bases de datos desplegadas"
}

# Database IPs for microservices
output "database_ips" {
  value = {
    mysql      = aws_instance.mysql.private_ip
    postgresql = aws_instance.postgresql.private_ip
    mongodb    = aws_instance.mongodb.private_ip
    redis      = aws_instance.redis.private_ip
  }
  description = "IPs privadas de todas las bases de datos"
}
