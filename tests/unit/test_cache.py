"""Unit tests for embedding cache."""

import tempfile
from pathlib import Path

import numpy as np
from pytest_semantic_assert.cache import EmbeddingCache


class TestEmbeddingCache:
    """Test EmbeddingCache class."""

    def test_cache_disabled(self) -> None:
        """Test that disabled cache always returns None."""
        cache = EmbeddingCache(cache_dir="memory", enabled=False)

        # Store an embedding
        embedding = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        cache.set("test text", "model-name", embedding)

        # Should return None because cache is disabled
        result = cache.get("test text", "model-name")
        assert result is None

    def test_memory_mode_set_and_get(self) -> None:
        """Test cache set and get in memory mode."""
        cache = EmbeddingCache(cache_dir="memory", enabled=True)

        embedding = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        cache.set("test text", "model-name", embedding)

        result = cache.get("test text", "model-name")
        assert result is not None
        np.testing.assert_array_equal(result, embedding)

    def test_memory_mode_cache_miss(self) -> None:
        """Test that memory cache returns None for missing keys."""
        cache = EmbeddingCache(cache_dir="memory", enabled=True)

        result = cache.get("nonexistent text", "model-name")
        assert result is None

    def test_memory_mode_different_model_names(self) -> None:
        """Test that different model names have separate cache entries."""
        cache = EmbeddingCache(cache_dir="memory", enabled=True)

        embedding1 = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        embedding2 = np.array([4.0, 5.0, 6.0], dtype=np.float32)

        cache.set("same text", "model-1", embedding1)
        cache.set("same text", "model-2", embedding2)

        result1 = cache.get("same text", "model-1")
        result2 = cache.get("same text", "model-2")

        assert result1 is not None
        assert result2 is not None
        np.testing.assert_array_equal(result1, embedding1)
        np.testing.assert_array_equal(result2, embedding2)

    def test_file_mode_set_and_get(self) -> None:
        """Test cache set and get in file mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = EmbeddingCache(cache_dir=tmpdir, enabled=True)

            embedding = np.array([1.0, 2.0, 3.0], dtype=np.float32)
            cache.set("test text", "model-name", embedding)

            result = cache.get("test text", "model-name")
            assert result is not None
            np.testing.assert_array_equal(result, embedding)

    def test_file_mode_cache_miss(self) -> None:
        """Test that file cache returns None for missing keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = EmbeddingCache(cache_dir=tmpdir, enabled=True)

            result = cache.get("nonexistent text", "model-name")
            assert result is None

    def test_file_mode_persistence(self) -> None:
        """Test that file cache persists across cache instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create cache and store embedding
            cache1 = EmbeddingCache(cache_dir=tmpdir, enabled=True)
            embedding = np.array([1.0, 2.0, 3.0], dtype=np.float32)
            cache1.set("test text", "model-name", embedding)

            # Create new cache instance and retrieve
            cache2 = EmbeddingCache(cache_dir=tmpdir, enabled=True)
            result = cache2.get("test text", "model-name")

            assert result is not None
            np.testing.assert_array_equal(result, embedding)

    def test_cache_key_generation(self) -> None:
        """Test that cache key is deterministic."""
        cache = EmbeddingCache(cache_dir="memory", enabled=True)

        key1 = cache._cache_key("test text", "model-name")
        key2 = cache._cache_key("test text", "model-name")

        assert key1 == key2
        assert len(key1) == 16  # First 16 chars of SHA256 hash

    def test_cache_key_different_for_different_texts(self) -> None:
        """Test that different texts produce different cache keys."""
        cache = EmbeddingCache(cache_dir="memory", enabled=True)

        key1 = cache._cache_key("text one", "model-name")
        key2 = cache._cache_key("text two", "model-name")

        assert key1 != key2

    def test_cache_key_different_for_different_models(self) -> None:
        """Test that different models produce different cache keys."""
        cache = EmbeddingCache(cache_dir="memory", enabled=True)

        key1 = cache._cache_key("same text", "model-1")
        key2 = cache._cache_key("same text", "model-2")

        assert key1 != key2

    def test_cache_directory_created(self) -> None:
        """Test that cache directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "subdir" / "cache"
            cache = EmbeddingCache(cache_dir=str(cache_path), enabled=True)

            # Trigger directory creation by setting a value
            embedding = np.array([1.0, 2.0, 3.0], dtype=np.float32)
            cache.set("test", "model", embedding)

            assert cache_path.exists()
            assert cache_path.is_dir()

    def test_corrupted_cache_file_handled_gracefully(self) -> None:
        """Test that corrupted cache files are handled gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = EmbeddingCache(cache_dir=tmpdir, enabled=True)

            # Write corrupted file
            cache_dir = Path(tmpdir)
            key = cache._cache_key("test", "model")
            cache_file = cache_dir / f"{key}.pkl"
            cache_file.write_text("corrupted data")

            # Should return None and not crash
            result = cache.get("test", "model")
            assert result is None

    def test_high_dimensional_embedding(self) -> None:
        """Test caching high-dimensional embeddings (384-dim like all-MiniLM-L6-v2)."""
        cache = EmbeddingCache(cache_dir="memory", enabled=True)

        # 384-dimensional embedding
        embedding = np.random.rand(384).astype(np.float32)
        cache.set("test text", "model-name", embedding)

        result = cache.get("test text", "model-name")
        assert result is not None
        np.testing.assert_array_equal(result, embedding)
        assert result.shape == (384,)

    def test_multiple_embeddings_in_memory(self) -> None:
        """Test storing multiple embeddings in memory cache."""
        cache = EmbeddingCache(cache_dir="memory", enabled=True)

        embeddings = {
            "text1": np.array([1.0, 2.0, 3.0], dtype=np.float32),
            "text2": np.array([4.0, 5.0, 6.0], dtype=np.float32),
            "text3": np.array([7.0, 8.0, 9.0], dtype=np.float32),
        }

        # Store all
        for text, embedding in embeddings.items():
            cache.set(text, "model", embedding)

        # Retrieve all
        for text, expected in embeddings.items():
            result = cache.get(text, "model")
            assert result is not None
            np.testing.assert_array_equal(result, expected)

    def test_lock_timeout_handling(self, tmp_path: Path) -> None:
        """Test that lock timeout is handled gracefully."""
        from unittest.mock import patch

        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=True)
        embedding = np.array([1.0, 2.0, 3.0], dtype=np.float32)

        # Mock FileLock to raise Timeout
        with patch("pytest_semantic_assert.cache.FileLock") as mock_lock:
            from filelock import Timeout

            mock_lock.return_value.__enter__.side_effect = Timeout("test_lock")

            # Should handle timeout gracefully (no exception)
            cache.set("test", "model", embedding)

    def test_general_exception_handling_in_lock_and_write(self, tmp_path: Path) -> None:
        """Test that general exceptions in _lock_and_write are handled gracefully."""
        from unittest.mock import patch

        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=True)
        embedding = np.array([1.0, 2.0, 3.0], dtype=np.float32)

        # Mock FileLock to raise a general exception
        with patch("pytest_semantic_assert.cache.FileLock") as mock_lock:
            mock_lock.return_value.__enter__.side_effect = RuntimeError("Unexpected error")

            # Should handle exception gracefully (no exception propagated)
            cache.set("test", "model", embedding)
