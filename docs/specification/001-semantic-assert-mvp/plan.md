# Implementation Plan: Semantic Assertions for LLM Testing

**Branch**: `001-semantic-assert-mvp` | **Date**: 2025-12-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-semantic-assert-mvp/spec.md`

## Summary

A pytest plugin enabling semantic assertions for LLM outputs using embedding-based similarity comparison. Solves the problem of brittle LLM tests that fail on wording variations despite semantic equivalence. Core MVP includes `assert_semantically_similar()` function, pytest.ini configuration, multi-value comparison, and helpful error messages with configurable caching strategy.

**Technical Approach**: Leverage sentence-transformers for local embedding generation, cosine similarity for comparison, file-based disk cache with locking for parallel execution safety, and pytest plugin hooks for seamless integration.

## Technical Context

**Language/Version**: Python 3.9+ (support 3.9, 3.10, 3.11, 3.12)
**Primary Dependencies**:
- `pytest` >= 7.0 (plugin host framework)
- `sentence-transformers` (embedding model library)
- `numpy` (vector operations, cosine similarity)
- `filelock` (file-based locking for parallel execution)
- Optional: `diskcache` or built-in `pickle` for embedding serialization

**Storage**: File-based cache (default: `.pytest-semantic-cache/` in project directory); configurable to user home or in-memory
**Testing**: pytest (self-testing the plugin); tox for multi-version testing (Python 3.9-3.12, pytest 7.0+)
**Target Platform**: Cross-platform (Linux, macOS, Windows) - wherever pytest runs
**Project Type**: Single Python package (pytest plugin)
**Performance Goals**:
- <50ms per comparison (cached embeddings)
- <200ms per comparison (first-run, uncached)
- <30s installation + first test (including model download)
- <5s for 100+ item list comparison

**Constraints**:
- Text length: 3-10,000 characters (configurable max)
- Model download: requires network on first run (offline afterwards)
- Cache lock timeout: 5 seconds for parallel execution
- Model retry: 3 attempts with exponential backoff (1s, 2s, 4s)

**Scale/Scope**:
- MVP: 4 user stories (P1-P4)
- Single pytest plugin package
- ~1,500-2,000 LOC estimated
- Support 1000s of assertions per test suite

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **PyPI Package Excellence**: All public APIs will have type hints and docstrings; dependencies minimal (pytest, sentence-transformers, numpy, filelock); no hardcoded credentials
- [x] **Pytest Integration First**: Uses `pytest_configure`, `pytest_addoption` hooks; configuration via pytest.ini/pyproject.toml; compatible with pytest 7.0+
- [x] **Test-Driven Development**: Tests written before implementation; >90% coverage target; unit/integration/contract/E2E tests planned for each user story
- [x] **Semantic Versioning**: Initial version 0.1.0 (pre-1.0 for MVP); breaking changes expected before 1.0.0; will document in CHANGELOG
- [x] **Developer Experience**: Error messages actionable (show score, threshold, suggestions); clear API (`assert_semantically_similar`); zero-config defaults; `--semantic-assert-debug` flag planned
- [x] **Performance & Efficiency**: Speed targets defined (<50ms cached, <200ms uncached); disk cache with file locking; session-scoped model loading; CI-friendly (cacheable models)
- [x] **Documentation as Code**: README with quickstart; API docs from docstrings (Sphinx); examples will be tested; CHANGELOG.md from start

**Complexity Justification**: None - all checks pass

## Project Structure

### Documentation (this feature)

```text
specs/001-semantic-assert-mvp/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: Technology decisions & best practices
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Getting started guide
├── contracts/           # Phase 1: Public API contracts
│   └── api.md          # Function signatures, return types
└── checklists/
    └── requirements.md  # Spec quality validation
```

### Source Code (repository root)

```text
pytest-semantic-assert/
├── pyproject.toml           # Project metadata, dependencies, entry points
├── README.md                # Quick start, installation, examples
├── CHANGELOG.md             # Version history
├── LICENSE                  # MIT license
├── .gitignore              # Exclude .pytest-semantic-cache/, __pycache__, etc.
│
├── src/
│   └── pytest_semantic_assert/
│       ├── __init__.py              # Version, public API exports
│       ├── plugin.py                # Pytest hooks (pytest_configure, pytest_addoption)
│       ├── assertions.py            # assert_semantically_similar, assert_semantically_similar_to_any
│       ├── embeddings.py            # Embedding model loading, caching, retry logic
│       ├── similarity.py            # Cosine similarity computation
│       ├── cache.py                 # Cache management (disk/memory), file locking
│       ├── config.py                # Configuration loading, validation
│       └── exceptions.py            # Custom exceptions (TextTooShortError, TextTooLongError, etc.)
│
└── tests/
    ├── unit/
    │   ├── test_similarity.py       # Test cosine similarity calculations
    │   ├── test_config.py           # Test configuration loading/validation
    │   ├── test_cache.py            # Test cache operations, locking
    │   └── test_embeddings.py       # Test embedding generation (mocked model)
    │
    ├── integration/
    │   ├── test_plugin_hooks.py     # Test pytest plugin registration
    │   ├── test_assertions.py       # Test assertion functions end-to-end
    │   ├── test_configuration.py    # Test pytest.ini configuration
    │   └── test_parallel.py         # Test pytest-xdist compatibility
    │
    ├── contract/
    │   └── test_public_api.py       # Test public API signatures stability
    │
    └── e2e/
        ├── test_user_stories.py     # Test each user story acceptance scenario
        └── test_edge_cases.py       # Test edge cases (empty, long, model failures)
