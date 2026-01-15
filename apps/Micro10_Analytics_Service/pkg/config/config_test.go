package config

import (
	"os"
	"testing"
)

func TestLoadConfig(t *testing.T) {
	// Set test environment variables
	os.Setenv("PORT", "9999")
	os.Setenv("APP_NAME", "Test Analytics Service")
	os.Setenv("MONGODB_URI", "mongodb://test:27017")
	os.Setenv("REDIS_HOST", "test-redis")
	os.Setenv("RABBITMQ_HOST", "test-rabbitmq")

	err := LoadConfig()
	if err != nil {
		t.Fatalf("LoadConfig failed: %v", err)
	}

	if AppConfig.Port != "9999" {
		t.Errorf("Expected Port to be 9999, got %s", AppConfig.Port)
	}

	if AppConfig.AppName != "Test Analytics Service" {
		t.Errorf("Expected AppName to be 'Test Analytics Service', got %s", AppConfig.AppName)
	}

	// Cleanup
	os.Unsetenv("PORT")
	os.Unsetenv("APP_NAME")
}

func TestConfig_Defaults(t *testing.T) {
	// Clear all env vars
	os.Clearenv()

	err := LoadConfig()
	if err != nil {
		t.Fatalf("LoadConfig failed: %v", err)
	}

	// Check default values
	if AppConfig.Port == "" {
		t.Error("Port should have a default value")
	}

	if AppConfig.AppName == "" {
		t.Error("AppName should have a default value")
	}
}

func TestConfig_MongoDBSettings(t *testing.T) {
	os.Setenv("MONGODB_HOST", "test-mongo")
	os.Setenv("MONGODB_PORT", "27017")
	os.Setenv("MONGODB_DATABASE", "test_analytics")

	err := LoadConfig()
	if err != nil {
		t.Fatalf("LoadConfig failed: %v", err)
	}

	if AppConfig.MongoDBHost != "test-mongo" {
		t.Errorf("Expected MongoDBHost to be 'test-mongo', got %s", AppConfig.MongoDBHost)
	}

	if AppConfig.MongoDBDatabase != "test_analytics" {
		t.Errorf("Expected MongoDBDatabase to be 'test_analytics', got %s", AppConfig.MongoDBDatabase)
	}

	// Cleanup
	os.Unsetenv("MONGODB_HOST")
	os.Unsetenv("MONGODB_PORT")
	os.Unsetenv("MONGODB_DATABASE")
}

func TestConfig_RedisSettings(t *testing.T) {
	os.Setenv("REDIS_HOST", "test-redis")
	os.Setenv("REDIS_PORT", "6379")

	err := LoadConfig()
	if err != nil {
		t.Fatalf("LoadConfig failed: %v", err)
	}

	if AppConfig.RedisHost != "test-redis" {
		t.Errorf("Expected RedisHost to be 'test-redis', got %s", AppConfig.RedisHost)
	}

	// Cleanup
	os.Unsetenv("REDIS_HOST")
	os.Unsetenv("REDIS_PORT")
}

func TestConfig_RabbitMQSettings(t *testing.T) {
	os.Setenv("RABBITMQ_HOST", "test-rabbitmq")
	os.Setenv("RABBITMQ_PORT", "5672")
	os.Setenv("RABBITMQ_USER", "testuser")
	os.Setenv("RABBITMQ_PASSWORD", "testpass")
	os.Setenv("RABBITMQ_EXCHANGE", "test_events")

	err := LoadConfig()
	if err != nil {
		t.Fatalf("LoadConfig failed: %v", err)
	}

	if AppConfig.RabbitMQHost != "test-rabbitmq" {
		t.Errorf("Expected RabbitMQHost to be 'test-rabbitmq', got %s", AppConfig.RabbitMQHost)
	}

	if AppConfig.RabbitMQExchange != "test_events" {
		t.Errorf("Expected RabbitMQExchange to be 'test_events', got %s", AppConfig.RabbitMQExchange)
	}

	// Cleanup
	os.Unsetenv("RABBITMQ_HOST")
	os.Unsetenv("RABBITMQ_PORT")
	os.Unsetenv("RABBITMQ_USER")
	os.Unsetenv("RABBITMQ_PASSWORD")
	os.Unsetenv("RABBITMQ_EXCHANGE")
}

func TestConfig_ServiceURLs(t *testing.T) {
	os.Setenv("AUTH_SERVICE_URL", "http://test-auth:8000")
	os.Setenv("USER_SERVICE_URL", "http://test-user:8001")
	os.Setenv("APPOINTMENT_SERVICE_URL", "http://test-appointment:8003")

	err := LoadConfig()
	if err != nil {
		t.Fatalf("LoadConfig failed: %v", err)
	}

	if AppConfig.AuthServiceURL != "http://test-auth:8000" {
		t.Errorf("Expected AuthServiceURL to be 'http://test-auth:8000', got %s", AppConfig.AuthServiceURL)
	}

	if AppConfig.UserServiceURL != "http://test-user:8001" {
		t.Errorf("Expected UserServiceURL to be 'http://test-user:8001', got %s", AppConfig.UserServiceURL)
	}

	// Cleanup
	os.Unsetenv("AUTH_SERVICE_URL")
	os.Unsetenv("USER_SERVICE_URL")
	os.Unsetenv("APPOINTMENT_SERVICE_URL")
}

func TestConfig_JWTSettings(t *testing.T) {
	os.Setenv("JWT_SECRET_KEY", "test-secret-key")
	os.Setenv("JWT_ALGORITHM", "HS256")

	err := LoadConfig()
	if err != nil {
		t.Fatalf("LoadConfig failed: %v", err)
	}

	if AppConfig.JWTSecretKey != "test-secret-key" {
		t.Errorf("Expected JWTSecretKey to be 'test-secret-key', got %s", AppConfig.JWTSecretKey)
	}

	// Cleanup
	os.Unsetenv("JWT_SECRET_KEY")
	os.Unsetenv("JWT_ALGORITHM")
}

func TestConfig_DebugMode(t *testing.T) {
	os.Setenv("DEBUG", "true")

	err := LoadConfig()
	if err != nil {
		t.Fatalf("LoadConfig failed: %v", err)
	}

	if !AppConfig.Debug {
		t.Error("Expected Debug to be true")
	}

	// Test false
	os.Setenv("DEBUG", "false")
	err = LoadConfig()
	if err != nil {
		t.Fatalf("LoadConfig failed: %v", err)
	}

	if AppConfig.Debug {
		t.Error("Expected Debug to be false")
	}

	// Cleanup
	os.Unsetenv("DEBUG")
}
