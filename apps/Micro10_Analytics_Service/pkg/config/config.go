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

	// MongoDB
	MongoDBHost       string
	MongoDBPort       string
	MongoDBUser       string
	MongoDBPassword   string
	MongoDBDatabase   string
	MongoDBAuthSource string

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
	RoomServiceURL        string
	ClinicalServiceURL    string
	SupervisionServiceURL string
	NotificationServiceURL string
	ReportingServiceURL   string

	// CORS
	CORSOrigins string
}

var AppConfig *Config

func LoadConfig() error {
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using environment variables")
	}

	AppConfig = &Config{
		AppName:     getEnv("APP_NAME", "Analytics Service"),
		AppVersion:  getEnv("APP_VERSION", "1.0.0"),
		Environment: getEnv("ENVIRONMENT", "development"),
		Port:        getEnv("PORT", "8009"),
		Debug:       getEnvAsBool("DEBUG", true),

		MongoDBHost:       getEnv("MONGODB_HOST", "localhost"),
		MongoDBPort:       getEnv("MONGODB_PORT", "27017"),
		MongoDBUser:       getEnv("MONGODB_USER", "root"),
		MongoDBPassword:   getEnv("MONGODB_PASSWORD", "root123"),
		MongoDBDatabase:   getEnv("MONGODB_DATABASE", "analytics_db"),
		MongoDBAuthSource: getEnv("MONGODB_AUTH_SOURCE", "admin"),

		RedisHost:     getEnv("REDIS_HOST", "localhost"),
		RedisPort:     getEnv("REDIS_PORT", "6379"),
		RedisPassword: getEnv("REDIS_PASSWORD", ""),
		RedisDB:       getEnvAsInt("REDIS_DB", 0),

		RabbitMQHost:     getEnv("RABBITMQ_HOST", "localhost"),
		RabbitMQPort:     getEnv("RABBITMQ_PORT", "5672"),
		RabbitMQUser:     getEnv("RABBITMQ_USER", "guest"),
		RabbitMQPassword: getEnv("RABBITMQ_PASSWORD", "guest"),
		RabbitMQVHost:    getEnv("RABBITMQ_VHOST", "/"),
		RabbitMQExchange: getEnv("RABBITMQ_EXCHANGE", "uce_events"),

		JWTSecretKey: getEnv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production"),
		JWTAlgorithm: getEnv("JWT_ALGORITHM", "HS256"),

		AuthServiceURL:         getEnv("AUTH_SERVICE_URL", "http://localhost:8000"),
		UserServiceURL:         getEnv("USER_SERVICE_URL", "http://localhost:8001"),
		PatientServiceURL:      getEnv("PATIENT_SERVICE_URL", "http://localhost:8002"),
		AppointmentServiceURL:  getEnv("APPOINTMENT_SERVICE_URL", "http://localhost:8003"),
		RoomServiceURL:         getEnv("ROOM_SERVICE_URL", "http://localhost:8004"),
		ClinicalServiceURL:     getEnv("CLINICAL_SERVICE_URL", "http://localhost:8005"),
		SupervisionServiceURL:  getEnv("SUPERVISION_SERVICE_URL", "http://localhost:8006"),
		NotificationServiceURL: getEnv("NOTIFICATION_SERVICE_URL", "http://localhost:8007"),
		ReportingServiceURL:    getEnv("REPORTING_SERVICE_URL", "http://localhost:8008"),

		CORSOrigins: getEnv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"),
	}

	return nil
}

func GetMongoURI() string {
	if AppConfig.MongoDBUser != "" && AppConfig.MongoDBPassword != "" {
		return fmt.Sprintf("mongodb://%s:%s@%s:%s/%s?authSource=%s",
			AppConfig.MongoDBUser,
			AppConfig.MongoDBPassword,
			AppConfig.MongoDBHost,
			AppConfig.MongoDBPort,
			AppConfig.MongoDBDatabase,
			AppConfig.MongoDBAuthSource,
		)
	}
	return fmt.Sprintf("mongodb://%s:%s/%s",
		AppConfig.MongoDBHost,
		AppConfig.MongoDBPort,
		AppConfig.MongoDBDatabase,
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

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvAsBool(key string, defaultValue bool) bool {
	valStr := getEnv(key, "")
	if val, err := strconv.ParseBool(valStr); err == nil {
		return val
	}
	return defaultValue
}

func getEnvAsInt(key string, defaultValue int) int {
	valStr := getEnv(key, "")
	if val, err := strconv.Atoi(valStr); err == nil {
		return val
	}
	return defaultValue
}
