"""
Restaurant domain model.

Phase 0 stub — fields defined based on the canonical schema in architecture.md §3.1.
Full implementation (validation, serialization helpers) added in Phase 1.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Restaurant:
    """Represents a single restaurant entry from the Zomato dataset.

    All fields map to the canonical schema defined in architecture.md §3.1.
    ``budget_tier`` is derived by the preprocessor using ``BUDGET_THRESHOLDS``.
    """

    id: str
    """Stable unique identifier (dataset row index converted to string)."""

    name: str
    """Restaurant display name."""

    location: str
    """City or locality (title-cased, trimmed)."""

    cuisines: list[str] = field(default_factory=list)
    """List of cuisine tags, e.g. ``["Italian", "Continental"]``."""

    cost_for_two: int = 0
    """Approximate cost for two people (INR)."""

    rating: float = 0.0
    """Aggregate rating (0.0 – 5.0)."""

    votes: int = 0
    """Number of votes — used as a popularity signal for tie-breaking."""

    rest_type: str = ""
    """Restaurant type, e.g. 'Casual Dining', 'Café'. Optional."""

    budget_tier: str = ""
    """Derived tier: 'low' | 'medium' | 'high'. Set by DataPreprocessor."""
