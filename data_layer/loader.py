"""
Dataset loading and caching.

Downloads the Zomato restaurant recommendation dataset from Hugging Face,
applies preprocessing, and caches the result locally as a parquet file.
"""

from __future__ import annotations

import logging
import os
import time
import pandas as pd
from datasets import load_dataset
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log
from src.config import settings
from data_layer.preprocessor import DataPreprocessor

logger = logging.getLogger(__name__)


class DatasetLoader:
    """Manages loading the restaurant dataset from local cache or Hugging Face."""

    def __init__(self) -> None:
        self.preprocessor = DataPreprocessor()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=10),
        reraise=True,
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _download_with_retry(self, dataset_name: str) -> pd.DataFrame:
        """Download the dataset from Hugging Face with exponential backoff retry logic."""
        logger.info(f"Downloading dataset '{dataset_name}' from Hugging Face...")
        # load_dataset returns a DatasetDict, we split 'train'
        dataset = load_dataset(dataset_name, split="train")
        # Convert Hugging Face Dataset to pandas DataFrame
        df = dataset.to_pandas()
        logger.info("Dataset downloaded successfully.")
        return df


    def load_dataset(self) -> pd.DataFrame:
        """Load the processed dataset.

        Loads from local cache if it exists, otherwise downloads, processes, caches, and returns it.
        """
        cache_path = settings.DATA_CACHE_PATH

        if os.path.exists(cache_path):
            logger.info(f"Loading dataset from local cache: {cache_path}")
            try:
                df = pd.read_parquet(cache_path)
                logger.info(f"Loaded {len(df)} restaurants from cache.")
                return df
            except Exception as exc:
                logger.error(f"Failed to read cache file at {cache_path}: {exc}. Deleting corrupt cache.")
                try:
                    os.remove(cache_path)
                except OSError:
                    pass

        # If cache doesn't exist or is corrupt, download and process
        raw_df = self._download_with_retry(settings.HF_DATASET_NAME)
        processed_df = self.preprocessor.preprocess(raw_df)

        # Cache the processed dataset
        try:
            # Ensure the directory exists
            cache_dir = os.path.dirname(cache_path)
            if cache_dir:
                os.makedirs(cache_dir, exist_ok=True)

            logger.info(f"Caching preprocessed dataset to: {cache_path}")
            processed_df.to_parquet(cache_path, index=False)
        except Exception as exc:
            # Documented in EC-C3: Log error and raise OSError with the path
            logger.critical(f"Failed to cache processed dataset to {cache_path}: {exc}")
            raise OSError(
                f"Failed to write cache to '{cache_path}'. Please check directory permissions or create it manually."
            ) from exc

        return processed_df
