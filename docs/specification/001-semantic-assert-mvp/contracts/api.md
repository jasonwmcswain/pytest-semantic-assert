# Public API Contract: pytest-semantic-assert

**Version**: 0.1.0 (MVP)
**Date**: 2025-12-06
**Status**: Draft
**Purpose**: Define public API signatures for stability and contract testing

---

## Package Exports

**Module**: `pytest_semantic_assert`

```python
from pytest_semantic_assert import (
    assert_semantically_similar,      # Core assertion function
    assert_semantically_similar_to_any,  # Multi-value assertion
    __version__,                       # Package version string
)
```

---

## Core Assertion Functions

### assert_semantically_similar

**Signature**:
```python
def assert_semantically_similar(
    actual: str,
    expected: str,
    threshold: float | None = None,
) -> None:
    """
    Assert that two texts are semantically similar above a threshold.

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
```

**Parameters**:
- `actual: str` - **Required**. Text to test. Must be 3-10000 chars (configurable max).
- `expected: str` - **Required**. Reference text for comparison. Must be 3-10000 chars.
- `threshold: float | None` - **Optional**. Similarity threshold (0.0-1.0). Defaults to config value (0.85).

**Return**: `None` (raises on failure, silent on success per pytest convention)

**Exceptions**:
- `AssertionError`: Similarity below threshold (test failure)
  - Message format: 3-part structure (what failed, details, suggestion)
  - Always includes: expected, actual, score (2 decimals), threshold
- `ValueError`: Invalid input (empty, too short <3 chars, too long >max_length)
  - Message: Clear explanation with bounds
- `RuntimeError`: Model load failure after retries
  - Message: Troubleshooting steps (network, disk space, model name)

**Behavior**:
- **Threshold Priority**: Explicit param > pytest.ini > default (0.85)
- **Caching**: Embeddings cached by default (configurable)
- **Performance**: <50ms with cache, <200ms without (per spec SC-003, SC-004)
- **Parallel-Safe**: File locking for cache writes, concurrent reads allowed

**Contract Stability**:
- Signature MUST NOT change in PATCH or MINOR versions
- New optional parameters allowed in MINOR versions (at end)
- Breaking changes ONLY in MAJOR versions with migration guide

---

### assert_semantically_similar_to_any

**Signature**:
```python
def assert_semantically_similar_to_any(
    actual: str,
    expected_list: list[str],
    threshold: float | None = None,
) -> None:
    """
    Assert that text is semantically similar to ANY option in a list.

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
```

**Parameters**:
- `actual: str` - **Required**. Text to test. Must be 3-10000 chars.
- `expected_list: list[str]` - **Required**. Non-empty list of expected texts. Each item must be 3-10000 chars.
- `threshold: float | None` - **Optional**. Similarity threshold (0.0-1.0). Defaults to config value (0.85).

**Return**: `None`

**Exceptions**:
- `AssertionError`: No match in list above threshold
  - Message format: Shows similarity score for each list item
  - Sorted by score (highest first) for readability
- `ValueError`: Empty list or invalid text lengths
  - Message: "expected_list must be non-empty"
- `RuntimeError`: Model load failure

**Behavior**:
- **Matching Strategy**: Short-circuit on first success (optimization)
- **Error Reporting**: Full scores for all options (debugging)
- **Performance Target**: <5s for 100-item list (per spec US3-4)

**Contract Stability**: Same as `assert_semantically_similar`

---

## Pytest Plugin Hooks

### pytest_configure

**Signature**:
```python
def pytest_configure(config: pytest.Config) -> None:
    """
    Pytest hook called after command line options parsed.

    Responsibilities:
    - Load and validate configuration from pytest.ini
    - Initialize session-scoped embedding manager (lazy)
    - Fail fast if configuration invalid

    Args:
        config: Pytest configuration object

    Raises:
        pytest.UsageError: If configuration invalid (threshold out of range,
            cache directory not writable, invalid model name format)
    """
```

**Configuration Loaded**:
- `semantic_assert_threshold` (float, default 0.85)
- `semantic_assert_model` (str, default "all-MiniLM-L6-v2")
- `semantic_assert_cache` (bool, default true)
- `semantic_assert_cache_dir` (str, default ".pytest-semantic-cache/")
- `semantic_assert_max_length` (int, default 10000)

**Validation**:
- Threshold: Must be 0.0 ≤ threshold ≤ 1.0
- Model: Must be non-empty string
- Cache dir: Must be writable or "memory"
- Max length: Must be positive integer

---

### pytest_addoption

**Signature**:
```python
def pytest_addoption(parser: pytest.Parser) -> None:
    """
    Pytest hook to register configuration options.

    Registers ini options for semantic assertion configuration.

    Args:
        parser: Pytest argument parser
    """
```

