# Feature Specification: Semantic Assertions for LLM Testing

**Feature Branch**: `001-semantic-assert-mvp`
**Created**: 2025-12-06
**Status**: Draft
**Input**: User description: "Pytest plugin for semantic LLM output assertions using embeddings"

## Clarifications

### Session 2025-12-06

- Q: Where should computed embeddings be cached to ensure persistence across pytest sessions while maintaining performance? → A: Configurable via pytest.ini (support both in-memory and disk options), with default being persistent disk cache in project directory (.pytest-semantic-cache/)
- Q: How should the plugin handle empty strings and very short inputs (1-2 characters)? → A: Fail with clear error message ("Cannot compute semantic similarity for empty or very short text - minimum 3 characters required")
- Q: How should the plugin behave when the embedding model cannot be loaded (network failure, corrupted download, unsupported platform)? → A: Retry model download up to 3 times with exponential backoff, then fail session startup if still unsuccessful
- Q: How should the plugin handle very long text inputs that might cause performance degradation or memory issues? → A: Configurable maximum length via pytest.ini (default 10,000 characters, fail if exceeded)
- Q: How should the cache handle concurrent read/write access when tests run in parallel (pytest-xdist)? → A: File-based locking mechanism for cache writes (workers wait for lock, reads are concurrent-safe)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Semantic Similarity Assertion (Priority: P1)

A developer testing an LLM-powered chatbot needs to verify that greeting responses are semantically correct without requiring exact string matches. They want to write a single assertion that passes for "Hello!", "Hi there!", or "Greetings!" when expecting a greeting.

**Why this priority**: This is the core value proposition - solving the fundamental problem of brittle LLM tests. Without this, the plugin has no value.

**Independent Test**: Can be fully tested by installing the plugin, writing a test with `assert_semantically_similar()`, running pytest, and verifying it passes for semantically equivalent texts and fails for semantically different texts.

**Acceptance Scenarios**:

1. **Given** a test file with `assert_semantically_similar("Hello!", "Hi there!", threshold=0.85)`, **When** pytest runs, **Then** the assertion passes
2. **Given** a test file with `assert_semantically_similar("Hello!", "Goodbye!", threshold=0.85)`, **When** pytest runs, **Then** the assertion fails with a clear error message showing similarity score
3. **Given** a test file with semantically equivalent texts in different wordings, **When** pytest runs, **Then** the assertion passes regardless of exact phrasing
4. **Given** a test file with a custom threshold of 0.90, **When** pytest runs, **Then** the assertion respects the specified threshold
5. **Given** a failed assertion, **When** pytest displays the error, **Then** the message shows expected text, actual text, similarity score, and threshold

---

### User Story 2 - Configuration via pytest.ini (Priority: P2)

A developer wants to set a project-wide default similarity threshold and embedding model without repeating configuration in every test. They configure these settings once in `pytest.ini` and all semantic assertions respect those defaults.

**Why this priority**: Configuration is essential for production use but the plugin is usable without it (using hardcoded defaults). This enables professional usage patterns.

**Independent Test**: Can be fully tested by creating a `pytest.ini` file with semantic assertion settings, writing tests without explicit configuration, and verifying the configured defaults are used.

**Acceptance Scenarios**:

1. **Given** a `pytest.ini` with `semantic_assert_threshold = 0.90`, **When** a test uses `assert_semantically_similar()` without a threshold parameter, **Then** the assertion uses 0.90 as the threshold
2. **Given** a `pytest.ini` with `semantic_assert_model = all-MiniLM-L6-v2`, **When** tests run, **Then** the specified embedding model is loaded once and reused across all tests
3. **Given** a `pytest.ini` with `semantic_assert_cache = true`, **When** the same text is compared multiple times, **Then** embeddings are cached and not recomputed
4. **Given** both configuration file defaults and explicit test parameters, **When** pytest runs, **Then** explicit parameters override configuration file defaults
5. **Given** invalid configuration values in `pytest.ini`, **When** pytest starts, **Then** pytest fails fast with a clear error message indicating the invalid setting

