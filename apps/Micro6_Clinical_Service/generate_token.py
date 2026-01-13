from app.security import create_access_token
from datetime import timedelta

# Token configuration
user_data = {
    "sub": "1",  # User ID
    "email": "admin@uce.edu.ec",
    "role": "admin"
}

# Generate token (expires in 30 minutes by default)
token = create_access_token(user_data, expires_delta=timedelta(days=7))

print("\n" + "="*80)
print("JWT TOKEN GENERATED FOR CLINICAL SERVICE")
print("="*80)
print(f"\nUser: {user_data['email']}")
print(f"Role: {user_data['role']}")
print(f"User ID: {user_data['sub']}")
print(f"\nToken (expires in 7 days):")
print("-"*80)
print(token)
print("-"*80)
print("\nUse this token in Postman:")
print("Authorization: Bearer <token>")
print("="*80 + "\n")
