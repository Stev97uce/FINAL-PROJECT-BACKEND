# ============================================================
# BASTION HOST - TÚNEL PARA TODAS LAS CUENTAS
# ============================================================

# Elastic IP para Bastion
resource "aws_eip" "bastion" {
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-${var.environment}-bastion-eip"
  }

  depends_on = [aws_internet_gateway.infrastructure]
}

# Asociar Elastic IP al Bastion
resource "aws_eip_association" "bastion" {
  instance_id   = aws_instance.bastion.id
  allocation_id = aws_eip.bastion.id
}

# Instancia EC2 Bastion
resource "aws_instance" "bastion" {
  ami           = var.ami_ubuntu_docker
  instance_type = var.instance_type_bastion
  key_name      = aws_key_pair.finalkey.key_name

  subnet_id                   = aws_subnet.public[0].id
  private_ip                  = "10.10.1.10"  # IP fija según plan de IPs
  vpc_security_group_ids      = [aws_security_group.bastion.id]
  associate_public_ip_address = true

  user_data = base64encode(templatefile("${path.module}/user-data/bastion.sh", {
    hostname = "bastion-qa"
  }))

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "${var.project_name}-${var.environment}-bastion-root"
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-bastion"
    Role = "Bastion-Tunnel"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Output para fácil acceso SSH
output "bastion_public_ip" {
  value       = aws_eip.bastion.public_ip
  description = "IP pública del Bastion Host"
}

output "bastion_ssh_command" {
  value       = "ssh -i ../shared/finalkey.pem ubuntu@${aws_eip.bastion.public_ip}"
  description = "Comando SSH para conectarse al Bastion"
}
