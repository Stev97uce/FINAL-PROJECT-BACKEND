# 🚀 Guía Rápida de Inicio - Auth Service

## Paso 1: Configurar MySQL

### Opción A: Usando MySQL Workbench o Terminal
```sql
-- Ejecutar el archivo database_setup.sql
mysql -u root -p < database_setup.sql
```

### Opción B: Manualmente
```sql
CREATE DATABASE auth_service_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

⚠️ **Importante**: El script SQL incluye un usuario administrador inicial:
- **Email**: admin@uce.edu.ec
- **Password**: Admin123
- **Rol**: administrador

## Paso 2: Configurar Variables de Entorno

El archivo `.env` ya está configurado con valores por defecto. Ajusta si es necesario:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=TU_PASSWORD_AQUI
DB_NAME=auth_service_db
```

## Paso 3: Iniciar el Servidor

```powershell
cd BACKEND
python run.py
```

O con el entorno virtual explícito:
```powershell
"C:/Users/Stev/Desktop/Stev/U/Noveno/Distribuida 2.0/Proyecto Final/Micro1_Auth/.venv/Scripts/python.exe" run.py
```

🎉 El servidor estará disponible en: **http://localhost:8000**

## Paso 4: Verificar que Funciona

### Usando el navegador:
- **Docs Interactiva**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Usando Postman:
1. Importar el archivo `UCE_Auth_Service.postman_collection.json`
2. Ejecutar "Health Check" para verificar
3. Ejecutar "1. Registrar Usuario Consultante"

## 📋 Flujo de Pruebas con Postman

### Prueba 1: Registro de Consultante (Auto-registro)
```
POST /api/auth/register
Body:
{
  "nombres": "Juan Pérez",
  "identificacion": "1234567890",
  "email": "juan@example.com",
  "telefono": "0999999999",
  "password": "Password123",
  "rol": "consultante"
}
```

### Prueba 2: Verificar Email
```
1. Conectar a MySQL y obtener el token:
   SELECT token FROM verification_tokens WHERE tipo = 'email_verification' ORDER BY id DESC LIMIT 1;

2. Usar el token en Postman:
   GET /api/auth/verify-email/{TOKEN}
```

### Prueba 3: Login
```
POST /api/auth/login
Body:
{
  "email": "juan@example.com",
  "password": "Password123"
}

Respuesta incluye: access_token, refresh_token
```

### Prueba 4: Validar Token
```
GET /api/auth/validate
Headers:
Authorization: Bearer {access_token}
```

### Prueba 5: Registrar Usuario con Rol Especial
```
1. Primero hacer login como admin:
   POST /api/auth/login
   Body: {"email": "admin@uce.edu.ec", "password": "Admin123"}

2. Usar el access_token para registrar:
   POST /api/auth/register
   Headers: Authorization: Bearer {admin_access_token}
   Body:
   {
     "nombres": "María García",
     "identificacion": "0987654321",
     "email": "maria@uce.edu.ec",
     "telefono": "0988888888",
     "password": "Password123",
     "rol": "recepcionista"
   }
```

## 🔍 Consultas SQL Útiles

### Ver todos los usuarios
```sql
SELECT id, nombres, email, rol, estado, email_verificado 
FROM users;
```

### Ver tokens de verificación pendientes
```sql
SELECT vt.token, u.email, vt.tipo, vt.expira_en, vt.usado
FROM verification_tokens vt
JOIN users u ON vt.user_id = u.id
WHERE vt.usado = FALSE
ORDER BY vt.created_at DESC;
```

### Ver refresh tokens activos
```sql
SELECT rt.token, u.email, rt.expira_en, rt.revocado
FROM refresh_tokens rt
JOIN users u ON rt.user_id = u.id
WHERE rt.revocado = FALSE
ORDER BY rt.created_at DESC;
```

## ❌ Problemas Comunes

### Error: "Can't connect to MySQL server"
- Verifica que MySQL esté corriendo
- Verifica usuario y password en `.env`

### Error: "Database doesn't exist"
- Ejecuta el script `database_setup.sql`

### Error: "Module not found"
- Instala dependencias: `pip install -r requirements.txt`

### Error: Email ya registrado
- Usa un email diferente o elimina el usuario de la BD

## 📊 Endpoints Disponibles

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | No |
| POST | `/api/auth/register` | Registro | No* |
| GET | `/api/auth/verify-email/{token}` | Verificar email | No |
| POST | `/api/auth/login` | Login | No |
| POST | `/api/auth/forgot-password` | Recuperar contraseña | No |
| POST | `/api/auth/reset-password` | Restablecer contraseña | No |
| POST | `/api/auth/refresh` | Renovar token | No |
| POST | `/api/auth/logout` | Logout | Sí |
| GET | `/api/auth/validate` | Validar token | Sí |

*Roles especiales requieren auth de admin

## 🎯 Próximos Pasos

1. ✅ Probar todos los endpoints con Postman
2. ✅ Verificar eventos en RabbitMQ (opcional)
3. ✅ Revisar logs del servidor
4. 🔜 Desarrollar el frontend (cuando tú digas)

## 💡 Tips

- Los tokens de verificación expiran en 24h
- Los tokens de recuperación expiran en 1h
- El access_token expira en 24h
- El refresh_token expira en 7 días
- Las contraseñas deben tener: 8+ caracteres, mayúsculas, minúsculas y números
