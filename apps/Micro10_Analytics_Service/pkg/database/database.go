package database

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/go-redis/redis/v8"
	"github.com/stev97uce/analytics-service/pkg/config"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var (
	MongoDB     *mongo.Database
	RedisClient *redis.Client
)

func InitMongoDB() error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	clientOptions := options.Client().ApplyURI(config.GetMongoURI())
	
	client, err := mongo.Connect(ctx, clientOptions)
	if err != nil {
		return fmt.Errorf("failed to connect to MongoDB: %w", err)
	}

	if err := client.Ping(ctx, nil); err != nil {
		return fmt.Errorf("failed to ping MongoDB: %w", err)
	}

	MongoDB = client.Database(config.AppConfig.MongoDBDatabase)
	log.Println("MongoDB connected successfully")

	if err := createIndexes(ctx); err != nil {
		log.Printf("Warning: Failed to create indexes: %v", err)
	}

	return nil
}

func InitRedis() error {
	RedisClient = redis.NewClient(&redis.Options{
		Addr:     config.GetRedisAddr(),
		Password: config.AppConfig.RedisPassword,
		DB:       config.AppConfig.RedisDB,
	})

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := RedisClient.Ping(ctx).Err(); err != nil {
		return fmt.Errorf("failed to connect to Redis: %w", err)
	}

	log.Println("Redis connected successfully")
	return nil
}

func createIndexes(ctx context.Context) error {
	metricsCollection := MongoDB.Collection("metrics")
	
	_, err := metricsCollection.Indexes().CreateMany(ctx, []mongo.IndexModel{
		{
			Keys: map[string]interface{}{
				"metric_type": 1,
				"timestamp":   -1,
			},
		},
		{
			Keys: map[string]interface{}{
				"timestamp": -1,
			},
		},
	})
	
	return err
}

func HealthCheck(ctx context.Context) error {
	if err := MongoDB.Client().Ping(ctx, nil); err != nil {
		return fmt.Errorf("MongoDB health check failed: %w", err)
	}

	if err := RedisClient.Ping(ctx).Err(); err != nil {
		return fmt.Errorf("Redis health check failed: %w", err)
	}

	return nil
}

func CloseConnections() {
	if MongoDB != nil {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		if err := MongoDB.Client().Disconnect(ctx); err != nil {
			log.Printf("Error disconnecting MongoDB: %v", err)
		}
	}

	if RedisClient != nil {
		if err := RedisClient.Close(); err != nil {
			log.Printf("Error closing Redis: %v", err)
		}
	}
}
