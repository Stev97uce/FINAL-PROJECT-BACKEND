"""
RabbitMQ event publisher and consumer
Single Responsibility Principle - handles only messaging
"""
import json
import logging
import pika
from typing import Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    """
    RabbitMQ event publisher
    Single Responsibility: Publish events to message broker
    """
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connect()
    
    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                virtual_host=settings.RABBITMQ_VHOST,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange
            self.channel.exchange_declare(
                exchange=settings.RABBITMQ_EXCHANGE,
                exchange_type='topic',
                durable=True
            )
            logger.info(f"Connected to RabbitMQ: {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def publish_event(self, routing_key: str, event_data: Dict[str, Any]):
        """
        Publish event to RabbitMQ exchange
        
        Args:
            routing_key: Event routing key (e.g., 'supervision.feedback_added')
            event_data: Event payload as dictionary
        """
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
            
            message = json.dumps(event_data, default=str)
            
            self.channel.basic_publish(
                exchange=settings.RABBITMQ_EXCHANGE,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent message
                    content_type='application/json'
                )
            )
            logger.info(f"Published event: {routing_key}")
        except Exception as e:
            logger.error(f"Failed to publish event {routing_key}: {e}")
            # Try to reconnect and publish again
            try:
                self.connect()
                self.channel.basic_publish(
                    exchange=settings.RABBITMQ_EXCHANGE,
                    routing_key=routing_key,
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        content_type='application/json'
                    )
                )
                logger.info(f"Published event after reconnection: {routing_key}")
            except Exception as retry_error:
                logger.error(f"Failed to publish event after retry: {retry_error}")
    
    def close(self):
        """Close RabbitMQ connection"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")


# Global publisher instance
publisher = RabbitMQPublisher()


def publish_feedback_added(
    feedback_id: int,
    session_note_id: str,
    supervisor_id: int,
    student_id: int,
    assignment_id: int,
    reviewed_at: str
):
    """
    Publish supervision.feedback_added event
    This event notifies Clinical Service and Notification Service
    """
    event_data = {
        "feedback_id": feedback_id,
        "session_note_id": session_note_id,
        "supervisor_id": supervisor_id,
        "student_id": student_id,
        "assignment_id": assignment_id,
        "reviewed_at": reviewed_at
    }
    publisher.publish_event("supervision.feedback_added", event_data)


def get_publisher() -> RabbitMQPublisher:
    """Get publisher instance for dependency injection"""
    return publisher
