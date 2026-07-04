"""
Pytest configuration and global fixtures.
"""

from __future__ import annotations

import os
import sys

# Set dummy environment variables for tests before importing any app modules
os.environ["GROQ_API_KEY"] = "mock-groq-api-key-for-testing"
os.environ["HF_DATASET_NAME"] = "ManikaSaini/zomato-restaurant-recommendation"
os.environ["DATA_CACHE_PATH"] = "./data/test_restaurants.parquet"