---

### User Story 3 - Compare Against Multiple Expected Values (Priority: P3)

A developer testing a chatbot farewell function wants to verify the response matches any of several acceptable farewells ("Goodbye!", "See you later!", "Have a great day!"). They use a single assertion that passes if the actual response is semantically similar to any option in the list.

**Why this priority**: This extends the core functionality for common testing patterns but isn't required for the MVP to deliver value.

**Independent Test**: Can be fully tested by writing a test with `assert_semantically_similar_to_any()` passing a list of expected values, and verifying it passes when the actual matches any option.

**Acceptance Scenarios**:

1. **Given** a test with `assert_semantically_similar_to_any("Bye!", ["Goodbye!", "See you later!", "Farewell!"], threshold=0.85)`, **When** pytest runs, **Then** the assertion passes
2. **Given** a test with actual text not matching any option in the list, **When** pytest runs, **Then** the assertion fails with an error showing similarity scores for each option
3. **Given** a test with an empty list of expected values, **When** pytest runs, **Then** the assertion fails with a clear error message
4. **Given** a test with a very large list of expected values (100+ items), **When** pytest runs, **Then** the assertion completes in under 5 seconds

---

### User Story 4 - Helpful Error Messages with Suggestions (Priority: P4)

A developer sees a failed semantic assertion and receives not just the similarity score, but contextual suggestions (e.g., "These texts have opposite meanings - consider using assert_contradicts()").

**Why this priority**: Enhances developer experience but core functionality works without it. This is polish for better usability.

**Independent Test**: Can be fully tested by creating failing assertions with specific patterns (opposites, unrelated texts, near-matches) and verifying appropriate suggestions appear in error messages.

**Acceptance Scenarios**:

1. **Given** a failed assertion comparing "Hello" and "Goodbye" (opposites), **When** pytest displays the error, **Then** the message suggests using `assert_contradicts()` for testing opposite meanings
2. **Given** a failed assertion with similarity score close to threshold (e.g., 0.83 vs 0.85), **When** pytest displays the error, **Then** the message indicates texts are nearly similar and suggests adjusting threshold
3. **Given** a failed assertion with very low similarity score (<0.3), **When** pytest displays the error, **Then** the message indicates texts are unrelated
4. **Given** a failed assertion, **When** pytest displays the error, **Then** the message includes the actual similarity score formatted to 2 decimal places

---

### Edge Cases

- Empty strings or text shorter than 3 characters MUST fail with error: "Cannot compute semantic similarity for empty or very short text - minimum 3 characters required"
- Texts exceeding configurable maximum length (default 10,000 characters via `semantic_assert_max_length`) MUST fail with error message indicating text length and configured limit
- Embedding model load failures MUST trigger up to 3 retry attempts with exponential backoff (1s, 2s, 4s); if all retries fail, pytest session startup MUST fail with actionable error message (check network connectivity, verify model name, check disk space for model cache)
- How does caching behave when the same text appears with different thresholds?
- What happens when the cache directory is not writable or disk is full?
- How should the .pytest-semantic-cache/ directory be handled in version control (.gitignore)?
- What happens when comparing texts in different languages (if model supports multilingual)?
- How are whitespace, newlines, and special characters handled in comparisons?
- Parallel test execution (pytest-xdist) MUST use file-based locking for cache writes to prevent corruption; multiple workers can read from cache concurrently; lock acquisition failures MUST timeout and fail with clear error after 5 seconds
- How does the plugin behave when no configuration is provided (zero-config mode)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Plugin MUST provide an `assert_semantically_similar(actual, expected, threshold)` function that compares two text strings using semantic similarity; MUST reject empty strings or text shorter than 3 characters with clear error message; MUST reject texts exceeding configurable maximum length (default 10,000 characters)
- **FR-002**: Plugin MUST compute similarity scores between 0.0 (completely different) and 1.0 (identical meaning)
- **FR-003**: Assertions MUST pass when similarity score meets or exceeds the threshold, fail otherwise
- **FR-004**: Plugin MUST provide clear failure messages showing: expected text, actual text, similarity score, and threshold
- **FR-005**: Plugin MUST support configuration via `pytest.ini` for default threshold, embedding model, and caching settings
- **FR-006**: Plugin MUST load embedding models once per pytest session and reuse across all tests; MUST retry model download up to 3 times with exponential backoff on failure, then fail session startup with clear error message if unsuccessful
- **FR-007**: Plugin MUST cache computed embeddings to avoid redundant computation for repeated texts; cache location configurable (project directory by default for team sharing, supports user home directory or in-memory options)
- **FR-008**: Plugin MUST provide an `assert_semantically_similar_to_any(actual, expected_list, threshold)` function for comparing against multiple expected values
- **FR-009**: Plugin MUST support custom thresholds per assertion that override configuration defaults
- **FR-010**: Plugin MUST validate configuration at pytest startup and fail fast with actionable error messages for invalid settings
- **FR-011**: Plugin MUST be thread-safe and support parallel test execution (pytest-xdist compatibility); cache writes MUST use file-based locking to prevent corruption, cache reads MUST be concurrent-safe
- **FR-012**: Plugin MUST work in zero-config mode with sensible defaults (threshold=0.85, default embedding model, caching enabled)

