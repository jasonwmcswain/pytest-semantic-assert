"""Unit tests for pytest plugin hooks."""

import pytest
from pytest_semantic_assert import plugin
from pytest_semantic_assert.config import Configuration
from pytest_semantic_assert.embeddings import EmbeddingManager


class TestPytestAddoption:
    """Test pytest_addoption hook."""

    def test_pytest_addoption_registers_ini_options(self) -> None:
        """Test that pytest_addoption registers all required ini options."""

        # Create a mock parser
        class MockParser:
            def __init__(self) -> None:
                self.ini_options: dict[str, dict] = {}

            def addini(self, name: str, **kwargs: object) -> None:
                self.ini_options[name] = kwargs

        parser = MockParser()
        plugin.pytest_addoption(parser)  # type: ignore

        # Verify all options are registered
        assert "semantic_assert_threshold" in parser.ini_options
        assert "semantic_assert_model" in parser.ini_options
        assert "semantic_assert_cache" in parser.ini_options
        assert "semantic_assert_cache_dir" in parser.ini_options
        assert "semantic_assert_max_length" in parser.ini_options

    def test_threshold_option_defaults(self) -> None:
        """Test threshold option has correct defaults."""

        class MockParser:
            def __init__(self) -> None:
                self.ini_options: dict[str, dict] = {}

            def addini(self, name: str, **kwargs: object) -> None:
                self.ini_options[name] = kwargs

        parser = MockParser()
        plugin.pytest_addoption(parser)  # type: ignore

        threshold_opt = parser.ini_options["semantic_assert_threshold"]
        assert threshold_opt["default"] == "0.85"
        assert threshold_opt["type"] == "string"
        assert "help" in threshold_opt

    def test_model_option_defaults(self) -> None:
        """Test model option has correct defaults."""

        class MockParser:
            def __init__(self) -> None:
                self.ini_options: dict[str, dict] = {}

            def addini(self, name: str, **kwargs: object) -> None:
                self.ini_options[name] = kwargs

        parser = MockParser()
        plugin.pytest_addoption(parser)  # type: ignore

        model_opt = parser.ini_options["semantic_assert_model"]
        assert model_opt["default"] == "all-MiniLM-L6-v2"
        assert model_opt["type"] == "string"


class TestPytestConfigure:
    """Test pytest_configure hook."""

    def test_pytest_configure_loads_config(self, pytestconfig: pytest.Config) -> None:
        """Test that pytest_configure loads and validates configuration."""
        # Reset global state
        plugin._config = None

        # Call configure
        plugin.pytest_configure(pytestconfig)

        # Verify config was loaded
        assert plugin._config is not None
        assert plugin._config.__class__.__name__ == "Configuration"

    def test_pytest_configure_stores_config_in_namespace(self, pytestconfig: pytest.Config) -> None:
        """Test that config is stored in pytest namespace."""
        # Reset global state
        plugin._config = None

        # Call configure
        plugin.pytest_configure(pytestconfig)

        # Verify config is accessible via pytest namespace
        assert hasattr(pytestconfig, "_semantic_assert_config")
        assert pytestconfig._semantic_assert_config.__class__.__name__ == "Configuration"  # type: ignore

    def test_pytest_configure_validates_config(self, pytestconfig: pytest.Config) -> None:
        """Test that pytest_configure validates configuration."""
        # Reset global state
        plugin._config = None

        # This should not raise - config is valid
        plugin.pytest_configure(pytestconfig)

        # Config should be validated (threshold in range, etc.)
        assert plugin._config is not None
        assert 0.0 <= plugin._config.threshold <= 1.0


