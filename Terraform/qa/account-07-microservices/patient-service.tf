# ============================================================
# PATIENT SERVICE - EC2 INSTANCE
# ============================================================

resource "aws_instance" "patient_service" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = aws_key_pair.finalkey.key_name
  
  subnet_id                   = aws_subnet.private[0].id
  vpc_security_group_ids      = [aws_security_group.patient_service.id]
  private_ip                  = var.patient_service_ip
  associate_public_ip_address = false

  user_data = file("${path.module}/user-data/patient-service.sh")

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "uce-qa-patient-service-root"
    }
  }

  tags = {
    Name        = "uce-qa-patient-service"
    Service     = "Patient"
    Port        = "8002"
    Database    = "PostgreSQL"
    DockerImage = var.docker_images["patient"]
  }

  depends_on = [
    aws_nat_gateway.microservices_1,
    aws_instance.auth_service,
    aws_instance.user_service
  ]
}
