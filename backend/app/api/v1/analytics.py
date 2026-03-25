"""
Analytics API — Phase 3 分析機能
"""

from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.auth import get_current_user
from app.db.database import get_db
from app.db.models import User, Field, SensorReading, Sensor, FieldScore, Alert

router = APIRouter()


@router.get("/analytics/dashboard", tags=["analytics"])
def dashboard_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """ダッシュボード概要データ"""
    fields = db.query(Field).filter(Field.user_id == user.id).all()
    field_ids = [f.id for f in fields]

    total_sensors = db.query(Sensor).filter(
        Sensor.field_id.in_(field_ids),
        Sensor.is_active == True,
    ).count() if field_ids else 0

    unread_alerts = db.query(Alert).filter(
        Alert.field_id.in_(field_ids),
        Alert.is_read == False,
    ).count() if field_ids else 0

    # Latest readings per sensor type
    latest_readings = {}
    if field_ids:
        for stype in ["soil_moisture", "temperature", "humidity", "light"]:
            reading = db.query(SensorReading).join(Sensor).filter(
                SensorReading.field_id.in_(field_ids),
                Sensor.sensor_type == stype,
            ).order_by(SensorReading.timestamp.desc()).first()
            if reading:
                latest_readings[stype] = {
                    "value": reading.value,
                    "unit": reading.unit,
                    "timestamp": reading.timestamp.isoformat(),
                }

    # Average scores
    avg_score = None
    if field_ids:
        scores = db.query(FieldScore).filter(FieldScore.field_id.in_(field_ids)).all()
        if scores:
            avg_score = round(sum(s.overall_score for s in scores) / len(scores), 1)

    return {
        "field_count": len(fields),
        "sensor_count": total_sensors,
        "unread_alerts": unread_alerts,
        "avg_score": avg_score,
        "latest_readings": latest_readings,
        "plan": user.plan,
        "api_calls_month": user.api_calls_month,
    }


@router.get("/analytics/fields/compare", tags=["analytics"])
def compare_fields(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """全圃場のスコア比較"""
    fields = db.query(Field).filter(Field.user_id == user.id).all()
    results = []
    for f in fields:
        score = db.query(FieldScore).filter(
            FieldScore.field_id == f.id,
        ).order_by(FieldScore.scored_at.desc()).first()

        results.append({
            "field_id": str(f.id),
            "name": f.name,
            "crop_type": f.crop_type,
            "overall_score": score.overall_score if score else None,
            "soil_score": score.soil_score if score else None,
            "climate_score": score.climate_score if score else None,
            "water_score": score.water_score if score else None,
            "sunlight_score": score.sunlight_score if score else None,
        })

    results.sort(key=lambda x: x["overall_score"] or 0, reverse=True)
    return {"fields": results}


@router.get("/analytics/sensor-trends", tags=["analytics"])
def sensor_trends(
    field_id: UUID = Query(...),
    sensor_type: str = Query(...),
    days: int = Query(30, ge=1, le=365),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """センサーデータのトレンド分析"""
    field = db.query(Field).filter(Field.id == field_id, Field.user_id == user.id).first()
    if not field:
        return {"error": "圃場が見つかりません"}

    since = datetime.utcnow() - timedelta(days=days)
    readings = db.query(SensorReading).join(Sensor).filter(
        SensorReading.field_id == field_id,
        Sensor.sensor_type == sensor_type,
        SensorReading.timestamp >= since,
    ).order_by(SensorReading.timestamp).all()

    if not readings:
        return {"trend": "insufficient_data", "data_points": 0}

    values = [r.value for r in readings]
    n = len(values)

    # Simple trend detection
    if n >= 2:
        first_half = sum(values[:n // 2]) / (n // 2)
        second_half = sum(values[n // 2:]) / (n - n // 2)
        change_pct = ((second_half - first_half) / first_half * 100) if first_half != 0 else 0

        if change_pct > 10:
            trend = "上昇傾向"
        elif change_pct < -10:
            trend = "下降傾向"
        else:
            trend = "安定"
    else:
        trend = "データ不足"
        change_pct = 0

    return {
        "field_name": field.name,
        "sensor_type": sensor_type,
        "period_days": days,
        "data_points": n,
        "trend": trend,
        "change_pct": round(change_pct, 1),
        "avg": round(sum(values) / n, 2),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "std_dev": round((sum((v - sum(values) / n) ** 2 for v in values) / n) ** 0.5, 2),
    }
