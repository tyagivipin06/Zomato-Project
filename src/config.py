"""
Application configuration.

All settings are loaded from environment variables (via .env or shell).
Copy .env.example → .env and fill in your GROQ_API_KEY before running.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings backed by environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Groq LLM ──────────────────────────────────────────────────────────────
    GROQ_API_KEY: str = Field(
        ...,
        description="Groq API key — obtain from https://console.groq.com",
    )
    GROQ_MODEL: str = Field(
        default="llama-3.3-70b-versatile",
        description="Primary Groq model for ranking and explanations.",
    )
    GROQ_FALLBACK_MODEL: str = Field(
        default="llama-3.1-8b-instant",
        description="Fallback Groq model (faster / cheaper) for dev or cost-sensitive runs.",
    )
    GROQ_TEMPERATURE: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="Sampling temperature for Groq completions. Retry uses 0.1.",
    )

    # ── Hugging Face Dataset ───────────────────────────────────────────────────
    HF_DATASET_NAME: str = Field(
        default="ManikaSaini/zomato-restaurant-recommendation",
        description="Hugging Face dataset identifier.",
    )

    # ── Local Data Cache ───────────────────────────────────────────────────────
    DATA_CACHE_PATH: str = Field(
        default="./data/restaurants.parquet",
        description="Local path for caching the preprocessed dataset.",
    )

    # ── Budget Thresholds (INR cost-for-two) ──────────────────────────────────
    # Tier boundaries:  low ≤ BUDGET_LOW_MAX  <  medium ≤ BUDGET_MEDIUM_MAX  <  high
    BUDGET_LOW_MAX: int = Field(
        default=500,
        description="Maximum cost_for_two (INR) for 'low' budget tier.",
    )
    BUDGET_MEDIUM_MAX: int = Field(
        default=1500,
        description="Maximum cost_for_two (INR) for 'medium' budget tier. 'High' is above this.",
    )

    # ── Recommendation Engine ──────────────────────────────────────────────────
    MAX_CANDIDATES_FOR_LLM: int = Field(
        default=20,
        description="Maximum number of pre-filtered candidates sent to Groq for ranking.",
    )
    TOP_K_RECOMMENDATIONS: int = Field(
        default=5,
        description="Final number of ranked recommendations returned to the user.",
    )

    # ── Convenience property ──────────────────────────────────────────────────
    @property
    def BUDGET_THRESHOLDS(self) -> dict[str, int]:
        """Mapping of budget tier name → upper bound (INR cost-for-two).

        Usage::

            if restaurant.cost_for_two <= settings.BUDGET_THRESHOLDS["low"]:
                tier = "low"
        """
        return {
            "low": self.BUDGET_LOW_MAX,
            "medium": self.BUDGET_MEDIUM_MAX,
        }


# Module-level singleton — import this everywhere:
#   from src.config import settings
settings = Settings()
