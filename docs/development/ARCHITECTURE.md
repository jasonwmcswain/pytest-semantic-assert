# Architecture Overview

Technical architecture and design decisions for pytest-semantic-assert.

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│              Pytest Framework                    │
└───────────────────┬─────────────────────────────┘
                    │ pytest11 entry point
                    ▼
┌─────────────────────────────────────────────────┐
│         pytest_semantic_assert.plugin           │
│  ┌───────────────────────────────────────────┐  │
│  │ pytest_configure() - Load configuration  │  │
│  │ pytest_addoption() - Register options    │  │
│  └───────────────────────────────────────────┘  │
└───────────────────┬─────────────────────────────┘
                    │
    ┌───────────────┴───────────────┐
    ▼                               ▼
┌─────────────────┐        ┌─────────────────────┐
│  Configuration  │        │ EmbeddingManager    │
│  - threshold    │◄───────│ - model (lazy)      │
│  - model_name   │        │ - cache             │
│  - cache_dir    │        │ - retry logic       │
└─────────────────┘        └──────────┬──────────┘
                                      │
                    ┌─────────────────┴─────────────┐
                    ▼                               ▼
          ┌──────────────────┐          ┌──────────────────┐
          │ EmbeddingCache   │          │ SentenceTransf.  │
          │ - disk/memory    │          │ (all-MiniLM-L6)  │
          │ - file locking   │          │ 384-dim vectors  │
          └──────────────────┘          └──────────────────┘
                    │
                    ▼
          ┌──────────────────┐
          │   Assertions     │
          │ - similarity     │
          │ - threshold      │
          │ - error msgs     │
          └──────────────────┘
                    │
                    ▼
          ┌──────────────────┐
          │ SimilarityCalc   │
          │ - cosine sim     │
          │ - numpy          │
          └──────────────────┘
```

## 📦 Core Components

### 1. Plugin Integration (`plugin.py`)

**Purpose**: Pytest plugin hooks and configuration

**Key Functions**:
- `pytest_addoption()` - Register pytest.ini options
- `pytest_configure()` - Load and validate configuration
- `get_embedding_manager()` - Session-scoped manager singleton

**Design Decisions**:
- Session-scoped model loading (load once, reuse across all tests)
- Lazy initialization (only load model when first assertion runs)
- Configuration validation at session start (fail-fast)

### 2. Configuration Management (`config.py`)

**Purpose**: Load and validate pytest.ini settings

**Configuration Options**:
```python
semantic_assert_threshold: float = 0.85      # Similarity threshold (0.0-1.0)
semantic_assert_model: str = "all-MiniLM-L6-v2"  # Embedding model
semantic_assert_cache: bool = True           # Enable caching
semantic_assert_cache_dir: str = ".pytest-semantic-cache/"  # Cache location
semantic_assert_max_length: int = 10000      # Max text length
```

**Validation Rules**:
- Threshold: 0.0 ≤ threshold ≤ 1.0
- Model name: Non-empty string
- Max length: Positive integer
- Cache dir: Writable directory or "memory"

### 3. Embedding Management (`embeddings.py`)

**Purpose**: Model lifecycle and embedding computation

**Key Features**:
- **Lazy Loading**: Model loaded on first use, not at import
- **Retry Logic**: 3 attempts with exponential backoff (1s, 2s, 4s)
- **Cache Integration**: Check cache before computing
- **Text Validation**: Length checks (3-10000 chars)

**Model Details**:
- **Name**: all-MiniLM-L6-v2 (sentence-transformers)
- **Size**: ~80MB
- **Dimensions**: 384 float32 values
- **Speed**: ~50ms inference on CPU

### 4. Caching System (`cache.py`)

**Purpose**: Persistent embedding storage with parallel safety

**Architecture**:
```python
Cache Key: SHA256(text + "::" + model_name)[:16]
Cache File: .pytest-semantic-cache/{key}.pkl
Lock File: .pytest-semantic-cache/.lock
```

**Modes**:
1. **Disk Mode** (default):
   - Files: `{cache_dir}/{hash}.pkl`
   - Locking: `filelock` with 5s timeout
   - Persistent across sessions

2. **Memory Mode** (`cache_dir="memory"`):
   - In-memory dict (session only)
   - No file I/O
   - No locking needed

**Parallel Safety**:
- **Reads**: Concurrent (no locks)
- **Writes**: File-locked with timeout
- **Double-check pattern**: Recheck after acquiring lock

### 5. Assertions (`assertions.py`)

**Purpose**: Core assertion functions with helpful errors

**Functions**:
1. `assert_semantically_similar(actual, expected, threshold=None)`
2. `assert_semantically_similar_to_any(actual, expected_list, threshold=None)`

**Error Message Format** (3-part structure):
```
AssertionError: Semantic similarity too low

