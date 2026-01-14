package services

import (
	"context"

	"github.com/stev97uce/analytics-service/internal/models"
	"github.com/stev97uce/analytics-service/internal/repository"
)

type DashboardService struct {
	repo *repository.DashboardRepository
}

func NewDashboardService(repo *repository.DashboardRepository) *DashboardService {
	return &DashboardService{repo: repo}
}

func (s *DashboardService) CreateDashboard(ctx context.Context, dashboard *models.Dashboard) error {
	return s.repo.Create(ctx, dashboard)
}

func (s *DashboardService) GetDashboard(ctx context.Context, id string) (*models.Dashboard, error) {
	return s.repo.FindByID(ctx, id)
}

func (s *DashboardService) GetUserDashboards(ctx context.Context, userID int) ([]models.Dashboard, error) {
	return s.repo.FindByUserID(ctx, userID)
}

func (s *DashboardService) UpdateDashboard(ctx context.Context, id string, dashboard *models.Dashboard) error {
	return s.repo.Update(ctx, id, dashboard)
}

func (s *DashboardService) DeleteDashboard(ctx context.Context, id string) error {
	return s.repo.Delete(ctx, id)
}
