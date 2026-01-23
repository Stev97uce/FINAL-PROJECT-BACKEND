# ============================================================
# SECURITY GROUPS - CUENTA 7 (MICROSERVICIOS GRUPO 1)
# ============================================================

# ============================================================
# AUTH SERVICE SECURITY GROUP
# ============================================================

resource "aws_security_group" "auth_service" {
  name        = "uce-qa-auth-service-sg"
  description = "Security group for Auth Service"
  vpc_id      = aws_vpc.microservices_1.id

  # Inbound Rules
  ingress {
    description = "HTTP from API Gateway (Account 10)"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["10.10.0.0/16"]
  }

  ingress {
    description = "HTTP from other microservices (Account 7)"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["10.7.0.0/16"]
  }

  ingress {
    description = "HTTP from Account 8 microservices"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["10.8.0.0/16"]
  }

  ingress {
    description = "HTTP from Account 9 microservices"
    from_port   = 8000
    to_port     = 8000
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
    description = "MySQL connection (Account 1)"
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["${var.mysql_host}/32"]
  }

  egress {
    description = "RabbitMQ connection (Account 10)"
    from_port   = 5672
    to_port     = 5672
    protocol    = "tcp"
    cidr_blocks = ["${var.rabbitmq_host}/32"]
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
    Name = "uce-qa-auth-service-sg"
    Service = "Auth"
  }
}

# ============================================================
# USER SERVICE SECURITY GROUP
# ============================================================

resource "aws_security_group" "user_service" {
  name        = "uce-qa-user-service-sg"
  description = "Security group for User Service"
  vpc_id      = aws_vpc.microservices_1.id

  # Inbound Rules
  ingress {
    description = "HTTP from API Gateway (Account 10)"
    from_port   = 8001
    to_port     = 8001
    protocol    = "tcp"
    cidr_blocks = ["10.10.0.0/16"]
  }

  ingress {
    description = "HTTP from other microservices (Account 7)"
    from_port   = 8001
    to_port     = 8001
    protocol    = "tcp"
    cidr_blocks = ["10.7.0.0/16"]
  }

  ingress {
    description = "HTTP from Account 8 microservices"
    from_port   = 8001
    to_port     = 8001
    protocol    = "tcp"
    cidr_blocks = ["10.8.0.0/16"]
  }

  ingress {
    description = "HTTP from Account 9 microservices"
    from_port   = 8001
    to_port     = 8001
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
    cidr_blocks = ["${var.auth_service_ip}/32"]
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
    Name = "uce-qa-user-service-sg"
    Service = "User"
  }
}

# ============================================================
# PATIENT SERVICE SECURITY GROUP
# ============================================================

resource "aws_security_group" "patient_service" {
  name        = "uce-qa-patient-service-sg"
  description = "Security group for Patient Service"
  vpc_id      = aws_vpc.microservices_1.id

  # Inbound Rules
  ingress {
    description = "HTTP from API Gateway (Account 10)"
    from_port   = 8002
    to_port     = 8002
    protocol    = "tcp"
    cidr_blocks = ["10.10.0.0/16"]
  }

  ingress {
    description = "HTTP from other microservices (Account 7)"
    from_port   = 8002
    to_port     = 8002
    protocol    = "tcp"
    cidr_blocks = ["10.7.0.0/16"]
  }

  ingress {
    description = "HTTP from Account 8 microservices"
    from_port   = 8002
    to_port     = 8002
    protocol    = "tcp"
    cidr_blocks = ["10.8.0.0/16"]
  }

  ingress {
    description = "HTTP from Account 9 microservices"
    from_port   = 8002
    to_port     = 8002
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
    cidr_blocks = ["${var.auth_service_ip}/32"]
  }

  egress {
    description = "User Service connection"
    from_port   = 8001
    to_port     = 8001
    protocol    = "tcp"
    cidr_blocks = ["${var.user_service_ip}/32"]
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
    Name = "uce-qa-patient-service-sg"
    Service = "Patient"
  }
}

# ============================================================
# APPOINTMENT SERVICE SECURITY GROUP
# ============================================================

resource "aws_security_group" "appointment_service" {
  name        = "uce-qa-appointment-service-sg"
  description = "Security group for Appointment Service"
  vpc_id      = aws_vpc.microservices_1.id

  # Inbound Rules
  ingress {
    description = "HTTP from API Gateway (Account 10)"
    from_port   = 8003
    to_port     = 8003
    protocol    = "tcp"
    cidr_blocks = ["10.10.0.0/16"]
  }

  ingress {
    description = "HTTP from other microservices (Account 7)"
    from_port   = 8003
    to_port     = 8003
    protocol    = "tcp"
    cidr_blocks = ["10.7.0.0/16"]
  }

  ingress {
    description = "HTTP from Account 8 microservices"
    from_port   = 8003
    to_port     = 8003
    protocol    = "tcp"
    cidr_blocks = ["10.8.0.0/16"]
  }

  ingress {
    description = "HTTP from Account 9 microservices"
    from_port   = 8003
    to_port     = 8003
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
    cidr_blocks = ["${var.auth_service_ip}/32"]
  }

  egress {
    description = "User Service connection"
    from_port   = 8001
    to_port     = 8001
    protocol    = "tcp"
    cidr_blocks = ["${var.user_service_ip}/32"]
  }

  egress {
    description = "Patient Service connection"
    from_port   = 8002
    to_port     = 8002
    protocol    = "tcp"
    cidr_blocks = ["${var.patient_service_ip}/32"]
  }

  egress {
    description = "Room Service connection (Account 8 - Future)"
    from_port   = 8004
    to_port     = 8004
    protocol    = "tcp"
    cidr_blocks = ["10.8.11.10/32"]
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
    Name = "uce-qa-appointment-service-sg"
    Service = "Appointment"
  }
}
