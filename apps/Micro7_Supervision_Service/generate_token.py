"""
Token generator for testing Supervision Service
"""
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key-change-in-production-supervision-service-2025"
ALGORITHM = "HS256"


def generate_token(user_id: int, username: str, role: str, email: str):
    """Generate JWT token for testing"""
    payload = {
        "sub": username,
        "user_id": user_id,
        "role": role,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


if __name__ == "__main__":
    # Generate tokens for different roles
    
    # Admin token
    admin_token = generate_token(
        user_id=1,
        username="admin",
        role="admin",
        email="admin@uce.edu.ec"
    )
    print("=" * 80)
    print("ADMIN TOKEN:")
    print(admin_token)
    print("=" * 80)
    
    # Supervisor token
    supervisor_token = generate_token(
        user_id=2,
        username="supervisor_maria",
        role="psicologo_supervisor",
        email="maria.supervisor@uce.edu.ec"
    )
    print("\nSUPERVISOR TOKEN:")
    print(supervisor_token)
    print("=" * 80)
    
    # Student token
    student_token = generate_token(
        user_id=3,
        username="estudiante_juan",
        role="estudiante",
        email="juan.estudiante@uce.edu.ec"
    )
    print("\nSTUDENT TOKEN:")
    print(student_token)
    print("=" * 80)
    
    # Coordinador token
    coordinador_token = generate_token(
        user_id=4,
        username="coordinador",
        role="coordinador",
        email="coordinador@uce.edu.ec"
    )
    print("\nCOORDINADOR TOKEN:")
    print(coordinador_token)
    print("=" * 80)
