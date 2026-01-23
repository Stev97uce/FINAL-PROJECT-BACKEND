# ============================================================
# VPC PEERING - CUENTA 10 (INFRAESTRUCTURA)
# ============================================================
# Conecta la VPC de Infraestructura con las demás cuentas
# para permitir comunicación directa entre servicios
# ============================================================

# ===== PEERING: CUENTA 10 → CUENTA 1 (DATABASES) =====

resource "aws_vpc_peering_connection" "infra_to_databases" {
  count = var.enable_vpc_peering && var.account_01_id != "" && var.account_01_vpc_id != "" ? 1 : 0

  vpc_id        = aws_vpc.infrastructure.id
  peer_vpc_id   = var.account_01_vpc_id
  peer_owner_id = var.account_01_id
  peer_region   = var.aws_region
  auto_accept   = false  # Siempre false para cross-account peering

  tags = {
    Name = "${var.project_name}-${var.environment}-infra-to-db-peering"
    Side = "Requester"
    PeerAccount = "Account-01-Databases"
  }
}

# Rutas en Cuenta 10 hacia Cuenta 1
resource "aws_route" "infra_to_databases_public" {
  count = var.enable_vpc_peering && var.account_01_id != "" && var.account_01_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.public.id
  destination_cidr_block    = var.account_01_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.infra_to_databases[0].id
}

resource "aws_route" "infra_to_databases_private" {
  count = var.enable_vpc_peering && var.account_01_id != "" && var.account_01_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.private.id
  destination_cidr_block    = var.account_01_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.infra_to_databases[0].id
}

# ===== PEERING: CUENTA 10 → CUENTA 7 (MICROSERVICES 1) =====
# NOTA: El peering fue creado desde Account 7, por lo que Account 10 es el accepter
# Usamos data source para referenciar el peering existente en lugar de crear uno nuevo

data "aws_vpc_peering_connection" "infra_to_microservices_1" {
  count = var.enable_vpc_peering && var.account_07_id != "" && var.account_07_vpc_id != "" ? 1 : 0

  filter {
    name   = "accepter-vpc-info.vpc-id"
    values = [aws_vpc.infrastructure.id]
  }
  
  filter {
    name   = "requester-vpc-info.vpc-id"
    values = [var.account_07_vpc_id]
  }
  
  filter {
    name   = "status-code"
    values = ["active"]
  }
  
  # El peering existente tiene ID: pcx-04dfa90992df6390b
  # Si hay múltiples, usar el más reciente
}

# Rutas en Cuenta 10 hacia Cuenta 7
resource "aws_route" "infra_to_microservices_1_public" {
  count = var.enable_vpc_peering && var.account_07_id != "" && var.account_07_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.public.id
  destination_cidr_block    = var.account_07_cidr
  vpc_peering_connection_id = data.aws_vpc_peering_connection.infra_to_microservices_1[0].id
}

resource "aws_route" "infra_to_microservices_1_private" {
  count = var.enable_vpc_peering && var.account_07_id != "" && var.account_07_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.private.id
  destination_cidr_block    = var.account_07_cidr
  vpc_peering_connection_id = data.aws_vpc_peering_connection.infra_to_microservices_1[0].id
}

# ===== PEERING: CUENTA 10 → CUENTA 8 (MICROSERVICES 2) =====
# NOTA: El peering fue creado desde Account 8, por lo que Account 10 es el accepter
# Usamos data source para referenciar el peering existente en lugar de crear uno nuevo

data "aws_vpc_peering_connection" "infra_to_microservices_2" {
  count = var.enable_vpc_peering && var.account_08_id != "" && var.account_08_vpc_id != "" ? 1 : 0

  filter {
    name   = "accepter-vpc-info.vpc-id"
    values = [aws_vpc.infrastructure.id]
  }
  
  filter {
    name   = "requester-vpc-info.vpc-id"
    values = [var.account_08_vpc_id]
  }
  
  filter {
    name   = "status-code"
    values = ["active"]
  }
}

# Rutas en Cuenta 10 hacia Cuenta 8
resource "aws_route" "infra_to_microservices_2_public" {
  count = var.enable_vpc_peering && var.account_08_id != "" && var.account_08_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.public.id
  destination_cidr_block    = var.account_08_cidr
  vpc_peering_connection_id = data.aws_vpc_peering_connection.infra_to_microservices_2[0].id
}

