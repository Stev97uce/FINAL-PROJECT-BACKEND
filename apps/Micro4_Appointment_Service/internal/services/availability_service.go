package services

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/stev97uce/appointment-service/internal/models"
	"github.com/stev97uce/appointment-service/internal/repository"
)

type AvailabilityService interface {
	CreateAvailability(ctx context.Context, req *models.CreateAvailabilityRequest) (*models.Availability, error)
	GetAvailability(ctx context.Context, id uuid.UUID) (*models.Availability, error)
	ListByProfessional(ctx context.Context, professionalID int) ([]models.Availability, error)
	UpdateAvailability(ctx context.Context, id uuid.UUID, req *models.UpdateAvailabilityRequest) (*models.Availability, error)
	DeleteAvailability(ctx context.Context, id uuid.UUID) error
	FindAvailableSlots(ctx context.Context, professionalID int, date string, durationMinutes int) ([]models.TimeSlot, error)
}

type availabilityService struct {
	availRepo repository.AvailabilityRepository
	aptRepo   repository.AppointmentRepository
}

func NewAvailabilityService(availRepo repository.AvailabilityRepository, aptRepo repository.AppointmentRepository) AvailabilityService {
	return &availabilityService{
		availRepo: availRepo,
		aptRepo:   aptRepo,
	}
}

func (s *availabilityService) CreateAvailability(ctx context.Context, req *models.CreateAvailabilityRequest) (*models.Availability, error) {
	startTime, err := time.Parse("15:04", req.StartTime)
	if err != nil {
		return nil, errors.New("invalid start time format")
	}

	endTime, err := time.Parse("15:04", req.EndTime)
	if err != nil {
		return nil, errors.New("invalid end time format")
	}

	effectiveFrom, err := time.Parse("2006-01-02", req.EffectiveFrom)
	if err != nil {
		return nil, errors.New("invalid effective from date format")
	}

	var effectiveUntil *time.Time
	if req.EffectiveUntil != "" {
		parsed, err := time.Parse("2006-01-02", req.EffectiveUntil)
		if err != nil {
			return nil, errors.New("invalid effective until date format")
		}
		effectiveUntil = &parsed
	}

	// Validate time range
	if !endTime.After(startTime) {
		return nil, errors.New("end time must be after start time")
	}

	availability := &models.Availability{
		ProfessionalID: req.ProfessionalID,
		DayOfWeek:      req.DayOfWeek,
		StartTime:      startTime,
		EndTime:        endTime,
		IsActive:       true,
		EffectiveFrom:  effectiveFrom,
		EffectiveUntil: effectiveUntil,
	}

	if err := s.availRepo.Create(ctx, availability); err != nil {
		return nil, fmt.Errorf("error creating availability: %w", err)
	}

	return availability, nil
}

func (s *availabilityService) GetAvailability(ctx context.Context, id uuid.UUID) (*models.Availability, error) {
	availability, err := s.availRepo.FindByID(ctx, id)
	if err != nil {
		return nil, errors.New("availability not found")
	}
	return availability, nil
}

func (s *availabilityService) ListByProfessional(ctx context.Context, professionalID int) ([]models.Availability, error) {
	return s.availRepo.FindByProfessional(ctx, professionalID)
}

func (s *availabilityService) UpdateAvailability(ctx context.Context, id uuid.UUID, req *models.UpdateAvailabilityRequest) (*models.Availability, error) {
	availability, err := s.availRepo.FindByID(ctx, id)
	if err != nil {
		return nil, errors.New("availability not found")
	}

	if req.DayOfWeek != nil {
		availability.DayOfWeek = *req.DayOfWeek
	}

	if req.StartTime != nil {
		startTime, err := time.Parse("15:04", *req.StartTime)
		if err != nil {
			return nil, errors.New("invalid start time format")
		}
		availability.StartTime = startTime
	}

	if req.EndTime != nil {
		endTime, err := time.Parse("15:04", *req.EndTime)
		if err != nil {
			return nil, errors.New("invalid end time format")
		}
		availability.EndTime = endTime
	}

	if req.IsActive != nil {
		availability.IsActive = *req.IsActive
	}

	if req.EffectiveFrom != nil {
		effectiveFrom, err := time.Parse("2006-01-02", *req.EffectiveFrom)
		if err != nil {
			return nil, errors.New("invalid effective from date format")
		}
		availability.EffectiveFrom = effectiveFrom
	}

	if req.EffectiveUntil != nil {
		effectiveUntil, err := time.Parse("2006-01-02", *req.EffectiveUntil)
		if err != nil {
			return nil, errors.New("invalid effective until date format")
		}
		availability.EffectiveUntil = &effectiveUntil
	}

	// Validate time range
	if !availability.EndTime.After(availability.StartTime) {
		return nil, errors.New("end time must be after start time")
	}

	if err := s.availRepo.Update(ctx, availability); err != nil {
		return nil, fmt.Errorf("error updating availability: %w", err)
	}

	return availability, nil
}

func (s *availabilityService) DeleteAvailability(ctx context.Context, id uuid.UUID) error {
	_, err := s.availRepo.FindByID(ctx, id)
	if err != nil {
		return errors.New("availability not found")
	}

	return s.availRepo.Delete(ctx, id)
}

func (s *availabilityService) FindAvailableSlots(ctx context.Context, professionalID int, dateStr string, durationMinutes int) ([]models.TimeSlot, error) {
	// Parse date
	date, err := time.Parse("2006-01-02", dateStr)
	if err != nil {
		return nil, errors.New("invalid date format")
	}

	// Get day of week (0 = Sunday, 6 = Saturday)
	dayOfWeek := int(date.Weekday())

	// Find availability for this day
	availabilities, err := s.availRepo.FindActiveByProfessionalAndDay(ctx, professionalID, dayOfWeek, date)
	if err != nil {
		return nil, fmt.Errorf("error getting availabilities: %w", err)
	}

	if len(availabilities) == 0 {
		return []models.TimeSlot{}, nil
	}

	// Get existing appointments for this day
	nextDay := date.AddDate(0, 0, 1)
	appointments, err := s.aptRepo.FindByProfessionalAndDateRange(ctx, professionalID, date, nextDay)
	if err != nil {
		return nil, fmt.Errorf("error getting appointments: %w", err)
	}

	// Generate time slots
	var slots []models.TimeSlot
	slotDuration := time.Duration(durationMinutes) * time.Minute

	for _, avail := range availabilities {
		currentTime := avail.StartTime
		endTime := avail.EndTime

		for currentTime.Add(slotDuration).Before(endTime) || currentTime.Add(slotDuration).Equal(endTime) {
			slotEndTime := currentTime.Add(slotDuration)

			// Check if slot is available (no overlapping appointments)
			available := true
			for _, apt := range appointments {
				if timesOverlap(currentTime, slotEndTime, apt.StartTime, apt.EndTime) {
					available = false
					break
				}
			}

			slots = append(slots, models.TimeSlot{
				Date:      dateStr,
				StartTime: currentTime.Format("15:04"),
				EndTime:   slotEndTime.Format("15:04"),
				Available: available,
			})

			currentTime = slotEndTime
		}
	}

	return slots, nil
}

func timesOverlap(start1, end1, start2, end2 time.Time) bool {
	return start1.Before(end2) && end1.After(start2)
}