class TestGetEmbeddingManager:
    """Test get_embedding_manager function."""

    def test_get_embedding_manager_creates_manager(self, pytestconfig: pytest.Config) -> None:
        """Test that get_embedding_manager creates an EmbeddingManager."""
        # Reset global state
        plugin._embedding_manager = None
        plugin._config = None

        manager = plugin.get_embedding_manager(pytestconfig)

        assert manager is not None
        assert isinstance(manager, EmbeddingManager)

    def test_get_embedding_manager_returns_singleton(self, pytestconfig: pytest.Config) -> None:
        """Test that get_embedding_manager returns the same instance."""
        # Reset global state
        plugin._embedding_manager = None
        plugin._config = None

        manager1 = plugin.get_embedding_manager(pytestconfig)
        manager2 = plugin.get_embedding_manager(pytestconfig)

        # Should be the same instance (singleton pattern)
        assert manager1 is manager2

    def test_get_embedding_manager_with_existing_config(self, pytestconfig: pytest.Config) -> None:
        """Test get_embedding_manager when config already exists."""
        # Set up existing config
        plugin._config = Configuration()
        plugin._embedding_manager = None

        manager = plugin.get_embedding_manager(pytestconfig)

        assert manager is not None
        assert isinstance(manager, EmbeddingManager)

    def test_get_embedding_manager_creates_config_if_needed(
        self, pytestconfig: pytest.Config
    ) -> None:
        """Test that get_embedding_manager creates config if not present."""
        # Reset global state
        plugin._embedding_manager = None
        plugin._config = None

        manager = plugin.get_embedding_manager(pytestconfig)

        # Config should have been created
        assert plugin._config is not None
        assert plugin._config.__class__.__name__ == "Configuration"
        assert manager is not None


class TestGetConfig:
    """Test get_config function."""

    def test_get_config_returns_configuration(self, pytestconfig: pytest.Config) -> None:
        """Test that get_config returns a Configuration instance."""
        # Reset global state
        plugin._config = None

        config = plugin.get_config(pytestconfig)

        assert config is not None
        assert config.__class__.__name__ == "Configuration"

    def test_get_config_returns_singleton(self, pytestconfig: pytest.Config) -> None:
        """Test that get_config returns the same instance."""
        # Reset global state
        plugin._config = None

        config1 = plugin.get_config(pytestconfig)
        config2 = plugin.get_config(pytestconfig)

        # Should be the same instance
        assert config1 is config2

    def test_get_config_with_existing_config(self, pytestconfig: pytest.Config) -> None:
        """Test get_config when config already exists."""
        # Set up existing config
        existing_config = Configuration(threshold=0.95)
        plugin._config = existing_config

        config = plugin.get_config(pytestconfig)

        # Should return the existing config
        assert config is existing_config
        assert config.threshold == 0.95

    def test_get_config_creates_from_pytest_config(self, pytestconfig: pytest.Config) -> None:
        """Test that get_config creates config from pytest Config."""
        # Reset global state
        plugin._config = None

        config = plugin.get_config(pytestconfig)

        # Should have default values from pytest config
        assert config.threshold == 0.85  # Default
        assert config.model_name == "all-MiniLM-L6-v2"  # Default


class TestGlobalState:
    """Test global state management."""

    def test_global_state_initialization(self) -> None:
        """Test that global state variables are properly initialized."""
        # These should be module-level variables
        assert hasattr(plugin, "_embedding_manager")
        assert hasattr(plugin, "_config")

    def test_global_state_can_be_reset(self, pytestconfig: pytest.Config) -> None:
        """Test that global state can be reset between tests."""
        # Set some state
        plugin._config = Configuration(threshold=0.99)
        plugin._embedding_manager = None

        # Reset
        plugin._config = None
        plugin._embedding_manager = None

        # Verify reset
        assert plugin._config is None
        assert plugin._embedding_manager is None

    def test_multiple_get_config_calls_share_state(self, pytestconfig: pytest.Config) -> None:
        """Test that multiple get_config calls share global state."""
        # Reset
        plugin._config = None

        # First call creates config
        config1 = plugin.get_config(pytestconfig)

        # Modify global state
        plugin._config.threshold = 0.77

        # Second call should see the modification
        config2 = plugin.get_config(pytestconfig)
        assert config2.threshold == 0.77
        assert config1 is config2
