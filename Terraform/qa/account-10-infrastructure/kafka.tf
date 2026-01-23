# ============================================================
# KAFKA CLUSTER
# ============================================================

# Instancia EC2 Kafka (subnet privada - sin EIP necesaria)
resource "aws_instance" "kafka" {
  ami           = var.ami_ubuntu_docker
  instance_type = var.instance_type_kafka
  key_name      = aws_key_pair.finalkey.key_name

  subnet_id                   = aws_subnet.private[0].id
  private_ip                  = "10.10.11.60"  # IP fija según plan de IPs
  vpc_security_group_ids      = [aws_security_group.kafka.id]
  associate_public_ip_address = false

  user_data = base64encode(templatefile("${path.module}/user-data/kafka.sh", {
    hostname       = "kafka-qa"
    kafka_image    = var.docker_images.kafka
    zookeeper_image = var.docker_images.zookeeper
  }))

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 50
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "${var.project_name}-${var.environment}-kafka-root"
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-kafka"
    Role = "Message-Broker-Kafka"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Output
output "kafka_private_ip" {
  value       = aws_instance.kafka.private_ip
  description = "IP privada del servidor Kafka"
}
