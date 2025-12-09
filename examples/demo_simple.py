"""
Simplest possible demonstration of pytest-semantic-assert.

Run this file to see semantic assertions in action!
"""

from pytest_semantic_assert import assert_semantically_similar


def test_basic_semantic_match():
    """Test that semantically similar texts pass."""
    actual = "Hello! How can I help you today?"
    expected = "Hi there! What can I do for you?"

    # This passes even though the wording is different
    assert_semantically_similar(actual, expected, threshold=0.55)
    print("✅ Semantic assertion passed!")


def test_exact_match():
    """Test that exact matches always pass."""
    text = "The quick brown fox jumps over the lazy dog"

    assert_semantically_similar(text, text, threshold=0.99)
    print("✅ Exact match passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("pytest-semantic-assert Demo")
    print("=" * 60)
    print()
    print("Running semantic assertion tests...")
    print()

    # Run the tests
    import pytest

    pytest.main([__file__, "-v"])

