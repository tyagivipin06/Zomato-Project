"""
Filtering service to narrow down candidates before passing to the LLM.
"""

from __future__ import annotations
from typing import List, Tuple
from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant
from data_layer.repository import RestaurantRepository
from src.config import settings
import logging

logger = logging.getLogger(__name__)

class RestaurantFilter:
    """Filters the dataset deterministically based on user preferences."""

    def __init__(self, repository: RestaurantRepository):
        self.repository = repository

    def filter(self, prefs: UserPreferences) -> Tuple[List[Restaurant], List[str]]:
        """
        Applies hard constraints and constraint relaxation if needed.
        Returns:
            (filtered_restaurants, warning_messages)
        """
        all_restaurants = self.repository.get_all()
        warnings = []
        
        # Base filter by location (always required, guaranteed to exist by validator)
        location_matched = [r for r in all_restaurants if r.location.lower() == prefs.location.lower()]

        # Try strict filtering
        results = self._apply_filters(location_matched, prefs.budget, prefs.min_rating, prefs.cuisine)
        
        if results:
            return self._sort_and_cap(results), warnings
        
        # Constraint relaxation 1: Drop cuisine
        if prefs.cuisine:
            warnings.append(f"No results found for cuisine '{prefs.cuisine}'. Broadening search to all cuisines.")
            results = self._apply_filters(location_matched, prefs.budget, prefs.min_rating, None)
            if results:
                return self._sort_and_cap(results), warnings

        # Constraint relaxation 2: Widen budget
        warnings.append(f"No results found for budget '{prefs.budget}'. Relaxing budget constraint.")
        results = self._apply_filters(location_matched, None, prefs.min_rating, None)
        if results:
            return self._sort_and_cap(results), warnings

        # Constraint relaxation 3: Lower min_rating
        if prefs.min_rating > 0:
            warnings.append(f"No results found for minimum rating {prefs.min_rating}. Relaxing rating constraint.")
            results = self._apply_filters(location_matched, None, 0.0, None)
            if results:
                return self._sort_and_cap(results), warnings

        # If still empty (very rare, means no restaurants in location)
        warnings.append(f"No restaurants found in location '{prefs.location}'.")
        return [], warnings

    def _apply_filters(self, 
                       restaurants: List[Restaurant], 
                       budget: str | None, 
                       min_rating: float, 
                       cuisine: str | None) -> List[Restaurant]:
        """Apply the active constraints to the list of restaurants."""
        filtered = []
        for r in restaurants:
            if budget and r.budget_tier != budget:
                continue
            if r.rating < min_rating:
                continue
            if cuisine:
                r_cuisines_lower = [c.lower() for c in r.cuisines]
                if cuisine.lower() not in r_cuisines_lower:
                    continue
            filtered.append(r)
        return filtered

    def _sort_and_cap(self, restaurants: List[Restaurant]) -> List[Restaurant]:
        """Sort by rating (desc) and votes (desc), cap at MAX_CANDIDATES_FOR_LLM."""
        sorted_rests = sorted(restaurants, key=lambda x: (x.rating, x.votes), reverse=True)
        return sorted_rests[:settings.MAX_CANDIDATES_FOR_LLM]
