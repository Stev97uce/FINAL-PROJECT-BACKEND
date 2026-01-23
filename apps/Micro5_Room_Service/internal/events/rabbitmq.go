package events

import (
	"context"
	"encoding/json"
	"fmt"
	"log"

	amqp "github.com/rabbitmq/amqp091-go"
	"github.com/stev97uce/room-service/pkg/config"
)

type RabbitMQPublisher struct {
	conn     *amqp.Connection
	channel  *amqp.Channel
	exchange string
}

type Event struct {
	Type      string      `json:"type"`
	Aggregate string      `json:"aggregate"`
	Data      interface{} `json:"data"`
	Timestamp string      `json:"timestamp"`
}

func NewRabbitMQPublisher() (*RabbitMQPublisher, error) {
	conn, err := amqp.Dial(config.GetRabbitMQURL())
	if err != nil {
		return nil, fmt.Errorf("failed to connect to RabbitMQ: %w", err)
	}

	channel, err := conn.Channel()
	if err != nil {
		conn.Close()
		return nil, fmt.Errorf("failed to open channel: %w", err)
	}

	// Declare exchange
	exchange := config.AppConfig.RabbitMQExchange
	err = channel.ExchangeDeclare(
		exchange, // name
		"topic",  // type
		true,     // durable
		false,    // auto-deleted
		false,    // internal
		false,    // no-wait
		nil,      // arguments
	)
	if err != nil {
		channel.Close()
		conn.Close()
		return nil, fmt.Errorf("failed to declare exchange: %w", err)
	}

	log.Println("Connected to RabbitMQ")

	return &RabbitMQPublisher{
		conn:     conn,
		channel:  channel,
		exchange: exchange,
	}, nil
}

func (p *RabbitMQPublisher) PublishEvent(ctx context.Context, routingKey string, event Event) error {
	body, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	err = p.channel.PublishWithContext(
		ctx,
		p.exchange, // exchange
		routingKey, // routing key
		false,      // mandatory
		false,      // immediate
		amqp.Publishing{
			ContentType: "application/json",
			Body:        body,
		},
	)
	if err != nil {
		return fmt.Errorf("failed to publish event: %w", err)
	}

	log.Printf("Published event: %s to routing key: %s", event.Type, routingKey)
	return nil
}

func (p *RabbitMQPublisher) Close() error {
	if p.channel != nil {
		if err := p.channel.Close(); err != nil {
			return err
		}
	}
	if p.conn != nil {
		if err := p.conn.Close(); err != nil {
			return err
		}
	}
	log.Println("RabbitMQ connection closed")
	return nil
}
