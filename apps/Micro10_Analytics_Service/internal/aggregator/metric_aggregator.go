package aggregator

import (
	"context"
	"log"
	"time"

	"github.com/stev97uce/analytics-service/internal/clients"
	"github.com/stev97uce/analytics-service/internal/models"
	"github.com/stev97uce/analytics-service/internal/services"
	"github.com/stev97uce/analytics-service/pkg/config"
)

// MetricAggregator periodically aggregates metrics from all services
type MetricAggregator struct {
	serviceClient *clients.ServiceClient
	metricService *services.MetricService
	config        *config.Config
	stopChan      chan bool
}

// NewMetricAggregator creates a new metric aggregator
func NewMetricAggregator(cfg *config.Config, serviceClient *clients.ServiceClient, metricService *services.MetricService) *MetricAggregator {
	return &MetricAggregator{
		serviceClient: serviceClient,
		metricService: metricService,
		config:        cfg,
		stopChan:      make(chan bool),
	}
}

// Start begins the periodic aggregation
func (a *MetricAggregator) Start() {
	log.Println("🚀 Starting Metric Aggregator...")
	
	// Run immediately on startup
	go a.aggregateAllMetrics()
	
	// Then run every 5 minutes
	ticker := time.NewTicker(5 * time.Minute)
	
	go func() {
		for {
			select {
			case <-ticker.C:
				a.aggregateAllMetrics()
			case <-a.stopChan:
				ticker.Stop()
				log.Println("🛑 Metric Aggregator stopped")
				return
			}
		}
	}()
}

// Stop stops the aggregator
func (a *MetricAggregator) Stop() {
	close(a.stopChan)
}

// aggregateAllMetrics fetches and stores metrics from all services
func (a *MetricAggregator) aggregateAllMetrics() {
	log.Println("📊 Starting metric aggregation cycle...")
	ctx := context.Background()
	
	// 1. Aggregate appointment stats
	a.aggregateAppointmentStats(ctx)
	
	// 2. Aggregate user activity
	a.aggregateUserActivity(ctx)
	
	// 3. Aggregate room utilization
	a.aggregateRoomUtilization(ctx)
	
	// 4. Aggregate clinical session stats
	a.aggregateClinicalStats(ctx)
	
	// 5. Aggregate supervision stats
	a.aggregateSupervisionStats(ctx)
	
	// 6. Aggregate system performance
	a.aggregateSystemPerformance(ctx)
	
	log.Println("✅ Metric aggregation cycle completed")
}

// aggregateAppointmentStats aggregates appointment statistics
func (a *MetricAggregator) aggregateAppointmentStats(ctx context.Context) {
	log.Println("📊 Aggregating appointment stats...")
	
	stats, err := a.serviceClient.GetAppointmentStats(ctx)
	if err != nil {
		log.Printf("⚠️  Failed to get appointment stats: %v", err)
		return
	}
	
	// Create metric
	metric := &models.Metric{
		MetricType: "appointment_stats",
		Period:     "daily",
		Data:       stats,
		Metadata: map[string]interface{}{
			"source":           "appointment_service",
			"aggregation_type": "scheduled",
			"collection_time":  time.Now().UTC(),
		},
	}
	
	err = a.metricService.CreateMetric(ctx, metric)
	if err != nil {
		log.Printf("⚠️  Failed to store appointment stats: %v", err)
	} else {
		log.Println("✅ Appointment stats aggregated successfully")
	}
}

// aggregateUserActivity aggregates user activity metrics
func (a *MetricAggregator) aggregateUserActivity(ctx context.Context) {
	log.Println("📊 Aggregating user activity...")
	
	stats, err := a.serviceClient.GetUserStats(ctx)
	if err != nil {
		log.Printf("⚠️  Failed to get user stats: %v", err)
		return
	}
	
	// Also get patient stats
	patientStats, err := a.serviceClient.GetPatientStats(ctx)
	if err != nil {
		log.Printf("⚠️  Failed to get patient stats: %v", err)
	} else {
		// Merge patient stats into user stats
		if stats == nil {
			stats = make(map[string]interface{})
		}
		stats["patient_stats"] = patientStats
	}
	
	// Create metric
	metric := &models.Metric{
		MetricType: "user_activity",
		Period:     "daily",
		Data:       stats,
		Metadata: map[string]interface{}{
			"source":           "user_service",
			"aggregation_type": "scheduled",
			"collection_time":  time.Now().UTC(),
		},
	}
	
	err = a.metricService.CreateMetric(ctx, metric)
	if err != nil {
		log.Printf("⚠️  Failed to store user activity: %v", err)
	} else {
		log.Println("✅ User activity aggregated successfully")
	}
}