### Pytest Plugin Requirements

- **Plugin Registration**: Plugin discovered via entry point `[pytest11]` in `pyproject.toml`; hooks registered using `pytest_configure` and `pytest_addoption`
- **Configuration Options**:
  - `semantic_assert_threshold` (float, default 0.85): Default similarity threshold
  - `semantic_assert_model` (string, default "all-MiniLM-L6-v2"): Embedding model identifier
  - `semantic_assert_cache` (boolean, default true): Enable/disable embedding caching
  - `semantic_assert_cache_dir` (string, default ".pytest-semantic-cache/"): Cache storage location - supports project directory path (team-shareable), user home directory path, or "memory" for in-memory only caching
  - `semantic_assert_max_length` (integer, default 10000): Maximum text length in characters; texts exceeding this limit will fail with clear error message
- **Pytest Compatibility**: pytest 7.0+ (support for modern plugin hooks and configuration)
- **Python Compatibility**: Python 3.9, 3.10, 3.11, 3.12 (current maintained Python versions)

### Key Entities

- **Semantic Assertion**: Represents a comparison operation with actual text, expected text(s), threshold, and resulting similarity score
- **Embedding Cache**: Stores computed embeddings keyed by text content to avoid redundant computation
- **Similarity Score**: Numerical value (0.0-1.0) representing semantic closeness between two texts
- **Configuration**: Plugin settings including default threshold, model selection, and caching preferences

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can write a semantic assertion test in under 2 minutes after reading the README quickstart
- **SC-002**: Plugin installation and first test execution completes in under 30 seconds (including model download on first run)
- **SC-003**: Semantic assertions with cached embeddings complete in under 50 milliseconds per comparison
- **SC-004**: First-run semantic assertions (uncached) complete in under 200 milliseconds per comparison
- **SC-005**: Plugin maintains 100% test pass rate across pytest 7.0+ and Python 3.9-3.12 in CI
- **SC-006**: Error messages for failed assertions include all required information (expected, actual, score, threshold) in 100% of cases
- **SC-007**: Plugin successfully runs in parallel test execution mode without race conditions or cache corruption
- **SC-008**: Zero-config usage (no pytest.ini) works immediately after installation for 100% of users
- **SC-009**: Configuration validation catches 100% of invalid settings before any tests execute
- **SC-010**: Plugin package installs successfully from PyPI with zero post-install configuration required

### Assumptions

- Developers have basic pytest knowledge (how to write tests, run pytest, read pytest output)
- Developers are testing English language text outputs (primary use case, though model may support other languages)
- Test environments have network access on first run for downloading embedding models (subsequent runs work offline with cached models)
- Semantic similarity using cosine distance on embeddings is sufficient for most LLM testing use cases
- Default threshold of 0.85 provides reasonable balance between strictness and flexibility for most use cases
