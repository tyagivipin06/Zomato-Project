import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ResponseParser:
    @staticmethod
    def parse(raw_json: str) -> Dict[str, Any]:
        """
        Parses and validates the JSON output from the LLM.
        Expected format:
        {
          "summary": "...",
          "recommendations": [
            { "id": "...", "rank": 1, "explanation": "..." }
          ]
        }
        """
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise ValueError("Invalid JSON response from LLM") from e
            
        if "summary" not in data or "recommendations" not in data:
            raise ValueError("Missing 'summary' or 'recommendations' in LLM response")
            
        if not isinstance(data["recommendations"], list):
            raise ValueError("'recommendations' must be a list")
            
        for rec in data["recommendations"]:
            if not all(k in rec for k in ("id", "rank", "explanation")):
                raise ValueError(f"Recommendation missing required fields: {rec}")
                
        return data