// aggregateRoomUtilization aggregates room utilization metrics
func (a *MetricAggregator) aggregateRoomUtilization(ctx context.Context) {
	log.Println("📊 Aggregating room utilization...")
	
	stats, err := a.serviceClient.GetRoomUtilization(ctx)
	if err != nil {
		log.Printf("⚠️  Failed to get room utilization: %v", err)
		return
	}
	
	// Create metric
	metric := &models.Metric{
		MetricType: "room_utilization",
		Period:     "daily",
		Data:       stats,
		Metadata: map[string]interface{}{
			"source":           "room_service",
			"aggregation_type": "scheduled",
			"collection_time":  time.Now().UTC(),
		},
	}
	
	err = a.metricService.CreateMetric(ctx, metric)
	if err != nil {
		log.Printf("⚠️  Failed to store room utilization: %v", err)
	} else {
		log.Println("✅ Room utilization aggregated successfully")
	}
}

// aggregateClinicalStats aggregates clinical session statistics
func (a *MetricAggregator) aggregateClinicalStats(ctx context.Context) {
	log.Println("📊 Aggregating clinical stats...")
	
	stats, err := a.serviceClient.GetClinicalStats(ctx)
	if err != nil {
		log.Printf("⚠️  Failed to get clinical stats: %v", err)
		return
	}
	
	// Create metric
	metric := &models.Metric{
		MetricType: "session_stats",
		Period:     "daily",
		Data:       stats,
		Metadata: map[string]interface{}{
			"source":           "clinical_service",
			"aggregation_type": "scheduled",
			"collection_time":  time.Now().UTC(),
		},
	}
	
	err = a.metricService.CreateMetric(ctx, metric)
	if err != nil {
		log.Printf("⚠️  Failed to store clinical stats: %v", err)
	} else {
		log.Println("✅ Clinical stats aggregated successfully")
	}
}

// aggregateSupervisionStats aggregates supervision statistics
func (a *MetricAggregator) aggregateSupervisionStats(ctx context.Context) {
	log.Println("📊 Aggregating supervision stats...")
	
	stats, err := a.serviceClient.GetSupervisionStats(ctx)
	if err != nil {
		log.Printf("⚠️  Failed to get supervision stats: %v", err)
		return
	}
	
	// Create metric
	metric := &models.Metric{
		MetricType: "supervision_stats",
		Period:     "daily",
		Data:       stats,
		Metadata: map[string]interface{}{
			"source":           "supervision_service",
			"aggregation_type": "scheduled",
			"collection_time":  time.Now().UTC(),
		},
	}
	
	err = a.metricService.CreateMetric(ctx, metric)
	if err != nil {
		log.Printf("⚠️  Failed to store supervision stats: %v", err)
	} else {
		log.Println("✅ Supervision stats aggregated successfully")
	}
}

// aggregateSystemPerformance aggregates system-wide performance metrics
func (a *MetricAggregator) aggregateSystemPerformance(ctx context.Context) {
	log.Println("📊 Aggregating system performance...")
	
	healthData, err := a.serviceClient.GetSystemHealth(ctx)
	if err != nil {
		log.Printf("⚠️  Failed to get system health: %v", err)
		return
	}
	
	// Also get all stats for comprehensive performance view
	allStats, err := a.serviceClient.AggregateAllStats(ctx)
	if err != nil {
		log.Printf("⚠️  Failed to aggregate all stats: %v", err)
		// Continue with just health data
		allStats = make(map[string]interface{})
	}
	
	// Merge health data with all stats
	performanceData := make(map[string]interface{})
	performanceData["health"] = healthData
	performanceData["statistics"] = allStats
	performanceData["timestamp"] = time.Now().UTC()
	
	// Create metric
	metric := &models.Metric{
		MetricType: "system_performance",
		Period:     "daily",
		Data:       performanceData,
		Metadata: map[string]interface{}{
			"source":           "all_services",
			"aggregation_type": "scheduled",
			"collection_time":  time.Now().UTC(),
		},
	}
	
	err = a.metricService.CreateMetric(ctx, metric)
	if err != nil {
		log.Printf("⚠️  Failed to store system performance: %v", err)
	} else {
		log.Println("✅ System performance aggregated successfully")
	}
}
