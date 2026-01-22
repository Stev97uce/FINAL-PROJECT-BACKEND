# ============================================================
# REDIS CACHE SERVER
# ============================================================

resource "aws_instance" "redis" {
  ami           = var.ami_ubuntu_docker
  instance_type = var.instance_type_redis
  key_name      = data.aws_key_pair.finalkey.key_name

  subnet_id                   = aws_subnet.private[0].id
  private_ip                  = "10.1.11.40"  # IP fija según plan
  vpc_security_group_ids      = [aws_security_group.redis.id]
  associate_public_ip_address = false

  user_data = base64encode(file("${path.module}/user-data/redis.sh"))

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "${var.project_name}-${var.environment}-redis-root"
    }
  }

  tags = {
    Name     = "${var.project_name}-${var.environment}-redis"
    Database = "Redis"
    Role     = "Cache-Server"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Volumen adicional para datos de Redis
resource "aws_ebs_volume" "redis_data" {
  availability_zone = aws_instance.redis.availability_zone
  size              = var.redis_data_volume_size
  type              = "gp3"
  encrypted         = true

  tags = {
    Name = "${var.project_name}-${var.environment}-redis-data"
  }
}

resource "aws_volume_attachment" "redis_data" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.redis_data.id
  instance_id = aws_instance.redis.id
}

# Outputs
output "redis_private_ip" {
  value       = aws_instance.redis.private_ip
  description = "IP privada de Redis"
}

output "redis_connection_string" {
  value       = "redis://:Admin123!@#@${aws_instance.redis.private_ip}:6379"
  sensitive   = true
  description = "Connection string para Redis"
}
