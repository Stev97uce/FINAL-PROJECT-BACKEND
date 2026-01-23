package repository

import (
	"context"
	"time"

	"github.com/stev97uce/analytics-service/internal/models"
	"github.com/stev97uce/analytics-service/pkg/database"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type MetricRepository struct{}

func NewMetricRepository() *MetricRepository {
	return &MetricRepository{}
}

func (r *MetricRepository) Create(ctx context.Context, metric *models.Metric) error {
	metric.CreatedAt = time.Now()
	if metric.Timestamp.IsZero() {
		metric.Timestamp = time.Now()
	}

	collection := database.MongoDB.Collection("metrics")
	result, err := collection.InsertOne(ctx, metric)
	if err != nil {
		return err
	}

	metric.ID = result.InsertedID.(primitive.ObjectID)
	return nil
}

func (r *MetricRepository) FindByType(ctx context.Context, metricType models.MetricType, limit int) ([]models.Metric, error) {
	collection := database.MongoDB.Collection("metrics")
	
	filter := bson.M{"metric_type": metricType}
	opts := options.Find().SetSort(bson.D{{Key: "timestamp", Value: -1}})
	
	if limit > 0 {
		opts.SetLimit(int64(limit))
	}

	cursor, err := collection.Find(ctx, filter, opts)
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var metrics []models.Metric
	if err := cursor.All(ctx, &metrics); err != nil {
		return nil, err
	}

	return metrics, nil
}

func (r *MetricRepository) FindByDateRange(ctx context.Context, metricType models.MetricType, startDate, endDate time.Time, limit int) ([]models.Metric, error) {
	collection := database.MongoDB.Collection("metrics")
	
	filter := bson.M{
		"metric_type": metricType,
		"timestamp": bson.M{
			"$gte": startDate,
			"$lte": endDate,
		},
	}
	
	opts := options.Find().SetSort(bson.D{{Key: "timestamp", Value: -1}})
	if limit > 0 {
		opts.SetLimit(int64(limit))
	}

	cursor, err := collection.Find(ctx, filter, opts)
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var metrics []models.Metric
	if err := cursor.All(ctx, &metrics); err != nil {
		return nil, err
	}

	return metrics, nil
}

func (r *MetricRepository) GetLatest(ctx context.Context, metricType models.MetricType) (*models.Metric, error) {
	collection := database.MongoDB.Collection("metrics")
	
	filter := bson.M{"metric_type": metricType}
	opts := options.FindOne().SetSort(bson.D{{Key: "timestamp", Value: -1}})

	var metric models.Metric
	if err := collection.FindOne(ctx, filter, opts).Decode(&metric); err != nil {
		return nil, err
	}

	return &metric, nil
}

func (r *MetricRepository) DeleteOlderThan(ctx context.Context, cutoffDate time.Time) (int64, error) {
	collection := database.MongoDB.Collection("metrics")
	
	filter := bson.M{
		"timestamp": bson.M{
			"$lt": cutoffDate,
		},
	}

	result, err := collection.DeleteMany(ctx, filter)
	if err != nil {
		return 0, err
	}

	return result.DeletedCount, nil
}
