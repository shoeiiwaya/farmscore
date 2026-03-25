"""
FarmScore Scoring Engine Tests
"""

import asyncio
import pytest


def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class TestSoilAnalyzer:
    def test_estimate_soil_type(self):
        from backend.app.services.soil_analyzer import estimate_soil_type
        assert estimate_soil_type(35.4, 139.6, 3) == "グライ土"
        assert estimate_soil_type(35.4, 139.6, 20) == "灰色低地土"
        assert estimate_soil_type(35.4, 139.6, 50) == "褐色低地土"
        assert estimate_soil_type(35.4, 139.6, 200) == "黒ボク土"
        assert estimate_soil_type(35.4, 139.6, 400) == "褐色森林土"

    def test_soil_score_range(self):
        from backend.app.services.soil_analyzer import calculate_soil_score
        score = calculate_soil_score("黒ボク土")
        assert 0 <= score <= 100

    def test_soil_score_with_crop(self):
        from backend.app.services.soil_analyzer import calculate_soil_score
        score_generic = calculate_soil_score("黒ボク土")
        score_tea = calculate_soil_score("黒ボク土", "tea")
        # Andosol is good for tea, should score well
        assert score_tea > 0


class TestClimateAnalyzer:
    def test_get_region(self):
        from backend.app.services.climate_analyzer import get_region
        assert get_region(35.4, 139.6) == "kanto"
        assert get_region(43.0, 141.3) == "hokkaido"
        assert get_region(26.3, 127.8) == "okinawa"

    def test_climate_score_range(self):
        from backend.app.services.climate_analyzer import analyze_climate
        result = analyze_climate(35.4, 139.6)
        assert 0 <= result["score"] <= 100
        assert result["annual_temp_avg"] > 0
        assert result["annual_precip_mm"] > 0

    def test_gdd_calculation(self):
        from backend.app.services.climate_analyzer import calculate_gdd
        gdd = calculate_gdd(20.0, 200, base_temp=10.0)
        assert gdd == 2000.0

    def test_frost_risk(self):
        from backend.app.services.climate_analyzer import assess_frost_risk
        assert assess_frost_risk(365) == "極低"
        assert assess_frost_risk(100) == "極高"


class TestWaterAnalyzer:
    def test_find_nearest_river(self):
        from backend.app.services.water_analyzer import find_nearest_river
        name, dist = find_nearest_river(35.4, 139.6)
        assert isinstance(name, str)
        assert dist >= 0

    def test_water_score_range(self):
        from backend.app.services.water_analyzer import analyze_water
        result = analyze_water(35.4, 139.6, 50.0, 1500.0)
        assert 0 <= result["score"] <= 100


class TestCropRecommender:
    def test_recommend_crops(self):
        from backend.app.services.crop_recommender import recommend_crops
        crops = recommend_crops("andosol", 15.5, 1500, 1900, top_n=5)
        assert len(crops) == 5
        assert all(c["suitability_score"] >= 0 for c in crops)
        # Should be sorted descending
        scores = [c["suitability_score"] for c in crops]
        assert scores == sorted(scores, reverse=True)

    def test_target_crop_included(self):
        from backend.app.services.crop_recommender import recommend_crops
        crops = recommend_crops("sand_dune", 10.0, 500, 1000, target_crop="sweet_potato", top_n=3)
        names = [c["crop_name"] for c in crops]
        assert any("sweet_potato" in n for n in names)


class TestScoringEngine:
    def test_full_score(self):
        from backend.app.services.scoring_engine import calculate_farm_score
        result = run_async(calculate_farm_score(35.4437, 139.6380))
        assert 0 <= result["overall_score"] <= 100
        assert result["grade"] in ("S", "A", "B", "C", "D")
        assert result["soil_score"] >= 0
        assert result["climate_score"] >= 0
        assert result["water_score"] >= 0
        assert result["sunlight_score"] >= 0
        assert len(result["crop_recommendations"]) == 5
        assert "disclaimer" in result

    def test_score_with_crop(self):
        from backend.app.services.scoring_engine import calculate_farm_score
        result = run_async(calculate_farm_score(35.4437, 139.6380, "rice"))
        assert result["overall_score"] >= 0

    def test_hokkaido_score(self):
        from backend.app.services.scoring_engine import calculate_farm_score
        result = run_async(calculate_farm_score(42.9236, 143.1966))
        assert result["climate"]["climate_zone"] == "Dfb"
        assert result["climate"]["frost_risk"] in ("高", "極高")

    def test_okinawa_score(self):
        from backend.app.services.scoring_engine import calculate_farm_score
        result = run_async(calculate_farm_score(26.3, 127.8))
        assert result["climate"]["typhoon_risk"] == "極高"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
