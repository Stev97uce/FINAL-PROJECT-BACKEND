# ============================================================
# POSTGRESQL DATABASE SERVER
# ============================================================

resource "aws_instance" "postgresql" {
  ami           = var.ami_ubuntu_docker
  instance_type = var.instance_type_postgresql
  key_name      = data.aws_key_pair.finalkey.key_name

  subnet_id                   = aws_subnet.private[0].id
  private_ip                  = "10.1.11.20"  # IP fija según plan
  vpc_security_group_ids      = [aws_security_group.postgresql.id]
  associate_public_ip_address = false

  user_data = base64encode(file("${path.module}/user-data/postgresql.sh"))

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "${var.project_name}-${var.environment}-postgresql-root"
    }
  }

  tags = {
    Name     = "${var.project_name}-${var.environment}-postgresql"
    Database = "PostgreSQL"
    Role     = "Database-Server"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Volumen adicional para datos de PostgreSQL
resource "aws_ebs_volume" "postgresql_data" {
  availability_zone = aws_instance.postgresql.availability_zone
  size              = var.postgresql_data_volume_size
  type              = "gp3"
  encrypted         = true

  tags = {
    Name = "${var.project_name}-${var.environment}-postgresql-data"
  }
}

resource "aws_volume_attachment" "postgresql_data" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.postgresql_data.id
  instance_id = aws_instance.postgresql.id
}

# Outputs
output "postgresql_private_ip" {
  value       = aws_instance.postgresql.private_ip
  description = "IP privada de PostgreSQL"
}

output "postgresql_connection_string" {
  value       = "postgresql://admin:Admin123!@#@${aws_instance.postgresql.private_ip}:5432/uce_psychology"
  sensitive   = true
  description = "Connection string para PostgreSQL"
}
