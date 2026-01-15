package events

import (
	"context"
	"encoding/json"
	"fmt"
	"log"

	"github.com/stev97uce/analytics-service/internal/services"
	"github.com/stev97uce/analytics-service/pkg/config"
	"github.com/streadway/amqp"
)

// EventMessage represents a message from RabbitMQ
type EventMessage struct {
	Event     string                 `json:"event"`
	Data      map[string]interface{} `json:"data"`
	Timestamp string                 `json:"timestamp"`
}

// RabbitMQConsumer handles consuming events from RabbitMQ
type RabbitMQConsumer struct {
	conn          *amqp.Connection
	channel       *amqp.Channel
	metricService *services.MetricService
	config        *config.Config
	done          chan bool
}

// NewRabbitMQConsumer creates a new RabbitMQ consumer
func NewRabbitMQConsumer(cfg *config.Config, metricService *services.MetricService) *RabbitMQConsumer {
	return &RabbitMQConsumer{
		config:        cfg,
		metricService: metricService,
		done:          make(chan bool),
	}
}

// Connect establishes connection to RabbitMQ
func (c *RabbitMQConsumer) Connect() error {
	url := fmt.Sprintf("amqp://%s:%s@%s:%s/",
		c.config.RabbitMQUser,
		c.config.RabbitMQPassword,
		c.config.RabbitMQHost,
		c.config.RabbitMQPort,
	)

	conn, err := amqp.Dial(url)
	if err != nil {
		return fmt.Errorf("failed to connect to RabbitMQ: %w", err)
	}

	ch, err := conn.Channel()
	if err != nil {
		conn.Close()
		return fmt.Errorf("failed to open channel: %w", err)
	}

	// Declare exchange
	err = ch.ExchangeDeclare(
		c.config.RabbitMQExchange, // name
		"topic",                    // type
		true,                       // durable
		false,                      // auto-deleted
		false,                      // internal
		false,                      // no-wait
		nil,                        // arguments
	)
	if err != nil {
		ch.Close()
		conn.Close()
		return fmt.Errorf("failed to declare exchange: %w", err)
	}

	c.conn = conn
	c.channel = ch

	log.Println("✅ Connected to RabbitMQ successfully")
	return nil
}

// StartConsuming starts consuming events from RabbitMQ
func (c *RabbitMQConsumer) StartConsuming() error {
	if c.channel == nil {
		return fmt.Errorf("channel is not initialized")
	}

	// Declare queue for analytics service
	queueName := "analytics_service_queue"
	queue, err := c.channel.QueueDeclare(
		queueName, // name
		true,      // durable
		false,     // delete when unused
		false,     // exclusive
		false,     // no-wait
		nil,       // arguments
	)
	if err != nil {
		return fmt.Errorf("failed to declare queue: %w", err)
	}

	// Bind to multiple routing keys (events from all services)
	routingKeys := []string{
		// Auth Service events
		"user.registered",
		"user.verified",
		"password.reset_requested",
		
		// Patient Service events
		"patient.created",
		"patient.updated",
		"patient.deleted",
		"expediente.created",
		"expediente.updated",
		"expediente.closed",
		
		// Appointment Service events
		"appointment.created",
		"appointment.confirmed",
		"appointment.cancelled",
		"appointment.rescheduled",
		
		// Room Service events
		"room.created",
		"room.updated",
		"room.booked",
		"room.released",
		
		// Clinical Service events
		"clinical.record.created",
		"clinical.session.recorded",
		"clinical.note.created",
		"clinical.goal.achieved",
		
		// Supervision Service events
		"supervision.session.created",
		"supervision.feedback_added",
		"supervision.assignment.created",
		
		// Notification Service events
		"notification.sent",
		"notification.failed",
		
		// Reporting Service events
		"report.generated",
		"report.completed",
	}

	for _, routingKey := range routingKeys {
		err = c.channel.QueueBind(
			queue.Name,                 // queue name
			routingKey,                 // routing key
			c.config.RabbitMQExchange, // exchange
			false,
			nil,
		)
		if err != nil {
			return fmt.Errorf("failed to bind queue for %s: %w", routingKey, err)
		}
	}

	// Set QoS
	err = c.channel.Qos(
		1,     // prefetch count
		0,     // prefetch size
		false, // global
	)
	if err != nil {
		return fmt.Errorf("failed to set QoS: %w", err)
	}

	// Start consuming
	msgs, err := c.channel.Consume(
		queue.Name, // queue
		"",         // consumer
		false,      // auto-ack
		false,      // exclusive
		false,      // no-local
		false,      // no-wait
		nil,        // args
	)
	if err != nil {
		return fmt.Errorf("failed to register consumer: %w", err)
	}

	log.Printf("📡 Analytics Service listening to %d event types from RabbitMQ", len(routingKeys))

	// Start consuming in a goroutine
	go c.handleMessages(msgs)

	return nil
}

