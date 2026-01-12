package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/stev97uce/room-service/internal/models"
	"github.com/stev97uce/room-service/internal/services"
)

type RoomHandler struct {
	service services.RoomService
}

func NewRoomHandler(service services.RoomService) *RoomHandler {
	return &RoomHandler{service: service}
}

func (h *RoomHandler) CreateRoom(c *gin.Context) {
	var req models.CreateRoomRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	room, err := h.service.CreateRoom(c.Request.Context(), &req)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"success": true,
		"message": "Room created successfully",
		"data":    toRoomResponse(room),
	})
}

func (h *RoomHandler) GetRoom(c *gin.Context) {
	idParam := c.Param("id")
	id, err := uuid.Parse(idParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid room ID"})
		return
	}

	room, err := h.service.GetRoom(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "room not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    toRoomResponse(room),
	})
}

func (h *RoomHandler) ListRooms(c *gin.Context) {
	var query models.ListRoomsQuery
	if err := c.ShouldBindQuery(&query); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	result, err := h.service.ListRooms(c.Request.Context(), &query)
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

func (h *RoomHandler) UpdateRoom(c *gin.Context) {
	idParam := c.Param("id")
	id, err := uuid.Parse(idParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid room ID"})
		return
	}

	var req models.UpdateRoomRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	room, err := h.service.UpdateRoom(c.Request.Context(), id, &req)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Room updated successfully",
		"data":    toRoomResponse(room),
	})
}

func (h *RoomHandler) DeleteRoom(c *gin.Context) {
	idParam := c.Param("id")
	id, err := uuid.Parse(idParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid room ID"})
		return
	}

	if err := h.service.DeleteRoom(c.Request.Context(), id); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Room deleted successfully",
	})
}

func (h *RoomHandler) UpdateRoomStatus(c *gin.Context) {
	idParam := c.Param("id")
	id, err := uuid.Parse(idParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid room ID"})
		return
	}

	var req models.UpdateRoomStatusRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	room, err := h.service.UpdateRoomStatus(c.Request.Context(), id, req.Status)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Room status updated successfully",
		"data":    toRoomResponse(room),
	})
}

func (h *RoomHandler) FindAvailableRooms(c *gin.Context) {
	var query models.AvailableRoomsQuery
	if err := c.ShouldBindQuery(&query); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	rooms, err := h.service.FindAvailableRooms(c.Request.Context(), &query)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	responses := make([]models.RoomResponse, len(rooms))
	for i, room := range rooms {
		responses[i] = toRoomResponse(&room)
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    responses,
	})
}

func toRoomResponse(room *models.Room) models.RoomResponse {
	return models.RoomResponse{
		ID:          room.ID,
		Name:        room.Name,
		RoomNumber:  room.RoomNumber,
		FloorNumber: room.FloorNumber,
		Building:    room.Building,
		Capacity:    room.Capacity,
		RoomType:    room.RoomType,
		Status:      room.Status,
		Equipment:   room.Equipment,
		Description: room.Description,
		IsActive:    room.IsActive,
		CreatedAt:   room.CreatedAt.Format("2006-01-02T15:04:05Z07:00"),
		UpdatedAt:   room.UpdatedAt.Format("2006-01-02T15:04:05Z07:00"),
	}
}
