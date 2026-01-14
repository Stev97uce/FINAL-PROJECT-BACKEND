"""
Script para generar tokens JWT de prueba
"""
from jose import jwt
from datetime import datetime, timedelta

# Configuración (debe coincidir con Auth Service)
SECRET_KEY = "Q7v1P7Rp-vglhy04pduFZ0LeHW-_z9eBqSPwEV_2Ea4"
ALGORITHM = "HS256"


def generate_token(user_id: int, email: str, rol: str, expires_minutes: int = 1440):
    """Generate JWT token"""
    payload = {
        "user_id": user_id,
        "email": email,
        "rol": rol,
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


if __name__ == "__main__":
    print("=" * 80)
    print("TOKENS JWT PARA TESTING - NOTIFICATION SERVICE")
    print("=" * 80)
    
    # Admin token
    admin_token = generate_token(
        user_id=1,
        email="admin@uce.edu.ec",
        rol="administrador"
    )
    
    print("\n🔑 ADMIN TOKEN (rol: administrador)")
    print("-" * 80)
    print(admin_token)
    print("-" * 80)
    
    # User token (consultante)
    user_token = generate_token(
        user_id=2,
        email="juan.perez@example.com",
        rol="consultante"
    )
    
    print("\n🔑 USER TOKEN (rol: consultante)")
    print("-" * 80)
    print(user_token)
    print("-" * 80)
    
    # Estudiante token
    student_token = generate_token(
        user_id=3,
        email="estudiante@uce.edu.ec",
        rol="estudiante"
    )
    
    print("\n🔑 STUDENT TOKEN (rol: estudiante)")
    print("-" * 80)
    print(student_token)
    print("-" * 80)
    
    # Supervisor token
    supervisor_token = generate_token(
        user_id=4,
        email="supervisor@uce.edu.ec",
        rol="psicologo_supervisor"
    )
    
    print("\n🔑 SUPERVISOR TOKEN (rol: psicologo_supervisor)")
    print("-" * 80)
    print(supervisor_token)
    print("-" * 80)
    
    print("\n✅ Tokens generados exitosamente!")
    print("📝 Usa estos tokens en el header Authorization: Bearer <token>")
    print("⏰ Válidos por 24 horas")
    print("=" * 80)
