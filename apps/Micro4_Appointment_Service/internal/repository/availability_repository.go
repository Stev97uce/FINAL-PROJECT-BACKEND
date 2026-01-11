package repository

import (
	"context"
	"time"

	"github.com/google/uuid"
	"github.com/stev97uce/appointment-service/internal/models"
	"gorm.io/gorm"
)

type AvailabilityRepository interface {
	Create(ctx context.Context, availability *models.Availability) error
	FindByID(ctx context.Context, id uuid.UUID) (*models.Availability, error)
	FindByProfessional(ctx context.Context, professionalID int) ([]models.Availability, error)
	FindActiveByProfessionalAndDay(ctx context.Context, professionalID int, dayOfWeek int, date time.Time) ([]models.Availability, error)
	Update(ctx context.Context, availability *models.Availability) error
	Delete(ctx context.Context, id uuid.UUID) error
}

type availabilityRepository struct {
	db *gorm.DB
}

func NewAvailabilityRepository(db *gorm.DB) AvailabilityRepository {
	return &availabilityRepository{db: db}
}

func (r *availabilityRepository) Create(ctx context.Context, availability *models.Availability) error {
	return r.db.WithContext(ctx).Create(availability).Error
}

func (r *availabilityRepository) FindByID(ctx context.Context, id uuid.UUID) (*models.Availability, error) {
	var availability models.Availability
	err := r.db.WithContext(ctx).Where("id = ?", id).First(&availability).Error
	if err != nil {
		return nil, err
	}
	return &availability, nil
}

func (r *availabilityRepository) FindByProfessional(ctx context.Context, professionalID int) ([]models.Availability, error) {
	var availabilities []models.Availability
	err := r.db.WithContext(ctx).
		Where("professional_id = ?", professionalID).
		Order("day_of_week, start_time").
		Find(&availabilities).Error
	return availabilities, err
}

func (r *availabilityRepository) FindActiveByProfessionalAndDay(ctx context.Context, professionalID int, dayOfWeek int, date time.Time) ([]models.Availability, error) {
	var availabilities []models.Availability
	err := r.db.WithContext(ctx).
		Where("professional_id = ?", professionalID).
		Where("day_of_week = ?", dayOfWeek).
		Where("is_active = ?", true).
		Where("effective_from <= ?", date).
		Where("effective_until IS NULL OR effective_until >= ?", date).
		Order("start_time").
		Find(&availabilities).Error
	return availabilities, err
}

func (r *availabilityRepository) Update(ctx context.Context, availability *models.Availability) error {
	return r.db.WithContext(ctx).Save(availability).Error
}

func (r *availabilityRepository) Delete(ctx context.Context, id uuid.UUID) error {
	return r.db.WithContext(ctx).Delete(&models.Availability{}, "id = ?", id).Error
}
