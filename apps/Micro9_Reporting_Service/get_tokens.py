"""
Generate JWT tokens for Reporting Service testing
"""
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "Q7v1P7Rp-vglhy04pduFZ0LeHW-_z9eBqSPwEV_2Ea4"
ALGORITHM = "HS256"


def generate_token(user_id: int, email: str, rol: str) -> str:
    """Generate JWT token"""
    payload = {
        "user_id": user_id,
        "email": email,
        "rol": rol,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


if __name__ == "__main__":
    print("="  * 80)
    print("REPORTING SERVICE - JWT TOKEN GENERATOR")
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
    
    # Coordinador token
    coord_token = generate_token(
        user_id=2,
        email="coordinador@uce.edu.ec",
        rol="coordinador"
    )
    
    print("\n🔑 COORDINADOR TOKEN (rol: coordinador)")
    print("-" * 80)
    print(coord_token)
    print("-" * 80)
    
    # Psicologo token
    psi_token = generate_token(
        user_id=3,
        email="psicologo@uce.edu.ec",
        rol="psicologo_supervisor"
    )
    
    print("\n🔑 PSICÓLOGO TOKEN (rol: psicologo_supervisor)")
    print("-" * 80)
    print(psi_token)
    print("-" * 80)
    
    # Estudiante token
    est_token = generate_token(
        user_id=4,
        email="estudiante@uce.edu.ec",
        rol="estudiante"
    )
    
    print("\n🔑 ESTUDIANTE TOKEN (rol: estudiante)")
    print("-" * 80)
    print(est_token)
    print("-" * 80)
    
    print("\n✅ Tokens generados exitosamente!")
    print("📝 Usa estos tokens en el header Authorization: Bearer <token>")
    print("⏰ Válidos por 24 horas")
    print("=" * 80)
