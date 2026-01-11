#!/usr/bin/env python
"""
Script para generar tokens JWT de prueba para el Patient Service
"""

from jose import jwt
from datetime import datetime, timedelta
import sys

# Configuración (debe coincidir con JWT_SECRET_KEY del .env)
SECRET_KEY = "your-super-secret-key-change-in-production"
ALGORITHM = "HS256"

# Roles disponibles
ROLES = {
    "1": ("recepcionista", "Recepcionista - Puede crear y gestionar pacientes"),
    "2": ("estudiante", "Estudiante - Puede gestionar expedientes propios"),
    "3": ("psicologo_supervisor", "Psicólogo Supervisor - Puede supervisar todos los expedientes"),
    "4": ("administrador", "Administrador - Acceso total"),
    "5": ("consultante", "Consultante - Solo puede ver su propio perfil")
}

def generate_token(role: str, user_id: int = 1, email: str = None, days: int = 1):
    """Generar token JWT"""
    
    if not email:
        email = f"{role}@uce.edu.ec"
    
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "is_verified": True,
        "exp": datetime.utcnow() + timedelta(days=days)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def main():
    print("\n" + "="*70)
    print("GENERADOR DE TOKENS JWT - Patient Service")
    print("="*70)
    
    print("\nSelecciona un rol:\n")
    for key, (role, description) in ROLES.items():
        print(f"  [{key}] {description}")
    
    print("\n" + "-"*70)
    choice = input("\nIngresa el número del rol [1-5]: ").strip()
    
    if choice not in ROLES:
        print("Opción inválida")
        sys.exit(1)
    
    role, description = ROLES[choice]
    
    # Opciones adicionales
    print("\n" + "-"*70)
    user_id_input = input(f"User ID (default: 1): ").strip()
    user_id = int(user_id_input) if user_id_input else 1
    
    email_input = input(f"Email (default: {role}@uce.edu.ec): ").strip()
    email = email_input if email_input else f"{role}@uce.edu.ec"
    
    days_input = input("Días de validez (default: 1): ").strip()
    days = int(days_input) if days_input else 1
    
    # Generar token
    token = generate_token(role, user_id, email, days)
    
    # Mostrar resultado
    print("\n" + "="*70)
    print("TOKEN GENERADO EXITOSAMENTE")
    print("="*70)
    print(f"\nInformación del Token:")
    print(f"   - Rol: {role}")
    print(f"   - User ID: {user_id}")
    print(f"   - Email: {email}")
    print(f"   - Validez: {days} día(s)")
    print(f"   - Expira: {(datetime.utcnow() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    print(f"\nTu Token JWT:\n")
    print(f"{token}")
    
    print("\n" + "-"*70)
    print("Instrucciones para Postman:")
    print("   1. Abre Postman")
    print("   2. Ve a la colección 'Patient Service API'")
    print("   3. Click en la pestaña 'Variables'")
    print("   4. En la variable 'jwt_token', pega el token de arriba")
    print("   5. Guarda los cambios")
    print("   6. Listo para probar los endpoints")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelado por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
