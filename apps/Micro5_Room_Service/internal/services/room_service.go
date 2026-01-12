package services

import (
	"context"
	"errors"
	"time"

	"github.com/google/uuid"
	"github.com/stev97uce/room-service/internal/models"
	"github.com/stev97uce/room-service/internal/repository"
)

type RoomService interface {
	CreateRoom(ctx context.Context, req *models.CreateRoomRequest) (*models.Room, error)
	GetRoom(ctx context.Context, id uuid.UUID) (*models.Room, error)
	ListRooms(ctx context.Context, query *models.ListRoomsQuery) (*models.PaginatedRoomsResponse, error)
	UpdateRoom(ctx context.Context, id uuid.UUID, req *models.UpdateRoomRequest) (*models.Room, error)
	DeleteRoom(ctx context.Context, id uuid.UUID) error
	UpdateRoomStatus(ctx context.Context, id uuid.UUID, status models.RoomStatus) (*models.Room, error)
	FindAvailableRooms(ctx context.Context, query *models.AvailableRoomsQuery) ([]models.Room, error)
}

type roomService struct {
	roomRepo     repository.RoomRepository
	scheduleRepo repository.ScheduleRepository
}

func NewRoomService(roomRepo repository.RoomRepository, scheduleRepo repository.ScheduleRepository) RoomService {
	return &roomService{
		roomRepo:     roomRepo,
		scheduleRepo: scheduleRepo,
	}
}

func (s *roomService) CreateRoom(ctx context.Context, req *models.CreateRoomRequest) (*models.Room, error) {
	// Check if room number already exists
	existing, err := s.roomRepo.GetByRoomNumber(ctx, req.RoomNumber)
	if err == nil && existing != nil {
		return nil, errors.New("room number already exists")
	}

	room := &models.Room{
		Name:        req.Name,
		RoomNumber:  req.RoomNumber,
		FloorNumber: req.FloorNumber,
		Building:    req.Building,
		Capacity:    req.Capacity,
		RoomType:    req.RoomType,
		Status:      models.RoomStatusAvailable,
		Equipment:   req.Equipment,
		Description: req.Description,
		IsActive:    true,
	}

	if err := s.roomRepo.Create(ctx, room); err != nil {
		return nil, err
	}

	return room, nil
}

func (s *roomService) GetRoom(ctx context.Context, id uuid.UUID) (*models.Room, error) {
	return s.roomRepo.GetByID(ctx, id)
}

func (s *roomService) ListRooms(ctx context.Context, query *models.ListRoomsQuery) (*models.PaginatedRoomsResponse, error) {
	rooms, totalCount, err := s.roomRepo.List(ctx, query)
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
	roomResponses := make([]models.RoomResponse, len(rooms))
	for i, room := range rooms {
		roomResponses[i] = models.RoomResponse{
			ID:          room.ID,
			Name:        room.Name,
			RoomNumber:  room.RoomNumber,
			FloorNumber: room.FloorNumber,
			Building:    room.Building,
			Capacity:    room.Capacity,
			RoomType:    room.RoomType,
			Status:      room.Status,
			Equipment:   room.Equipment,
			Description: room.Description,
			IsActive:    room.IsActive,
			CreatedAt:   room.CreatedAt.Format(time.RFC3339),
			UpdatedAt:   room.UpdatedAt.Format(time.RFC3339),
		}
	}

	return &models.PaginatedRoomsResponse{
		Data:       roomResponses,
		TotalCount: totalCount,
		Page:       page,
		PageSize:   pageSize,
		TotalPages: totalPages,
	}, nil
}

func (s *roomService) UpdateRoom(ctx context.Context, id uuid.UUID, req *models.UpdateRoomRequest) (*models.Room, error) {
	room, err := s.roomRepo.GetByID(ctx, id)
	if err != nil {
		return nil, errors.New("room not found")
	}

	// Check if room number is being changed and if it already exists
	if req.RoomNumber != nil && *req.RoomNumber != room.RoomNumber {
		existing, err := s.roomRepo.GetByRoomNumber(ctx, *req.RoomNumber)
		if err == nil && existing != nil && existing.ID != id {
			return nil, errors.New("room number already exists")
		}
	}

	// Update fields
	if req.Name != nil {
		room.Name = *req.Name
	}
	if req.RoomNumber != nil {
		room.RoomNumber = *req.RoomNumber
	}
	if req.FloorNumber != nil {
		room.FloorNumber = *req.FloorNumber
	}
	if req.Building != nil {
		room.Building = *req.Building
	}
	if req.Capacity != nil {
		room.Capacity = *req.Capacity
	}
	if req.RoomType != nil {
		room.RoomType = *req.RoomType
	}
	if req.Equipment != nil {
		room.Equipment = req.Equipment
	}
	if req.Description != nil {
		room.Description = *req.Description
	}
	if req.IsActive != nil {
		room.IsActive = *req.IsActive
	}

	if err := s.roomRepo.Update(ctx, room); err != nil {
		return nil, err
	}

	return room, nil
}

func (s *roomService) DeleteRoom(ctx context.Context, id uuid.UUID) error {
	room, err := s.roomRepo.GetByID(ctx, id)
	if err != nil {
		return errors.New("room not found")
	}

	// Check if room has future schedules
	now := time.Now()
	futureEnd := now.AddDate(1, 0, 0) // Check next year
	schedules, err := s.scheduleRepo.GetRoomSchedules(ctx, room.ID, now, futureEnd)
	if err != nil {
		return err
	}

	if len(schedules) > 0 {
		return errors.New("cannot delete room with future schedules")
	}

	return s.roomRepo.Delete(ctx, id)
}

func (s *roomService) UpdateRoomStatus(ctx context.Context, id uuid.UUID, status models.RoomStatus) (*models.Room, error) {
	room, err := s.roomRepo.GetByID(ctx, id)
	if err != nil {
		return nil, errors.New("room not found")
	}

	if err := s.roomRepo.UpdateStatus(ctx, id, status); err != nil {
		return nil, err
	}

	room.Status = status
	return room, nil
}

func (s *roomService) FindAvailableRooms(ctx context.Context, query *models.AvailableRoomsQuery) ([]models.Room, error) {
	// Parse times
	startTime, err := time.Parse(time.RFC3339, query.StartTime)
	if err != nil {
		return nil, errors.New("invalid start_time format, use ISO 8601")
	}

	endTime, err := time.Parse(time.RFC3339, query.EndTime)
	if err != nil {
		return nil, errors.New("invalid end_time format, use ISO 8601")
	}

	if endTime.Before(startTime) || endTime.Equal(startTime) {
		return nil, errors.New("end_time must be after start_time")
	}

	// Get all rooms matching criteria
	rooms, err := s.roomRepo.FindAvailable(ctx, query)
	if err != nil {
		return nil, err
	}

	// Filter out rooms with conflicts
	var availableRooms []models.Room
	for _, room := range rooms {
		hasConflict, err := s.scheduleRepo.CheckConflict(ctx, room.ID, startTime, endTime, nil)
		if err != nil {
			continue
		}

		if !hasConflict {
			availableRooms = append(availableRooms, room)
		}
	}

	return availableRooms, nil
}
