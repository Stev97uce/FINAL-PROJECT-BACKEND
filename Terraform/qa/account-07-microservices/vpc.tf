# ============================================================
# VPC CONFIGURATION - CUENTA 7 (MICROSERVICIOS GRUPO 1)
# ============================================================

# VPC
resource "aws_vpc" "microservices_1" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "uce-psychology-qa-microservices-1-vpc"
  }
}

# ============================================================
# PUBLIC SUBNETS
# ============================================================

resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.microservices_1.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "uce-psychology-qa-microservices-1-public-subnet-${count.index + 1}"
    Type = "Public"
  }
}

# ============================================================
# PRIVATE SUBNETS
# ============================================================

resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.microservices_1.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "uce-psychology-qa-microservices-1-private-subnet-${count.index + 1}"
    Type = "Private"
  }
}

# ============================================================
# INTERNET GATEWAY
# ============================================================

resource "aws_internet_gateway" "microservices_1" {
  vpc_id = aws_vpc.microservices_1.id

  tags = {
    Name = "uce-psychology-qa-microservices-1-igw"
  }
}

# ============================================================
# ELASTIC IP FOR NAT GATEWAY
# ============================================================

resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name = "uce-psychology-qa-microservices-1-nat-eip"
  }

  depends_on = [aws_internet_gateway.microservices_1]
}

# ============================================================
# NAT GATEWAY
# ============================================================

resource "aws_nat_gateway" "microservices_1" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  tags = {
    Name = "uce-psychology-qa-microservices-1-nat"
  }

  depends_on = [aws_internet_gateway.microservices_1]
}

# ============================================================
# ROUTE TABLES
# ============================================================

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.microservices_1.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.microservices_1.id
  }

  tags = {
    Name = "uce-psychology-qa-microservices-1-public-rt"
    Type = "Public"
  }
}

# Private Route Table
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.microservices_1.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.microservices_1.id
  }

  tags = {
    Name = "uce-psychology-qa-microservices-1-private-rt"
    Type = "Private"
  }
}

# ============================================================
# ROUTE TABLE ASSOCIATIONS
# ============================================================

# Associate public subnets with public route table
resource "aws_route_table_association" "public" {
  count          = length(var.public_subnet_cidrs)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Associate private subnets with private route table
resource "aws_route_table_association" "private" {
  count          = length(var.private_subnet_cidrs)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}
