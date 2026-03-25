"""
Sensor Data Integration Service
================================
Handles MQTT ingestion from LoRa sensors (Dragino LSE01, LHT65N etc.)
and provides data query/aggregation.

Supported sensor types:
- soil_moisture: Dragino LSE01 (%)
- temperature: LHT65N (°C)
- humidity: LHT65N (%)
- light: BH1750 (lux)
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.db.models import Sensor, SensorReading, Field, Alert

logger = logging.getLogger(__name__)

# Alert thresholds
THRESHOLDS = {
    "soil_moisture": {"low": 20.0, "high": 80.0, "unit": "%"},
    "temperature": {"low": 5.0, "high": 35.0, "unit": "°C"},
    "humidity": {"low": 30.0, "high": 95.0, "unit": "%"},
    "light": {"low": 100.0, "high": 100000.0, "unit": "lux"},
}


def process_sensor_data(
    db: Session,
    device_id: str,
    payload: dict,
) -> Optional[SensorReading]:
    """Process incoming sensor data from MQTT/webhook."""
    sensor = db.query(Sensor).filter(
        Sensor.device_id == device_id,
        Sensor.is_active == True,
    ).first()

    if not sensor:
        logger.warning(f"Unknown sensor device: {device_id}")
        return None

    # Parse value from payload (supports multiple formats)
    value = _extract_value(payload, sensor.sensor_type)
    if value is None:
        logger.warning(f"Could not parse value from payload: {payload}")
        return None

    unit = THRESHOLDS.get(sensor.sensor_type, {}).get("unit", "")

    reading = SensorReading(
        sensor_id=sensor.id,
        field_id=sensor.field_id,
        timestamp=datetime.utcnow(),
        value=value,
        unit=unit,
        raw_payload=payload,
    )
    db.add(reading)

    # Update sensor last seen
    sensor.last_seen_at = datetime.utcnow()
    if "battery" in payload:
        sensor.battery_pct = float(payload["battery"])

    # Check thresholds and create alerts
    _check_thresholds(db, sensor, value)

    db.commit()
    return reading


def _extract_value(payload: dict, sensor_type: str) -> Optional[float]:
    """Extract sensor value from various payload formats."""
    # Dragino format
    if "value" in payload:
        return float(payload["value"])
    # TTN/ChirpStack decoded format
    if sensor_type == "soil_moisture" and "soil_moisture" in payload:
        return float(payload["soil_moisture"])
    if sensor_type == "temperature" and "temperature" in payload:
        return float(payload["temperature"])
    if sensor_type == "humidity" and "humidity" in payload:
        return float(payload["humidity"])
    if sensor_type == "light" and "light" in payload:
        return float(payload["light"])
    # Generic
    for key in ("val", "data", "reading"):
        if key in payload:
            try:
                return float(payload[key])
            except (ValueError, TypeError):
                continue
    return None


def _check_thresholds(db: Session, sensor: Sensor, value: float):
    """Check if value exceeds thresholds and create alert."""
    thresholds = THRESHOLDS.get(sensor.sensor_type)
    if not thresholds:
        return

    alert_type = None
    severity = "warning"
    message = ""

    if value < thresholds["low"]:
        if sensor.sensor_type == "soil_moisture":
            alert_type = "drought"
            message = f"土壌水分が低下しています: {value}{thresholds['unit']}（閾値: {thresholds['low']}{thresholds['unit']}）。灌水を検討してください。"
        elif sensor.sensor_type == "temperature":
            alert_type = "frost"
            severity = "critical" if value < 0 else "warning"
            message = f"低温注意: {value}{thresholds['unit']}。霜害のリスクがあります。"
        else:
            alert_type = f"{sensor.sensor_type}_low"
            message = f"{sensor.sensor_type}が低下: {value}{thresholds['unit']}"

    elif value > thresholds["high"]:
        if sensor.sensor_type == "temperature":
            alert_type = "heat"
            severity = "critical" if value > 40 else "warning"
            message = f"高温注意: {value}{thresholds['unit']}。遮光・灌水を検討してください。"
        elif sensor.sensor_type == "soil_moisture":
            alert_type = "waterlog"
            message = f"過湿注意: 土壌水分{value}{thresholds['unit']}。排水を確認してください。"
        else:
            alert_type = f"{sensor.sensor_type}_high"
            message = f"{sensor.sensor_type}が上昇: {value}{thresholds['unit']}"

    if alert_type:
        # Don't spam: check if similar alert exists in last 6 hours
        recent = db.query(Alert).filter(
            Alert.field_id == sensor.field_id,
            Alert.alert_type == alert_type,
            Alert.created_at > datetime.utcnow() - timedelta(hours=6),
        ).first()

        if not recent:
            alert = Alert(
                field_id=sensor.field_id,
                alert_type=alert_type,
                severity=severity,
                message=message,
            )
            db.add(alert)


def get_readings(
    db: Session,
    field_id: UUID,
    sensor_type: Optional[str] = None,
    hours: int = 24,
    limit: int = 500,
) -> list[SensorReading]:
    """Get sensor readings for a field."""
    since = datetime.utcnow() - timedelta(hours=hours)
    q = db.query(SensorReading).filter(
        SensorReading.field_id == field_id,
        SensorReading.timestamp >= since,
    )
    if sensor_type:
        q = q.join(Sensor).filter(Sensor.sensor_type == sensor_type)

    return q.order_by(SensorReading.timestamp.desc()).limit(limit).all()


def get_readings_aggregated(
    db: Session,
    field_id: UUID,
    sensor_type: str,
    hours: int = 168,  # 7 days
    interval_minutes: int = 60,
) -> list[dict]:
    """Get aggregated readings (avg/min/max per interval)."""
    since = datetime.utcnow() - timedelta(hours=hours)

    readings = db.query(SensorReading).join(Sensor).filter(
        SensorReading.field_id == field_id,
        Sensor.sensor_type == sensor_type,
        SensorReading.timestamp >= since,
    ).order_by(SensorReading.timestamp).all()

    if not readings:
        return []

    # Bucket into intervals
    buckets = {}
    for r in readings:
        bucket_ts = r.timestamp.replace(
            minute=(r.timestamp.minute // interval_minutes) * interval_minutes,
            second=0,
            microsecond=0,
        )
        if bucket_ts not in buckets:
            buckets[bucket_ts] = []
        buckets[bucket_ts].append(r.value)

    result = []
    for ts, values in sorted(buckets.items()):
        result.append({
            "timestamp": ts.isoformat(),
            "avg": round(sum(values) / len(values), 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "count": len(values),
        })

    return result
