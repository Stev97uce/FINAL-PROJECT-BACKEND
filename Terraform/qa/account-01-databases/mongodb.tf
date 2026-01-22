# ============================================================
# MONGODB DATABASE SERVER
# ============================================================

resource "aws_instance" "mongodb" {
  ami           = var.ami_ubuntu_docker
  instance_type = var.instance_type_mongodb
  key_name      = data.aws_key_pair.finalkey.key_name

  subnet_id                   = aws_subnet.private[0].id
  private_ip                  = "10.1.11.30"  # IP fija según plan
  vpc_security_group_ids      = [aws_security_group.mongodb.id]
  associate_public_ip_address = false

  user_data = base64encode(file("${path.module}/user-data/mongodb.sh"))

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "${var.project_name}-${var.environment}-mongodb-root"
    }
  }

  tags = {
    Name     = "${var.project_name}-${var.environment}-mongodb"
    Database = "MongoDB"
    Role     = "Database-Server"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Volumen adicional para datos de MongoDB
resource "aws_ebs_volume" "mongodb_data" {
  availability_zone = aws_instance.mongodb.availability_zone
  size              = var.mongodb_data_volume_size
  type              = "gp3"
  encrypted         = true

  tags = {
    Name = "${var.project_name}-${var.environment}-mongodb-data"
  }
}

resource "aws_volume_attachment" "mongodb_data" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.mongodb_data.id
  instance_id = aws_instance.mongodb.id
}

# Outputs
output "mongodb_private_ip" {
  value       = aws_instance.mongodb.private_ip
  description = "IP privada de MongoDB"
}

output "mongodb_connection_string" {
  value       = "mongodb://admin:Admin123!@#@${aws_instance.mongodb.private_ip}:27017/uce_psychology?authSource=admin"
  sensitive   = true
  description = "Connection string para MongoDB"
}
