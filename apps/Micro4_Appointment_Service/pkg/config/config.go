package config

import (
	"fmt"
	"log"
	"net/url"
	"os"
	"strconv"
	"strings"

	"github.com/joho/godotenv"
)

type Config struct {
	// Server
	AppName     string
	AppVersion  string
	Environment string
	Port        string
	Debug       bool

	// Database
	DBHost     string
	DBPort     string
	DBUser     string
	DBPassword string
	DBName     string
	DBSSLMode  string

	// Redis
	RedisHost     string
	RedisPort     string
	RedisPassword string
	RedisDB       int

	// RabbitMQ
	RabbitMQHost     string
	RabbitMQPort     string
	RabbitMQUser     string
	RabbitMQPassword string
	RabbitMQVHost    string
	RabbitMQExchange string

	// JWT
	JWTSecretKey  string
	JWTAlgorithm  string

	// External Services
	AuthServiceURL    string
	UserServiceURL    string
	PatientServiceURL string
	RoomServiceURL    string

	// CORS
	CORSOrigins string
}

var AppConfig *Config

func LoadConfig() *Config {
	// Load .env file if exists
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using environment variables")
	}

	debug, _ := strconv.ParseBool(getEnv("DEBUG", "false"))
	redisDB, _ := strconv.Atoi(getEnv("REDIS_DB", "0"))

	AppConfig = &Config{
		// Server
		AppName:     getEnv("APP_NAME", "Appointment Service"),
		AppVersion:  getEnv("APP_VERSION", "1.0.0"),
		Environment: getEnv("ENVIRONMENT", "development"),
		Port:        getEnv("PORT", "8003"),
		Debug:       debug,

		// Database
		DBHost:     getEnv("DB_HOST", "localhost"),
		DBPort:     getEnv("DB_PORT", "5432"),
		DBUser:     getEnv("DB_USER", "postgres"),
		DBPassword: getEnv("DB_PASSWORD", "postgres"),
		DBName:     getEnv("DB_NAME", "appointment_db"),
		DBSSLMode:  getEnv("DB_SSLMODE", "disable"),

		// Redis
		RedisHost:     getEnv("REDIS_HOST", "localhost"),
		RedisPort:     getEnv("REDIS_PORT", "6379"),
		RedisPassword: getEnv("REDIS_PASSWORD", ""),
		RedisDB:       redisDB,

		// RabbitMQ
		RabbitMQHost:     getEnv("RABBITMQ_HOST", "localhost"),
		RabbitMQPort:     getEnv("RABBITMQ_PORT", "5672"),
		RabbitMQUser:     getEnv("RABBITMQ_USER", "guest"),
		RabbitMQPassword: getEnv("RABBITMQ_PASSWORD", "guest"),
		RabbitMQVHost:    getEnv("RABBITMQ_VHOST", "/"),
		RabbitMQExchange: getEnv("RABBITMQ_EXCHANGE", "uce_events"),

		// JWT
		JWTSecretKey: getEnv("JWT_SECRET_KEY", "your-secret-key-change-in-production"),
		JWTAlgorithm: getEnv("JWT_ALGORITHM", "HS256"),

		// External Services
		AuthServiceURL:    getEnv("AUTH_SERVICE_URL", "http://localhost:8000"),
		UserServiceURL:    getEnv("USER_SERVICE_URL", "http://localhost:8001"),
		PatientServiceURL: getEnv("PATIENT_SERVICE_URL", "http://localhost:8002"),
		RoomServiceURL:    getEnv("ROOM_SERVICE_URL", "http://localhost:8004"),

		// CORS
		CORSOrigins: getEnv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"),
	}

	log.Printf("Configuration loaded for %s v%s", AppConfig.AppName, AppConfig.AppVersion)
	return AppConfig
}

func (c *Config) GetDSN() string {
	// PostgreSQL DSN format handles special characters directly
	// If password contains spaces or special characters, wrap in single quotes
	password := c.DBPassword
	if strings.Contains(password, " ") || strings.ContainsAny(password, "!@#$%^&*()") {
		password = "'" + strings.ReplaceAll(password, "'", "''") + "'"
	}
	
	user := c.DBUser
	if strings.Contains(user, " ") {
		user = "'" + strings.ReplaceAll(user, "'", "''") + "'"
	}
	
	return fmt.Sprintf(
		"host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
		c.DBHost, c.DBPort, user, password, c.DBName, c.DBSSLMode,
	)
}

func (c *Config) GetRedisAddr() string {
	return fmt.Sprintf("%s:%s", c.RedisHost, c.RedisPort)
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

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
