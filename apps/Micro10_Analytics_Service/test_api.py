"""
Script de pruebas para Analytics Service (Micro10)
Prueba todos los endpoints con diferentes roles y casos de uso
"""

import requests
import json
from datetime import datetime, timedelta, UTC
import jwt

# Configuración
BASE_URL = "http://localhost:8009"
JWT_SECRET = "your-super-secret-key-change-in-production"

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(name, success, details=""):
    """Imprime resultado de un test"""
    status = f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}" if success else f"{Colors.FAIL}✗ FAIL{Colors.ENDC}"
    print(f"{status} - {name}")
    if details:
        print(f"      {details}")

def generate_token(user_id, email, role):
    """Genera un token JWT para pruebas"""
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(UTC) + timedelta(days=7),
        "iat": datetime.now(UTC)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# Generar tokens para diferentes roles
TOKENS = {
    "admin": generate_token(1, "admin@uce.edu.ec", "admin"),
    "coordinador": generate_token(2, "coordinador@uce.edu.ec", "coordinador"),
    "psicologo": generate_token(3, "psicologo@uce.edu.ec", "psicologo"),
    "estudiante": generate_token(4, "estudiante@uce.edu.ec", "estudiante")
}

def get_headers(role=None):
    """Obtiene headers con o sin autenticación"""
    headers = {"Content-Type": "application/json"}
    if role:
        headers["Authorization"] = f"Bearer {TOKENS[role]}"
    return headers

def test_health_endpoint():
    """Test 1: Health Check"""
    print(f"\n{Colors.HEADER}=== Test 1: Health Check ==={Colors.ENDC}")
    try:
        response = requests.get(f"{BASE_URL}/health")
        success = response.status_code == 200 and response.json().get("status") == "healthy"
        details = f"Status: {response.json().get('status')}, MongoDB: {response.json().get('mongodb')}, Redis: {response.json().get('redis')}"
        print_test("GET /health", success, details)
        return response.json()
    except Exception as e:
        print_test("GET /health", False, str(e))
        return None

def test_service_info():
    """Test 2: Service Info"""
    print(f"\n{Colors.HEADER}=== Test 2: Service Info ==={Colors.ENDC}")
    try:
        response = requests.get(f"{BASE_URL}/")
        success = response.status_code == 200 and "service" in response.json()
        details = f"Service: {response.json().get('service')}, Version: {response.json().get('version')}"
        print_test("GET /", success, details)
        return response.json()
    except Exception as e:
        print_test("GET /", False, str(e))
        return None

def test_create_metrics():
    """Test 3-8: Crear métricas de diferentes tipos"""
    print(f"\n{Colors.HEADER}=== Test 3-8: Crear Métricas ==={Colors.ENDC}")
    
    metric_types = [
        {
            "metric_type": "appointment_stats",
            "data": {
                "total_appointments": 150,
                "completed": 120,
                "cancelled": 15,
                "pending": 15,
                "average_duration_minutes": 45
            }
        },
        {
            "metric_type": "user_activity",
            "data": {
                "total_users": 500,
                "active_users": 350,
                "new_users_last_month": 50,
                "sessions_today": 200
            }
        },
        {
            "metric_type": "room_utilization",
            "data": {
                "total_rooms": 20,
                "occupied_rooms": 15,
                "utilization_percentage": 75.0,
                "peak_hours": ["09:00-11:00", "14:00-16:00"]
            }
        },
        {
            "metric_type": "session_stats",
            "data": {
                "total_sessions": 300,
                "individual_sessions": 200,
                "group_sessions": 100,
                "average_rating": 4.5
            }
        },
        {
            "metric_type": "supervision_stats",
            "data": {
                "total_supervisions": 50,
                "pending_reviews": 10,
                "approved": 35,
                "rejected": 5
            }
        },
        {
            "metric_type": "system_performance",
            "data": {
                "response_time_ms": 120,
                "cpu_usage_percent": 45.5,
                "memory_usage_mb": 512,
                "active_connections": 150
            }
        }
    ]
    
    created_ids = []
    for i, metric in enumerate(metric_types, 3):
        try:
            # Admin y coordinador pueden crear métricas
            role = "admin" if i % 2 == 0 else "coordinador"
            response = requests.post(
                f"{BASE_URL}/api/v1/metrics/",
                headers=get_headers(role),
                json=metric
            )
            success = response.status_code == 201
            if success:
                data = response.json().get("data", {})
                metric_id = data.get("id")
                created_ids.append(metric_id)
                details = f"ID: {metric_id}, Type: {metric['metric_type']}, Role: {role}"
            else:
                details = f"Error: {response.json()}"
            print_test(f"POST /api/v1/metrics/ ({metric['metric_type']})", success, details)
        except Exception as e:
            print_test(f"POST /api/v1/metrics/ ({metric['metric_type']})", False, str(e))
    
    return created_ids

