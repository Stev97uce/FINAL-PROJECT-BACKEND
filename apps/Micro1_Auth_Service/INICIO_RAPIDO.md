# 🚀 INICIO RÁPIDO - 5 PASOS

## ✅ Pre-requisitos Verificados
- [x] Python 3.11+ ✓
- [x] Entorno virtual creado ✓
- [x] Dependencias instaladas ✓

## 📝 Pasos para Iniciar

### PASO 1: Configurar MySQL

Opción A - Ejecutar script completo:
```powershell
mysql -u root -p < database_setup.sql
```

Opción B - Manualmente:
```sql
CREATE DATABASE auth_service_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### PASO 2: Configurar Credenciales

Editar el archivo `.env` y cambiar el password de MySQL:
```env
DB_PASSWORD=TU_PASSWORD_AQUI
```

### PASO 3: Iniciar el Servidor

```powershell
python run.py
```

¡Listo! El servidor estará en: **http://localhost:8000**

### PASO 4: Verificar que Funciona

Opción A - Navegador:
```
http://localhost:8000/health
http://localhost:8000/docs
```

Opción B - Script de pruebas:
```powershell
python test_api.py
```

### PASO 5: Probar con Postman

1. Abrir Postman
2. Import → File → Seleccionar `UCE_Auth_Service.postman_collection.json`
3. Ejecutar "Health Check"
4. Ejecutar "1. Registrar Usuario Consultante"
5. Ver token en BD y ejecutar "2. Verificar Email"
6. Ejecutar "3. Login"

---

## 🔑 Credenciales Pre-configuradas

**Admin** (ya existe en BD):
- Email: `admin@uce.edu.ec`
- Password: `Admin123`

---

## 🛠️ Comandos Útiles

### Ver tokens de verificación
```powershell
python get_tokens.py verify
```

### Listar usuarios
```powershell
python get_tokens.py users
```

### Detener el servidor
`Ctrl + C` en la terminal

---

## 📚 Documentación Completa

- **README.md** - Visión general del proyecto
- **GUIA_RAPIDA.md** - Guía detallada con ejemplos
- **Swagger UI** - http://localhost:8000/docs (después de iniciar)

---

## ❓ Problemas Comunes

### "Can't connect to MySQL"
→ Verifica que MySQL esté corriendo
→ Verifica el password en `.env`

### "Module not found"
→ Activa el entorno virtual:
```powershell
..\..\.venv\Scripts\Activate.ps1
```

### "Database doesn't exist"
→ Ejecuta `database_setup.sql`

---

## 🎯 Siguiente: Probar con Postman

Una vez que el servidor esté corriendo (PASO 3), importa la colección de Postman y sigue el orden de los requests.

**¡Listo para comenzar!** 🚀
