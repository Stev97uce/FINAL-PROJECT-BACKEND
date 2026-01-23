package services

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/stev97uce/analytics-service/internal/models"
	"github.com/stev97uce/analytics-service/internal/repository"
	"github.com/stev97uce/analytics-service/pkg/database"
)

type MetricService struct {
	repo *repository.MetricRepository
}

func NewMetricService(repo *repository.MetricRepository) *MetricService {
	return &MetricService{repo: repo}
}

func (s *MetricService) CreateMetric(ctx context.Context, metric *models.Metric) error {
	return s.repo.Create(ctx, metric)
}

func (s *MetricService) GetMetricsByType(ctx context.Context, metricType models.MetricType, limit int) ([]models.Metric, error) {
	cacheKey := fmt.Sprintf("metrics:%s:latest:%d", metricType, limit)
	
	cached, err := database.RedisClient.Get(ctx, cacheKey).Result()
	if err == nil {
		var metrics []models.Metric
		if err := json.Unmarshal([]byte(cached), &metrics); err == nil {
			log.Printf("Cache hit for metrics: %s", metricType)
			return metrics, nil
		}
	}

	metrics, err := s.repo.FindByType(ctx, metricType, limit)
	if err != nil {
		return nil, err
	}

	if data, err := json.Marshal(metrics); err == nil {
		database.RedisClient.Set(ctx, cacheKey, data, 5*time.Minute)
	}

	return metrics, nil
}

func (s *MetricService) GetMetricsByDateRange(ctx context.Context, metricType models.MetricType, startDate, endDate time.Time, limit int) ([]models.Metric, error) {
	return s.repo.FindByDateRange(ctx, metricType, startDate, endDate, limit)
}

func (s *MetricService) GetLatestMetric(ctx context.Context, metricType models.MetricType) (*models.Metric, error) {
	cacheKey := fmt.Sprintf("metrics:%s:current", metricType)
	
	cached, err := database.RedisClient.Get(ctx, cacheKey).Result()
	if err == nil {
		var metric models.Metric
		if err := json.Unmarshal([]byte(cached), &metric); err == nil {
			return &metric, nil
		}
	}

	metric, err := s.repo.GetLatest(ctx, metricType)
	if err != nil {
		return nil, err
	}

	if data, err := json.Marshal(metric); err == nil {
		database.RedisClient.Set(ctx, cacheKey, data, 2*time.Minute)
	}

	return metric, nil
}

func (s *MetricService) GetDashboardSummary(ctx context.Context) (*models.DashboardSummary, error) {
	cacheKey := "dashboard:summary"
	
	cached, err := database.RedisClient.Get(ctx, cacheKey).Result()
	if err == nil {
		var summary models.DashboardSummary
		if err := json.Unmarshal([]byte(cached), &summary); err == nil {
			return &summary, nil
		}
	}

	summary := &models.DashboardSummary{
		TotalAppointments: 0,
		TotalUsers:        0,
		TotalPatients:     0,
		TotalSessions:     0,
		RoomUtilization:   0.0,
		AppointmentRate:   0.0,
		ActiveUsers:       0,
		CompletionRate:    0.0,
	}

	if appointmentMetric, err := s.repo.GetLatest(ctx, models.MetricTypeAppointmentStats); err == nil {
		if total, ok := appointmentMetric.Data["total"].(int); ok {
			summary.TotalAppointments = total
		}
		if completed, ok := appointmentMetric.Data["completed"].(int); ok {
			if summary.TotalAppointments > 0 {
				summary.CompletionRate = float64(completed) / float64(summary.TotalAppointments) * 100
			}
		}
	}

	if userMetric, err := s.repo.GetLatest(ctx, models.MetricTypeUserActivity); err == nil {
		if total, ok := userMetric.Data["total_users"].(int); ok {
			summary.TotalUsers = total
		}
		if active, ok := userMetric.Data["active_users"].(int); ok {
			summary.ActiveUsers = active
		}
	}

	if roomMetric, err := s.repo.GetLatest(ctx, models.MetricTypeRoomUtilization); err == nil {
		if utilization, ok := roomMetric.Data["utilization"].(float64); ok {
			summary.RoomUtilization = utilization
		}
	}

	if sessionMetric, err := s.repo.GetLatest(ctx, models.MetricTypeSessionStats); err == nil {
		if total, ok := sessionMetric.Data["total"].(int); ok {
			summary.TotalSessions = total
		}
	}

	if data, err := json.Marshal(summary); err == nil {
		database.RedisClient.Set(ctx, cacheKey, data, 3*time.Minute)
	}

	return summary, nil
}

func (s *MetricService) CleanupOldMetrics(ctx context.Context, daysToKeep int) (int64, error) {
	cutoffDate := time.Now().AddDate(0, 0, -daysToKeep)
	return s.repo.DeleteOlderThan(ctx, cutoffDate)
}
