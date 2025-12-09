"""Unit tests for async semantic assertion functions.

Tests the async wrappers around synchronous assertions, verifying they work
correctly in async contexts with pytest-asyncio.
"""

import pytest
from pytest_semantic_assert.async_assertions import (
    assert_semantically_similar_async,
    assert_semantically_similar_to_any_async,
)
from pytest_semantic_assert.exceptions import TextTooLongError, TextTooShortError


class TestAssertSemanticallySimilarAsync:
    """Test cases for assert_semantically_similar_async."""

    @pytest.mark.asyncio
    async def test_basic_assertion_pass(self) -> None:
        """Test basic async assertion that should pass."""
        actual = "Hello world"
        expected = "Hi there"

        # Should pass without raising
        await assert_semantically_similar_async(actual, expected, threshold=0.40)

    @pytest.mark.asyncio
    async def test_basic_assertion_fail(self) -> None:
        """Test basic async assertion that should fail."""
        actual = "Hello world"
        expected = "Goodbye forever"

        with pytest.raises(AssertionError) as exc_info:
            await assert_semantically_similar_async(actual, expected, threshold=0.85)

        error_message = str(exc_info.value)
        assert "Semantic similarity too low" in error_message
        assert "Hello world" in error_message
        assert "Goodbye forever" in error_message

    @pytest.mark.asyncio
    async def test_explicit_threshold_override(self) -> None:
        """Test async assertion with explicit threshold override."""
        actual = "The quick brown fox"
        expected = "A fast brown fox"

        # Should pass with lower threshold
        await assert_semantically_similar_async(actual, expected, threshold=0.70)

        # Should fail with higher threshold
        with pytest.raises(AssertionError):
            await assert_semantically_similar_async(actual, expected, threshold=0.95)

    @pytest.mark.asyncio
    async def test_identical_texts_pass(self) -> None:
        """Test async assertion with identical texts."""
        text = "This is an identical text"

        # Identical texts should have similarity ~1.0
        await assert_semantically_similar_async(text, text, threshold=0.99)

    @pytest.mark.asyncio
    async def test_text_too_short_error(self) -> None:
        """Test async assertion with text too short."""
        actual = "Hi"  # Too short (< 3 chars)
        expected = "Hello world"

        with pytest.raises(TextTooShortError) as exc_info:
            await assert_semantically_similar_async(actual, expected)

        assert "minimum 3 characters required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_text_too_long_error(self) -> None:
        """Test async assertion with text too long."""
        actual = "x" * 15000  # Exceeds default max_length of 10000
        expected = "Hello world"

        with pytest.raises(TextTooLongError) as exc_info:
            await assert_semantically_similar_async(actual, expected)

        assert "exceeds maximum length" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_threshold_error(self) -> None:
        """Test async assertion with invalid threshold."""
        actual = "Hello world"
        expected = "Hi there"

        # Threshold > 1.0
        with pytest.raises(ValueError) as exc_info:
            await assert_semantically_similar_async(actual, expected, threshold=1.5)
        assert "threshold must be between 0.0 and 1.0" in str(exc_info.value)

        # Threshold < 0.0
        with pytest.raises(ValueError) as exc_info:
            await assert_semantically_similar_async(actual, expected, threshold=-0.1)
        assert "threshold must be between 0.0 and 1.0" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_unicode_text_handling(self) -> None:
        """Test async assertion with unicode text."""
        actual = "Hello 世界"
        expected = "Hi world"

        # Should handle unicode without errors
        await assert_semantically_similar_async(actual, expected, threshold=0.50)

    @pytest.mark.asyncio
    async def test_boundary_threshold_values(self) -> None:
        """Test async assertion with boundary threshold values."""
        actual = "Hello world"
        expected = "Hi there world"

        # Threshold = 0.0 should always pass
        await assert_semantically_similar_async(actual, expected, threshold=0.0)

        # Threshold = 1.0 should only pass for identical (or very similar)
        with pytest.raises(AssertionError):
            await assert_semantically_similar_async(actual, expected, threshold=1.0)


