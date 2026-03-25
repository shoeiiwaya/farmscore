"""
Fields API — 圃場管理（Phase 1+）
"""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.db.models import User, Field, Sensor, SensorReading, FieldScore, Alert
from app.schemas.field import (
    FieldCreate, FieldUpdate, FieldResponse,
    SensorCreate, SensorResponse, SensorReadingResponse, AlertResponse,
)
from app.services.scoring_engine import calculate_farm_score
from app.services.sensor_service import get_readings, get_readings_aggregated

router = APIRouter()


# ─── Fields CRUD ──────────────────────────────────────────────

@router.get("/fields", response_model=list[FieldResponse], tags=["fields"])
def list_fields(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """登録済み圃場一覧"""
    fields = db.query(Field).filter(Field.user_id == user.id).all()
    result = []
    for f in fields:
        sensor_count = db.query(Sensor).filter(Sensor.field_id == f.id, Sensor.is_active == True).count()
        latest = db.query(FieldScore).filter(FieldScore.field_id == f.id).order_by(FieldScore.scored_at.desc()).first()
        result.append(FieldResponse(
            id=f.id, name=f.name, lat=f.lat, lon=f.lon,
            area_sqm=f.area_sqm, crop_type=f.crop_type, description=f.description,
            created_at=f.created_at, sensor_count=sensor_count,
            latest_score=latest.overall_score if latest else None,
        ))
    return result


@router.post("/fields", response_model=FieldResponse, tags=["fields"])
async def create_field(
    req: FieldCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """圃場を登録"""
    # Check plan limits
    field_count = db.query(Field).filter(Field.user_id == user.id).count()
    limits = {"free": 3, "starter": 10, "pro": 50, "enterprise": 999}
    max_fields = limits.get(user.plan, 3)
    if field_count >= max_fields:
        raise HTTPException(status_code=403, detail=f"プラン上限に達しています（{user.plan}: 最大{max_fields}圃場）")

    field = Field(user_id=user.id, **req.model_dump())
    db.add(field)
    db.commit()
    db.refresh(field)

    # Auto-score the field
    score_result = await calculate_farm_score(field.lat, field.lon, field.crop_type)
    field_score = FieldScore(
        field_id=field.id,
        overall_score=score_result["overall_score"],
        soil_score=score_result["soil_score"],
        climate_score=score_result["climate_score"],
        water_score=score_result["water_score"],
        sunlight_score=score_result["sunlight_score"],
        elevation_score=score_result["elevation_score"],
        detail=score_result,
    )
    db.add(field_score)
    db.commit()

    return FieldResponse(
        id=field.id, name=field.name, lat=field.lat, lon=field.lon,
        area_sqm=field.area_sqm, crop_type=field.crop_type, description=field.description,
        created_at=field.created_at, sensor_count=0,
        latest_score=score_result["overall_score"],
    )


@router.get("/fields/{field_id}", tags=["fields"])
async def get_field(
    field_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """圃場詳細（スコア・センサーデータ・アラート含む）"""
    field = db.query(Field).filter(Field.id == field_id, Field.user_id == user.id).first()
    if not field:
        raise HTTPException(status_code=404, detail="圃場が見つかりません")

    sensors = db.query(Sensor).filter(Sensor.field_id == field.id).all()
    latest_score = db.query(FieldScore).filter(FieldScore.field_id == field.id).order_by(FieldScore.scored_at.desc()).first()
    alerts = db.query(Alert).filter(Alert.field_id == field.id, Alert.is_read == False).order_by(Alert.created_at.desc()).limit(10).all()

    return {
        "field": FieldResponse(
            id=field.id, name=field.name, lat=field.lat, lon=field.lon,
            area_sqm=field.area_sqm, crop_type=field.crop_type, description=field.description,
            created_at=field.created_at, sensor_count=len(sensors),
            latest_score=latest_score.overall_score if latest_score else None,
        ),
        "score_detail": latest_score.detail if latest_score else None,
        "sensors": [SensorResponse.model_validate(s) for s in sensors],
        "alerts": [AlertResponse.model_validate(a) for a in alerts],
    }


@router.patch("/fields/{field_id}", response_model=FieldResponse, tags=["fields"])
def update_field(
    field_id: UUID,
    req: FieldUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """圃場情報を更新"""
    field = db.query(Field).filter(Field.id == field_id, Field.user_id == user.id).first()
    if not field:
        raise HTTPException(status_code=404, detail="圃場が見つかりません")

    update_data = req.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(field, k, v)
    db.commit()
    db.refresh(field)

    return FieldResponse(
        id=field.id, name=field.name, lat=field.lat, lon=field.lon,
        area_sqm=field.area_sqm, crop_type=field.crop_type, description=field.description,
        created_at=field.created_at,
    )


@router.delete("/fields/{field_id}", tags=["fields"])
def delete_field(
    field_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """圃場を削除"""
    field = db.query(Field).filter(Field.id == field_id, Field.user_id == user.id).first()
    if not field:
        raise HTTPException(status_code=404, detail="圃場が見つかりません")
    db.delete(field)
    db.commit()
    return {"message": "削除しました"}


# ─── Sensors ──────────────────────────────────────────────────

@router.post("/fields/{field_id}/sensors", response_model=SensorResponse, tags=["sensors"])
def add_sensor(
    field_id: UUID,
    req: SensorCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """圃場にセンサーを追加"""
    field = db.query(Field).filter(Field.id == field_id, Field.user_id == user.id).first()
    if not field:
        raise HTTPException(status_code=404, detail="圃場が見つかりません")

    sensor = Sensor(field_id=field.id, **req.model_dump())
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    return sensor


@router.get("/fields/{field_id}/readings", tags=["sensors"])
def get_field_readings(
    field_id: UUID,
    sensor_type: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=720),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """圃場のセンサーデータ取得"""
    field = db.query(Field).filter(Field.id == field_id, Field.user_id == user.id).first()
    if not field:
        raise HTTPException(status_code=404, detail="圃場が見つかりません")

    readings = get_readings(db, field_id, sensor_type, hours)
    return [SensorReadingResponse.model_validate(r) for r in readings]


@router.get("/fields/{field_id}/readings/aggregated", tags=["sensors"])
def get_aggregated_readings(
    field_id: UUID,
    sensor_type: str = Query(..., description="soil_moisture, temperature, humidity, light"),
    hours: int = Query(168, ge=1, le=720),
    interval: int = Query(60, description="集計間隔（分）"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """集計済みセンサーデータ（グラフ用）"""
    field = db.query(Field).filter(Field.id == field_id, Field.user_id == user.id).first()
    if not field:
        raise HTTPException(status_code=404, detail="圃場が見つかりません")

    return get_readings_aggregated(db, field_id, sensor_type, hours, interval)


# ─── Alerts ───────────────────────────────────────────────────

@router.get("/fields/{field_id}/alerts", response_model=list[AlertResponse], tags=["alerts"])
def get_alerts(
    field_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """圃場のアラート一覧"""
    field = db.query(Field).filter(Field.id == field_id, Field.user_id == user.id).first()
    if not field:
        raise HTTPException(status_code=404, detail="圃場が見つかりません")

    alerts = db.query(Alert).filter(Alert.field_id == field.id).order_by(Alert.created_at.desc()).limit(50).all()
    return alerts


@router.patch("/alerts/{alert_id}/read", tags=["alerts"])
def mark_alert_read(
    alert_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """アラートを既読にする"""
    alert = db.query(Alert).join(Field).filter(
        Alert.id == alert_id,
        Field.user_id == user.id,
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="アラートが見つかりません")

    alert.is_read = True
    db.commit()
    return {"message": "既読にしました"}


# ─── Webhook for sensors ─────────────────────────────────────

@router.post("/webhook/sensor", tags=["sensors"])
def sensor_webhook(
    payload: dict,
    db: Session = Depends(get_db),
):
    """
    センサーデータ受信Webhook（LoRaゲートウェイ/TTN/ChirpStackから）

    認証不要（デバイスIDで識別）
    """
    device_id = payload.get("device_id") or payload.get("dev_eui", "")
    if not device_id:
        raise HTTPException(status_code=400, detail="device_id is required")

    from app.services.sensor_service import process_sensor_data
    reading = process_sensor_data(db, device_id, payload)
    if not reading:
        raise HTTPException(status_code=404, detail="Unknown device")

    return {"status": "ok", "reading_id": str(reading.id)}
