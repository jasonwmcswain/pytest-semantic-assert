"""Configuration management for pytest-semantic-assert."""

from dataclasses import dataclass

import pytest


@dataclass
class Configuration:
    """Plugin configuration loaded from pytest.ini or pyproject.toml."""

    threshold: float = 0.85
    model_name: str = "all-MiniLM-L6-v2"
    cache_enabled: bool = True
    cache_dir: str = ".pytest-semantic-cache/"
    max_length: int = 10000

    @classmethod
    def from_pytest_config(cls, config: pytest.Config) -> "Configuration":
        """Load configuration from pytest Config object.

        Args:
            config: Pytest configuration object

        Returns:
            Configuration instance with validated settings

        Raises:
            pytest.UsageError: If configuration is invalid
        """
        # Load values from pytest.ini/pyproject.toml
        threshold_str = config.getini("semantic_assert_threshold")
        model_name = config.getini("semantic_assert_model")
        cache_str = config.getini("semantic_assert_cache")
        cache_dir = config.getini("semantic_assert_cache_dir")
        max_length_str = config.getini("semantic_assert_max_length")

        # Parse and validate threshold
        try:
            threshold = float(threshold_str) if threshold_str else 0.85
        except ValueError as e:
            raise pytest.UsageError(
                f"semantic_assert_threshold must be a float, got: {threshold_str}"
            ) from e

        if not 0.0 <= threshold <= 1.0:
            raise pytest.UsageError(
                f"semantic_assert_threshold must be between 0.0 and 1.0, got: {threshold}"
            )

        # Parse and validate cache enabled
        if isinstance(cache_str, bool):
            cache_enabled = cache_str
        elif isinstance(cache_str, str):
            cache_enabled = cache_str.lower() in ("true", "1", "yes", "on")
        else:
            cache_enabled = True

        # Parse and validate max_length
        try:
            max_length = int(max_length_str) if max_length_str else 10000
        except ValueError as e:
            raise pytest.UsageError(
                f"semantic_assert_max_length must be an integer, got: {max_length_str}"
            ) from e

        if max_length <= 0:
            raise pytest.UsageError(
                f"semantic_assert_max_length must be positive, got: {max_length}"
            )

        # Validate model name
        if not model_name:
            model_name = "all-MiniLM-L6-v2"

        if not isinstance(model_name, str) or not model_name.strip():
            raise pytest.UsageError(
                f"semantic_assert_model must be a non-empty string, got: {model_name}"
            )

        # Validate cache_dir
        if not cache_dir:
            cache_dir = ".pytest-semantic-cache/"

        return cls(
            threshold=threshold,
            model_name=model_name.strip(),
            cache_enabled=cache_enabled,
            cache_dir=cache_dir.strip(),
            max_length=max_length,
        )

    def validate(self) -> None:
        """Validate configuration values.

        Raises:
            ValueError: If any configuration value is invalid
        """
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError(f"threshold must be between 0.0 and 1.0, got: {self.threshold}")

        if not self.model_name or not self.model_name.strip():
            raise ValueError("model_name must be a non-empty string")

        if self.max_length <= 0:
            raise ValueError(f"max_length must be positive, got: {self.max_length}")
