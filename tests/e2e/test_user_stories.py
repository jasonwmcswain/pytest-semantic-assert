"""End-to-end tests for user stories."""

import pytest
from pytest_semantic_assert import assert_semantically_similar, assert_semantically_similar_to_any


class TestUserStory1BasicSemanticSimilarity:
    """Test US1: Basic semantic similarity assertion."""

    def test_us1_scenario1_semantically_similar_texts_pass(self) -> None:
        """US1-1: Semantically similar texts pass the assertion."""
        # These texts have the same meaning but different wording
        actual = "Hello! How can I help you?"
        expected = "Hi there! What can I do for you?"

        # Should pass without raising AssertionError
        assert_semantically_similar(actual, expected, threshold=0.60)

    def test_us1_scenario2_different_texts_fail_with_score(self) -> None:
        """US1-2: Different texts fail with similarity score shown."""
        actual = "Hello!"
        expected = "Goodbye!"

        with pytest.raises(AssertionError) as exc_info:
            assert_semantically_similar(actual, expected, threshold=0.85)

        error_msg = str(exc_info.value)
        assert "Semantic similarity too low" in error_msg
        assert "Similarity Score:" in error_msg
        assert "threshold: 0.85" in error_msg

    def test_us1_scenario3_equivalent_texts_different_wording_pass(self) -> None:
        """US1-3: Equivalent texts in different wordings pass."""
        actual = "The weather is nice today."
        expected = "Today's weather is pleasant."

        # Should pass - same meaning, different wording
        assert_semantically_similar(actual, expected, threshold=0.70)

    def test_us1_scenario4_custom_threshold_respected(self) -> None:
        """US1-4: Custom threshold parameter is respected."""
        actual = "Good morning!"
        expected = "Good evening!"

        # With low threshold (lenient), should pass
        assert_semantically_similar(actual, expected, threshold=0.50)

        # With high threshold (strict), should fail
        with pytest.raises(AssertionError):
            assert_semantically_similar(actual, expected, threshold=0.95)

    def test_us1_scenario5_failure_message_shows_all_fields(self) -> None:
        """US1-5: Failure message shows expected, actual, score, and suggestion."""
        actual = "Apple"
        expected = "Orange"

        with pytest.raises(AssertionError) as exc_info:
            assert_semantically_similar(actual, expected, threshold=0.85)

        error_msg = str(exc_info.value)
        # Check all required fields are present
        assert 'Expected (semantically): "Orange"' in error_msg
        assert 'Actual: "Apple"' in error_msg
        assert "Similarity Score:" in error_msg
        assert "threshold: 0.85" in error_msg
        assert "Suggestion:" in error_msg


class TestUserStory3MultiValueComparison:
    """Test US3: Compare against multiple expected values."""

    def test_us3_scenario1_matches_first_option(self) -> None:
        """US3-1: Passes if matches first option in list."""
        actual = "Goodbye!"
        expected_list = ["Farewell!", "See you later!", "Take care!"]

        # Should pass - matches "Farewell!" semantically
        assert_semantically_similar_to_any(actual, expected_list, threshold=0.70)

    def test_us3_scenario2_matches_middle_option(self) -> None:
        """US3-2: Passes if matches any option in the middle."""
        actual = "See you!"
        expected_list = ["Hello!", "See you later!", "Goodbye!"]

        # Should pass - matches "See you later!" semantically
        assert_semantically_similar_to_any(actual, expected_list, threshold=0.70)

    def test_us3_scenario3_no_match_shows_all_scores(self) -> None:
        """US3-3: If no match, error shows scores for all options."""
        actual = "Hello!"
        expected_list = ["Goodbye!", "Farewell!", "Take care!"]

        with pytest.raises(AssertionError) as exc_info:
            assert_semantically_similar_to_any(actual, expected_list, threshold=0.85)

        error_msg = str(exc_info.value)
        # Should show all three options with their scores
        assert "Goodbye!" in error_msg
        assert "Farewell!" in error_msg
        assert "Take care!" in error_msg
        assert "Similarity Scores" in error_msg

    def test_us3_scenario4_large_list_completes_quickly(self) -> None:
        """US3-4: Large list (100+ items) completes in reasonable time."""
        import time

        actual = "Hello!"
        # Create 100 greetings
        expected_list = [f"Hi there number {i}!" for i in range(100)]
        # Add a match at the end
        expected_list.append("Hello there!")

        start = time.time()
        assert_semantically_similar_to_any(actual, expected_list, threshold=0.70)
        duration = time.time() - start

        # Should complete in under 5 seconds (per spec)
        assert duration < 5.0

    def test_us3_scenario5_empty_list_raises_error(self) -> None:
        """US3-5: Empty expected_list raises ValueError."""
        actual = "Hello!"
        expected_list: list[str] = []

        with pytest.raises(ValueError, match="expected_list must be non-empty"):
            assert_semantically_similar_to_any(actual, expected_list, threshold=0.85)


class TestEdgeCases:
    """Test edge cases from spec."""

    def test_text_too_short_raises_error(self) -> None:
        """Edge case: Text shorter than 3 characters raises error."""
        with pytest.raises(ValueError, match="minimum 3 characters required"):
            assert_semantically_similar("ab", "Hello", threshold=0.85)

    def test_empty_string_raises_error(self) -> None:
        """Edge case: Empty string raises error."""
        with pytest.raises(ValueError, match="minimum 3 characters required"):
            assert_semantically_similar("", "Hello", threshold=0.85)

    def test_threshold_out_of_range_low(self) -> None:
        """Edge case: Threshold below 0.0 raises error."""
        with pytest.raises(ValueError, match="threshold must be between 0.0 and 1.0"):
            assert_semantically_similar("Hello", "Hi", threshold=-0.1)

    def test_threshold_out_of_range_high(self) -> None:
        """Edge case: Threshold above 1.0 raises error."""
        with pytest.raises(ValueError, match="threshold must be between 0.0 and 1.0"):
            assert_semantically_similar("Hello", "Hi", threshold=1.5)

    def test_threshold_boundary_values(self) -> None:
        """Edge case: Threshold at boundary values (0.0, 1.0) are valid."""
        # threshold=0.0 should always pass
        assert_semantically_similar("Hello world", "Completely different text", threshold=0.0)

        # threshold=1.0 is valid but very strict
        # This may fail unless texts are nearly identical
        try:
            assert_semantically_similar("Hello world", "Hello there", threshold=1.0)
        except AssertionError:
            pass  # Expected for non-identical texts
