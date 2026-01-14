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

type DashboardRepository struct{}

func NewDashboardRepository() *DashboardRepository {
	return &DashboardRepository{}
}

func (r *DashboardRepository) Create(ctx context.Context, dashboard *models.Dashboard) error {
	dashboard.CreatedAt = time.Now()
	dashboard.UpdatedAt = time.Now()

	collection := database.MongoDB.Collection("dashboards")
	result, err := collection.InsertOne(ctx, dashboard)
	if err != nil {
		return err
	}

	dashboard.ID = result.InsertedID.(primitive.ObjectID)
	return nil
}

func (r *DashboardRepository) FindByID(ctx context.Context, id string) (*models.Dashboard, error) {
	collection := database.MongoDB.Collection("dashboards")
	
	objID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return nil, err
	}

	var dashboard models.Dashboard
	if err := collection.FindOne(ctx, bson.M{"_id": objID}).Decode(&dashboard); err != nil {
		return nil, err
	}

	return &dashboard, nil
}

func (r *DashboardRepository) FindByUserID(ctx context.Context, userID int) ([]models.Dashboard, error) {
	collection := database.MongoDB.Collection("dashboards")
	
	filter := bson.M{
		"$or": []bson.M{
			{"user_id": userID},
			{"is_public": true},
		},
	}

	cursor, err := collection.Find(ctx, filter, options.Find().SetSort(bson.D{{Key: "created_at", Value: -1}}))
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var dashboards []models.Dashboard
	if err := cursor.All(ctx, &dashboards); err != nil {
		return nil, err
	}

	return dashboards, nil
}

func (r *DashboardRepository) Update(ctx context.Context, id string, dashboard *models.Dashboard) error {
	collection := database.MongoDB.Collection("dashboards")
	
	objID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return err
	}

	dashboard.UpdatedAt = time.Now()
	
	update := bson.M{
		"$set": bson.M{
			"name":        dashboard.Name,
			"description": dashboard.Description,
			"widgets":     dashboard.Widgets,
			"is_public":   dashboard.IsPublic,
			"updated_at":  dashboard.UpdatedAt,
		},
	}

	_, err = collection.UpdateOne(ctx, bson.M{"_id": objID}, update)
	return err
}

func (r *DashboardRepository) Delete(ctx context.Context, id string) error {
	collection := database.MongoDB.Collection("dashboards")
	
	objID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return err
	}

	_, err = collection.DeleteOne(ctx, bson.M{"_id": objID})
	return err
}
