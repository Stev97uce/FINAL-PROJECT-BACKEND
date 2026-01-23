# ============================================================
# RABBITMQ + MQTT
# ============================================================

# Instancia EC2 RabbitMQ (subnet privada - sin EIP necesaria) + MQTT
resource "aws_instance" "rabbitmq" {
  ami           = var.ami_ubuntu_docker
  instance_type = var.instance_type_rabbitmq
  key_name      = aws_key_pair.finalkey.key_name

  subnet_id                   = aws_subnet.private[0].id
  private_ip                  = "10.10.11.50"  # IP fija según plan de IPs
  vpc_security_group_ids      = [aws_security_group.rabbitmq.id]
  associate_public_ip_address = false

  user_data = base64encode(templatefile("${path.module}/user-data/rabbitmq.sh", {
    hostname        = "rabbitmq-qa"
    rabbitmq_image  = var.docker_images.rabbitmq
    rabbitmq_user   = "uce_admin"
    rabbitmq_pass   = "UCE_RabbitMQ_2026_Secure!"
  }))

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 30
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "${var.project_name}-${var.environment}-rabbitmq-root"
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-rabbitmq"
    Role = "Message-Broker-RabbitMQ-MQTT"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Output
output "rabbitmq_private_ip" {
  value       = aws_instance.rabbitmq.private_ip
  description = "IP privada del servidor RabbitMQ"
}

output "rabbitmq_management_url" {
  value       = "http://${aws_instance.rabbitmq.private_ip}:15672"
  description = "URL del RabbitMQ Management UI (accesible via Bastion)"
}
