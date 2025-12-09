# Testing Guide

Comprehensive guide to testing pytest-semantic-assert.

## 🧪 Test Suite Overview

Total: **84 tests** across 5 categories

### Test Categories

| Category | Count | Purpose |
|----------|-------|---------|
| **Unit** | 50 | Individual components in isolation |
| **Integration** | 13 | Component interactions with real implementations |
| **Contract** | 6 | Public API stability |
| **E2E** | 15 | Complete user scenarios |
| **Examples** | 11 | Real-world usage patterns (not counted in main suite) |

## 🏃 Running Tests

### Quick Commands

```bash
# All tests
make test
# or
pytest tests/ examples/

# With coverage
make coverage-combined
# or
pytest tests/ --cov=pytest_semantic_assert --cov-report=html

# Specific categories
make unit-test          # Unit tests only
make integration-test   # Integration tests
make contract-test      # Contract tests
make e2e-test          # End-to-end tests
```

### Specific Test Files

```bash
# Single file
pytest tests/unit/test_similarity.py -v

# Single test
pytest tests/unit/test_similarity.py::TestCosineSimilarity::test_identical_vectors -v

# Pattern matching
pytest tests/ -k "similarity" -v
```

## 📝 Unit Tests (50 tests)

**Location**: `tests/unit/`

### test_similarity.py (10 tests)
Tests cosine similarity computation:
- Identical vectors
- Orthogonal vectors
- Similar vectors
- Different dimensions (error case)
- Zero vectors (error case)
- High-dimensional vectors (384-dim)

```bash
pytest tests/unit/test_similarity.py -v
```

### test_config.py (14 tests)
Tests configuration loading and validation:
- Default values
- Custom values
- Invalid threshold (out of range)
- Invalid max_length (zero/negative)
- Empty model name
- Boundary values

```bash
pytest tests/unit/test_config.py -v
```

### test_cache.py (14 tests)
Tests caching system:
- Memory mode set/get
- Disk mode set/get
- Persistence across instances
- Cache key generation
- File locking
- Corrupted file handling
- High-dimensional embeddings (384-dim)

```bash
pytest tests/unit/test_cache.py -v
```

### test_embeddings.py (12 tests)
Tests embedding manager (with mocked model):
- Lazy loading
- Model loaded once
- Text too short/long validation
- Cache integration
- Retry logic (with failures)
- Model load exhausted retries
- Custom model name

```bash
pytest tests/unit/test_embeddings.py -v
```

## 🔌 Integration Tests (13 tests)

**Location**: `tests/integration/`

**Purpose**: Test component interactions with real implementations (not mocked)

### test_assertions.py (7 tests)
Tests assertion functions with real embedding model and similarity calculations:
- Basic assertion pass case (similar texts)
- Basic assertion fail case (different texts with error message validation)
- Explicit threshold override
- Embedding caching across multiple assertions
- Boundary threshold values (0.0 and 1.0)
- Unicode and special characters handling
- Error message formatting through full stack

```bash
pytest tests/integration/test_assertions.py -v
```

### test_configuration.py (6 tests)
Tests pytest.ini configuration integration:
- Threshold override from pytest.ini
- Model selection from pytest.ini
- Cache settings from pytest.ini
- Explicit parameter overriding pytest.ini default
- Max length setting enforcement
- Multiple settings working together

```bash
pytest tests/integration/test_configuration.py -v
```

**Note**: Integration tests use real embedding models (not mocked), so they take longer to run than unit tests but verify actual behavior.

## 🔗 Contract Tests (6 tests)

**Location**: `tests/contract/test_public_api.py`

**Purpose**: Ensure public API stability (prevent breaking changes)

Tests:
- Function signatures unchanged
- Type annotations preserved
- Return types consistent
- __version__ exists
- Docstrings present
- Public exports complete

```bash
pytest tests/contract/ -v
```

## 🎯 E2E Tests (15 tests)

