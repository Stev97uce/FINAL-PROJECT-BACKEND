"""
RabbitMQ event consumer
KISS principle: Simple event consumption from multiple services
"""
import json
import logging
import pika
import threading
from typing import Dict, Any
from app.config import settings
from app.models import NotificationChannel

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    """
    RabbitMQ event consumer
    Listens to events from Auth, Appointment, Clinical, and Supervision services
    """
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.thread = None
        self.running = False
    
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
                exchange=settings.RABBITMQ_EXCHANGE,
                exchange_type='topic',
                durable=True
            )
            
            # Declare queue for notification service
            queue_name = 'notification_service_queue'
            self.channel.queue_declare(queue=queue_name, durable=True)
            
            # Bind to multiple routing keys
            routing_keys = [
                'user.registered',
                'user.verified',
                'password.reset_requested',
                'appointment.created',
                'appointment.confirmed',
                'appointment.cancelled',
                'clinical.session_recorded',
                'supervision.feedback_added'
            ]
            
            for routing_key in routing_keys:
                self.channel.queue_bind(
                    exchange=settings.RABBITMQ_EXCHANGE,
                    queue=queue_name,
                    routing_key=routing_key
                )
            
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=self.callback
            )
            
            logger.info(f"Connected to RabbitMQ, listening to {len(routing_keys)} events")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self.connection = None
            self.channel = None
    
    def callback(self, ch, method, properties, body):
        """Callback for processing messages"""
        try:
            event_data = json.loads(body)
            routing_key = method.routing_key
            
            logger.info(f"Received event: {routing_key}")
            
            # Route to appropriate handler
            if routing_key == 'user.registered':
                self.handle_user_registered(event_data)
            elif routing_key == 'user.verified':
                self.handle_user_verified(event_data)
            elif routing_key == 'password.reset_requested':
                self.handle_password_reset(event_data)
            elif routing_key == 'appointment.created':
                self.handle_appointment_created(event_data)
            elif routing_key == 'appointment.confirmed':
                self.handle_appointment_confirmed(event_data)
            elif routing_key == 'appointment.cancelled':
                self.handle_appointment_cancelled(event_data)
            elif routing_key == 'clinical.session_recorded':
                self.handle_session_recorded(event_data)
            elif routing_key == 'supervision.feedback_added':
                self.handle_feedback_added(event_data)
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Reject and requeue
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def handle_user_registered(self, event_data: Dict[str, Any]):
        """Handle user.registered event - send verification email"""
        from app.services.notification_service import notification_service
        import asyncio
        
        user_id = event_data.get("user_id")
        email = event_data.get("email")
        nombres = event_data.get("nombres", "Usuario")
        
        if not user_id or not email:
            logger.warning(f"Invalid user.registered event: {event_data}")
            return
        
        # Send verification email
        asyncio.run(notification_service.send_notification(
            user_id=user_id,
            channel=NotificationChannel.EMAIL,
            template_name="email_verification",
            variables={
                "email": email,
                "user_name": nombres,
                "verification_link": f"{settings.AUTH_SERVICE_URL}/verify-email?token=xxx"
            },
            recipient=email
        ))
        
        logger.info(f"Sent verification email to user {user_id}")
    
    def handle_user_verified(self, event_data: Dict[str, Any]):
        """Handle user.verified event - send welcome email"""
        from app.services.notification_service import notification_service
        import asyncio
        
        user_id = event_data.get("user_id")
        email = event_data.get("email")
        
        if not user_id or not email:
            return
        
        asyncio.run(notification_service.send_notification(
            user_id=user_id,
            channel=NotificationChannel.EMAIL,
            template_name="welcome_email",
            variables={"email": email, "user_name": "Usuario"},
            recipient=email
        ))
        
        logger.info(f"Sent welcome email to user {user_id}")
    
    def handle_password_reset(self, event_data: Dict[str, Any]):
        """Handle password.reset_requested event"""
        # Similar implementation
        logger.info("Password reset notification (not implemented)")
    
    def handle_appointment_created(self, event_data: Dict[str, Any]):
        """Handle appointment.created event - send confirmation"""
        from app.services.notification_service import notification_service
        import asyncio
        
        # Send email confirmation
        # Send WhatsApp confirmation
        # Schedule reminders (48h and 24h)
        logger.info("Appointment created notification (not fully implemented)")
    
    def handle_appointment_confirmed(self, event_data: Dict[str, Any]):
        """Handle appointment.confirmed event"""
        logger.info("Appointment confirmed notification (not implemented)")
    
    def handle_appointment_cancelled(self, event_data: Dict[str, Any]):
        """Handle appointment.cancelled event"""
        logger.info("Appointment cancelled notification (not implemented)")
    
    def handle_session_recorded(self, event_data: Dict[str, Any]):
        """Handle clinical.session_recorded event - notify supervisor"""
        from app.services.notification_service import notification_service
        import asyncio
        
        supervisor_id = event_data.get("supervisor_id")
        session_note_id = event_data.get("session_note_id")
        
        if supervisor_id:
            # Send internal notification
            asyncio.run(notification_service.send_notification(
                user_id=supervisor_id,
                channel=NotificationChannel.INTERNAL,
                template_name="supervisor_session_alert",
                variables={
                    "category": "supervision",
                    "priority": "high",
                    "session_note_id": session_note_id,
                    "action_url": f"/supervision/review/{session_note_id}"
                }
            ))
            
            logger.info(f"Notified supervisor {supervisor_id} about new session")
    
    def handle_feedback_added(self, event_data: Dict[str, Any]):
        """Handle supervision.feedback_added event - notify student"""
        from app.services.notification_service import notification_service
        import asyncio
        
        student_id = event_data.get("student_id")
        feedback_id = event_data.get("feedback_id")
        
        if student_id:
            # Send internal notification + MQTT
            asyncio.run(notification_service.send_notification(
                user_id=student_id,
                channel=NotificationChannel.INTERNAL,
                template_name="student_feedback_alert",
                variables={
                    "category": "supervision",
                    "priority": "high",
                    "feedback_id": feedback_id,
                    "action_url": f"/supervision/feedback/{feedback_id}"
                }
            ))
            
            # Also send via MQTT for real-time
            asyncio.run(notification_service.send_notification(
                user_id=student_id,
                channel=NotificationChannel.MQTT,
                template_name="student_feedback_alert",
                variables={
                    "category": "supervision",
                    "feedback_id": feedback_id,
                    "action_url": f"/supervision/feedback/{feedback_id}"
                }
            ))
            
            logger.info(f"Notified student {student_id} about new feedback")
    
    def start_consuming(self):
        """Start consuming messages"""
        if self.channel:
            logger.info("Starting RabbitMQ consumer")
            self.running = True
            self.channel.start_consuming()
    
    def start(self):
        """Start consumer in a separate thread"""
        if not self.connection:
            self.connect()
        
        if self.connection and not self.running:
            self.thread = threading.Thread(target=self.start_consuming, daemon=True)
            self.thread.start()
            logger.info("RabbitMQ consumer started in background")
    
    def stop(self):
        """Stop consuming messages"""
        if self.channel and self.running:
            self.running = False
            self.channel.stop_consuming()
            if self.connection:
                self.connection.close()
            logger.info("RabbitMQ consumer stopped")


# Global consumer instance
rabbitmq_consumer = RabbitMQConsumer()
