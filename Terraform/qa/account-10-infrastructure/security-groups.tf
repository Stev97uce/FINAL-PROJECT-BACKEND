# ============================================================
# SECURITY GROUPS - CUENTA 10 (INFRAESTRUCTURA)
# ============================================================

# ===== SECURITY GROUP PARA BASTION =====
resource "aws_security_group" "bastion" {
  name        = "${var.project_name}-${var.environment}-bastion-sg"
  description = "Security group para Bastion Host - Tunel para todas las cuentas"
  vpc_id      = aws_vpc.infrastructure.id

  # SSH desde cualquier lugar (cambiar en producción)
  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidrs
  }

  # SSH desde otras cuentas
  ingress {
    description = "SSH from Account 1 (Databases)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.account_01_cidr]
  }

  ingress {
    description = "SSH from Account 7 (Microservices)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.account_07_cidr]
  }

  ingress {
    description = "SSH from Account 8 (Microservices)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.account_08_cidr]
  }

  ingress {
    description = "SSH from Account 9 (Microservices + Monitoring)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.account_09_cidr]
  }

  # Permitir TODO el tráfico desde la VPC local
  ingress {
    description = "All traffic from local VPC"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  # Permitir TODO el tráfico desde otras cuentas (para tunneling)
  ingress {
    description = "All traffic from Account 1"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = [var.account_01_cidr]
  }

  ingress {
    description = "All traffic from Account 7"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = [var.account_07_cidr]
  }

  ingress {
    description = "All traffic from Account 8"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = [var.account_08_cidr]
  }

  ingress {
    description = "All traffic from Account 9"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = [var.account_09_cidr]
  }

  # Permitir TODO el tráfico saliente
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-bastion-sg"
  }
}

# ===== SECURITY GROUP PARA KAFKA =====
resource "aws_security_group" "kafka" {
  name        = "${var.project_name}-${var.environment}-kafka-sg"
  description = "Security group para Kafka Cluster"
  vpc_id      = aws_vpc.infrastructure.id

  # Kafka Broker
  ingress {
    description = "Kafka Broker"
    from_port   = var.kafka_ports.broker
    to_port     = var.kafka_ports.broker
    protocol    = "tcp"
    cidr_blocks = [
      var.vpc_cidr,
      var.account_01_cidr,
      var.account_07_cidr,
      var.account_08_cidr,
      var.account_09_cidr
    ]
  }

  # Zookeeper
  ingress {
    description = "Zookeeper"
    from_port   = var.kafka_ports.zookeeper
    to_port     = var.kafka_ports.zookeeper
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  # JMX para monitoreo
  ingress {
    description = "JMX Monitoring"
    from_port   = var.kafka_ports.jmx
    to_port     = var.kafka_ports.jmx
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr, var.account_09_cidr]
  }

  # SSH desde Bastion
  ingress {
    description     = "SSH from Bastion"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-kafka-sg"
  }
}

# ===== SECURITY GROUP PARA RABBITMQ + MQTT =====
resource "aws_security_group" "rabbitmq" {
  name        = "${var.project_name}-${var.environment}-rabbitmq-sg"
  description = "Security group para RabbitMQ + MQTT"
  vpc_id      = aws_vpc.infrastructure.id

  # AMQP (RabbitMQ)
  ingress {
    description = "AMQP Protocol"
    from_port   = var.rabbitmq_ports.amqp
    to_port     = var.rabbitmq_ports.amqp
    protocol    = "tcp"
    cidr_blocks = [
      var.vpc_cidr,
      var.account_01_cidr,
      var.account_07_cidr,
      var.account_08_cidr,
      var.account_09_cidr
    ]
  }

  # RabbitMQ Management UI
  ingress {
    description = "RabbitMQ Management UI"
    from_port   = var.rabbitmq_ports.management
    to_port     = var.rabbitmq_ports.management
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Acceso público para management
  }

  # MQTT
  ingress {
    description = "MQTT Protocol"
    from_port   = var.rabbitmq_ports.mqtt
    to_port     = var.rabbitmq_ports.mqtt
    protocol    = "tcp"
    cidr_blocks = [
      var.vpc_cidr,
      var.account_07_cidr,
      var.account_08_cidr,
      var.account_09_cidr
    ]
  }

  # MQTT WebSockets
  ingress {
    description = "MQTT over WebSockets"
    from_port   = var.rabbitmq_ports.mqtt_ws
    to_port     = var.rabbitmq_ports.mqtt_ws
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # STOMP
  ingress {
    description = "STOMP Protocol"
    from_port   = var.rabbitmq_ports.stomp
    to_port     = var.rabbitmq_ports.stomp
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  # SSH desde Bastion
  ingress {
    description     = "SSH from Bastion"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-rabbitmq-sg"
  }
}

# ===== SECURITY GROUP PARA API GATEWAY (QA) =====
resource "aws_security_group" "api_gateway_qa" {
  name        = "${var.project_name}-${var.environment}-api-gateway-qa-sg"
  description = "Security group para API Gateway QA"
  vpc_id      = aws_vpc.infrastructure.id

  # HTTP
  ingress {
    description = "HTTP"
    from_port   = var.api_gateway_ports.http
    to_port     = var.api_gateway_ports.http
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS
  ingress {
    description = "HTTPS"
    from_port   = var.api_gateway_ports.https
    to_port     = var.api_gateway_ports.https
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Admin API
  ingress {
    description = "Admin API"
    from_port   = var.api_gateway_ports.admin
    to_port     = var.api_gateway_ports.admin
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  # Comunicación con microservicios
  ingress {
    description = "From Microservices"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = [
      var.account_07_cidr,
      var.account_08_cidr,
      var.account_09_cidr
    ]
  }

  # SSH desde Bastion
  ingress {
    description     = "SSH from Bastion"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-api-gateway-qa-sg"
  }
}

# ===== SECURITY GROUP PARA NGINX =====
resource "aws_security_group" "nginx" {
  name        = "${var.project_name}-${var.environment}-nginx-sg"
  description = "Security group para NGINX Load Balancer"
  vpc_id      = aws_vpc.infrastructure.id

  # HTTP
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Puerto 8080 para admin/stats
  ingress {
    description = "NGINX Admin"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  # SSH desde Bastion
  ingress {
    description     = "SSH from Bastion"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-nginx-sg"
  }
}
