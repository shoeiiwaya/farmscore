from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class FieldCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    lat: float = Field(..., ge=20.0, le=46.0)
    lon: float = Field(..., ge=122.0, le=154.0)
    area_sqm: Optional[float] = None
    crop_type: Optional[str] = None
    description: Optional[str] = None


class FieldUpdate(BaseModel):
    name: Optional[str] = None
    crop_type: Optional[str] = None
    description: Optional[str] = None
    area_sqm: Optional[float] = None


class FieldResponse(BaseModel):
    id: UUID
    name: str
    lat: float
    lon: float
    area_sqm: Optional[float]
    crop_type: Optional[str]
    description: Optional[str]
    created_at: datetime
    sensor_count: int = 0
    latest_score: Optional[float] = None

    class Config:
        from_attributes = True


class SensorCreate(BaseModel):
    device_id: str
    sensor_type: str  # soil_moisture, temperature, humidity, light
    model: Optional[str] = None


class SensorResponse(BaseModel):
    id: UUID
    device_id: str
    sensor_type: str
    model: Optional[str]
    is_active: bool
    last_seen_at: Optional[datetime]
    battery_pct: Optional[float]

    class Config:
        from_attributes = True


class SensorReadingResponse(BaseModel):
    timestamp: datetime
    value: float
    unit: Optional[str]

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    id: UUID
    alert_type: str
    severity: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
