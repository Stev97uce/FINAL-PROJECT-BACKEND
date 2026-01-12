# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy go.mod first
COPY go.mod ./

# Download dependencies (this generates go.sum)
RUN go mod download

# Copy the rest of the source code
COPY . .

# Ensure go.sum is up to date with all dependencies
RUN go mod tidy

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o room-service ./cmd/main.go

# Runtime stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates tzdata

WORKDIR /root/

# Copy the binary from builder
COPY --from=builder /app/room-service .

# Expose port
EXPOSE 8004

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8004/health || exit 1

# Run the application
CMD ["./room-service"]
