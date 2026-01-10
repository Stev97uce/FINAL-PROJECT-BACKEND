# DockerHub Setup y CI/CD

Este documento explica cómo configurar DockerHub y GitHub Actions para los microservicios.

## Prerequisitos

1. Cuenta en DockerHub: https://hub.docker.com
2. Repositorio en GitHub
3. Docker instalado localmente

## Paso 1: Configurar DockerHub

### 1.1 Crear Token de Acceso

1. Ir a https://hub.docker.com/settings/security
2. Click en "New Access Token"
3. Nombre: `github-actions-uce`
4. Permisos: Read, Write, Delete
5. Copiar el token generado (solo se muestra una vez)

### 1.2 Crear Repositorios

Crear los siguientes repositorios en DockerHub:
- `tu-usuario/uce-auth-service`
- `tu-usuario/uce-user-service`

## Paso 2: Configurar GitHub Secrets

En tu repositorio de GitHub, ir a: `Settings > Secrets and variables > Actions`

Crear los siguientes secrets:

### Secrets Requeridos Ahora:
```
DOCKERHUB_USERNAME: tu_usuario_dockerhub
DOCKERHUB_TOKEN: tu_token_dockerhub
```

### Secrets para AWS (agregar cuando tengamos infraestructura):
```
EC2_HOST: ip_o_dns_de_ec2
EC2_USER: ubuntu
EC2_SSH_KEY: contenido_completo_del_archivo_.pem
```

## Paso 3: Build y Push Manual (Opcional)

### Auth Service

```bash
# Build
docker build -t tu-usuario/uce-auth-service:latest ./apps/Micro1_Auth_Service

# Login
docker login

# Push
docker push tu-usuario/uce-auth-service:latest
```

### User Service

```bash
# Build
docker build -t tu-usuario/uce-user-service:latest ./apps/Micro2_User_Service

# Login (si no estás logueado)
docker login

# Push
docker push tu-usuario/uce-user-service:latest
```

## Paso 4: Verificar GitHub Actions

1. Hacer commit de los cambios
2. Push a la rama `develop` o `main`
3. Ir a `Actions` en GitHub
4. Verificar que los workflows se ejecuten correctamente

## Flujo de CI/CD

### Automatic Workflow:

1. **Push a develop/main**
   - ✅ Ejecuta pruebas unitarias (pytest)
   - ✅ Build imagen Docker
   - ✅ Push a DockerHub con tags automáticos
   - ⏸️ Deploy a AWS (comentado hasta tener infraestructura)

2. **Pull Request**
   - ✅ Ejecuta solo pruebas unitarias
   - ❌ No hace build ni push

### Tags de Docker:

- `latest` - Solo para rama main
- `main-{sha}` - Para commits en main
- `develop-{sha}` - Para commits en develop
- `develop` - Última versión en develop

## Paso 5: Testing Local

### Ejecutar pruebas localmente:

```bash
# Auth Service
cd apps/Micro1_Auth_Service
pip install -r requirements-dev.txt
pytest tests/ -v

# User Service
cd apps/Micro2_User_Service
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Paso 6: Actualizar docker-compose.yml para usar DockerHub

Cuando quieras usar las imágenes de DockerHub en lugar de build local:

```yaml
services:
  auth-service:
    image: tu-usuario/uce-auth-service:latest
    # Comentar o eliminar la sección build:
    # build:
    #   context: ./apps/Micro1_Auth_Service
    #   dockerfile: Dockerfile
```

## Troubleshooting

### Error: "unauthorized: incorrect username or password"
- Verificar DOCKERHUB_USERNAME y DOCKERHUB_TOKEN en GitHub Secrets
- Regenerar token en DockerHub si es necesario

### Error: "Tests failed"
- Verificar que todas las dependencias estén en requirements.txt
- Ejecutar pruebas localmente para debugging

### Error: "Cannot connect to database in tests"
- Las pruebas unitarias no requieren base de datos real
- Usan TestClient de FastAPI que mockea las conexiones

## Comandos Útiles

```bash
# Ver imágenes locales
docker images | grep uce

# Limpiar imágenes antiguas
docker image prune -f

# Ver logs de un workflow en GitHub
gh run view --log

# Forzar rebuild sin cache
docker build --no-cache -t imagen:tag .
```

## Próximos Pasos (Cuando tengamos AWS)

1. Crear infraestructura EC2 con Terraform
2. Agregar secrets de AWS a GitHub
3. Descomentar sección deploy-aws en workflows
4. Configurar SSH keys y permisos
5. Probar deployment automático

## Notas Importantes

- Los workflows solo se ejecutan cuando hay cambios en su carpeta respectiva
- Las pruebas deben pasar antes de hacer build/push
- El deployment a AWS está preparado pero comentado
- Mantener tokens de DockerHub seguros (nunca commitearlos)
