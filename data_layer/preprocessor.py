"""
Data preprocessing logic.

Maps raw columns to canonical fields, parses cuisines, coerces numbers,
handles invalid values, and computes budget tiers.
"""

from __future__ import annotations

import logging
import re
import pandas as pd
from src.config import settings

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Handles parsing, cleaning, and schema mapping for the raw Zomato dataset."""

    @staticmethod
    def parse_rating(rate_str: str | None) -> float | None:
        """Parse rating string (e.g., "4.1/5", "4.5 / 5", "NEW", "-") into a float.

        Returns None if parsing fails or rating is invalid/missing.
        """
        if not rate_str or not isinstance(rate_str, str):
            return None

        rate_str = rate_str.strip()
        if rate_str in ("NEW", "-", ""):
            return None

        # Extract number before the slash, allowing optional spaces
        match = re.match(r"^([0-9.]+)\s*/\s*5", rate_str)
        if match:
            try:
                val = float(match.group(1))
                if 0.0 <= val <= 5.0:
                    return val
            except ValueError:
                pass

        # Try direct float conversion
        try:
            val = float(rate_str)
            if 0.0 <= val <= 5.0:
                return val
        except ValueError:
            pass

        return None

    @staticmethod
    def parse_cost(cost_str: str | float | int | None) -> int | None:
        """Parse cost string (e.g. "1,200", "2,500 for two") to integer.

        Returns None if parsing fails.
        """
        if cost_str is None:
            return None

        if isinstance(cost_str, (int, float)):
            if pd.isna(cost_str):
                return None
            return int(cost_str)

        if not isinstance(cost_str, str):
            return None

        # Find the first sequence of digits and commas
        match = re.search(r"([0-9,]+)", cost_str)
        if not match:
            return None

        cost_str_clean = match.group(1).replace(",", "").strip()
        try:
            return int(cost_str_clean)
        except ValueError:
            return None

    @staticmethod
    def parse_cuisines(cuisines_str: str | None) -> list[str]:
        """Parse comma-separated cuisines string into a list of cleaned cuisine names.

        Returns empty list if cuisines is missing.
        """
        if not cuisines_str or not isinstance(cuisines_str, str):
            return []
        return [c.strip() for c in cuisines_str.split(",") if c.strip()]

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process the raw DataFrame to conform to the canonical schema.

        Performs:
        - Renaming columns.
        - Processing ratings, cost, cuisines, and location.
        - Dropping rows with missing critical information (name, location).
        - Imputing missing ratings/costs with median.
        - Deriving budget tier.
        """
        # Ensure we work on a copy
        df = df.copy()

        # Log initial row count
        initial_count = len(df)
        logger.info(f"Starting preprocessing on {initial_count} rows.")

        # 1. Rename columns to match canonical schema (ignoring case/spaces where possible)
        rename_map = {
            "name": "name",
            "location": "location",
            "rate": "raw_rate",
            "votes": "votes",
            "rest_type": "rest_type",
            "cuisines": "raw_cuisines",
            "approx_cost(for two people)": "raw_cost",
        }

        # Select only required columns if they exist, keeping name/location/votes/rest_type
        # Add fallback for missing columns
        for col in rename_map:
            if col not in df.columns:
                # If exact column name is not found, try case-insensitive or partial match
                matched_cols = [c for c in df.columns if c.lower().replace(" ", "") == col.lower().replace(" ", "")]
                if matched_cols:
                    df.rename(columns={matched_cols[0]: col}, inplace=True)

        df = df.rename(columns=rename_map)

        # Ensure required columns are present in some form, fill defaults if completely missing
        required_cols = ["name", "location"]
        for col in required_cols:
            if col not in df.columns:
                raise KeyError(f"Required column '{col}' is missing from raw dataset. Columns: {list(df.columns)}")

        # 2. Handle missing critical identifier columns (name and location must be valid)
        df.dropna(subset=["name", "location"], inplace=True)
        df = df[df["name"].astype(str).str.strip() != ""]
        df = df[df["location"].astype(str).str.strip() != ""]

        # 3. Clean and parse fields
        df["rating"] = df["raw_rate"].apply(self.parse_rating) if "raw_rate" in df.columns else None
        df["cost_for_two"] = df["raw_cost"].apply(self.parse_cost) if "raw_cost" in df.columns else None
        df["cuisines"] = df["raw_cuisines"].apply(self.parse_cuisines) if "raw_cuisines" in df.columns else None
        if "cuisines" not in df.columns or df["cuisines"].isnull().all():
            df["cuisines"] = [[] for _ in range(len(df))]

        df["votes"] = pd.to_numeric(df.get("votes"), errors="coerce").fillna(0).astype(int) if "votes" in df.columns else 0
        df["rest_type"] = df["rest_type"].fillna("").astype(str).str.strip() if "rest_type" in df.columns else ""

        # Normalise location
        df["location"] = df["location"].astype(str).str.strip().str.title()

        # 4. Impute missing ratings and costs
        # Instead of dropping, we impute ratings/costs with median values so we don't lose data
        median_rating = df["rating"].median()
        if pd.isna(median_rating):
            median_rating = 3.5  # fallback if all ratings are null
        df["rating"] = df["rating"].fillna(median_rating)

        median_cost = df["cost_for_two"].median()
        if pd.isna(median_cost):
            median_cost = 500  # fallback if all costs are null
        df["cost_for_two"] = df["cost_for_two"].fillna(median_cost).astype(int)

        # 5. Derive budget tier
        def get_budget_tier(cost: int) -> str:
            low_threshold = settings.BUDGET_THRESHOLDS["low"]
            medium_threshold = settings.BUDGET_THRESHOLDS["medium"]
            if cost <= low_threshold:
                return "low"
            elif cost <= medium_threshold:
                return "medium"
            else:
                return "high"

        df["budget_tier"] = df["cost_for_two"].apply(get_budget_tier)

        # 6. Generate a stable ID
        # Since the source dataset doesn't have an ID, we use the reset index as string IDs
        df.reset_index(drop=True, inplace=True)
        df["id"] = df.index.astype(str)

        # Keep only canonical columns
        canonical_cols = ["id", "name", "location", "cuisines", "cost_for_two", "rating", "votes", "rest_type", "budget_tier"]
        df = df[canonical_cols]

        processed_count = len(df)
        dropped_count = initial_count - processed_count
        logger.info(f"Preprocessing complete. Kept {processed_count} rows, dropped {dropped_count} invalid rows.")

        if processed_count == 0:
            raise ValueError(f"All {initial_count} rows were invalid after preprocessing.")

        return df
