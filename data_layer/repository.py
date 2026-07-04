"""
In-memory repository for querying processed restaurant data.
"""

from __future__ import annotations

import logging
import pandas as pd
from data_layer.loader import DatasetLoader
from src.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


class RestaurantRepository:
    """Provides an interface to query processed restaurant records from memory."""

    _instance: RestaurantRepository | None = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> RestaurantRepository:
        """Expose repository as a singleton to avoid reloading data multiple times."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, df: pd.DataFrame | None = None) -> None:
        """Initialise the repository.

        If df is not provided, uses DatasetLoader to load the dataset.
        """
        if self._initialized:
            return

        if df is not None:
            self._df = df
        else:
            loader = DatasetLoader()
            self._df = loader.load_dataset()

        # Map DataFrame rows to Restaurant dataclass instances for fast domain queries
        self._restaurants = self._build_restaurant_list()
        self._restaurant_map = {r.id: r for r in self._restaurants}
        self._locations = sorted(list(self._df["location"].dropna().unique()))

        # Flat unique sorted list of cuisines
        all_cuisines = set()
        for cuisines_list in self._df["cuisines"]:
            all_cuisines.update(cuisines_list)
        self._cuisines = sorted(list(all_cuisines))

        self._initialized = True
        logger.info(
            f"Repository initialized with {len(self._restaurants)} restaurants, "
            f"{len(self._locations)} locations, and {len(self._cuisines)} cuisines."
        )

    def _build_restaurant_list(self) -> list[Restaurant]:
        """Convert the internal DataFrame to a list of Restaurant model objects."""
        restaurants = []
        for _, row in self._df.iterrows():
            r = Restaurant(
                id=str(row["id"]),
                name=str(row["name"]),
                location=str(row["location"]),
                cuisines=list(row["cuisines"]),
                cost_for_two=int(row["cost_for_two"]),
                rating=float(row["rating"]),
                votes=int(row["votes"]),
                rest_type=str(row["rest_type"]),
                budget_tier=str(row["budget_tier"]),
            )
            restaurants.append(r)
        return restaurants

    def get_all(self) -> list[Restaurant]:
        """Return all restaurants in the repository."""
        return self._restaurants

    def get_locations(self) -> list[str]:
        """Return sorted list of unique normalized locations (cities/localities)."""
        return self._locations

    def get_cuisines(self) -> list[str]:
        """Return sorted list of unique cuisines."""
        return self._cuisines

    def get_by_id(self, restaurant_id: str) -> Restaurant | None:
        """Find a restaurant by its unique string ID."""
        return self._restaurant_map.get(restaurant_id)

    @classmethod
    def reset_singleton(cls) -> None:
        """Force reinitialization on next instantiation (useful for testing)."""
        cls._instance = None
        cls._initialized = False
