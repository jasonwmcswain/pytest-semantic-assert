"""Quickstart example for pytest-semantic-assert.

This demonstrates the most common use cases in under 5 minutes.
"""

from pytest_semantic_assert import assert_semantically_similar, assert_semantically_similar_to_any


def test_basic_semantic_assertion():
    """Most basic usage: assert two texts are semantically similar."""
    actual = "Hello! How can I help you?"
    expected = "Hi there! What can I do for you?"

    # Pass if semantically similar (even with different wording)
    assert_semantically_similar(actual, expected, threshold=0.60)


def test_exact_match_always_passes():
    """Exact matches always pass."""
    assert_semantically_similar("The quick brown fox", "The quick brown fox", threshold=0.99)


def test_similar_meaning_different_words():
    """Similar meaning with different words passes."""
    assert_semantically_similar(
        "The weather is nice today", "Today's weather is pleasant", threshold=0.60
    )


def test_multiple_acceptable_responses():
    """Test against multiple acceptable responses."""
    actual = "Goodbye!"

    # Passes if actual matches ANY of these semantically
    assert_semantically_similar_to_any(
        actual, ["Farewell!", "See you later!", "Take care!", "Have a great day!"], threshold=0.60
    )


def test_threshold_examples():
    """Demonstrate different thresholds."""
    # High threshold = strict (very similar required)
    assert_semantically_similar("Good morning", "Good morning!", threshold=0.95)  # Almost identical

    # Medium threshold = balanced (recommended default)
    assert_semantically_similar("How are you?", "How's it going?", threshold=0.60)

    # Low threshold = lenient (loosely related accepted)
    assert_semantically_similar("Hello", "Greetings", threshold=0.50)


if __name__ == "__main__":
    # Run with: pytest quickstart.py -v
    print("Run tests with: pytest quickstart.py -v")
