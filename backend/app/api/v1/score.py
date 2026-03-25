"""
Score API — 農地適性スコアリング
"""

from fastapi import APIRouter, Query
from typing import Optional

from app.services.scoring_engine import calculate_farm_score
from app.schemas.score import ScoreRequest, ScoreResponse, BatchScoreRequest, BatchScoreResponse

router = APIRouter()


@router.get("/score", response_model=ScoreResponse, tags=["score"])
async def get_farm_score(
    lat: float = Query(..., ge=20.0, le=46.0, description="緯度"),
    lon: float = Query(..., ge=122.0, le=154.0, description="経度"),
    crop: Optional[str] = Query(None, description="対象作物 (例: rice, tomato, strawberry)"),
):
    """
    農地適性スコアを算出します。

    緯度・経度を入力すると、土壌・気候・水利・日照・標高の5カテゴリで
    農地としての適性を0〜100でスコアリングし、おすすめ作物を提案します。

    **データソース**: 農研機構eSoil, 気象庁, 国土数値情報, GSI DEM
    """
    result = await calculate_farm_score(lat, lon, crop)
    return result


@router.post("/score/batch", response_model=BatchScoreResponse, tags=["score"])
async def batch_farm_score(req: BatchScoreRequest):
    """
    最大50地点を一括スコアリングします。
    """
    results = []
    for loc in req.locations:
        r = await calculate_farm_score(loc.lat, loc.lon, loc.crop)
        results.append(r)

    return BatchScoreResponse(results=results, count=len(results))
