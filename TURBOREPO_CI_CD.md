# TurboRepo CI/CD Architecture

## 📋 Resumen

Cada microservicio tiene su propio workflow de GitHub Actions independiente que aprovecha TurboRepo para optimizar la ejecución de tareas, caching y paralelización.

## 🏗️ Estructura

```
FINAL-PROJECT-BACKEND/
├── turbo.json                    # Configuración central de Turbo
├── package.json                  # Scripts globales con Turbo
├── .github/
│   └── workflows/
│       ├── auth-service.yml      # CI/CD específico para Auth Service
│       ├── user-service.yml      # CI/CD específico para User Service
│       └── ...                   # Un workflow por cada microservicio
└── apps/
    ├── Micro1_Auth_Service/
    │   ├── package.json          # Scripts de test, lint, format, docker:build
    │   └── tests/
    └── Micro2_User_Service/
        ├── package.json          # Scripts de test, lint, format, docker:build
        └── tests/
```

## 🎯 Ventajas de esta Arquitectura

### 1. **Independencia**
- Cada microservicio tiene su propio workflow de CI/CD
- Los workflows solo se activan cuando hay cambios en su directorio específico
- Ejemplo: push a `apps/Micro1_Auth_Service/**` solo activa `auth-service.yml`

### 2. **Optimización con TurboRepo**
- **Caching inteligente**: Turbo cachea los resultados de tests y builds
- **Ejecución paralela**: Turbo puede ejecutar múltiples tareas en paralelo
- **Incremental builds**: Solo ejecuta lo que cambió

### 3. **Escalabilidad**
- Fácil agregar nuevos microservicios
- Cada servicio mantiene sus propias dependencias y configuraciones
- No hay conflictos entre microservicios

## 📝 Configuración de Cada Microservicio

### package.json de cada microservicio

Cada `apps/MicroX_Service/package.json` debe incluir:

```json
{
  "name": "MicroX_Service",
  "version": "1.0.0",
  "scripts": {
    "dev": "python run.py",
    "test": "pytest tests/ -v --cov=app --cov-report=term-missing",
    "lint": "pylint app/",
    "format": "black app/",
    "docker:build": "docker build -t uce-service-name ."
  }
}
```

### GitHub Actions Workflow

Cada workflow sigue esta estructura:

```yaml
name: Service Name CI/CD

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'apps/MicroX_Service/**'
      - '.github/workflows/service-name.yml'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Node.js (for Turbo)
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install root dependencies (Turbo)
        run: npm install
      
      - name: Install Python dependencies
        working-directory: apps/MicroX_Service
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests with Turbo
        run: turbo run test --filter=MicroX_Service
      
      # ... build-and-push, deploy, etc.
```

## 🔄 Flujo de CI/CD

### 1. Developer Push
```bash
git add apps/Micro1_Auth_Service/
git commit -m "feat: add new endpoint"
git push origin develop
```

### 2. GitHub Actions Triggered
- Solo se activa `auth-service.yml`
- Otros workflows permanecen inactivos

### 3. Turbo Execution
```bash
turbo run test --filter=Micro1_Auth_Service
```

TurboRepo:
- Verifica si hay cache disponible
- Instala dependencias si es necesario
- Ejecuta las pruebas
- Guarda resultados en cache

### 4. Build & Push
Si los tests pasan:
- Construye imagen Docker
- Pushea a DockerHub con tags apropiados
- (Opcional) Deploy a AWS

## 🎨 Comandos Útiles

### Desde la raíz del proyecto

```bash
# Ejecutar tests de todos los microservicios
npm run test

# Ejecutar tests de un microservicio específico
npm run test -- --filter=Micro1_Auth_Service

# Ejecutar dev mode de un microservicio
turbo run dev --filter=Micro1_Auth_Service

# Ejecutar dev mode de múltiples microservicios
turbo run dev --filter=Micro1_Auth_Service --filter=Micro2_User_Service

# Ver el grafo de tareas
turbo run test --graph

# Limpiar cache de Turbo
turbo run clean
```

### Atajos definidos en root package.json

```bash
# Dev mode para Auth Service
npm run auth:dev

# Dev mode para User Service
npm run user:dev
```

## 🔧 turbo.json Configuration