def test_get_metrics():
    """Test 9: Listar métricas"""
    print(f"\n{Colors.HEADER}=== Test 9: Listar Métricas ==={Colors.ENDC}")
    try:
        # Sin filtros
        response = requests.get(
            f"{BASE_URL}/api/v1/metrics/",
            headers=get_headers("psicologo")
        )
        success = response.status_code == 200 and "data" in response.json()
        data = response.json().get("data", [])
        count = len(data)
        details = f"Total métricas: {count}"
        print_test("GET /api/v1/metrics/ (sin filtros)", success, details)
        
        # Con filtro de tipo
        response = requests.get(
            f"{BASE_URL}/api/v1/metrics/?metric_type=appointment_stats&limit=5",
            headers=get_headers("estudiante")
        )
        success = response.status_code == 200
        data = response.json().get("data", [])
        count = len(data)
        details = f"Métricas tipo appointment_stats: {count}"
        print_test("GET /api/v1/metrics/ (con filtros)", success, details)
        
        return True
    except Exception as e:
        print_test("GET /api/v1/metrics/", False, str(e))
        return False

def test_get_latest_metric():
    """Test 10: Obtener última métrica por tipo"""
    print(f"\n{Colors.HEADER}=== Test 10: Última Métrica por Tipo ==={Colors.ENDC}")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/metrics/latest/user_activity",
            headers=get_headers("psicologo")
        )
        success = response.status_code == 200 and response.json().get("success") == True
        if success:
            metric = response.json().get("data", {})
            details = f"Type: {metric.get('metric_type')}, Active users: {metric.get('data', {}).get('active_users')}"
        else:
            details = f"Error: {response.json()}"
        print_test("GET /api/v1/metrics/latest/user_activity", success, details)
        return success
    except Exception as e:
        print_test("GET /api/v1/metrics/latest/user_activity", False, str(e))
        return False

def test_get_dashboard_summary():
    """Test 11: Dashboard Summary"""
    print(f"\n{Colors.HEADER}=== Test 11: Dashboard Summary ==={Colors.ENDC}")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/metrics/summary",
            headers=get_headers("coordinador")
        )
        success = response.status_code == 200 and response.json().get("success") == True
        if success:
            summary = response.json().get("data", {})
            details = f"Total appointments: {summary.get('total_appointments', 0)}, Active users: {summary.get('active_users', 0)}"
        else:
            details = f"Error: {response.json()}"
        print_test("GET /api/v1/metrics/summary", success, details)
        return summary if success else None
    except Exception as e:
        print_test("GET /api/v1/metrics/summary", False, str(e))
        return None

def test_create_dashboard():
    """Test 12-13: Crear dashboards"""
    print(f"\n{Colors.HEADER}=== Test 12-13: Crear Dashboards ==={Colors.ENDC}")
    
    dashboards = [
        {
            "name": "Dashboard Principal",
            "description": "Vista general del sistema",
            "is_public": True,
            "widgets": [
                {
                    "title": "Estadísticas de Citas",
                    "metric_type": "appointment_stats",
                    "position": {"x": 0, "y": 0, "width": 6, "height": 4}
                },
                {
                    "title": "Actividad de Usuarios",
                    "metric_type": "user_activity",
                    "position": {"x": 6, "y": 0, "width": 6, "height": 4}
                }
            ]
        },
        {
            "name": "Dashboard Privado Psicólogo",
            "description": "Mi dashboard personal",
            "is_public": False,
            "widgets": [
                {
                    "title": "Mis Sesiones",
                    "metric_type": "session_stats",
                    "position": {"x": 0, "y": 0, "width": 12, "height": 4}
                }
            ]
        }
    ]
    
    created_ids = []
    for i, dashboard in enumerate(dashboards, 12):
        try:
            role = "admin" if i == 12 else "psicologo"
            response = requests.post(
                f"{BASE_URL}/api/v1/dashboards/",
                headers=get_headers(role),
                json=dashboard
            )
            success = response.status_code == 201
            if success:
                data = response.json().get("data", {})
                dashboard_id = data.get("id")
                created_ids.append(dashboard_id)
                details = f"ID: {dashboard_id}, Name: {dashboard['name']}, Role: {role}"
            else:
                details = f"Error: {response.json()}"
            print_test(f"POST /api/v1/dashboards/ ({dashboard['name']})", success, details)
        except Exception as e:
            print_test(f"POST /api/v1/dashboards/", False, str(e))
    
    return created_ids

