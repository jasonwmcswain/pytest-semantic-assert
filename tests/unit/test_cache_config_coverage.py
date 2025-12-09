"""Additional tests to achieve 100% coverage for cache.py and config.py."""

import importlib
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest


class TestCacheModuleImports:
    """Test cache module imports and class definition."""

    def test_import_cache_module(self) -> None:
        """Test importing cache module to cover import statements."""
        if "pytest_semantic_assert.cache" in sys.modules:
            module = importlib.reload(sys.modules["pytest_semantic_assert.cache"])
        else:
            import pytest_semantic_assert.cache as module

        assert "pytest_semantic_assert.cache" in sys.modules
        assert module is not None

    def test_cache_imports_hashlib(self) -> None:
        """Test that hashlib is imported."""
        from pytest_semantic_assert import cache

        assert hasattr(cache, "hashlib")

    def test_cache_imports_pickle(self) -> None:
        """Test that pickle is imported."""
        from pytest_semantic_assert import cache

        assert hasattr(cache, "pickle")

    def test_cache_imports_path(self) -> None:
        """Test that Path is imported."""
        from pytest_semantic_assert import cache

        assert hasattr(cache, "Path")

    def test_cache_imports_typing(self) -> None:
        """Test that Optional is imported."""
        from pytest_semantic_assert import cache

        assert hasattr(cache, "Optional")

    def test_cache_imports_numpy(self) -> None:
        """Test that numpy imports are present."""
        from pytest_semantic_assert import cache

        assert hasattr(cache, "np")
        assert hasattr(cache, "npt")

    def test_cache_imports_filelock(self) -> None:
        """Test that FileLock and Timeout are imported."""
        from pytest_semantic_assert import cache

        assert hasattr(cache, "FileLock")
        assert hasattr(cache, "Timeout")

    def test_embedding_cache_class_definition(self) -> None:
        """Test EmbeddingCache class definition."""
        from pytest_semantic_assert.cache import EmbeddingCache

        assert EmbeddingCache.__name__ == "EmbeddingCache"
        assert EmbeddingCache.__doc__ is not None
        assert "File-based or in-memory cache" in EmbeddingCache.__doc__


class TestCacheMethodSignatures:
    """Test that all cache method signatures are covered."""

    def test_cache_key_method_signature(self, tmp_path: Path) -> None:
        """Test _cache_key method signature and execution."""
        from pytest_semantic_assert.cache import EmbeddingCache

        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=True)

        # Call the method to cover its signature line
        key = cache._cache_key("test text", "model-name")

        assert isinstance(key, str)
        assert len(key) == 16

    def test_get_method_signature(self, tmp_path: Path) -> None:
        """Test get method signature and execution."""
        from pytest_semantic_assert.cache import EmbeddingCache

        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=True)

        # Call the method to cover its signature line
        result = cache.get("nonexistent", "model")

        assert result is None

    def test_set_method_signature(self, tmp_path: Path) -> None:
        """Test set method signature and execution."""
        from pytest_semantic_assert.cache import EmbeddingCache

        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=True)
        embedding = np.array([1.0, 2.0, 3.0], dtype=np.float32)

        # Call the method to cover its signature line
        cache.set("test", "model", embedding)

        # Verify it was stored
        result = cache.get("test", "model")
        assert result is not None

    def test_lock_and_write_method_signature(self, tmp_path: Path) -> None:
        """Test _lock_and_write method signature and execution."""
        from pytest_semantic_assert.cache import EmbeddingCache

        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=True)
        embedding = np.array([1.0, 2.0, 3.0], dtype=np.float32)

        key = cache._cache_key("test", "model")

        # Call the method directly to cover its signature line
        cache._lock_and_write(key, embedding)

        # Verify file was created
        cache_file = tmp_path / f"{key}.pkl"
        assert cache_file.exists()


class TestCacheEdgeCases:
    """Test edge cases to improve cache.py coverage."""

    def test_lock_and_write_with_none_cache_dir(self) -> None:
        """Test _lock_and_write early return when cache_dir is None."""
        from pytest_semantic_assert.cache import EmbeddingCache

        # Create cache in memory mode (cache_dir will be None)
        cache = EmbeddingCache(cache_dir="memory", enabled=True)
        embedding = np.array([1.0, 2.0, 3.0], dtype=np.float32)

        # This should return early because cache_dir is None
        key = cache._cache_key("test", "model")
        cache._lock_and_write(key, embedding)

        # Verify cache_dir is None
        assert cache.cache_dir is None
        assert cache.lock_file is None

    def test_lock_and_write_with_existing_file(self, tmp_path: Path) -> None:
        """Test _lock_and_write early return when file already exists."""
        from pytest_semantic_assert.cache import EmbeddingCache

        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=True)
        embedding = np.array([1.0, 2.0, 3.0], dtype=np.float32)

        # Write once
        key = cache._cache_key("test", "model")
        cache._lock_and_write(key, embedding)

        # Mock to track if pickle.dump is called again
        with patch("pytest_semantic_assert.cache.pickle.dump") as mock_dump:
            # Write again - should return early due to double-check pattern
            cache._lock_and_write(key, embedding)

            # pickle.dump should not be called (file already exists)
            assert mock_dump.call_count == 0

    def test_cache_disabled_set_returns_early(self, tmp_path: Path) -> None:
        """Test that set returns early when cache is disabled."""
        from pytest_semantic_assert.cache import EmbeddingCache

        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=False)
        embedding = np.array([1.0, 2.0, 3.0], dtype=np.float32)

        # This should return early
        cache.set("test", "model", embedding)

        # Verify nothing was cached
        result = cache.get("test", "model")
        assert result is None

    def test_cache_disabled_get_returns_none(self, tmp_path: Path) -> None:
        """Test that get returns None when cache is disabled."""
        from pytest_semantic_assert.cache import EmbeddingCache

        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=False)

        result = cache.get("test", "model")
        assert result is None


