package config

import (
	"fmt"
	"log"
	"os"
	"strconv"

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
	JWTSecretKey string
	JWTAlgorithm string

	// External Services
	AuthServiceURL        string
	UserServiceURL        string
	PatientServiceURL     string
	AppointmentServiceURL string

	// CORS
	CORSOrigins string
}

var AppConfig *Config

func LoadConfig() error {
	// Load .env file if exists
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using environment variables")
	}

	AppConfig = &Config{
		// Server
		AppName:     getEnv("APP_NAME", "Room Service"),
		AppVersion:  getEnv("APP_VERSION", "1.0.0"),
		Environment: getEnv("ENVIRONMENT", "development"),
		Port:        getEnv("PORT", "8004"),
		Debug:       getEnvAsBool("DEBUG", true),

		// Database
		DBHost:     getEnv("DB_HOST", "localhost"),
		DBPort:     getEnv("DB_PORT", "5432"),
		DBUser:     getEnv("DB_USER", "postgres"),
		DBPassword: getEnv("DB_PASSWORD", "postgres"),
		DBName:     getEnv("DB_NAME", "room_db"),
		DBSSLMode:  getEnv("DB_SSLMODE", "disable"),

		// Redis
		RedisHost:     getEnv("REDIS_HOST", "localhost"),
		RedisPort:     getEnv("REDIS_PORT", "6379"),
		RedisPassword: getEnv("REDIS_PASSWORD", ""),
		RedisDB:       getEnvAsInt("REDIS_DB", 0),

		// RabbitMQ
		RabbitMQHost:     getEnv("RABBITMQ_HOST", "localhost"),
		RabbitMQPort:     getEnv("RABBITMQ_PORT", "5672"),
		RabbitMQUser:     getEnv("RABBITMQ_USER", "guest"),
		RabbitMQPassword: getEnv("RABBITMQ_PASSWORD", "guest"),
		RabbitMQVHost:    getEnv("RABBITMQ_VHOST", "/"),
		RabbitMQExchange: getEnv("RABBITMQ_EXCHANGE", "uce_events"),

		// JWT
		JWTSecretKey: getEnv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production"),
		JWTAlgorithm: getEnv("JWT_ALGORITHM", "HS256"),

		// External Services
		AuthServiceURL:        getEnv("AUTH_SERVICE_URL", "http://localhost:8000"),
		UserServiceURL:        getEnv("USER_SERVICE_URL", "http://localhost:8001"),
		PatientServiceURL:     getEnv("PATIENT_SERVICE_URL", "http://localhost:8002"),
		AppointmentServiceURL: getEnv("APPOINTMENT_SERVICE_URL", "http://localhost:8003"),

		// CORS
		CORSOrigins: getEnv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"),
	}

	log.Printf("Configuration loaded for %s v%s", AppConfig.AppName, AppConfig.AppVersion)
	return nil
}

func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}

func getEnvAsInt(key string, defaultValue int) int {
	valueStr := os.Getenv(key)
	if valueStr == "" {
		return defaultValue
	}
	value, err := strconv.Atoi(valueStr)
	if err != nil {
		log.Printf("Warning: Invalid integer value for %s, using default: %d", key, defaultValue)
		return defaultValue
	}
	return value
}

func getEnvAsBool(key string, defaultValue bool) bool {
	valueStr := os.Getenv(key)
	if valueStr == "" {
		return defaultValue
	}
	value, err := strconv.ParseBool(valueStr)
	if err != nil {
		log.Printf("Warning: Invalid boolean value for %s, using default: %t", key, defaultValue)
		return defaultValue
	}
	return value
}

func GetDSN() string {
	return fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
		AppConfig.DBHost,
		AppConfig.DBPort,
		AppConfig.DBUser,
		AppConfig.DBPassword,
		AppConfig.DBName,
		AppConfig.DBSSLMode,
	)
}

func GetRedisAddr() string {
	return fmt.Sprintf("%s:%s", AppConfig.RedisHost, AppConfig.RedisPort)
}

func GetRabbitMQURL() string {
	return fmt.Sprintf("amqp://%s:%s@%s:%s%s",
		AppConfig.RabbitMQUser,
		AppConfig.RabbitMQPassword,
		AppConfig.RabbitMQHost,
		AppConfig.RabbitMQPort,
		AppConfig.RabbitMQVHost,
	)
}
