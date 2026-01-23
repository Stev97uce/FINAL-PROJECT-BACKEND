# ============================================================
# SECURITY GROUPS - CUENTA 8 (MICROSERVICIOS GRUPO 2)
# ============================================================

# ============================================================
# ROOM SERVICE SECURITY GROUP
# ============================================================

resource "aws_security_group" "room_service" {
  name        = "uce-qa-room-service-sg"
  description = "Security group for Room Service"
  vpc_id      = aws_vpc.microservices_2.id

  # Inbound Rules
  ingress {
    description = "HTTP from API Gateway (Account 10)"
    from_port   = 8004
    to_port     = 8004
    protocol    = "tcp"
    cidr_blocks = ["10.10.0.0/16"]
  }

  ingress {
    description = "HTTP from other microservices (Account 8)"
    from_port   = 8004
    to_port     = 8004
    protocol    = "tcp"
    cidr_blocks = ["10.8.0.0/16"]
  }

  ingress {
    description = "HTTP from Account 7 microservices"
    from_port   = 8004
    to_port     = 8004
    protocol    = "tcp"
    cidr_blocks = ["10.7.0.0/16"]
  }

  ingress {
    description = "HTTP from Account 9 microservices"
    from_port   = 8004
    to_port     = 8004
    protocol    = "tcp"
    cidr_blocks = ["10.9.0.0/16"]
  }

  ingress {
    description = "SSH from Bastion (Account 10 VPC)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.10.0.0/16"]  # Permitir desde toda la VPC de Account 10
  }

  # Outbound Rules
  egress {
    description = "PostgreSQL connection (Account 1)"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["${var.postgresql_host}/32"]
  }

  egress {
    description = "Redis connection (Account 1)"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["${var.redis_host}/32"]
  }

  egress {
    description = "RabbitMQ connection (Account 10)"
    from_port   = 5672
    to_port     = 5672
    protocol    = "tcp"
    cidr_blocks = ["${var.rabbitmq_host}/32"]
  }

  egress {
    description = "Auth Service connection"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["10.7.11.10/32"]
  }

  egress {
    description = "HTTPS for Docker pulls and updates"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "HTTP for package updates"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "DNS"
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "uce-qa-room-service-sg"
    Service = "Room"
  }
}

# ============================================================
# CLINICAL SERVICE SECURITY GROUP
# ============================================================

resource "aws_security_group" "clinical_service" {
  name        = "uce-qa-clinical-service-sg"
  description = "Security group for Clinical Service"
  vpc_id      = aws_vpc.microservices_2.id

  # Inbound Rules
  ingress {
    description = "HTTP from API Gateway (Account 10)"
    from_port   = 8005
    to_port     = 8005
    protocol    = "tcp"
    cidr_blocks = ["10.10.0.0/16"]
  }

  ingress {
    description = "HTTP from other microservices (Account 8)"
    from_port   = 8005
    to_port     = 8005
    protocol    = "tcp"
    cidr_blocks = ["10.8.0.0/16"]
  }

  ingress {
    description = "HTTP from Account 7 microservices"
    from_port   = 8005
    to_port     = 8005
    protocol    = "tcp"
    cidr_blocks = ["10.7.0.0/16"]
  }

  ingress {
    description = "HTTP from Account 9 microservices"
    from_port   = 8005
    to_port     = 8005
    protocol    = "tcp"
    cidr_blocks = ["10.9.0.0/16"]
  }

  ingress {
    description = "SSH from Bastion (Account 10 VPC)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.10.0.0/16"]  # Permitir desde toda la VPC de Account 10
  }

  # Outbound Rules
  egress {
    description = "MongoDB connection (Account 1)"
    from_port   = 27017
    to_port     = 27017
    protocol    = "tcp"
    cidr_blocks = ["${var.mongodb_host}/32"]
  }

  egress {
    description = "Redis connection (Account 1)"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["${var.redis_host}/32"]
  }

  egress {
    description = "RabbitMQ connection (Account 10)"
    from_port   = 5672
    to_port     = 5672
    protocol    = "tcp"
    cidr_blocks = ["${var.rabbitmq_host}/32"]
  }

  egress {
    description = "Auth Service connection"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["10.7.11.10/32"]
  }

  egress {
    description = "HTTPS for Docker pulls and updates"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "HTTP for package updates"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "DNS"
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "uce-qa-clinical-service-sg"
    Service = "Clinical"
  }
}

