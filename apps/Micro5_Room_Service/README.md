# Room Service - UCE Psychology System

Microservice for managing physical spaces, rooms, and consultation offices for the UCE Psychology System.

## Technology Stack

- **Language:** Go 1.21+
- **Framework:** Gin
- **Database:** PostgreSQL 14 + Redis 7
- **Message Broker:** RabbitMQ 3
- **Port:** 8004

## Features

- Room CRUD operations (consultorios, offices)
- Room scheduling and reservations
- Conflict detection for room bookings
- Room availability finder
- Real-time room status management
- Equipment and capacity tracking
- JWT authentication and role-based access control
- Event publishing to RabbitMQ
- Redis caching for performance

## API Endpoints

### Rooms

- `GET /api/v1/rooms/` - List all rooms (with filters)
- `GET /api/v1/rooms/available` - Find available rooms
- `GET /api/v1/rooms/:id` - Get room details
- `POST /api/v1/rooms/` - Create room (admin, coordinador)
- `PUT /api/v1/rooms/:id` - Update room
- `DELETE /api/v1/rooms/:id` - Delete room
- `PATCH /api/v1/rooms/:id/status` - Update room status
- `GET /api/v1/rooms/:id/schedule` - Get room schedule

### Schedules

- `GET /api/v1/schedules/` - List schedules
- `GET /api/v1/schedules/:id` - Get schedule details
- `POST /api/v1/schedules/` - Create schedule/reservation
- `PUT /api/v1/schedules/:id` - Update schedule
- `DELETE /api/v1/schedules/:id` - Delete schedule

### Health Check

- `GET /health` - Service health status

## Installation

### Prerequisites

- Go 1.21+
- PostgreSQL 14+
- Redis 7+
- RabbitMQ 3+

### Local Development

```bash
# Install dependencies
go mod download

# Run the service
go run cmd/main.go

# Or build and run
go build -o room-service cmd/main.go
./room-service
```

### Docker

```bash
# Build image
docker build -t room-service .

# Run with docker-compose
docker-compose up -d
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DB_HOST` - PostgreSQL host
- `DB_PORT` - PostgreSQL port (default: 5432)
- `DB_NAME` - Database name (default: room_db)
- `REDIS_HOST` - Redis host
- `RABBITMQ_HOST` - RabbitMQ host
- `JWT_SECRET_KEY` - Secret key for JWT validation
- `PORT` - Service port (default: 8004)

## Database Models

### Room
- id (UUID)
- name (string)
- room_number (string, unique)
- floor_number (int)
- building (string)
- capacity (int)
- room_type (enum: consultorio_individual, consultorio_grupal, sala_observacion, sala_reunion)
- status (enum: disponible, ocupado, mantenimiento, inactivo)
- equipment (array of strings)
- description (text)
- is_active (boolean)
- created_at, updated_at (timestamps)

### RoomSchedule
- id (UUID)
- room_id (UUID, FK)
- appointment_id (UUID, nullable)
- start_time (datetime)
- end_time (datetime)
- status (enum: reserved, occupied, completed, cancelled)
- reserved_by (int, user_id)
- purpose (string)
- notes (text)
- created_at, updated_at (timestamps)

## Events Published

- `room.created`
- `room.updated`
- `room.status_changed`
- `room.deleted`
- `schedule.created`
- `schedule.updated`
- `schedule.cancelled`

## Integration with Other Services

- **Appointment Service (8003):** Provides room assignment for appointments
- **Notification Service (8008):** Receives events for room changes
- **Auth Service (8000):** JWT token validation

## Testing

```bash
# Run tests
go test ./...

# Run tests with coverage
go test -cover ./...

# Run specific test
go test -run TestHealthEndpoint ./cmd
```

## Project Structure

```
Micro5_Room_Service/
├── cmd/
│   ├── main.go              # Application entry point
│   └── main_test.go         # Basic tests
├── internal/
│   ├── models/
│   │   ├── room.go          # Room model
│   │   ├── room_schedule.go # Schedule model
│   │   └── dto.go           # Request/response DTOs
│   ├── repository/
│   │   ├── room_repository.go
│   │   └── schedule_repository.go
│   ├── services/
│   │   ├── room_service.go
│   │   └── schedule_service.go
│   ├── handlers/
│   │   ├── room_handler.go
│   │   └── schedule_handler.go
│   ├── middleware/
│   │   ├── auth.go          # JWT authentication
│   │   └── logger.go        # Request logging
│   └── events/
│       └── rabbitmq.go      # Event publisher
├── pkg/
│   ├── config/
│   │   └── config.go        # Configuration management
│   └── database/
│       └── database.go      # Database connections
├── Dockerfile
├── docker-compose.yml
├── go.mod
├── go.sum
└── README.md
```

## License

MIT
