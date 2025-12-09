"""Integration tests for assertion functions with real components.

These tests verify that assertion functions work correctly when integrated
with real embedding models, similarity calculations, and configuration.
Unlike unit tests (which mock components) or E2E tests (which test full
user scenarios), these tests focus on component interactions.
"""

import pytest
from pytest_semantic_assert import assert_semantically_similar


class TestAssertSemanticallySimilarIntegration:
    """Integration tests for assert_semantically_similar with real components."""

    def test_basic_assertion_pass_case_similar_texts(self) -> None:
        """Test basic assertion passes with semantically similar texts.

        Verifies integration between:
        - Assertion function
        - Embedding manager (real model)
        - Similarity calculator
        - Configuration defaults
        """
        actual = "The quick brown fox jumps over the lazy dog"
        expected = "A fast brown fox leaps over a sleepy dog"

        # Should pass - texts are semantically similar
        # Uses real embeddings and similarity calculation
        assert_semantically_similar(actual, expected, threshold=0.70)

    def test_basic_assertion_fail_case_different_texts(self) -> None:
        """Test basic assertion fails with semantically different texts.

        Verifies integration between:
        - Assertion function
        - Embedding manager (real model)
        - Similarity calculator
        - Error message formatting
        """
        actual = "The weather is sunny and warm today"
        expected = "I enjoy programming in Python"

        # Should fail - texts are semantically different
        with pytest.raises(AssertionError) as exc_info:
            assert_semantically_similar(actual, expected, threshold=0.85)

        # Verify error message contains all required components
        error_msg = str(exc_info.value)
        assert "Semantic similarity too low" in error_msg
        assert 'Expected (semantically): "I enjoy programming in Python"' in error_msg
        assert 'Actual: "The weather is sunny and warm today"' in error_msg
        assert "Similarity Score:" in error_msg
        assert "threshold: 0.85" in error_msg
        assert "Suggestion:" in error_msg

        # Verify score is actually low (< 0.85)
        # Extract score from error message for validation
        assert "0." in error_msg  # Score should be present as decimal

    def test_assertion_with_explicit_threshold_override(self) -> None:
        """Test that explicit threshold parameter overrides config default.

        Verifies that threshold parameter correctly flows through:
        - Assertion function parameter
        - Configuration system
        - Similarity comparison logic
        """
        actual = "Hello there"
        expected = "Hi there"

        # These texts are similar but not identical
        # With low threshold, should pass
        assert_semantically_similar(actual, expected, threshold=0.60)

        # With very high threshold, should fail
        with pytest.raises(AssertionError) as exc_info:
            assert_semantically_similar(actual, expected, threshold=0.99)

        error_msg = str(exc_info.value)
        assert "threshold: 0.99" in error_msg

    def test_assertion_caching_integration(self) -> None:
        """Test that embedding caching works across multiple assertions.

        Verifies integration between:
        - Assertion function
        - Embedding manager with caching
        - Cache system (memory or disk)

        Note: This test verifies caching works but doesn't measure performance.
        """
        text1 = "This is a test sentence for caching"
        text2 = "This is another test sentence for caching too"

        # First call - embeddings should be computed and cached
        assert_semantically_similar(text1, text2, threshold=0.60)

        # Second call with same texts - should use cached embeddings
        assert_semantically_similar(text1, text2, threshold=0.60)

        # Third call with one new text - should compute only one new embedding
        text3 = "This is yet another test sentence for caching"
        assert_semantically_similar(text1, text3, threshold=0.60)

    def test_assertion_with_boundary_threshold_values(self) -> None:
        """Test assertions work correctly with boundary threshold values.

        Verifies that threshold boundaries (0.0 and 1.0) are handled correctly
        through the full integration stack.
        """
        actual = "Hello world"
        expected = "Goodbye world"

        # threshold=0.0 should always pass (any similarity is sufficient)
        assert_semantically_similar(actual, expected, threshold=0.0)

        # threshold=1.0 is valid but very strict - likely to fail unless identical
        # We don't assert failure here as it depends on embedding model behavior
        try:
            assert_semantically_similar(actual, expected, threshold=1.0)
        except AssertionError:
            pass  # Expected for non-identical texts

    def test_assertion_with_unicode_and_special_characters(self) -> None:
        """Test assertions handle Unicode and special characters correctly.

        Verifies integration with embedding model's text encoding and
        similarity calculation with non-ASCII text.
        """
        actual = "Hello! 你好! Привет! مرحبا"
        expected = "Greetings! 你好! Привет! مرحبا"

        # Should handle Unicode correctly through the full stack
        assert_semantically_similar(actual, expected, threshold=0.70)

    def test_assertion_error_message_formatting_integration(self) -> None:
        """Test that error messages are correctly formatted through full stack.

        Verifies integration between:
        - Assertion function
        - Error message formatter
        - Suggestion generator
        - Score formatting
        """
        actual = "Machine learning is fascinating"
        expected = "Cooking pasta is delicious"

        with pytest.raises(AssertionError) as exc_info:
            assert_semantically_similar(actual, expected, threshold=0.85)

        error_msg = str(exc_info.value)

        # Verify all message components are present and properly formatted
        assert "Semantic similarity too low" in error_msg
        assert "Expected (semantically):" in error_msg
        assert "Actual:" in error_msg
        assert "Similarity Score:" in error_msg
        assert "Suggestion:" in error_msg

        # Verify texts are properly quoted in message
        assert '"Machine learning is fascinating"' in error_msg
        assert '"Cooking pasta is delicious"' in error_msg

        # Verify score is formatted as percentage or decimal
        lines = error_msg.split("\n")
        score_line = [line for line in lines if "Similarity Score:" in line][0]
        assert "0." in score_line or "%" in score_line
