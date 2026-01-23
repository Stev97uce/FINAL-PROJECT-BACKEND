package clients

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

	"github.com/stev97uce/analytics-service/pkg/config"
)

// ServiceClient handles HTTP requests to other microservices
type ServiceClient struct {
	httpClient *http.Client
	config     *config.Config
	authToken  string
}

// NewServiceClient creates a new service client
func NewServiceClient(cfg *config.Config, authToken string) *ServiceClient {
	return &ServiceClient{
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
		config:    cfg,
		authToken: authToken,
	}
}

// makeRequest makes an HTTP GET request to a service
func (c *ServiceClient) makeRequest(ctx context.Context, url string) (map[string]interface{}, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	// Add auth token if available
	if c.authToken != "" {
		req.Header.Set("Authorization", "Bearer "+c.authToken)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("unexpected status code %d: %s", resp.StatusCode, string(body))
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	var result map[string]interface{}
	err = json.Unmarshal(body, &result)
	if err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	return result, nil
}

// GetAppointmentStats fetches appointment statistics from Appointment Service
func (c *ServiceClient) GetAppointmentStats(ctx context.Context) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/api/v1/appointments/stats", c.config.AppointmentServiceURL)
	log.Printf("📊 Fetching appointment stats from: %s", url)
	
	data, err := c.makeRequest(ctx, url)
	if err != nil {
		return nil, fmt.Errorf("failed to get appointment stats: %w", err)
	}
	
	return data, nil
}

// GetUserStats fetches user statistics from User Service
func (c *ServiceClient) GetUserStats(ctx context.Context) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/api/v1/users/stats", c.config.UserServiceURL)
	log.Printf("📊 Fetching user stats from: %s", url)
	
	data, err := c.makeRequest(ctx, url)
	if err != nil {
		return nil, fmt.Errorf("failed to get user stats: %w", err)
	}
	
	return data, nil
}

// GetPatientStats fetches patient statistics from Patient Service
func (c *ServiceClient) GetPatientStats(ctx context.Context) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/api/v1/patients/stats", c.config.PatientServiceURL)
	log.Printf("📊 Fetching patient stats from: %s", url)
	
	data, err := c.makeRequest(ctx, url)
	if err != nil {
		return nil, fmt.Errorf("failed to get patient stats: %w", err)
	}
	
	return data, nil
}

// GetRoomUtilization fetches room utilization from Room Service
func (c *ServiceClient) GetRoomUtilization(ctx context.Context) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/api/v1/rooms/utilization", c.config.RoomServiceURL)
	log.Printf("📊 Fetching room utilization from: %s", url)
	
	data, err := c.makeRequest(ctx, url)
	if err != nil {
		return nil, fmt.Errorf("failed to get room utilization: %w", err)
	}
	
	return data, nil
}

// GetClinicalStats fetches clinical statistics from Clinical Service
func (c *ServiceClient) GetClinicalStats(ctx context.Context) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/api/v1/clinical/stats", c.config.ClinicalServiceURL)
	log.Printf("📊 Fetching clinical stats from: %s", url)
	
	data, err := c.makeRequest(ctx, url)
	if err != nil {
		return nil, fmt.Errorf("failed to get clinical stats: %w", err)
	}
	
	return data, nil
}

// GetSupervisionStats fetches supervision statistics from Supervision Service
func (c *ServiceClient) GetSupervisionStats(ctx context.Context) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/api/v1/supervision/stats", c.config.SupervisionServiceURL)
	log.Printf("📊 Fetching supervision stats from: %s", url)
	
	data, err := c.makeRequest(ctx, url)
	if err != nil {
		return nil, fmt.Errorf("failed to get supervision stats: %w", err)
	}
	
	return data, nil
}

