# Research: Technology Decisions & Best Practices

**Feature**: Semantic Assertions for LLM Testing
**Date**: 2025-12-06
**Purpose**: Resolve technical unknowns and establish technology stack with rationale

---

## 1. Embedding Model Selection

### Decision: **all-MiniLM-L6-v2**

**Rationale**:
- **Size**: 80MB model (fast download, <30s target achievable)
- **Speed**: ~50ms inference on CPU for typical sentences (meets <200ms uncached target)
- **Quality**: 384-dimensional embeddings, SOTA performance on semantic similarity benchmarks
- **Multilingual**: Primarily English, but spec assumes English (per assumptions section)
- **Maintained**: Active HuggingFace model with broad adoption

**Alternatives Considered**:
- **all-mpnet-base-v2**: Better quality (768-dim) but 420MB, slower (~120ms inference) - rejected for speed/size tradeoff
- **distiluse-base-multilingual**: Multilingual support but spec scopes to English initially
- **MiniLM** chosen for optimal speed/quality balance per performance targets

**Configuration**: Model identifier configurable via `semantic_assert_model` in pytest.ini

---

## 2. Cache Serialization Strategy

### Decision: **pickle (Python built-in)**

**Rationale**:
- **Zero Dependencies**: No additional package required (aligns with minimal dependencies principle)
- **Native numpy Support**: Efficiently serializes numpy arrays (embeddings are np.ndarray)
- **Performance**: Fast serialize/deserialize (~1-2ms for typical embeddings)
- **Sufficient Security**: Cache is local project directory, not untrusted input
- **Simplicity**: Single line to save/load: `pickle.dump()` / `pickle.load()`

**Alternatives Considered**:
- **joblib**: Better compression but adds dependency (rejected - no material benefit)
- **msgpack**: Smaller files but requires numpy conversion (rejected - added complexity)
- **diskcache**: Full caching library but overkill for simple key-value store (rejected - YAGNI)

**Implementation**:
- Cache key: hash of (text content + model name) to ensure model changes invalidate cache
- Cache file format: `.pkl` binary files in `.pytest-semantic-cache/` directory
- Each cache entry: `{text_hash: numpy.ndarray}` dictionary

---

## 3. File Locking Library

### Decision: **filelock**

**Rationale**:
- **Cross-Platform**: Works on Linux, macOS, Windows (meets target platform requirement)
- **Simple API**: `with FileLock("lockfile"): ...` context manager pattern
- **Timeout Support**: Built-in timeout parameter (meets 5-second timeout requirement)
- **Pytest-xdist Compatible**: Used by other pytest plugins successfully
- **Lightweight**: Single small dependency (~10KB)
- **Battle-Tested**: 10M+ downloads/month, stable

**Alternatives Considered**:
- **portalocker**: Similar but less widely adopted in pytest ecosystem
- **fcntl** (Unix only): Not cross-platform (Windows incompatible) - rejected
- **Custom implementation**: Reinventing wheel, error-prone - rejected per KISS principle

**Implementation**:
- Lock file: `.pytest-semantic-cache/.lock`
- Lock scope: Per cache write operation (reads are concurrent-safe)
- Timeout: 5 seconds (per spec), raise clear error on timeout

---

## 4. Pytest Plugin Best Practices

### Key Patterns Researched

**Session-Scoped Resources** (embedding model loading):
- **Pattern**: Use `pytest_configure(config)` hook to initialize global state
- **Cleanup**: Use `pytest_unconfigure(config)` for teardown
- **Storage**: Store in `config._semantic_assert_model` for session lifetime
- **Lazy Loading**: Initialize on first assertion call, not at configure time (faster startup)

**Configuration Validation** (fail-fast on invalid pytest.ini):
- **Pattern**: Validate in `pytest_configure()` before any tests run
- **Method**: Use `config.getini()` to read values, validate types/ranges
- **Error Handling**: Raise `pytest.UsageError` with actionable message
- **Defaults**: Apply defaults if not specified (zero-config mode)

**Custom Assertions** (assert_semantically_similar):
- **Pattern**: Regular Python functions (not pytest fixtures) for assertion logic
- **Failure Reporting**: Raise `AssertionError` with detailed message (pytest captures)
- **Introspection**: Use `pytest.raises()` in tests to verify error messages
- **Integration**: No special pytest integration needed - just importable functions

**Entry Point Registration**:
- **Pattern**: `[pytest11]` entry point in `pyproject.toml`:
  ```toml
  [project.entry-points.pytest11]
  semantic_assert = "pytest_semantic_assert.plugin"
  ```
- **Hook Discovery**: pytest auto-discovers `pytest_*` functions in plugin module

**Source**: Official pytest plugin development guide, `pytest-xdist`, `pytest-mock` patterns

---

## 5. Cosine Similarity Implementation

### Decision: **numpy (manual implementation)**

**Rationale**:
- **Already Required**: numpy is dependency of sentence-transformers (no new dep)
- **Simple & Fast**: `np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))` - 3 lines
- **Explicit**: Clear what's happening (transparent algorithm)
- **Performance**: Optimized C code, meets <50ms target easily
- **No scipy Needed**: Avoids large scipy dependency (~50MB) for single function

**Alternatives Considered**:
- **scipy.spatial.distance.cosine**: Requires scipy dependency (50MB+) - rejected as overkill
- **sentence-transformers util.cos_sim()**: Tightly couples to library, less explicit - rejected
- **sklearn.metrics.pairwise.cosine_similarity**: Requires scikit-learn (large) - rejected

**Implementation**:
```python
def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors (0.0 to 1.0)."""
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    return float(dot_product / (norm_a * norm_b))
```

---

## 6. Model Download & Retry Logic

