package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/stev97uce/appointment-service/internal/middleware"
	"github.com/stev97uce/appointment-service/internal/models"
	"github.com/stev97uce/appointment-service/internal/services"
)

type AppointmentHandler struct {
	service services.AppointmentService
}

func NewAppointmentHandler(service services.AppointmentService) *AppointmentHandler {
	return &AppointmentHandler{service: service}
}

func (h *AppointmentHandler) CreateAppointment(c *gin.Context) {
	var req models.CreateAppointmentRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	userID, err := middleware.GetUserID(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "unauthorized"})
		return
	}

	appointment, err := h.service.CreateAppointment(c.Request.Context(), &req, userID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"success": true,
		"message": "Appointment created successfully",
		"data":    toAppointmentResponse(appointment),
	})
}

func (h *AppointmentHandler) GetAppointment(c *gin.Context) {
	idParam := c.Param("id")
	id, err := uuid.Parse(idParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid appointment ID"})
		return
	}

	appointment, err := h.service.GetAppointment(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "appointment not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    toAppointmentResponse(appointment),
	})
}

func (h *AppointmentHandler) ListAppointments(c *gin.Context) {
	var query models.ListAppointmentsQuery
	if err := c.ShouldBindQuery(&query); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	result, err := h.service.ListAppointments(c.Request.Context(), &query)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    result,
	})
}

func (h *AppointmentHandler) UpdateAppointment(c *gin.Context) {
	idParam := c.Param("id")
	id, err := uuid.Parse(idParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid appointment ID"})
		return
	}

	var req models.UpdateAppointmentRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	appointment, err := h.service.UpdateAppointment(c.Request.Context(), id, &req)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Appointment updated successfully",
		"data":    toAppointmentResponse(appointment),
	})
}

func (h *AppointmentHandler) CancelAppointment(c *gin.Context) {
	idParam := c.Param("id")
	id, err := uuid.Parse(idParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid appointment ID"})
		return
	}

	var req models.CancelAppointmentRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := h.service.CancelAppointment(c.Request.Context(), id, req.CancellationReason); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Appointment cancelled successfully",
	})
}

func (h *AppointmentHandler) ConfirmAppointment(c *gin.Context) {
	idParam := c.Param("id")
	id, err := uuid.Parse(idParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid appointment ID"})
		return
	}

	if err := h.service.ConfirmAppointment(c.Request.Context(), id); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Appointment confirmed successfully",
	})
}

func (h *AppointmentHandler) CompleteAppointment(c *gin.Context) {
	idParam := c.Param("id")
	id, err := uuid.Parse(idParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid appointment ID"})
		return
	}

	if err := h.service.CompleteAppointment(c.Request.Context(), id); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Appointment completed successfully",
	})
}

func (h *AppointmentHandler) MarkNoShow(c *gin.Context) {
	idParam := c.Param("id")
	id, err := uuid.Parse(idParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid appointment ID"})
		return
	}

	if err := h.service.MarkNoShow(c.Request.Context(), id); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Appointment marked as no-show",
	})
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
		CreatedAt:          apt.CreatedAt.Format("2006-01-02T15:04:05Z07:00"),
		UpdatedAt:          apt.UpdatedAt.Format("2006-01-02T15:04:05Z07:00"),
	}
}
