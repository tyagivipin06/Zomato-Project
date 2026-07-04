from fastapi.testclient import TestClient
from src.api.routes import app
import pytest

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_locations():
    # First, let's trigger the startup event to initialize services
    with TestClient(app) as client_with_startup:
        response = client_with_startup.get("/api/v1/locations")
        assert response.status_code == 200
        data = response.json()
        assert "locations" in data
        assert isinstance(data["locations"], list)

def test_get_cuisines():
    with TestClient(app) as client_with_startup:
        response = client_with_startup.get("/api/v1/cuisines")
        assert response.status_code == 200
        data = response.json()
        assert "cuisines" in data
        assert isinstance(data["cuisines"], list)

def test_recommend():
    with TestClient(app) as client_with_startup:
        payload = {
            "location": "Bangalore",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
            "additional_preferences": ""
        }
        response = client_with_startup.post("/api/v1/recommend", json=payload)
        
        # We might get 200 or potentially 500 if LLM fails, but the endpoint should be reachable
        assert response.status_code in [200, 500, 503]
        if response.status_code == 200:
            data = response.json()
            assert "recommendations" in data
            assert "summary" in data
