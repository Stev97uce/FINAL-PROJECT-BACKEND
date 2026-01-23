# ============================================================
# SECURITY GROUPS - CUENTA 1 (DATABASES)
# ============================================================

# ===== SECURITY GROUP PARA MYSQL =====
resource "aws_security_group" "mysql" {
  name        = "${var.project_name}-${var.environment}-mysql-sg"
  description = "Security group para MySQL Database"
  vpc_id      = aws_vpc.databases.id

  # MySQL desde Cuenta 10 (Infrastructure)
  ingress {
    description = "MySQL from Account 10"
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [var.account_10_cidr]
  }

  # MySQL desde Cuenta 7 (Auth Service)
  ingress {
    description = "MySQL from Account 7 (Auth Service)"
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [var.account_07_cidr]
  }

  # MySQL desde VPC local
  ingress {
    description = "MySQL from local VPC"
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  # SSH desde Bastion (para administración)
  ingress {
    description = "SSH from Bastion"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${var.bastion_ip}/32", var.account_10_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-mysql-sg"
  }
}

# ===== SECURITY GROUP PARA POSTGRESQL =====
resource "aws_security_group" "postgresql" {
  name        = "${var.project_name}-${var.environment}-postgresql-sg"
  description = "Security group para PostgreSQL Database"
  vpc_id      = aws_vpc.databases.id

  # PostgreSQL desde Cuenta 10
  ingress {
    description = "PostgreSQL from Account 10"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.account_10_cidr]
  }

  # PostgreSQL desde Cuenta 7 (User, Patient, Appointment)
  ingress {
    description = "PostgreSQL from Account 7"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.account_07_cidr]
  }

  # PostgreSQL desde Cuenta 8 (Room, Supervision)
  ingress {
    description = "PostgreSQL from Account 8"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.account_08_cidr]
  }

  # PostgreSQL desde Cuenta 9 (Reporting)
  ingress {
    description = "PostgreSQL from Account 9"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.account_09_cidr]
  }

  # PostgreSQL desde VPC local
  ingress {
    description = "PostgreSQL from local VPC"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  # SSH desde Bastion
  ingress {
    description = "SSH from Bastion"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${var.bastion_ip}/32", var.account_10_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-postgresql-sg"
  }
}

# ===== SECURITY GROUP PARA MONGODB =====
resource "aws_security_group" "mongodb" {
  name        = "${var.project_name}-${var.environment}-mongodb-sg"
  description = "Security group para MongoDB Database"
  vpc_id      = aws_vpc.databases.id

  # MongoDB desde Cuenta 10
  ingress {
    description = "MongoDB from Account 10"
    from_port   = 27017
    to_port     = 27017
    protocol    = "tcp"
    cidr_blocks = [var.account_10_cidr]
  }

  # MongoDB desde Cuenta 8 (Clinical, Notification)
  ingress {
    description = "MongoDB from Account 8"
    from_port   = 27017
    to_port     = 27017
    protocol    = "tcp"
    cidr_blocks = [var.account_08_cidr]
  }

  # MongoDB desde Cuenta 9 (Analytics)
  ingress {
    description = "MongoDB from Account 9"
    from_port   = 27017
    to_port     = 27017
    protocol    = "tcp"
    cidr_blocks = [var.account_09_cidr]
  }

  # MongoDB desde VPC local
  ingress {
    description = "MongoDB from local VPC"
    from_port   = 27017
    to_port     = 27017
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  # SSH desde Bastion
  ingress {
    description = "SSH from Bastion"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${var.bastion_ip}/32", var.account_10_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-mongodb-sg"
  }
}

# ===== SECURITY GROUP PARA REDIS =====
resource "aws_security_group" "redis" {
  name        = "${var.project_name}-${var.environment}-redis-sg"
  description = "Security group para Redis Cache"
  vpc_id      = aws_vpc.databases.id

  # Redis desde Cuenta 10
  ingress {
    description = "Redis from Account 10"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.account_10_cidr]
  }

  # Redis desde Cuenta 7
  ingress {
    description = "Redis from Account 7"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.account_07_cidr]
  }

  # Redis desde Cuenta 8
  ingress {
    description = "Redis from Account 8"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.account_08_cidr]
  }

  # Redis desde Cuenta 9
  ingress {
    description = "Redis from Account 9"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.account_09_cidr]
  }

  # Redis desde VPC local
  ingress {
    description = "Redis from local VPC"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  # SSH desde Bastion
  ingress {
    description = "SSH from Bastion"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${var.bastion_ip}/32", var.account_10_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-redis-sg"
  }
}
