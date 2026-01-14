# 📊 Reporting Service - UCE Psychology System

Multi-format report generation service with PDF, Excel, and CSV support.

## 🎯 Features

- **Multi-Format Export:** PDF (ReportLab), Excel (openpyxl), CSV (pandas)
- **Template System:** Predefined report templates
- **Scheduled Reports:** Automated report generation
- **Data Aggregation:** Consolidates data from all microservices
- **Role-Based Access:** Per-template permissions
- **Async Processing:** Celery integration (ready)
- **Charts & Graphs:** Matplotlib integration

## 🏗️ Architecture

- **Language:** Python 3.11
- **Framework:** FastAPI 0.109.0
- **Database:** PostgreSQL 14 (async with asyncpg)
- **Cache:** Redis 7.0
- **Event Bus:** RabbitMQ
- **Pattern:** KISS (Keep It Simple, Stupid)
- **Port:** 8008

## 📦 Models

### Report
- Stores report metadata and status
- Links to generated files
- Tracks generation progress

### ReportTemplate
- Predefined report configurations
- Query templates and parameters
- Role-based permissions

### ScheduledReport
- Automated report scheduling
- Cron-based execution
- Email distribution

### AggregatedMetric
- Pre-calculated metrics
- Fast report generation
- Time-series data

## 🔌 API Endpoints

### User Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/reports` | List user's reports |
| GET | `/api/v1/reports/{id}` | Get report details |
| GET | `/api/v1/reports/{id}/download` | Download report file |
| POST | `/api/v1/reports/generate` | Generate new report |
| DELETE | `/api/v1/reports/{id}` | Delete report |
| GET | `/api/v1/reports/templates/available` | List available templates |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/templates` | List all templates |
| POST | `/api/v1/admin/templates` | Create template |
| PUT | `/api/v1/admin/templates/{id}` | Update template |
| DELETE | `/api/v1/admin/templates/{id}` | Delete template |
| GET | `/api/v1/admin/stats` | Report statistics |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | Service info |

## 🔗 Microservice Integration

Consults data from:
- **Auth Service** (8000): Users, authentication stats
- **User Service** (8001): User profiles, activity
- **Patient Service** (8002): Consultantes, expedientes
- **Appointment Service** (8003): Appointments, scheduling
- **Room Service** (8004): Room utilization
- **Clinical Service** (8005): Sessions, clinical notes
- **Supervision Service** (8006): Supervisions, feedback
- **Notification Service** (8007): Notification stats

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start service
python -m app.main
```

### Docker

```bash
# Build image
docker build -t stevxd97/uce-reporting-service:latest .

# Run container
docker-compose up -d reporting-service
```

## 📊 Report Types

### 1. Operational Reports
- Daily/weekly appointments
- Room occupancy
- User activity

### 2. Analytical Reports
- Executive dashboards
- Trend analysis
- Performance metrics

### 3. Clinical Reports
- Patient expedientes
- Session summaries
- Treatment plans

### 4. Administrative Reports
- Resource utilization
- Quality metrics
- Statistical summaries

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Specific test file
pytest tests/test_models.py -v
```

## 📝 Environment Variables

Key variables:
- `DATABASE_URL`: PostgreSQL connection
- `REDIS_HOST`: Redis cache server
- `RABBITMQ_HOST`: RabbitMQ message broker
- `REPORTS_STORAGE_PATH`: Report file storage
- `ENABLE_CHARTS`: Enable/disable chart generation
- `MAX_CONCURRENT_REPORTS`: Concurrent report limit

See `.env.example` for full list.

## 🔒 Security

- JWT authentication on all endpoints
- Role-based access control
- File access validation
- SQL injection prevention (SQLAlchemy ORM)

## 📈 Performance

- Async database operations (asyncpg)
- Redis caching for frequent queries
- Celery for background processing (ready)
- Pagination on list endpoints

## 📚 Dependencies

- **FastAPI:** Web framework
- **SQLAlchemy:** ORM
- **ReportLab:** PDF generation
- **openpyxl:** Excel generation
- **pandas:** Data processing
- **matplotlib:** Chart generation
- **httpx:** HTTP client

## 🐛 Troubleshooting

### Reports not generating
- Check Celery worker status (when implemented)
- Verify storage path permissions
- Check microservice connectivity

### Database connection issues
- Verify PostgreSQL is running
- Check DATABASE_URL format
- Ensure database exists

### Chart generation fails
- Install matplotlib dependencies
- Check ENABLE_CHARTS setting
- Verify data format

## 📖 Documentation

- **Swagger UI:** http://localhost:8008/docs
- **ReDoc:** http://localhost:8008/redoc
- **Analysis:** See ANALYSIS.md for detailed design

## 🎨 Pattern: KISS

- Simple file generation pipeline
- Clear separation: Query → Process → Export
- Minimal abstractions
- Configuration over code
- Fail fast, log clearly

## 🔄 Future Enhancements

- [ ] Celery task implementation
- [ ] APScheduler for cron jobs
- [ ] S3 storage integration
- [ ] Report templates UI builder
- [ ] Real-time report progress
- [ ] Advanced chart types

## 📊 Metrics

Health check: http://localhost:8008/health

Returns:
- Service status
- Database connection
- Redis connection
- RabbitMQ status

## 👥 Roles & Permissions

| Role | List Reports | Generate | Download | Admin Templates |
|------|--------------|----------|----------|-----------------|
| Administrador | All | ✅ | All | ✅ |
| Coordinador | All | ✅ | All | ✅ |
| Psicólogo | Own | ✅* | Own | ❌ |
| Estudiante | Own | ✅* | Own | ❌ |
| Consultante | Own | ✅* | Own | ❌ |

*Based on template permissions

## 📝 License

MIT

## 🤝 Contributing

1. Follow KISS principle
2. Add tests for new features
3. Update documentation
4. Use conventional commits

## 📧 Contact

UCE Psychology System - Reporting Service v1.0.0
