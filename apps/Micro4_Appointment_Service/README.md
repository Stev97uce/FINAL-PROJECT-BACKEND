# Appointment Service - UCE Psychology System

Microservice for managing appointments, calendar, and availability for the UCE Psychology System.

## Technology Stack

- **Language:** Go 1.21+
- **Framework:** Gin
- **Database:** PostgreSQL 14 + Redis 7
- **Message Broker:** RabbitMQ 3
- **Port:** 8003

## Features

- Appointment CRUD operations
- Professional availability management
- Time slot finder with overlap detection
- Calendar views
- Appointment status management (scheduled, confirmed, in_progress, completed, cancelled, no_show)
- JWT authentication and role-based access control
- Event publishing to RabbitMQ
- Redis caching for performance

## API Endpoints

### Appointments

- `POST /api/v1/appointments/` - Create appointment (recepcionista, coordinador, admin)
- `GET /api/v1/appointments/` - List appointments with filters
- `GET /api/v1/appointments/{id}` - Get appointment details
- `PATCH /api/v1/appointments/{id}` - Update appointment
- `DELETE /api/v1/appointments/{id}` - Cancel appointment
- `POST /api/v1/appointments/{id}/confirm` - Confirm appointment
- `POST /api/v1/appointments/{id}/complete` - Mark as completed
- `POST /api/v1/appointments/{id}/no-show` - Mark as no-show

### Availability

- `GET /api/v1/availability/slots` - Find available time slots
- `GET /api/v1/availability/` - List availability by professional
- `GET /api/v1/availability/{id}` - Get availability details
- `POST /api/v1/availability/` - Create availability (coordinador, admin)
- `PUT /api/v1/availability/{id}` - Update availability
- `DELETE /api/v1/availability/{id}` - Delete availability

### Health Check

- `GET /health` - Service health status

## Installation

### Prerequisites

- Go 1.21+
- Docker & Docker Compose
- PostgreSQL 14
- Redis 7
- RabbitMQ 3

### Local Development

1. Clone the repository
2. Copy environment variables:
```bash
cp .env.example .env
```

3. Install dependencies:
```bash
go mod download
```

4. Run the service:
```bash
go run cmd/main.go
```

### Docker

Build and run with Docker Compose:

```bash
# Build image
docker build -t stevxd97/uce-appointment-service:latest .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f appointment_service

# Stop services
docker-compose down
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DB_HOST` - PostgreSQL host
- `DB_PORT` - PostgreSQL port (default: 5432)
- `DB_NAME` - Database name
- `REDIS_HOST` - Redis host
- `RABBITMQ_HOST` - RabbitMQ host
- `JWT_SECRET_KEY` - Secret key for JWT validation
- `PORT` - Service port (default: 8003)

## Database Models

### Appointment
- id (UUID)
- patient_id (int)
- professional_id (int)
- room_id (int, nullable)
- appointment_date (date)
- start_time (time)
- end_time (time)
- duration_minutes (int)
- status (enum)
- appointment_type (enum)
- modality (enum)
- notes (text)
- cancellation_reason (text)
- created_by (int)
- created_at, updated_at (timestamps)

### Availability
- id (UUID)
- professional_id (int)
- day_of_week (int, 0-6)
- start_time (time)
- end_time (time)
- is_active (boolean)
- effective_from (date)
- effective_until (date, nullable)
- created_at, updated_at (timestamps)

## Events Published

- `appointment.created`
- `appointment.confirmed`
- `appointment.cancelled`
- `appointment.completed`
- `appointment.no_show`
- `appointment.reminder_48h`
- `appointment.reminder_24h`

## Integration with Other Services

- **Auth Service (8000):** JWT token validation
- **User Service (8001):** Professional/user data
- **Patient Service (8002):** Patient data
- **Room Service (8004):** Room assignment
- **Notification Service (8007):** Receives appointment events

## Testing

Run tests:
```bash
go test ./... -v
```

With coverage:
```bash
go test ./... -cover -coverprofile=coverage.out
go tool cover -html=coverage.out
```

## Project Structure

```
Micro4_Appointment_Service/
├── cmd/
│   └── main.go                 # Entry point
├── internal/
│   ├── handlers/               # HTTP handlers (Gin)
│   ├── services/               # Business logic
│   ├── models/                 # GORM models & DTOs
│   ├── repository/             # Data access layer
│   ├── middleware/             # JWT auth, logging
│   └── events/                 # RabbitMQ publisher
├── pkg/
│   ├── config/                 # Configuration
│   └── database/               # PostgreSQL + Redis
├── Dockerfile
├── docker-compose.yml
├── go.mod
├── go.sum
└── README.md
```

## License

MIT
