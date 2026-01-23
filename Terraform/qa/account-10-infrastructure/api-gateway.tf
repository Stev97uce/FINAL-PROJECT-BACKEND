# ============================================================
# API GATEWAYS (QA Y PROD)
# ============================================================

# ===== API GATEWAY QA =====

# Elastic IP para API Gateway QA
resource "aws_eip" "api_gateway_qa" {
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-${var.environment}-api-gateway-qa-eip"
  }

  depends_on = [aws_internet_gateway.infrastructure]
}

# Asociar Elastic IP al API Gateway QA
resource "aws_eip_association" "api_gateway_qa" {
  instance_id   = aws_instance.api_gateway_qa.id
  allocation_id = aws_eip.api_gateway_qa.id
}

# Instancia EC2 API Gateway QA
resource "aws_instance" "api_gateway_qa" {
  ami           = var.ami_ubuntu_docker
  instance_type = var.instance_type_api_gateway
  key_name      = aws_key_pair.finalkey.key_name

  subnet_id                   = aws_subnet.public[0].id
  private_ip                  = "10.10.1.30"  # IP fija según plan de IPs
  vpc_security_group_ids      = [aws_security_group.api_gateway_qa.id]
  associate_public_ip_address = true

  user_data = base64encode(file("${path.module}/user-data/api-gateway-qa.sh"))

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "${var.project_name}-${var.environment}-api-gateway-qa-root"
    }
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-api-gateway-qa"
    Role        = "API-Gateway-QA"
    Environment = "QA"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# ===== OUTPUTS =====

output "api_gateway_qa_public_ip" {
  value       = aws_eip.api_gateway_qa.public_ip
  description = "IP pública del API Gateway QA"
}

output "api_gateway_qa_url" {
  value       = "http://${aws_eip.api_gateway_qa.public_ip}"
  description = "URL del API Gateway QA"
}
