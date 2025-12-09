# Data Model: Semantic Assertions for LLM Testing

**Feature**: 001-semantic-assert-mvp
**Date**: 2025-12-06
**Purpose**: Define core entities, their attributes, relationships, and validation rules

---

## Entity Definitions

### 1. Configuration

**Purpose**: Holds plugin settings loaded from pytest.ini/pyproject.toml with validated defaults

**Attributes**:
- `threshold: float` - Default similarity threshold (0.0 to 1.0)
- `model_name: str` - Embedding model identifier (e.g., "all-MiniLM-L6-v2")
- `cache_enabled: bool` - Whether to cache embeddings
- `cache_dir: str` - Cache storage location or "memory"
- `max_length: int` - Maximum text length in characters

**Validation Rules**:
- `threshold` MUST be >= 0.0 and <= 1.0
- `model_name` MUST be non-empty string
- `max_length` MUST be > 0
- `cache_dir` MUST be writable directory path or literal "memory"

**Lifecycle**:
- Created: During `pytest_configure()` hook
- Accessed: By assertion functions and embedding manager
- Destroyed: At pytest session end

**Relationships**:
- Used by: EmbeddingManager, SemanticAssertion

---

### 2. EmbeddingManager

**Purpose**: Manages embedding model lifecycle, caching, and computation

**Attributes**:
- `model: SentenceTransformer` - Loaded embedding model (lazy-initialized)
- `cache: EmbeddingCache` - Cache instance
- `config: Configuration` - Plugin configuration
- `model_loaded: bool` - Whether model has been initialized

**Methods**:
- `get_embedding(text: str) -> np.ndarray` - Get embedding for text (cached or computed)
- `load_model() -> None` - Load embedding model with retry logic
- `_retry_download(attempts: int = 3) -> SentenceTransformer` - Retry model download

**Validation Rules**:
- `text` MUST be >= 3 characters and <= `config.max_length`
- Model MUST be loaded before computing embeddings
- Failed loads MUST retry up to 3 times with exponential backoff

**Lifecycle**:
- Created: On first assertion call (lazy initialization)
- Persists: For entire pytest session (session-scoped)
- Cleanup: Model unloaded at session end

**Relationships**:
- Contains: EmbeddingCache
- Uses: Configuration
- Used by: SemanticAssertion

---

### 3. EmbeddingCache

**Purpose**: Stores and retrieves computed embeddings with file-based locking for parallel safety

**Attributes**:
- `cache_dir: Path` - Directory path for cache storage
- `lock_file: Path` - File lock path for write synchronization
- `memory_cache: dict[str, np.ndarray]` - In-memory cache (if cache_dir == "memory")

**Methods**:
- `get(text: str, model_name: str) -> Optional[np.ndarray]` - Retrieve cached embedding
- `set(text: str, model_name: str, embedding: np.ndarray) -> None` - Store embedding
- `_cache_key(text: str, model_name: str) -> str` - Generate cache key (hash)
- `_lock_and_write(key: str, embedding: np.ndarray) -> None` - Thread-safe write

**Cache Key Format**:
- `key = sha256(text + "::" + model_name).hexdigest()` (first 16 chars)
- Example: `a1b2c3d4e5f6g7h8.pkl`

**Validation Rules**:
- Cache directory MUST be writable (or "memory" for in-memory mode)
- Lock timeout MUST be 5 seconds max
- Cache files MUST be `.pkl` format

**File Structure**:
```
.pytest-semantic-cache/
├── .lock                    # File lock for write synchronization
├── a1b2c3d4e5f6g7h8.pkl    # Cached embedding for text+model hash
├── 9f8e7d6c5b4a3g2h.pkl
└── ...
```

**Lifecycle**:
- Created: When EmbeddingManager initializes
- Persists: Across pytest sessions (disk cache) or per-session (memory cache)
- Cleanup: No automatic cleanup (cache accumulates)

**Relationships**:
- Owned by: EmbeddingManager
- Uses: filelock library for synchronization

---

### 4. SemanticAssertion

**Purpose**: Represents a single semantic similarity comparison operation

**Attributes**:
- `actual: str` - Actual text from test
- `expected: str | list[str]` - Expected text(s) to compare against
- `threshold: float` - Similarity threshold for pass/fail
- `score: float` - Computed similarity score (0.0 to 1.0)
- `passed: bool` - Whether assertion passed

**Methods**:
- `execute() -> None` - Perform comparison and raise AssertionError if failed
- `_compute_score() -> float` - Calculate similarity score
- `_format_error_message() -> str` - Generate detailed failure message
- `_suggest_action() -> str` - Provide contextual suggestion based on score

**Validation Rules**:
- `actual` MUST be >= 3 chars and <= max_length
- `expected` (if list) MUST be non-empty
- Each `expected` item MUST be >= 3 chars and <= max_length
- `threshold` MUST be >= 0.0 and <= 1.0

