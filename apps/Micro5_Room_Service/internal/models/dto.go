package models

import (
	"github.com/google/uuid"
)

// CreateRoomRequest represents the request body for creating a room
type CreateRoomRequest struct {
	Name        string   `json:"name" binding:"required,min=3,max=100"`
	RoomNumber  string   `json:"room_number" binding:"required,min=1,max=20"`
	FloorNumber int      `json:"floor_number" binding:"required,min=0"`
	Building    string   `json:"building" binding:"max=50"`
	Capacity    int      `json:"capacity" binding:"required,min=1,max=50"`
	RoomType    RoomType `json:"room_type" binding:"required,oneof=consultorio_individual consultorio_grupal sala_observacion sala_reunion"`
	Equipment   []string `json:"equipment"`
	Description string   `json:"description"`
}

// UpdateRoomRequest represents the request body for updating a room
type UpdateRoomRequest struct {
	Name        *string    `json:"name" binding:"omitempty,min=3,max=100"`
	RoomNumber  *string    `json:"room_number" binding:"omitempty,min=1,max=20"`
	FloorNumber *int       `json:"floor_number" binding:"omitempty,min=0"`
	Building    *string    `json:"building" binding:"omitempty,max=50"`
	Capacity    *int       `json:"capacity" binding:"omitempty,min=1,max=50"`
	RoomType    *RoomType  `json:"room_type" binding:"omitempty,oneof=consultorio_individual consultorio_grupal sala_observacion sala_reunion"`
	Equipment   []string   `json:"equipment"`
	Description *string    `json:"description"`
	IsActive    *bool      `json:"is_active"`
}

// UpdateRoomStatusRequest represents the request body for updating room status
type UpdateRoomStatusRequest struct {
	Status RoomStatus `json:"status" binding:"required,oneof=disponible ocupado mantenimiento inactivo"`
}

// ListRoomsQuery represents query parameters for listing rooms
type ListRoomsQuery struct {
	Page       int        `form:"page" binding:"omitempty,min=1"`
	PageSize   int        `form:"page_size" binding:"omitempty,min=1,max=100"`
	RoomType   RoomType   `form:"room_type" binding:"omitempty"`
	Status     RoomStatus `form:"status" binding:"omitempty"`
	Building   string     `form:"building" binding:"omitempty"`
	IsActive   *bool      `form:"is_active" binding:"omitempty"`
	MinCapacity int       `form:"min_capacity" binding:"omitempty,min=1"`
}

// RoomResponse represents the response body for a room
type RoomResponse struct {
	ID          uuid.UUID  `json:"id"`
	Name        string     `json:"name"`
	RoomNumber  string     `json:"room_number"`
	FloorNumber int        `json:"floor_number"`
	Building    string     `json:"building"`
	Capacity    int        `json:"capacity"`
	RoomType    RoomType   `json:"room_type"`
	Status      RoomStatus `json:"status"`
	Equipment   []string   `json:"equipment"`
	Description string     `json:"description,omitempty"`
	IsActive    bool       `json:"is_active"`
	CreatedAt   string     `json:"created_at"`
	UpdatedAt   string     `json:"updated_at"`
}

// CreateScheduleRequest represents the request body for creating a schedule
type CreateScheduleRequest struct {
	RoomID        uuid.UUID  `json:"room_id" binding:"required"`
	AppointmentID *uuid.UUID `json:"appointment_id"`
	StartTime     string     `json:"start_time" binding:"required"` // ISO 8601 format
	EndTime       string     `json:"end_time" binding:"required"`
	Purpose       string     `json:"purpose" binding:"max=200"`
	Notes         string     `json:"notes"`
}

// UpdateScheduleRequest represents the request body for updating a schedule
type UpdateScheduleRequest struct {
	StartTime *string         `json:"start_time"`
	EndTime   *string         `json:"end_time"`
	Status    *ScheduleStatus `json:"status" binding:"omitempty,oneof=reserved occupied completed cancelled"`
	Purpose   *string         `json:"purpose" binding:"omitempty,max=200"`
	Notes     *string         `json:"notes"`
}

// ScheduleResponse represents the response body for a schedule
type ScheduleResponse struct {
	ID            uuid.UUID       `json:"id"`
	RoomID        uuid.UUID       `json:"room_id"`
	Room          *RoomResponse   `json:"room,omitempty"`
	AppointmentID *uuid.UUID      `json:"appointment_id,omitempty"`
	StartTime     string          `json:"start_time"`
	EndTime       string          `json:"end_time"`
	Status        ScheduleStatus  `json:"status"`
	ReservedBy    int             `json:"reserved_by"`
	Purpose       string          `json:"purpose,omitempty"`
	Notes         string          `json:"notes,omitempty"`
	CreatedAt     string          `json:"created_at"`
	UpdatedAt     string          `json:"updated_at"`
}

// ListSchedulesQuery represents query parameters for listing schedules
type ListSchedulesQuery struct {
	Page      int             `form:"page" binding:"omitempty,min=1"`
	PageSize  int             `form:"page_size" binding:"omitempty,min=1,max=100"`
	RoomID    *uuid.UUID      `form:"room_id" binding:"omitempty"`
	Status    *ScheduleStatus `form:"status" binding:"omitempty"`
	StartDate string          `form:"start_date" binding:"omitempty"` // YYYY-MM-DD
	EndDate   string          `form:"end_date" binding:"omitempty"`
}

// AvailableRoomsQuery represents query parameters for finding available rooms
type AvailableRoomsQuery struct {
	StartTime   string   `form:"start_time" binding:"required"` // ISO 8601
	EndTime     string   `form:"end_time" binding:"required"`
	RoomType    RoomType `form:"room_type" binding:"omitempty"`
	MinCapacity int      `form:"min_capacity" binding:"omitempty,min=1"`
	Building    string   `form:"building" binding:"omitempty"`
}

// PaginatedRoomsResponse represents paginated rooms response
type PaginatedRoomsResponse struct {
	Data       []RoomResponse `json:"data"`
	TotalCount int64          `json:"total_count"`
	Page       int            `json:"page"`
	PageSize   int            `json:"page_size"`
	TotalPages int            `json:"total_pages"`
}

// PaginatedSchedulesResponse represents paginated schedules response
type PaginatedSchedulesResponse struct {
	Data       []ScheduleResponse `json:"data"`
	TotalCount int64              `json:"total_count"`
	Page       int                `json:"page"`
	PageSize   int                `json:"page_size"`
	TotalPages int                `json:"total_pages"`
}
