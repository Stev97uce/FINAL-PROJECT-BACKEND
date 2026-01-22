# Solución de Problemas en Microservicios - Account 7

## Resumen

Este documento describe los problemas encontrados y las soluciones aplicadas para los microservicios en Account 7, específicamente relacionados con la codificación de contraseñas en las URLs de conexión a bases de datos.

---

## Problema Identificado

### Síntoma
Los microservicios fallaban al intentar conectarse a las bases de datos (MySQL y PostgreSQL) con errores como:
- `could not translate host name "#@10.1.11.10" to address`
- `Can't connect to MySQL server on '#@10.1.11.10' (timed out)`

### Causa Raíz
Las contraseñas de las bases de datos contienen caracteres especiales (por ejemplo: `Admin123!@#`). Cuando estas contraseñas se insertan directamente en las URLs de conexión sin codificación URL, los caracteres especiales (`!`, `@`, `#`) son interpretados incorrectamente:
- `@` se interpreta como separador de usuario/contraseña
- `#` se interpreta como inicio de fragmento URL
- `!` puede causar problemas en algunos parsers

### Ejemplo del Problema
```python
# ❌ INCORRECTO - Sin codificación
DATABASE_URL = f"mysql+pymysql://admin:Admin123!@#@10.1.11.10:3306/db"
# El parser interpreta: usuario="admin", password="Admin123", host="@#@10.1.11.10"
```

---

## Soluciones Aplicadas

### 1. Auth Service (Python - MySQL)

**Archivo:** `apps/Micro1_Auth_Service/app/config.py`

**Problema:** La contraseña `Admin123!@#` no estaba codificada en la URL de conexión a MySQL.

**Solución:**
```python
from urllib.parse import quote_plus

@property
def DATABASE_URL(self) -> str:
    encoded_password = urllib.parse.quote_plus(self.DB_PASSWORD)
    return f"mysql+pymysql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
```

**Cambios:**
- Importar `urllib.parse.quote_plus`
- Codificar la contraseña antes de construir la URL
- La contraseña `Admin123!@#` se convierte en `Admin123%21%40%23`

---

### 2. User Service (Python - PostgreSQL)

**Archivo:** `apps/Micro2_User_Service/app/config.py`

**Problema:** Similar al Auth Service, pero para PostgreSQL.

**Solución:**
```python
from urllib.parse import quote_plus

@property
def DATABASE_URL(self) -> str:
    # URL-encode password and user to handle special characters
    encoded_password = quote_plus(self.DB_PASSWORD)
    encoded_user = quote_plus(self.DB_USER)
    return f"postgresql://{encoded_user}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
```

**Cambios:**
- Importar `quote_plus` de `urllib.parse`
- Codificar tanto usuario como contraseña (por si el usuario también tiene caracteres especiales)
- También se corrigió `REDIS_URL` para manejar contraseñas de Redis si las hay

---

### 3. Patient Service (Python - PostgreSQL)

**Archivo:** `apps/Micro3_Patient_Service/app/database.py`

**Problema:** Similar a User Service.

**Solución:**
```python
from urllib.parse import quote_plus

# URL-encode password and user to handle special characters
encoded_password = quote_plus(settings.DB_PASSWORD)
encoded_user = quote_plus(settings.DB_USER)
DATABASE_URL = f"postgresql+psycopg://{encoded_user}:{encoded_password}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
```

**Cambios:**
- Aplicar codificación URL directamente en la construcción de `DATABASE_URL`
- Codificar usuario y contraseña

---

### 4. Appointment Service (Go - PostgreSQL)

**Archivo:** `apps/Micro4_Appointment_Service/pkg/config/config.go`

**Problema:** Appointment Service está escrito en Go y usa un formato DSN diferente (`host=... password=...`), pero también necesita codificar la contraseña.

**Solución Requerida:**
```go
import (
    "net/url"
)

func (c *Config) GetDSN() string {
    // URL-encode password and user to handle special characters
    encodedPassword := url.QueryEscape(c.DBPassword)
    encodedUser := url.QueryEscape(c.DBUser)
    
    return fmt.Sprintf(
        "host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
        c.DBHost, c.DBPort, encodedUser, encodedPassword, c.DBName, c.DBSSLMode,
    )
}
```

**Solución Aplicada:**
```go
import (
    "net/url"
    // ... otros imports
)

func (c *Config) GetDSN() string {
    // URL-encode password and user to handle special characters
    encodedPassword := url.QueryEscape(c.DBPassword)
    encodedUser := url.QueryEscape(c.DBUser)
    
    return fmt.Sprintf(
        "host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
        c.DBHost, c.DBPort, encodedUser, encodedPassword, c.DBName, c.DBSSLMode,
    )
}

func (c *Config) GetRabbitMQURL() string {
    // URL-encode RabbitMQ credentials to handle special characters
    encodedUser := url.QueryEscape(c.RabbitMQUser)
    encodedPassword := url.QueryEscape(c.RabbitMQPassword)
    
    return fmt.Sprintf(
        "amqp://%s:%s@%s:%s%s",
        encodedUser, encodedPassword, c.RabbitMQHost, c.RabbitMQPort, c.RabbitMQVHost,
    )
}
```

**Cambios:**
- Importar `net/url`
- Usar `url.QueryEscape()` para codificar usuario y contraseña en `GetDSN()`
- También codificar credenciales de RabbitMQ en `GetRabbitMQURL()` (prevención)

