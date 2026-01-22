# ============================================================
# VPC PEERING CONNECTIONS - CUENTA 8
# ============================================================

# ============================================================
# PEERING TO ACCOUNT 10 (INFRASTRUCTURE)
# ============================================================

resource "aws_vpc_peering_connection" "to_infrastructure" {
  count = var.enable_vpc_peering && var.account_10_vpc_id != "" ? 1 : 0

  vpc_id        = aws_vpc.microservices_2.id
  peer_vpc_id   = var.account_10_vpc_id
  peer_owner_id = var.account_10_id
  peer_region   = var.aws_region
  auto_accept   = false

  tags = {
    Name        = "uce-psychology-qa-micro2-to-infra-peering"
    Side        = "Requester"
    PeerAccount = "Account-10-Infrastructure"
  }
}

# ============================================================
# PEERING TO ACCOUNT 01 (DATABASES)
# ============================================================

resource "aws_vpc_peering_connection" "to_databases" {
  count = var.enable_vpc_peering && var.account_01_vpc_id != "" ? 1 : 0

  vpc_id        = aws_vpc.microservices_2.id
  peer_vpc_id   = var.account_01_vpc_id
  peer_owner_id = var.account_01_id
  peer_region   = var.aws_region
  auto_accept   = false

  tags = {
    Name        = "uce-psychology-qa-micro2-to-db-peering"
    Side        = "Requester"
    PeerAccount = "Account-01-Databases"
  }
}

# ============================================================
# ROUTES TO ACCOUNT 10 (INFRASTRUCTURE)
# ============================================================

# Route from Private Subnet to Account 10
resource "aws_route" "to_infrastructure_private" {
  count = var.enable_vpc_peering && var.account_10_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.private.id
  destination_cidr_block    = "10.10.0.0/16"
  vpc_peering_connection_id = aws_vpc_peering_connection.to_infrastructure[0].id
}

# Route from Public Subnet to Account 10
resource "aws_route" "to_infrastructure_public" {
  count = var.enable_vpc_peering && var.account_10_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.public.id
  destination_cidr_block    = "10.10.0.0/16"
  vpc_peering_connection_id = aws_vpc_peering_connection.to_infrastructure[0].id
}

# ============================================================
# ROUTES TO ACCOUNT 01 (DATABASES)
# ============================================================

# Route from Private Subnet to Account 01
resource "aws_route" "to_databases_private" {
  count = var.enable_vpc_peering && var.account_01_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.private.id
  destination_cidr_block    = "10.1.0.0/16"
  vpc_peering_connection_id = aws_vpc_peering_connection.to_databases[0].id
}

# Route from Public Subnet to Account 01
resource "aws_route" "to_databases_public" {
  count = var.enable_vpc_peering && var.account_01_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.public.id
  destination_cidr_block    = "10.1.0.0/16"
  vpc_peering_connection_id = aws_vpc_peering_connection.to_databases[0].id
}
