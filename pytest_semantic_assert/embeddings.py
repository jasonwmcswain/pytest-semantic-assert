"""Embedding model management with lazy loading and retry logic."""

import time
from typing import Optional

import numpy as np
import numpy.typing as npt
from sentence_transformers import SentenceTransformer

from pytest_semantic_assert.cache import EmbeddingCache
from pytest_semantic_assert.config import Configuration
from pytest_semantic_assert.exceptions import ModelLoadError, TextTooLongError, TextTooShortError


class EmbeddingManager:
    """Manages embedding model lifecycle and caching."""

    def __init__(self, config: Configuration) -> None:
        """Initialize embedding manager.

        Args:
            config: Plugin configuration
        """
        self.config = config
        self.model: Optional[SentenceTransformer] = None
        self.model_loaded = False
        self.cache = EmbeddingCache(cache_dir=config.cache_dir, enabled=config.cache_enabled)

    def get_embedding(self, text: str) -> npt.NDArray[np.float32]:
        """Get embedding for text (cached or computed).

        Args:
            text: Input text to embed

        Returns:
            Embedding vector (384-dimensional for all-MiniLM-L6-v2)

        Raises:
            TextTooShortError: If text is too short (<3 characters)
            TextTooLongError: If text exceeds max_length
            ModelLoadError: If model fails to load
        """
        # Validate text length
        text = text.strip()
        if len(text) < 3:
            raise TextTooShortError(len(text), min_length=3)

        if len(text) > self.config.max_length:
            raise TextTooLongError(len(text), self.config.max_length)

        # Check cache first
        cached = self.cache.get(text, self.config.model_name)
        if cached is not None:
            return cached

        # Ensure model is loaded
        if not self.model_loaded:
            self.load_model()

        # Compute embedding
        assert self.model is not None  # Type narrowing
        embedding: npt.NDArray[np.float32] = self.model.encode(
            text, convert_to_numpy=True, show_progress_bar=False
        )

        # Cache for future use
        self.cache.set(text, self.config.model_name, embedding)

        return embedding

    def load_model(self) -> None:
        """Load embedding model with retry logic.

        Raises:
            ModelLoadError: If model fails to load after 3 attempts
        """
        if self.model_loaded and self.model is not None:
            return

        self.model = self._retry_download(attempts=3)
        self.model_loaded = True

    def _retry_download(self, attempts: int = 3) -> SentenceTransformer:
        """Retry model download with exponential backoff.

        Args:
            attempts: Number of retry attempts (default: 3)

        Returns:
            Loaded SentenceTransformer model

        Raises:
            ModelLoadError: If all retry attempts fail
        """
        last_error: Optional[Exception] = None

        for attempt in range(1, attempts + 1):
            try:
                model = SentenceTransformer(self.config.model_name)
                return model
            except Exception as e:
                last_error = e
                if attempt < attempts:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** (attempt - 1)
                    time.sleep(wait_time)

        # All attempts failed
        raise ModelLoadError(self.config.model_name, attempts) from last_error
