# ============================================================
# VPC PEERING - CUENTA 1 (DATABASES) ←→ CUENTA 10 (INFRASTRUCTURE)
# ============================================================

# ============================================================
# VPC PEERING - PROCESO EN 2 FASES
# ============================================================
# FASE 1: Desplegar Cuenta 1 SIN VPC Peering (enable_vpc_peering = false)
# FASE 2: Actualizar Cuenta 10 con VPC ID de Cuenta 1
# FASE 3: Re-aplicar Cuenta 1 CON VPC Peering (enable_vpc_peering = true)
# ============================================================

# Buscar el peering request de Cuenta 10
data "aws_vpc_peering_connection" "from_infrastructure" {
  count = var.enable_vpc_peering && var.account_10_vpc_id != "" ? 1 : 0

  filter {
    name   = "requester-vpc-info.owner-id"
    values = [var.account_10_id]
  }
  filter {
    name   = "requester-vpc-info.vpc-id"
    values = [var.account_10_vpc_id]
  }
  filter {
    name   = "accepter-vpc-info.vpc-id"
    values = [aws_vpc.databases.id]
  }
  filter {
    name   = "status-code"
    values = ["pending-acceptance", "active"]
  }
}

# Aceptar el peering
resource "aws_vpc_peering_connection_accepter" "from_infrastructure" {
  count = var.enable_vpc_peering && var.account_10_vpc_id != "" ? 1 : 0

  vpc_peering_connection_id = data.aws_vpc_peering_connection.from_infrastructure[0].id
  auto_accept               = true

  tags = {
    Name = "${var.project_name}-${var.environment}-db-to-infra-peering-accepter"
    Side = "Accepter"
  }
}

# Ruta hacia Cuenta 10 (Infrastructure) desde subnet pública
resource "aws_route" "to_infrastructure_public" {
  count = var.enable_vpc_peering && var.account_10_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.public.id
  destination_cidr_block    = var.account_10_cidr
  vpc_peering_connection_id = data.aws_vpc_peering_connection.from_infrastructure[0].id

  depends_on = [aws_vpc_peering_connection_accepter.from_infrastructure]
}

# Ruta hacia Cuenta 10 (Infrastructure) desde subnet privada
resource "aws_route" "to_infrastructure_private" {
  count = var.enable_vpc_peering && var.account_10_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.private.id
  destination_cidr_block    = var.account_10_cidr
  vpc_peering_connection_id = data.aws_vpc_peering_connection.from_infrastructure[0].id

  depends_on = [aws_vpc_peering_connection_accepter.from_infrastructure]
}

# ============================================================
# VPC PEERING - CUENTA 1 (DATABASES) ←→ CUENTA 7 (MICROSERVICES 1)
# ============================================================

# Buscar el peering request de Cuenta 7
data "aws_vpc_peering_connection" "from_microservices_1" {
  count = var.enable_vpc_peering && var.account_07_id != "" && var.account_07_vpc_id != "" ? 1 : 0

  filter {
    name   = "requester-vpc-info.owner-id"
    values = [var.account_07_id]
  }
  filter {
    name   = "requester-vpc-info.vpc-id"
    values = [var.account_07_vpc_id]
  }
  filter {
    name   = "accepter-vpc-info.vpc-id"
    values = [aws_vpc.databases.id]
  }
  filter {
    name   = "status-code"
    values = ["pending-acceptance", "active"]
  }
}

# Aceptar el peering desde Cuenta 7
resource "aws_vpc_peering_connection_accepter" "from_microservices_1" {
  count = var.enable_vpc_peering && var.account_07_id != "" && var.account_07_vpc_id != "" ? 1 : 0

  vpc_peering_connection_id = data.aws_vpc_peering_connection.from_microservices_1[0].id
  auto_accept               = true

  tags = {
    Name = "${var.project_name}-${var.environment}-db-to-micro1-peering-accepter"
    Side = "Accepter"
  }
}

# Ruta hacia Cuenta 7 (Microservices 1) desde subnet pública
resource "aws_route" "to_microservices_1_public" {
  count = var.enable_vpc_peering && var.account_07_id != "" && var.account_07_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.public.id
  destination_cidr_block    = var.account_07_cidr
  vpc_peering_connection_id = data.aws_vpc_peering_connection.from_microservices_1[0].id

  depends_on = [aws_vpc_peering_connection_accepter.from_microservices_1]
}