// GetSystemHealth fetches health status from all services
func (c *ServiceClient) GetSystemHealth(ctx context.Context) (map[string]interface{}, error) {
	log.Println("📊 Fetching system health from all services")
	
	services := map[string]string{
		"auth_service":        c.config.AuthServiceURL + "/health",
		"user_service":        c.config.UserServiceURL + "/health",
		"patient_service":     c.config.PatientServiceURL + "/health",
		"appointment_service": c.config.AppointmentServiceURL + "/health",
		"room_service":        c.config.RoomServiceURL + "/health",
		"clinical_service":    c.config.ClinicalServiceURL + "/health",
		"supervision_service": c.config.SupervisionServiceURL + "/health",
		"notification_service": c.config.NotificationServiceURL + "/health",
		"reporting_service":   c.config.ReportingServiceURL + "/health",
	}
	
	healthData := make(map[string]interface{})
	healthyCount := 0
	unhealthyCount := 0
	
	for serviceName, url := range services {
		data, err := c.makeRequest(ctx, url)
		if err != nil {
			log.Printf("⚠️  %s is unhealthy: %v", serviceName, err)
			healthData[serviceName] = map[string]interface{}{
				"status": "unhealthy",
				"error":  err.Error(),
			}
			unhealthyCount++
		} else {
			log.Printf("✅ %s is healthy", serviceName)
			healthData[serviceName] = data
			healthyCount++
		}
	}
	
	healthData["summary"] = map[string]interface{}{
		"total_services": len(services),
		"healthy":        healthyCount,
		"unhealthy":      unhealthyCount,
		"health_percentage": float64(healthyCount) / float64(len(services)) * 100,
	}
	
	return healthData, nil
}

// AggregateAllStats aggregates statistics from all services
func (c *ServiceClient) AggregateAllStats(ctx context.Context) (map[string]interface{}, error) {
	log.Println("📊 Aggregating statistics from all services")
	
	aggregatedStats := make(map[string]interface{})
	
	// Appointment stats
	if appointmentStats, err := c.GetAppointmentStats(ctx); err == nil {
		aggregatedStats["appointment_stats"] = appointmentStats
	} else {
		log.Printf("⚠️  Failed to get appointment stats: %v", err)
		aggregatedStats["appointment_stats"] = map[string]interface{}{"error": err.Error()}
	}
	
	// User stats
	if userStats, err := c.GetUserStats(ctx); err == nil {
		aggregatedStats["user_stats"] = userStats
	} else {
		log.Printf("⚠️  Failed to get user stats: %v", err)
		aggregatedStats["user_stats"] = map[string]interface{}{"error": err.Error()}
	}
	
	// Patient stats
	if patientStats, err := c.GetPatientStats(ctx); err == nil {
		aggregatedStats["patient_stats"] = patientStats
	} else {
		log.Printf("⚠️  Failed to get patient stats: %v", err)
		aggregatedStats["patient_stats"] = map[string]interface{}{"error": err.Error()}
	}
	
	// Room utilization
	if roomStats, err := c.GetRoomUtilization(ctx); err == nil {
		aggregatedStats["room_utilization"] = roomStats
	} else {
		log.Printf("⚠️  Failed to get room utilization: %v", err)
		aggregatedStats["room_utilization"] = map[string]interface{}{"error": err.Error()}
	}
	
	// Clinical stats
	if clinicalStats, err := c.GetClinicalStats(ctx); err == nil {
		aggregatedStats["clinical_stats"] = clinicalStats
	} else {
		log.Printf("⚠️  Failed to get clinical stats: %v", err)
		aggregatedStats["clinical_stats"] = map[string]interface{}{"error": err.Error()}
	}
	
	// Supervision stats
	if supervisionStats, err := c.GetSupervisionStats(ctx); err == nil {
		aggregatedStats["supervision_stats"] = supervisionStats
	} else {
		log.Printf("⚠️  Failed to get supervision stats: %v", err)
		aggregatedStats["supervision_stats"] = map[string]interface{}{"error": err.Error()}
	}
	
	// System health
	if systemHealth, err := c.GetSystemHealth(ctx); err == nil {
		aggregatedStats["system_health"] = systemHealth
	} else {
		log.Printf("⚠️  Failed to get system health: %v", err)
		aggregatedStats["system_health"] = map[string]interface{}{"error": err.Error()}
	}
	
	aggregatedStats["timestamp"] = time.Now().UTC()
	
	log.Println("✅ Successfully aggregated statistics from all services")
	return aggregatedStats, nil
}
