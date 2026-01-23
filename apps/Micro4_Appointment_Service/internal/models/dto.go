package models

// DTOs for API requests/responses

type CreateAppointmentRequest struct {
	PatientID       int             `json:"patient_id" binding:"required"`
	ProfessionalID  int             `json:"professional_id" binding:"required"`
	AppointmentDate string          `json:"appointment_date" binding:"required"`
	StartTime       string          `json:"start_time" binding:"required"`
	DurationMinutes int             `json:"duration_minutes" binding:"required,min=15,max=180"`
	AppointmentType AppointmentType `json:"appointment_type" binding:"required"`
	Modality        Modality        `json:"modality" binding:"required"`
	Notes           string          `json:"notes"`
}

type UpdateAppointmentRequest struct {
	AppointmentDate *string          `json:"appointment_date"`
	StartTime       *string          `json:"start_time"`
	DurationMinutes *int             `json:"duration_minutes" binding:"omitempty,min=15,max=180"`
	AppointmentType *AppointmentType `json:"appointment_type"`
	Modality        *Modality        `json:"modality"`
	Notes           *string          `json:"notes"`
}

type CancelAppointmentRequest struct {
	CancellationReason string `json:"cancellation_reason" binding:"required,min=10"`
}

type AppointmentResponse struct {
	ID                 string            `json:"id"`
	PatientID          int               `json:"patient_id"`
	ProfessionalID     int               `json:"professional_id"`
	RoomID             *int              `json:"room_id,omitempty"`
	AppointmentDate    string            `json:"appointment_date"`
	StartTime          string            `json:"start_time"`
	EndTime            string            `json:"end_time"`
	DurationMinutes    int               `json:"duration_minutes"`
	Status             AppointmentStatus `json:"status"`
	AppointmentType    AppointmentType   `json:"appointment_type"`
	Modality           Modality          `json:"modality"`
	Notes              string            `json:"notes,omitempty"`
	CancellationReason string            `json:"cancellation_reason,omitempty"`
	CreatedBy          int               `json:"created_by"`
	CreatedAt          string            `json:"created_at"`
	UpdatedAt          string            `json:"updated_at"`
}

type CreateAvailabilityRequest struct {
	ProfessionalID int    `json:"professional_id" binding:"required"`
	DayOfWeek      int    `json:"day_of_week" binding:"required,min=0,max=6"`
	StartTime      string `json:"start_time" binding:"required"`
	EndTime        string `json:"end_time" binding:"required"`
	EffectiveFrom  string `json:"effective_from" binding:"required"`
	EffectiveUntil string `json:"effective_until"`
}

type UpdateAvailabilityRequest struct {
	DayOfWeek      *int    `json:"day_of_week" binding:"omitempty,min=0,max=6"`
	StartTime      *string `json:"start_time"`
	EndTime        *string `json:"end_time"`
	IsActive       *bool   `json:"is_active"`
	EffectiveFrom  *string `json:"effective_from"`
	EffectiveUntil *string `json:"effective_until"`
}

type AvailabilityResponse struct {
	ID             string  `json:"id"`
	ProfessionalID int     `json:"professional_id"`
	DayOfWeek      int     `json:"day_of_week"`
	StartTime      string  `json:"start_time"`
	EndTime        string  `json:"end_time"`
	IsActive       bool    `json:"is_active"`
	EffectiveFrom  string  `json:"effective_from"`
	EffectiveUntil *string `json:"effective_until,omitempty"`
	CreatedAt      string  `json:"created_at"`
	UpdatedAt      string  `json:"updated_at"`
}

type TimeSlot struct {
	Date      string `json:"date"`
	StartTime string `json:"start_time"`
	EndTime   string `json:"end_time"`
	Available bool   `json:"available"`
}

type AvailableSlotsResponse struct {
	ProfessionalID int        `json:"professional_id"`
	Date           string     `json:"date"`
	Slots          []TimeSlot `json:"slots"`
}

type ListAppointmentsQuery struct {
	PatientID      *int               `form:"patient_id"`
	ProfessionalID *int               `form:"professional_id"`
	Status         *AppointmentStatus `form:"status"`
	StartDate      *string            `form:"start_date"`
	EndDate        *string            `form:"end_date"`
	Page           int                `form:"page" binding:"min=1"`
	PageSize       int                `form:"page_size" binding:"min=1,max=100"`
}

type PaginatedResponse struct {
	Data       interface{} `json:"data"`
	TotalCount int64       `json:"total_count"`
	Page       int         `json:"page"`
	PageSize   int         `json:"page_size"`
	TotalPages int         `json:"total_pages"`
}
