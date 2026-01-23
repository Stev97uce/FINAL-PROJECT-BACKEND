# ============================================================
# VPC Y NETWORKING - CUENTA 10 (INFRAESTRUCTURA)
# ============================================================

# VPC Principal
resource "aws_vpc" "infrastructure" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-${var.environment}-infrastructure-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "infrastructure" {
  vpc_id = aws_vpc.infrastructure.id

  tags = {
    Name = "${var.project_name}-${var.environment}-infrastructure-igw"
  }
}

# Subnets Públicas
resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.infrastructure.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-${var.environment}-public-subnet-${count.index + 1}"
    Type = "Public"
  }
}

# Subnets Privadas
resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.infrastructure.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "${var.project_name}-${var.environment}-private-subnet-${count.index + 1}"
    Type = "Private"
  }
}

# Elastic IP para NAT Gateway
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-${var.environment}-nat-eip"
  }

  depends_on = [aws_internet_gateway.infrastructure]
}

# NAT Gateway (para que instancias privadas accedan a internet)
resource "aws_nat_gateway" "infrastructure" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  tags = {
    Name = "${var.project_name}-${var.environment}-nat-gateway"
  }

  depends_on = [aws_internet_gateway.infrastructure]
}

# Route Table para Subnets Públicas
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.infrastructure.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.infrastructure.id
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-public-rt"
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
  vpc_id = aws_vpc.infrastructure.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.infrastructure.id
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-private-rt"
  }
}

# Asociar Route Table con Subnets Privadas
resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}
