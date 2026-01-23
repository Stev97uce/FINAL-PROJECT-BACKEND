package events

import (
	"encoding/json"
	"log"

	"github.com/stev97uce/analytics-service/pkg/config"
	"github.com/streadway/amqp"
)

type RabbitMQPublisher struct {
	conn    *amqp.Connection
	channel *amqp.Channel
}

func NewRabbitMQPublisher() (*RabbitMQPublisher, error) {
	conn, err := amqp.Dial(config.GetRabbitMQURL())
	if err != nil {
		return nil, err
	}

	channel, err := conn.Channel()
	if err != nil {
		conn.Close()
		return nil, err
	}

	err = channel.ExchangeDeclare(
		config.AppConfig.RabbitMQExchange,
		"topic",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		channel.Close()
		conn.Close()
		return nil, err
	}

	log.Println("RabbitMQ publisher initialized successfully")
	return &RabbitMQPublisher{
		conn:    conn,
		channel: channel,
	}, nil
}

func (p *RabbitMQPublisher) Publish(routingKey string, data interface{}) error {
	body, err := json.Marshal(data)
	if err != nil {
		return err
	}

	err = p.channel.Publish(
		config.AppConfig.RabbitMQExchange,
		routingKey,
		false,
		false,
		amqp.Publishing{
			ContentType: "application/json",
			Body:        body,
		},
	)
	
	if err != nil {
		log.Printf("Error publishing message to %s: %v", routingKey, err)
		return err
	}

	log.Printf("Published message to routing key: %s", routingKey)
	return nil
}

func (p *RabbitMQPublisher) Close() {
	if p.channel != nil {
		p.channel.Close()
	}
	if p.conn != nil {
		p.conn.Close()
	}
	log.Println("RabbitMQ publisher closed")
}
