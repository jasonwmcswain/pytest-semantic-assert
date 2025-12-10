# pytest-semantic-assert

**Stop fighting flaky LLM tests. Assert on meaning, not exact strings.**

A pytest plugin for semantic assertions of LLM outputs using embedding-based similarity comparison. Test what your LLM _means_, not what it _says_.

[![PyPI version](https://badge.fury.io/py/pytest-semantic-assert.svg)](https://badge.fury.io/py/pytest-semantic-assert)
[![Python](https://img.shields.io/pypi/pyversions/pytest-semantic-assert.svg)](https://pypi.org/project/pytest-semantic-assert/)
[![pytest](https://img.shields.io/badge/pytest-7.0+-blue.svg)](https://docs.pytest.org/en/stable/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage](https://img.shields.io/badge/coverage-94.85%25-brightgreen.svg)](https://github.com/pytest-semantic-assert/pytest-semantic-assert)
[![Async](https://img.shields.io/badge/async-supported-blue.svg)](https://github.com/pytest-semantic-assert/pytest-semantic-assert)

---

## Table of Contents

- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [Why pytest-semantic-assert?](#why-pytest-semantic-assert)
- [Features](#features)
- [Installation](#installation)
- [Dependencies](#dependencies)
- [Quick Start](#quick-start)
- [Configuration Options](#configuration-options)
- [Understanding Failures](#understanding-failures)
- [How It Works](#how-it-works)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)
- [Use Cases & Examples](#use-cases--examples)
- [FAQ](#faq)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Similar Projects & Alternatives](#similar-projects--alternatives)
- [Roadmap](#roadmap)
- [Security & Privacy](#security--privacy)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

---

## The Problem

Traditional string assertions are brittle when testing LLM outputs:

```python
# ❌ This fails even though the meaning is identical
response = chatbot.ask("Hello")
assert response == "Hi! How can I help you?"  # FAILS if response is "Hello! What can I do for you?"
```

## The Solution

Semantic assertions test meaning, not exact wording:

```python
# ✅ This passes for any semantically similar greeting
from pytest_semantic_assert import assert_semantically_similar

response = chatbot.ask("Hello")
assert_semantically_similar(response, "Hi! How can I help you?", threshold=0.85)
# PASSES for: "Hello!", "Greetings! How may I assist?", "Hi there! What can I do for you?"
```

---

## Why pytest-semantic-assert?

**Perfect for**:
- 🤖 Testing LLM/AI applications (ChatGPT, Claude, Llama, etc.)
- 💬 Chatbot response validation
- 📝 Natural language generation testing
- 🔄 Translation and paraphrasing systems
- 🎯 Any scenario where meaning matters more than exact wording

## Features

- 🎯 **Semantic Assertions**: Compare texts by meaning using state-of-the-art embeddings
- ⚡ **Fast**: <50ms per comparison (cached), <200ms uncached
- 🔧 **Zero Config**: Works out of the box with sensible defaults
- 🎨 **Fully Configurable**: Adjust thresholds, models, and cache via pytest.ini/pyproject.toml
- 🔒 **Parallel Safe**: Works with pytest-xdist (file-based locking for multi-process testing)
- 📊 **Helpful Errors**: Detailed failure messages with similarity scores and suggestions
- 🐍 **Python 3.9-3.12**: Broad version support
- 🧪 **Pytest 7.0+**: Compatible with modern pytest
- ⚡ **Async/Await Support**: Native async assertions for agentic LLM testing workflows
- ✅ **Production Ready**: 94.85% test coverage, fully typed, 256 passing tests
- 🚀 **No External APIs**: Everything runs locally, no API keys or rate limits

---

## Installation

```bash
pip install pytest-semantic-assert
```

**Requirements**:
- Python 3.9 or higher
- pytest 7.0 or higher
- ~100MB disk space for the embedding model

**First-time setup**: The embedding model (~80MB) downloads automatically on first use (~30 seconds). No API keys or external services required!

---

## Dependencies

### Production Dependencies

These packages are installed automatically when you install `pytest-semantic-assert`:

| Library | Use Case |
|---------|----------|
| [pytest](https://docs.pytest.org/) ≥7.0 | Testing framework integration and plugin system |
| [sentence-transformers](https://www.sbert.net/) ≥2.2.0 | Semantic embedding generation using transformer models |
| [numpy](https://numpy.org/) ≥1.21.0 | Efficient numerical operations for similarity computations |
| [filelock](https://github.com/tox-dev/py-filelock) ≥3.0.0 | Thread-safe file locking for parallel test execution |

**Total install size**: ~500MB (including the embedding model)

### Development Dependencies

These packages are only needed if you're contributing to the project:

| Library | Use Case |
|---------|----------|
| [pytest-cov](https://pytest-cov.readthedocs.io/) | Code coverage reporting and analysis |
| [pytest-xdist](https://pytest-xdist.readthedocs.io/) | Parallel test execution across multiple CPUs |
| [pytest-asyncio](https://pytest-asyncio.readthedocs.io/) | Testing async/await functionality |
| [black](https://black.readthedocs.io/) | Code formatting and style consistency |
| [ruff](https://docs.astral.sh/ruff/) | Fast Python linter for code quality checks |
| [mypy](https://mypy.readthedocs.io/) | Static type checking and type safety validation |
| [build](https://pypa-build.readthedocs.io/) | Building distribution packages (wheel, sdist) |
| [twine](https://twine.readthedocs.io/) | Uploading packages to PyPI |

**Install development dependencies**:
```bash
pip install pytest-semantic-assert[dev]
```

---

## Quick Start

### 1. Basic Assertion

```python
from pytest_semantic_assert import assert_semantically_similar

def test_chatbot_greeting():
    """Test that chatbot responds with a greeting."""
    response = my_chatbot.ask("Hello")

    # Passes for any greeting-like response
    # "Hi there!", "Hello!", "Hey! How can I help?" all pass
    assert_semantically_similar(
        response,
        "Hello! How can I help you?",
        threshold=0.85
    )
```

**What happens**: The plugin converts both texts to embeddings and computes their cosine similarity. If similarity ≥ 0.85, the test passes.

### 1b. Async Assertion (for async LLM tests)

```python
from pytest_semantic_assert import assert_semantically_similar_async
import pytest

@pytest.mark.asyncio
async def test_async_chatbot_greeting():
    """Test async chatbot with semantic assertions."""
    response = await my_async_chatbot.ask("Hello")

    # Async version - same behavior, async/await syntax
    await assert_semantically_similar_async(
        response,
        "Hello! How can I help you?",
        threshold=0.85
    )
```

**Why async?**: Perfect for agentic LLM testing where your code is already async. The assertion runs in a thread pool to avoid blocking the event loop.

### 2. Multiple Acceptable Responses

```python
from pytest_semantic_assert import assert_semantically_similar_to_any

def test_chatbot_farewell():
    """Test chatbot says goodbye appropriately."""
    response = my_chatbot.ask("Goodbye")

    # Passes if response matches ANY of these
    assert_semantically_similar_to_any(
        response,
        ["Goodbye!", "See you later!", "Farewell!", "Take care!"],
        threshold=0.80
    )
```

**What happens**: Compares `response` against each option, passing if ANY similarity ≥ 0.80.

**Async version**: Use `assert_semantically_similar_to_any_async()` for async tests.

### 3. Using Without Configuration

No configuration needed! Just import and use:

```python
# Works immediately with sensible defaults
from pytest_semantic_assert import assert_semantically_similar

def test_without_config():
    assert_semantically_similar(
        "The cat sat on the mat",
        "A feline rested on the rug",
        threshold=0.70  # Explicit threshold
    )
```

### 4. Configure Project-Wide Defaults

**Option A**: Create `pytest.ini` in your project root:

```ini
[pytest]
semantic_assert_threshold = 0.85
semantic_assert_model = all-MiniLM-L6-v2
semantic_assert_cache = true
semantic_assert_cache_dir = .pytest-semantic-cache/
semantic_assert_max_length = 10000
```

**Option B**: Or use `pyproject.toml`:

```toml
[tool.pytest.ini_options]
semantic_assert_threshold = 0.85
semantic_assert_model = "all-MiniLM-L6-v2"
semantic_assert_cache = true
semantic_assert_cache_dir = ".pytest-semantic-cache/"
semantic_assert_max_length = 10000
```

**Pro Tip**: Configuration is optional. Omit settings to use defaults, or override per-assertion.

---

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `semantic_assert_threshold` | `0.85` | Similarity threshold (0.0-1.0). Higher = stricter matching |
| `semantic_assert_model` | `all-MiniLM-L6-v2` | HuggingFace model identifier for embeddings |
| `semantic_assert_cache` | `true` | Enable disk-based embedding caching for performance |
| `semantic_assert_cache_dir` | `.pytest-semantic-cache/` | Directory for cached embeddings |
| `semantic_assert_max_length` | `10000` | Maximum text length in characters (prevents memory issues) |

**Note**: All options can be overridden per-assertion via function parameters.

---

## Understanding Failures

When assertions fail, you get detailed, actionable feedback:

```python
def test_example():
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

---

## How It Works

1. **Embedding Model**: Uses `all-MiniLM-L6-v2` from [sentence-transformers](https://www.sbert.net/) for semantic encoding
2. **Similarity Metric**: Computes cosine similarity between 384-dimensional embeddings
3. **Intelligent Caching**: Stores embeddings on disk for fast repeated comparisons
4. **Configurable Thresholds**: Set similarity threshold (0.0-1.0, default 0.85) per-assertion or globally
5. **Thread-Safe**: File-based locking ensures safe parallel test execution

**Performance Benchmarks**:
- ✅ <50ms per comparison (cached) - instant feedback
- ✅ <200ms per comparison (uncached) - still very fast
- ✅ <5s for 100-item list comparison - efficient batch testing
- ✅ <30s installation + first test - quick onboarding

**Quality Metrics**:
- ✅ 94.85% test coverage - thoroughly tested
- ✅ 256 passing tests - comprehensive test suite
- ✅ Fully typed - excellent IDE support
- ✅ Async/await support - native async assertions for LLM testing
- ✅ Zero external APIs - just pytest and transformers

---

## Advanced Usage

### Custom Thresholds

```python
# Strict matching (very similar required)
assert_semantically_similar(text, expected, threshold=0.95)

# Lenient matching (broader semantic match)
assert_semantically_similar(text, expected, threshold=0.70)
```

### Parallel Testing

Works seamlessly with pytest-xdist for faster test execution:

```bash
# Run tests in parallel across all CPU cores
pytest -n auto

# Run tests across 4 workers
pytest -n 4
```

The plugin handles file locking automatically, ensuring safe parallel execution.

### CI/CD Optimization

Speed up CI runs by caching embeddings across builds:

#### GitHub Actions

```yaml
- name: Cache semantic embeddings
  uses: actions/cache@v3
  with:
    path: .pytest-semantic-cache/
    key: semantic-cache-${{ hashFiles('tests/**/*.py') }}
    restore-keys: |
      semantic-cache-

- name: Run tests
  run: pytest -n auto
```

#### GitLab CI

```yaml
cache:
  paths:
    - .pytest-semantic-cache/

test:
  script:
    - pytest -n auto
```

### Docker Support

Include the cache in your Dockerfile for faster builds:

```dockerfile
# Copy cache (optional, for faster builds)
COPY .pytest-semantic-cache/ /app/.pytest-semantic-cache/

# Or mount as volume for development
# docker run -v ./.pytest-semantic-cache:/app/.pytest-semantic-cache
```

---

## API Reference

### Synchronous Assertions

#### `assert_semantically_similar(actual, expected, threshold=None)`

Assert that two texts are semantically similar.

**Parameters**:
- `actual` (str): Text to test (3-10000 chars)
- `expected` (str): Expected text for comparison (3-10000 chars)
- `threshold` (float | None): Similarity threshold (0.0-1.0). Defaults to config value (0.85)

**Raises**:
- `AssertionError`: Similarity below threshold
- `ValueError`: Invalid text (too short/long)
- `RuntimeError`: Model load failure

#### `assert_semantically_similar_to_any(actual, expected_list, threshold=None)`

Assert that text is semantically similar to ANY option in a list.

**Parameters**:
- `actual` (str): Text to test (3-10000 chars)
- `expected_list` (list[str]): Non-empty list of expected texts
- `threshold` (float | None): Similarity threshold (0.0-1.0). Defaults to config value (0.85)

**Raises**:
- `AssertionError`: No match in list
- `ValueError`: Empty list or invalid text
- `RuntimeError`: Model load failure

### Async Assertions

#### `assert_semantically_similar_async(actual, expected, threshold=None)`

Async version of `assert_semantically_similar()` for async test contexts.

**Parameters**: Same as synchronous version

**Raises**: Same as synchronous version

**Usage**:
```python
@pytest.mark.asyncio
async def test_async_llm():
    response = await llm.generate("Hello")
    await assert_semantically_similar_async(response, "Hi!", threshold=0.85)
```

**Note**: Requires `pytest-asyncio`. Runs assertion in thread pool to avoid blocking event loop.

#### `assert_semantically_similar_to_any_async(actual, expected_list, threshold=None)`

Async version of `assert_semantically_similar_to_any()` for async test contexts.

**Parameters**: Same as synchronous version

**Raises**: Same as synchronous version

**Usage**:
```python
@pytest.mark.asyncio
async def test_async_llm_multi():
    response = await llm.generate("Goodbye")
    await assert_semantically_similar_to_any_async(
        response,
        ["Bye!", "Farewell!", "See you!"],
        threshold=0.80
    )
```

**Parallel Testing**: Can be used with `asyncio.gather()` for batch assertions:
```python
await asyncio.gather(
    assert_semantically_similar_async(response1, expected1),
    assert_semantically_similar_async(response2, expected2),
)
```

---

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/your-org/pytest-semantic-assert.git
cd pytest-semantic-assert

# Create virtual environment
make venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in development mode
pip install -e ".[dev]"
```

### Run Tests

```bash
# All tests
make test

# Unit tests only
make unit-test

# With coverage
make coverage-combined

# Validate all (format, lint, type check, test)
make validate
```

### Code Quality

```bash
# Format code
make format

# Lint
make ruff-check

# Type check
make mypy
```

---

## Troubleshooting

### Model Won't Download

**Error**: `Failed to load embedding model 'all-MiniLM-L6-v2' after 3 attempts`

**Solutions**:
1. **Check network connectivity** - Model downloads from HuggingFace
2. **Verify model name** in `pytest.ini` configuration
3. **Ensure disk space** - ~100MB required for model files
4. **Try manual download**:
   ```bash
   pip install sentence-transformers
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```
5. **Check firewall/proxy** - Ensure HuggingFace Hub is accessible
6. **Use pre-downloaded model** - Set `HF_HOME` environment variable to cached model location

### Text Too Short/Long

**Error**: `Cannot compute semantic similarity for empty or very short text - minimum 3 characters required`

**Solutions**:
- Ensure text is between 3-10000 characters (default)
- Adjust `semantic_assert_max_length` in config if needed:
  ```ini
  [pytest]
  semantic_assert_max_length = 50000  # For longer texts
  ```

### Threshold Too Strict

**Issue**: Tests failing with `Similarity Score: 0.78 (threshold: 0.85)`

**Solutions**:
- Lower the threshold for more lenient matching:
  ```python
  assert_semantically_similar(actual, expected, threshold=0.70)
  ```
- Or adjust global default in `pytest.ini`:
  ```ini
  [pytest]
  semantic_assert_threshold = 0.75
  ```

**Threshold Guidelines**:
- `0.95-1.0`: Nearly identical (very strict)
- `0.85-0.95`: Strong semantic similarity (recommended default)
- `0.70-0.85`: Moderate semantic similarity (lenient)
- `0.50-0.70`: Weak semantic similarity (very lenient)
- `<0.50`: Barely related (too lenient for most use cases)

### Cache Issues

**Issue**: Cache growing too large

**Solution**: Clear the cache directory:
```bash
rm -rf .pytest-semantic-cache/
```

Or exclude from version control (already in `.gitignore`):
```gitignore
.pytest-semantic-cache/
```

### ImportError or Module Not Found

**Error**: `No module named 'pytest_semantic_assert'`

**Solutions**:
1. Ensure plugin is installed: `pip list | grep pytest-semantic-assert`
2. Reinstall: `pip install --force-reinstall pytest-semantic-assert`
3. Check pytest discovers the plugin: `pytest --trace-config | grep semantic`

---

## Documentation

📚 **Comprehensive documentation available in [docs/](docs/)**

- **[Development Guide](docs/development/DEVELOPMENT.md)** - Setup, testing, and contributing
- **[Architecture](docs/development/ARCHITECTURE.md)** - Technical design and decisions
- **[Testing Guide](docs/development/TESTING.md)** - Complete testing documentation
- **[API Specification](docs/specification/001-semantic-assert-mvp/contracts/api.md)** - Public API contract

---

## Use Cases & Examples

### Testing Chatbots

```python
def test_chatbot_handles_greetings():
    """Test chatbot responds appropriately to greetings."""
    response = chatbot.send("Good morning")
    assert_semantically_similar(
        response,
        "Hello! How can I assist you today?",
        threshold=0.80
    )
```

### Testing Content Generation

```python
def test_summary_generation():
    """Test article summarization maintains key points."""
    article = "Long article text..."
    summary = summarizer.generate(article)

    expected_summary = "Expected summary capturing main points..."
    assert_semantically_similar(summary, expected_summary, threshold=0.85)
```

### Testing Translation

```python
def test_translation_quality():
    """Test translation preserves meaning."""
    original = "The weather is beautiful today"
    translated = translator.translate(original, target="es")

    # Back-translate and compare
    back_translated = translator.translate(translated, target="en")
    assert_semantically_similar(original, back_translated, threshold=0.90)
```

### Testing Multiple Valid Responses

```python
def test_farewell_responses():
    """Test chatbot can say goodbye in various ways."""
    response = chatbot.send("I have to go")

    # Any of these farewells should be acceptable
    assert_semantically_similar_to_any(
        response,
        [
            "Goodbye! Have a great day!",
            "See you later!",
            "Take care!",
            "Bye! Come back soon!"
        ],
        threshold=0.75
    )
```

### Testing Async Agentic Workflows

```python
import pytest
from pytest_semantic_assert import assert_semantically_similar_async

@pytest.mark.asyncio
async def test_agent_conversation_flow():
    """Test multi-turn agent conversation."""
    agent = MyLLMAgent()

    # Turn 1: Greeting
    response1 = await agent.process("Hello")
    await assert_semantically_similar_async(
        response1,
        "Hi! How can I help you today?",
        threshold=0.80
    )

    # Turn 2: Request
    response2 = await agent.process("Tell me about the weather")
    await assert_semantically_similar_async(
        response2,
        "I'll check the weather forecast for you",
        threshold=0.75
    )

@pytest.mark.asyncio
async def test_parallel_agent_responses():
    """Test multiple agent responses in parallel."""
    import asyncio

    agent = MyLLMAgent()

    # Process multiple queries in parallel
    responses = await asyncio.gather(
        agent.process("Hello"),
        agent.process("Goodbye"),
        agent.process("Thank you")
    )

    # Verify all responses in parallel
    await asyncio.gather(
        assert_semantically_similar_async(responses[0], "Hi there!", threshold=0.75),
        assert_semantically_similar_async(responses[1], "Bye!", threshold=0.75),
        assert_semantically_similar_async(responses[2], "You're welcome!", threshold=0.75),
    )
```

## FAQ

### Q: How accurate is semantic similarity?

**A**: The default model (`all-MiniLM-L6-v2`) achieves ~80-85% correlation with human similarity judgments on standard benchmarks. For most LLM testing scenarios, this is more than sufficient.

### Q: Can I use a different embedding model?

**A**: Yes! Set `semantic_assert_model` in your config to any [sentence-transformers](https://www.sbert.net/docs/pretrained_models.html) model:

```ini
[pytest]
semantic_assert_model = paraphrase-multilingual-MiniLM-L12-v2  # For multilingual support
```

### Q: Does this work offline?

**A**: Yes, after the initial model download. The model is cached locally and all processing happens on your machine.

### Q: How does this compare to exact string matching?

**A**: Exact matching: `"Hello" != "Hi"` ❌
Semantic matching: `"Hello" ≈ "Hi"` ✅ (similarity ~0.65)

### Q: What's the performance impact?

**A**: First comparison: ~200ms (uncached)
Subsequent comparisons with same text: <50ms (cached)
This is negligible for most test suites.

### Q: Is this suitable for production testing?

**A**: Absolutely! The plugin has:
- 94.85% test coverage
- 256 passing tests (including 22 async tests)
- Extensive use in LLM testing scenarios
- Thread-safe parallel execution
- Async/await support for modern LLM testing
- Deterministic behavior (same inputs = same outputs)

### Q: Can I use this for non-English texts?

**A**: Yes, but the default model is optimized for English. For other languages, use a multilingual model:

```ini
[pytest]
semantic_assert_model = paraphrase-multilingual-MiniLM-L12-v2
```

## Contributing

Contributions are welcome! We'd love your help making pytest-semantic-assert better.

**Ways to contribute**:
- 🐛 Report bugs via [GitHub Issues](https://github.com/pytest-semantic-assert/pytest-semantic-assert/issues)
- 💡 Suggest features or improvements
- 📝 Improve documentation
- 🔧 Submit pull requests

See [Development Guide](docs/development/DEVELOPMENT.md) for setup and guidelines.

### Development Setup

```bash
git clone https://github.com/jasonwmcswain/pytest-semantic-assert.git
cd pytest-semantic-assert
make venv
source venv/bin/activate
pip install -e ".[dev]"
make test
```

---

## Legal Notice & Disclaimer
This project is an independent work intended for general consumption. It does not contain any proprietary code, intellectual property, or confidential information belonging to any company.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Similar Projects & Alternatives

If pytest-semantic-assert doesn't fit your needs, consider:

- **[pytest-match](https://github.com/pytest-dev/pytest-match)** - Regex and pattern matching for pytest
- **[pytest-testmon](https://github.com/tarpas/pytest-testmon)** - Only run tests affected by code changes
- **[deepeval](https://github.com/confident-ai/deepeval)** - LLM evaluation framework with more metrics
- **Manual LLM judges** - Use GPT-4 or Claude to judge output quality

**Why choose pytest-semantic-assert?**:
- ✅ No API calls or rate limits (fully local)
- ✅ Deterministic results (same input = same output)
- ✅ Fast (<200ms even uncached)
- ✅ Works with any pytest project
- ✅ Simple, focused API

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## Roadmap

**v0.1.0 - Initial Release** ✅
- [x] Core semantic assertions
- [x] Async/await support for agentic testing
- [x] Disk-based caching
- [x] Parallel testing (pytest-xdist)

**Future Enhancements**:
- [ ] Custom embedding model support (bring your own)
- [ ] Batch assertion optimizations (process multiple comparisons simultaneously)
- [ ] Fuzzy matching with configurable edit distance
- [ ] Multi-language model auto-detection
- [ ] Embedding model auto-selection based on text type
- [ ] Integration with popular LLM testing frameworks
- [ ] Streaming assertion support for large texts

Vote on features or suggest new ones via [GitHub Issues](https://github.com/jasonwmcswain/pytest-semantic-assert/issues)!

## Security & Privacy

**pytest-semantic-assert** is designed with security and privacy in mind:

### ✅ What We Do
- **100% Local Processing**: All embeddings computed on your machine
- **No External API Calls**: After initial model download, works completely offline
- **No Data Collection**: We never send your test data anywhere
- **Open Source**: Full transparency - inspect the code yourself
- **MIT Licensed**: Use freely in commercial projects

### 🔒 Privacy Guarantees
- Your test data **never** leaves your machine
- No telemetry, analytics, or tracking
- No account creation or registration required
- Cache files stored locally in your project directory

### 📦 Dependencies
All dependencies are well-maintained, widely-used packages:
- `pytest` - Testing framework
- `sentence-transformers` - Embedding models
- `numpy` - Numerical operations
- `filelock` - File locking for parallel safety

### 🛡️ Security Best Practices
- Keep dependencies updated: `pip install --upgrade pytest-semantic-assert`
- Review the [CHANGELOG.md](CHANGELOG.md) for security updates
- Report security issues privately via GitHub Security Advisories

### ⚠️ Initial Model Download
On first use, `sentence-transformers` downloads the embedding model (~80MB) from HuggingFace Hub. This is a one-time operation. The model is cached in:
- Default: `~/.cache/huggingface/` or `~/.cache/torch/`
- Custom: Set `HF_HOME` environment variable

## Acknowledgments

- Built on [sentence-transformers](https://www.sbert.net/) by UKPLab
- Powered by [HuggingFace Transformers](https://huggingface.co/transformers/)
- Embedding model: [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- Inspired by the need for robust, maintainable LLM testing in production environments

## Support

- 📖 **Documentation**: [docs/](docs/)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/pytest-semantic-assert/pytest-semantic-assert/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/pytest-semantic-assert/pytest-semantic-assert/discussions)
- 📧 **Email**: (coming soon)

---

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

---

**Ready to start testing LLMs semantically?** 🚀

```bash
pip install pytest-semantic-assert
```

**Stop fighting flaky tests. Assert on meaning, not strings.**

---

*Made with ❤️ for the LLM testing community*
