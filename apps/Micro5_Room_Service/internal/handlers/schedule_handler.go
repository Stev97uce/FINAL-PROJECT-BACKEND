package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/stev97uce/room-service/internal/middleware"
	"github.com/stev97uce/room-service/internal/models"
	"github.com/stev97uce/room-service/internal/services"
)

type ScheduleHandler struct {
	service services.ScheduleService
}

func NewScheduleHandler(service services.ScheduleService) *ScheduleHandler {
	return &ScheduleHandler{service: service}
}

func (h *ScheduleHandler) CreateSchedule(c *gin.Context) {
	var req models.CreateScheduleRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	userID, err := middleware.GetUserID(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "unauthorized"})
		return
	}

	schedule, err := h.service.CreateSchedule(c.Request.Context(), &req, userID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"success": true,
		"message": "Schedule created successfully",
		"data":    toScheduleResponse(schedule),
	})
}

func (h *ScheduleHandler) GetSchedule(c *gin.Context) {
	idParam := c.Param("id")
	id, err := uuid.Parse(idParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid schedule ID"})
		return
	}

	schedule, err := h.service.GetSchedule(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "schedule not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    toScheduleResponse(schedule),
	})
}

func (h *ScheduleHandler) ListSchedules(c *gin.Context) {
	var query models.ListSchedulesQuery
	if err := c.ShouldBindQuery(&query); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	result, err := h.service.ListSchedules(c.Request.Context(), &query)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data": gin.H{
			"data":        result.Data,
			"total_count": result.TotalCount,
			"page":        result.Page,
			"page_size":   result.PageSize,
			"total_pages": result.TotalPages,
		},
	})
}

func (h *ScheduleHandler) UpdateSchedule(c *gin.Context) {
	idParam := c.Param("id")
	id, err := uuid.Parse(idParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid schedule ID"})
		return
	}

	var req models.UpdateScheduleRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	schedule, err := h.service.UpdateSchedule(c.Request.Context(), id, &req)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Schedule updated successfully",
		"data":    toScheduleResponse(schedule),
	})
}

func (h *ScheduleHandler) DeleteSchedule(c *gin.Context) {
	idParam := c.Param("id")
	id, err := uuid.Parse(idParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid schedule ID"})
		return
	}

	if err := h.service.DeleteSchedule(c.Request.Context(), id); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Schedule deleted successfully",
	})
}

func (h *ScheduleHandler) GetRoomSchedules(c *gin.Context) {
	roomIDParam := c.Param("id")
	roomID, err := uuid.Parse(roomIDParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid room ID"})
		return
	}

	startDate := c.Query("start_date")
	endDate := c.Query("end_date")

	if startDate == "" || endDate == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "start_date and end_date are required"})
		return
	}

	schedules, err := h.service.GetRoomSchedules(c.Request.Context(), roomID, startDate, endDate)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	responses := make([]models.ScheduleResponse, len(schedules))
	for i, schedule := range schedules {
		responses[i] = toScheduleResponse(&schedule)
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    responses,
	})
}

func toScheduleResponse(schedule *models.RoomSchedule) models.ScheduleResponse {
	response := models.ScheduleResponse{
		ID:            schedule.ID,
		RoomID:        schedule.RoomID,
		AppointmentID: schedule.AppointmentID,
		StartTime:     schedule.StartTime.Format("2006-01-02T15:04:05Z07:00"),
		EndTime:       schedule.EndTime.Format("2006-01-02T15:04:05Z07:00"),
		Status:        schedule.Status,
		ReservedBy:    schedule.ReservedBy,
		Purpose:       schedule.Purpose,
		Notes:         schedule.Notes,
		CreatedAt:     schedule.CreatedAt.Format("2006-01-02T15:04:05Z07:00"),
		UpdatedAt:     schedule.UpdatedAt.Format("2006-01-02T15:04:05Z07:00"),
	}

	if schedule.Room != nil {
		roomResp := toRoomResponse(schedule.Room)
		response.Room = &roomResp
	}

	return response
}
