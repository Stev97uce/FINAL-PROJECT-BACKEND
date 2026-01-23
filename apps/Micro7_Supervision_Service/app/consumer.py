"""
RabbitMQ event consumer for clinical.session_recorded events
Single Responsibility Principle - only consumes and processes events
"""
import json
import logging
import pika
import threading
from sqlalchemy.orm import Session
from app.config import settings
from app.database import SessionLocal
from app.models import SupervisionAssignment
from app.events import publish_feedback_added

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    """
    RabbitMQ event consumer
    Listens to clinical.session_recorded events from Clinical Service
    """
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.consumer_thread = None
    
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
            
            # Declare queue for this service
            queue_name = 'supervision_service_queue'
            self.channel.queue_declare(queue=queue_name, durable=True)
            
            # Bind queue to exchange with routing key
            self.channel.queue_bind(
                exchange=settings.RABBITMQ_EXCHANGE,
                queue=queue_name,
                routing_key='clinical.session_recorded'
            )
            
            logger.info(f"Consumer connected to RabbitMQ: {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}")
            logger.info(f"Listening for events: clinical.session_recorded")
        except Exception as e:
            logger.error(f"Failed to connect consumer to RabbitMQ: {e}")
            raise
    
    def handle_session_recorded(self, event_data: dict):
        """
        Handle clinical.session_recorded event
        Identifies supervisor and triggers notification
        """
        try:
            session_note_id = event_data.get("session_note_id")
            student_id = event_data.get("student_id")
            
            if not session_note_id or not student_id:
                logger.warning(f"Invalid event data: {event_data}")
                return
            
            # Find active supervision assignment for student
            db: Session = SessionLocal()
            try:
                assignment = db.query(SupervisionAssignment).filter(
                    SupervisionAssignment.student_user_id == student_id,
                    SupervisionAssignment.status == "active"
                ).first()
                
                if assignment:
                    logger.info(
                        f"Session note {session_note_id} by student {student_id} "
                        f"assigned to supervisor {assignment.supervisor_user_id}"
                    )
                    # Here we would trigger notification to supervisor
                    # For now, just log the assignment
                    # In production, this would publish an event to Notification Service
                else:
                    logger.warning(f"No active supervisor found for student {student_id}")
            finally:
                db.close()
        
        except Exception as e:
            logger.error(f"Error handling session_recorded event: {e}")
    
    def callback(self, ch, method, properties, body):
        """Callback for processing messages"""
        try:
            event_data = json.loads(body)
            logger.info(f"Received event: {method.routing_key}")
            
            if method.routing_key == 'clinical.session_recorded':
                self.handle_session_recorded(event_data)
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Reject and requeue message
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self):
        """Start consuming messages"""
        try:
            self.connect()
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue='supervision_service_queue',
                on_message_callback=self.callback
            )
            logger.info("Started consuming messages")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Error in consumer: {e}")
    
    def start(self):
        """Start consumer in a separate thread"""
        self.consumer_thread = threading.Thread(target=self.start_consuming, daemon=True)
        self.consumer_thread.start()
        logger.info("Consumer thread started")
    
    def stop(self):
        """Stop consuming messages"""
        try:
            if self.channel:
                self.channel.stop_consuming()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            logger.info("Consumer stopped")
        except Exception as e:
            logger.error(f"Error stopping consumer: {e}")


# Global consumer instance
consumer = RabbitMQConsumer()
