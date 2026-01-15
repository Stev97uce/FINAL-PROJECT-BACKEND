package models

import (
	"testing"
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

func TestMetricType_String(t *testing.T) {
	tests := []struct {
		name     string
		metricType MetricType
		want     string
	}{
		{"appointment_stats", MetricTypeAppointmentStats, "appointment_stats"},
		{"user_activity", MetricTypeUserActivity, "user_activity"},
		{"room_utilization", MetricTypeRoomUtilization, "room_utilization"},
		{"session_stats", MetricTypeSessionStats, "session_stats"},
		{"supervision_stats", MetricTypeSupervisionStats, "supervision_stats"},
		{"system_performance", MetricTypeSystemPerformance, "system_performance"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := string(tt.metricType); got != tt.want {
				t.Errorf("MetricType = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestMetric_Creation(t *testing.T) {
	now := time.Now()
	
	metric := &Metric{
		ID:         primitive.NewObjectID(),
		MetricType: MetricTypeAppointmentStats,
		Data: map[string]interface{}{
			"total": 100,
			"completed": 75,
		},
		Timestamp: now,
		Period:    "daily",
		Metadata: map[string]interface{}{
			"source": "test",
		},
		CreatedAt: now,
	}

	if metric.MetricType != MetricTypeAppointmentStats {
		t.Errorf("Expected MetricType to be appointment_stats, got %s", metric.MetricType)
	}

	if metric.Period != "daily" {
		t.Errorf("Expected Period to be daily, got %s", metric.Period)
	}

	if metric.Data["total"] != 100 {
		t.Errorf("Expected Data.total to be 100, got %v", metric.Data["total"])
	}
}

func TestDashboard_Creation(t *testing.T) {
	now := time.Now()
	
	dashboard := &Dashboard{
		ID:          primitive.NewObjectID(),
		Name:        "Test Dashboard",
		Description: "Test Description",
		Widgets:     []Widget{},
		UserID:      1,
		IsPublic:    true,
		CreatedAt:   now,
		UpdatedAt:   now,
	}

	if dashboard.Name != "Test Dashboard" {
		t.Errorf("Expected Name to be 'Test Dashboard', got %s", dashboard.Name)
	}

	if !dashboard.IsPublic {
		t.Error("Expected IsPublic to be true")
	}

	if dashboard.UserID != 1 {
		t.Errorf("Expected UserID to be 1, got %d", dashboard.UserID)
	}
}

func TestWidget_Creation(t *testing.T) {
	widget := Widget{
		ID:         "widget-1",
		Title:      "Appointment Stats",
		Type:       "chart",
		MetricType: MetricTypeAppointmentStats,
		Config: map[string]interface{}{
			"chartType": "bar",
		},
		Position: Position{
			X:      0,
			Y:      0,
			Width:  6,
			Height: 4,
		},
	}

	if widget.ID != "widget-1" {
		t.Errorf("Expected ID to be 'widget-1', got %s", widget.ID)
	}

	if widget.Type != "chart" {
		t.Errorf("Expected Type to be 'chart', got %s", widget.Type)
	}

	if widget.Position.Width != 6 {
		t.Errorf("Expected Position.Width to be 6, got %d", widget.Position.Width)
	}
}

func TestPosition_Values(t *testing.T) {
	position := Position{
		X:      10,
		Y:      20,
		Width:  30,
		Height: 40,
	}

	if position.X != 10 || position.Y != 20 || position.Width != 30 || position.Height != 40 {
		t.Error("Position values don't match expected values")
	}
}

func TestDashboardSummary_Creation(t *testing.T) {
	summary := &DashboardSummary{
		TotalAppointments:  150,
		TotalUsers:         50,
		TotalPatients:      80,
		TotalSessions:      120,
		RoomUtilization:    75.5,
		AppointmentRate:    85.2,
		ActiveUsers:        45,
		CompletionRate:     90.0,
	}

	if summary.TotalAppointments != 150 {
		t.Errorf("Expected TotalAppointments to be 150, got %d", summary.TotalAppointments)
	}

	if summary.RoomUtilization != 75.5 {
		t.Errorf("Expected RoomUtilization to be 75.5, got %f", summary.RoomUtilization)
	}

	if summary.CompletionRate != 90.0 {
		t.Errorf("Expected CompletionRate to be 90.0, got %f", summary.CompletionRate)
	}
}

func TestAppointmentMetrics_Creation(t *testing.T) {
	metrics := &AppointmentMetrics{
		Total:     100,
		Completed: 75,
		Cancelled: 10,
		Pending:   15,
		ByStatus: map[string]int{
			"completed": 75,
			"cancelled": 10,
			"pending":   15,
		},
		ByType: map[string]int{
			"primera_vez": 30,
			"seguimiento": 70,
		},
		Trend: TimeSeriesData{
			Labels: []string{"Lun", "Mar", "Mie", "Jue", "Vie"},
			Values: []float64{20, 25, 18, 22, 15},
		},
	}

	if metrics.Total != 100 {
		t.Errorf("Expected Total to be 100, got %d", metrics.Total)
	}

	if metrics.ByStatus["completed"] != 75 {
		t.Errorf("Expected ByStatus.completed to be 75, got %d", metrics.ByStatus["completed"])
	}

	if len(metrics.Trend.Labels) != 5 {
		t.Errorf("Expected Trend.Labels length to be 5, got %d", len(metrics.Trend.Labels))
	}
}

func TestTimeSeriesData_Creation(t *testing.T) {
	data := TimeSeriesData{
		Labels: []string{"Jan", "Feb", "Mar"},
		Values: []float64{10.5, 20.3, 15.7},
	}

	if len(data.Labels) != len(data.Values) {
		t.Error("Labels and Values lengths don't match")
	}

	if data.Values[1] != 20.3 {
		t.Errorf("Expected Values[1] to be 20.3, got %f", data.Values[1])
	}
}

func TestMetric_WithMetadata(t *testing.T) {
	metric := &Metric{
		ID:         primitive.NewObjectID(),
		MetricType: MetricTypeUserActivity,
		Data: map[string]interface{}{
			"active_users": 50,
		},
		Timestamp: time.Now(),
		Metadata: map[string]interface{}{
			"source":           "user_service",
			"aggregation_type": "scheduled",
			"event_type":       "user.login",
		},
	}

	if metric.Metadata["source"] != "user_service" {
		t.Errorf("Expected Metadata.source to be 'user_service', got %v", metric.Metadata["source"])
	}

	if metric.Metadata["aggregation_type"] != "scheduled" {
		t.Errorf("Expected Metadata.aggregation_type to be 'scheduled', got %v", metric.Metadata["aggregation_type"])
	}
}
