package models

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

type MetricType string

const (
	MetricTypeAppointmentStats  MetricType = "appointment_stats"
	MetricTypeUserActivity      MetricType = "user_activity"
	MetricTypeRoomUtilization   MetricType = "room_utilization"
	MetricTypeSessionStats      MetricType = "session_stats"
	MetricTypeSupervisionStats  MetricType = "supervision_stats"
	MetricTypeSystemPerformance MetricType = "system_performance"
)

type Metric struct {
	ID         primitive.ObjectID     `bson:"_id,omitempty" json:"id"`
	MetricType MetricType             `bson:"metric_type" json:"metric_type"`
	Data       map[string]interface{} `bson:"data" json:"data"`
	Timestamp  time.Time              `bson:"timestamp" json:"timestamp"`
	Period     string                 `bson:"period,omitempty" json:"period,omitempty"`
	CreatedAt  time.Time              `bson:"created_at" json:"created_at"`
}

type Dashboard struct {
	ID          primitive.ObjectID     `bson:"_id,omitempty" json:"id"`
	Name        string                 `bson:"name" json:"name"`
	Description string                 `bson:"description,omitempty" json:"description,omitempty"`
	Widgets     []Widget               `bson:"widgets" json:"widgets"`
	UserID      int                    `bson:"user_id" json:"user_id"`
	IsPublic    bool                   `bson:"is_public" json:"is_public"`
	CreatedAt   time.Time              `bson:"created_at" json:"created_at"`
	UpdatedAt   time.Time              `bson:"updated_at" json:"updated_at"`
}

type Widget struct {
	ID         string                 `bson:"id" json:"id"`
	Title      string                 `bson:"title" json:"title"`
	Type       string                 `bson:"type" json:"type"`
	MetricType MetricType             `bson:"metric_type" json:"metric_type"`
	Config     map[string]interface{} `bson:"config,omitempty" json:"config,omitempty"`
	Position   Position               `bson:"position" json:"position"`
}

type Position struct {
	X      int `bson:"x" json:"x"`
	Y      int `bson:"y" json:"y"`
	Width  int `bson:"width" json:"width"`
	Height int `bson:"height" json:"height"`
}

type TimeSeriesData struct {
	Labels []string  `json:"labels"`
	Values []float64 `json:"values"`
}

type DashboardSummary struct {
	TotalAppointments  int     `json:"total_appointments"`
	TotalUsers         int     `json:"total_users"`
	TotalPatients      int     `json:"total_patients"`
	TotalSessions      int     `json:"total_sessions"`
	RoomUtilization    float64 `json:"room_utilization"`
	AppointmentRate    float64 `json:"appointment_rate"`
	ActiveUsers        int     `json:"active_users"`
	CompletionRate     float64 `json:"completion_rate"`
}

type AppointmentMetrics struct {
	Total      int                    `json:"total"`
	Completed  int                    `json:"completed"`
	Cancelled  int                    `json:"cancelled"`
	Pending    int                    `json:"pending"`
	ByStatus   map[string]int         `json:"by_status"`
	ByType     map[string]int         `json:"by_type"`
	Trend      TimeSeriesData         `json:"trend"`
}

type RoomMetrics struct {
	TotalRooms      int                    `json:"total_rooms"`
	AvailableRooms  int                    `json:"available_rooms"`
	OccupiedRooms   int                    `json:"occupied_rooms"`
	Utilization     float64                `json:"utilization"`
	UtilizationByRoom map[string]float64   `json:"utilization_by_room"`
}

type UserMetrics struct {
	TotalUsers    int            `json:"total_users"`
	ActiveUsers   int            `json:"active_users"`
	ByRole        map[string]int `json:"by_role"`
	NewUsers      int            `json:"new_users"`
	Trend         TimeSeriesData `json:"trend"`
}
