package models

type CreateMetricRequest struct {
	MetricType MetricType             `json:"metric_type" binding:"required"`
	Data       map[string]interface{} `json:"data" binding:"required"`
	Period     string                 `json:"period,omitempty"`
}

type QueryMetricsRequest struct {
	MetricType MetricType `form:"metric_type"`
	StartDate  string     `form:"start_date"`
	EndDate    string     `form:"end_date"`
	Period     string     `form:"period"`
	Limit      int        `form:"limit"`
}

type CreateDashboardRequest struct {
	Name        string   `json:"name" binding:"required"`
	Description string   `json:"description"`
	Widgets     []Widget `json:"widgets"`
	IsPublic    bool     `json:"is_public"`
}

type UpdateDashboardRequest struct {
	Name        string   `json:"name"`
	Description string   `json:"description"`
	Widgets     []Widget `json:"widgets"`
	IsPublic    bool     `json:"is_public"`
}

type DashboardResponse struct {
	Success bool       `json:"success"`
	Data    *Dashboard `json:"data,omitempty"`
	Message string     `json:"message,omitempty"`
}

type MetricsResponse struct {
	Success bool      `json:"success"`
	Data    []Metric  `json:"data,omitempty"`
	Count   int       `json:"count"`
	Message string    `json:"message,omitempty"`
}

type ErrorResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
	Error   string `json:"error,omitempty"`
}