### Decision: **sentence-transformers built-in + custom retry wrapper**

**Rationale**:
- **Built-in Caching**: sentence-transformers uses HuggingFace cache (~/.cache/huggingface/)
- **Automatic Download**: Model auto-downloads on first `SentenceTransformer(model_name)` call
- **Custom Retry**: Wrap in retry decorator for exponential backoff (not built-in)
- **Error Handling**: Catch `OSError`, `HTTPError` for network failures

**Implementation**:
- Retry on: network errors, HTTP errors, incomplete downloads
- Backoff: 1s, 2s, 4s (exponential)
- Max retries: 3 attempts (per spec)
- Final failure: Raise `pytest.UsageError` with actionable message:
  ```
  Failed to load embedding model 'all-MiniLM-L6-v2' after 3 attempts.

  Troubleshooting:
  - Check network connectivity
  - Verify model name in pytest.ini
  - Check disk space (~100MB required)
  - Try manual download: huggingface-cli download sentence-transformers/all-MiniLM-L6-v2
  ```

---

## 7. Text Preprocessing & Normalization

### Decision: **Minimal preprocessing (whitespace normalization only)**

**Rationale**:
- **Preserve Intent**: Users expect semantic comparison of actual LLM output
- **Model Handles It**: Sentence transformers already handle punctuation, case, etc.
- **Explicit**: What you see is what's compared (no hidden transformations)
- **KISS**: Avoid complexity of tokenization, stemming, etc.

**Processing Steps**:
1. Validate length (3 to max_length characters)
2. Strip leading/trailing whitespace
3. Normalize internal whitespace (multiple spaces → single space)
4. Pass to embedding model as-is

**Alternatives Considered**:
- **Aggressive normalization**: Lowercase, remove punctuation - rejected (loses semantic info)
- **Zero normalization**: Keep all whitespace - rejected (inconsistent trailing space issues)

---

## 8. Error Message Design

### Pattern: **Actionable Three-Part Structure**

**Components**:
1. **What Failed**: Clear statement of the assertion failure
2. **Details**: Actual vs expected, similarity score, threshold
3. **Suggestion**: Contextual help based on score pattern

**Example Output**:
```
AssertionError: Semantic similarity too low

Expected (semantically): "Hello, how can I help you?"
Actual: "Goodbye!"
Similarity Score: 0.23 (threshold: 0.85)

Suggestion: These texts have opposite meanings (similarity < 0.3).
Consider using assert_contradicts() if testing for opposite meanings.
```

**Score-Based Suggestions**:
- **< 0.3**: "Texts are semantically unrelated"
- **0.3 - 0.6**: "Texts are somewhat related but differ in meaning"
- **0.6 - threshold**: "Texts are nearly similar (score {score:.2f} vs threshold {threshold:.2f}). Consider lowering threshold or reviewing expected text."
- **Opposite detection**: Heuristic for "hello" vs "goodbye" patterns (future enhancement)

---

## 9. Parallel Execution Strategy

### Decision: **File-based locking on cache writes, concurrent reads**

**Architecture**:
- **Read Operations**: No lock (pickle.load is atomic, files immutable after write)
- **Write Operations**: Acquire `.lock` file before writing, release after
- **Lock Timeout**: 5 seconds (per spec)
- **Lock File Location**: `.pytest-semantic-cache/.lock`

**Workflow**:
1. Check if cache entry exists (no lock needed for read)
2. If exists: Load and return (concurrent-safe)
3. If missing: Acquire lock → compute embedding → write → release lock
4. Other workers wait on lock if computing same embedding simultaneously

**Race Condition Handling**:
- **Double-check pattern**: After acquiring lock, check again if file exists (another worker may have written it)
- **Atomic writes**: Write to temp file, then rename (atomic on POSIX systems)
- **Timeout failure**: Clear error message with suggestion to check for deadlocks

---

## 10. Zero-Config Defaults

### Design: **Convention over Configuration**

**Defaults** (no pytest.ini required):
- `semantic_assert_threshold`: 0.85 (balanced strictness)
- `semantic_assert_model`: "all-MiniLM-L6-v2" (optimal speed/quality)
- `semantic_assert_cache`: true (performance)
- `semantic_assert_cache_dir`: ".pytest-semantic-cache/" (team-shareable)
- `semantic_assert_max_length`: 10000 (prevent performance issues)

**Configuration Discovery Order**:
1. Explicit function parameter (highest priority)
2. pytest.ini / pyproject.toml `[tool.pytest.ini_options]`
3. Environment variables (e.g., `SEMANTIC_ASSERT_THRESHOLD`)
4. Hard-coded defaults (lowest priority)

**Validation**:
- Threshold: Must be float between 0.0 and 1.0
- Model: Must be valid sentence-transformer model name
- Cache dir: Must be writable or "memory"
- Max length: Must be positive integer

---

## Summary: Final Tech Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Embedding Model** | all-MiniLM-L6-v2 | Optimal speed/size/quality balance |
| **Similarity Metric** | Cosine (numpy) | Simple, fast, no extra dependencies |
| **Cache Storage** | pickle files | Zero dependencies, native numpy support |
| **Cache Locking** | filelock | Cross-platform, pytest-xdist compatible |
| **Plugin Framework** | pytest hooks | Standard pytest plugin pattern |
| **Testing** | pytest + tox | Self-testing, multi-version validation |
| **Build System** | pyproject.toml | Modern PEP 517/518 compliant |

**Total Dependencies**: pytest (required), sentence-transformers, numpy (transitive), filelock

**Estimated Package Size**: ~85MB (mostly embedding model)

**Performance Confidence**: All targets achievable (<50ms cached, <200ms uncached, <30s install)