# Ruta hacia Cuenta 7 (Microservices 1) desde subnet privada
resource "aws_route" "to_microservices_1_private" {
  count = var.enable_vpc_peering && var.account_07_id != "" && var.account_07_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.private.id
  destination_cidr_block    = var.account_07_cidr
  vpc_peering_connection_id = data.aws_vpc_peering_connection.from_microservices_1[0].id

  depends_on = [aws_vpc_peering_connection_accepter.from_microservices_1]
}

# ============================================================
# VPC PEERING - CUENTA 1 (DATABASES) ←→ CUENTA 8 (MICROSERVICES 2)
# ============================================================

# Buscar el peering request de Cuenta 8
data "aws_vpc_peering_connection" "from_microservices_2" {
  count = var.enable_vpc_peering && var.account_08_id != "" && var.account_08_vpc_id != "" ? 1 : 0

  filter {
    name   = "requester-vpc-info.owner-id"
    values = [var.account_08_id]
  }
  filter {
    name   = "requester-vpc-info.vpc-id"
    values = [var.account_08_vpc_id]
  }
  filter {
    name   = "accepter-vpc-info.vpc-id"
    values = [aws_vpc.databases.id]
  }
  filter {
    name   = "status-code"
    values = ["pending-acceptance", "active"]
  }
}

# Aceptar el peering desde Cuenta 8
resource "aws_vpc_peering_connection_accepter" "from_microservices_2" {
  count = var.enable_vpc_peering && var.account_08_id != "" && var.account_08_vpc_id != "" ? 1 : 0

  vpc_peering_connection_id = data.aws_vpc_peering_connection.from_microservices_2[0].id
  auto_accept               = true

  tags = {
    Name = "${var.project_name}-${var.environment}-db-to-micro2-peering-accepter"
    Side = "Accepter"
  }
}

# Ruta hacia Cuenta 8 (Microservices 2) desde subnet pública
resource "aws_route" "to_microservices_2_public" {
  count = var.enable_vpc_peering && var.account_08_id != "" && var.account_08_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.public.id
  destination_cidr_block    = var.account_08_cidr
  vpc_peering_connection_id = data.aws_vpc_peering_connection.from_microservices_2[0].id

  depends_on = [aws_vpc_peering_connection_accepter.from_microservices_2]
}

# Ruta hacia Cuenta 8 (Microservices 2) desde subnet privada
resource "aws_route" "to_microservices_2_private" {
  count = var.enable_vpc_peering && var.account_08_id != "" && var.account_08_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.private.id
  destination_cidr_block    = var.account_08_cidr
  vpc_peering_connection_id = data.aws_vpc_peering_connection.from_microservices_2[0].id

  depends_on = [aws_vpc_peering_connection_accepter.from_microservices_2]
}

# ===== OUTPUTS =====

output "vpc_peering_connection_id" {
  value       = var.enable_vpc_peering && var.account_10_vpc_id != "" && length(data.aws_vpc_peering_connection.from_infrastructure) > 0 ? data.aws_vpc_peering_connection.from_infrastructure[0].id : null
  description = "ID de la conexión VPC Peering con Account 10"
}

output "vpc_peering_status" {
  value       = var.enable_vpc_peering && var.account_10_vpc_id != "" && length(data.aws_vpc_peering_connection.from_infrastructure) > 0 ? data.aws_vpc_peering_connection.from_infrastructure[0].status : "disabled"
  description = "Estado del VPC Peering con Account 10"
}

output "vpc_peering_connection_id_microservices_1" {
  value       = var.enable_vpc_peering && var.account_07_id != "" && var.account_07_vpc_id != "" && length(data.aws_vpc_peering_connection.from_microservices_1) > 0 ? data.aws_vpc_peering_connection.from_microservices_1[0].id : null
  description = "ID de la conexión VPC Peering con Account 7"
}

output "vpc_peering_status_microservices_1" {
  value       = var.enable_vpc_peering && var.account_07_id != "" && var.account_07_vpc_id != "" && length(data.aws_vpc_peering_connection.from_microservices_1) > 0 ? data.aws_vpc_peering_connection.from_microservices_1[0].status : "disabled"
  description = "Estado del VPC Peering con Account 7"
}
