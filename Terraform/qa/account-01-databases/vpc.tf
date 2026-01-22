# ============================================================
# VPC Y NETWORKING - CUENTA 1 (DATABASES)
# ============================================================

# VPC Principal
resource "aws_vpc" "databases" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-${var.environment}-databases-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "databases" {
  vpc_id = aws_vpc.databases.id

  tags = {
    Name = "${var.project_name}-${var.environment}-databases-igw"
  }
}

# Subnets Públicas (para Bastion si es necesario)
resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.databases.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-${var.environment}-db-public-subnet-${count.index + 1}"
    Type = "Public"
  }
}

# Subnets Privadas (donde estarán las bases de datos)
resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.databases.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "${var.project_name}-${var.environment}-db-private-subnet-${count.index + 1}"
    Type = "Private"
  }
}

# Elastic IP para NAT Gateway
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-${var.environment}-db-nat-eip"
  }

  depends_on = [aws_internet_gateway.databases]
}

# NAT Gateway (para que las DBs puedan descargar updates)
resource "aws_nat_gateway" "databases" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  tags = {
    Name = "${var.project_name}-${var.environment}-db-nat-gateway"
  }

  depends_on = [aws_internet_gateway.databases]
}

# Route Table para Subnets Públicas
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.databases.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.databases.id
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-db-public-rt"
  }
}

# Asociar Route Table con Subnets Públicas
resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Route Table para Subnets Privadas
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.databases.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.databases.id
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-db-private-rt"
  }
}

# Asociar Route Table con Subnets Privadas
resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# ===== OUTPUTS =====

output "vpc_id" {
  value       = aws_vpc.databases.id
  description = "ID de la VPC de Databases"
}

output "vpc_cidr" {
  value       = aws_vpc.databases.cidr_block
  description = "CIDR block de la VPC"
}

output "private_subnet_ids" {
  value       = aws_subnet.private[*].id
  description = "IDs de las subnets privadas"
}

output "public_subnet_ids" {
  value       = aws_subnet.public[*].id
  description = "IDs de las subnets públicas"
}
