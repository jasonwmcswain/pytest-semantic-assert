# Quickstart Guide: pytest-semantic-assert

**Get started with semantic assertions for LLM testing in under 2 minutes**

---

## Installation

```bash
pip install pytest-semantic-assert
```

**First-time setup**: The embedding model (~80MB) will download automatically on first use.

---

## Basic Usage

### 1. Write Your First Semantic Assertion

Create a test file `test_chatbot.py`:

```python
from pytest_semantic_assert import assert_semantically_similar

def test_chatbot_greeting():
    """Test that chatbot responds with a greeting."""
    # Your LLM/chatbot code
    response = my_chatbot.ask("Hello")

    # Semantic assertion - passes for any greeting-like response
    assert_semantically_similar(
        response,
        "Hello! How can I help you?",
        threshold=0.85
    )
```

### 2. Run Your Tests

```bash
pytest test_chatbot.py
```

**What happens**:
- ✅ First run: Downloads model (~30 seconds), runs test
- ✅ Subsequent runs: Uses cached model (<1 second)

### 3. See It Pass

Your test **passes** even if the chatbot responds with variations like:
- "Hi there!"
- "Greetings! How may I assist you?"
- "Hello, what can I do for you today?"

All are semantically similar to the expected greeting!

---

## Common Patterns

### Pattern 1: Test Against Multiple Acceptable Responses

```python
from pytest_semantic_assert import assert_semantically_similar_to_any

def test_chatbot_farewell():
    """Test chatbot farewell accepts multiple phrasings."""
    response = my_chatbot.ask("Goodbye")

    # Passes if response matches ANY of these semantically
    assert_semantically_similar_to_any(
        response,
        [
            "Goodbye!",
            "See you later!",
            "Have a great day!",
            "Farewell!"
        ],
        threshold=0.80
    )
```

### Pattern 2: Adjust Threshold for Strictness

```python
def test_strict_response():
    """Require very close semantic match."""
    response = generate_summary(article)

    # Higher threshold = stricter matching
    assert_semantically_similar(
        response,
        "Article discusses climate change impacts.",
        threshold=0.95  # Very strict
    )

def test_loose_response():
    """Allow broader semantic match."""
    response = generate_keywords(article)

    # Lower threshold = more lenient
    assert_semantically_similar(
        response,
        "environment, climate, weather",
        threshold=0.70  # More lenient
    )
```

### Pattern 3: Project-Wide Configuration

Create `pytest.ini` in your project root:

```ini
[pytest]
semantic_assert_threshold = 0.85
semantic_assert_model = all-MiniLM-L6-v2
semantic_assert_cache = true
semantic_assert_cache_dir = .pytest-semantic-cache/
```

Now all assertions use these defaults:

```python
def test_with_defaults():
    """Uses threshold=0.85 from pytest.ini."""
    response = my_function()

    # No need to specify threshold - uses 0.85 from config
    assert_semantically_similar(response, "Expected output")
```

---

## Understanding Failures

When an assertion fails, you get detailed, actionable feedback:

```python
def test_failure_example():
    assert_semantically_similar("Hello", "Goodbye", threshold=0.85)
```

**Output**:
```
AssertionError: Semantic similarity too low

Expected (semantically): "Goodbye"
Actual: "Hello"
Similarity Score: 0.23 (threshold: 0.85)

Suggestion: These texts are semantically unrelated (similarity < 0.3).
Verify your expected text matches the intended meaning.
```

**Helpful suggestions** based on similarity score:
- `< 0.3`: Texts are unrelated
- `0.3 - 0.6`: Somewhat related but different meaning
- `0.6 - threshold`: Nearly similar - consider lowering threshold

---

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `semantic_assert_threshold` | 0.85 | Default similarity threshold (0.0-1.0) |
| `semantic_assert_model` | all-MiniLM-L6-v2 | Embedding model to use |
| `semantic_assert_cache` | true | Enable embedding caching |
| `semantic_assert_cache_dir` | .pytest-semantic-cache/ | Where to store cache |
| `semantic_assert_max_length` | 10000 | Maximum text length (chars) |

