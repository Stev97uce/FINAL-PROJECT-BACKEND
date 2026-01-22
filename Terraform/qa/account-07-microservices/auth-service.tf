# ============================================================
# AUTH SERVICE - EC2 INSTANCE
# ============================================================

resource "aws_instance" "auth_service" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = aws_key_pair.finalkey.key_name
  
  subnet_id                   = aws_subnet.private[0].id
  vpc_security_group_ids      = [aws_security_group.auth_service.id]
  private_ip                  = var.auth_service_ip
  associate_public_ip_address = false

  user_data = file("${path.module}/user-data/auth-service.sh")

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "uce-qa-auth-service-root"
    }
  }

  tags = {
    Name        = "uce-qa-auth-service"
    Service     = "Auth"
    Port        = "8000"
    Database    = "MySQL"
    DockerImage = var.docker_images["auth"]
  }

  depends_on = [
    aws_nat_gateway.microservices_1
  ]
}
