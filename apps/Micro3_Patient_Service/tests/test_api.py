import os
import sys
from datetime import date, datetime

# Configurar variables de entorno ANTES de importar la app
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_USER", "postgres")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_NAME", "test_patient_db")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("RABBITMQ_HOST", "localhost")
os.environ.setdefault("RABBITMQ_PORT", "5672")
os.environ.setdefault("RABBITMQ_USER", "guest")
os.environ.setdefault("RABBITMQ_PASSWORD", "guest")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing")
os.environ.setdefault("AUTH_SERVICE_URL", "http://localhost:8000")
os.environ.setdefault("USER_SERVICE_URL", "http://localhost:8001")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jose import jwt
from unittest.mock import MagicMock, patch

# Mock de RabbitMQ antes de importar app
mock_rabbitmq = MagicMock()
mock_rabbitmq.connect = MagicMock()
mock_rabbitmq.close = MagicMock()
mock_rabbitmq.publish_event = MagicMock()

# Importar después de configurar variables de entorno
with patch('app.events.rabbitmq_publisher', mock_rabbitmq):
    from app.main import app
    from app.database import Base, get_db
    from app.config import settings

# Base de datos en memoria para tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_patient.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override de la dependencia de base de datos
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Cliente de prueba
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Crear y limpiar base de datos para cada test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def create_test_token(user_id: int = 1, role: str = "recepcionista", email: str = "test@test.com"):
    """Crear token JWT de prueba"""
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "is_verified": True
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def test_health_check():
    """Test del endpoint de health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Patient Service"

def test_root_endpoint():
    """Test del endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data

