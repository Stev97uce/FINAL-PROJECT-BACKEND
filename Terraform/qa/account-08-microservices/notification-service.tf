# ============================================================
# NOTIFICATION SERVICE - EC2 INSTANCE
# ============================================================

resource "aws_instance" "notification_service" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = aws_key_pair.finalkey.key_name
  
  subnet_id                   = aws_subnet.private[0].id
  vpc_security_group_ids      = [aws_security_group.notification_service.id]
  private_ip                  = var.notification_service_ip
  associate_public_ip_address = false

  user_data = file("${path.module}/user-data/notification-service.sh")

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "uce-qa-notification-service-root"
    }
  }

  tags = {
    Name        = "uce-qa-notification-service"
    Service     = "Notification"
    Port        = "8007"
    Database    = "MongoDB"
    DockerImage = var.docker_images["notification"]
  }

  depends_on = [
    aws_nat_gateway.microservices_2
  ]
}
