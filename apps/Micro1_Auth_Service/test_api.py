"""
Script de pruebas básicas para verificar que el Auth Service está funcionando correctamente
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_result(success, message):
    icon = "✓" if success else "✗"
    print(f"{icon} {message}")

def test_health_check():
    """Test 1: Health Check"""
    print_header("TEST 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Health Check OK: {data}")
            return True
        else:
            print_result(False, f"Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Error conectando al servidor: {e}")
        return False

def test_register_consultante():
    """Test 2: Registrar Consultante"""
    print_header("TEST 2: Registrar Usuario Consultante")
    
    # Generar email único con timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    email = f"test{timestamp}@example.com"
    
    data = {
        "nombres": "Usuario Test",
        "identificacion": f"TEST{timestamp}",
        "email": email,
        "telefono": "0999999999",
        "password": "Password123",
        "rol": "consultante"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            result = response.json()
            print_result(True, f"Usuario registrado: ID {result['user_id']}")
            print(f"   Email: {email}")
            print(f"   Mensaje: {result['message']}")
            return email, result['user_id']
        else:
            print_result(False, f"Error {response.status_code}: {response.text}")
            return None, None
    except Exception as e:
        print_result(False, f"Error: {e}")
        return None, None

def test_login_admin():
    """Test 3: Login como Administrador"""
    print_header("TEST 3: Login como Administrador")
    
    data = {
        "email": "admin@uce.edu.ec",
        "password": "Admin123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result(True, "Login exitoso")
            print(f"   Usuario: {result['user']['nombres']}")
            print(f"   Rol: {result['user']['rol']}")
            print(f"   Access Token: {result['access_token'][:50]}...")
            return result['access_token'], result['refresh_token']
        else:
            print_result(False, f"Error {response.status_code}: {response.text}")
            return None, None
    except Exception as e:
        print_result(False, f"Error: {e}")
        return None, None

def test_validate_token(access_token):
    """Test 4: Validar Token"""
    print_header("TEST 4: Validar Token")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/validate",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result(True, "Token válido")
            print(f"   User ID: {result['user_id']}")
            print(f"   Email: {result['email']}")
            print(f"   Rol: {result['rol']}")
            return True
        else:
            print_result(False, f"Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False

def test_forgot_password(email):
    """Test 5: Solicitar Recuperación de Contraseña"""
    print_header("TEST 5: Solicitar Recuperación de Contraseña")
    
    data = {"email": email}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result(True, result['message'])
            return True
        else:
            print_result(False, f"Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False

def test_refresh_token(refresh_token):
    """Test 6: Renovar Access Token"""
    print_header("TEST 6: Renovar Access Token")
    
    data = {"refresh_token": refresh_token}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/refresh",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result(True, "Token renovado exitosamente")
            print(f"   Nuevo Access Token: {result['access_token'][:50]}...")
            return True
        else:
            print_result(False, f"Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False

def run_all_tests():
    """Ejecutar todas las pruebas"""
    print("\n" + "="*70)
    print("  🧪 PRUEBAS AUTOMÁTICAS - AUTH SERVICE")
    print("="*70)
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_health_check()))
    
    # Test 2: Registrar Consultante
    email, user_id = test_register_consultante()
    results.append(("Registrar Consultante", email is not None))
    
    # Test 3: Login Admin
    access_token, refresh_token = test_login_admin()
    results.append(("Login Admin", access_token is not None))
    
    if access_token:
        # Test 4: Validar Token
        results.append(("Validar Token", test_validate_token(access_token)))
        
        # Test 6: Renovar Token
        if refresh_token:
            results.append(("Renovar Token", test_refresh_token(refresh_token)))
    
    # Test 5: Forgot Password (usando email de admin)
    results.append(("Recuperar Contraseña", test_forgot_password("admin@uce.edu.ec")))
    
    # Resumen
    print_header("RESUMEN DE PRUEBAS")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        print_result(result, test_name)
    
    print(f"\n{'='*70}")
    print(f"  RESULTADO: {passed}/{total} pruebas pasadas")
    
    if passed == total:
        print("  🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        print("  ⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    run_all_tests()
