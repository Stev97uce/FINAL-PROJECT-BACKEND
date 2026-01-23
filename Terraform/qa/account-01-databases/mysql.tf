# ============================================================
# MYSQL DATABASE SERVER
# ============================================================

resource "aws_instance" "mysql" {
  ami           = var.ami_ubuntu_docker
  instance_type = var.instance_type_mysql
  key_name      = data.aws_key_pair.finalkey.key_name

  subnet_id                   = aws_subnet.private[0].id
  private_ip                  = "10.1.11.10"  # IP fija según plan
  vpc_security_group_ids      = [aws_security_group.mysql.id]
  associate_public_ip_address = false

  user_data = base64encode(file("${path.module}/user-data/mysql.sh"))

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "${var.project_name}-${var.environment}-mysql-root"
    }
  }

  tags = {
    Name     = "${var.project_name}-${var.environment}-mysql"
    Database = "MySQL"
    Role     = "Database-Server"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Volumen adicional para datos de MySQL
resource "aws_ebs_volume" "mysql_data" {
  availability_zone = aws_instance.mysql.availability_zone
  size              = var.mysql_data_volume_size
  type              = "gp3"
  encrypted         = true

  tags = {
    Name = "${var.project_name}-${var.environment}-mysql-data"
  }
}

resource "aws_volume_attachment" "mysql_data" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.mysql_data.id
  instance_id = aws_instance.mysql.id
}

# Outputs
output "mysql_private_ip" {
  value       = aws_instance.mysql.private_ip
  description = "IP privada de MySQL"
}

output "mysql_connection_string" {
  value       = "mysql://admin:Admin123!@#@${aws_instance.mysql.private_ip}:3306/uce_psychology_auth"
  sensitive   = true
  description = "Connection string para MySQL"
}