**State Transitions**:
1. **Created** → `actual`, `expected`, `threshold` set
2. **Executed** → embeddings computed, `score` calculated
3. **Passed/Failed** → `passed` set, AssertionError raised if failed

**Error Message Format**:
```
AssertionError: Semantic similarity too low

Expected (semantically): "{expected}"
Actual: "{actual}"
Similarity Score: {score:.2f} (threshold: {threshold})

Suggestion: {contextual_suggestion}
```

**Relationships**:
- Uses: EmbeddingManager (to get embeddings)
- Uses: SimilarityCalculator (to compute score)

---

### 5. SimilarityCalculator

**Purpose**: Computes cosine similarity between embedding vectors

**Attributes**: (None - stateless utility)

**Methods**:
- `compute(embedding_a: np.ndarray, embedding_b: np.ndarray) -> float` - Calculate cosine similarity

**Algorithm**:
```
similarity = dot(a, b) / (norm(a) * norm(b))
```

**Validation Rules**:
- Embeddings MUST be same dimension
- Embeddings MUST be non-zero vectors
- Result MUST be clamped to [0.0, 1.0] range

**Lifecycle**:
- Stateless: No instance state
- Used: By SemanticAssertion for score computation

**Relationships**:
- Used by: SemanticAssertion

---

## Entity Relationship Diagram

```
┌─────────────────┐
│  Configuration  │
│  - threshold    │
│  - model_name   │
│  - cache_dir    │
│  - max_length   │
└────────┬────────┘
         │ used by
         ▼
┌─────────────────────────┐
│   EmbeddingManager      │
│   - model               │◄──────┐
│   - cache               │       │
│   - config              │       │
└───────┬─────────────────┘       │
        │ owns                    │ uses
        ▼                         │
┌─────────────────────────┐       │
│   EmbeddingCache        │       │
│   - cache_dir           │       │
│   - lock_file           │       │
│   - memory_cache        │       │
└─────────────────────────┘       │
                                  │
┌─────────────────────────┐       │
│  SemanticAssertion      │───────┘
│  - actual               │
│  - expected             │
│  - threshold            │
│  - score                │
│  - passed               │
└───────┬─────────────────┘
        │ uses
        ▼
┌─────────────────────────┐
│  SimilarityCalculator   │
│  (stateless)            │
└─────────────────────────┘
```

---

## Data Flow

### Assertion Execution Flow

```
1. User calls: assert_semantically_similar(actual, expected, threshold)
   │
   ├─→ Validate inputs (length, type)
   │
   ├─→ Load Configuration (from pytest config)
   │
   ├─→ Get/Create EmbeddingManager (session-scoped)
   │   │
   │   └─→ Lazy-load model if not loaded
   │       │
   │       └─→ Retry download up to 3 times on failure
   │
   ├─→ Get embeddings for actual and expected
   │   │
   │   ├─→ Check cache (EmbeddingCache.get)
   │   │   │
   │   │   ├─→ HIT: Return cached embedding
   │   │   │
   │   │   └─→ MISS: Compute embedding
   │   │       │
   │   │       ├─→ Acquire lock (if disk cache)
   │   │       ├─→ Compute via model
   │   │       ├─→ Save to cache
   │   │       └─→ Release lock
   │   │
   │   └─→ Return embeddings
   │
   ├─→ Compute similarity score (SimilarityCalculator)
   │
   ├─→ Compare score to threshold
   │   │
   │   ├─→ PASS: Return silently
   │   │
   │   └─→ FAIL: Raise AssertionError with detailed message
   │       │
   │       └─→ Include contextual suggestion based on score
```

---

## Validation Summary

| Entity | Critical Validations |
|--------|---------------------|
| **Configuration** | threshold in [0.0, 1.0]; max_length > 0; cache_dir writable |
| **EmbeddingManager** | Model loaded before use; text length within bounds |
| **EmbeddingCache** | Lock timeout 5s; atomic writes; valid pickle files |
| **SemanticAssertion** | Text >= 3 chars; expected list non-empty; threshold valid |
| **SimilarityCalculator** | Equal embedding dimensions; non-zero vectors |

---

## Performance Considerations

**Caching Impact**:
- **Cache Hit**: ~2ms (disk read + pickle deserialize)
- **Cache Miss**: ~150ms (model inference + cache write)
- **Target**: >90% hit rate in typical test suites (repeated comparisons)

**Memory Footprint**:
- **Model**: ~100MB (all-MiniLM-L6-v2 loaded once)
- **Per Embedding**: ~1.5KB (384 float32 values)
- **In-Memory Cache**: ~15MB for 10,000 unique texts

**Parallel Execution**:
- **Lock Contention**: Minimal (only on cache writes)
- **Read Concurrency**: Unlimited (no locks on reads)
- **Expected Throughput**: 100+ assertions/second with caching

