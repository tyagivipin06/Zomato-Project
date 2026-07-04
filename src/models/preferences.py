"""
UserPreferences domain model.

Phase 2 Implementation: Pydantic model with validation for basic constraints.
Complex validation (e.g., location existence) is handled by the PreferenceValidator service.
"""

from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

class UserPreferences(BaseModel):
    """Represents the preferences submitted by the user."""

    location: str = Field(..., description="City or locality the user wants restaurants in.")
    budget: Literal["low", "medium", "high"] = Field(..., description="Budget tier: 'low' | 'medium' | 'high'.")
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Minimum acceptable rating (0.0 – 5.0).")
    cuisine: Optional[str] = Field(default=None, description="Optional preferred cuisine.")
    additional: Optional[str] = Field(default=None, description="Optional free-text preferences.")

    @field_validator("location")
    @classmethod
    def location_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Location cannot be empty")
        return v
