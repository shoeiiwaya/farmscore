"""
Demo API — 認証不要のデモエンドポイント
"""

from fastapi import APIRouter, Query
from typing import Optional

from app.services.scoring_engine import calculate_farm_score

router = APIRouter()


@router.get("/demo/score", tags=["demo"])
async def demo_score(
    lat: float = Query(35.4437, description="緯度（デフォルト: 横浜）"),
    lon: float = Query(139.6380, description="経度（デフォルト: 横浜）"),
    crop: Optional[str] = Query(None, description="対象作物"),
):
    """
    認証不要のデモスコアリング。

    レート制限: 20リクエスト/時間（IP別）
    """
    result = await calculate_farm_score(lat, lon, crop)
    return result


@router.get("/demo/crops", tags=["demo"])
def demo_crops():
    """利用可能な作物一覧"""
    from app.services.crop_recommender import CROP_DATABASE
    return {
        key: {
            "name_ja": info["name_ja"],
            "category": info["category"],
            "season": info["season"],
        }
        for key, info in CROP_DATABASE.items()
    }


@router.get("/demo/regions", tags=["demo"])
def demo_regions():
    """サンプル地点一覧"""
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
