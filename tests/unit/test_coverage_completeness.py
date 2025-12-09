"""Tests to ensure complete coverage of all modules and imports."""

from pathlib import Path

import numpy as np
import pytest


class TestImportCoverage:
    """Test that all imports are covered."""

    def test_import_all_modules(self) -> None:
        """Test importing all modules to cover import statements."""
        # Import main package

        # Import all submodules explicitly
        from pytest_semantic_assert import (
            assertions,
            cache,
            config,
            embeddings,
            exceptions,
            plugin,
            similarity,
        )

        # Verify all modules are imported
        assert assertions is not None
        assert cache is not None
        assert config is not None
        assert embeddings is not None
        assert exceptions is not None
        assert plugin is not None
        assert similarity is not None

    def test_import_all_exceptions(self) -> None:
        """Test importing all exception classes."""
        from pytest_semantic_assert.exceptions import (
            ModelLoadError,
            TextTooLongError,
            TextTooShortError,
        )

        # Verify exceptions are importable
        assert TextTooShortError is not None
        assert TextTooLongError is not None
        assert ModelLoadError is not None

    def test_import_all_functions(self) -> None:
        """Test importing all public functions."""
        from pytest_semantic_assert import (
            assert_semantically_similar,
            assert_semantically_similar_to_any,
        )
        from pytest_semantic_assert.similarity import cosine_similarity

        assert assert_semantically_similar is not None
        assert assert_semantically_similar_to_any is not None
        assert cosine_similarity is not None

    def test_import_all_classes(self) -> None:
        """Test importing all classes."""
        from pytest_semantic_assert.cache import EmbeddingCache
        from pytest_semantic_assert.config import Configuration
        from pytest_semantic_assert.embeddings import EmbeddingManager

        assert EmbeddingCache is not None
        assert Configuration is not None
        assert EmbeddingManager is not None


class TestExceptionInstantiation:
    """Test that all exception classes can be instantiated."""

    def test_text_too_short_error_instantiation(self) -> None:
        """Test TextTooShortError can be instantiated."""
        from pytest_semantic_assert.exceptions import TextTooShortError

        # Test with defaults
        error1 = TextTooShortError(2)
        assert isinstance(error1, ValueError)
        assert error1.text_length == 2
        assert error1.min_length == 3

        # Test with custom min_length
        error2 = TextTooShortError(5, min_length=10)
        assert error2.text_length == 5
        assert error2.min_length == 10

        # Test string representation
        assert "minimum" in str(error1)
        assert "3 characters" in str(error1)

    def test_text_too_long_error_instantiation(self) -> None:
        """Test TextTooLongError can be instantiated."""
        from pytest_semantic_assert.exceptions import TextTooLongError

        error = TextTooLongError(15000, 10000)
        assert isinstance(error, ValueError)
        assert error.text_length == 15000
        assert error.max_length == 10000

        # Test string representation
        assert "exceeds maximum length" in str(error)
        assert "15000" in str(error)
        assert "10000" in str(error)

    def test_model_load_error_instantiation(self) -> None:
        """Test ModelLoadError can be instantiated."""
        from pytest_semantic_assert.exceptions import ModelLoadError

        # Test with defaults
        error1 = ModelLoadError("test-model")
        assert isinstance(error1, RuntimeError)
        assert error1.model_name == "test-model"
        assert error1.attempts == 3

        # Test with custom attempts
        error2 = ModelLoadError("custom-model", attempts=5)
        assert error2.model_name == "custom-model"
        assert error2.attempts == 5

        # Test string representation includes troubleshooting
        message = str(error1)
        assert "Failed to load" in message
        assert "test-model" in message
        assert "Troubleshooting:" in message
        assert "network connectivity" in message


class TestPluginHooksCoverage:
    """Test plugin hooks to ensure coverage."""

    def test_pytest_addoption_coverage(self) -> None:
        """Test pytest_addoption to cover import lines."""
        from pytest_semantic_assert import plugin

        # Create a mock parser
        class MockParser:
            def __init__(self) -> None:
                self.options: list = []

            def addini(self, name: str, **kwargs: object) -> None:
                self.options.append(name)

        parser = MockParser()
        plugin.pytest_addoption(parser)  # type: ignore

        # Verify options were added
        assert len(parser.options) >= 5

    def test_pytest_configure_coverage(self, pytestconfig: pytest.Config) -> None:
        """Test pytest_configure to cover import lines."""
        from pytest_semantic_assert import plugin

        # Reset global state
        plugin._config = None

        # Call configure
        plugin.pytest_configure(pytestconfig)

        # Verify config was created
        assert plugin._config is not None


