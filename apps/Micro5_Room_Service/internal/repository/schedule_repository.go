package repository

import (
	"context"
	"time"

	"github.com/google/uuid"
	"github.com/stev97uce/room-service/internal/models"
	"gorm.io/gorm"
)

type ScheduleRepository interface {
	Create(ctx context.Context, schedule *models.RoomSchedule) error
	GetByID(ctx context.Context, id uuid.UUID) (*models.RoomSchedule, error)
	List(ctx context.Context, query *models.ListSchedulesQuery) ([]models.RoomSchedule, int64, error)
	Update(ctx context.Context, schedule *models.RoomSchedule) error
	Delete(ctx context.Context, id uuid.UUID) error
	CheckConflict(ctx context.Context, roomID uuid.UUID, startTime, endTime time.Time, excludeID *uuid.UUID) (bool, error)
	GetByAppointmentID(ctx context.Context, appointmentID uuid.UUID) (*models.RoomSchedule, error)
	UpdateStatus(ctx context.Context, id uuid.UUID, status models.ScheduleStatus) error
	GetRoomSchedules(ctx context.Context, roomID uuid.UUID, startDate, endDate time.Time) ([]models.RoomSchedule, error)
}

type scheduleRepository struct {
	db *gorm.DB
}

func NewScheduleRepository(db *gorm.DB) ScheduleRepository {
	return &scheduleRepository{db: db}
}

func (r *scheduleRepository) Create(ctx context.Context, schedule *models.RoomSchedule) error {
	return r.db.WithContext(ctx).Create(schedule).Error
}

func (r *scheduleRepository) GetByID(ctx context.Context, id uuid.UUID) (*models.RoomSchedule, error) {
	var schedule models.RoomSchedule
	err := r.db.WithContext(ctx).Preload("Room").Where("id = ?", id).First(&schedule).Error
	if err != nil {
		return nil, err
	}
	return &schedule, nil
}

func (r *scheduleRepository) List(ctx context.Context, query *models.ListSchedulesQuery) ([]models.RoomSchedule, int64, error) {
	var schedules []models.RoomSchedule
	var totalCount int64

	db := r.db.WithContext(ctx).Model(&models.RoomSchedule{})

	// Apply filters
	if query.RoomID != nil {
		db = db.Where("room_id = ?", *query.RoomID)
	}
	if query.Status != nil {
		db = db.Where("status = ?", *query.Status)
	}
	if query.StartDate != "" {
		startDate, _ := time.Parse("2006-01-02", query.StartDate)
		db = db.Where("start_time >= ?", startDate)
	}
	if query.EndDate != "" {
		endDate, _ := time.Parse("2006-01-02", query.EndDate)
		db = db.Where("end_time <= ?", endDate.Add(24*time.Hour))
	}

	// Count total
	if err := db.Count(&totalCount).Error; err != nil {
		return nil, 0, err
	}

	// Apply pagination
	page := query.Page
	if page < 1 {
		page = 1
	}
	pageSize := query.PageSize
	if pageSize < 1 {
		pageSize = 10
	}

	offset := (page - 1) * pageSize
	if err := db.Preload("Room").Offset(offset).Limit(pageSize).Order("start_time DESC").Find(&schedules).Error; err != nil {
		return nil, 0, err
	}

	return schedules, totalCount, nil
}

func (r *scheduleRepository) Update(ctx context.Context, schedule *models.RoomSchedule) error {
	return r.db.WithContext(ctx).Save(schedule).Error
}

func (r *scheduleRepository) Delete(ctx context.Context, id uuid.UUID) error {
	return r.db.WithContext(ctx).Delete(&models.RoomSchedule{}, "id = ?", id).Error
}

func (r *scheduleRepository) CheckConflict(ctx context.Context, roomID uuid.UUID, startTime, endTime time.Time, excludeID *uuid.UUID) (bool, error) {
	var count int64
	db := r.db.WithContext(ctx).Model(&models.RoomSchedule{}).
		Where("room_id = ?", roomID).
		Where("status NOT IN ?", []models.ScheduleStatus{models.ScheduleStatusCancelled, models.ScheduleStatusCompleted}).
		Where("(start_time < ? AND end_time > ?)", endTime, startTime)

	if excludeID != nil {
		db = db.Where("id != ?", *excludeID)
	}

	if err := db.Count(&count).Error; err != nil {
		return false, err
	}

	return count > 0, nil
}

func (r *scheduleRepository) GetByAppointmentID(ctx context.Context, appointmentID uuid.UUID) (*models.RoomSchedule, error) {
	var schedule models.RoomSchedule
	err := r.db.WithContext(ctx).Preload("Room").Where("appointment_id = ?", appointmentID).First(&schedule).Error
	if err != nil {
		return nil, err
	}
	return &schedule, nil
}

func (r *scheduleRepository) UpdateStatus(ctx context.Context, id uuid.UUID, status models.ScheduleStatus) error {
	return r.db.WithContext(ctx).Model(&models.RoomSchedule{}).Where("id = ?", id).Update("status", status).Error
}

func (r *scheduleRepository) GetRoomSchedules(ctx context.Context, roomID uuid.UUID, startDate, endDate time.Time) ([]models.RoomSchedule, error) {
	var schedules []models.RoomSchedule
	err := r.db.WithContext(ctx).
		Where("room_id = ?", roomID).
		Where("start_time >= ? AND end_time <= ?", startDate, endDate).
		Where("status NOT IN ?", []models.ScheduleStatus{models.ScheduleStatusCancelled}).
		Order("start_time").
		Find(&schedules).Error

	if err != nil {
		return nil, err
	}
	return schedules, nil
}