// handleMessages processes incoming messages
func (c *RabbitMQConsumer) handleMessages(msgs <-chan amqp.Delivery) {
	for msg := range msgs {
		go c.processMessage(msg)
	}
}

// processMessage processes a single message
func (c *RabbitMQConsumer) processMessage(msg amqp.Delivery) {
	defer func() {
		if r := recover(); r != nil {
			log.Printf("❌ Recovered from panic in processMessage: %v", r)
			msg.Nack(false, true) // requeue on panic
		}
	}()

	// Parse event message
	var event EventMessage
	err := json.Unmarshal(msg.Body, &event)
	if err != nil {
		log.Printf("❌ Failed to parse event message: %v", err)
		msg.Nack(false, false) // don't requeue invalid messages
		return
	}

	log.Printf("📥 Processing event: %s", event.Event)

	// Route to appropriate handler
	ctx := context.Background()
	switch event.Event {
	// Auth Service events
	case "user.registered":
		c.handleUserRegistered(ctx, event)
	case "user.verified":
		c.handleUserVerified(ctx, event)
	
	// Patient Service events
	case "patient.created":
		c.handlePatientCreated(ctx, event)
	case "patient.updated", "patient.deleted":
		c.handlePatientUpdated(ctx, event)
	
	// Appointment Service events
	case "appointment.created":
		c.handleAppointmentCreated(ctx, event)
	case "appointment.confirmed", "appointment.cancelled", "appointment.rescheduled":
		c.handleAppointmentUpdated(ctx, event)
	
	// Room Service events
	case "room.created":
		c.handleRoomCreated(ctx, event)
	case "room.booked", "room.released":
		c.handleRoomActivity(ctx, event)
	
	// Clinical Service events
	case "clinical.record.created", "clinical.session.recorded":
		c.handleClinicalActivity(ctx, event)
	case "clinical.note.created", "clinical.goal.achieved":
		c.handleClinicalNote(ctx, event)
	
	// Supervision Service events
	case "supervision.session.created", "supervision.feedback_added":
		c.handleSupervisionActivity(ctx, event)
	
	// Notification Service events
	case "notification.sent", "notification.failed":
		c.handleNotificationSent(ctx, event)
	
	// Reporting Service events
	case "report.generated", "report.completed":
		c.handleReportGenerated(ctx, event)
	
	default:
		log.Printf("⚠️  Unhandled event type: %s", event.Event)
	}

	// Acknowledge message
	err = msg.Ack(false)
	if err != nil {
		log.Printf("❌ Failed to ack message: %v", err)
	}
}

// Event Handlers

func (c *RabbitMQConsumer) handleUserRegistered(ctx context.Context, event EventMessage) {
	log.Printf("📊 Generating user_activity metric for user.registered")
	
	// Extract user data
	userID := event.Data["user_id"]
	role := event.Data["rol"]
	
	// Create metric
	metric := map[string]interface{}{
		"metric_type": "user_activity",
		"period":      "daily",
		"data": map[string]interface{}{
			"new_registrations": 1,
			"role":              role,
			"user_id":           userID,
		},
		"metadata": map[string]interface{}{
			"event_type": "user.registered",
			"source":     "auth_service",
		},
	}
	
	// Store metric (will be aggregated later)
	c.storeEventMetric(ctx, metric)
}

