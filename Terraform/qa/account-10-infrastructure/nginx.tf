# ============================================================
# NGINX LOAD BALANCER - ENTRADA PRINCIPAL
# ============================================================

# Elastic IP para NGINX
resource "aws_eip" "nginx" {
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-${var.environment}-nginx-eip"
  }

  depends_on = [aws_internet_gateway.infrastructure]
}

# Asociar Elastic IP al NGINX
resource "aws_eip_association" "nginx" {
  instance_id   = aws_instance.nginx.id
  allocation_id = aws_eip.nginx.id
}

# Instancia EC2 NGINX
resource "aws_instance" "nginx" {
  ami           = var.ami_ubuntu_docker
  instance_type = var.instance_type_nginx
  key_name      = aws_key_pair.finalkey.key_name

  subnet_id                   = aws_subnet.public[0].id
  private_ip                  = "10.10.1.20"  # IP fija según plan de IPs
  vpc_security_group_ids      = [aws_security_group.nginx.id]
  associate_public_ip_address = true

  user_data = base64encode(templatefile("${path.module}/user-data/nginx.sh", {
    hostname              = "nginx-lb-qa"
    api_gateway_qa_ip     = "10.10.1.30"  # IP privada para comunicación interna
    auth_service_ip       = "10.7.11.10"
    user_service_ip       = "10.7.11.11"
    patient_service_ip    = "10.7.11.12"
    appointment_service_ip = "10.7.11.13"
    room_service_ip       = "10.8.11.10"
    clinical_service_ip   = "10.8.11.11"
    supervision_service_ip = "10.8.11.12"
    notification_service_ip = "10.8.11.13"
    reporting_service_ip  = "10.9.11.10"
    analytics_service_ip  = "10.9.11.11"
  }))

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "${var.project_name}-${var.environment}-nginx-root"
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-nginx-lb"
    Role = "Load-Balancer-NGINX"
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_instance.api_gateway_qa
  ]
}

# Output
output "nginx_public_ip" {
  value       = aws_eip.nginx.public_ip
  description = "IP pública del NGINX Load Balancer"
}

output "nginx_url" {
  value       = "http://${aws_eip.nginx.public_ip}"
  description = "URL principal del sistema (NGINX)"
}

output "nginx_admin_url" {
  value       = "http://${aws_eip.nginx.public_ip}:8080/status"
  description = "URL del NGINX status page"
}
