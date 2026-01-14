package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/stev97uce/analytics-service/internal/models"
	"github.com/stev97uce/analytics-service/internal/services"
)

type DashboardHandler struct {
	service *services.DashboardService
}

func NewDashboardHandler(service *services.DashboardService) *DashboardHandler {
	return &DashboardHandler{service: service}
}

func (h *DashboardHandler) CreateDashboard(c *gin.Context) {
	var req models.CreateDashboardRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Success: false,
			Message: "Invalid request body",
			Error:   err.Error(),
		})
		return
	}

	userID := c.GetInt("user_id")
	
	dashboard := &models.Dashboard{
		Name:        req.Name,
		Description: req.Description,
		Widgets:     req.Widgets,
		UserID:      userID,
		IsPublic:    req.IsPublic,
	}

	if err := h.service.CreateDashboard(c.Request.Context(), dashboard); err != nil {
		c.JSON(http.StatusInternalServerError, models.ErrorResponse{
			Success: false,
			Message: "Failed to create dashboard",
			Error:   err.Error(),
		})
		return
	}

	c.JSON(http.StatusCreated, models.DashboardResponse{
		Success: true,
		Data:    dashboard,
		Message: "Dashboard created successfully",
	})
}

func (h *DashboardHandler) GetDashboard(c *gin.Context) {
	id := c.Param("id")

	dashboard, err := h.service.GetDashboard(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, models.ErrorResponse{
			Success: false,
			Message: "Dashboard not found",
			Error:   err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, models.DashboardResponse{
		Success: true,
		Data:    dashboard,
	})
}

func (h *DashboardHandler) ListDashboards(c *gin.Context) {
	userID := c.GetInt("user_id")

	dashboards, err := h.service.GetUserDashboards(c.Request.Context(), userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.ErrorResponse{
			Success: false,
			Message: "Failed to fetch dashboards",
			Error:   err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    dashboards,
		"count":   len(dashboards),
	})
}

func (h *DashboardHandler) UpdateDashboard(c *gin.Context) {
	id := c.Param("id")

	var req models.UpdateDashboardRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Success: false,
			Message: "Invalid request body",
			Error:   err.Error(),
		})
		return
	}

	dashboard := &models.Dashboard{
		Name:        req.Name,
		Description: req.Description,
		Widgets:     req.Widgets,
		IsPublic:    req.IsPublic,
	}

	if err := h.service.UpdateDashboard(c.Request.Context(), id, dashboard); err != nil {
		c.JSON(http.StatusInternalServerError, models.ErrorResponse{
			Success: false,
			Message: "Failed to update dashboard",
			Error:   err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Dashboard updated successfully",
	})
}

func (h *DashboardHandler) DeleteDashboard(c *gin.Context) {
	id := c.Param("id")

	if err := h.service.DeleteDashboard(c.Request.Context(), id); err != nil {
		c.JSON(http.StatusInternalServerError, models.ErrorResponse{
			Success: false,
			Message: "Failed to delete dashboard",
			Error:   err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Dashboard deleted successfully",
	})
}