func (c *RabbitMQConsumer) handleUserVerified(ctx context.Context, event EventMessage) {
	log.Printf("📊 Generating user_activity metric for user.verified")
	
	metric := map[string]interface{}{
		"metric_type": "user_activity",
		"period":      "daily",
		"data": map[string]interface{}{
			"verified_users": 1,
			"user_id":        event.Data["user_id"],
		},
		"metadata": map[string]interface{}{
			"event_type": "user.verified",
			"source":     "auth_service",
		},
	}
	
	c.storeEventMetric(ctx, metric)
}

func (c *RabbitMQConsumer) handlePatientCreated(ctx context.Context, event EventMessage) {
	log.Printf("📊 Generating user_activity metric for patient.created")
	
	metric := map[string]interface{}{
		"metric_type": "user_activity",
		"period":      "daily",
		"data": map[string]interface{}{
			"new_patients": 1,
			"patient_id":   event.Data["patient_id"],
		},
		"metadata": map[string]interface{}{
			"event_type": "patient.created",
			"source":     "patient_service",
		},
	}
	
	c.storeEventMetric(ctx, metric)
}

func (c *RabbitMQConsumer) handlePatientUpdated(ctx context.Context, event EventMessage) {
	log.Printf("📊 Tracking patient activity: %s", event.Event)
	
	metric := map[string]interface{}{
		"metric_type": "user_activity",
		"period":      "daily",
		"data": map[string]interface{}{
			"patient_updates": 1,
			"patient_id":      event.Data["patient_id"],
		},
		"metadata": map[string]interface{}{
			"event_type": event.Event,
			"source":     "patient_service",
		},
	}
	
	c.storeEventMetric(ctx, metric)
}

func (c *RabbitMQConsumer) handleAppointmentCreated(ctx context.Context, event EventMessage) {
	log.Printf("📊 Generating appointment_stats metric for appointment.created")
	
	metric := map[string]interface{}{
		"metric_type": "appointment_stats",
		"period":      "daily",
		"data": map[string]interface{}{
			"total_appointments": 1,
			"created":            1,
			"appointment_id":     event.Data["appointment_id"],
			"status":             event.Data["status"],
		},
		"metadata": map[string]interface{}{
			"event_type": "appointment.created",
			"source":     "appointment_service",
		},
	}
	
	c.storeEventMetric(ctx, metric)
}

func (c *RabbitMQConsumer) handleAppointmentUpdated(ctx context.Context, event EventMessage) {
	log.Printf("📊 Generating appointment_stats metric for %s", event.Event)
	
	metric := map[string]interface{}{
		"metric_type": "appointment_stats",
		"period":      "daily",
		"data": map[string]interface{}{
			"appointment_id": event.Data["appointment_id"],
			"status":         event.Data["status"],
		},
		"metadata": map[string]interface{}{
			"event_type": event.Event,
			"source":     "appointment_service",
		},
	}
	
	if event.Event == "appointment.cancelled" {
		metric["data"].(map[string]interface{})["cancelled"] = 1
	} else if event.Event == "appointment.confirmed" {
		metric["data"].(map[string]interface{})["confirmed"] = 1
	}
	
	c.storeEventMetric(ctx, metric)
}

func (c *RabbitMQConsumer) handleRoomCreated(ctx context.Context, event EventMessage) {
	log.Printf("📊 Generating room_utilization metric for room.created")
	
	metric := map[string]interface{}{
		"metric_type": "room_utilization",
		"period":      "daily",
		"data": map[string]interface{}{
			"total_rooms": 1,
			"room_id":     event.Data["room_id"],
			"room_type":   event.Data["tipo_sala"],
		},
		"metadata": map[string]interface{}{
			"event_type": "room.created",
			"source":     "room_service",
		},
	}
	
	c.storeEventMetric(ctx, metric)
}

func (c *RabbitMQConsumer) handleRoomActivity(ctx context.Context, event EventMessage) {
	log.Printf("📊 Generating room_utilization metric for %s", event.Event)
	
	metric := map[string]interface{}{
		"metric_type": "room_utilization",
		"period":      "daily",
		"data": map[string]interface{}{
			"room_id": event.Data["room_id"],
		},
		"metadata": map[string]interface{}{
			"event_type": event.Event,
			"source":     "room_service",
		},
	}
	
	if event.Event == "room.booked" {
		metric["data"].(map[string]interface{})["bookings"] = 1
		metric["data"].(map[string]interface{})["occupied"] = 1
	} else if event.Event == "room.released" {
		metric["data"].(map[string]interface{})["released"] = 1
		metric["data"].(map[string]interface{})["available"] = 1
	}
	
	c.storeEventMetric(ctx, metric)
}