```json
{
  "tasks": {
    "test": {
      "dependsOn": ["^build"],
      "outputs": ["coverage/**", "test-results/**"],
      "inputs": ["**/*.py", "tests/**", "**/test_*.py"]
    },
    "docker:build": {
      "dependsOn": ["^docker:build"],
      "cache": false
    }
  }
}
```

**Explicación:**
- `dependsOn`: Define dependencias entre tareas
- `outputs`: Archivos que Turbo debe cachear
- `inputs`: Archivos que invalidan el cache si cambian
- `cache: false`: Para tareas que no deben cachearse

## 📊 Pipeline Stages

```
┌─────────────────────────────────────────────────────┐
│              Developer Push                          │
│       (apps/Micro1_Auth_Service/...)                │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│        GitHub Actions Triggered                      │
│     (auth-service.yml only)                          │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│          Setup (Node.js + Python)                    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│    Install Root Dependencies (npm install)           │
│           (includes TurboRepo)                       │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│   Install Service Dependencies (pip install)         │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│    Run Tests with Turbo                              │
│  (turbo run test --filter=Micro1_Auth_Service)      │
│           ├─ Check Cache                             │
│           ├─ Run Tests                               │
│           └─ Save to Cache                           │
└────────────────┬────────────────────────────────────┘
                 │
          ┌──────┴──────┐
          │             │
     ✅ Pass        ❌ Fail
          │             │
          ▼             ▼
┌──────────────┐  ┌──────────────┐
│ Build Docker │  │ Stop Pipeline│
│ Push to Hub  │  │ Notify Team  │
│ Deploy AWS   │  └──────────────┘
└──────────────┘
```

## 🚀 Agregar Nuevo Microservicio

### 1. Crear estructura del servicio

```bash
mkdir -p apps/Micro3_NewService/tests
cd apps/Micro3_NewService
```

### 2. Crear package.json

```json
{
  "name": "Micro3_NewService",
  "version": "1.0.0",
  "scripts": {
    "dev": "python run.py",
    "test": "pytest tests/ -v --cov=app",
    "lint": "pylint app/",
    "format": "black app/",
    "docker:build": "docker build -t uce-new-service ."
  }
}
```

### 3. Crear workflow

```bash
cp .github/workflows/auth-service.yml .github/workflows/new-service.yml
```

Editar `new-service.yml`:
- Cambiar nombre del workflow
- Actualizar paths
- Cambiar `--filter=Micro3_NewService`

### 4. Actualizar root package.json (opcional)

```json
{
  "scripts": {
    "new:dev": "turbo run dev --filter=Micro3_NewService"
  }
}
```

## 📈 Monitoreo y Logs

### GitHub Actions Dashboard
- Ver todos los workflows en: `github.com/tu-repo/actions`
- Cada workflow muestra su propio historial
- Logs separados por microservicio

### TurboRepo Dashboard (Local)
```bash
# Ver estadísticas de cache
turbo run test --summarize

# Ver qué tareas se ejecutaron
turbo run test --filter=Micro1_Auth_Service --dry-run
```

## 🎯 Best Practices

1. **Commits atómicos**: Un commit por microservicio
2. **Branches por feature**: `feature/auth-new-endpoint`
3. **Tests antes de push**: `npm run test -- --filter=MicroX`
4. **Revisar cache**: Si tests fallan inesperadamente, limpiar cache
5. **Documentar cambios**: Actualizar README de cada microservicio

## 🔍 Troubleshooting

### Tests no se ejecutan
```bash
# Verificar que el filtro coincide con el nombre en package.json
turbo run test --filter=Micro1_Auth_Service --dry-run
```

### Cache obsoleto
```bash
# Limpiar cache de Turbo
rm -rf .turbo
turbo run test --force
```

### Workflow no se activa
- Verificar paths en el workflow YAML
- Asegurar que los cambios están en `apps/MicroX_Service/**`

## 📚 Recursos

- [TurboRepo Docs](https://turbo.build/repo/docs)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Build & Push](https://github.com/marketplace/actions/build-and-push-docker-images)

---

**Resumen:** Cada microservicio es independiente pero aprovecha TurboRepo para optimización. Los workflows solo se activan para cambios específicos de cada servicio. ✨
