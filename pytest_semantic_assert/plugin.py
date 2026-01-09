"""Pytest plugin hooks for semantic assertions."""

from typing import Optional

import pytest

from pytest_semantic_assert.config import Configuration
from pytest_semantic_assert.embeddings import EmbeddingManager

# Global session-scoped embedding manager
_embedding_manager: Optional[EmbeddingManager] = None
_config: Optional[Configuration] = None


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register configuration options for semantic assertions.

    Args:
        parser: Pytest argument parser
    """
    parser.addini(
        "semantic_assert_threshold",
        type="string",
        default="0.85",
        help="Default similarity threshold (0.0-1.0)",
    )
    parser.addini(
        "semantic_assert_model",
        type="string",
        default="all-MiniLM-L6-v2",
        help="Embedding model identifier (sentence-transformers model name)",
    )
    parser.addini(
        "semantic_assert_cache",
        type="string",
        default="true",
        help="Enable embedding caching (true/false)",
    )
    parser.addini(
        "semantic_assert_cache_dir",
        type="string",
        default=".pytest-semantic-cache/",
        help="Cache storage location (directory path or 'memory')",
    )
    parser.addini(
        "semantic_assert_max_length",
        type="string",
        default="10000",
        help="Maximum text length in characters",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Configure plugin and validate settings.

    Args:
        config: Pytest configuration object

    Raises:
        pytest.UsageError: If configuration is invalid
    """
    global _config

    # Load and validate configuration
    _config = Configuration.from_pytest_config(config)
    _config.validate()

    # Store config in pytest namespace for access from tests
    config._semantic_assert_config = _config


def get_embedding_manager(config: pytest.Config) -> EmbeddingManager:
    """Get or create session-scoped embedding manager.

    Args:
        config: Pytest configuration object

    Returns:
        EmbeddingManager instance (created once per session)
    """
    global _embedding_manager, _config

    if _embedding_manager is None:
        if _config is None:
            _config = Configuration.from_pytest_config(config)
        _embedding_manager = EmbeddingManager(_config)

    return _embedding_manager


def get_config(config: pytest.Config) -> Configuration:
    """Get configuration for semantic assertions.

    Args:
        config: Pytest configuration object

    Returns:
        Configuration instance
    """
    global _config

    if _config is None:
        _config = Configuration.from_pytest_config(config)

    return _config
