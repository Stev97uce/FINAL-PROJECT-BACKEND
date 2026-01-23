package models

import (
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// ScheduleStatus enum
type ScheduleStatus string

const (
	ScheduleStatusReserved  ScheduleStatus = "reserved"
	ScheduleStatusOccupied  ScheduleStatus = "occupied"
	ScheduleStatusCompleted ScheduleStatus = "completed"
	ScheduleStatusCancelled ScheduleStatus = "cancelled"
)

// RoomSchedule represents a reservation or usage of a room
type RoomSchedule struct {
	ID            uuid.UUID       `gorm:"type:uuid;primary_key;default:gen_random_uuid()" json:"id"`
	RoomID        uuid.UUID       `gorm:"type:uuid;not null;index" json:"room_id"`
	Room          *Room           `gorm:"foreignKey:RoomID" json:"room,omitempty"`
	AppointmentID *uuid.UUID      `gorm:"type:uuid;index" json:"appointment_id,omitempty"`
	StartTime     time.Time       `gorm:"not null;index" json:"start_time"`
	EndTime       time.Time       `gorm:"not null;index" json:"end_time"`
	Status        ScheduleStatus  `gorm:"type:varchar(20);not null;default:'reserved'" json:"status"`
	ReservedBy    int             `gorm:"not null;index" json:"reserved_by"` // user_id
	Purpose       string          `gorm:"size:200" json:"purpose,omitempty"`
	Notes         string          `gorm:"type:text" json:"notes,omitempty"`
	CreatedAt     time.Time       `json:"created_at"`
	UpdatedAt     time.Time       `json:"updated_at"`
	DeletedAt     gorm.DeletedAt  `gorm:"index" json:"-"`
}

// TableName specifies the table name for RoomSchedule
func (RoomSchedule) TableName() string {
	return "room_schedules"
}

// BeforeCreate hook to generate UUID
func (rs *RoomSchedule) BeforeCreate(tx *gorm.DB) error {
	if rs.ID == uuid.Nil {
		rs.ID = uuid.New()
	}
	return nil
}
