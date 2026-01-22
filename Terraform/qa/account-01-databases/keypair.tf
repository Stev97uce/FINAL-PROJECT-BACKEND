# ============================================================
# KEY PAIR - finalkey (COMPARTIDO DESDE CUENTA 10)
# ============================================================

# Usar la key pair existente (ya creada en Cuenta 10 o manualmente)
# No la gestionamos con Terraform en esta cuenta, solo la referenciamos
data "aws_key_pair" "finalkey" {
  key_name = var.key_name
}

output "key_pair_name" {
  value       = data.aws_key_pair.finalkey.key_name
  description = "Nombre del key pair"
}
