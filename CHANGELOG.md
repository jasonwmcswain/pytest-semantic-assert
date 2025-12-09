# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial MVP implementation of pytest-semantic-assert
- Core assertion functions:
  - `assert_semantically_similar(actual, expected, threshold)` - Synchronous version
  - `assert_semantically_similar_to_any(actual, expected_list, threshold)` - Multi-value version
  - `assert_semantically_similar_async(actual, expected, threshold)` - Async version (NEW!)
  - `assert_semantically_similar_to_any_async(actual, expected_list, threshold)` - Async multi-value (NEW!)
- Async/await support for agentic LLM testing workflows
  - Runs assertions in thread pool to avoid blocking event loop
  - Compatible with pytest-asyncio
  - Supports parallel async assertions with asyncio.gather()
- Configuration via pytest.ini/pyproject.toml:
  - `semantic_assert_threshold` (default: 0.85)
  - `semantic_assert_model` (default: "all-MiniLM-L6-v2")
  - `semantic_assert_cache` (default: true)
  - `semantic_assert_cache_dir` (default: ".pytest-semantic-cache/")
  - `semantic_assert_max_length` (default: 10000)
- Disk-based embedding cache with file locking for parallel execution safety
- Session-scoped embedding model lifecycle management
- Detailed error messages with contextual suggestions
- Support for pytest 7.0+ and Python 3.9-3.12
- Comprehensive test suite: 256 tests (unit, integration, contract, E2E, async)

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [0.1.0] - TBD

Initial MVP release - semantic assertions for LLM testing

### Features
- Embedding-based semantic similarity comparison using all-MiniLM-L6-v2
- Configurable similarity thresholds (0.0-1.0)
- Persistent disk cache for embeddings
- Parallel test execution support (pytest-xdist compatible)
- Zero-config defaults for instant productivity

---

**Legend**:
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes

