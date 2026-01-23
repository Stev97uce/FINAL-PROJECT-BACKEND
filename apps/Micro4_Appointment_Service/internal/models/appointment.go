package models

import (
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

type AppointmentStatus string

const (
	StatusScheduled  AppointmentStatus = "scheduled"
	StatusConfirmed  AppointmentStatus = "confirmed"
	StatusInProgress AppointmentStatus = "in_progress"
	StatusCompleted  AppointmentStatus = "completed"
	StatusCancelled  AppointmentStatus = "cancelled"
	StatusNoShow     AppointmentStatus = "no_show"
)

type AppointmentType string

const (
	TypeFirstTime  AppointmentType = "primera_vez"
	TypeFollowUp   AppointmentType = "seguimiento"
	TypeEvaluation AppointmentType = "evaluacion"
	TypeClosure    AppointmentType = "cierre"
)

type Modality string

const (
	ModalityInPerson  Modality = "presencial"
	ModalityVirtual   Modality = "virtual"
	ModalityTelephone Modality = "telefonica"
)

type Appointment struct {
	ID                 uuid.UUID         `gorm:"type:uuid;primary_key;default:gen_random_uuid()" json:"id"`
	PatientID          int               `gorm:"not null;index" json:"patient_id"`
	ProfessionalID     int               `gorm:"not null;index" json:"professional_id"`
	RoomID             *int              `gorm:"index" json:"room_id,omitempty"`
	AppointmentDate    time.Time         `gorm:"type:date;not null;index" json:"appointment_date"`
	StartTime          time.Time         `gorm:"type:time;not null" json:"start_time"`
	EndTime            time.Time         `gorm:"type:time;not null" json:"end_time"`
	DurationMinutes    int               `gorm:"not null;default:50" json:"duration_minutes"`
	Status             AppointmentStatus `gorm:"type:varchar(20);not null;default:'scheduled';index" json:"status"`
	AppointmentType    AppointmentType   `gorm:"type:varchar(20);not null;default:'primera_vez'" json:"appointment_type"`
	Modality           Modality          `gorm:"type:varchar(20);not null;default:'presencial'" json:"modality"`
	Notes              string            `gorm:"type:text" json:"notes,omitempty"`
	CancellationReason string            `gorm:"type:text" json:"cancellation_reason,omitempty"`
	CreatedBy          int               `gorm:"not null" json:"created_by"`
	CreatedAt          time.Time         `gorm:"autoCreateTime" json:"created_at"`
	UpdatedAt          time.Time         `gorm:"autoUpdateTime" json:"updated_at"`
}

func (Appointment) TableName() string {
	return "appointments"
}

func (a *Appointment) BeforeCreate(tx *gorm.DB) error {
	if a.ID == uuid.Nil {
		a.ID = uuid.New()
	}
	return nil
}

type Availability struct {
	ID             uuid.UUID `gorm:"type:uuid;primary_key;default:gen_random_uuid()" json:"id"`
	ProfessionalID int       `gorm:"not null;index" json:"professional_id"`
	DayOfWeek      int       `gorm:"not null;check:day_of_week >= 0 AND day_of_week <= 6" json:"day_of_week"`
	StartTime      time.Time `gorm:"type:time;not null" json:"start_time"`
	EndTime        time.Time `gorm:"type:time;not null" json:"end_time"`
	IsActive       bool      `gorm:"not null;default:true;index" json:"is_active"`
	EffectiveFrom  time.Time `gorm:"type:date;not null" json:"effective_from"`
	EffectiveUntil *time.Time `gorm:"type:date" json:"effective_until,omitempty"`
	CreatedAt      time.Time `gorm:"autoCreateTime" json:"created_at"`
	UpdatedAt      time.Time `gorm:"autoUpdateTime" json:"updated_at"`
}

func (Availability) TableName() string {
	return "availabilities"
}

func (a *Availability) BeforeCreate(tx *gorm.DB) error {
	if a.ID == uuid.Nil {
		a.ID = uuid.New()
	}
	return nil
}
