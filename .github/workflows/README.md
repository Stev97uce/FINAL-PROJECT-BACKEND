# GitHub Actions - Guía de Configuración

Esta guía explica cómo configurar los workflows de GitHub Actions para deployment automático de microservicios a AWS.

## 📋 Workflows Disponibles

Cada microservicio tiene su propio workflow:

| Workflow | Archivo | Servicio | EC2 Host | Puerto |
|----------|---------|----------|----------|--------|
| Deploy Auth Service | `deploy-auth-qa.yml` | Auth | 10.1.1.10 | 8000 |
| Deploy User Service | `deploy-user-qa.yml` | User | 10.1.1.11 | 8001 |
| Deploy Patient Service | `deploy-patient-qa.yml` | Patient | 10.1.1.12 | 8002 |
| Deploy Appointment Service | `deploy-appointment-qa.yml` | Appointment | 10.1.1.13 | 8003 |
| Deploy Room Service | `deploy-room-qa.yml` | Room | 10.2.1.10 | 8004 |
| Deploy Clinical Service | `deploy-clinical-qa.yml` | Clinical | 10.2.1.11 | 8005 |
| Deploy Supervision Service | `deploy-supervision-qa.yml` | Supervision | 10.2.1.12 | 8006 |
| Deploy Notification Service | `deploy-notification-qa.yml` | Notification | 10.2.1.13 | 8007 |
| Deploy Reporting Service | `deploy-reporting-qa.yml` | Reporting | 10.3.1.10 | 8008 |
| Deploy Analytics Service | `deploy-analytics-qa.yml` | Analytics | 10.3.1.11 | 8009 |

## 🔐 Secrets Requeridos

### GitHub Repository Secrets

Configurar en: **Settings → Secrets and variables → Actions → New repository secret**

#### 1. DockerHub Credentials

```
DOCKERHUB_USERNAME = tu-usuario-dockerhub
DOCKERHUB_TOKEN    = dckr_pat_xxxxxxxxxxxxxxxxxxxxx
```

**Obtener token**: DockerHub → Account Settings → Security → New Access Token

#### 2. Bastion SSH Key

```
BASTION_HOST    = 3.85.123.45  (IP elástica del Bastion)
BASTION_SSH_KEY = -----BEGIN RSA PRIVATE KEY-----
                  MIIEpAIBAAKCAQEA...
                  -----END RSA PRIVATE KEY-----
```

**Obtener key**: La private key del par SSH usado para el Bastion (ej: `bastion-key.pem`)

#### 3. EC2 SSH Key

```
EC2_SSH_KEY = -----BEGIN RSA PRIVATE KEY-----
              MIIEpAIBAAKCAQEA...
              -----END RSA PRIVATE KEY-----
```

**Obtener key**: La private key del par SSH usado para microservicios en Cuentas 7, 8, 9

> ⚠️ **Nota**: Puede ser la misma key que Bastion o diferente, según tu configuración en Terraform

## 🚀 Flujo de Deployment

```
┌─────────────────────────────────────────────────────────────┐
│  1. git push origin qa                                      │
│     (Cambios en apps/Micro1_Auth_Service/)                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  2. GitHub Actions Trigger                                  │
│     - Detecta cambios en path específico                    │
│     - Inicia workflow para ese servicio                     │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Build Docker Image                                      │
│     - docker build con cache                                │
│     - Tag: latest y sha-xxxxx                               │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Push to DockerHub                                       │
│     - docker push ucepsychology/auth-service:latest         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  5. SSH to EC2 (via Bastion ProxyJump)                      │
│     - ssh bastion → ssh target                              │
│     - Ejecuta commands en EC2                               │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Deploy en EC2                                           │
│     - docker pull latest                                    │
│     - docker stop old container                             │
│     - docker run new container                              │
│     - docker system prune                                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  7. Health Check                                            │
│     - curl http://10.1.1.10:8000/health                     │
│     - Verifica que servicio responda 200 OK                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  8. Notificación                                            │
│     - ✅ Success: Log en GitHub Actions                      │
│     - ❌ Failure: Workflow falla, revisar logs               │
└─────────────────────────────────────────────────────────────┘
```

## 📝 Crear Workflow para Otro Servicio

### Paso 1: Copiar plantilla

```bash
cp .github/workflows/deploy-auth-qa.yml .github/workflows/deploy-user-qa.yml
```

### Paso 2: Editar variables

```yaml
name: Deploy User Service to QA  # ← Cambiar nombre

on:
  push:
    branches:
      - qa
    paths:
      - 'apps/Micro2_User_Service/**'  # ← Cambiar path
      - '.github/workflows/deploy-user-qa.yml'

env:
  SERVICE_NAME: user-service           # ← Cambiar nombre
  DOCKER_IMAGE: ucepsychology/user-service  # ← Cambiar imagen
  EC2_HOST: 10.1.1.11                  # ← Cambiar IP
  SERVICE_PORT: 8001                   # ← Cambiar puerto
```

### Paso 3: Actualizar context en Build step

```yaml
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    context: ./apps/Micro2_User_Service    # ← Cambiar path
    file: ./apps/Micro2_User_Service/Dockerfile  # ← Cambiar path
```

