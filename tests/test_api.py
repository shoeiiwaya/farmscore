"""
FarmScore API Integration Tests
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Use env that doesn't need real DB for demo endpoints
    import os
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["MQTT_BROKER"] = "disabled"
    from backend.app.main import app
    return TestClient(app)


class TestDemoEndpoints:
    def test_demo_score(self, client):
        resp = client.get("/v1/demo/score?lat=35.44&lon=139.64")
        assert resp.status_code == 200
        data = resp.json()
        assert "overall_score" in data
        assert "grade" in data
        assert "soil" in data
        assert "climate" in data
        assert "water" in data
        assert "crop_recommendations" in data

    def test_demo_score_with_crop(self, client):
        resp = client.get("/v1/demo/score?lat=35.44&lon=139.64&crop=rice")
        assert resp.status_code == 200

    def test_demo_crops(self, client):
        resp = client.get("/v1/demo/crops")
        assert resp.status_code == 200
        data = resp.json()
        assert "rice" in data
        assert "tomato" in data

    def test_demo_regions(self, client):
        resp = client.get("/v1/demo/regions")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0
        assert "lat" in data[0]


class TestAdminEndpoints:
    def test_attribution(self, client):
        resp = client.get("/v1/admin/attribution")
        assert resp.status_code == 200
        data = resp.json()
        assert "data_sources" in data
        assert len(data["data_sources"]) > 0

    def test_plans(self, client):
        resp = client.get("/v1/admin/plans")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 4


class TestHealthCheck:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "FarmScore API"


class TestAuthRequired:
    def test_score_without_auth(self, client):
        resp = client.get("/v1/score?lat=35.44&lon=139.64")
        assert resp.status_code in (401, 403, 422)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
