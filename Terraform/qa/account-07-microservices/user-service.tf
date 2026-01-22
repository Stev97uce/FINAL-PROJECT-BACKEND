# ============================================================
# USER SERVICE - EC2 INSTANCE
# ============================================================

resource "aws_instance" "user_service" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = aws_key_pair.finalkey.key_name
  
  subnet_id                   = aws_subnet.private[0].id
  vpc_security_group_ids      = [aws_security_group.user_service.id]
  private_ip                  = var.user_service_ip
  associate_public_ip_address = false

  user_data = file("${path.module}/user-data/user-service.sh")

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "uce-qa-user-service-root"
    }
  }

  tags = {
    Name        = "uce-qa-user-service"
    Service     = "User"
    Port        = "8001"
    Database    = "PostgreSQL"
    DockerImage = var.docker_images["user"]
  }

  depends_on = [
    aws_nat_gateway.microservices_1,
    aws_instance.auth_service
  ]
}
