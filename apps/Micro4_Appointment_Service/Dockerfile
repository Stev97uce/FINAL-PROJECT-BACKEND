# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Install dependencies
RUN apk add --no-cache git

# Copy all source code
COPY . .

# Download dependencies and create go.sum
RUN go mod tidy && go mod download && go mod verify

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o appointment-service ./cmd/main.go

# Runtime stage
FROM alpine:latest

WORKDIR /root/

# Install ca-certificates for HTTPS
RUN apk --no-cache add ca-certificates tzdata

# Set timezone
ENV TZ=America/Guayaquil

# Copy binary from builder
COPY --from=builder /app/appointment-service .

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8003/health || exit 1

# Run the application
CMD ["./appointment-service"]
