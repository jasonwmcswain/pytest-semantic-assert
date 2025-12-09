"""Unit tests for assertions module standalone usage (without pytest)."""

from unittest.mock import patch

import pytest


class TestAssertSemanticallySimilarStandalone:
    """Test assert_semantically_similar in standalone mode (non-pytest context)."""

    def test_fallback_config_when_pytest_unavailable(self) -> None:
        """Test that assertions work when pytest.Config.fromdictargs fails."""
        # Mock pytest.Config.fromdictargs to raise an exception
        with patch("pytest.Config.fromdictargs", side_effect=Exception("Not in pytest context")):
            from pytest_semantic_assert import assert_semantically_similar

            # Should fall back to default Configuration and still work
            assert_semantically_similar("Hello world", "Hello world", threshold=0.95)

    def test_fallback_uses_default_configuration(self) -> None:
        """Test that fallback creates Configuration with defaults."""
        with patch("pytest.Config.fromdictargs", side_effect=RuntimeError("No pytest")):
            from pytest_semantic_assert import assert_semantically_similar

            # Should use default threshold (0.85) when no threshold provided
            # These texts are similar enough to pass with default threshold
            assert_semantically_similar("The weather is nice", "The weather is pleasant")

    def test_assert_semantically_similar_to_any_fallback(self) -> None:
        """Test assert_semantically_similar_to_any with fallback config."""
        with patch("pytest.Config.fromdictargs", side_effect=Exception("No pytest")):
            from pytest_semantic_assert import assert_semantically_similar_to_any

            # Should fall back and still work
            assert_semantically_similar_to_any(
                "Hello there", ["Hi there", "Hey there", "Greetings friend"], threshold=0.60
            )


class TestAssertSemanticallySimilarToAnyEdgeCases:
    """Test edge cases for assert_semantically_similar_to_any."""

    def test_empty_expected_list_raises_error(self) -> None:
        """Test that empty expected_list raises ValueError."""
        from pytest_semantic_assert import assert_semantically_similar_to_any

        with pytest.raises(ValueError, match="expected_list must be non-empty"):
            assert_semantically_similar_to_any("Hello", [], threshold=0.85)

    def test_single_item_list(self) -> None:
        """Test with single item in expected_list."""
        from pytest_semantic_assert import assert_semantically_similar_to_any

        # Should work with single item
        assert_semantically_similar_to_any("Hello world", ["Hello world"], threshold=0.95)

    def test_no_match_shows_all_scores(self) -> None:
        """Test that failure message shows all scores."""
        from pytest_semantic_assert import assert_semantically_similar_to_any

        with pytest.raises(AssertionError) as exc_info:
            assert_semantically_similar_to_any(
                "Hello",
                ["Goodbye", "Farewell", "See you"],
                threshold=0.95,
            )

        error_msg = str(exc_info.value)
        # Should show all three options
        assert "Goodbye" in error_msg
        assert "Farewell" in error_msg
        assert "See you" in error_msg
        assert "Similarity Scores" in error_msg

    def test_threshold_validation(self) -> None:
        """Test threshold validation in assert_semantically_similar_to_any."""
        from pytest_semantic_assert import assert_semantically_similar_to_any

        # Test invalid threshold
        with pytest.raises(ValueError, match="threshold must be between 0.0 and 1.0"):
            assert_semantically_similar_to_any("Hello", ["Hi"], threshold=1.5)

        with pytest.raises(ValueError, match="threshold must be between 0.0 and 1.0"):
            assert_semantically_similar_to_any("Hello", ["Hi"], threshold=-0.1)


