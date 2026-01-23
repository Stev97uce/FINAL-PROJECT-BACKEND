# ============================================================
# OUTPUTS - CUENTA 10 (INFRAESTRUCTURA)
# ============================================================

# ===== KEY PAIR =====
output "key_pair_name" {
  value       = aws_key_pair.finalkey.key_name
  description = "Nombre del key pair creado"
}

output "private_key_path" {
  value       = local_file.private_key.filename
  description = "Ruta al archivo de clave privada"
  sensitive   = true
}

# ===== VPC =====
output "vpc_id" {
  value       = aws_vpc.infrastructure.id
  description = "ID de la VPC de infraestructura"
}

output "vpc_cidr" {
  value       = aws_vpc.infrastructure.cidr_block
  description = "CIDR block de la VPC"
}

# ===== BASTION =====
output "bastion_connection_info" {
  value = {
    public_ip    = aws_eip.bastion.public_ip
    private_ip   = aws_instance.bastion.private_ip
    ssh_command  = "ssh -i ../shared/finalkey.pem ubuntu@${aws_eip.bastion.public_ip}"
  }
  description = "Información de conexión del Bastion Host"
}

# ===== NGINX =====
output "nginx_info" {
  value = {
    public_ip       = aws_eip.nginx.public_ip
    url             = "http://${aws_eip.nginx.public_ip}"
    status_url      = "http://${aws_eip.nginx.public_ip}:8080/status"
  }
  description = "Información del NGINX Load Balancer (PUNTO DE ENTRADA PRINCIPAL)"
}

# ===== API GATEWAYS =====
output "api_gateway_qa_info" {
  value = {
    public_ip  = aws_eip.api_gateway_qa.public_ip
    private_ip = aws_instance.api_gateway_qa.private_ip
    url        = "http://${aws_eip.api_gateway_qa.public_ip}"
    admin_url  = "http://${aws_instance.api_gateway_qa.private_ip}:8001"
  }
  description = "Información del API Gateway QA (Kong)"
}

# API Gateway PROD eliminado - se creará en el ambiente de producción

# ===== KAFKA =====
output "kafka_info" {
  value = {
    private_ip   = aws_instance.kafka.private_ip
    broker_url   = "${aws_instance.kafka.private_ip}:9092"
    zookeeper    = "${aws_instance.kafka.private_ip}:2181"
  }
  description = "Información del Kafka Cluster (acceso via Bastion)"
}

# ===== RABBITMQ =====
output "rabbitmq_info" {
  value = {
    private_ip      = aws_instance.rabbitmq.private_ip
    amqp_url        = "${aws_instance.rabbitmq.private_ip}:5672"
    management_url  = "http://${aws_instance.rabbitmq.private_ip}:15672"
    mqtt_url        = "${aws_instance.rabbitmq.private_ip}:1883"
  }
  description = "Información del RabbitMQ + MQTT (acceso via Bastion)"
  sensitive   = false
}

# ===== VPC PEERING STATUS =====
output "vpc_peering_status" {
  value = var.enable_vpc_peering ? (
    var.account_01_id != "" && var.account_01_vpc_id != "" ? 
      "✅ VPC Peering configurado y ACTIVO" : 
      "⚠️  VPC Peering HABILITADO pero esperando Account IDs y VPC IDs en terraform.tfvars"
  ) : "❌ VPC Peering DESHABILITADO"
  description = "Estado de la configuración de VPC Peering"
}

# ===== RESUMEN COMPLETO =====
output "infrastructure_summary" {
  value = <<-EOT
  
  ╔══════════════════════════════════════════════════════════════════╗
  ║        CUENTA 10 - INFRAESTRUCTURA - QA ENVIRONMENT             ║
  ╚══════════════════════════════════════════════════════════════════╝
  
  🌐 PUNTO DE ENTRADA PRINCIPAL:
     NGINX Load Balancer: http://${aws_eip.nginx.public_ip}
  
  🔐 BASTION HOST (Túnel SSH):
     IP Pública: ${aws_eip.bastion.public_ip}
     Comando SSH: ssh -i ../shared/finalkey.pem ubuntu@${aws_eip.bastion.public_ip}
  
  🚪 API GATEWAY QA (Kong):
     URL: http://${aws_eip.api_gateway_qa.public_ip}
     Admin API: http://${aws_instance.api_gateway_qa.private_ip}:8001
  
  📨 RABBITMQ + MQTT (acceso via Bastion):
     AMQP: ${aws_instance.rabbitmq.private_ip}:5672
     Management UI: http://${aws_instance.rabbitmq.private_ip}:15672
     MQTT: ${aws_instance.rabbitmq.private_ip}:1883
     Usuario: uce_admin / UCE_RabbitMQ_2026_Secure!
  
  🔄 KAFKA:
     Broker: ${aws_instance.kafka.private_ip}:9092
     Zookeeper: ${aws_instance.kafka.private_ip}:2181
  
  🔑 KEY PAIR:
     Nombre: ${aws_key_pair.finalkey.key_name}
     Archivo: ../shared/finalkey.pem
  
  🌍 VPC:
     ID: ${aws_vpc.infrastructure.id}
     CIDR: ${aws_vpc.infrastructure.cidr_block}
  
  ═══════════════════════════════════════════════════════════════════
  Para conectarse a instancias privadas vía Bastion:
  ssh -i ../shared/finalkey.pem -J ubuntu@${aws_eip.bastion.public_ip} ubuntu@PRIVATE_IP
  ═══════════════════════════════════════════════════════════════════
  
  🔗 VPC PEERING STATUS:
  ${var.enable_vpc_peering ? (
    var.account_01_id != "" && var.account_01_vpc_id != "" ? 
      "✅ Peerings ACTIVOS - Comunicación entre cuentas HABILITADA" : 
      "⚠️  Peering HABILITADO pero esperando IDs - Agregar a terraform.tfvars:\n     account_01_id, account_01_vpc_id, account_07_id, etc.\n     Luego ejecutar: terraform apply"
  ) : "❌ VPC Peering DESHABILITADO - No hay comunicación entre cuentas"}
  
  EOT
  description = "Resumen completo de la infraestructura desplegada"
}

# ===== CONEXIÓN PARA OTRAS CUENTAS =====
output "bastion_ip_for_other_accounts" {
  value       = aws_eip.bastion.public_ip
  description = "IP del Bastion para configurar en otras cuentas"
}

output "rabbitmq_connection_string" {
  value       = "amqp://uce_admin:UCE_RabbitMQ_2026_Secure!@${aws_instance.rabbitmq.private_ip}:5672/"
  description = "Connection string de RabbitMQ para microservicios"
  sensitive   = true
}

output "kafka_bootstrap_servers" {
  value       = "${aws_instance.kafka.private_ip}:9092"
  description = "Kafka bootstrap servers para microservicios"
}
