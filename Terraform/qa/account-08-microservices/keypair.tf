# ============================================================
# KEY PAIR CONFIGURATION - SHARED KEY
# ============================================================

# Create key pair using shared public key
resource "aws_key_pair" "finalkey" {
  key_name   = var.key_name
  public_key = file("../shared/finalkey.pub")

  tags = {
    Name = "finalkey"
    Usage = "SSH access to all EC2 instances"
  }
}
