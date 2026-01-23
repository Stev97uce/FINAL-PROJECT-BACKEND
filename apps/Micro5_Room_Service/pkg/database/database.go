package database

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/go-redis/redis/v8"
	"github.com/stev97uce/room-service/internal/models"
	"github.com/stev97uce/room-service/pkg/config"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var (
	DB          *gorm.DB
	RedisClient *redis.Client
)

// InitPostgreSQL initializes the PostgreSQL database connection
func InitPostgreSQL() error {
	dsn := config.GetDSN()

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	if err != nil {
		return fmt.Errorf("failed to connect to database: %w", err)
	}

	sqlDB, err := db.DB()
	if err != nil {
		return fmt.Errorf("failed to get database instance: %w", err)
	}

	// Connection pool settings
	sqlDB.SetMaxIdleConns(10)
	sqlDB.SetMaxOpenConns(100)
	sqlDB.SetConnMaxLifetime(time.Hour)

	// Test connection
	if err := sqlDB.Ping(); err != nil {
		return fmt.Errorf("failed to ping database: %w", err)
	}

	DB = db
	log.Println("PostgreSQL connected successfully")

	// Run migrations
	if err := runMigrations(); err != nil {
		return fmt.Errorf("failed to run migrations: %w", err)
	}

	return nil
}

// InitRedis initializes the Redis client
func InitRedis() error {
	RedisClient = redis.NewClient(&redis.Options{
		Addr:     config.GetRedisAddr(),
		Password: config.AppConfig.RedisPassword,
		DB:       config.AppConfig.RedisDB,
	})

	// Test connection
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := RedisClient.Ping(ctx).Err(); err != nil {
		return fmt.Errorf("failed to connect to Redis: %w", err)
	}

	log.Println("Redis connected successfully")
	return nil
}

// runMigrations runs database migrations
func runMigrations() error {
	log.Println("Running database migrations...")

	if err := DB.AutoMigrate(
		&models.Room{},
		&models.RoomSchedule{},
	); err != nil {
		return err
	}

	log.Println("Database migrations completed")
	return nil
}

// CloseDB closes database connections
func CloseDB() error {
	if DB != nil {
		sqlDB, err := DB.DB()
		if err != nil {
			return err
		}
		if err := sqlDB.Close(); err != nil {
			return err
		}
		log.Println("PostgreSQL connection closed")
	}

	if RedisClient != nil {
		if err := RedisClient.Close(); err != nil {
			return err
		}
		log.Println("Redis connection closed")
	}

	return nil
}

// HealthCheck checks the health of database connections
func HealthCheck(ctx context.Context) error {
	// Check PostgreSQL
	if DB != nil {
		sqlDB, err := DB.DB()
		if err != nil {
			return fmt.Errorf("failed to get PostgreSQL instance: %w", err)
		}
		if err := sqlDB.PingContext(ctx); err != nil {
			return fmt.Errorf("PostgreSQL health check failed: %w", err)
		}
	}

	// Check Redis
	if RedisClient != nil {
		if err := RedisClient.Ping(ctx).Err(); err != nil {
			return fmt.Errorf("Redis health check failed: %w", err)
		}
	}

	return nil
}