Expected (semantically): "{expected}"
Actual: "{actual}"
Similarity Score: 0.62 (threshold: 0.75)

Suggestion: {contextual_suggestion}
```

**Suggestions by Score**:
- `< 0.3`: Texts are semantically unrelated
- `0.3-0.6`: Somewhat related but differ in meaning
- `0.6-threshold`: Nearly similar, consider lowering threshold

### 6. Similarity Computation (`similarity.py`)

**Purpose**: Cosine similarity calculation

**Algorithm**:
```python
similarity = dot(a, b) / (norm(a) * norm(b))
```

**Implementation**:
- Pure numpy (no scipy needed)
- Validates equal dimensions
- Clamps result to [0.0, 1.0]
- Rejects zero vectors

## 🔄 Data Flow

### Typical Assertion Flow

```
1. User calls: assert_semantically_similar(actual, expected, threshold)
   │
   ├─► Get configuration (from pytest config or defaults)
   │
   ├─► Get/Create EmbeddingManager (session-scoped singleton)
   │   │
   │   ├─► Load model (lazy, first-time only)
   │   │   └─► Retry 3 times with exponential backoff on failure
   │   │
   │   └─► Get embeddings for actual and expected
   │       │
   │       ├─► Check cache (Cache.get)
   │       │   ├─► HIT: Return cached embedding (~2ms)
   │       │   └─► MISS: Compute embedding
   │       │       ├─► Validate text (3-10000 chars)
   │       │       ├─► Compute via model (~150ms)
   │       │       ├─► Acquire lock (if disk cache)
   │       │       ├─► Save to cache
   │       │       └─► Release lock
   │       │
   │       └─► Return embeddings
   │
   ├─► Compute cosine similarity
   │
   └─► Compare to threshold
       ├─► PASS: Return silently
       └─► FAIL: Raise AssertionError with 3-part message
```

## 🎯 Design Principles

### 1. Zero-Config First
- Works out-of-box with sensible defaults
- Configuration optional but available

### 2. Performance-Optimized
- **Session-scoped model**: Load once, reuse
- **Aggressive caching**: Disk persistence
- **Lazy loading**: Defer model load until needed

**Performance Targets** (all met):
- Cached comparison: <50ms (achieved: ~2ms)
- Uncached comparison: <200ms (achieved: ~150ms)

### 3. Parallel-Safe
- File locking for cache writes
- Concurrent reads allowed
- pytest-xdist compatible

### 4. Developer-Friendly
- **Clear errors**: 3-part structure with suggestions
- **Type safety**: Full mypy strict compliance
- **Tested**: 82 tests, 67% coverage

## 🔧 Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Embedding Model** | all-MiniLM-L6-v2 | Optimal speed/quality/size balance |
| **Similarity** | Cosine (numpy) | Simple, fast, no extra dependencies |
| **Cache Storage** | pickle | Built-in, native numpy support |
| **Cache Locking** | filelock | Cross-platform, pytest-xdist compatible |
| **Plugin Framework** | pytest hooks | Standard pytest pattern |
| **Testing** | pytest | Self-hosting (plugin tests with pytest) |

## 📈 Performance Characteristics

### Memory Footprint
- **Model**: ~100MB (loaded once per session)
- **Per Embedding**: ~1.5KB (384 float32 values)
- **10K Cached Texts**: ~15MB (in-memory)

### Latency
- **Cache Hit**: ~2ms (disk read + pickle deserialize)
- **Cache Miss**: ~150ms (model inference + cache write)
- **Model Load**: ~1-2s (first time)

### Throughput
- **With cache**: 100+ assertions/second
- **Without cache**: ~6 assertions/second
- **Expected hit rate**: >90% in typical test suites

## 🔐 Security Considerations

1. **No Untrusted Input**: Cache uses pickle (trusted local data only)
2. **No Network Calls**: Model cached locally after first download
3. **File Permissions**: Cache files inherit directory permissions
4. **No Secrets**: No API keys or credentials needed

## 🧪 Testing Strategy

### Test Categories
1. **Unit Tests** (50): Individual components
2. **Integration Tests**: Multiple components
3. **Contract Tests** (6): API stability
4. **E2E Tests** (15): User scenarios

### Mocking Strategy
- Mock `SentenceTransformer` in unit tests
- Use real model in E2E tests
- Cache disabled in most unit tests (for isolation)

## 📚 References

- [Sentence Transformers](https://www.sbert.net/)
- [pytest Plugin Development](https://docs.pytest.org/en/latest/how-to/writing_plugins.html)
- [Cosine Similarity](https://en.wikipedia.org/wiki/Cosine_similarity)