```

**Structure Decision**: Single Python package using modern `src/` layout for proper import isolation. Pytest plugin code in `pytest_semantic_assert/` with entry point `[pytest11]` in `pyproject.toml`. Comprehensive test structure covering all test categories per constitution TDD requirements.

## Complexity Tracking

> No violations - constitution check passed

**Complexity Justification**: None - all checks pass

---

## Phase 0: Research & Technology Decisions ✅ COMPLETE

**Status**: All technical unknowns resolved
**Output**: [research.md](./research.md)

### Key Decisions

| Decision Area | Choice | Rationale |
|---------------|--------|-----------|
| **Embedding Model** | all-MiniLM-L6-v2 | 80MB, ~50ms inference, optimal speed/quality balance |
| **Cache Serialization** | pickle (built-in) | Zero dependencies, native numpy support, fast |
| **File Locking** | filelock library | Cross-platform, pytest-xdist compatible, simple API |
| **Similarity Computation** | numpy manual implementation | Already required, simple, fast, no scipy needed |
| **Pytest Patterns** | Session-scoped lazy loading | Standard plugin patterns, optimal performance |

**All NEEDS CLARIFICATION items resolved** - ready for Phase 1.

---

## Phase 1: Design & Contracts ✅ COMPLETE

**Status**: Design artifacts generated
**Outputs**:
- [data-model.md](./data-model.md) - Entity definitions and relationships
- [contracts/api.md](./contracts/api.md) - Public API signatures and stability guarantees
- [quickstart.md](./quickstart.md) - User-facing getting started guide

### Data Model Summary

**Core Entities**:
1. **Configuration** - Plugin settings from pytest.ini (threshold, model, cache_dir, max_length)
2. **EmbeddingManager** - Session-scoped model lifecycle and caching orchestration
3. **EmbeddingCache** - File-based storage with locking for parallel safety
4. **SemanticAssertion** - Comparison operation with score computation and error formatting
5. **SimilarityCalculator** - Stateless cosine similarity utility

**Key Relationships**:
- Configuration → used by EmbeddingManager and SemanticAssertion
- EmbeddingManager → owns EmbeddingCache, lazy-loads model
- SemanticAssertion → uses EmbeddingManager and SimilarityCalculator

### API Contract Summary

**Public Functions**:
- `assert_semantically_similar(actual, expected, threshold=None)` - Core assertion
- `assert_semantically_similar_to_any(actual, expected_list, threshold=None)` - Multi-value assertion

**Configuration Options** (5 total):
- `semantic_assert_threshold` (float, default 0.85)
- `semantic_assert_model` (string, default "all-MiniLM-L6-v2")
- `semantic_assert_cache` (bool, default true)
- `semantic_assert_cache_dir` (string, default ".pytest-semantic-cache/")
- `semantic_assert_max_length` (int, default 10000)

**Stability Guarantees**:
- Pre-1.0: API may change in MINOR versions with deprecation warnings
- Post-1.0: Breaking changes ONLY in MAJOR versions

---

## Constitution Re-Check (Post-Design)

*GATE: Must pass before proceeding to tasks.*

- [x] **PyPI Package Excellence**:
  - ✅ Type hints defined in API contract for all public functions
  - ✅ Dependencies minimal and justified (pytest, sentence-transformers, numpy, filelock)
  - ✅ No hardcoded credentials (model downloaded from HuggingFace public repo)

- [x] **Pytest Integration First**:
  - ✅ Hooks defined (`pytest_configure`, `pytest_addoption`)
  - ✅ Configuration via pytest.ini/pyproject.toml specified
  - ✅ Entry point `[pytest11]` documented
  - ✅ Compatible with pytest 7.0+ per contract

- [x] **Test-Driven Development**:
  - ✅ Test structure defined (unit, integration, contract, E2E)
  - ✅ Test categories mapped to entities
  - ✅ >90% coverage target for core logic established
  - ✅ Acceptance scenarios from spec testable

- [x] **Semantic Versioning**:
  - ✅ Initial version 0.1.0 planned
  - ✅ Breaking change policy documented in API contract
  - ✅ Deprecation strategy defined (1 MINOR version notice)

- [x] **Developer Experience**:
  - ✅ Error messages designed with 3-part structure
  - ✅ Contextual suggestions based on similarity score
  - ✅ Zero-config defaults specified
  - ✅ Quickstart guide completed (<2 minute target)

- [x] **Performance & Efficiency**:
  - ✅ Targets achievable (<50ms cached, <200ms uncached per research)
  - ✅ Caching strategy with file locking defined
  - ✅ Session-scoped model loading (load once)
  - ✅ CI/CD caching strategy documented in quickstart

- [x] **Documentation as Code**:
  - ✅ Quickstart guide created
  - ✅ API contract with full docstrings
  - ✅ Examples in quickstart will be tested (noted)
  - ✅ CHANGELOG.md planned from start

**Result**: ✅ **ALL GATES PASSED** - Design is constitution-compliant

---

## Next Steps

**Phase 2: Task Breakdown** (via `/speckit.tasks`)

Now that planning is complete, the next step is to create the implementation task list:

```bash
/speckit.tasks
```

This will generate `tasks.md` with:
- Task breakdown by user story (P1, P2, P3, P4)
- Parallel execution opportunities
- Test-first workflow (TDD)
- Specific file paths for each task
- Dependency ordering

**Estimated Implementation Timeline**:
- Phase 1 (Setup): 1-2 days
- Phase 2 (P1 - Core Assertion): 3-5 days
- Phase 3 (P2 - Configuration): 2-3 days
- Phase 4 (P3 - Multi-value): 2-3 days
- Phase 5 (P4 - Error Messages): 1-2 days
- Phase 6 (Polish & Release): 2-3 days

**Total**: ~7-10 weeks (per original estimate)