class TestAssertSemanticallySimilarToAnyAsync:
    """Test cases for assert_semantically_similar_to_any_async."""

    @pytest.mark.asyncio
    async def test_basic_assertion_pass(self) -> None:
        """Test basic async multi-value assertion that should pass."""
        actual = "Goodbye"
        expected_list = ["Farewell", "See you later", "Bye bye"]

        # Should pass (matches "Farewell" or "Bye bye")
        await assert_semantically_similar_to_any_async(actual, expected_list, threshold=0.60)

    @pytest.mark.asyncio
    async def test_basic_assertion_fail(self) -> None:
        """Test basic async multi-value assertion that should fail."""
        actual = "Hello"
        expected_list = ["Goodbye", "Farewell", "See you later"]

        with pytest.raises(AssertionError) as exc_info:
            await assert_semantically_similar_to_any_async(actual, expected_list, threshold=0.85)

        error_message = str(exc_info.value)
        assert "Semantic similarity too low for all options" in error_message
        assert "Hello" in error_message
        assert "Goodbye" in error_message

    @pytest.mark.asyncio
    async def test_first_match_success(self) -> None:
        """Test async assertion passes on first matching option."""
        actual = "Hello there"
        expected_list = ["Hi there", "Goodbye", "Farewell"]  # First should match

        # Should pass immediately on first match
        await assert_semantically_similar_to_any_async(actual, expected_list, threshold=0.60)

    @pytest.mark.asyncio
    async def test_last_match_success(self) -> None:
        """Test async assertion passes on last matching option."""
        actual = "Farewell"
        expected_list = ["Hello", "Good morning", "Goodbye"]  # Last should match

        # Should eventually match last option
        await assert_semantically_similar_to_any_async(actual, expected_list, threshold=0.60)

    @pytest.mark.asyncio
    async def test_empty_list_error(self) -> None:
        """Test async assertion with empty expected list."""
        actual = "Hello world"
        expected_list: list[str] = []

        with pytest.raises(ValueError) as exc_info:
            await assert_semantically_similar_to_any_async(actual, expected_list)

        assert "expected_list must be non-empty" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_single_item_list(self) -> None:
        """Test async assertion with single-item expected list."""
        actual = "Hello world"
        expected_list = ["Hi there world"]

        # Should work like regular assert_semantically_similar
        await assert_semantically_similar_to_any_async(actual, expected_list, threshold=0.60)

    @pytest.mark.asyncio
    async def test_text_too_short_in_list(self) -> None:
        """Test async assertion with too-short text in expected list."""
        actual = "Hello world"
        expected_list = ["Hi", "Yo", "OK"]  # First too short (< 3 chars after strip)

        with pytest.raises(TextTooShortError):
            await assert_semantically_similar_to_any_async(actual, expected_list)

    @pytest.mark.asyncio
    async def test_explicit_threshold_override(self) -> None:
        """Test async multi-value assertion with explicit threshold."""
        actual = "Good morning"
        expected_list = ["Hello", "Hi there", "Greetings"]

        # Should pass with lower threshold
        await assert_semantically_similar_to_any_async(actual, expected_list, threshold=0.50)

        # Should fail with higher threshold
        with pytest.raises(AssertionError):
            await assert_semantically_similar_to_any_async(actual, expected_list, threshold=0.95)

    @pytest.mark.asyncio
    async def test_large_expected_list(self) -> None:
        """Test async assertion with large expected list."""
        actual = "Hello"
        # Create list with 50 items, one should match
        expected_list = [f"Unrelated text {i}" for i in range(49)] + ["Hi there"]

        # Should find the matching item
        await assert_semantically_similar_to_any_async(actual, expected_list, threshold=0.60)

    @pytest.mark.asyncio
    async def test_unicode_in_list(self) -> None:
        """Test async assertion with unicode in expected list."""
        actual = "Hello world"
        expected_list = ["Bonjour monde", "Hi 世界", "Hola mundo"]

        # Should handle unicode without errors
        await assert_semantically_similar_to_any_async(actual, expected_list, threshold=0.40)


class TestAsyncBatchAssertions:
    """Test parallel async assertion execution."""

    @pytest.mark.asyncio
    async def test_parallel_assertions_with_gather(self) -> None:
        """Test multiple async assertions running in parallel."""
        import asyncio

        # Simulate parallel assertion execution
        await asyncio.gather(
            assert_semantically_similar_async("Hello", "Hi there", threshold=0.50),
            assert_semantically_similar_async("Goodbye", "Farewell", threshold=0.50),
            assert_semantically_similar_async("Thank you", "Thanks", threshold=0.60),
        )

    @pytest.mark.asyncio
    async def test_parallel_multi_assertions_with_gather(self) -> None:
        """Test multiple async multi-value assertions in parallel."""
        import asyncio

        # Simulate parallel multi-value assertion execution
        await asyncio.gather(
            assert_semantically_similar_to_any_async(
                "Hello", ["Hi there", "Hey there", "Greetings"], threshold=0.50
            ),
            assert_semantically_similar_to_any_async(
                "Goodbye", ["Bye bye", "Farewell", "See you"], threshold=0.50
            ),
        )

    @pytest.mark.asyncio
    async def test_mixed_pass_fail_in_parallel(self) -> None:
        """Test that one failure doesn't prevent other assertions."""
        import asyncio

        # First should pass, second should fail
        results = await asyncio.gather(
            assert_semantically_similar_async("Hello", "Hi there", threshold=0.50),
            assert_semantically_similar_async("Hello", "Goodbye", threshold=0.95),
            return_exceptions=True,  # Capture exceptions
        )

        # First should succeed (None)
        assert results[0] is None

        # Second should fail (AssertionError)
        assert isinstance(results[1], AssertionError)