**Location**: `tests/e2e/test_user_stories.py`

**Purpose**: Validate complete user scenarios with real model

### User Story 1: Basic Assertions
- Semantically similar texts pass
- Different texts fail with score
- Custom threshold respected
- Failure message shows all fields

### User Story 3: Multi-Value
- Matches first option
- Matches middle option
- No match shows all scores
- Large list performance (<5s for 100+ items)
- Empty list raises error

### Edge Cases
- Text too short (<3 chars)
- Empty string
- Threshold out of range
- Threshold boundary values (0.0, 1.0)

```bash
pytest tests/e2e/ -v
```

## 📚 Example Tests (11 tests)

**Location**: `examples/`

**Purpose**: Demonstrate real-world usage patterns

Files:
- `demo_simple.py` - Simplest examples (2 tests)
- `quickstart.py` - Quick start guide (5 tests)
- `test_example_chatbot.py` - Realistic scenarios (11 tests)

```bash
pytest examples/ -v
```

## 🎨 Writing Tests

### Unit Test Pattern

```python
import pytest
from pytest_semantic_assert.similarity import cosine_similarity

class TestSimilarity:
    def test_specific_behavior(self) -> None:
        """Test description."""
        # Arrange
        vec_a = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        vec_b = np.array([1.0, 2.0, 3.0], dtype=np.float32)

        # Act
        result = cosine_similarity(vec_a, vec_b)

        # Assert
        assert abs(result - 1.0) < 1e-6
```

### E2E Test Pattern

```python
def test_user_scenario(self) -> None:
    """Test complete user workflow."""
    # Use real function
    assert_semantically_similar(
        "Hello! How can I help?",
        "Hi! What can I do for you?",
        threshold=0.60
    )
```

### Mocking in Unit Tests

```python
from unittest.mock import MagicMock, patch

@patch("pytest_semantic_assert.embeddings.SentenceTransformer")
def test_with_mock(self, mock_st: MagicMock) -> None:
    """Test with mocked model."""
    # Setup mock
    mock_model = MagicMock()
    mock_model.encode.return_value = np.random.rand(384).astype(np.float32)
    mock_st.return_value = mock_model

    # Test
    manager = EmbeddingManager(config)
    embedding = manager.get_embedding("test text")

    # Verify
    mock_model.encode.assert_called_once()
```

## 📊 Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Overall | ≥60% | 67% ✅ |
| Core Logic | ≥80% | 75% ✅ |
| Public API | 100% | 100% ✅ |

### Viewing Coverage

```bash
# Generate HTML report
pytest tests/ --cov=pytest_semantic_assert --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## 🐛 Debugging Tests

### Run with verbose output
```bash
pytest tests/ -vv
```

### Drop into debugger on failure
```bash
pytest tests/ --pdb
```

### Show print statements
```bash
pytest tests/ -s
```

### Run only failed tests
```bash
pytest tests/ --lf
```

### Run specific test with full output
```bash
pytest tests/unit/test_similarity.py::TestCosineSimilarity::test_identical_vectors -vv -s
```

## 🚀 Performance Testing

### Measure test execution time
```bash
pytest tests/ --durations=10
```

### Profile slow tests
```bash
pytest tests/ --profile
```

## 🔄 Continuous Integration

Tests run automatically on:
- Every push
- Every pull request
- Python 3.9, 3.10, 3.11, 3.12
- Multiple pytest versions

### Local Multi-Version Testing

```bash
# Using tox
tox

# Specific environment
tox -e py39-pytest70
```

## ✅ Pre-Commit Checklist

Before committing:

```bash
# 1. Format code
make format

# 2. Lint
make ruff-check

# 3. Type check
mypy src/

# 4. Run tests
make test

# 5. Check coverage
make coverage-combined

# Or run all at once
make validate
```

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [pytest-cov](https://pytest-cov.readthedocs.io/)


