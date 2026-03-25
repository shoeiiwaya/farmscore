"""
MQTT Client for Sensor Data Ingestion
=======================================
Subscribes to LoRa gateway topics and processes incoming sensor data.
Supports: Dragino LoRa gateways, TTN/ChirpStack decoders.
"""

import json
import logging
import threading
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

_mqtt_thread: Optional[threading.Thread] = None


def start_mqtt_listener(db_session_factory):
    """Start MQTT listener in background thread."""
    global _mqtt_thread

    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        logger.warning("paho-mqtt not installed, MQTT listener disabled")
        return

    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            topic = f"{settings.MQTT_TOPIC_PREFIX}#"
            client.subscribe(topic)
            logger.info(f"MQTT connected, subscribed to {topic}")
        else:
            logger.error(f"MQTT connection failed: rc={rc}")

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            # Extract device_id from topic: farmscore/sensors/{device_id}
            parts = msg.topic.split("/")
            if len(parts) >= 3:
                device_id = parts[2]
            else:
                device_id = payload.get("device_id", "unknown")

            from app.services.sensor_service import process_sensor_data
            db = db_session_factory()
            try:
                process_sensor_data(db, device_id, payload)
            finally:
                db.close()

        except Exception as e:
            logger.error(f"MQTT message processing error: {e}")

    def run():
        client = mqtt.Client(
            client_id="farmscore-backend",
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        )
        client.on_connect = on_connect
        client.on_message = on_message

        try:
            client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, keepalive=60)
            client.loop_forever()
        except Exception as e:
            logger.error(f"MQTT connection error: {e}")

    _mqtt_thread = threading.Thread(target=run, daemon=True, name="mqtt-listener")
    _mqtt_thread.start()
    logger.info("MQTT listener thread started")