class TestSimilarityFunctionCoverage:
    """Test similarity function to ensure full coverage."""

    def test_cosine_similarity_imports(self) -> None:
        """Test cosine_similarity to cover import lines."""
        from pytest_semantic_assert.similarity import cosine_similarity

        vec1 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        vec2 = np.array([1.0, 0.0, 0.0], dtype=np.float32)

        result = cosine_similarity(vec1, vec2)
        assert result == 1.0

    def test_cosine_similarity_with_negative_values(self) -> None:
        """Test cosine similarity with negative values (edge case for clamping)."""
        from pytest_semantic_assert.similarity import cosine_similarity

        # Vectors pointing in opposite directions
        vec1 = np.array([1.0, 0.0], dtype=np.float32)
        vec2 = np.array([-1.0, 0.0], dtype=np.float32)

        result = cosine_similarity(vec1, vec2)
        # Should be clamped to 0.0 (negative similarity becomes 0)
        assert result == 0.0


class TestCacheInternalMethods:
    """Test cache internal methods for coverage."""

    def test_cache_key_method(self, tmp_path: Path) -> None:
        """Test _cache_key method directly."""
        from pytest_semantic_assert.cache import EmbeddingCache

        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=True)

        key1 = cache._cache_key("test text", "model")
        key2 = cache._cache_key("test text", "model")

        assert key1 == key2
        assert isinstance(key1, str)
        assert len(key1) == 16

    def test_lock_and_write_method(self, tmp_path: Path) -> None:
        """Test _lock_and_write method directly."""
        from pytest_semantic_assert.cache import EmbeddingCache

        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=True)
        embedding = np.array([1.0, 2.0, 3.0], dtype=np.float32)

        key = cache._cache_key("test", "model")
        cache._lock_and_write(key, embedding)

        # Verify file was created
        cache_file = tmp_path / f"{key}.pkl"
        assert cache_file.exists()


class TestConfigurationEdgeCases:
    """Test configuration edge cases for coverage."""

    def test_config_with_boolean_cache_enabled(self) -> None:
        """Test from_pytest_config with boolean cache_enabled."""

        class MockConfig:
            def getini(self, name: str) -> object:
                if name == "semantic_assert_cache":
                    return True  # Boolean instead of string
                return {
                    "semantic_assert_threshold": "0.85",
                    "semantic_assert_model": "all-MiniLM-L6-v2",
                    "semantic_assert_cache_dir": ".cache/",
                    "semantic_assert_max_length": "10000",
                }.get(name, "")

        from pytest_semantic_assert.config import Configuration

        config = Configuration.from_pytest_config(MockConfig())  # type: ignore
        assert config.cache_enabled is True

    def test_config_with_non_boolean_non_string_cache(self) -> None:
        """Test from_pytest_config with non-boolean, non-string cache value."""

        class MockConfig:
            def getini(self, name: str) -> object:
                if name == "semantic_assert_cache":
                    return 123  # Not a boolean or string
                return {
                    "semantic_assert_threshold": "0.85",
                    "semantic_assert_model": "all-MiniLM-L6-v2",
                    "semantic_assert_cache_dir": ".cache/",
                    "semantic_assert_max_length": "10000",
                }.get(name, "")

        from pytest_semantic_assert.config import Configuration

        config = Configuration.from_pytest_config(MockConfig())  # type: ignore
        # Should default to True
        assert config.cache_enabled is True


class TestEmbeddingsManagerCoverage:
    """Test embeddings manager for coverage."""

    def test_load_model_when_already_loaded(self) -> None:
        """Test load_model when model is already loaded."""
        from pytest_semantic_assert.config import Configuration
        from pytest_semantic_assert.embeddings import EmbeddingManager

        config = Configuration()
        manager = EmbeddingManager(config)

        # Load model
        manager.load_model()
        assert manager.model_loaded is True

        # Load again - should return early
        manager.load_model()
        assert manager.model_loaded is True


class TestAssertionsFunctionCoverage:
    """Test assertions functions for complete coverage."""

    def test_assert_semantically_similar_with_none_threshold(self) -> None:
        """Test with None threshold to use config default."""
        from pytest_semantic_assert import assert_semantically_similar

        # Should use default threshold from config
        assert_semantically_similar("Hello world", "Hello world")

    def test_assert_semantically_similar_to_any_with_none_threshold(self) -> None:
        """Test assert_semantically_similar_to_any with None threshold."""
        from pytest_semantic_assert import assert_semantically_similar_to_any

        # Should use default threshold from config
        assert_semantically_similar_to_any("Hello world", ["Hello world", "Hi there"])
