package repository

import (
	"context"
	"time"

	"github.com/google/uuid"
	"github.com/stev97uce/appointment-service/internal/models"
	"gorm.io/gorm"
)

type AppointmentRepository interface {
	Create(ctx context.Context, appointment *models.Appointment) error
	FindByID(ctx context.Context, id uuid.UUID) (*models.Appointment, error)
	FindAll(ctx context.Context, filters map[string]interface{}, page, pageSize int) ([]models.Appointment, int64, error)
	Update(ctx context.Context, appointment *models.Appointment) error
	Delete(ctx context.Context, id uuid.UUID) error
	CheckOverlap(ctx context.Context, professionalID int, date time.Time, startTime, endTime time.Time, excludeID *uuid.UUID) (bool, error)
	FindByProfessionalAndDateRange(ctx context.Context, professionalID int, startDate, endDate time.Time) ([]models.Appointment, error)
}

type appointmentRepository struct {
	db *gorm.DB
}

func NewAppointmentRepository(db *gorm.DB) AppointmentRepository {
	return &appointmentRepository{db: db}
}

func (r *appointmentRepository) Create(ctx context.Context, appointment *models.Appointment) error {
	return r.db.WithContext(ctx).Create(appointment).Error
}

func (r *appointmentRepository) FindByID(ctx context.Context, id uuid.UUID) (*models.Appointment, error) {
	var appointment models.Appointment
	err := r.db.WithContext(ctx).Where("id = ?", id).First(&appointment).Error
	if err != nil {
		return nil, err
	}
	return &appointment, nil
}

func (r *appointmentRepository) FindAll(ctx context.Context, filters map[string]interface{}, page, pageSize int) ([]models.Appointment, int64, error) {
	var appointments []models.Appointment
	var totalCount int64

	query := r.db.WithContext(ctx).Model(&models.Appointment{})

	// Apply filters
	if patientID, ok := filters["patient_id"]; ok {
		query = query.Where("patient_id = ?", patientID)
	}
	if professionalID, ok := filters["professional_id"]; ok {
		query = query.Where("professional_id = ?", professionalID)
	}
	if status, ok := filters["status"]; ok {
		query = query.Where("status = ?", status)
	}
	if startDate, ok := filters["start_date"]; ok {
		query = query.Where("appointment_date >= ?", startDate)
	}
	if endDate, ok := filters["end_date"]; ok {
		query = query.Where("appointment_date <= ?", endDate)
	}

	// Count total
	if err := query.Count(&totalCount).Error; err != nil {
		return nil, 0, err
	}

	// Paginate
	offset := (page - 1) * pageSize
	err := query.
		Order("appointment_date DESC, start_time DESC").
		Limit(pageSize).
		Offset(offset).
		Find(&appointments).Error

	return appointments, totalCount, err
}

func (r *appointmentRepository) Update(ctx context.Context, appointment *models.Appointment) error {
	return r.db.WithContext(ctx).Save(appointment).Error
}

func (r *appointmentRepository) Delete(ctx context.Context, id uuid.UUID) error {
	return r.db.WithContext(ctx).Delete(&models.Appointment{}, "id = ?", id).Error
}

func (r *appointmentRepository) CheckOverlap(ctx context.Context, professionalID int, date time.Time, startTime, endTime time.Time, excludeID *uuid.UUID) (bool, error) {
	var count int64
	query := r.db.WithContext(ctx).Model(&models.Appointment{}).
		Where("professional_id = ?", professionalID).
		Where("appointment_date = ?", date).
		Where("status NOT IN ?", []models.AppointmentStatus{models.StatusCancelled, models.StatusNoShow}).
		Where("((start_time < ? AND end_time > ?) OR (start_time < ? AND end_time > ?) OR (start_time >= ? AND end_time <= ?))",
			endTime, startTime, endTime, endTime, startTime, endTime)

	if excludeID != nil {
		query = query.Where("id != ?", *excludeID)
	}

	err := query.Count(&count).Error
	return count > 0, err
}

func (r *appointmentRepository) FindByProfessionalAndDateRange(ctx context.Context, professionalID int, startDate, endDate time.Time) ([]models.Appointment, error) {
	var appointments []models.Appointment
	err := r.db.WithContext(ctx).
		Where("professional_id = ?", professionalID).
		Where("appointment_date BETWEEN ? AND ?", startDate, endDate).
		Where("status NOT IN ?", []models.AppointmentStatus{models.StatusCancelled, models.StatusNoShow}).
		Order("appointment_date, start_time").
		Find(&appointments).Error
	return appointments, err
}