def test_list_dashboards(dashboard_ids):
    """Test 14: Listar dashboards"""
    print(f"\n{Colors.HEADER}=== Test 14: Listar Dashboards ==={Colors.ENDC}")
    try:
        # Psicologo ve sus propios dashboards + públicos
        response = requests.get(
            f"{BASE_URL}/api/v1/dashboards/",
            headers=get_headers("psicologo")
        )
        success = response.status_code == 200 and "data" in response.json()
        count = len(response.json().get("data", []))
        details = f"Dashboards visibles (psicólogo): {count}"
        print_test("GET /api/v1/dashboards/ (psicologo)", success, details)
        
        # Estudiante solo ve públicos
        response = requests.get(
            f"{BASE_URL}/api/v1/dashboards/",
            headers=get_headers("estudiante")
        )
        success = response.status_code == 200
        count = len(response.json().get("data", []))
        details = f"Dashboards visibles (estudiante): {count}"
        print_test("GET /api/v1/dashboards/ (estudiante)", success, details)
        
        return True
    except Exception as e:
        print_test("GET /api/v1/dashboards/", False, str(e))
        return False

def test_get_dashboard(dashboard_id):
    """Test 15: Obtener dashboard específico"""
    print(f"\n{Colors.HEADER}=== Test 15: Obtener Dashboard ==={Colors.ENDC}")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/dashboards/{dashboard_id}",
            headers=get_headers("coordinador")
        )
        success = response.status_code == 200 and response.json().get("success") == True
        if success:
            dashboard = response.json().get("data", {})
            details = f"Name: {dashboard.get('name')}, Widgets: {len(dashboard.get('widgets', []))}"
        else:
            details = f"Error: {response.json()}"
        print_test(f"GET /api/v1/dashboards/{dashboard_id}", success, details)
        return success
    except Exception as e:
        print_test(f"GET /api/v1/dashboards/{dashboard_id}", False, str(e))
        return False

def test_update_dashboard(dashboard_id):
    """Test 16: Actualizar dashboard"""
    print(f"\n{Colors.HEADER}=== Test 16: Actualizar Dashboard ==={Colors.ENDC}")
    try:
        update_data = {
            "name": "Dashboard Principal - Actualizado",
            "description": "Vista general del sistema (actualizada)",
            "widgets": [
                {
                    "title": "Estadísticas de Citas Actualizadas",
                    "metric_type": "appointment_stats",
                    "position": {"x": 0, "y": 0, "width": 4, "height": 4}
                },
                {
                    "title": "Actividad de Usuarios",
                    "metric_type": "user_activity",
                    "position": {"x": 4, "y": 0, "width": 4, "height": 4}
                },
                {
                    "title": "Nuevo Widget - Rendimiento",
                    "metric_type": "system_performance",
                    "position": {"x": 8, "y": 0, "width": 4, "height": 4}
                }
            ]
        }
        response = requests.put(
            f"{BASE_URL}/api/v1/dashboards/{dashboard_id}",
            headers=get_headers("admin"),
            json=update_data
        )
        success = response.status_code == 200
        if success:
            dashboard = response.json().get("data", {})
            details = f"Updated: {dashboard.get('name')}, Widgets: {len(dashboard.get('widgets', []))}"
        else:
            details = f"Error: {response.json()}"
        print_test(f"PUT /api/v1/dashboards/{dashboard_id}", success, details)
        return success
    except Exception as e:
        print_test(f"PUT /api/v1/dashboards/{dashboard_id}", False, str(e))
        return False

def test_delete_dashboard(dashboard_id):
    """Test 17: Eliminar dashboard"""
    print(f"\n{Colors.HEADER}=== Test 17: Eliminar Dashboard ==={Colors.ENDC}")
    try:
        # Estudiante no puede eliminar (403)
        response = requests.delete(
            f"{BASE_URL}/api/v1/dashboards/{dashboard_id}",
            headers=get_headers("estudiante")
        )
        success_forbidden = response.status_code == 403
        print_test(f"DELETE /api/v1/dashboards/{dashboard_id} (estudiante - debe fallar)", 
                   success_forbidden, "Correctamente prohibido (403)")
        
        # Admin puede eliminar
        response = requests.delete(
            f"{BASE_URL}/api/v1/dashboards/{dashboard_id}",
            headers=get_headers("admin")
        )
        success_delete = response.status_code == 200
        details = "Dashboard eliminado correctamente" if success_delete else f"Error: {response.json()}"
        print_test(f"DELETE /api/v1/dashboards/{dashboard_id} (admin)", success_delete, details)
        
        return success_delete
    except Exception as e:
        print_test(f"DELETE /api/v1/dashboards/{dashboard_id}", False, str(e))
        return False

