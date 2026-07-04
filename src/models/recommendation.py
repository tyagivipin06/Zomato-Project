"""
Recommendation output models.

Phase 0 stub — structures defined based on architecture.md §3.4 Output Model.
Full implementation (Groq response parsing, enrichment) added in Phase 3.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Recommendation:
    """A single ranked restaurant recommendation produced by the Groq LLM.

    Produced by ``RecommendationEnricher`` which joins the LLM's ranking output
    with the full ``Restaurant`` record from the repository.
    """

    rank: int
    """Position in the recommendation list (1-indexed)."""

    name: str
    """Restaurant display name."""

    cuisine: str
    """Joined cuisine string for display, e.g. ``"Italian, Continental"``."""

    rating: float
    """Aggregate rating (0.0 – 5.0)."""

    estimated_cost: int
    """``cost_for_two`` in INR."""

    explanation: str
    """Groq-generated rationale tied to the user's preferences.

    Falls back to ``"Top-rated match for your preferences."`` when Groq is
    unavailable (heuristic ranking path).
    """

    restaurant_id: str = ""
    """Internal id linking back to the source ``Restaurant`` record."""


@dataclass
class RecommendationResponse:
    """The complete response returned to the UI / API layer.

    Wraps a list of ``Recommendation`` objects together with an optional Groq
    summary and request metadata.
    """

    recommendations: list[Recommendation] = field(default_factory=list)
    """Ranked list of recommendations (up to ``TOP_K_RECOMMENDATIONS`` items)."""

    summary: str | None = None
    """Optional Groq-generated overview of the recommendation set."""

    metadata: dict = field(default_factory=dict)
    """Request-level metadata including:

    - ``candidates_considered``: number of restaurants sent to Groq.
    - ``filters_applied``: dict of active filter values.
    - ``model``: Groq model used (or ``"heuristic"`` if fallback was triggered).
    - ``relaxation_applied``: bool, set to ``True`` if filter constraints were loosened.
    """
