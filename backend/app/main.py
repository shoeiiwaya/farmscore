import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import engine, get_db, Base
from app.db.models import User, ApiKey, Field, Sensor, SensorReading, FieldScore, Alert
from app.api.v1 import score, auth, fields, demo, admin, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    Base.metadata.create_all(bind=engine)

    # Start MQTT listener if configured
    if settings.MQTT_BROKER != "disabled":
        try:
            from app.services.mqtt_client import start_mqtt_listener
            from app.db.database import SessionLocal
            start_mqtt_listener(SessionLocal)
        except Exception:
            pass  # MQTT is optional

    yield
    # Shutdown


_IS_PROD = os.getenv("ENV", "").lower() == "production"

_DESCRIPTION = """
# FarmScore — 農地ポテンシャル診断API

緯度・経度を入力すると、**土壌・気候・水利・日照・標高**の5カテゴリで
農地としての適性を0〜100でスコアリングし、最適な作物を提案します。

## 主要機能

| 機能 | エンドポイント | 概要 |
|------|-------------|------|
| **農地スコア** | `GET /v1/score` | 5カテゴリ統合スコア + 作物推薦 |
| **バッチスコア** | `POST /v1/score/batch` | 最大50地点を一括評価 |
| **圃場管理** | `GET/POST /v1/fields` | 圃場CRUD + 自動スコアリング |
| **センサーデータ** | `GET /v1/fields/{id}/readings` | リアルタイムモニタリング |
| **アラート** | `GET /v1/fields/{id}/alerts` | 霜・干ばつ・過湿の自動通知 |
| **分析** | `GET /v1/analytics/dashboard` | ダッシュボード統計 |
| **デモ** | `GET /v1/demo/score` | 認証不要のお試しAPI |

## 認証

Bearer Token (JWT) または `X-API-Key` ヘッダーで認証します。

```
curl -H "X-API-Key: fs_YOUR_KEY" "https://api.farmscore.jp/v1/score?lat=35.44&lon=139.64"
```

## スコアリング方式

- **土壌**: 農研機構eSoil土壌分類 × 作物適合度マトリクス
- **気候**: 気象庁メッシュ平年値 × GDD(積算温度) × 霜リスク
- **水利**: 国土数値情報河川データ × 洪水リスク × 地下水推定
- **日照**: 気象庁日照時間 × GSI DEM傾斜・方位
- **標高**: 国土地理院DEM × 地形分類

## データソース

農研機構eSoil, 気象庁, 国土数値情報, 国土地理院DEM, JAXA ALOS

## 利用プラン

| プラン | 月額 | APIコール | 圃場数 |
|--------|------|----------|--------|
| Free | 0円 | 100/月 | 3 |
| Starter | 5,000円 | 1,000/月 | 10 |
| Pro | 20,000円 | 5,000/月 | 50 |
| Enterprise | 要見積 | 無制限 | 無制限 |
"""

app = FastAPI(
    title="FarmScore API",
    description=_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url=None if _IS_PROD else "/docs",
    redoc_url=None if _IS_PROD else "/redoc",
    contact={"name": "FarmScore Support", "url": "https://farmscore.jp"},
    license_info={"name": "Proprietary"},
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://farmscore.jp",
        "https://www.farmscore.jp",
    ],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["X-API-Key", "Content-Type", "Authorization"],
)

# Public endpoints (no auth)
app.include_router(demo.router, prefix="/v1", tags=["demo"])
app.include_router(admin.router, prefix="/v1", tags=["admin"])
app.include_router(auth.router, prefix="/v1", tags=["auth"])

# Score endpoint (API key auth)
from app.core.auth import require_api_key
app.include_router(
    score.router, prefix="/v1", tags=["score"],
    dependencies=[Depends(require_api_key)],
)

# Protected endpoints (JWT auth)
from app.core.auth import get_current_user
app.include_router(fields.router, prefix="/v1")
app.include_router(analytics.router, prefix="/v1")

# Sensor webhook (device auth)
from app.api.v1.fields import router as fields_webhook_router


@app.get("/health", tags=["system"])
def health(db: Session = Depends(get_db)):
    """ヘルスチェック"""
    checks = {"api": "ok"}
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "degraded"

    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return {
        "status": overall,
        "version": settings.VERSION,
        "checks": checks,
    }


@app.get("/", tags=["system"])
def root():
    return {
        "name": "FarmScore API",
        "version": settings.VERSION,
        "description": "農地ポテンシャル診断 × 圃場モニタリング",
        "docs": "/docs",
        "demo": "/v1/demo/score?lat=35.44&lon=139.64",
    }
