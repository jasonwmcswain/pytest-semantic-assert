"""Core semantic assertion functions."""

from typing import Optional

import pytest

from pytest_semantic_assert.plugin import get_config, get_embedding_manager
from pytest_semantic_assert.similarity import cosine_similarity


def assert_semantically_similar(
    actual: str,
    expected: str,
    threshold: Optional[float] = None,
) -> None:
    """Assert that two texts are semantically similar above a threshold.

    Compares `actual` and `expected` using semantic embeddings and cosine
    similarity. Raises AssertionError if similarity score is below threshold.

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
        >>> assert_semantically_similar("Hello!", "Hi there!", threshold=0.85)
        # Passes - semantically similar

        >>> assert_semantically_similar("Hello!", "Goodbye!", threshold=0.85)
        # Raises AssertionError - semantically different

    Notes:
        - Threshold defaults to pytest.ini `semantic_assert_threshold` (0.85)
        - Embeddings are cached for performance (configurable via pytest.ini)
        - Thread-safe for parallel test execution (pytest-xdist compatible)
    """
    # Get pytest config
    try:
        config = pytest.Config.fromdictargs({}, [])
        pytest_config = get_config(config)
        manager = get_embedding_manager(config)
    except Exception:
        # Fallback for non-pytest usage
        from pytest_semantic_assert.config import Configuration
        from pytest_semantic_assert.embeddings import EmbeddingManager

        pytest_config = Configuration()
        manager = EmbeddingManager(pytest_config)

    # Use provided threshold or config default
    if threshold is None:
        threshold = pytest_config.threshold

    # Validate threshold
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"threshold must be between 0.0 and 1.0, got: {threshold}")

    # Get embeddings (validation happens in manager)
    actual_embedding = manager.get_embedding(actual)
    expected_embedding = manager.get_embedding(expected)

    # Compute similarity
    score = cosine_similarity(actual_embedding, expected_embedding)

    # Check if assertion passes
    if score >= threshold:
        return  # Pass silently

    # Generate failure message
    message = _format_error_message(actual, expected, score, threshold)
    raise AssertionError(message)


def assert_semantically_similar_to_any(
    actual: str,
    expected_list: list[str],
    threshold: Optional[float] = None,
) -> None:
    """Assert that text is semantically similar to ANY option in a list.

    Compares `actual` against each item in `expected_list` using semantic
    similarity. Passes if ANY comparison meets threshold. Useful for testing
    against multiple acceptable responses.

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
        >>> assert_semantically_similar_to_any(
        ...     "Bye!",
        ...     ["Goodbye!", "See you later!", "Farewell!"],
        ...     threshold=0.85
        ... )
        # Passes - matches "Goodbye!" semantically

        >>> assert_semantically_similar_to_any(
        ...     "Hello!",
        ...     ["Goodbye!", "Farewell!"],
        ...     threshold=0.85
        ... )
        # Raises AssertionError - no match in list

    Notes:
        - Short-circuits on first match (early success optimization)
        - Error message shows scores for ALL options (debugging aid)
        - Performance: <5s for 100-item list (per spec US3 scenario 4)
    """
    # Validate expected_list
    if not expected_list:
        raise ValueError("expected_list must be non-empty")

    # Get pytest config
    try:
        config = pytest.Config.fromdictargs({}, [])
        pytest_config = get_config(config)
        manager = get_embedding_manager(config)
    except Exception:
        # Fallback for non-pytest usage
        from pytest_semantic_assert.config import Configuration
        from pytest_semantic_assert.embeddings import EmbeddingManager

        pytest_config = Configuration()
        manager = EmbeddingManager(pytest_config)

    # Use provided threshold or config default
    if threshold is None:
        threshold = pytest_config.threshold

    # Validate threshold
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"threshold must be between 0.0 and 1.0, got: {threshold}")

    # Get embedding for actual text
    actual_embedding = manager.get_embedding(actual)

    # Compare against each expected value
    scores: list[tuple[str, float]] = []
    for expected in expected_list:
        expected_embedding = manager.get_embedding(expected)
        score = cosine_similarity(actual_embedding, expected_embedding)
        scores.append((expected, score))

        # Short-circuit on first match
        if score >= threshold:
            return  # Pass silently

    # All comparisons failed - generate detailed error message
    message = _format_multi_error_message(actual, scores, threshold)
    raise AssertionError(message)


def _format_error_message(actual: str, expected: str, score: float, threshold: float) -> str:
    """Format detailed assertion error message.

    Args:
        actual: Actual text
        expected: Expected text
        score: Similarity score
        threshold: Threshold that was not met

    Returns:
        Formatted error message with suggestion
    """
    suggestion = _suggest_action(score, threshold)

    return (
        f"Semantic similarity too low\n\n"
        f'Expected (semantically): "{expected}"\n'
        f'Actual: "{actual}"\n'
        f"Similarity Score: {score:.2f} (threshold: {threshold})\n\n"
        f"Suggestion: {suggestion}"
    )


def _format_multi_error_message(
    actual: str, scores: list[tuple[str, float]], threshold: float
) -> str:
    """Format error message for multi-value assertion.

    Args:
        actual: Actual text
        scores: List of (expected, score) tuples
        threshold: Threshold that was not met

    Returns:
        Formatted error message showing all scores
    """
    # Sort scores by similarity (highest first)
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)

    scores_text = "\n".join(f'  - "{expected}": {score:.2f}' for expected, score in sorted_scores)

    best_score = sorted_scores[0][1] if sorted_scores else 0.0
    suggestion = _suggest_action(best_score, threshold)

    return (
        f"Semantic similarity too low for all options\n\n"
        f'Actual: "{actual}"\n'
        f"Similarity Scores (threshold: {threshold}):\n"
        f"{scores_text}\n\n"
        f"Suggestion: {suggestion}"
    )


def _suggest_action(score: float, threshold: float) -> str:
    """Generate contextual suggestion based on similarity score.

    Args:
        score: Similarity score achieved
        threshold: Threshold that was expected

    Returns:
        Contextual suggestion string
    """
    if score < 0.3:
        return (
            "These texts are semantically unrelated (similarity < 0.3). "
            "Verify your expected text matches the intended meaning."
        )
    elif score < 0.6:
        return (
            "These texts are somewhat related but differ in meaning (similarity 0.3-0.6). "
            "Check if expected text captures the core concept correctly."
        )
    else:
        # Close to threshold
        return (
            f"Texts are nearly similar (score {score:.2f} vs threshold {threshold}). "
            f"Consider lowering threshold or reviewing expected text for minor differences."
        )
