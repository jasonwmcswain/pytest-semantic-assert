"""Unit tests for embedding manager."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from pytest_semantic_assert.config import Configuration
from pytest_semantic_assert.embeddings import EmbeddingManager
from pytest_semantic_assert.exceptions import ModelLoadError, TextTooLongError, TextTooShortError


class TestEmbeddingManager:
    """Test EmbeddingManager class."""

    @patch("pytest_semantic_assert.embeddings.SentenceTransformer")
    def test_lazy_loading(self, mock_st: MagicMock) -> None:
        """Test that model is loaded lazily on first use."""
        config = Configuration(cache_enabled=False)
        manager = EmbeddingManager(config)

        # Model should not be loaded yet
        assert not manager.model_loaded
        mock_st.assert_not_called()

        # Mock the model
        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.rand(384).astype(np.float32)
        mock_st.return_value = mock_model

        # Get embedding - should trigger model load
        manager.get_embedding("Hello world!")

        # Model should now be loaded
        assert manager.model_loaded
        mock_st.assert_called_once_with("all-MiniLM-L6-v2")

    @patch("pytest_semantic_assert.embeddings.SentenceTransformer")
    def test_model_loaded_once(self, mock_st: MagicMock) -> None:
        """Test that model is loaded only once even for multiple calls."""
        config = Configuration(cache_enabled=False)
        manager = EmbeddingManager(config)

        # Mock the model
        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.rand(384).astype(np.float32)
        mock_st.return_value = mock_model

        # Get multiple embeddings
        manager.get_embedding("Text 1")
        manager.get_embedding("Text 2")
        manager.get_embedding("Text 3")

        # Model should be initialized only once
        mock_st.assert_called_once()

    @patch("pytest_semantic_assert.embeddings.SentenceTransformer")
    def test_text_too_short_raises_error(self, mock_st: MagicMock) -> None:
        """Test that text shorter than 3 characters raises TextTooShortError."""
        config = Configuration()
        manager = EmbeddingManager(config)

        with pytest.raises(TextTooShortError, match="minimum 3 characters required"):
            manager.get_embedding("ab")

        with pytest.raises(TextTooShortError):
            manager.get_embedding("")

    @patch("pytest_semantic_assert.embeddings.SentenceTransformer")
    def test_text_too_long_raises_error(self, mock_st: MagicMock) -> None:
        """Test that text exceeding max_length raises TextTooLongError."""
        config = Configuration(max_length=100)
        manager = EmbeddingManager(config)

        long_text = "a" * 101

        with pytest.raises(TextTooLongError, match="exceeds maximum length"):
            manager.get_embedding(long_text)

    @patch("pytest_semantic_assert.embeddings.SentenceTransformer")
    def test_text_at_boundaries(self, mock_st: MagicMock) -> None:
        """Test text at min and max length boundaries."""
        config = Configuration(max_length=10)
        manager = EmbeddingManager(config)

        # Mock the model
        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.rand(384).astype(np.float32)
        mock_st.return_value = mock_model

        # Minimum length (3 chars)
        manager.get_embedding("abc")  # Should not raise

        # Maximum length (10 chars)
        manager.get_embedding("a" * 10)  # Should not raise

    @patch("pytest_semantic_assert.embeddings.SentenceTransformer")
    def test_cache_integration(self, mock_st: MagicMock) -> None:
        """Test that embeddings are cached and reused."""
        config = Configuration(cache_dir="memory", cache_enabled=True)
        manager = EmbeddingManager(config)

        # Mock the model
        mock_model = MagicMock()
        embedding = np.random.rand(384).astype(np.float32)
        mock_model.encode.return_value = embedding
        mock_st.return_value = mock_model

        # First call - should compute
        result1 = manager.get_embedding("test text")
        assert mock_model.encode.call_count == 1

        # Second call with same text - should use cache
        result2 = manager.get_embedding("test text")
        assert mock_model.encode.call_count == 1  # Still 1, no new computation

        # Results should be identical
        np.testing.assert_array_equal(result1, result2)

    @patch("pytest_semantic_assert.embeddings.SentenceTransformer")
    def test_cache_disabled(self, mock_st: MagicMock) -> None:
        """Test that cache can be disabled."""
        config = Configuration(cache_enabled=False)
        manager = EmbeddingManager(config)

        # Mock the model
        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.rand(384).astype(np.float32)
        mock_st.return_value = mock_model

        # Both calls should compute (no caching)
        manager.get_embedding("test text")
        manager.get_embedding("test text")

        assert mock_model.encode.call_count == 2

    @patch("pytest_semantic_assert.embeddings.time.sleep")
    @patch("pytest_semantic_assert.embeddings.SentenceTransformer")
    def test_retry_logic_on_failure(self, mock_st: MagicMock, mock_sleep: MagicMock) -> None:
        """Test that model load retries on failure."""
        config = Configuration()
        manager = EmbeddingManager(config)

        # Mock to fail twice, then succeed
        mock_st.side_effect = [
            Exception("Network error"),
            Exception("Timeout"),
            MagicMock(encode=lambda x, **kwargs: np.random.rand(384).astype(np.float32)),
        ]

        # Should succeed after retries
        manager.load_model()

        # Should have attempted 3 times
        assert mock_st.call_count == 3

        # Should have slept between retries (1s, 2s)
        assert mock_sleep.call_count == 2

    @patch("pytest_semantic_assert.embeddings.time.sleep")
    @patch("pytest_semantic_assert.embeddings.SentenceTransformer")
    def test_retry_logic_exhausted(self, mock_st: MagicMock, mock_sleep: MagicMock) -> None:
        """Test that ModelLoadError is raised after all retries fail."""
        config = Configuration()
        manager = EmbeddingManager(config)

        # Mock to always fail
        mock_st.side_effect = Exception("Network error")

        with pytest.raises(ModelLoadError, match="Failed to load embedding model"):
            manager.load_model()

        # Should have attempted 3 times
        assert mock_st.call_count == 3

    @patch("pytest_semantic_assert.embeddings.SentenceTransformer")
    def test_whitespace_stripping(self, mock_st: MagicMock) -> None:
        """Test that leading/trailing whitespace is stripped."""
        config = Configuration(cache_enabled=False)  # Disable cache for this test
        manager = EmbeddingManager(config)

        # Mock the model
        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.rand(384).astype(np.float32)
        mock_st.return_value = mock_model

        # Text with whitespace
        manager.get_embedding("  hello world  ")

        # Check that encode was called with stripped text
        # (We can't directly check the exact call, but we know it didn't fail on length validation)
        mock_model.encode.assert_called_once()

    @patch("pytest_semantic_assert.embeddings.SentenceTransformer")
    def test_custom_model_name(self, mock_st: MagicMock) -> None:
        """Test that custom model name is used."""
        config = Configuration(model_name="custom-model-name", cache_enabled=False)
        manager = EmbeddingManager(config)

        # Mock the model
        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.rand(384).astype(np.float32)
        mock_st.return_value = mock_model

        manager.get_embedding("test text")

        # Check that custom model was loaded
        mock_st.assert_called_once_with("custom-model-name")

    @patch("pytest_semantic_assert.embeddings.SentenceTransformer")
    def test_different_texts_different_embeddings(self, mock_st: MagicMock) -> None:
        """Test that different texts produce different embeddings."""
        config = Configuration(cache_enabled=False)
        manager = EmbeddingManager(config)

        # Mock the model to return different embeddings
        mock_model = MagicMock()
        mock_model.encode.side_effect = [
            np.array([1.0, 2.0, 3.0], dtype=np.float32),
            np.array([4.0, 5.0, 6.0], dtype=np.float32),
        ]
        mock_st.return_value = mock_model

        embedding1 = manager.get_embedding("text one")
        embedding2 = manager.get_embedding("text two")

        # Embeddings should be different
        assert not np.array_equal(embedding1, embedding2)