# ============================================================
# SUPERVISION SERVICE SECURITY GROUP
# ============================================================

resource "aws_security_group" "supervision_service" {
  name        = "uce-qa-supervision-service-sg"
  description = "Security group for Supervision Service"
  vpc_id      = aws_vpc.microservices_2.id

  # Inbound Rules
  ingress {
    description = "HTTP from API Gateway (Account 10)"
    from_port   = 8006
    to_port     = 8006
    protocol    = "tcp"
    cidr_blocks = ["10.10.0.0/16"]
  }

  ingress {
    description = "HTTP from other microservices (Account 8)"
    from_port   = 8006
    to_port     = 8006
    protocol    = "tcp"
    cidr_blocks = ["10.8.0.0/16"]
  }

  ingress {
    description = "HTTP from Account 7 microservices"
    from_port   = 8006
    to_port     = 8006
    protocol    = "tcp"
    cidr_blocks = ["10.7.0.0/16"]
  }

  ingress {
    description = "HTTP from Account 9 microservices"
    from_port   = 8006
    to_port     = 8006
    protocol    = "tcp"
    cidr_blocks = ["10.9.0.0/16"]
  }

  ingress {
    description = "SSH from Bastion (Account 10 VPC)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.10.0.0/16"]  # Permitir desde toda la VPC de Account 10
  }

  # Outbound Rules
  egress {
    description = "PostgreSQL connection (Account 1)"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["${var.postgresql_host}/32"]
  }

  egress {
    description = "Redis connection (Account 1)"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["${var.redis_host}/32"]
  }

  egress {
    description = "RabbitMQ connection (Account 10)"
    from_port   = 5672
    to_port     = 5672
    protocol    = "tcp"
    cidr_blocks = ["${var.rabbitmq_host}/32"]
  }

  egress {
    description = "Auth Service connection"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["10.7.11.10/32"]
  }

  egress {
    description = "Clinical Service connection"
    from_port   = 8005
    to_port     = 8005
    protocol    = "tcp"
    cidr_blocks = ["${var.clinical_service_ip}/32"]
  }

  egress {
    description = "HTTPS for Docker pulls and updates"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "HTTP for package updates"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "DNS"
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "uce-qa-supervision-service-sg"
    Service = "Supervision"
  }
}

# ============================================================
# NOTIFICATION SERVICE SECURITY GROUP
# ============================================================

resource "aws_security_group" "notification_service" {
  name        = "uce-qa-notification-service-sg"
  description = "Security group for Notification Service"
  vpc_id      = aws_vpc.microservices_2.id

  # Inbound Rules
  ingress {
    description = "HTTP from API Gateway (Account 10)"
    from_port   = 8007
    to_port     = 8007
    protocol    = "tcp"
    cidr_blocks = ["10.10.0.0/16"]
  }

  ingress {
    description = "HTTP from other microservices (Account 8)"
    from_port   = 8007
    to_port     = 8007
    protocol    = "tcp"
    cidr_blocks = ["10.8.0.0/16"]
  }

  ingress {
    description = "HTTP from Account 7 microservices"
    from_port   = 8007
    to_port     = 8007
    protocol    = "tcp"
    cidr_blocks = ["10.7.0.0/16"]
  }

  ingress {
    description = "HTTP from Account 9 microservices"
    from_port   = 8007
    to_port     = 8007
    protocol    = "tcp"
    cidr_blocks = ["10.9.0.0/16"]
  }

  ingress {
    description = "SSH from Bastion (Account 10 VPC)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.10.0.0/16"]  # Permitir desde toda la VPC de Account 10
  }

  # Outbound Rules
  egress {
    description = "MongoDB connection (Account 1)"
    from_port   = 27017
    to_port     = 27017
    protocol    = "tcp"
    cidr_blocks = ["${var.mongodb_host}/32"]
  }

  egress {
    description = "Redis connection (Account 1)"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["${var.redis_host}/32"]
  }

  egress {
    description = "RabbitMQ connection (Account 10)"
    from_port   = 5672
    to_port     = 5672
    protocol    = "tcp"
    cidr_blocks = ["${var.rabbitmq_host}/32"]
  }

  egress {
    description = "Auth Service connection"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["10.7.11.10/32"]
  }

  egress {
    description = "HTTPS for Docker pulls and updates"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "HTTP for package updates"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "DNS"
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "uce-qa-notification-service-sg"
    Service = "Notification"
  }
}
