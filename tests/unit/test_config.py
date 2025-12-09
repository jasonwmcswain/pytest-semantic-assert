"""Unit tests for configuration management."""

import pytest
from pytest_semantic_assert.config import Configuration


class TestConfiguration:
    """Test Configuration class."""

    def test_default_values(self) -> None:
        """Test that default configuration values are correct."""
        config = Configuration()

        assert config.threshold == 0.85
        assert config.model_name == "all-MiniLM-L6-v2"
        assert config.cache_enabled is True
        assert config.cache_dir == ".pytest-semantic-cache/"
        assert config.max_length == 10000

    def test_custom_values(self) -> None:
        """Test creating configuration with custom values."""
        config = Configuration(
            threshold=0.90,
            model_name="custom-model",
            cache_enabled=False,
            cache_dir="/tmp/cache/",
            max_length=5000,
        )

        assert config.threshold == 0.90
        assert config.model_name == "custom-model"
        assert config.cache_enabled is False
        assert config.cache_dir == "/tmp/cache/"
        assert config.max_length == 5000

    def test_validate_valid_config(self) -> None:
        """Test that valid configuration passes validation."""
        config = Configuration(threshold=0.75, max_length=1000)
        config.validate()  # Should not raise

    def test_validate_invalid_threshold_low(self) -> None:
        """Test that threshold below 0.0 fails validation."""
        config = Configuration(threshold=-0.1)

        with pytest.raises(ValueError, match="threshold must be between 0.0 and 1.0"):
            config.validate()

    def test_validate_invalid_threshold_high(self) -> None:
        """Test that threshold above 1.0 fails validation."""
        config = Configuration(threshold=1.5)

        with pytest.raises(ValueError, match="threshold must be between 0.0 and 1.0"):
            config.validate()

    def test_validate_invalid_max_length_zero(self) -> None:
        """Test that max_length of 0 fails validation."""
        config = Configuration(max_length=0)

        with pytest.raises(ValueError, match="max_length must be positive"):
            config.validate()

    def test_validate_invalid_max_length_negative(self) -> None:
        """Test that negative max_length fails validation."""
        config = Configuration(max_length=-100)

        with pytest.raises(ValueError, match="max_length must be positive"):
            config.validate()

    def test_validate_empty_model_name(self) -> None:
        """Test that empty model name fails validation."""
        config = Configuration(model_name="")

        with pytest.raises(ValueError, match="model_name must be a non-empty string"):
            config.validate()

    def test_validate_whitespace_model_name(self) -> None:
        """Test that whitespace-only model name fails validation."""
        config = Configuration(model_name="   ")

        with pytest.raises(ValueError, match="model_name must be a non-empty string"):
            config.validate()

    def test_from_pytest_config_with_defaults(self, pytestconfig: pytest.Config) -> None:
        """Test loading configuration from pytest config with defaults."""
        # Mock pytest config with no ini values set
        config = Configuration.from_pytest_config(pytestconfig)

        assert config.threshold == 0.85
        assert config.model_name == "all-MiniLM-L6-v2"
        assert config.cache_enabled is True
        assert config.cache_dir == ".pytest-semantic-cache/"
        assert config.max_length == 10000

    def test_from_pytest_config_invalid_threshold(self, pytestconfig: pytest.Config) -> None:
        """Test that invalid threshold in pytest config raises UsageError."""
        # This test requires mocking pytest config getini method
        # For now, we'll test the validation logic directly
        pass  # TODO: Add mock-based test if needed

    def test_threshold_boundary_values(self) -> None:
        """Test threshold at boundary values (0.0 and 1.0)."""
        config_low = Configuration(threshold=0.0)
        config_low.validate()  # Should not raise

        config_high = Configuration(threshold=1.0)
        config_high.validate()  # Should not raise

    def test_max_length_boundary_value(self) -> None:
        """Test max_length at boundary value (1)."""
        config = Configuration(max_length=1)
        config.validate()  # Should not raise

    def test_memory_cache_dir(self) -> None:
        """Test that 'memory' cache_dir is accepted."""
        config = Configuration(cache_dir="memory")
        config.validate()  # Should not raise
        assert config.cache_dir == "memory"

    def test_from_pytest_config_with_invalid_threshold_string(self) -> None:
        """Test from_pytest_config with non-numeric threshold string."""

        class MockConfig:
            def getini(self, name: str) -> str:
                if name == "semantic_assert_threshold":
                    return "not_a_number"
                return {
                    "semantic_assert_model": "all-MiniLM-L6-v2",
                    "semantic_assert_cache": "true",
                    "semantic_assert_cache_dir": ".cache/",
                    "semantic_assert_max_length": "10000",
                }.get(name, "")

        with pytest.raises(pytest.UsageError, match="must be a float"):
            Configuration.from_pytest_config(MockConfig())  # type: ignore

    def test_from_pytest_config_with_threshold_out_of_range_high(self) -> None:
        """Test from_pytest_config with threshold > 1.0."""

        class MockConfig:
            def getini(self, name: str) -> str:
                if name == "semantic_assert_threshold":
                    return "1.5"
                return {
                    "semantic_assert_model": "all-MiniLM-L6-v2",
                    "semantic_assert_cache": "true",
                    "semantic_assert_cache_dir": ".cache/",
                    "semantic_assert_max_length": "10000",
                }.get(name, "")

        with pytest.raises(pytest.UsageError, match="must be between 0.0 and 1.0"):
            Configuration.from_pytest_config(MockConfig())  # type: ignore

    def test_from_pytest_config_with_threshold_out_of_range_low(self) -> None:
        """Test from_pytest_config with threshold < 0.0."""

        class MockConfig:
            def getini(self, name: str) -> str:
                if name == "semantic_assert_threshold":
                    return "-0.5"
                return {
                    "semantic_assert_model": "all-MiniLM-L6-v2",
                    "semantic_assert_cache": "true",
                    "semantic_assert_cache_dir": ".cache/",
                    "semantic_assert_max_length": "10000",
                }.get(name, "")

        with pytest.raises(pytest.UsageError, match="must be between 0.0 and 1.0"):
            Configuration.from_pytest_config(MockConfig())  # type: ignore

    def test_from_pytest_config_with_invalid_max_length_string(self) -> None:
        """Test from_pytest_config with non-numeric max_length string."""

        class MockConfig:
            def getini(self, name: str) -> str:
                if name == "semantic_assert_max_length":
                    return "not_a_number"
                return {
                    "semantic_assert_threshold": "0.85",
                    "semantic_assert_model": "all-MiniLM-L6-v2",
                    "semantic_assert_cache": "true",
                    "semantic_assert_cache_dir": ".cache/",
                }.get(name, "")

        with pytest.raises(pytest.UsageError, match="must be an integer"):
            Configuration.from_pytest_config(MockConfig())  # type: ignore

    def test_from_pytest_config_with_zero_max_length(self) -> None:
        """Test from_pytest_config with max_length = 0."""

        class MockConfig:
            def getini(self, name: str) -> str:
                if name == "semantic_assert_max_length":
                    return "0"
                return {
                    "semantic_assert_threshold": "0.85",
                    "semantic_assert_model": "all-MiniLM-L6-v2",
                    "semantic_assert_cache": "true",
                    "semantic_assert_cache_dir": ".cache/",
                }.get(name, "")

        with pytest.raises(pytest.UsageError, match="must be positive"):
            Configuration.from_pytest_config(MockConfig())  # type: ignore

    def test_from_pytest_config_with_negative_max_length(self) -> None:
        """Test from_pytest_config with negative max_length."""

        class MockConfig:
            def getini(self, name: str) -> str:
                if name == "semantic_assert_max_length":
                    return "-100"
                return {
                    "semantic_assert_threshold": "0.85",
                    "semantic_assert_model": "all-MiniLM-L6-v2",
                    "semantic_assert_cache": "true",
                    "semantic_assert_cache_dir": ".cache/",
                }.get(name, "")

        with pytest.raises(pytest.UsageError, match="must be positive"):
            Configuration.from_pytest_config(MockConfig())  # type: ignore

    def test_from_pytest_config_with_empty_model_name(self) -> None:
        """Test from_pytest_config with empty model name."""

        class MockConfig:
            def getini(self, name: str) -> str:
                if name == "semantic_assert_model":
                    return ""
                return {
                    "semantic_assert_threshold": "0.85",
                    "semantic_assert_cache": "true",
                    "semantic_assert_cache_dir": ".cache/",
                    "semantic_assert_max_length": "10000",
                }.get(name, "")

        # Should use default model name
        config = Configuration.from_pytest_config(MockConfig())  # type: ignore
        assert config.model_name == "all-MiniLM-L6-v2"

    def test_from_pytest_config_with_whitespace_model_name(self) -> None:
        """Test from_pytest_config with whitespace-only model name."""

        class MockConfig:
            def getini(self, name: str) -> str:
                if name == "semantic_assert_model":
                    return "   "
                return {
                    "semantic_assert_threshold": "0.85",
                    "semantic_assert_cache": "true",
                    "semantic_assert_cache_dir": ".cache/",
                    "semantic_assert_max_length": "10000",
                }.get(name, "")

        with pytest.raises(pytest.UsageError, match="must be a non-empty string"):
            Configuration.from_pytest_config(MockConfig())  # type: ignore

    def test_from_pytest_config_cache_enabled_variations(self) -> None:
        """Test from_pytest_config with various cache enabled values."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
            ("off", False),
        ]

        for cache_str, expected in test_cases:

            class MockConfig:
                def __init__(self, cache_value: str) -> None:
                    self.cache_value = cache_value

                def getini(self, name: str) -> str:
                    if name == "semantic_assert_cache":
                        return self.cache_value
                    return {
                        "semantic_assert_threshold": "0.85",
                        "semantic_assert_model": "all-MiniLM-L6-v2",
                        "semantic_assert_cache_dir": ".cache/",
                        "semantic_assert_max_length": "10000",
                    }.get(name, "")

            config = Configuration.from_pytest_config(MockConfig(cache_str))  # type: ignore
            assert config.cache_enabled == expected, f"Failed for cache_str='{cache_str}'"

    def test_from_pytest_config_with_empty_cache_dir(self) -> None:
        """Test from_pytest_config with empty cache_dir."""

        class MockConfig:
            def getini(self, name: str) -> str:
                if name == "semantic_assert_cache_dir":
                    return ""
                return {
                    "semantic_assert_threshold": "0.85",
                    "semantic_assert_model": "all-MiniLM-L6-v2",
                    "semantic_assert_cache": "true",
                    "semantic_assert_max_length": "10000",
                }.get(name, "")

        # Should use default cache_dir
        config = Configuration.from_pytest_config(MockConfig())  # type: ignore
        assert config.cache_dir == ".pytest-semantic-cache/"

    def test_from_pytest_config_strips_whitespace(self) -> None:
        """Test that from_pytest_config strips whitespace from strings."""

        class MockConfig:
            def getini(self, name: str) -> str:
                return {
                    "semantic_assert_threshold": "0.85",
                    "semantic_assert_model": "  my-model  ",
                    "semantic_assert_cache": "true",
                    "semantic_assert_cache_dir": "  /tmp/cache/  ",
                    "semantic_assert_max_length": "10000",
                }.get(name, "")

        config = Configuration.from_pytest_config(MockConfig())  # type: ignore
        assert config.model_name == "my-model"  # Stripped
        assert config.cache_dir == "/tmp/cache/"  # Stripped
