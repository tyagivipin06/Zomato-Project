"""
Unit tests for the DataPreprocessor class.
"""

from __future__ import annotations

import os
from unittest.mock import patch
import pandas as pd
import pytest
from data_layer.preprocessor import DataPreprocessor


@pytest.fixture
def preprocessor():
    return DataPreprocessor()


def test_parse_rating(preprocessor):
    """Test various rating formats."""
    # Valid formats
    assert preprocessor.parse_rating("4.1/5") == 4.1
    assert preprocessor.parse_rating("4.5 / 5") == 4.5
    assert preprocessor.parse_rating("3.0/5") == 3.0
    assert preprocessor.parse_rating("4.2") == 4.2

    # Edge cases / Invalid formats
    assert preprocessor.parse_rating("NEW") is None
    assert preprocessor.parse_rating("-") is None
    assert preprocessor.parse_rating("") is None
    assert preprocessor.parse_rating(None) is None
    assert preprocessor.parse_rating("invalid") is None
    assert preprocessor.parse_rating("9.9/5") is None  # out of 0.0 - 5.0 range
    assert preprocessor.parse_rating("-1.5") is None


def test_parse_cost(preprocessor):
    """Test cost strings parsing."""
    assert preprocessor.parse_cost("800") == 800
    assert preprocessor.parse_cost("1,200") == 1200
    assert preprocessor.parse_cost("2,500 for two") == 2500
    assert preprocessor.parse_cost(1500) == 1500
    assert preprocessor.parse_cost(350.5) == 350

    # Invalid formats
    assert preprocessor.parse_cost("") is None
    assert preprocessor.parse_cost("invalid") is None
    assert preprocessor.parse_cost(None) is None


def test_parse_cuisines(preprocessor):
    """Test cuisine comma parsing."""
    assert preprocessor.parse_cuisines("North Indian, Mughlai, Chinese") == ["North Indian", "Mughlai", "Chinese"]
    assert preprocessor.parse_cuisines("Italian") == ["Italian"]
    assert preprocessor.parse_cuisines("") == []
    assert preprocessor.parse_cuisines(None) == []


def test_budget_tier_assignment(preprocessor):
    """Test derivation of budget tiers based on cost thresholds."""
    raw_data = {
        "name": ["Rest A", "Rest B", "Rest C", "Rest D"],
        "location": ["Bangalore", "Bangalore", "Bangalore", "Bangalore"],
        "rate": ["4.1/5", "3.5/5", "4.2/5", "4.5/5"],
        "votes": [100, 20, 200, 50],
        "cuisines": ["Italian", "Indian", "Chinese", "Mexican"],
        "approx_cost(for two people)": ["400", "800", "1500", "2000"],
    }
    df = pd.DataFrame(raw_data)

    # Patch config settings thresholds to low=500, medium=1500
    env_patch = {"GROQ_API_KEY": "dummy"}
    with patch.dict(os.environ, env_patch, clear=False):
        processed_df = preprocessor.preprocess(df)

        assert processed_df.loc[0, "budget_tier"] == "low"     # cost 400 <= 500
        assert processed_df.loc[1, "budget_tier"] == "medium"  # cost 800 <= 1500
        assert processed_df.loc[2, "budget_tier"] == "medium"  # cost 1500 <= 1500
        assert processed_df.loc[3, "budget_tier"] == "high"    # cost 2000 > 1500


def test_invalid_rows_handling(preprocessor):
    """Test dropping rows without name or location, and filling empty values."""
    raw_data = {
        "name": ["Rest A", "", None, "Rest D"],
        "location": ["Bangalore", "Bangalore", "Bangalore", ""],
        "rate": ["4.1/5", "3.5/5", "4.2/5", "4.5/5"],
        "votes": [100, 20, 200, 50],
        "cuisines": ["Italian", "Indian", "Chinese", "Mexican"],
        "approx_cost(for two people)": ["400", "800", "1500", "2000"],
    }
    df = pd.DataFrame(raw_data)

    env_patch = {"GROQ_API_KEY": "dummy"}
    with patch.dict(os.environ, env_patch, clear=False):
        processed_df = preprocessor.preprocess(df)

        # Only Rest A is valid (Rest B has empty name, Rest C has None name, Rest D has empty location)
        assert len(processed_df) == 1
        assert processed_df.loc[0, "name"] == "Rest A"
