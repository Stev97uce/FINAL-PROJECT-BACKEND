package models

import (
	"time"

	"github.com/google/uuid"
	"github.com/lib/pq"
	"gorm.io/gorm"
)

// RoomType enum
type RoomType string

const (
	RoomTypeIndividual  RoomType = "consultorio_individual"
	RoomTypeGroup       RoomType = "consultorio_grupal"
	RoomTypeObservation RoomType = "sala_observacion"
	RoomTypeMeeting     RoomType = "sala_reunion"
)

// RoomStatus enum
type RoomStatus string

const (
	RoomStatusAvailable   RoomStatus = "disponible"
	RoomStatusOccupied    RoomStatus = "ocupado"
	RoomStatusMaintenance RoomStatus = "mantenimiento"
	RoomStatusInactive    RoomStatus = "inactivo"
)

// Room represents a physical space/office
type Room struct {
	ID          uuid.UUID      `gorm:"type:uuid;primary_key;default:gen_random_uuid()" json:"id"`
	Name        string         `gorm:"size:100;not null;uniqueIndex" json:"name"`
	RoomNumber  string         `gorm:"size:20;not null;uniqueIndex" json:"room_number"`
	FloorNumber int            `gorm:"not null" json:"floor_number"`
	Building    string         `gorm:"size:50" json:"building"`
	Capacity    int            `gorm:"not null;default:1" json:"capacity"`
	RoomType    RoomType       `gorm:"type:varchar(30);not null" json:"room_type"`
	Status      RoomStatus     `gorm:"type:varchar(20);not null;default:'disponible'" json:"status"`
	Equipment   pq.StringArray `gorm:"type:text[]" json:"equipment"`
	Description string         `gorm:"type:text" json:"description,omitempty"`
	IsActive    bool           `gorm:"not null;default:true;index" json:"is_active"`
	CreatedAt   time.Time      `json:"created_at"`
	UpdatedAt   time.Time      `json:"updated_at"`
	DeletedAt   gorm.DeletedAt `gorm:"index" json:"-"`
}

// TableName specifies the table name for Room
func (Room) TableName() string {
	return "rooms"
}

// BeforeCreate hook to generate UUID
func (r *Room) BeforeCreate(tx *gorm.DB) error {
	if r.ID == uuid.Nil {
		r.ID = uuid.New()
	}
	return nil
}
