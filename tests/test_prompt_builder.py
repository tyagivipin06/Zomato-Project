import pytest
import json
from src.llm.prompt_builder import PromptBuilder
from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant

def test_prompt_builder_includes_preferences_and_candidates():
    # Setup test data
    prefs = UserPreferences(
        location="Bangalore",
        budget="medium",
        min_rating=4.5,
        cuisine="Italian",
        additional="outdoor seating"
    )
    
    candidates = [
        Restaurant(id="1", name="Pasta Fresca", location="Bangalore", cuisines=["Italian"], rating=4.6, votes=100, cost_for_two=1200),
        Restaurant(id="2", name="Pizza Place", location="Bangalore", cuisines=["Italian", "Pizza"], rating=4.5, votes=200, cost_for_two=800)
    ]
    
    # Execute
    messages = PromptBuilder.build_prompt(prefs, candidates)
    
    # Verify structure
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    
    # Verify content
    user_prompt = messages[1]["content"]
    
    # Check preferences are passed
    assert "Bangalore" in user_prompt
    assert "Italian" in user_prompt
    assert "outdoor seating" in user_prompt
    
    # Check candidates are serialized
    assert "Pasta Fresca" in user_prompt
    assert "Pizza Place" in user_prompt
    
    # Verify we ask for JSON
    system_prompt = messages[0]["content"]
    assert "JSON" in system_prompt or "json" in system_prompt
