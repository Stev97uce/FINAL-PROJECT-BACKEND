import pika
import json
from datetime import datetime
from typing import Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class EventPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = settings.RABBITMQ_EXCHANGE
        
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
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange as topic
            self.channel.exchange_declare(
                exchange=self.exchange,
                exchange_type='topic',
                durable=True
            )
            
            logger.info("Connected to RabbitMQ successfully")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self.connection = None
            self.channel = None
    
    def publish_event(self, event_name: str, data: Dict[str, Any]):
        """Publish an event to RabbitMQ"""
        if not self.channel:
            self.connect()
        
        if not self.channel:
            logger.error("Cannot publish event: No connection to RabbitMQ")
            return
        
        try:
            event_message = {
                "event": event_name,
                "data": data,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=event_name,
                body=json.dumps(event_message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Event published: {event_name}")
        except Exception as e:
            logger.error(f"Failed to publish event {event_name}: {e}")
            # Try to reconnect
            self.connect()
    
    def close(self):
        """Close RabbitMQ connection"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")


# Global event publisher instance
event_publisher = EventPublisher()


# Event publishing functions
def publish_user_registered(user_id: int, email: str, nombres: str, rol: str, telefono: str):
    """Publish user.registered event"""
    event_publisher.publish_event("user.registered", {
        "user_id": user_id,
        "email": email,
        "nombres": nombres,
        "rol": rol,
        "telefono": telefono
    })


def publish_user_verified(user_id: int, email: str):
    """Publish user.verified event"""
    event_publisher.publish_event("user.verified", {
        "user_id": user_id,
        "email": email
    })


def publish_password_reset_requested(email: str, token: str, expira_en: str):
    """Publish password.reset_requested event"""
    event_publisher.publish_event("password.reset_requested", {
        "email": email,
        "token": token,
        "expira_en": expira_en
    })
