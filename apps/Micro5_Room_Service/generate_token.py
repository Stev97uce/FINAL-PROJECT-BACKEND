#!/usr/bin/env python3
"""
Script para generar tokens JWT para el Room Service
"""
import jwt
import datetime
import sys

SECRET_KEY = "Q7v1P7Rp-vglhy04pduFZ0LeHW-_z9eBqSPwEV_2Ea4"

def generate_token(role):
    """Genera un token JWT para el rol especificado"""
    
    payload = {
        "user_id": 1,
        "email": f"test_{role}@uce.edu.ec",
        "role": role,
        "is_verified": True,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1),
        "iat": datetime.datetime.now(datetime.UTC),
        "iss": "room-service"
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def main():
    print("=== Room Service - Token Generator ===\n")
    print("Seleccione el rol:")
    print("1. admin")
    print("2. coordinador")
    print("3. recepcionista")
    print("4. profesional")
    print("5. estudiante")
    print("6. consultante")
    
    try:
        option = int(input("\nOpcion: "))
    except ValueError:
        print("Opcion invalida")
        sys.exit(1)
    
    roles = {
        1: "admin",
        2: "coordinador",
        3: "recepcionista",
        4: "profesional",
        5: "estudiante",
        6: "consultante"
    }
    
    if option not in roles:
        print("Opcion invalida")
        sys.exit(1)
    
    role = roles[option]
    token = generate_token(role)
    
    print(f"\n=== TOKEN GENERADO ===\n")
    print(f"Rol: {role}")
    print(f"User ID: 1")
    print(f"Email: test_{role}@uce.edu.ec")
    print(f"Expira: {datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)}\n")
    print("Token:")
    print(token)
    print("\nCopia este token y usalo en Postman:")
    print(f"Authorization: Bearer {token}")

if __name__ == "__main__":
    main()