### Paso 4: Commit y push

```bash
git add .github/workflows/deploy-user-qa.yml
git commit -m "Add User Service deployment workflow"
git push origin main
```

## 🧪 Probar Workflow

### Opción 1: Push a rama qa

```bash
# Hacer cambio en el servicio
echo "# Test change" >> apps/Micro1_Auth_Service/README.md

# Commit y push a rama qa
git add .
git commit -m "Test deployment workflow"
git push origin qa
```

### Opción 2: Trigger manual (workflow_dispatch)

Agregar al workflow:

```yaml
on:
  push:
    branches:
      - qa
  workflow_dispatch:  # ← Permite trigger manual
```

En GitHub: **Actions → Select workflow → Run workflow**

## 📊 Monitorear Deployment

### En GitHub Actions

1. Ir a **Actions** tab en GitHub
2. Seleccionar el workflow que está corriendo
3. Ver logs en tiempo real
4. Expandir cada step para ver detalles

### En EC2 (logs en vivo)

```bash
# Conectar al EC2
ssh -J ubuntu@<BASTION_IP> ubuntu@10.1.1.10

# Ver logs del contenedor
docker logs -f auth-service
```

### En Prometheus/Grafana

- **Prometheus**: Verificar que target esté UP
- **Grafana**: Ver métricas de CPU/RAM después del deployment

## 🔧 Troubleshooting

### Error: "Permission denied (publickey)"

**Causa**: SSH key incorrecta o mal formateada

**Solución**:
1. Verificar que copiaste toda la key (incluyendo BEGIN/END)
2. Asegurar que no hay espacios extra o saltos de línea adicionales
3. Key debe tener permisos 600: `chmod 600 key.pem`

### Error: "Connection refused"

**Causa**: Bastion no accesible o IP incorrecta

**Solución**:
1. Verificar `BASTION_HOST` tiene la IP elástica correcta
2. Security Group del Bastion permite SSH desde GitHub Actions IPs
3. Bastion está corriendo: `aws ec2 describe-instances --instance-ids i-xxxxx`

### Error: "docker: command not found"

**Causa**: Docker no instalado en EC2

**Solución**:
1. Verificar que user-data script corrió correctamente
2. Conectar manualmente y verificar: `docker --version`
3. Si falta, ejecutar: `sudo apt-get update && sudo apt-get install -y docker.io`

### Error: "Health check failed"

**Causa**: Servicio no responde en /health endpoint

**Solución**:
1. Conectar al EC2: `ssh -J ubuntu@<BASTION> ubuntu@<TARGET>`
2. Ver logs: `docker logs auth-service`
3. Verificar puerto: `ss -tulnp | grep 8000`
4. Probar manualmente: `curl http://localhost:8000/health`

### Workflow se queda "pending"

**Causa**: GitHub Actions runner ocupado o límite de concurrencia

**Solución**:
1. Esperar a que otros jobs terminen
2. Cancelar jobs viejos si están stuck
3. Verificar límites de la cuenta GitHub (free tier = 1 job simultáneo)

## ⚡ Optimizaciones

### 1. Docker Build Cache

Ya implementado en el workflow:

```yaml
cache-from: type=registry,ref=${{ env.DOCKER_IMAGE }}:buildcache
cache-to: type=registry,ref=${{ env.DOCKER_IMAGE }}:buildcache,mode=max
```

Esto reduce tiempo de build de ~5min a ~30seg en builds subsecuentes.

### 2. Conditional Deployment

Evitar deployment si solo cambiaron archivos no críticos:

```yaml
on:
  push:
    branches:
      - qa
    paths:
      - 'apps/Micro1_Auth_Service/app/**'  # Solo código
      - 'apps/Micro1_Auth_Service/requirements.txt'
      - '.github/workflows/deploy-auth-qa.yml'
    paths-ignore:
      - '**/*.md'  # Ignorar README changes
      - '**/*.txt' # Ignorar docs
```

### 3. Parallel Deployments

Para deployar múltiples servicios en paralelo, crear un workflow maestro:

```yaml
name: Deploy All Services

on:
  workflow_dispatch:

jobs:
  deploy-group-1:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [auth, user, patient, appointment]
    steps:
      - uses: ./.github/workflows/deploy-${{ matrix.service }}-qa.yml
```

## 🔒 Seguridad

### Best Practices

1. ✅ **Nunca commitear secrets** en el código
2. ✅ **Usar GitHub Secrets** para credenciales
3. ✅ **Rotar SSH keys** periódicamente (cada 3 meses)
4. ✅ **Limitar branch** triggers (solo qa, no main)
5. ✅ **Review logs** antes de merge a production

### Secrets Rotation

Cuando cambies SSH keys:

1. Generar nuevo par de keys en AWS
2. Actualizar secret en GitHub: **Settings → Secrets → Edit**
3. Re-run workflows que fallaron con old key

## 📚 Referencias

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [SSH Action](https://github.com/appleboy/ssh-action)

---

**¿Preguntas?** Ver logs detallados en GitHub Actions o revisar [terraform/qa/README.md](../terraform/qa/README.md)
