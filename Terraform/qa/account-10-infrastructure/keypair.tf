# ============================================================
# KEY PAIR - finalkey (PARA TODAS LAS CUENTAS)
# ============================================================

# Generar par de claves SSH
resource "tls_private_key" "finalkey" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Crear Key Pair en AWS
resource "aws_key_pair" "finalkey" {
  key_name   = var.key_name
  public_key = tls_private_key.finalkey.public_key_openssh

  tags = {
    Name = "${var.project_name}-${var.environment}-finalkey"
  }
}

# Guardar clave privada localmente
resource "local_file" "private_key" {
  content         = tls_private_key.finalkey.private_key_pem
  filename        = "${path.module}/../shared/${var.key_name}.pem"
  file_permission = "0400"
}

# Guardar clave pública localmente
resource "local_file" "public_key" {
  content         = tls_private_key.finalkey.public_key_openssh
  filename        = "${path.module}/../shared/${var.key_name}.pub"
  file_permission = "0644"
}
