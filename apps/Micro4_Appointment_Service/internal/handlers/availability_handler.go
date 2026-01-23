package handlers

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/stev97uce/appointment-service/internal/models"
	"github.com/stev97uce/appointment-service/internal/services"
)

type AvailabilityHandler struct {
	service services.AvailabilityService
}

func NewAvailabilityHandler(service services.AvailabilityService) *AvailabilityHandler {
	return &AvailabilityHandler{service: service}
}

func (h *AvailabilityHandler) CreateAvailability(c *gin.Context) {
	var req models.CreateAvailabilityRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	availability, err := h.service.CreateAvailability(c.Request.Context(), &req)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"success": true,
		"message": "Availability created successfully",
		"data":    toAvailabilityResponse(availability),
	})
}

func (h *AvailabilityHandler) GetAvailability(c *gin.Context) {
	idParam := c.Param("id")
	id, err := uuid.Parse(idParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid availability ID"})
		return
	}

	availability, err := h.service.GetAvailability(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "availability not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    toAvailabilityResponse(availability),
	})
}

func (h *AvailabilityHandler) ListByProfessional(c *gin.Context) {
	professionalID := c.Query("professional_id")
	if professionalID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "professional_id is required"})
		return
	}

	var profID int
	if _, err := fmt.Sscanf(professionalID, "%d", &profID); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid professional_id"})
		return
	}

	availabilities, err := h.service.ListByProfessional(c.Request.Context(), profID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	responses := make([]models.AvailabilityResponse, len(availabilities))
	for i, avail := range availabilities {
		responses[i] = toAvailabilityResponse(&avail)
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    responses,
	})
}

func (h *AvailabilityHandler) UpdateAvailability(c *gin.Context) {
	idParam := c.Param("id")
	id, err := uuid.Parse(idParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid availability ID"})
		return
	}

	var req models.UpdateAvailabilityRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	availability, err := h.service.UpdateAvailability(c.Request.Context(), id, &req)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Availability updated successfully",
		"data":    toAvailabilityResponse(availability),
	})
}

func (h *AvailabilityHandler) DeleteAvailability(c *gin.Context) {
	idParam := c.Param("id")
	id, err := uuid.Parse(idParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid availability ID"})
		return
	}

	if err := h.service.DeleteAvailability(c.Request.Context(), id); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Availability deleted successfully",
	})
}

func (h *AvailabilityHandler) FindAvailableSlots(c *gin.Context) {
	professionalID := c.Query("professional_id")
	date := c.Query("date")
	duration := c.Query("duration")

	if professionalID == "" || date == "" || duration == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "professional_id, date, and duration are required"})
		return
	}

	var profID, durationMinutes int
	if _, err := fmt.Sscanf(professionalID, "%d", &profID); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid professional_id"})
		return
	}
	if _, err := fmt.Sscanf(duration, "%d", &durationMinutes); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid duration"})
		return
	}

	slots, err := h.service.FindAvailableSlots(c.Request.Context(), profID, date, durationMinutes)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data": models.AvailableSlotsResponse{
			ProfessionalID: profID,
			Date:           date,
			Slots:          slots,
		},
	})
}

func toAvailabilityResponse(avail *models.Availability) models.AvailabilityResponse {
	var effectiveUntil *string
	if avail.EffectiveUntil != nil {
		until := avail.EffectiveUntil.Format("2006-01-02")
		effectiveUntil = &until
	}

	return models.AvailabilityResponse{
		ID:             avail.ID.String(),
		ProfessionalID: avail.ProfessionalID,
		DayOfWeek:      avail.DayOfWeek,
		StartTime:      avail.StartTime.Format("15:04"),
		EndTime:        avail.EndTime.Format("15:04"),
		IsActive:       avail.IsActive,
		EffectiveFrom:  avail.EffectiveFrom.Format("2006-01-02"),
		EffectiveUntil: effectiveUntil,
		CreatedAt:      avail.CreatedAt.Format("2006-01-02T15:04:05Z07:00"),
		UpdatedAt:      avail.UpdatedAt.Format("2006-01-02T15:04:05Z07:00"),
	}
}