func (c *RabbitMQConsumer) handleClinicalActivity(ctx context.Context, event EventMessage) {
	log.Printf("📊 Generating session_stats metric for %s", event.Event)
	
	metric := map[string]interface{}{
		"metric_type": "session_stats",
		"period":      "daily",
		"data": map[string]interface{}{
			"total_sessions": 1,
			"completed":      1,
		},
		"metadata": map[string]interface{}{
			"event_type": event.Event,
			"source":     "clinical_service",
		},
	}
	
	c.storeEventMetric(ctx, metric)
}

func (c *RabbitMQConsumer) handleClinicalNote(ctx context.Context, event EventMessage) {
	log.Printf("📊 Tracking clinical activity: %s", event.Event)
	
	metric := map[string]interface{}{
		"metric_type": "session_stats",
		"period":      "daily",
		"data": map[string]interface{}{
			"notes_created": 1,
		},
		"metadata": map[string]interface{}{
			"event_type": event.Event,
			"source":     "clinical_service",
		},
	}
	
	if event.Event == "clinical.goal.achieved" {
		metric["data"].(map[string]interface{})["goals_achieved"] = 1
	}
	
	c.storeEventMetric(ctx, metric)
}

func (c *RabbitMQConsumer) handleSupervisionActivity(ctx context.Context, event EventMessage) {
	log.Printf("📊 Generating supervision_stats metric for %s", event.Event)
	
	metric := map[string]interface{}{
		"metric_type": "supervision_stats",
		"period":      "daily",
		"data": map[string]interface{}{
			"total_sessions": 1,
		},
		"metadata": map[string]interface{}{
			"event_type": event.Event,
			"source":     "supervision_service",
		},
	}
	
	if event.Event == "supervision.feedback_added" {
		metric["data"].(map[string]interface{})["feedback_provided"] = 1
	}
	
	c.storeEventMetric(ctx, metric)
}

func (c *RabbitMQConsumer) handleNotificationSent(ctx context.Context, event EventMessage) {
	log.Printf("📊 Tracking notification: %s", event.Event)
	
	metric := map[string]interface{}{
		"metric_type": "system_performance",
		"period":      "daily",
		"data": map[string]interface{}{
			"notifications_sent": 1,
		},
		"metadata": map[string]interface{}{
			"event_type": event.Event,
			"source":     "notification_service",
		},
	}
	
	if event.Event == "notification.failed" {
		metric["data"].(map[string]interface{})["notifications_failed"] = 1
		delete(metric["data"].(map[string]interface{}), "notifications_sent")
	}
	
	c.storeEventMetric(ctx, metric)
}

func (c *RabbitMQConsumer) handleReportGenerated(ctx context.Context, event EventMessage) {
	log.Printf("📊 Tracking report generation: %s", event.Event)
	
	metric := map[string]interface{}{
		"metric_type": "system_performance",
		"period":      "daily",
		"data": map[string]interface{}{
			"reports_generated": 1,
			"report_type":       event.Data["report_type"],
		},
		"metadata": map[string]interface{}{
			"event_type": event.Event,
			"source":     "reporting_service",
		},
	}
	
	c.storeEventMetric(ctx, metric)
}

// storeEventMetric stores the event-based metric
func (c *RabbitMQConsumer) storeEventMetric(ctx context.Context, metricData map[string]interface{}) {
	// This will be handled by the MetricService
	// For now, just log the metric
	log.Printf("💾 Storing event metric: %s", metricData["metric_type"])
	
	// TODO: Integrate with MetricService to store in MongoDB
	// Example: c.metricService.CreateMetricFromEvent(ctx, metricData)
}

// Close closes the RabbitMQ connection
func (c *RabbitMQConsumer) Close() error {
	if c.channel != nil {
		c.channel.Close()
	}
	if c.conn != nil {
		c.conn.Close()
	}
	log.Println("🔌 RabbitMQ consumer closed")
	return nil
}
