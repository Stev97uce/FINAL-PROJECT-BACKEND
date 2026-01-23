package services

import (
	"context"
	"errors"
	"time"

	"github.com/google/uuid"
	"github.com/stev97uce/room-service/internal/models"
	"github.com/stev97uce/room-service/internal/repository"
	"gorm.io/gorm"
)

type ScheduleService interface {
	CreateSchedule(ctx context.Context, req *models.CreateScheduleRequest, userID int) (*models.RoomSchedule, error)
	GetSchedule(ctx context.Context, id uuid.UUID) (*models.RoomSchedule, error)
	ListSchedules(ctx context.Context, query *models.ListSchedulesQuery) (*models.PaginatedSchedulesResponse, error)
	UpdateSchedule(ctx context.Context, id uuid.UUID, req *models.UpdateScheduleRequest) (*models.RoomSchedule, error)
	DeleteSchedule(ctx context.Context, id uuid.UUID) error
	GetRoomSchedules(ctx context.Context, roomID uuid.UUID, startDate, endDate string) ([]models.RoomSchedule, error)
	ReleaseSchedule(ctx context.Context, appointmentID uuid.UUID) error
}

type scheduleService struct {
	scheduleRepo repository.ScheduleRepository
	roomRepo     repository.RoomRepository
}

func NewScheduleService(scheduleRepo repository.ScheduleRepository, roomRepo repository.RoomRepository) ScheduleService {
	return &scheduleService{
		scheduleRepo: scheduleRepo,
		roomRepo:     roomRepo,
	}
}

func (s *scheduleService) CreateSchedule(ctx context.Context, req *models.CreateScheduleRequest, userID int) (*models.RoomSchedule, error) {
	// Verify room exists and is available
	room, err := s.roomRepo.GetByID(ctx, req.RoomID)
	if err != nil {
		return nil, errors.New("room not found")
	}

	if !room.IsActive {
		return nil, errors.New("room is not active")
	}

	// Parse times
	startTime, err := time.Parse(time.RFC3339, req.StartTime)
	if err != nil {
		return nil, errors.New("invalid start_time format, use ISO 8601")
	}

	endTime, err := time.Parse(time.RFC3339, req.EndTime)
	if err != nil {
		return nil, errors.New("invalid end_time format, use ISO 8601")
	}

	if endTime.Before(startTime) || endTime.Equal(startTime) {
		return nil, errors.New("end_time must be after start_time")
	}

	// Check for conflicts
	hasConflict, err := s.scheduleRepo.CheckConflict(ctx, req.RoomID, startTime, endTime, nil)
	if err != nil {
		return nil, err
	}

	if hasConflict {
		return nil, errors.New("time slot is already reserved")
	}

	schedule := &models.RoomSchedule{
		RoomID:        req.RoomID,
		AppointmentID: req.AppointmentID,
		StartTime:     startTime,
		EndTime:       endTime,
		Status:        models.ScheduleStatusReserved,
		ReservedBy:    userID,
		Purpose:       req.Purpose,
		Notes:         req.Notes,
	}

	if err := s.scheduleRepo.Create(ctx, schedule); err != nil {
		return nil, err
	}

	// Update room status to occupied
	if err := s.roomRepo.UpdateStatus(ctx, req.RoomID, models.RoomStatusOccupied); err != nil {
		// Log error but don't fail the schedule creation
	}

	return schedule, nil
}

func (s *scheduleService) GetSchedule(ctx context.Context, id uuid.UUID) (*models.RoomSchedule, error) {
	return s.scheduleRepo.GetByID(ctx, id)
}

func (s *scheduleService) ListSchedules(ctx context.Context, query *models.ListSchedulesQuery) (*models.PaginatedSchedulesResponse, error) {
	schedules, totalCount, err := s.scheduleRepo.List(ctx, query)
	if err != nil {
		return nil, err
	}

	page := query.Page
	if page < 1 {
		page = 1
	}
	pageSize := query.PageSize
	if pageSize < 1 {
		pageSize = 10
	}

	totalPages := int(totalCount) / pageSize
	if int(totalCount)%pageSize != 0 {
		totalPages++
	}

	// Convert to response DTOs
	scheduleResponses := make([]models.ScheduleResponse, len(schedules))
	for i, schedule := range schedules {
		scheduleResponses[i] = models.ScheduleResponse{
			ID:            schedule.ID,
			RoomID:        schedule.RoomID,
			AppointmentID: schedule.AppointmentID,
			StartTime:     schedule.StartTime.Format(time.RFC3339),
			EndTime:       schedule.EndTime.Format(time.RFC3339),
			Status:        schedule.Status,
			ReservedBy:    schedule.ReservedBy,
			Purpose:       schedule.Purpose,
			Notes:         schedule.Notes,
			CreatedAt:     schedule.CreatedAt.Format(time.RFC3339),
			UpdatedAt:     schedule.UpdatedAt.Format(time.RFC3339),
		}
		// Add room data if preloaded
		if schedule.Room.ID != uuid.Nil {
			scheduleResponses[i].Room = &models.RoomResponse{
				ID:          schedule.Room.ID,
				Name:        schedule.Room.Name,
				RoomNumber:  schedule.Room.RoomNumber,
				FloorNumber: schedule.Room.FloorNumber,
				Building:    schedule.Room.Building,
				Capacity:    schedule.Room.Capacity,
				RoomType:    schedule.Room.RoomType,
				Status:      schedule.Room.Status,
				Equipment:   schedule.Room.Equipment,
				Description: schedule.Room.Description,
				IsActive:    schedule.Room.IsActive,
				CreatedAt:   schedule.Room.CreatedAt.Format(time.RFC3339),
				UpdatedAt:   schedule.Room.UpdatedAt.Format(time.RFC3339),
			}
		}
	}

	return &models.PaginatedSchedulesResponse{
		Data:       scheduleResponses,
		TotalCount: totalCount,
		Page:       page,
		PageSize:   pageSize,
		TotalPages: totalPages,
	}, nil
}

