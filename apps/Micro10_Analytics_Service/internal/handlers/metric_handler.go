package handlers

import (
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/stev97uce/analytics-service/internal/models"
	"github.com/stev97uce/analytics-service/internal/services"
)

type MetricHandler struct {
	service *services.MetricService
}

func NewMetricHandler(service *services.MetricService) *MetricHandler {
	return &MetricHandler{service: service}
}

func (h *MetricHandler) CreateMetric(c *gin.Context) {
	var req models.CreateMetricRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Success: false,
			Message: "Invalid request body",
			Error:   err.Error(),
		})
		return
	}

	metric := &models.Metric{
		MetricType: req.MetricType,
		Data:       req.Data,
		Period:     req.Period,
		Timestamp:  time.Now(),
	}

	if err := h.service.CreateMetric(c.Request.Context(), metric); err != nil {
		c.JSON(http.StatusInternalServerError, models.ErrorResponse{
			Success: false,
			Message: "Failed to create metric",
			Error:   err.Error(),
		})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"success": true,
		"data":    metric,
		"message": "Metric created successfully",
	})
}

func (h *MetricHandler) GetMetrics(c *gin.Context) {
	metricType := models.MetricType(c.Query("metric_type"))
	limitStr := c.DefaultQuery("limit", "100")
	startDate := c.Query("start_date")
	endDate := c.Query("end_date")

	limit, _ := strconv.Atoi(limitStr)

	var metrics []models.Metric
	var err error

	if startDate != "" && endDate != "" {
		start, err1 := time.Parse("2006-01-02", startDate)
		end, err2 := time.Parse("2006-01-02", endDate)
		
		if err1 != nil || err2 != nil {
			c.JSON(http.StatusBadRequest, models.ErrorResponse{
				Success: false,
				Message: "Invalid date format. Use YYYY-MM-DD",
			})
			return
		}

		metrics, err = h.service.GetMetricsByDateRange(c.Request.Context(), metricType, start, end, limit)
	} else {
		metrics, err = h.service.GetMetricsByType(c.Request.Context(), metricType, limit)
	}

	if err != nil {
		c.JSON(http.StatusInternalServerError, models.ErrorResponse{
			Success: false,
			Message: "Failed to fetch metrics",
			Error:   err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, models.MetricsResponse{
		Success: true,
		Data:    metrics,
		Count:   len(metrics),
	})
}

func (h *MetricHandler) GetLatestMetric(c *gin.Context) {
	metricType := models.MetricType(c.Param("type"))

	metric, err := h.service.GetLatestMetric(c.Request.Context(), metricType)
	if err != nil {
		c.JSON(http.StatusNotFound, models.ErrorResponse{
			Success: false,
			Message: "Metric not found",
			Error:   err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    metric,
	})
}

func (h *MetricHandler) GetDashboardSummary(c *gin.Context) {
	summary, err := h.service.GetDashboardSummary(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.ErrorResponse{
			Success: false,
			Message: "Failed to get dashboard summary",
			Error:   err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    summary,
	})
}
