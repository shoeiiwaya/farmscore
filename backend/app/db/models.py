import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON,
    UniqueConstraint, Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


# ─── Users & Auth ─────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(100))
    plan = Column(String(20), default="free")  # free / starter / pro / enterprise
    stripe_customer_id = Column(String(100))
    api_calls_today = Column(Integer, default=0)
    api_calls_month = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    api_keys = relationship("ApiKey", back_populates="user")
    fields = relationship("Field", back_populates="user")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash = Column(String(255), unique=True, nullable=False)
    prefix = Column(String(20), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), default="default")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime)

    user = relationship("User", back_populates="api_keys")


# ─── Fields (圃場) ────────────────────────────────────────────

class Field(Base):
    __tablename__ = "fields"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    area_sqm = Column(Float)
    crop_type = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="fields")
    sensors = relationship("Sensor", back_populates="field")
    sensor_readings = relationship("SensorReading", back_populates="field")
    scores = relationship("FieldScore", back_populates="field")
    alerts = relationship("Alert", back_populates="field")

    __table_args__ = (
        Index("ix_fields_location", "lat", "lon"),
    )


# ─── Sensors ──────────────────────────────────────────────────

class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False)
    device_id = Column(String(100), unique=True, nullable=False)
    sensor_type = Column(String(50), nullable=False)  # soil_moisture, temperature, humidity, light
    model = Column(String(100))  # e.g. "Dragino LSE01"
    is_active = Column(Boolean, default=True)
    last_seen_at = Column(DateTime)
    battery_pct = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    field = relationship("Field", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.id"), nullable=False)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(20))  # %, °C, lux, etc.
    raw_payload = Column(JSON)

    sensor = relationship("Sensor", back_populates="readings")
    field = relationship("Field", back_populates="sensor_readings")

    __table_args__ = (
        Index("ix_readings_sensor_ts", "sensor_id", "timestamp"),
        Index("ix_readings_field_ts", "field_id", "timestamp"),
    )


# ─── Scores ───────────────────────────────────────────────────

class FieldScore(Base):
    __tablename__ = "field_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False)
    overall_score = Column(Float, nullable=False)
    soil_score = Column(Float)
    climate_score = Column(Float)
    water_score = Column(Float)
    sunlight_score = Column(Float)
    elevation_score = Column(Float)
    accessibility_score = Column(Float)
    detail = Column(JSON)
    scored_at = Column(DateTime, default=datetime.utcnow)

    field = relationship("Field", back_populates="scores")


# ─── Alerts ───────────────────────────────────────────────────

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # frost, drought, pest_risk, soil_moisture_low
    severity = Column(String(20), nullable=False)  # info, warning, critical
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    field = relationship("Field", back_populates="alerts")
