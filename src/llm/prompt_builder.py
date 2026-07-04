from __future__ import annotations
import json
from typing import List, Dict, Any
from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant
from src.config import settings

class PromptBuilder:
    @staticmethod
    def build_prompt(prefs: UserPreferences, candidates: List[Restaurant]) -> List[Dict[str, str]]:
        top_k = min(len(candidates), settings.TOP_K_RECOMMENDATIONS)
        system_msg = (
            "You are an expert Zomato restaurant recommender. "
            "You will be provided with user preferences and a list of pre-filtered candidate restaurants. "
            f"Your task is to select and rank the top {top_k} restaurants from the given candidates based on how well they match the user's preferences. "
            "Output MUST be in strict JSON format. "
            "The JSON must have this exact structure: "
            "{\"summary\": \"A short greeting and summary of your recommendations based on their preferences.\", "
            "\"recommendations\": [{\"id\": \"<restaurant_id>\", \"rank\": <1-N>, \"explanation\": \"<Why you recommend this restaurant, mentioning their preferences like budget, rating, and cuisine if applicable.>\"}]}"
        )
        
        candidates_json = []
        for r in candidates:
            candidates_json.append({
                "id": str(r.id),
                "name": r.name,
                "cuisines": r.cuisines,
                "cost_for_two": r.cost_for_two,
                "rating": r.rating,
                "votes": r.votes,
            })
            
        user_msg = (
            f"User Preferences:\n"
            f"- Location: {prefs.location}\n"
            f"- Budget Tier: {prefs.budget}\n"
            f"- Minimum Rating: {prefs.min_rating}\n"
            f"- Preferred Cuisine: {prefs.cuisine or 'Any'}\n"
            f"- Additional requests: {prefs.additional or 'None'}\n\n"
            f"Candidate Restaurants:\n{json.dumps(candidates_json, indent=2)}\n\n"
            "Please evaluate the candidates and provide your JSON response."
        )
        
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]