class TestErrorMessageFormatting:
    """Test error message formatting functions."""

    def test_error_message_with_very_long_texts(self) -> None:
        """Test error message formatting with very long texts."""
        from pytest_semantic_assert import assert_semantically_similar

        long_text1 = "Hello " * 100  # 600 characters
        long_text2 = "Goodbye " * 100  # 800 characters

        with pytest.raises(AssertionError) as exc_info:
            assert_semantically_similar(long_text1, long_text2, threshold=0.95)

        error_msg = str(exc_info.value)
        # Should contain truncated versions or full text
        assert "Semantic similarity too low" in error_msg
        assert "Similarity Score:" in error_msg

    def test_error_message_with_special_characters(self) -> None:
        """Test error message with special characters in text."""
        from pytest_semantic_assert import assert_semantically_similar

        text1 = 'Text with "quotes" and \\backslashes\\'
        text2 = "Completely different text"

        with pytest.raises(AssertionError) as exc_info:
            assert_semantically_similar(text1, text2, threshold=0.95)

        error_msg = str(exc_info.value)
        # Should handle special characters properly
        assert "Semantic similarity too low" in error_msg

    def test_error_message_with_newlines(self) -> None:
        """Test error message with newlines in text."""
        from pytest_semantic_assert import assert_semantically_similar

        text1 = "Line 1\nLine 2\nLine 3"
        text2 = "Different\nContent\nHere"

        with pytest.raises(AssertionError) as exc_info:
            assert_semantically_similar(text1, text2, threshold=0.95)

        error_msg = str(exc_info.value)
        assert "Semantic similarity too low" in error_msg


class TestSuggestionGeneration:
    """Test suggestion generation based on similarity scores."""

    def test_suggestion_for_very_low_similarity(self) -> None:
        """Test suggestion when similarity is very low (< 0.3)."""
        from pytest_semantic_assert import assert_semantically_similar

        with pytest.raises(AssertionError) as exc_info:
            assert_semantically_similar(
                "Machine learning algorithms",
                "Cooking delicious pasta",
                threshold=0.85,
            )

        error_msg = str(exc_info.value)
        # Should suggest texts are unrelated
        assert "Suggestion:" in error_msg

    def test_suggestion_for_moderate_similarity(self) -> None:
        """Test suggestion when similarity is moderate (0.3-0.6)."""
        from pytest_semantic_assert import assert_semantically_similar

        with pytest.raises(AssertionError) as exc_info:
            assert_semantically_similar("Good morning", "Good evening", threshold=0.85)

        error_msg = str(exc_info.value)
        assert "Suggestion:" in error_msg

    def test_suggestion_for_high_similarity(self) -> None:
        """Test suggestion when similarity is high but below threshold (0.6-threshold)."""
        from pytest_semantic_assert import assert_semantically_similar

        with pytest.raises(AssertionError) as exc_info:
            assert_semantically_similar("Hello there", "Hi there", threshold=0.95)

        error_msg = str(exc_info.value)
        assert "Suggestion:" in error_msg


class TestInputValidation:
    """Test input validation in assertion functions."""

    def test_text_too_short_actual(self) -> None:
        """Test that text too short raises appropriate error."""
        from pytest_semantic_assert import assert_semantically_similar
        from pytest_semantic_assert.exceptions import TextTooShortError

        with pytest.raises(TextTooShortError):
            assert_semantically_similar("ab", "Hello world", threshold=0.85)

    def test_text_too_short_expected(self) -> None:
        """Test that expected text too short raises appropriate error."""
        from pytest_semantic_assert import assert_semantically_similar
        from pytest_semantic_assert.exceptions import TextTooShortError

        with pytest.raises(TextTooShortError):
            assert_semantically_similar("Hello world", "ab", threshold=0.85)

    def test_empty_string_actual(self) -> None:
        """Test that empty actual string raises error."""
        from pytest_semantic_assert import assert_semantically_similar
        from pytest_semantic_assert.exceptions import TextTooShortError

        with pytest.raises(TextTooShortError):
            assert_semantically_similar("", "Hello", threshold=0.85)

    def test_whitespace_only_string(self) -> None:
        """Test that whitespace-only string raises error after stripping."""
        from pytest_semantic_assert import assert_semantically_similar
        from pytest_semantic_assert.exceptions import TextTooShortError

        with pytest.raises(TextTooShortError):
            assert_semantically_similar("   ", "Hello", threshold=0.85)
