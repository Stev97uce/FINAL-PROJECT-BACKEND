package events

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"
	"github.com/stev97uce/appointment-service/pkg/config"
)

type RabbitMQPublisher struct {
	conn    *amqp.Connection
	channel *amqp.Channel
	config  *config.Config
}

type Event struct {
	EventType string      `json:"event_type"`
	Timestamp string      `json:"timestamp"`
	Service   string      `json:"service"`
	Data      interface{} `json:"data"`
}

func NewRabbitMQPublisher(cfg *config.Config) *RabbitMQPublisher {
	return &RabbitMQPublisher{config: cfg}
}

func (r *RabbitMQPublisher) Connect() error {
	var err error

	r.conn, err = amqp.Dial(r.config.GetRabbitMQURL())
	if err != nil {
		return fmt.Errorf("failed to connect to RabbitMQ: %w", err)
	}

	r.channel, err = r.conn.Channel()
	if err != nil {
		return fmt.Errorf("failed to open channel: %w", err)
	}

	// Declare exchange
	err = r.channel.ExchangeDeclare(
		r.config.RabbitMQExchange, // name
		"topic",                    // type
		true,                       // durable
		false,                      // auto-deleted
		false,                      // internal
		false,                      // no-wait
		nil,                        // arguments
	)
	if err != nil {
		return fmt.Errorf("failed to declare exchange: %w", err)
	}

	log.Println("Connected to RabbitMQ")
	return nil
}

func (r *RabbitMQPublisher) Publish(routingKey string, data interface{}) error {
	if r.channel == nil {
		return fmt.Errorf("RabbitMQ channel not initialized")
	}

	event := Event{
		EventType: routingKey,
		Timestamp: time.Now().Format(time.RFC3339),
		Service:   "appointment-service",
		Data:      data,
	}

	body, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	err = r.channel.PublishWithContext(
		ctx,
		r.config.RabbitMQExchange, // exchange
		routingKey,                 // routing key
		false,                      // mandatory
		false,                      // immediate
		amqp.Publishing{
			ContentType: "application/json",
			Body:        body,
			Timestamp:   time.Now(),
		},
	)

	if err != nil {
		return fmt.Errorf("failed to publish event: %w", err)
	}

	log.Printf("Published event: %s", routingKey)
	return nil
}

func (r *RabbitMQPublisher) Close() error {
	if r.channel != nil {
		r.channel.Close()
	}
	if r.conn != nil {
		r.conn.Close()
	}
	log.Println("RabbitMQ connection closed")
	return nil
}

// Event types
const (
	EventAppointmentCreated   = "appointment.created"
	EventAppointmentConfirmed = "appointment.confirmed"
	EventAppointmentCancelled = "appointment.cancelled"
	EventAppointmentCompleted = "appointment.completed"
	EventAppointmentNoShow    = "appointment.no_show"
	EventReminder48h          = "appointment.reminder_48h"
	EventReminder24h          = "appointment.reminder_24h"
)