func (s *scheduleService) UpdateSchedule(ctx context.Context, id uuid.UUID, req *models.UpdateScheduleRequest) (*models.RoomSchedule, error) {
	schedule, err := s.scheduleRepo.GetByID(ctx, id)
	if err != nil {
		return nil, errors.New("schedule not found")
	}

	// Cannot update completed or cancelled schedules
	if schedule.Status == models.ScheduleStatusCompleted || schedule.Status == models.ScheduleStatusCancelled {
		return nil, errors.New("cannot update completed or cancelled schedule")
	}

	// Update times if provided
	var newStartTime, newEndTime time.Time
	needsConflictCheck := false

	if req.StartTime != nil {
		parsedTime, err := time.Parse(time.RFC3339, *req.StartTime)
		if err != nil {
			return nil, errors.New("invalid start_time format")
		}
		newStartTime = parsedTime
		needsConflictCheck = true
	} else {
		newStartTime = schedule.StartTime
	}

	if req.EndTime != nil {
		parsedTime, err := time.Parse(time.RFC3339, *req.EndTime)
		if err != nil {
			return nil, errors.New("invalid end_time format")
		}
		newEndTime = parsedTime
		needsConflictCheck = true
	} else {
		newEndTime = schedule.EndTime
	}

	if needsConflictCheck {
		if newEndTime.Before(newStartTime) || newEndTime.Equal(newStartTime) {
			return nil, errors.New("end_time must be after start_time")
		}

		// Check conflicts
		hasConflict, err := s.scheduleRepo.CheckConflict(ctx, schedule.RoomID, newStartTime, newEndTime, &schedule.ID)
		if err != nil {
			return nil, err
		}

		if hasConflict {
			return nil, errors.New("time slot is already reserved")
		}

		schedule.StartTime = newStartTime
		schedule.EndTime = newEndTime
	}

	if req.Status != nil {
		schedule.Status = *req.Status

		// If schedule is completed or cancelled, check if we should release the room
		if *req.Status == models.ScheduleStatusCompleted || *req.Status == models.ScheduleStatusCancelled {
			// Check if there are other active schedules for this room
			now := time.Now()
			futureSchedules, _ := s.scheduleRepo.GetRoomSchedules(ctx, schedule.RoomID, now, now.AddDate(0, 0, 1))
			
			// If no active schedules, mark room as available
			if len(futureSchedules) == 0 {
				s.roomRepo.UpdateStatus(ctx, schedule.RoomID, models.RoomStatusAvailable)
			}
		}
	}

	if req.Purpose != nil {
		schedule.Purpose = *req.Purpose
	}

	if req.Notes != nil {
		schedule.Notes = *req.Notes
	}

	if err := s.scheduleRepo.Update(ctx, schedule); err != nil {
		return nil, err
	}

	return schedule, nil
}

func (s *scheduleService) DeleteSchedule(ctx context.Context, id uuid.UUID) error {
	schedule, err := s.scheduleRepo.GetByID(ctx, id)
	if err != nil {
		return errors.New("schedule not found")
	}

	// Check if room should be released
	now := time.Now()
	futureSchedules, _ := s.scheduleRepo.GetRoomSchedules(ctx, schedule.RoomID, now, now.AddDate(0, 0, 1))
	
	if len(futureSchedules) <= 1 { // Only this schedule
		s.roomRepo.UpdateStatus(ctx, schedule.RoomID, models.RoomStatusAvailable)
	}

	return s.scheduleRepo.Delete(ctx, id)
}

func (s *scheduleService) GetRoomSchedules(ctx context.Context, roomID uuid.UUID, startDate, endDate string) ([]models.RoomSchedule, error) {
	start, err := time.Parse("2006-01-02", startDate)
	if err != nil {
		return nil, errors.New("invalid start_date format, use YYYY-MM-DD")
	}

	end, err := time.Parse("2006-01-02", endDate)
	if err != nil {
		return nil, errors.New("invalid end_date format, use YYYY-MM-DD")
	}

	return s.scheduleRepo.GetRoomSchedules(ctx, roomID, start, end.Add(24*time.Hour))
}

func (s *scheduleService) ReleaseSchedule(ctx context.Context, appointmentID uuid.UUID) error {
	schedule, err := s.scheduleRepo.GetByAppointmentID(ctx, appointmentID)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil // No schedule to release
		}
		return err
	}

	// Update status to completed
	if err := s.scheduleRepo.UpdateStatus(ctx, schedule.ID, models.ScheduleStatusCompleted); err != nil {
		return err
	}

	// Check if room should be released
	now := time.Now()
	futureSchedules, _ := s.scheduleRepo.GetRoomSchedules(ctx, schedule.RoomID, now, now.AddDate(0, 0, 1))
	
	if len(futureSchedules) == 0 {
		return s.roomRepo.UpdateStatus(ctx, schedule.RoomID, models.RoomStatusAvailable)
	}

	return nil
}
