import pika
import json
from .config import settings
import logging

logger = logging.getLogger(__name__)

class RabbitMQPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None
        
    def connect(self):
        """Establece conexión con RabbitMQ"""
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
            
            # Declarar exchange
            self.channel.exchange_declare(
                exchange=settings.RABBITMQ_EXCHANGE,
                exchange_type='topic',
                durable=True
            )
            logger.info("Conectado a RabbitMQ")
        except Exception as e:
            logger.error(f"Error conectando a RabbitMQ: {e}")
            self.connection = None
            self.channel = None
    
    def publish_event(self, routing_key: str, event_data: dict):
        """Publica un evento en RabbitMQ"""
        if not self.channel:
            self.connect()
        
        if not self.channel:
            logger.warning(f"No se pudo publicar evento {routing_key}: sin conexión a RabbitMQ")
            return
        
        try:
            message = json.dumps(event_data)
            self.channel.basic_publish(
                exchange=settings.RABBITMQ_EXCHANGE,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Mensaje persistente
                    content_type='application/json'
                )
            )
            logger.info(f"Evento publicado: {routing_key}")
        except Exception as e:
            logger.error(f"Error publicando evento {routing_key}: {e}")
            self.connect()  # Reintentar conexión
    
    def close(self):
        """Cierra la conexión"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("🔌 Conexión a RabbitMQ cerrada")

# Instancia global
rabbitmq_publisher = RabbitMQPublisher()

def get_rabbitmq_publisher():
    """Dependency para obtener el publisher de RabbitMQ"""
    return rabbitmq_publisher
