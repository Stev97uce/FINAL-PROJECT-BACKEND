import pika
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class EventPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None
        
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
            
            # Declare exchange
            self.channel.exchange_declare(
                exchange='uce_events',
                exchange_type='topic',
                durable=True
            )
            
            logger.info("Connected to RabbitMQ successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            return False
    
    def publish_event(self, routing_key: str, event_data: dict):
        """Publish an event to RabbitMQ"""
        try:
            if not self.channel or self.channel.is_closed:
                self.connect()
            
            message = json.dumps(event_data)
            
            self.channel.basic_publish(
                exchange='uce_events',
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published event: {routing_key}")
            
        except Exception as e:
            logger.error(f"Failed to publish event: {str(e)}")
    
    def close(self):
        """Close RabbitMQ connection"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {str(e)}")

# Global event publisher instance
event_publisher = EventPublisher()

def get_event_publisher() -> EventPublisher:
    """Get event publisher instance"""
    return event_publisher
