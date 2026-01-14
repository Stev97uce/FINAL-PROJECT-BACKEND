#!/usr/bin/env python3
"""
Script to generate JWT tokens for testing Analytics Service
"""

import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-super-secret-key-change-in-production"

def generate_token(user_id: int, email: str, role: str, days: int = 7) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=days),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

if __name__ == "__main__":
    print("=" * 80)
    print("JWT TOKENS FOR ANALYTICS SERVICE TESTING")
    print("=" * 80)
    print()
    
    users = [
        {"user_id": 1, "email": "admin@uce.edu.ec", "role": "admin"},
        {"user_id": 2, "email": "coordinador@uce.edu.ec", "role": "coordinador"},
        {"user_id": 3, "email": "psicologo@uce.edu.ec", "role": "psicologo"},
        {"user_id": 4, "email": "estudiante@uce.edu.ec", "role": "estudiante"},
    ]
    
    for user in users:
        token = generate_token(user["user_id"], user["email"], user["role"])
        print(f"Role: {user['role']}")
        print(f"Email: {user['email']}")
        print(f"Token: {token}")
        print()
        print("-" * 80)
        print()
