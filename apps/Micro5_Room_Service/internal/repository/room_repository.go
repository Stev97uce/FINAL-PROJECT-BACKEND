package repository

import (
	"context"

	"github.com/google/uuid"
	"github.com/stev97uce/room-service/internal/models"
	"gorm.io/gorm"
)

type RoomRepository interface {
	Create(ctx context.Context, room *models.Room) error
	GetByID(ctx context.Context, id uuid.UUID) (*models.Room, error)
	GetByRoomNumber(ctx context.Context, roomNumber string) (*models.Room, error)
	List(ctx context.Context, query *models.ListRoomsQuery) ([]models.Room, int64, error)
	Update(ctx context.Context, room *models.Room) error
	Delete(ctx context.Context, id uuid.UUID) error
	UpdateStatus(ctx context.Context, id uuid.UUID, status models.RoomStatus) error
	FindAvailable(ctx context.Context, query *models.AvailableRoomsQuery) ([]models.Room, error)
}

type roomRepository struct {
	db *gorm.DB
}

func NewRoomRepository(db *gorm.DB) RoomRepository {
	return &roomRepository{db: db}
}

func (r *roomRepository) Create(ctx context.Context, room *models.Room) error {
	return r.db.WithContext(ctx).Create(room).Error
}

func (r *roomRepository) GetByID(ctx context.Context, id uuid.UUID) (*models.Room, error) {
	var room models.Room
	err := r.db.WithContext(ctx).Where("id = ?", id).First(&room).Error
	if err != nil {
		return nil, err
	}
	return &room, nil
}

func (r *roomRepository) GetByRoomNumber(ctx context.Context, roomNumber string) (*models.Room, error) {
	var room models.Room
	err := r.db.WithContext(ctx).Where("room_number = ?", roomNumber).First(&room).Error
	if err != nil {
		return nil, err
	}
	return &room, nil
}

func (r *roomRepository) List(ctx context.Context, query *models.ListRoomsQuery) ([]models.Room, int64, error) {
	var rooms []models.Room
	var totalCount int64

	db := r.db.WithContext(ctx).Model(&models.Room{})

	// Apply filters
	if query.RoomType != "" {
		db = db.Where("room_type = ?", query.RoomType)
	}
	if query.Status != "" {
		db = db.Where("status = ?", query.Status)
	}
	if query.Building != "" {
		db = db.Where("building = ?", query.Building)
	}
	if query.IsActive != nil {
		db = db.Where("is_active = ?", *query.IsActive)
	}
	if query.MinCapacity > 0 {
		db = db.Where("capacity >= ?", query.MinCapacity)
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
	if err := db.Offset(offset).Limit(pageSize).Order("created_at DESC").Find(&rooms).Error; err != nil {
		return nil, 0, err
	}

	return rooms, totalCount, nil
}

func (r *roomRepository) Update(ctx context.Context, room *models.Room) error {
	return r.db.WithContext(ctx).Save(room).Error
}

func (r *roomRepository) Delete(ctx context.Context, id uuid.UUID) error {
	return r.db.WithContext(ctx).Delete(&models.Room{}, "id = ?", id).Error
}

func (r *roomRepository) UpdateStatus(ctx context.Context, id uuid.UUID, status models.RoomStatus) error {
	return r.db.WithContext(ctx).Model(&models.Room{}).Where("id = ?", id).Update("status", status).Error
}

func (r *roomRepository) FindAvailable(ctx context.Context, query *models.AvailableRoomsQuery) ([]models.Room, error) {
	var rooms []models.Room

	db := r.db.WithContext(ctx).Model(&models.Room{}).
		Where("is_active = ?", true).
		Where("status = ?", models.RoomStatusAvailable)

	// Apply filters
	if query.RoomType != "" {
		db = db.Where("room_type = ?", query.RoomType)
	}
	if query.Building != "" {
		db = db.Where("building = ?", query.Building)
	}
	if query.MinCapacity > 0 {
		db = db.Where("capacity >= ?", query.MinCapacity)
	}

	if err := db.Order("floor_number, room_number").Find(&rooms).Error; err != nil {
		return nil, err
	}

	return rooms, nil
}
