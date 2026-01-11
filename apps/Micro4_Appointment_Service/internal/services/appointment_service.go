package services

import (
	"context"
	"errors"
	"fmt"
	"math"
	"time"

	"github.com/google/uuid"
	"github.com/stev97uce/appointment-service/internal/models"
	"github.com/stev97uce/appointment-service/internal/repository"
)

type AppointmentService interface {
	CreateAppointment(ctx context.Context, req *models.CreateAppointmentRequest, createdBy int) (*models.Appointment, error)
	GetAppointment(ctx context.Context, id uuid.UUID) (*models.Appointment, error)
	ListAppointments(ctx context.Context, query *models.ListAppointmentsQuery) (*models.PaginatedResponse, error)
	UpdateAppointment(ctx context.Context, id uuid.UUID, req *models.UpdateAppointmentRequest) (*models.Appointment, error)
	CancelAppointment(ctx context.Context, id uuid.UUID, reason string) error
	ConfirmAppointment(ctx context.Context, id uuid.UUID) error
	CompleteAppointment(ctx context.Context, id uuid.UUID) error
	MarkNoShow(ctx context.Context, id uuid.UUID) error
}

type appointmentService struct {
	repo repository.AppointmentRepository
}

func NewAppointmentService(repo repository.AppointmentRepository) AppointmentService {
	return &appointmentService{repo: repo}
}

func (s *appointmentService) CreateAppointment(ctx context.Context, req *models.CreateAppointmentRequest, createdBy int) (*models.Appointment, error) {
	// Parse date and time
	appointmentDate, err := time.Parse("2006-01-02", req.AppointmentDate)
	if err != nil {
		return nil, errors.New("invalid appointment date format")
	}

	startTime, err := time.Parse("15:04", req.StartTime)
	if err != nil {
		return nil, errors.New("invalid start time format")
	}

	// Calculate end time
	endTime := startTime.Add(time.Duration(req.DurationMinutes) * time.Minute)

	// Check if appointment is in the past
	now := time.Now()
	appointmentDateTime := time.Date(
		appointmentDate.Year(), appointmentDate.Month(), appointmentDate.Day(),
		startTime.Hour(), startTime.Minute(), 0, 0, time.UTC,
	)
	if appointmentDateTime.Before(now) {
		return nil, errors.New("cannot create appointment in the past")
	}

	// Check for overlapping appointments
	hasOverlap, err := s.repo.CheckOverlap(ctx, req.ProfessionalID, appointmentDate, startTime, endTime, nil)
	if err != nil {
		return nil, fmt.Errorf("error checking overlaps: %w", err)
	}
	if hasOverlap {
		return nil, errors.New("professional already has an appointment at this time")
	}

	appointment := &models.Appointment{
		PatientID:       req.PatientID,
		ProfessionalID:  req.ProfessionalID,
		AppointmentDate: appointmentDate,
		StartTime:       startTime,
		EndTime:         endTime,
		DurationMinutes: req.DurationMinutes,
		Status:          models.StatusScheduled,
		AppointmentType: req.AppointmentType,
		Modality:        req.Modality,
		Notes:           req.Notes,
		CreatedBy:       createdBy,
	}

	if err := s.repo.Create(ctx, appointment); err != nil {
		return nil, fmt.Errorf("error creating appointment: %w", err)
	}

	return appointment, nil
}

func (s *appointmentService) GetAppointment(ctx context.Context, id uuid.UUID) (*models.Appointment, error) {
	appointment, err := s.repo.FindByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("appointment not found: %w", err)
	}
	return appointment, nil
}

func (s *appointmentService) ListAppointments(ctx context.Context, query *models.ListAppointmentsQuery) (*models.PaginatedResponse, error) {
	// Set defaults
	if query.Page < 1 {
		query.Page = 1
	}
	if query.PageSize < 1 {
		query.PageSize = 10
	}

	filters := make(map[string]interface{})
	if query.PatientID != nil {
		filters["patient_id"] = *query.PatientID
	}
	if query.ProfessionalID != nil {
		filters["professional_id"] = *query.ProfessionalID
	}
	if query.Status != nil {
		filters["status"] = *query.Status
	}
	if query.StartDate != nil {
		filters["start_date"] = *query.StartDate
	}
	if query.EndDate != nil {
		filters["end_date"] = *query.EndDate
	}

	appointments, totalCount, err := s.repo.FindAll(ctx, filters, query.Page, query.PageSize)
	if err != nil {
		return nil, fmt.Errorf("error listing appointments: %w", err)
	}

	// Convert to response format
	appointmentResponses := make([]models.AppointmentResponse, len(appointments))
	for i, apt := range appointments {
		appointmentResponses[i] = toAppointmentResponse(&apt)
	}

	totalPages := int(math.Ceil(float64(totalCount) / float64(query.PageSize)))

	return &models.PaginatedResponse{
		Data:       appointmentResponses,
		TotalCount: totalCount,
		Page:       query.Page,
		PageSize:   query.PageSize,
		TotalPages: totalPages,
	}, nil
}

