"""pytest-semantic-assert: Semantic assertions for LLM testing.

A pytest plugin for fuzzy semantic assertions of LLM outputs using
embedding-based similarity comparison.
"""

__version__ = "0.1.0"

from pytest_semantic_assert.assertions import (
    assert_semantically_similar,
    assert_semantically_similar_to_any,
)
from pytest_semantic_assert.async_assertions import (
    assert_semantically_similar_async,
    assert_semantically_similar_to_any_async,
)

__all__ = [
    "__version__",
    "assert_semantically_similar",
    "assert_semantically_similar_to_any",
    "assert_semantically_similar_async",
    "assert_semantically_similar_to_any_async",
]