**Registered Options**:
```python
parser.addini(
    "semantic_assert_threshold",
    type="string",
    default="0.85",
    help="Default similarity threshold (0.0-1.0)",
)
# ... (other options)
```

---

## Configuration Schema

**File**: `pytest.ini` or `pyproject.toml`

**Format** (pytest.ini):
```ini
[pytest]
semantic_assert_threshold = 0.85
semantic_assert_model = all-MiniLM-L6-v2
semantic_assert_cache = true
semantic_assert_cache_dir = .pytest-semantic-cache/
semantic_assert_max_length = 10000
```

**Format** (pyproject.toml):
```toml
[tool.pytest.ini_options]
semantic_assert_threshold = 0.85
semantic_assert_model = "all-MiniLM-L6-v2"
semantic_assert_cache = true
semantic_assert_cache_dir = ".pytest-semantic-cache/"
semantic_assert_max_length = 10000
```

**Option Definitions**:

| Option | Type | Default | Valid Range | Description |
|--------|------|---------|-------------|-------------|
| `semantic_assert_threshold` | float | 0.85 | 0.0 to 1.0 | Default similarity threshold |
| `semantic_assert_model` | string | "all-MiniLM-L6-v2" | Any valid ST model | Embedding model identifier |
| `semantic_assert_cache` | bool | true | true/false | Enable embedding caching |
| `semantic_assert_cache_dir` | string | ".pytest-semantic-cache/" | Path or "memory" | Cache storage location |
| `semantic_assert_max_length` | int | 10000 | > 0 | Maximum text length (chars) |

---

## Exception Hierarchy

```python
# Built-in exceptions used
AssertionError          # Test failures (similarity below threshold)
ValueError              # Invalid inputs (empty text, out of bounds)
RuntimeError            # System failures (model load)
```

**Error Message Contracts**:

**AssertionError** (similarity failure):
```
Format: Multi-line structured message

Line 1: "Semantic similarity too low"
Line 2: (blank)
Line 3: Expected (semantically): "{expected}"
Line 4: Actual: "{actual}"
Line 5: Similarity Score: {score:.2f} (threshold: {threshold})
Line 6: (blank)
Line 7: Suggestion: {contextual_suggestion}
```

**ValueError** (text too short):
```
"Cannot compute semantic similarity for empty or very short text - minimum 3 characters required"
```

**ValueError** (text too long):
```
"Text exceeds maximum length: {actual_length} characters (limit: {max_length})"
```

**RuntimeError** (model load failure):
```
"Failed to load embedding model '{model_name}' after 3 attempts.

Troubleshooting:
- Check network connectivity
- Verify model name in pytest.ini
- Check disk space (~100MB required)
- Try manual download: huggingface-cli download sentence-transformers/{model_name}"
```

---

## Type Annotations

**All public functions MUST include**:
- Parameter type hints
- Return type hints
- Docstring with Args, Returns, Raises sections

**Example**:
```python
def assert_semantically_similar(
    actual: str,
    expected: str,
    threshold: float | None = None,
) -> None:
    ...
```

**Type Checking**:
- mypy strict mode compliance required
- No `# type: ignore` comments in public API

---

## Versioning & Stability Guarantees

**Pre-1.0** (0.x.y):
- API may change in MINOR versions (0.x.0)
- Deprecation warnings for 1 MINOR version before removal
- PATCH versions (0.1.x) safe to upgrade

**Post-1.0** (1.x.y):
- API stable - breaking changes ONLY in MAJOR versions
- New features in MINOR versions (backwards compatible)
- Bug fixes in PATCH versions
- Deprecation policy: Minimum 1 MINOR version notice

---

## Contract Testing

**Tests Required**:
- Function signature stability (detect parameter changes)
- Return type consistency
- Exception type and message format
- Configuration option availability
- Type annotation completeness

**Contract Test Location**: `tests/contract/test_public_api.py`

**Example Contract Test**:
```python
def test_assert_semantically_similar_signature():
    """Ensure function signature remains stable."""
    import inspect
    from pytest_semantic_assert import assert_semantically_similar

    sig = inspect.signature(assert_semantically_similar)
    params = list(sig.parameters.keys())

    assert params == ["actual", "expected", "threshold"]
    assert sig.parameters["actual"].annotation == str
    assert sig.parameters["expected"].annotation == str
    assert sig.parameters["threshold"].annotation == float | None
    assert sig.return_annotation == None
```

---

## Breaking Change Policy

**Requires MAJOR version bump**:
- Remove or rename public functions
- Change function signatures (add required param, remove param, reorder)
- Change exception types raised
- Remove configuration options
- Change default behavior (threshold, caching, model)

**Allowed in MINOR version**:
- Add new public functions
- Add optional parameters (at end, with defaults)
- Add new configuration options
- Improve error messages (format stable)
- Performance improvements

**Allowed in PATCH version**:
- Bug fixes maintaining existing behavior
- Documentation updates
- Internal refactoring (no API changes)

