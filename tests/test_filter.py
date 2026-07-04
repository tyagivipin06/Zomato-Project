"""
Tests for Filter and Validation services.
"""

from __future__ import annotations

import pandas as pd
import pytest
from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant
from data_layer.repository import RestaurantRepository
from src.services.validator import PreferenceNormalizer, PreferenceValidator
from src.services.filter import RestaurantFilter

@pytest.fixture
def mock_repository():
    """Returns a RestaurantRepository initialized with a small fixture dataset."""
    RestaurantRepository.reset_singleton()
    raw_data = {
        "id": ["1", "2", "3", "4", "5"],
        "name": ["Italian Bistro", "Curry House", "Burger Joint", "Sushi Place", "Pizza Corner"],
        "location": ["Bangalore", "Bangalore", "Bangalore", "Delhi", "Bangalore"],
        "cuisines": [["Italian"], ["North Indian"], ["American", "Fast Food"], ["Japanese", "Sushi"], ["Italian", "Pizza"]],
        "cost_for_two": [1200, 400, 300, 2000, 600],
        "rating": [4.5, 3.8, 4.0, 4.8, 4.2],
        "votes": [100, 50, 200, 150, 80],
        "rest_type": ["Casual Dining", "Quick Bites", "Quick Bites", "Fine Dining", "Delivery"],
        "budget_tier": ["medium", "low", "low", "high", "medium"],
    }
    df = pd.DataFrame(raw_data)
    repo = RestaurantRepository(df)
    return repo


def test_preference_normalizer():
    prefs = UserPreferences(
        location=" BENGALURU ",
        budget="medium",
        cuisine=" ITALIAN "
    )
    norm = PreferenceNormalizer.normalize(prefs)
    assert norm.location == "Bangalore"
    assert norm.cuisine == "italian"


def test_preference_validator(mock_repository):
    validator = PreferenceValidator(mock_repository)
    
    # Valid case
    prefs = UserPreferences(location="Bangalore", budget="medium", cuisine="italian")
    is_valid, errors, updated = validator.validate(prefs)
    assert is_valid is True
    assert len(errors) == 0
    assert updated.cuisine == "Italian"  # fuzzy matched / exact matched from dataset cuisines

    # Invalid location
    prefs = UserPreferences(location="UnknownCity", budget="low")
    is_valid, errors, updated = validator.validate(prefs)
    assert is_valid is False
    assert "not found" in errors[0]

    # Fuzzy match cuisine
    prefs = UserPreferences(location="Bangalore", budget="low", cuisine="itallian")
    is_valid, errors, updated = validator.validate(prefs)
    assert is_valid is True
    assert updated.cuisine == "Italian"

    # Unrecognized cuisine
    prefs = UserPreferences(location="Bangalore", budget="low", cuisine="martian food")
    is_valid, errors, updated = validator.validate(prefs)
    assert is_valid is False
    assert "not recognized" in errors[0]


def test_restaurant_filter_strict(mock_repository):
    filter_svc = RestaurantFilter(mock_repository)
    prefs = UserPreferences(location="Bangalore", budget="low", min_rating=3.0)
    
    results, warnings = filter_svc.filter(prefs)
    assert len(results) == 2
    assert results[0].name == "Burger Joint"  # higher rating (4.0 vs 3.8)
    assert results[1].name == "Curry House"
    assert len(warnings) == 0


def test_restaurant_filter_cuisine_relaxation(mock_repository):
    filter_svc = RestaurantFilter(mock_repository)
    # Asking for Japanese in Bangalore (doesn't exist in fixture)
    prefs = UserPreferences(location="Bangalore", budget="low", min_rating=3.0, cuisine="Japanese")
    
    results, warnings = filter_svc.filter(prefs)
    # Should drop cuisine constraint and return the 2 low budget places in Bangalore
    assert len(results) == 2
    assert len(warnings) == 1
    assert "Broadening search to all cuisines" in warnings[0]


def test_restaurant_filter_budget_relaxation(mock_repository):
    filter_svc = RestaurantFilter(mock_repository)
    # Asking for high budget in Bangalore (doesn't exist in fixture)
    prefs = UserPreferences(location="Bangalore", budget="high", min_rating=3.0)
    
    results, warnings = filter_svc.filter(prefs)
    # Should drop budget constraint and return top places in Bangalore > 3.0
    assert len(results) > 0
    assert len(warnings) == 1
    assert "Relaxing budget constraint" in warnings[0]
