"""
Script de prueba para el User Service
Ejecutar: python test_user_service.py
"""

import requests
import json

BASE_URL = "http://localhost:8001"
AUTH_URL = "http://localhost:8000"

def print_response(title, response):
    """Print formatted response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def main():
    print("\nUCE USER SERVICE - TEST SCRIPT")
    print("="*60)
    
    # 1. Login to get token
    print("\n1. LOGIN (usando auth-service)")
    login_data = {
        "email": "juan.perez@test.com",
        "password": "Test123456"
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/api/auth/login", json=login_data)
        print_response("LOGIN RESPONSE", response)
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # 2. Get current profile (should not exist yet)
            print("\n2. GET PROFILE (no debería existir)")
            response = requests.get(f"{BASE_URL}/api/users/profile", headers=headers)
            print_response("GET PROFILE RESPONSE", response)
            
            # 3. Create profile
            print("\n3. CREATE PROFILE")
            profile_data = {
                "direccion": "Av. 10 de Agosto N37-123",
                "ciudad": "Quito",
                "pais": "Ecuador",
                "fecha_nacimiento": "1990-05-15",
                "genero": "masculino",
                "telefono_alternativo": "+593987654321",
                "contacto_emergencia_nombre": "María García",
                "contacto_emergencia_telefono": "+593912345678",
                "ocupacion": "Estudiante",
                "institucion": "Universidad Central del Ecuador",
                "notas_medicas": "Ninguna",
                "preferencias": {
                    "notificaciones_email": True,
                    "notificaciones_sms": False,
                    "idioma": "es"
                }
            }
            
            response = requests.post(f"{BASE_URL}/api/users/profile", json=profile_data, headers=headers)
            print_response("CREATE PROFILE RESPONSE", response)
            
            # 4. Get profile again
            print("\n4. GET PROFILE (ahora debería existir)")
            response = requests.get(f"{BASE_URL}/api/users/profile", headers=headers)
            print_response("GET PROFILE RESPONSE", response)
            
            # 5. Update profile
            print("\n5. UPDATE PROFILE")
            update_data = {
                "ciudad": "Guayaquil",
                "ocupacion": "Profesional en Psicología"
            }
            
            response = requests.put(f"{BASE_URL}/api/users/profile", json=update_data, headers=headers)
            print_response("UPDATE PROFILE RESPONSE", response)
            
            # 6. Get activity logs
            print("\n6. GET ACTIVITY LOGS")
            response = requests.get(f"{BASE_URL}/api/users/activity?limit=10", headers=headers)
            print_response("ACTIVITY LOGS RESPONSE", response)
            
            # 7. Create manual activity log
            print("\n7. CREATE ACTIVITY LOG")
            activity_data = {
                "accion": "prueba_api",
                "descripcion": "Prueba de endpoints del user-service"
            }
            
            response = requests.post(f"{BASE_URL}/api/users/activity", json=activity_data, headers=headers)
            print_response("CREATE ACTIVITY LOG RESPONSE", response)
            
            # 8. Health check
            print("\n8. HEALTH CHECK")
            response = requests.get(f"{BASE_URL}/health")
            print_response("HEALTH CHECK RESPONSE", response)
            
            print("\n" + "="*60)
            print("PRUEBAS COMPLETADAS EXITOSAMENTE")
            print("="*60)
            
        else:
            print("\nERROR: No se pudo obtener el token de autenticación")
            print("Asegúrate de que el usuario juan.perez@test.com exista y esté verificado")
            
    except requests.exceptions.ConnectionError:
        print("\nERROR: No se pudo conectar a los servicios")
        print("Asegúrate de que auth-service y user-service estén corriendo")
    except Exception as e:
        print(f"\nERROR: {str(e)}")

if __name__ == "__main__":
    main()
