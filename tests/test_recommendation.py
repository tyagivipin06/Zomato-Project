import pytest
import json
from src.llm.response_parser import ResponseParser
from src.llm.prompt_builder import PromptBuilder
from src.llm.recommendation import RecommendationService
from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant
from src.services.filter import RestaurantFilter

def test_response_parser_valid():
    valid_json = """
    {
        "summary": "Here are my top picks.",
        "recommendations": [
            {
                "id": "1",
                "rank": 1,
                "explanation": "Great Italian food."
            }
        ]
    }
    """
    data = ResponseParser.parse(valid_json)
    assert data["summary"] == "Here are my top picks."
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["id"] == "1"
    assert data["recommendations"][0]["rank"] == 1
    assert data["recommendations"][0]["explanation"] == "Great Italian food."

def test_response_parser_invalid_json():
    with pytest.raises(ValueError, match="Invalid JSON response from LLM"):
        ResponseParser.parse("This is not JSON")

def test_response_parser_missing_fields():
    missing_summary = """{"recommendations": [{"id": "1", "rank": 1, "explanation": "test"}]}"""
    with pytest.raises(ValueError, match="Missing 'summary' or 'recommendations'"):
        ResponseParser.parse(missing_summary)
        
    missing_explanation = """{"summary": "Test", "recommendations": [{"id": "1", "rank": 1}]}"""
    with pytest.raises(ValueError, match="Recommendation missing required fields"):
        ResponseParser.parse(missing_explanation)

class MockLLMClient:
    def __init__(self, response_text, should_fail=False):
        self.response_text = response_text
        self.should_fail = should_fail
        
    def complete(self, messages, temperature=None):
        if self.should_fail:
            raise Exception("Mocked API Error")
        return self.response_text

def test_recommendation_service_success():
    class MockFilter:
        def filter(self, prefs):
            return [
                Restaurant(id="1", name="Italian Place", location="Bangalore", cuisines=["Italian"], cost_for_two=1000, rating=4.5, votes=100, rest_type="Casual", budget_tier="medium")
            ], []

    mock_llm_response = """
    {
        "summary": "Enjoy this recommendation.",
        "recommendations": [
            {
                "id": "1",
                "rank": 1,
                "explanation": "Because you love Italian."
            }
        ]
    }
    """
    mock_client = MockLLMClient(mock_llm_response)
    service = RecommendationService(filter_service=MockFilter(), llm_client=mock_client)
    
    prefs = UserPreferences(location="Bangalore", budget="medium")
    response, warnings = service.recommend(prefs)
    
    assert response.summary == "Enjoy this recommendation."
    assert len(response.recommendations) == 1
    assert response.recommendations[0].name == "Italian Place"
    assert response.recommendations[0].explanation == "Because you love Italian."

def test_recommendation_service_fallback():
    class MockFilter:
        def filter(self, prefs):
            return [
                Restaurant(id="1", name="Italian Place", location="Bangalore", cuisines=["Italian"], cost_for_two=1000, rating=4.5, votes=100, rest_type="Casual", budget_tier="medium")
            ], []

    mock_client = MockLLMClient("", should_fail=True)
    service = RecommendationService(filter_service=MockFilter(), llm_client=mock_client)
    
    prefs = UserPreferences(location="Bangalore", budget="medium")
    response, warnings = service.recommend(prefs)
    
    # Should fallback to heuristic
    assert "Here are the top-rated restaurants matching your preferences." in response.summary
    assert len(response.recommendations) == 1
    assert response.recommendations[0].name == "Italian Place"
    assert "AI recommendations temporarily unavailable" in warnings[0]