class TestConfigModuleImports:
    """Test config module imports and class definition."""

    def test_import_config_module(self) -> None:
        """Test importing config module to cover import statements."""
        if "pytest_semantic_assert.config" in sys.modules:
            module = importlib.reload(sys.modules["pytest_semantic_assert.config"])
        else:
            import pytest_semantic_assert.config as module

        assert "pytest_semantic_assert.config" in sys.modules
        assert module is not None

    def test_config_imports_dataclass(self) -> None:
        """Test that dataclass is imported."""
        from pytest_semantic_assert import config

        assert hasattr(config, "dataclass")

    def test_config_imports_pytest(self) -> None:
        """Test that pytest is imported."""
        from pytest_semantic_assert import config

        assert hasattr(config, "pytest")

    def test_configuration_class_definition(self) -> None:
        """Test Configuration class definition."""
        from pytest_semantic_assert.config import Configuration

        assert Configuration.__name__ == "Configuration"
        assert Configuration.__doc__ is not None

    def test_configuration_is_dataclass(self) -> None:
        """Test that Configuration is a dataclass."""
        from dataclasses import is_dataclass

        from pytest_semantic_assert.config import Configuration

        assert is_dataclass(Configuration)

    def test_configuration_default_fields(self) -> None:
        """Test Configuration default field values."""
        from pytest_semantic_assert.config import Configuration

        config = Configuration()

        # Verify all default fields
        assert config.threshold == 0.85
        assert config.model_name == "all-MiniLM-L6-v2"
        assert config.cache_enabled is True
        assert config.cache_dir == ".pytest-semantic-cache/"
        assert config.max_length == 10000


class TestConfigValidateMethod:
    """Test Configuration.validate() method coverage."""

    def test_validate_method_signature(self) -> None:
        """Test validate method signature and execution."""
        from pytest_semantic_assert.config import Configuration

        config = Configuration()

        # Call validate to cover its signature line
        config.validate()  # Should not raise

    def test_validate_with_valid_config(self) -> None:
        """Test validate passes with valid configuration."""
        from pytest_semantic_assert.config import Configuration

        config = Configuration(threshold=0.75, model_name="test-model", max_length=5000)

        # Should not raise
        config.validate()

    def test_validate_catches_all_error_conditions(self) -> None:
        """Test that validate method checks all conditions."""
        from pytest_semantic_assert.config import Configuration

        # Test threshold validation
        config1 = Configuration(threshold=1.5)
        with pytest.raises(ValueError, match="threshold must be between"):
            config1.validate()

        # Test model_name validation
        config2 = Configuration(model_name="")
        with pytest.raises(ValueError, match="model_name must be"):
            config2.validate()

        # Test max_length validation
        config3 = Configuration(max_length=-1)
        with pytest.raises(ValueError, match="max_length must be positive"):
            config3.validate()


class TestConfigFromPytestConfig:
    """Test Configuration.from_pytest_config() method coverage."""

    def test_from_pytest_config_method_signature(self, pytestconfig: pytest.Config) -> None:
        """Test from_pytest_config method signature and execution."""
        from pytest_semantic_assert.config import Configuration

        # Call the method to cover its signature line
        config = Configuration.from_pytest_config(pytestconfig)

        assert isinstance(config, Configuration)

    def test_from_pytest_config_with_all_defaults(self) -> None:
        """Test from_pytest_config with all default values."""

        class MockConfig:
            def getini(self, name: str) -> str:
                # Return empty strings to trigger defaults
                # Empty string for cache is treated as false, so return "true"
                if name == "semantic_assert_cache":
                    return "true"
                return ""

        from pytest_semantic_assert.config import Configuration

        config = Configuration.from_pytest_config(MockConfig())  # type: ignore

        # Should use all defaults
        assert config.threshold == 0.85
        assert config.model_name == "all-MiniLM-L6-v2"
        assert config.cache_enabled is True
        assert config.cache_dir == ".pytest-semantic-cache/"
        assert config.max_length == 10000


class TestCacheModuleDocstring:
    """Test cache module docstring."""

    def test_cache_module_docstring(self) -> None:
        """Test cache module has docstring."""
        import pytest_semantic_assert.cache as cache_module

        assert cache_module.__doc__ is not None
        assert "Embedding cache" in cache_module.__doc__


class TestConfigModuleDocstring:
    """Test config module docstring."""

    def test_config_module_docstring(self) -> None:
        """Test config module has docstring."""
        import pytest_semantic_assert.config as config_module

        assert config_module.__doc__ is not None
        assert "Configuration management" in config_module.__doc__
