"""
Phase 0 smoke tests — config loading and model stubs.

These run without a real GROQ_API_KEY by patching the environment.
"""

from __future__ import annotations

import os
from unittest.mock import patch


def test_settings_loads_with_valid_env():
    """Settings should load when GROQ_API_KEY is present in the environment."""
    env_patch = {
        "GROQ_API_KEY": "test-key-abc123",
        "GROQ_MODEL": "llama-3.3-70b-versatile",
        "GROQ_TEMPERATURE": "0.3",
    }
    with patch.dict(os.environ, env_patch, clear=False):
        # Re-import to pick up patched env
        import importlib
        import src.config as cfg_module  # noqa: PLC0415

        importlib.reload(cfg_module)
        s = cfg_module.Settings()
        assert s.GROQ_API_KEY == "test-key-abc123"
        assert s.GROQ_MODEL == "llama-3.3-70b-versatile"
        assert s.GROQ_TEMPERATURE == 0.3


def test_budget_thresholds_property():
    """BUDGET_THRESHOLDS property should return expected tier boundaries."""
    env_patch = {"GROQ_API_KEY": "test-key"}
    with patch.dict(os.environ, env_patch, clear=False):
        import importlib
        import src.config as cfg_module  # noqa: PLC0415

        importlib.reload(cfg_module)
        s = cfg_module.Settings()
        thresholds = s.BUDGET_THRESHOLDS
        assert thresholds["low"] == 500
        assert thresholds["medium"] == 1500


def test_restaurant_dataclass_defaults():
    """Restaurant dataclass should instantiate with defaults."""
    from src.models.restaurant import Restaurant  # noqa: PLC0415

    r = Restaurant(id="1", name="Test Café", location="Bangalore")
    assert r.cuisines == []
    assert r.cost_for_two == 0
    assert r.rating == 0.0
    assert r.budget_tier == ""


def test_user_preferences_dataclass():
    """UserPreferences should store all fields correctly."""
    from src.models.preferences import UserPreferences  # noqa: PLC0415

    prefs = UserPreferences(
        location="Bangalore",
        budget="medium",
        min_rating=4.0,
        cuisine="Italian",
        additional="family-friendly",
    )
    assert prefs.location == "Bangalore"
    assert prefs.budget == "medium"
    assert prefs.cuisine == "Italian"


def test_recommendation_response_defaults():
    """RecommendationResponse should initialise with empty recommendations."""
    from src.models.recommendation import RecommendationResponse  # noqa: PLC0415

    resp = RecommendationResponse()
    assert resp.recommendations == []
    assert resp.summary is None
    assert resp.metadata == {}
