"""Async semantic assertion functions for async test contexts.

This module provides async wrappers around synchronous semantic assertions,
allowing seamless integration with pytest-asyncio and async LLM testing workflows.

The async functions run synchronous assertion logic in a thread pool to avoid
blocking the event loop, enabling natural async/await syntax in tests.
"""

import asyncio
from typing import Optional

from pytest_semantic_assert.assertions import (
    assert_semantically_similar as _sync_assert_semantically_similar,
)
from pytest_semantic_assert.assertions import (
    assert_semantically_similar_to_any as _sync_assert_semantically_similar_to_any,
)


async def assert_semantically_similar_async(
    actual: str,
    expected: str,
    threshold: Optional[float] = None,
) -> None:
    """Async version of assert_semantically_similar.

    Compares `actual` and `expected` using semantic embeddings and cosine
    similarity. Raises AssertionError if similarity score is below threshold.

    This async version runs the embedding computation in a thread pool to avoid
    blocking the event loop, making it suitable for async test contexts.

    Args:
        actual: The actual text output to test (from LLM, function, etc.)
        expected: The expected text for semantic comparison
        threshold: Similarity threshold (0.0-1.0). If None, uses configured
            default from pytest.ini (default: 0.85)

    Raises:
        AssertionError: If similarity score < threshold, with detailed message
            showing expected, actual, score, and contextual suggestion
        ValueError: If actual or expected is empty or outside length bounds
            (3 to max_length characters)
        RuntimeError: If embedding model fails to load after retries

    Examples:
        >>> async def test_chatbot():
        ...     response = await chatbot.ask("Hello")
        ...     await assert_semantically_similar_async(response, "Hi!", threshold=0.85)

        >>> async def test_agent_response():
        ...     result = await agent.process("What's the weather?")
        ...     await assert_semantically_similar_async(
        ...         result,
        ...         "I'll check the weather for you",
        ...         threshold=0.80
        ...     )

    Notes:
        - Requires pytest-asyncio for async test support
        - Embeddings are cached for performance (configurable via pytest.ini)
        - Thread-safe for parallel async test execution
        - Performance: Same as sync version (~2ms cached, ~150ms uncached)
    """
    # Run synchronous assertion in thread pool to avoid blocking event loop
    await asyncio.to_thread(
        _sync_assert_semantically_similar,
        actual,
        expected,
        threshold,
    )


async def assert_semantically_similar_to_any_async(
    actual: str,
    expected_list: list[str],
    threshold: Optional[float] = None,
) -> None:
    """Async version of assert_semantically_similar_to_any.

    Compares `actual` against each item in `expected_list` using semantic
    similarity. Passes if ANY comparison meets threshold. Useful for testing
    against multiple acceptable responses in async contexts.

    This async version runs the embedding computation in a thread pool to avoid
    blocking the event loop.

    Args:
        actual: The actual text output to test
        expected_list: List of acceptable expected texts (non-empty)
        threshold: Similarity threshold (0.0-1.0). If None, uses configured
            default from pytest.ini (default: 0.85)

    Raises:
        AssertionError: If ALL comparisons fail threshold, with detailed message
            showing all similarity scores
        ValueError: If actual is invalid, expected_list is empty, or any item
            is outside length bounds
        RuntimeError: If embedding model fails to load after retries

    Examples:
        >>> async def test_agent_farewell():
        ...     response = await agent.ask("Goodbye")
        ...     await assert_semantically_similar_to_any_async(
        ...         response,
        ...         ["Bye!", "See you later!", "Farewell!"],
        ...         threshold=0.80
        ...     )

        >>> async def test_batch_responses():
        ...     responses = await asyncio.gather(
        ...         agent.ask("Hello"),
        ...         agent.ask("Goodbye")
        ...     )
        ...     await asyncio.gather(
        ...         assert_semantically_similar_to_any_async(
        ...             responses[0],
        ...             ["Hi!", "Hello!", "Hey!"]
        ...         ),
        ...         assert_semantically_similar_to_any_async(
        ...             responses[1],
        ...             ["Bye!", "Goodbye!", "See you!"]
        ...         )
        ...     )

    Notes:
        - Short-circuits on first match (early success optimization)
        - Error message shows scores for ALL options (debugging aid)
        - Can be used with asyncio.gather() for parallel batch assertions
        - Performance: <5s for 100-item list (per spec US3 scenario 4)
    """
    # Run synchronous assertion in thread pool to avoid blocking event loop
    await asyncio.to_thread(
        _sync_assert_semantically_similar_to_any,
        actual,
        expected_list,
        threshold,
    )