**Proceso de Despliegue:**
1. ✅ Código modificado en `apps/Micro4_Appointment_Service/pkg/config/config.go`
2. ⏳ Reconstruir la imagen Docker:
   ```bash
   cd apps/Micro4_Appointment_Service
   docker build -t stevxd97/uce-appointment-service:latest .
   docker push stevxd97/uce-appointment-service:latest
   ```
3. ⏳ Reiniciar el servicio en Account 7:
   ```bash
   ssh -J ubuntu@<bastion> ubuntu@10.7.11.12
   cd /opt/appointment-service
   sudo docker compose pull
   sudo docker compose up -d --force-recreate appointment-service
   ```

---

## Proceso de Verificación

### 1. Verificar que los servicios están corriendo
```bash
# Desde el Bastion
curl http://10.7.11.10:8000/health  # Auth Service
curl http://10.7.11.11:8001/health  # User Service
curl http://10.7.11.12:8003/health  # Appointment Service
```

### 2. Verificar logs de conexión a base de datos
```bash
# Auth Service
ssh -J ubuntu@<bastion> ubuntu@10.7.11.10
sudo docker logs auth-service-uce | grep -i "database\|mysql\|connected"

# User Service
ssh -J ubuntu@<bastion> ubuntu@10.7.11.11
sudo docker logs user-service-uce | grep -i "database\|postgres\|connected"

# Appointment Service
ssh -J ubuntu@<bastion> ubuntu@10.7.11.12
sudo docker logs appointment-service-uce | grep -i "database\|postgres\|connected"
```

### 3. Prueba Funcional Completa
Ejecutar el script de prueba funcional:
```bash
# Desde el Bastion
/tmp/final-test.sh
```

---

## Caracteres Especiales que Requieren Codificación

| Carácter | Codificación URL | Descripción |
|----------|------------------|-------------|
| `!` | `%21` | Exclamación |
| `@` | `%40` | Arroba (crítico - separador en URLs) |
| `#` | `%23` | Numeral (inicio de fragmento) |
| `$` | `%24` | Dólar |
| `%` | `%25` | Porcentaje |
| `&` | `%26` | Ampersand |
| `+` | `%2B` | Más |
| `=` | `%3D` | Igual |
| `?` | `%3F` | Interrogación |
| `/` | `%2F` | Barra (puede causar problemas) |
| ` ` (espacio) | `%20` o `+` | Espacio |

---

## Mejores Prácticas

### 1. Siempre Codificar Contraseñas en URLs
- **Nunca** insertar contraseñas directamente en URLs de conexión
- Usar funciones de codificación URL apropiadas para cada lenguaje:
  - Python: `urllib.parse.quote_plus()`
  - Go: `url.QueryEscape()`
  - JavaScript/Node.js: `encodeURIComponent()`

### 2. Validar Contraseñas en Desarrollo
- Si una contraseña contiene caracteres especiales, verificar que esté codificada correctamente
- Probar con diferentes combinaciones de caracteres especiales

### 3. Usar Variables de Entorno
- Nunca hardcodear contraseñas en el código
- Usar variables de entorno o sistemas de gestión de secretos (AWS Secrets Manager, HashiCorp Vault, etc.)

### 4. Logging Seguro
- **Nunca** loguear contraseñas completas
- Si es necesario para debugging, mostrar solo los primeros/last caracteres: `Admin***`

---

## Archivos Modificados

1. ✅ `apps/Micro1_Auth_Service/app/config.py`
2. ✅ `apps/Micro2_User_Service/app/config.py`
3. ✅ `apps/Micro3_Patient_Service/app/database.py`
4. ✅ `apps/Micro4_Appointment_Service/pkg/config/config.go` (Corregido)

---

## Estado de Implementación

| Servicio | Estado | Base de Datos | Lenguaje |
|----------|--------|----------------|----------|
| Auth Service | ✅ Corregido | MySQL | Python |
| User Service | ✅ Corregido | PostgreSQL | Python |
| Patient Service | ✅ Corregido | PostgreSQL | Python |
| Appointment Service | ✅ Corregido | PostgreSQL | Go |

---

## Notas Adicionales

### Docker Images Actualizadas
- ✅ `stevxd97/uce-auth-service:latest`
- ✅ `stevxd97/uce-user-service:latest`
- ✅ `stevxd97/uce-patient-service:latest`
- ⏳ `stevxd97/uce-appointment-service:latest` (Requiere rebuild y push)

### Prueba Funcional Exitosa
La prueba funcional completa fue ejecutada exitosamente después de aplicar las correcciones:
- ✅ Registro de usuario
- ✅ Verificación de email (automática)
- ✅ Login y obtención de token JWT
- ✅ Creación de perfil en User Service
- ✅ Verificación de perfil creado

---

## Referencias

- [RFC 3986 - Uniform Resource Identifier (URI): Generic Syntax](https://tools.ietf.org/html/rfc3986)
- [Python urllib.parse documentation](https://docs.python.org/3/library/urllib.parse.html)
- [Go net/url package](https://pkg.go.dev/net/url)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)
- [MySQL Connection Strings](https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html)

---

**Fecha de Documentación:** 2026-01-22  
**Última Actualización:** 2026-01-22