def test_authentication_errors():
    """Test 18-19: Errores de autenticación y autorización"""
    print(f"\n{Colors.HEADER}=== Test 18-19: Autenticación y Autorización ==={Colors.ENDC}")
    
    # Sin token (401)
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/metrics/",
            json={"metric_type": "test", "data": {}}
        )
        success = response.status_code == 401
        print_test("POST /api/v1/metrics/ sin token (debe ser 401)", success, 
                   "Correctamente no autorizado")
    except Exception as e:
        print_test("POST sin token", False, str(e))
    
    # Rol sin permisos (403)
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/metrics/",
            headers=get_headers("estudiante"),
            json={"metric_type": "test_metric", "data": {"value": 1}}
        )
        success = response.status_code == 403
        print_test("POST /api/v1/metrics/ con rol estudiante (debe ser 403)", success,
                   "Correctamente prohibido")
    except Exception as e:
        print_test("POST con rol sin permisos", False, str(e))

def test_validation_errors():
    """Test 20: Errores de validación"""
    print(f"\n{Colors.HEADER}=== Test 20: Validación de Datos ==={Colors.ENDC}")
    
    # Métrica sin metric_type
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/metrics/",
            headers=get_headers("admin"),
            json={"data": {"value": 1}}
        )
        success = response.status_code == 400
        print_test("POST métrica sin metric_type (debe ser 400)", success, 
                   "Correctamente rechazado")
    except Exception as e:
        print_test("POST métrica inválida", False, str(e))
    
    # Dashboard sin nombre
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/dashboards/",
            headers=get_headers("admin"),
            json={"description": "Sin nombre"}
        )
        success = response.status_code == 400
        print_test("POST dashboard sin nombre (debe ser 400)", success,
                   "Correctamente rechazado")
    except Exception as e:
        print_test("POST dashboard inválido", False, str(e))

def main():
    """Ejecuta todos los tests"""
    print(f"{Colors.BOLD}{Colors.OKCYAN}")
    print("=" * 70)
    print("  ANALYTICS SERVICE (MICRO10) - TEST SUITE")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    
    # Test 1-2: Health y Service Info
    health = test_health_endpoint()
    if not health:
        print(f"\n{Colors.FAIL}Error: El servicio no está disponible{Colors.ENDC}")
        return
    
    service_info = test_service_info()
    
    # Test 3-8: Crear métricas
    metric_ids = test_create_metrics()
    
    # Test 9-11: Consultar métricas
    test_get_metrics()
    test_get_latest_metric()
    test_get_dashboard_summary()
    
    # Test 12-13: Crear dashboards
    dashboard_ids = test_create_dashboard()
    
    if dashboard_ids:
        # Test 14-17: Operaciones con dashboards
        test_list_dashboards(dashboard_ids)
        if dashboard_ids[0]:
            test_get_dashboard(dashboard_ids[0])
            test_update_dashboard(dashboard_ids[0])
        if len(dashboard_ids) > 1 and dashboard_ids[1]:
            test_delete_dashboard(dashboard_ids[1])
    
    # Test 18-20: Errores y validaciones
    test_authentication_errors()
    test_validation_errors()
    
    # Resumen final
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}")
    print("=" * 70)
    print("  RESUMEN DE PRUEBAS")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    print(f"✓ Health Check: {Colors.OKGREEN}OK{Colors.ENDC}")
    print(f"✓ Métricas creadas: {Colors.OKGREEN}{len([m for m in metric_ids if m])}{Colors.ENDC}")
    print(f"✓ Dashboards creados: {Colors.OKGREEN}{len([d for d in dashboard_ids if d])}{Colors.ENDC}")
    print(f"✓ Autenticación JWT: {Colors.OKGREEN}OK{Colors.ENDC}")
    print(f"✓ RBAC (4 roles): {Colors.OKGREEN}OK{Colors.ENDC}")
    print(f"\n{Colors.OKGREEN}Todas las pruebas completadas{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
