"""
MQTT service for real-time push notifications
KISS principle: Simple MQTT publisher
"""
import logging
import json
from typing import Dict, Any
import paho.mqtt.client as mqtt
from app.config import settings

logger = logging.getLogger(__name__)


class MQTTService:
    """Simple MQTT publisher for real-time notifications"""
    
    def __init__(self):
        self.client = None
        self.connected = False
        self._setup_client()
    
    def _setup_client(self):
        """Setup MQTT client"""
        try:
            self.client = mqtt.Client(client_id=settings.MQTT_CLIENT_ID)
            
            if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
                self.client.username_pw_set(
                    settings.MQTT_USERNAME,
                    settings.MQTT_PASSWORD
                )
            
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            
            # Connect
            self.client.connect(
                settings.MQTT_BROKER_HOST,
                settings.MQTT_BROKER_PORT,
                keepalive=60
            )
            self.client.loop_start()
            
            logger.info("MQTT client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MQTT: {e}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback on connection"""
        if rc == 0:
            self.connected = True
            logger.info("MQTT connected successfully")
        else:
            logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback on disconnection"""
        self.connected = False
        logger.warning(f"MQTT disconnected with code {rc}")
    
    async def publish_notification(
        self,
        user_id: int,
        notification: Dict[str, Any]
    ) -> bool:
        """
        Publish notification to user's MQTT topic
        
        Args:
            user_id: User ID
            notification: Notification data (dict)
        
        Returns:
            bool: True if published successfully
        """
        if not self.client or not self.connected:
            logger.warning("MQTT not connected, skipping publish")
            return False
        
        try:
            topic = f"uce/notifications/{user_id}"
            payload = json.dumps(notification)
            
            result = self.client.publish(
                topic,
                payload,
                qos=1,  # At least once delivery
                retain=False
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"MQTT published to {topic}")
                return True
            else:
                logger.error(f"MQTT publish failed with code {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to publish MQTT notification: {e}")
            return False
    
    def disconnect(self):
        """Disconnect MQTT client"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT client disconnected")


# Global instance
mqtt_service = MQTTService()
