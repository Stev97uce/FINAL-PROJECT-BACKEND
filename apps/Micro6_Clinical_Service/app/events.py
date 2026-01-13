import pika
import json
import logging
from typing import Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    """RabbitMQ event publisher"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        
    def connect(self):
        """Connect to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange
            self.channel.exchange_declare(
                exchange=settings.RABBITMQ_EXCHANGE,
                exchange_type='topic',
                durable=True
            )
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Error connecting to RabbitMQ: {e}")
            raise
    
    def publish_event(self, routing_key: str, event_data: Dict[str, Any]):
        """Publish event to RabbitMQ"""
        try:
            if not self.channel:
                self.connect()
            
            message = json.dumps(event_data)
            self.channel.basic_publish(
                exchange=settings.RABBITMQ_EXCHANGE,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json'
                )
            )
            logger.info(f"Published event: {routing_key}")
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            # Reconnect and retry
            self.connect()
            self.publish_event(routing_key, event_data)
    
    def close(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")


# Global publisher instance
rabbitmq_publisher = RabbitMQPublisher()


def publish_clinical_record_created(record_id: str, patient_id: int, therapist_id: int):
    """Publish clinical record created event"""
    event_data = {
        "event_type": "clinical.record_created",
        "record_id": record_id,
        "patient_id": patient_id,
        "therapist_id": therapist_id
    }
    rabbitmq_publisher.publish_event("clinical.record.created", event_data)


def publish_session_recorded(session_id: str, clinical_record_id: str, session_number: int):
    """Publish session recorded event"""
    event_data = {
        "event_type": "clinical.session_recorded",
        "session_id": session_id,
        "clinical_record_id": clinical_record_id,
        "session_number": session_number
    }
    rabbitmq_publisher.publish_event("clinical.session.recorded", event_data)


def publish_note_created(note_id: str, session_id: str, author_id: int):
    """Publish session note created event"""
    event_data = {
        "event_type": "clinical.note_created",
        "note_id": note_id,
        "session_id": session_id,
        "author_id": author_id
    }
    rabbitmq_publisher.publish_event("clinical.note.created", event_data)


def publish_goal_achieved(goal_id: str, clinical_record_id: str):
    """Publish therapeutic goal achieved event"""
    event_data = {
        "event_type": "clinical.goal_achieved",
        "goal_id": goal_id,
        "clinical_record_id": clinical_record_id
    }
    rabbitmq_publisher.publish_event("clinical.goal.achieved", event_data)
