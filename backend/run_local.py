"""
FarmScore Local Runner — DB不要でスコアリングAPIを起動
docker compose不要、Python単体で動作
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn

from app.services.scoring_engine import calculate_farm_score
from app.services.crop_recommender import CROP_DATABASE
from app.services.global_data import GLOBAL_CROPS_EXTRA
from app.services.fertilizer_advisor import (
    FERTILIZER_DATABASE, CROP_FERTILIZATION_STANDARDS, get_fertilizer_recommendation,
)
from app.services.japan_adaptation import analyze_japan_adaptation, get_crop_adaptation_detail

app = FastAPI(
    title="FarmScore API (Local)",
    description="農地ポテンシャル診断API — DB不要ローカル版",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "FarmScore API (Local)",
        "version": "1.0.0",
        "docs": "/docs",
        "try": "/v1/demo/score?lat=35.44&lon=139.64",
    }


@app.get("/v1/demo/score")
async def demo_score(
    lat: float = Query(35.4437, ge=-90.0, le=90.0, description="緯度（世界対応）"),
    lon: float = Query(139.6380, ge=-180.0, le=180.0, description="経度（世界対応）"),
    crop: Optional[str] = Query(None, description="対象作物 (rice, tomato, strawberry 等)"),
):
    """農地適性スコア — 認証不要"""
    return await calculate_farm_score(lat, lon, crop)


@app.post("/v1/demo/score/batch")
async def batch_score(locations: list[dict]):
    """バッチスコアリング — 最大50地点"""
    results = []
    for loc in locations[:50]:
        r = await calculate_farm_score(loc["lat"], loc["lon"], loc.get("crop"))
        results.append(r)
    return {"results": results, "count": len(results)}


@app.get("/v1/demo/crops")
def list_crops():
    """利用可能な作物一覧（日本137種 + グローバル作物）"""
    result = {
        key: {"name_ja": info["name_ja"], "category": info["category"], "season": info["season"]}
        for key, info in CROP_DATABASE.items()
    }
    for key, info in GLOBAL_CROPS_EXTRA.items():
        if key not in result:
            result[key] = {"name_ja": info["name_ja"], "category": info["category"], "season": info["season"]}
    return result


@app.get("/v1/demo/regions")
def sample_regions():
    """サンプル地点"""
    return [
        {"name": "横浜市（戸塚区）", "lat": 35.3964, "lon": 139.5309, "description": "都市近郊農業"},
        {"name": "千葉県南房総", "lat": 35.0465, "lon": 139.8570, "description": "温暖な花卉・果樹地帯"},
        {"name": "茨城県つくば", "lat": 36.0835, "lon": 140.0764, "description": "関東平野の大規模農業"},
        {"name": "長野県松本", "lat": 36.2381, "lon": 137.9720, "description": "高冷地レタス・セロリ"},
        {"name": "新潟県魚沼", "lat": 37.0667, "lon": 138.9500, "description": "コシヒカリの産地"},
        {"name": "北海道十勝", "lat": 42.9236, "lon": 143.1966, "description": "大規模畑作地帯"},
        {"name": "静岡県牧之原", "lat": 34.7421, "lon": 138.2210, "description": "茶の一大産地"},
        {"name": "宮崎県都城", "lat": 31.7275, "lon": 131.0621, "description": "畜産＋園芸"},
    ]


@app.get("/v1/demo/fertilizers")
def list_fertilizers():
    """肥料・土壌改良材データベース（25種以上）"""
    return {
        key: {
            "name_ja": info["name_ja"],
            "category": info["category"],
            "npk": info["npk"],
            "speed": info["speed"],
            "price_range": info["price_range"],
        }
        for key, info in FERTILIZER_DATABASE.items()
    }


@app.get("/v1/demo/fertilizer")
def fertilizer_advice(
    soil_type: str = Query("褐色森林土", description="土壌タイプ"),
    soil_ph: str = Query("5.5-6.5", description="pH範囲"),
    drainage: str = Query("moderate", description="排水性 (poor/moderate/good/excessive)"),
    organic_matter: str = Query("medium", description="有機物 (very_low/low/medium/high)"),
    crop: Optional[str] = Query(None, description="対象作物"),
):
    """肥料・土壌改良アドバイス"""
    return get_fertilizer_recommendation(soil_type, soil_ph, drainage, organic_matter, crop)


@app.get("/v1/demo/fertilizer/standards")
def fertilizer_standards():
    """作物別施肥基準（10aあたり標準施肥量）"""
    return {
        key: {
            "name_ja": std["name_ja"],
            "base_npk": std["base"],
            "topdress": std["topdress"],
            "notes": std["notes"],
        }
        for key, std in CROP_FERTILIZATION_STANDARDS.items()
    }


@app.get("/v1/demo/adaptation")
def japan_adaptation():
    """グローバル作物の日本適応分析 — どの海外作物が日本で栽培可能か"""
    return analyze_japan_adaptation()


@app.get("/v1/demo/adaptation/{crop_key}")
def japan_adaptation_detail(crop_key: str):
    """特定グローバル作物の日本適応詳細"""
    result = get_crop_adaptation_detail(crop_key)
    if result is None:
        return {"error": f"作物 '{crop_key}' は見つかりません", "available": list(GLOBAL_CROPS_EXTRA.keys())}
    return result


@app.get("/v1/admin/attribution")
def attribution():
    """データソース"""
    return {
        "data_sources": [
            {"name": "農研機構 日本土壌インベントリー", "usage": "土壌分析"},
            {"name": "気象庁 メッシュ平年値", "usage": "気候分析"},
            {"name": "国土数値情報", "usage": "河川・洪水データ"},
            {"name": "国土地理院 標高API", "usage": "DEM標高"},
        ]
    }


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    print(f"\n  🌱 FarmScore API starting...")
    print(f"  📍 http://localhost:{port}")
    print(f"  📖 http://localhost:{port}/docs")
    print(f"  🔍 http://localhost:{port}/v1/demo/score?lat=35.44&lon=139.64\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
