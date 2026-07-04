"""
Validation and normalization services for user preferences.
"""

from __future__ import annotations
from typing import List, Tuple
from difflib import get_close_matches
from src.models.preferences import UserPreferences
from data_layer.repository import RestaurantRepository

class PreferenceNormalizer:
    """Normalizes raw input preferences."""
    
    # Optional alias map for common city typos or alternative names
    CITY_ALIAS_MAP = {
        "bengaluru": "bangalore",
        "delhi ncr": "new delhi",
        "bombay": "mumbai",
    }

    @staticmethod
    def normalize(prefs: UserPreferences) -> UserPreferences:
        """Trim strings, lowercase cuisines, map city aliases."""
        loc = prefs.location.strip()
        loc_lower = loc.lower()
        if loc_lower in PreferenceNormalizer.CITY_ALIAS_MAP:
            loc = PreferenceNormalizer.CITY_ALIAS_MAP[loc_lower]
        
        # Ensure location is properly title-cased as in the dataset (usually title cased)
        loc = loc.title()
        
        cuisine = prefs.cuisine
        if cuisine is not None:
            cuisine = cuisine.strip().lower()
            if not cuisine:
                cuisine = None

        return UserPreferences(
            location=loc,
            budget=prefs.budget,
            min_rating=prefs.min_rating,
            cuisine=cuisine,
            additional=prefs.additional.strip() if prefs.additional else None
        )


class PreferenceValidator:
    """Validates preferences against the actual dataset."""

    def __init__(self, repository: RestaurantRepository):
        self.repository = repository

    def validate(self, prefs: UserPreferences) -> Tuple[bool, List[str], UserPreferences]:
        """
        Validates the normalized preferences.
        Returns:
            (is_valid, error_messages, updated_prefs)
            updated_prefs will have the fuzzy-matched cuisine if applicable.
        """
        errors = []
        updated_prefs = prefs.model_copy()

        # Check location
        valid_locations = self.repository.get_locations()
        # Case insensitive check
        valid_locations_lower = {l.lower(): l for l in valid_locations}
        
        if prefs.location.lower() not in valid_locations_lower:
            errors.append(f"Location '{prefs.location}' not found. Suggestions: {', '.join(valid_locations[:5])}...")
        else:
            updated_prefs.location = valid_locations_lower[prefs.location.lower()]

        # Fuzzy match cuisine if provided
        if prefs.cuisine:
            valid_cuisines = self.repository.get_cuisines()
            valid_cuisines_lower = {c.lower(): c for c in valid_cuisines}
            
            if prefs.cuisine.lower() in valid_cuisines_lower:
                updated_prefs.cuisine = valid_cuisines_lower[prefs.cuisine.lower()]
            else:
                # Try fuzzy matching with difflib
                matches = get_close_matches(prefs.cuisine.lower(), list(valid_cuisines_lower.keys()), n=1, cutoff=0.7)
                if matches:
                    updated_prefs.cuisine = valid_cuisines_lower[matches[0]]
                else:
                    errors.append(f"Cuisine '{prefs.cuisine}' not recognized.")

        return len(errors) == 0, errors, updated_prefs