func (s *appointmentService) UpdateAppointment(ctx context.Context, id uuid.UUID, req *models.UpdateAppointmentRequest) (*models.Appointment, error) {
	appointment, err := s.repo.FindByID(ctx, id)
	if err != nil {
		return nil, errors.New("appointment not found")
	}

	// Check if appointment can be updated
	if appointment.Status == models.StatusCompleted || appointment.Status == models.StatusCancelled {
		return nil, errors.New("cannot update completed or cancelled appointment")
	}

	// Update fields
	if req.AppointmentDate != nil {
		date, err := time.Parse("2006-01-02", *req.AppointmentDate)
		if err != nil {
			return nil, errors.New("invalid appointment date format")
		}
		appointment.AppointmentDate = date
	}

	if req.StartTime != nil {
		startTime, err := time.Parse("15:04", *req.StartTime)
		if err != nil {
			return nil, errors.New("invalid start time format")
		}
		appointment.StartTime = startTime
	}

	if req.DurationMinutes != nil {
		appointment.DurationMinutes = *req.DurationMinutes
		appointment.EndTime = appointment.StartTime.Add(time.Duration(*req.DurationMinutes) * time.Minute)
	}

	if req.AppointmentType != nil {
		appointment.AppointmentType = *req.AppointmentType
	}

	if req.Modality != nil {
		appointment.Modality = *req.Modality
	}

	if req.Notes != nil {
		appointment.Notes = *req.Notes
	}

	// Check for overlaps if time changed
	hasOverlap, err := s.repo.CheckOverlap(ctx, appointment.ProfessionalID, appointment.AppointmentDate, appointment.StartTime, appointment.EndTime, &id)
	if err != nil {
		return nil, fmt.Errorf("error checking overlaps: %w", err)
	}
	if hasOverlap {
		return nil, errors.New("professional already has an appointment at this time")
	}

	if err := s.repo.Update(ctx, appointment); err != nil {
		return nil, fmt.Errorf("error updating appointment: %w", err)
	}

	return appointment, nil
}

func (s *appointmentService) CancelAppointment(ctx context.Context, id uuid.UUID, reason string) error {
	appointment, err := s.repo.FindByID(ctx, id)
	if err != nil {
		return errors.New("appointment not found")
	}

	if appointment.Status == models.StatusCompleted || appointment.Status == models.StatusCancelled {
		return errors.New("cannot cancel completed or already cancelled appointment")
	}

	appointment.Status = models.StatusCancelled
	appointment.CancellationReason = reason

	return s.repo.Update(ctx, appointment)
}

func (s *appointmentService) ConfirmAppointment(ctx context.Context, id uuid.UUID) error {
	appointment, err := s.repo.FindByID(ctx, id)
	if err != nil {
		return errors.New("appointment not found")
	}

	if appointment.Status != models.StatusScheduled {
		return errors.New("only scheduled appointments can be confirmed")
	}

	appointment.Status = models.StatusConfirmed
	return s.repo.Update(ctx, appointment)
}

func (s *appointmentService) CompleteAppointment(ctx context.Context, id uuid.UUID) error {
	appointment, err := s.repo.FindByID(ctx, id)
	if err != nil {
		return errors.New("appointment not found")
	}

	if appointment.Status == models.StatusCompleted {
		return errors.New("appointment already completed")
	}

	if appointment.Status == models.StatusCancelled || appointment.Status == models.StatusNoShow {
		return errors.New("cannot complete cancelled or no-show appointment")
	}

	appointment.Status = models.StatusCompleted
	return s.repo.Update(ctx, appointment)
}

func (s *appointmentService) MarkNoShow(ctx context.Context, id uuid.UUID) error {
	appointment, err := s.repo.FindByID(ctx, id)
	if err != nil {
		return errors.New("appointment not found")
	}

	if appointment.Status == models.StatusCompleted {
		return errors.New("cannot mark completed appointment as no-show")
	}

	appointment.Status = models.StatusNoShow
	return s.repo.Update(ctx, appointment)
}

func toAppointmentResponse(apt *models.Appointment) models.AppointmentResponse {
	return models.AppointmentResponse{
		ID:                 apt.ID.String(),
		PatientID:          apt.PatientID,
		ProfessionalID:     apt.ProfessionalID,
		RoomID:             apt.RoomID,
		AppointmentDate:    apt.AppointmentDate.Format("2006-01-02"),
		StartTime:          apt.StartTime.Format("15:04"),
		EndTime:            apt.EndTime.Format("15:04"),
		DurationMinutes:    apt.DurationMinutes,
		Status:             apt.Status,
		AppointmentType:    apt.AppointmentType,
		Modality:           apt.Modality,
		Notes:              apt.Notes,
		CancellationReason: apt.CancellationReason,
		CreatedBy:          apt.CreatedBy,
		CreatedAt:          apt.CreatedAt.Format(time.RFC3339),
		UpdatedAt:          apt.UpdatedAt.Format(time.RFC3339),
	}
}
