package models

import (
	"testing"
)

func TestCreateMetricRequest_Validation(t *testing.T) {
	tests := []struct {
		name    string
		request CreateMetricRequest
		wantErr bool
	}{
		{
			name: "valid request",
			request: CreateMetricRequest{
				MetricType: "appointment_stats",
				Data: map[string]interface{}{
					"total": 100,
				},
				Period: "daily",
			},
			wantErr: false,
		},
		{
			name: "valid request hourly",
			request: CreateMetricRequest{
				MetricType: "user_activity",
				Data: map[string]interface{}{
					"active_users": 50,
				},
				Period: "hourly",
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.request.MetricType == "" && !tt.wantErr {
				t.Error("MetricType should not be empty for valid request")
			}
			if tt.request.Data == nil && !tt.wantErr {
				t.Error("Data should not be nil for valid request")
			}
		})
	}
}

func TestQueryMetricsRequest_Values(t *testing.T) {
	query := QueryMetricsRequest{
		MetricType: MetricTypeAppointmentStats,
		StartDate:  "2024-01-01",
		EndDate:    "2024-01-31",
		Period:     "daily",
		Limit:      100,
	}

	if query.MetricType != MetricTypeAppointmentStats {
		t.Errorf("Expected MetricType to be appointment_stats, got %s", query.MetricType)
	}

	if query.Limit != 100 {
		t.Errorf("Expected Limit to be 100, got %d", query.Limit)
	}

	if query.Period != "daily" {
		t.Errorf("Expected Period to be 'daily', got %s", query.Period)
	}
}

func TestCreateDashboardRequest_Validation(t *testing.T) {
	tests := []struct {
		name    string
		request CreateDashboardRequest
		wantErr bool
	}{
		{
			name: "valid request",
			request: CreateDashboardRequest{
				Name:        "Test Dashboard",
				Description: "Test Description",
				Widgets:     []Widget{},
				IsPublic:    true,
			},
			wantErr: false,
		},
		{
			name: "request with widgets",
			request: CreateDashboardRequest{
				Name: "Dashboard with Widgets",
				Widgets: []Widget{
					{
						ID:         "w1",
						Title:      "Widget 1",
						Type:       "chart",
						MetricType: "appointment_stats",
						Position: Position{
							X:      0,
							Y:      0,
							Width:  6,
							Height: 4,
						},
					},
				},
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.request.Name == "" && !tt.wantErr {
				t.Error("Name should not be empty for valid request")
			}
		})
	}
}

func TestUpdateDashboardRequest_Creation(t *testing.T) {
	update := UpdateDashboardRequest{
		Name:        "Updated Dashboard",
		Description: "Updated Description",
		Widgets: []Widget{
			{
				ID:         "w1",
				Title:      "New Widget",
				Type:       "line-chart",
				MetricType: "session_stats",
				Position: Position{
					X:      6,
					Y:      0,
					Width:  6,
					Height: 4,
				},
			},
		},
		IsPublic: false,
	}

	if update.Name != "Updated Dashboard" {
		t.Errorf("Expected Name to be 'Updated Dashboard', got %s", update.Name)
	}

	if update.IsPublic != false {
		t.Error("IsPublic should be false")
	}

	if len(update.Widgets) != 1 {
		t.Errorf("Expected 1 widget, got %d", len(update.Widgets))
	}
}

func TestDashboardResponse_Success(t *testing.T) {
	response := DashboardResponse{
		Success: true,
		Data:    &Dashboard{Name: "Test"},
		Message: "Success",
	}

	if !response.Success {
		t.Error("Expected Success to be true")
	}

	if response.Data == nil {
		t.Error("Data should not be nil")
	}

	if response.Message != "Success" {
		t.Errorf("Expected Message to be 'Success', got %s", response.Message)
	}
}

func TestMetricsResponse_WithData(t *testing.T) {
	metrics := []Metric{
		{MetricType: MetricTypeAppointmentStats},
		{MetricType: MetricTypeUserActivity},
	}

	response := MetricsResponse{
		Success: true,
		Data:    metrics,
		Count:   len(metrics),
		Message: "Retrieved successfully",
	}

	if !response.Success {
		t.Error("Expected Success to be true")
	}

	if response.Count != 2 {
		t.Errorf("Expected Count to be 2, got %d", response.Count)
	}

	if len(response.Data) != 2 {
		t.Errorf("Expected 2 metrics, got %d", len(response.Data))
	}
}

func TestErrorResponse_Creation(t *testing.T) {
	response := ErrorResponse{
		Success: false,
		Message: "An error occurred",
		Error:   "Database connection failed",
	}

	if response.Success {
		t.Error("Expected Success to be false")
	}

	if response.Message != "An error occurred" {
		t.Errorf("Expected Message to be 'An error occurred', got %s", response.Message)
	}

	if response.Error != "Database connection failed" {
		t.Errorf("Expected Error to be 'Database connection failed', got %s", response.Error)
	}
}

func TestQueryMetricsRequest_EmptyValues(t *testing.T) {
	query := QueryMetricsRequest{}

	if query.Limit != 0 {
		t.Errorf("Expected Limit to be 0, got %d", query.Limit)
	}

	if query.MetricType != "" {
		t.Errorf("Expected empty MetricType, got %s", query.MetricType)
	}
}