def test_create_patient():
    """Test de creación de paciente"""
    token = create_test_token(role="recepcionista")
    headers = {"Authorization": f"Bearer {token}"}
    
    patient_data = {
        "user_id": 100,
        "nombres": "Juan Carlos",
        "apellidos": "Pérez García",
        "cedula": "1234567890",
        "fecha_nacimiento": "1990-05-15",
        "genero": "Masculino",
        "estado_civil": "Soltero/a",
        "telefono": "0987654321",
        "direccion": "Calle Falsa 123",
        "ciudad": "Quito",
        "provincia": "Pichincha",
        "motivo_consulta_inicial": "Ansiedad generalizada"
    }
    
    response = client.post("/api/v1/patients/", json=patient_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nombres"] == "Juan Carlos"
    assert data["cedula"] == "1234567890"
    assert "id" in data

def test_create_patient_duplicate_cedula():
    """Test de validación: no se puede crear paciente con cédula duplicada"""
    token = create_test_token(role="recepcionista")
    headers = {"Authorization": f"Bearer {token}"}
    
    patient_data = {
        "user_id": 101,
        "nombres": "María",
        "apellidos": "López",
        "cedula": "1234567890",
        "fecha_nacimiento": "1985-03-20",
        "genero": "Femenino",
        "estado_civil": "Casado/a",
        "telefono": "0987654322",
        "direccion": "Av. Principal 456",
        "ciudad": "Guayaquil",
        "provincia": "Guayas",
        "motivo_consulta_inicial": "Depresión"
    }
    
    # Crear primer paciente
    client.post("/api/v1/patients/", json=patient_data, headers=headers)
    
    # Intentar crear segundo paciente con misma cédula
    patient_data["user_id"] = 102
    response = client.post("/api/v1/patients/", json=patient_data, headers=headers)
    assert response.status_code == 400
    assert "Ya existe un paciente" in response.json()["detail"]

def test_list_patients():
    """Test de listado de pacientes"""
    token = create_test_token(role="recepcionista")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear algunos pacientes
    for i in range(3):
        patient_data = {
            "user_id": 200 + i,
            "nombres": f"Paciente{i}",
            "apellidos": f"Test{i}",
            "cedula": f"123456789{i}",
            "fecha_nacimiento": "1990-01-01",
            "genero": "Masculino",
            "estado_civil": "Soltero/a",
            "telefono": f"098765432{i}",
            "direccion": "Dirección test",
            "ciudad": "Quito",
            "provincia": "Pichincha",
            "motivo_consulta_inicial": "Motivo test"
        }
        client.post("/api/v1/patients/", json=patient_data, headers=headers)
    
    # Listar pacientes
    response = client.get("/api/v1/patients/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

def test_get_patient_by_id():
    """Test de obtención de paciente por ID"""
    token = create_test_token(role="estudiante")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear paciente
    patient_data = {
        "user_id": 300,
        "nombres": "Pedro",
        "apellidos": "Ramírez",
        "cedula": "9876543210",
        "fecha_nacimiento": "1995-07-10",
        "genero": "Masculino",
        "estado_civil": "Soltero/a",
        "telefono": "0912345678",
        "direccion": "Calle Test 789",
        "ciudad": "Cuenca",
        "provincia": "Azuay",
        "motivo_consulta_inicial": "Estrés laboral"
    }
    
    create_token = create_test_token(role="recepcionista")
    create_headers = {"Authorization": f"Bearer {create_token}"}
    create_response = client.post("/api/v1/patients/", json=patient_data, headers=create_headers)
    patient_id = create_response.json()["id"]
    
    # Obtener paciente
    response = client.get(f"/api/v1/patients/{patient_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == patient_id
    assert data["nombres"] == "Pedro"

def test_create_expediente():
    """Test de creación de expediente"""
    token = create_test_token(role="estudiante")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear paciente primero
    patient_data = {
        "user_id": 400,
        "nombres": "Ana",
        "apellidos": "Martínez",
        "cedula": "1111111111",
        "fecha_nacimiento": "1992-12-25",
        "genero": "Femenino",
        "estado_civil": "Soltero/a",
        "telefono": "0923456789",
        "direccion": "Av. Test 111",
        "ciudad": "Quito",
        "provincia": "Pichincha",
        "motivo_consulta_inicial": "Problemas de autoestima"
    }
    
    create_token = create_test_token(role="recepcionista")
    create_headers = {"Authorization": f"Bearer {create_token}"}
    patient_response = client.post("/api/v1/patients/", json=patient_data, headers=create_headers)
    patient_id = patient_response.json()["id"]
    
    # Crear expediente
    expediente_data = {
        "patient_id": patient_id,
        "psicologo_asignado_id": 1,
        "supervisor_asignado_id": 2,
        "diagnostico_inicial": "Trastorno de ansiedad generalizada",
        "plan_tratamiento": "Terapia cognitivo-conductual"
    }
    
    response = client.post("/api/v1/expedientes/", json=expediente_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["patient_id"] == patient_id
    assert "codigo_expediente" in data
    assert data["codigo_expediente"].startswith("EXP-")

def test_unauthorized_access():
    """Test de acceso sin token"""
    response = client.get("/api/v1/patients/")
    assert response.status_code == 401  # HTTPBearer retorna 401 sin credenciales

def test_invalid_role():
    """Test de acceso con rol inválido"""
    # Intentar crear paciente con rol 'consultante' (no permitido)
    token = create_test_token(role="consultante")
    headers = {"Authorization": f"Bearer {token}"}
    
    patient_data = {
        "user_id": 500,
        "nombres": "Test",
        "apellidos": "Invalid",
        "cedula": "2222222222",
        "fecha_nacimiento": "1990-01-01",
        "genero": "Masculino",
        "estado_civil": "Soltero/a",
        "telefono": "0900000000",
        "direccion": "Test",
        "ciudad": "Quito",
        "provincia": "Pichincha",
        "motivo_consulta_inicial": "Test"
    }
    
    response = client.post("/api/v1/patients/", json=patient_data, headers=headers)
    assert response.status_code == 403
    assert "Permiso denegado" in response.json()["detail"]
