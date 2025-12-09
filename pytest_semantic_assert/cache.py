"""Embedding cache with file-based locking for parallel execution."""

import hashlib
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
import numpy.typing as npt
from filelock import FileLock, Timeout


class EmbeddingCache:
    """File-based or in-memory cache for embeddings with locking."""

    def __init__(self, cache_dir: str, enabled: bool = True) -> None:
        """Initialize embedding cache.

        Args:
            cache_dir: Directory path for cache storage or "memory" for in-memory mode
            enabled: Whether caching is enabled (default: True)
        """
        self.enabled = enabled
        self.cache_dir_str = cache_dir
        self.is_memory_mode = cache_dir.lower() == "memory"

        if self.is_memory_mode:
            self.memory_cache: dict[str, npt.NDArray[np.float32]] = {}
            self.cache_dir: Optional[Path] = None
            self.lock_file: Optional[Path] = None
        else:
            self.memory_cache = {}
            self.cache_dir = Path(cache_dir)
            self.lock_file = self.cache_dir / ".lock"

            # Create cache directory if it doesn't exist
            if self.enabled:
                self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, text: str, model_name: str) -> str:
        """Generate cache key from text and model name.

        Args:
            text: Input text
            model_name: Name of the embedding model

        Returns:
            Hash-based cache key (first 16 characters of SHA256 hash)
        """
        # Combine text and model name to ensure different models have separate caches
        combined = f"{text}::{model_name}"
        hash_obj = hashlib.sha256(combined.encode("utf-8"))
        return hash_obj.hexdigest()[:16]

    def get(self, text: str, model_name: str) -> Optional[npt.NDArray[np.float32]]:
        """Retrieve cached embedding if available.

        Args:
            text: Input text
            model_name: Name of the embedding model

        Returns:
            Cached embedding array or None if not found
        """
        if not self.enabled:
            return None

        key = self._cache_key(text, model_name)

        # Memory mode: simple dict lookup
        if self.is_memory_mode:
            return self.memory_cache.get(key)

        # File mode: load from disk
        cache_file = self.cache_dir / f"{key}.pkl"  # type: ignore
        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    embedding: npt.NDArray[np.float32] = pickle.load(f)
                    return embedding
            except Exception:
                # If cache file is corrupted, ignore and recompute
                return None

        return None

    def set(self, text: str, model_name: str, embedding: npt.NDArray[np.float32]) -> None:
        """Store embedding in cache.

        Args:
            text: Input text
            model_name: Name of the embedding model
            embedding: Embedding vector to cache
        """
        if not self.enabled:
            return

        key = self._cache_key(text, model_name)

        # Memory mode: simple dict storage
        if self.is_memory_mode:
            self.memory_cache[key] = embedding
            return

        # File mode: write to disk with file locking
        self._lock_and_write(key, embedding)

    def _lock_and_write(self, key: str, embedding: npt.NDArray[np.float32]) -> None:
        """Write embedding to disk with file locking.

        Args:
            key: Cache key
            embedding: Embedding vector to cache
        """
        if self.cache_dir is None or self.lock_file is None:
            return

        cache_file = self.cache_dir / f"{key}.pkl"

        # Use file lock to ensure thread/process safety
        lock = FileLock(str(self.lock_file), timeout=5)

        try:
            with lock:
                # Double-check pattern: another worker may have written it
                if cache_file.exists():
                    return

                # Write to temp file, then rename (atomic operation)
                temp_file = cache_file.with_suffix(".tmp")
                with open(temp_file, "wb") as f:
                    pickle.dump(embedding, f)

                temp_file.rename(cache_file)

        except Timeout:
            # Lock timeout - fail gracefully, continue without caching
            # The embedding will be recomputed next time
            pass
        except Exception:
            # Other errors - fail gracefully
            pass