resource "aws_route" "infra_to_microservices_2_private" {
  count = var.enable_vpc_peering && var.account_08_id != "" && var.account_08_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.private.id
  destination_cidr_block    = var.account_08_cidr
  vpc_peering_connection_id = data.aws_vpc_peering_connection.infra_to_microservices_2[0].id
}

# ===== PEERING: CUENTA 10 → CUENTA 9 (MICROSERVICES 3 + MONITORING) =====

resource "aws_vpc_peering_connection" "infra_to_microservices_3" {
  count = var.enable_vpc_peering && var.account_09_id != "" && var.account_09_vpc_id != "" ? 1 : 0

  vpc_id        = aws_vpc.infrastructure.id
  peer_vpc_id   = var.account_09_vpc_id
  peer_owner_id = var.account_09_id
  peer_region   = var.aws_region
  auto_accept   = false

  tags = {
    Name = "${var.project_name}-${var.environment}-infra-to-micro3-peering"
    Side = "Requester"
    PeerAccount = "Account-09-Microservices-3-Monitoring"
  }
}

# Rutas en Cuenta 10 hacia Cuenta 9
resource "aws_route" "infra_to_microservices_3_public" {
  count = var.enable_vpc_peering && var.account_09_id != "" && var.account_09_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.public.id
  destination_cidr_block    = var.account_09_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.infra_to_microservices_3[0].id
}

resource "aws_route" "infra_to_microservices_3_private" {
  count = var.enable_vpc_peering && var.account_09_id != "" && var.account_09_vpc_id != "" ? 1 : 0

  route_table_id            = aws_route_table.private.id
  destination_cidr_block    = var.account_09_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.infra_to_microservices_3[0].id
}

# ===== OUTPUTS =====

output "vpc_peering_connections" {
  value = {
    infra_to_databases = var.enable_vpc_peering && var.account_01_id != "" && var.account_01_vpc_id != "" ? {
      id     = aws_vpc_peering_connection.infra_to_databases[0].id
      status = aws_vpc_peering_connection.infra_to_databases[0].accept_status
    } : null
    
    infra_to_microservices_1 = var.enable_vpc_peering && var.account_07_id != "" && var.account_07_vpc_id != "" ? {
      id     = data.aws_vpc_peering_connection.infra_to_microservices_1[0].id
      status = data.aws_vpc_peering_connection.infra_to_microservices_1[0].status
    } : null
    
    infra_to_microservices_2 = var.enable_vpc_peering && var.account_08_id != "" && var.account_08_vpc_id != "" ? {
      id     = data.aws_vpc_peering_connection.infra_to_microservices_2[0].id
      status = data.aws_vpc_peering_connection.infra_to_microservices_2[0].status
    } : null
    
    infra_to_microservices_3 = var.enable_vpc_peering && var.account_09_id != "" && var.account_09_vpc_id != "" ? {
      id     = aws_vpc_peering_connection.infra_to_microservices_3[0].id
      status = aws_vpc_peering_connection.infra_to_microservices_3[0].accept_status
    } : null
  }
  description = "IDs y estados de las conexiones VPC Peering"
}

# ===== NOTAS IMPORTANTES =====
# 
# 1. ACEPTAR PEERING:
#    Si auto_accept = false, debes aceptar el peering manualmente en cada cuenta:
#    
#    aws ec2 accept-vpc-peering-connection \
#      --vpc-peering-connection-id <PEERING_ID> \
#      --region us-east-1
#
# 2. CONFIGURAR RUTAS EN OTRAS CUENTAS:
#    Cada cuenta destino necesita agregar rutas de vuelta hacia 10.10.0.0/16
#
# 3. SECURITY GROUPS:
#    Ya están configurados para permitir tráfico desde todas las VPCs
#
# 4. ORDEN DE DEPLOYMENT:
#    - Primero: Deploy Cuenta 10 (crea peering requests)
#    - Segundo: Aceptar peerings en cada cuenta (manual o con Terraform)
#    - Tercero: Agregar rutas en las otras cuentas
#
