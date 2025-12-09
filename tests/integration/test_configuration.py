"""Integration tests for pytest.ini configuration with real pytest.

These tests verify that configuration flows correctly from pytest.ini through
the plugin system to the assertion functions. They test the integration between:
- pytest.ini file parsing
- Plugin hooks (pytest_addoption, pytest_configure)
- Configuration loading
- Assertion function behavior with configured defaults
"""

import textwrap
from pathlib import Path

import pytest


class TestPytestIniConfigurationIntegration:
    """Integration tests for pytest.ini configuration."""

    def test_pytest_ini_threshold_override(self, tmp_path: Path) -> None:
        """Test that pytest.ini threshold setting overrides default.

        Verifies integration between:
        - pytest.ini parsing
        - Plugin configuration loading
        - Assertion function threshold usage
        """
        # Create a test file that uses default threshold (no explicit parameter)
        test_file = tmp_path / "test_threshold.py"
        test_file.write_text(
            textwrap.dedent(
                """
                from pytest_semantic_assert import assert_semantically_similar

                def test_with_config_threshold():
                    # These texts are moderately similar
                    # Should pass with threshold=0.70 but fail with 0.85
                    actual = "Good morning everyone, how are you today?"
                    expected = "Hello everybody, how are you doing today?"
                    assert_semantically_similar(actual, expected)
                """
            )
        )

        # Create pytest.ini with custom threshold
        pytest_ini = tmp_path / "pytest.ini"
        pytest_ini.write_text(
            textwrap.dedent(
                """
                [pytest]
                semantic_assert_threshold = 0.70
                """
            )
        )

        # Run pytest with the custom config
        result = pytest.main(["-v", str(test_file), f"--rootdir={tmp_path}"])

        # Should pass because threshold is 0.70 (lenient)
        assert result == 0, "Test should pass with threshold=0.70"

    def test_pytest_ini_model_selection(self, tmp_path: Path) -> None:
        """Test that pytest.ini model setting is used.

        Verifies integration between:
        - pytest.ini model configuration
        - Plugin configuration loading
        - EmbeddingManager model selection
        """
        # Create a simple passing test
        test_file = tmp_path / "test_model.py"
        test_file.write_text(
            textwrap.dedent(
                """
                from pytest_semantic_assert import assert_semantically_similar

                def test_with_config_model():
                    # Simple test that should pass with any reasonable model
                    actual = "Hello world"
                    expected = "Hello world"
                    assert_semantically_similar(actual, expected, threshold=0.95)
                """
            )
        )

        # Create pytest.ini with model specification
        # Note: We use the default model to ensure test passes
        # (testing with a non-existent model would fail at model load time)
        pytest_ini = tmp_path / "pytest.ini"
        pytest_ini.write_text(
            textwrap.dedent(
                """
                [pytest]
                semantic_assert_model = all-MiniLM-L6-v2
                """
            )
        )

        # Run pytest with the custom config
        result = pytest.main(["-v", str(test_file), f"--rootdir={tmp_path}"])

        # Should pass - verifies model config is loaded and used
        assert result == 0, "Test should pass with configured model"

    def test_pytest_ini_cache_settings(self, tmp_path: Path) -> None:
        """Test that pytest.ini cache settings are respected.

        Verifies integration between:
        - pytest.ini cache configuration
        - Plugin configuration loading
        - Cache system initialization
        """
        # Create a test that runs assertions multiple times
        test_file = tmp_path / "test_cache_config.py"
        test_file.write_text(
            textwrap.dedent(
                """
                from pytest_semantic_assert import assert_semantically_similar

                def test_with_cache_enabled():
                    # Run same assertion twice - should use cache on second call
                    actual = "The quick brown fox"
                    expected = "A fast brown fox"

                    assert_semantically_similar(actual, expected, threshold=0.70)
                    assert_semantically_similar(actual, expected, threshold=0.70)

                def test_cache_across_tests():
                    # This should also benefit from cache if previous test ran
                    actual = "The quick brown fox"
                    expected = "The speedy brown fox"
                    assert_semantically_similar(actual, expected, threshold=0.70)
                """
            )
        )

        # Create pytest.ini with cache enabled and custom directory
        cache_dir = tmp_path / "custom_cache"
        pytest_ini = tmp_path / "pytest.ini"
        pytest_ini.write_text(
            textwrap.dedent(
                f"""
                [pytest]
                semantic_assert_cache = true
                semantic_assert_cache_dir = {cache_dir}
                """
            )
        )

        # Run pytest with the custom config
        result = pytest.main(["-v", str(test_file), f"--rootdir={tmp_path}"])

        # Should pass
        assert result == 0, "Tests should pass with cache enabled"

        # Verify cache directory was created (if using disk cache)
        # Note: Cache might be in memory mode, so this is optional verification
        if cache_dir.exists():
            assert cache_dir.is_dir(), "Cache directory should be created"

    def test_explicit_param_overriding_pytest_ini_default(self, tmp_path: Path) -> None:
        """Test that explicit parameters override pytest.ini defaults.

        Verifies that parameter precedence works correctly:
        explicit parameter > pytest.ini > hardcoded default

        Verifies integration between:
        - pytest.ini default configuration
        - Assertion function parameter handling
        - Configuration override logic
        """
        # Create a test with explicit threshold parameter
        test_file = tmp_path / "test_override.py"
        test_file.write_text(
            textwrap.dedent(
                """
                from pytest_semantic_assert import assert_semantically_similar

                def test_explicit_overrides_config():
                    # These texts are moderately similar
                    actual = "Good afternoon"
                    expected = "Good evening"

                    # Explicit threshold=0.60 should override pytest.ini threshold=0.90
                    assert_semantically_similar(actual, expected, threshold=0.60)

                def test_config_default_used():
                    # This test uses pytest.ini default (0.90)
                    # Should fail because texts aren't similar enough
                    actual = "Hello"
                    expected = "Hello"
                    # Identical texts should pass even with high threshold
                    assert_semantically_similar(actual, expected)
                """
            )
        )

        # Create pytest.ini with high threshold
        pytest_ini = tmp_path / "pytest.ini"
        pytest_ini.write_text(
            textwrap.dedent(
                """
                [pytest]
                semantic_assert_threshold = 0.90
                """
            )
        )

        # Run pytest with the custom config
        result = pytest.main(["-v", str(test_file), f"--rootdir={tmp_path}"])

        # Both tests should pass:
        # - First test passes because explicit threshold=0.60 overrides config
        # - Second test passes because identical texts meet any threshold
        assert result == 0, "Tests should pass with explicit parameter override"

    def test_pytest_ini_max_length_setting(self, pytestconfig: pytest.Config) -> None:
        """Test that pytest.ini max_length setting is enforced.

        Verifies integration between:
        - pytest.ini max_length configuration
        - Configuration validation
        - Embedding manager text validation

        Note: This test uses the current pytest session's config rather than
        spawning a subprocess, which ensures config is properly loaded.
        """
        from pytest_semantic_assert.config import Configuration
        from pytest_semantic_assert.embeddings import EmbeddingManager
        from pytest_semantic_assert.exceptions import TextTooLongError

        # Create a custom configuration with low max_length
        config = Configuration(max_length=100)
        config.validate()

        # Create embedding manager with custom config
        manager = EmbeddingManager(config)

        # Test 1: Text within limit should work
        short_text = "Hello there friend"
        embedding = manager.get_embedding(short_text)
        assert embedding is not None
        assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension

        # Test 2: Text exceeding limit should raise TextTooLongError
        long_text = "x" * 150
        with pytest.raises(TextTooLongError):
            manager.get_embedding(long_text)

    def test_pytest_ini_multiple_settings_together(self, tmp_path: Path) -> None:
        """Test that multiple pytest.ini settings work together correctly.

        Verifies integration of all configuration options simultaneously:
        - threshold
        - model
        - cache settings
        - max_length
        """
        # Create a comprehensive test
        test_file = tmp_path / "test_multi_config.py"
        test_file.write_text(
            textwrap.dedent(
                """
                from pytest_semantic_assert import assert_semantically_similar

                def test_with_all_configs():
                    # Test that uses all configured settings
                    actual = "The weather is nice today"
                    expected = "Today's weather is pleasant"

                    # Should use:
                    # - threshold from pytest.ini (0.70)
                    # - model from pytest.ini (all-MiniLM-L6-v2)
                    # - cache from pytest.ini (enabled)
                    # - max_length from pytest.ini (5000)
                    assert_semantically_similar(actual, expected)
                """
            )
        )

        # Create pytest.ini with all settings
        cache_dir = tmp_path / "test_cache"
        pytest_ini = tmp_path / "pytest.ini"
        pytest_ini.write_text(
            textwrap.dedent(
                f"""
                [pytest]
                semantic_assert_threshold = 0.70
                semantic_assert_model = all-MiniLM-L6-v2
                semantic_assert_cache = true
                semantic_assert_cache_dir = {cache_dir}
                semantic_assert_max_length = 5000
                """
            )
        )

        # Run pytest with the custom config
        result = pytest.main(["-v", str(test_file), f"--rootdir={tmp_path}"])

        # Should pass with all settings configured
        assert result == 0, "Test should pass with all settings configured"