### Configuration Locations

**Option 1: pytest.ini**
```ini
[pytest]
semantic_assert_threshold = 0.90
```

**Option 2: pyproject.toml**
```toml
[tool.pytest.ini_options]
semantic_assert_threshold = 0.90
```

**Option 3: Per-assertion override**
```python
# Explicit threshold overrides config
assert_semantically_similar(actual, expected, threshold=0.95)
```

**Priority**: Explicit parameter > pytest.ini > default

---

## Performance Tips

### 1. Enable Caching (Default)

Embeddings are cached automatically for fast repeated comparisons:

- **First comparison**: ~150ms (compute embedding)
- **Cached comparison**: ~2ms (read from cache)

**Recommendation**: Add `.pytest-semantic-cache/` to `.gitignore` but commit in CI for team sharing.

### 2. Parallel Testing

Works seamlessly with `pytest-xdist`:

```bash
pytest -n auto  # Run tests in parallel
```

Cache writes are synchronized with file locking - no race conditions!

### 3. CI/CD Optimization

**Cache embeddings across CI runs**:

```yaml
# GitHub Actions example
- name: Cache embeddings
  uses: actions/cache@v3
  with:
    path: .pytest-semantic-cache/
    key: semantic-cache-${{ hashFiles('tests/**/*.py') }}
```

---

## Troubleshooting

### Model Won't Download

**Error**: "Failed to load embedding model after 3 attempts"

**Solutions**:
1. Check network connectivity
2. Verify model name in `pytest.ini`
3. Check disk space (~100MB required)
4. Manual download:
   ```bash
   pip install sentence-transformers
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```

### Text Too Short

**Error**: "Cannot compute semantic similarity for empty or very short text"

**Solution**: Ensure text is at least 3 characters long. Check your test fixtures.

### Text Too Long

**Error**: "Text exceeds maximum length: 15000 characters (limit: 10000)"

**Solutions**:
1. Increase limit in `pytest.ini`:
   ```ini
   semantic_assert_max_length = 20000
   ```
2. Test on text summary instead of full output

### Cache Directory Not Writable

**Error**: "Permission denied: .pytest-semantic-cache/"

**Solution**: Check directory permissions or use alternative cache location:
```ini
semantic_assert_cache_dir = ~/.cache/pytest-semantic-assert/
```

---

## Next Steps

### Learn More
- **Full Documentation**: [Link to docs]
- **API Reference**: [Link to API docs]
- **Examples**: [Link to examples repo]

### Advanced Features
- Custom embedding models
- Debugging mode (`--semantic-assert-debug`)
- Integration with CI/CD pipelines
- Performance tuning for large test suites

### Get Help
- **GitHub Issues**: [Link to issues]
- **Discussions**: [Link to discussions]
- **Stack Overflow**: Tag `pytest-semantic-assert`

---

## Quick Reference

```python
# Basic assertion
assert_semantically_similar(actual, expected, threshold=0.85)

# Multiple expected values
assert_semantically_similar_to_any(actual, [exp1, exp2, exp3], threshold=0.80)

# With config defaults
assert_semantically_similar(actual, expected)  # Uses pytest.ini threshold
```

**Threshold Guide**:
- `0.95+`: Very strict (near-identical meaning)
- `0.85-0.94`: Strict (default, good for most cases)
- `0.70-0.84`: Lenient (broader semantic match)
- `< 0.70`: Very lenient (loosely related)

**Performance Targets** (with caching):
- ✅ <50ms per comparison (cached)
- ✅ <200ms per comparison (uncached)
- ✅ <5s for 100-item list comparison

---

**You're ready to start testing LLMs semantically!** 🚀

Replace brittle string matching with robust semantic assertions and never worry about wording variations again.

