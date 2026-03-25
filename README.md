# FarmScore — 農地ポテンシャル診断 x 圃場モニタリング

緯度経度を入力するだけで農地の適性をAIがスコアリング。土壌・気候・水利・日照・標高の5軸で分析し、最適な作物を提案します。

## Architecture

```
frontend/          Next.js 15 + Leaflet + Recharts + Tailwind CSS
backend/           FastAPI + Python 3.11
  app/
    api/v1/        REST API endpoints
    services/      Scoring engine, sensor integration, MQTT
    schemas/       Pydantic models
    db/            SQLAlchemy + PostGIS models
    core/          Config, auth, security
docker-compose.yml PostgreSQL + Mosquitto MQTT + Backend + Frontend
```

## Quick Start

```bash
# Docker (recommended)
docker compose up -d

# Or manually:
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## API

Demo (no auth): `GET /v1/demo/score?lat=35.44&lon=139.64`

Full docs: http://localhost:8000/docs

## Data Sources

- 農研機構 日本土壌インベントリー (eSoil)
- 気象庁 メッシュ平年値
- 国土数値情報 (国土交通省)
- 国土地理院 標高API
- JAXA ALOS

## License

Proprietary
