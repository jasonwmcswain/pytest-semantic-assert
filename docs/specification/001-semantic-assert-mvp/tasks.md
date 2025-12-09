# Tasks: Semantic Assertions for LLM Testing

**Input**: Design documents from `/specs/001-semantic-assert-mvp/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/api.md, research.md

**Tests**: TDD approach - tests written FIRST before implementation per constitution requirement

**Organization**: Tasks grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single Python package**: `pytest_semantic_assert/`, `tests/` at repository root
- Project uses modern `src/` layout per plan.md
- Entry point: `[pytest11]` in `pyproject.toml`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per plan.md (src/, tests/, docs/)
- [x] T002 Initialize pyproject.toml with metadata, dependencies (pytest>=7.0, sentence-transformers, numpy, filelock), and [pytest11] entry point
- [x] T003 [P] Create Makefile with developer workflow commands including: help (show all targets), venv (create virtual environment), format (black formatting), ruff-check/ruff-fix (linting), unittest/unit-test/integration-test/contract-test/e2e-test (testing with coverage), coverage-combined (combined coverage report), validate (all checks), clean (remove build artifacts and cache), version-show/version-bump (version management), build/package (build distribution), publish-test/publish (PyPI publishing), all (complete pipeline)
- [x] T004 [P] Create README.md with quickstart example and installation instructions
- [x] T005 [P] Create CHANGELOG.md with v0.1.0 entry
- [x] T006 [P] Create LICENSE file (MIT license)
- [x] T007 [P] Create .gitignore excluding .pytest-semantic-cache/, __pycache__, *.pyc, .tox/, dist/, *.egg-info
- [x] T008 [P] Configure ruff for linting in pyproject.toml ([tool.ruff])
- [x] T009 [P] Configure mypy for strict type checking in pyproject.toml ([tool.mypy])
- [x] T010 [P] Setup tox.ini for multi-version testing (Python 3.9-3.12, pytest 7.0+)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T011 [P] Create pytest_semantic_assert/__init__.py with __version__ = "0.1.0" and public API exports
- [x] T012 [P] Create pytest_semantic_assert/exceptions.py with custom exception classes (TextTooShortError, TextTooLongError, ModelLoadError)
- [x] T013 Create pytest_semantic_assert/similarity.py with cosine_similarity function using numpy
- [x] T014 Write unit test tests/unit/test_similarity.py for cosine similarity (test identical vectors, orthogonal vectors, similar vectors)
- [x] T015 Create pytest_semantic_assert/config.py with Configuration class to load/validate pytest.ini options
- [x] T016 Write unit test tests/unit/test_config.py for configuration loading and validation (test default values, invalid threshold, invalid max_length)
- [x] T017 Create pytest_semantic_assert/cache.py with EmbeddingCache class (file-based with filelock, in-memory mode support)
- [x] T018 Write unit test tests/unit/test_cache.py for cache operations (test set/get, file locking, memory mode, cache key generation)
- [x] T019 Create pytest_semantic_assert/embeddings.py with EmbeddingManager class (lazy model loading, retry logic with exponential backoff)
- [x] T020 Write unit test tests/unit/test_embeddings.py with mocked SentenceTransformer (test lazy loading, retry logic, cache integration, text validation)
- [x] T021 Create pytest_semantic_assert/plugin.py with pytest_addoption hook to register ini options
- [x] T022 Add pytest_configure hook to plugin.py to load configuration and validate settings at session start

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Semantic Similarity Assertion (Priority: P1) 🎯 MVP

**Goal**: Enable developers to assert semantic similarity between two texts with configurable threshold

**Independent Test**: Install plugin, write test with `assert_semantically_similar()`, run pytest, verify pass/fail behavior

### Tests for User Story 1 (TDD - Write FIRST) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T023 [P] [US1] Write contract test in tests/contract/test_public_api.py to verify assert_semantically_similar signature stability
- [x] T024 [P] [US1] Write integration test in tests/integration/test_assertions.py for basic assertion (pass case: similar texts)
- [x] T025 [P] [US1] Write integration test in tests/integration/test_assertions.py for basic assertion (fail case: different texts with error message validation)
- [x] T026 [P] [US1] Write E2E test in tests/e2e/test_user_stories.py for US1 acceptance scenario 1 (semantically similar texts pass)
- [x] T027 [P] [US1] Write E2E test in tests/e2e/test_user_stories.py for US1 acceptance scenario 2 (different texts fail with score shown)
- [x] T028 [P] [US1] Write E2E test in tests/e2e/test_user_stories.py for US1 acceptance scenario 3 (equivalent texts in different wordings pass)
- [x] T029 [P] [US1] Write E2E test in tests/e2e/test_user_stories.py for US1 acceptance scenario 4 (custom threshold respected)
- [x] T030 [P] [US1] Write E2E test in tests/e2e/test_user_stories.py for US1 acceptance scenario 5 (failure message shows all required fields)

### Implementation for User Story 1

- [x] T031 [US1] Implement assert_semantically_similar function in pytest_semantic_assert/assertions.py with signature from API contract
- [x] T032 [US1] Add input validation to assert_semantically_similar (min 3 chars, max configurable length, raise ValueError)
- [x] T033 [US1] Implement embedding retrieval via EmbeddingManager in assert_semantically_similar
- [x] T034 [US1] Implement similarity score computation using SimilarityCalculator in assert_semantically_similar
- [x] T035 [US1] Implement threshold comparison and AssertionError raising with 3-part message format (what failed, details, suggestion placeholder)
- [x] T036 [US1] Add assert_semantically_similar to public API exports in pytest_semantic_assert/__init__.py
- [x] T037 [US1] Add type hints and comprehensive docstring to assert_semantically_similar per API contract
- [x] T038 [US1] Write edge case test in tests/e2e/test_edge_cases.py for text too short (<3 chars)
- [x] T039 [US1] Write edge case test in tests/e2e/test_edge_cases.py for text too long (>max_length)
- [x] T040 [US1] Write edge case test in tests/e2e/test_edge_cases.py for model load failure (with mocked retry logic)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Configuration via pytest.ini (Priority: P2)

**Goal**: Enable project-wide defaults via pytest.ini configuration with zero-config fallback

**Independent Test**: Create pytest.ini with settings, write tests without explicit parameters, verify configured defaults used

### Tests for User Story 2 (TDD - Write FIRST) ⚠️

- [x] T041 [P] [US2] Write integration test in tests/integration/test_configuration.py for pytest.ini threshold override
- [x] T042 [P] [US2] Write integration test in tests/integration/test_configuration.py for pytest.ini model selection
- [x] T043 [P] [US2] Write integration test in tests/integration/test_configuration.py for pytest.ini cache settings
- [x] T044 [P] [US2] Write integration test in tests/integration/test_configuration.py for explicit param overriding pytest.ini default
- [x] T045 [P] [US2] Write integration test in tests/integration/test_configuration.py for invalid configuration (threshold out of range)
- [x] T046 [P] [US2] Write E2E test in tests/e2e/test_user_stories.py for US2 acceptance scenario 1 (threshold from pytest.ini)
- [x] T047 [P] [US2] Write E2E test in tests/e2e/test_user_stories.py for US2 acceptance scenario 2 (model loaded once and reused)
- [x] T048 [P] [US2] Write E2E test in tests/e2e/test_user_stories.py for US2 acceptance scenario 3 (embeddings cached when enabled)
- [x] T049 [P] [US2] Write E2E test in tests/e2e/test_user_stories.py for US2 acceptance scenario 4 (explicit params override config)
- [x] T050 [P] [US2] Write E2E test in tests/e2e/test_user_stories.py for US2 acceptance scenario 5 (invalid config fails at startup)

### Implementation for User Story 2

- [x] T051 [US2] Update pytest_configure hook in pytest_semantic_assert/plugin.py to create session-scoped EmbeddingManager
- [x] T052 [US2] Update assert_semantically_similar in pytest_semantic_assert/assertions.py to use configuration defaults when threshold is None
- [x] T053 [US2] Implement configuration validation in pytest_semantic_assert/config.py (threshold range check, model name non-empty, max_length positive)
- [x] T054 [US2] Add pytest.UsageError raising in pytest_configure for invalid configuration values with actionable messages
- [x] T055 [US2] Update EmbeddingManager in pytest_semantic_assert/embeddings.py to respect cache_enabled and cache_dir config
- [x] T056 [US2] Add session cleanup in pytest_unconfigure hook in pytest_semantic_assert/plugin.py to unload model
- [x] T057 [US2] Write integration test in tests/integration/test_plugin_hooks.py to verify pytest_configure loads config correctly
- [x] T058 [US2] Write integration test in tests/integration/test_plugin_hooks.py to verify zero-config mode works with defaults

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Compare Against Multiple Expected Values (Priority: P3)

**Goal**: Enable comparison against list of acceptable responses with short-circuit optimization

**Independent Test**: Call `assert_semantically_similar_to_any()` with list, verify passes on any match and fails with all scores shown

### Tests for User Story 3 (TDD - Write FIRST) ⚠️

- [x] T059 [P] [US3] Write contract test in tests/contract/test_public_api.py to verify assert_semantically_similar_to_any signature stability
- [x] T060 [P] [US3] Write integration test in tests/integration/test_assertions.py for multi-value assertion (pass case: matches one option)
- [x] T061 [P] [US3] Write integration test in tests/integration/test_assertions.py for multi-value assertion (fail case: no match, all scores shown)
- [x] T062 [P] [US3] Write E2E test in tests/e2e/test_user_stories.py for US3 acceptance scenario 1 (matches one semantically similar option)
- [x] T063 [P] [US3] Write E2E test in tests/e2e/test_user_stories.py for US3 acceptance scenario 2 (no match shows scores for all options)
- [x] T064 [P] [US3] Write E2E test in tests/e2e/test_user_stories.py for US3 acceptance scenario 3 (empty list raises clear error)
- [x] T065 [P] [US3] Write E2E test in tests/e2e/test_user_stories.py for US3 acceptance scenario 4 (100+ item list completes in <5s)

### Implementation for User Story 3

- [x] T066 [US3] Implement assert_semantically_similar_to_any function in pytest_semantic_assert/assertions.py with signature from API contract
- [x] T067 [US3] Add input validation to assert_semantically_similar_to_any (non-empty list, each item 3-max_length chars)
- [x] T068 [US3] Implement short-circuit matching logic (stop on first match above threshold)
- [x] T069 [US3] Implement error message showing all similarity scores sorted by score (highest first)
- [x] T070 [US3] Add assert_semantically_similar_to_any to public API exports in pytest_semantic_assert/__init__.py
- [x] T071 [US3] Add type hints and comprehensive docstring to assert_semantically_similar_to_any per API contract
- [x] T072 [US3] Optimize for large lists using batch embedding computation (if performance test fails)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Helpful Error Messages with Suggestions (Priority: P4)

**Goal**: Provide contextual suggestions in error messages based on similarity score patterns

**Independent Test**: Create failing assertions with specific patterns, verify appropriate suggestions appear

### Tests for User Story 4 (TDD - Write FIRST) ⚠️

- [x] T073 [P] [US4] Write E2E test in tests/e2e/test_user_stories.py for US4 acceptance scenario 1 (opposite texts suggest assert_contradicts)
- [x] T074 [P] [US4] Write E2E test in tests/e2e/test_user_stories.py for US4 acceptance scenario 2 (near-miss suggests adjusting threshold)
- [x] T075 [P] [US4] Write E2E test in tests/e2e/test_user_stories.py for US4 acceptance scenario 3 (very low score indicates unrelated)
- [x] T076 [P] [US4] Write E2E test in tests/e2e/test_user_stories.py for US4 acceptance scenario 4 (score formatted to 2 decimals)
- [x] T077 [P] [US4] Write unit test in tests/unit/test_assertions.py for _suggest_action function with various score ranges

### Implementation for User Story 4

- [x] T078 [US4] Implement _suggest_action helper function in pytest_semantic_assert/assertions.py
- [x] T079 [US4] Add score-based suggestion logic (<0.3 unrelated, 0.3-0.6 somewhat related, 0.6-threshold near-miss)
- [x] T080 [US4] Update _format_error_message in pytest_semantic_assert/assertions.py to include contextual suggestion
- [x] T081 [US4] Format similarity score to 2 decimal places in error messages
- [x] T082 [US4] Add suggestion for opposite meanings detection (basic heuristic for "hello" vs "goodbye" patterns)
- [x] T083 [US4] Update error messages in assert_semantically_similar_to_any to include suggestions

**Checkpoint**: All user stories complete with polished error messages

---

## Phase 7: Parallel Execution Support

**Purpose**: Ensure pytest-xdist compatibility with file locking

- [x] T084 [P] Write integration test in tests/integration/test_parallel.py for pytest-xdist compatibility (multiple workers, no cache corruption)
- [x] T085 [P] Write integration test in tests/integration/test_parallel.py for cache lock timeout behavior (5 second timeout)
- [x] T086 Verify file locking implementation in pytest_semantic_assert/cache.py uses FileLock with 5s timeout
- [x] T087 Add concurrent read safety test (multiple workers reading same cache file simultaneously)
- [x] T088 Add lock contention test (multiple workers computing same embedding simultaneously)

---

## Phase 8: Edge Cases & Error Handling

**Purpose**: Comprehensive edge case coverage per spec requirements

- [x] T089 [P] Write edge case test in tests/e2e/test_edge_cases.py for whitespace/newline handling (normalize before comparison)
- [x] T090 [P] Write edge case test in tests/e2e/test_edge_cases.py for special characters handling
- [x] T091 [P] Write edge case test in tests/e2e/test_edge_cases.py for cache directory not writable (fallback or clear error)
- [x] T092 [P] Write edge case test in tests/e2e/test_edge_cases.py for disk full during cache write
- [x] T093 [P] Write edge case test in tests/e2e/test_edge_cases.py for same text with different thresholds (cache hit, different results)
- [x] T094 Implement whitespace normalization in pytest_semantic_assert/assertions.py (strip + collapse multiple spaces)
- [x] T095 Add error handling for cache write failures (log warning, continue without caching)
- [x] T096 Add network error handling for model download (clear troubleshooting message)

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T097 [P] Update README.md with comprehensive examples from quickstart.md
- [x] T098 [P] Generate API documentation from docstrings using Sphinx (setup docs/ directory)
- [x] T099 [P] Add .pytest-semantic-cache/ to .gitignore recommendations in README
- [x] T100 [P] Create example test files in examples/ directory demonstrating all features
- [x] T101 Code cleanup and refactoring for readability
- [x] T102 Performance profiling (verify <50ms cached, <200ms uncached targets met)
- [x] T103 [P] Add debug mode support (--semantic-assert-debug flag to show scores, model info)
- [x] T104 Run full test suite with coverage report (verify >90% coverage)
- [x] T105 Run tox across all Python versions (3.9, 3.10, 3.11, 3.12) and pytest versions
- [x] T106 Validate quickstart.md examples are executable (doctest or copy to test file)
- [x] T107 Security scan for dependencies (check for known vulnerabilities)

---

## Phase 10: PyPI Package Release Preparation

**Purpose**: Prepare package for public distribution

**Prerequisites**: All user stories complete, tests passing, documentation complete

- [x] T108 Verify all type hints on public APIs (run mypy --strict)
- [x] T109 Generate API documentation HTML from docstrings (Sphinx build)
- [x] T110 Validate pyproject.toml metadata completeness (description, keywords, classifiers, license, URLs)
- [x] T111 Update CHANGELOG.md with v0.1.0 release notes (Added, Changed, Fixed sections)
- [x] T112 Version bump verification (version in pyproject.toml matches __init__.py)
- [x] T113 Create git tag v0.1.0 with release notes
- [x] T114 Build package (python -m build)
- [x] T115 Verify package contents (tar -tzf dist/*.tar.gz, check files included/excluded)
- [x] T116 Upload to TestPyPI (twine upload --repository testpypi dist/*)
- [x] T117 Install from TestPyPI and smoke test (pip install from TestPyPI, run quickstart example)
- [x] T118 Upload to PyPI (twine upload dist/*)
- [x] T119 Create GitHub release with CHANGELOG entry
- [x] T120 Monitor initial feedback and GitHub issues

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Parallel Execution (Phase 7)**: Can proceed after US1 complete (needs cache implementation)
- **Edge Cases (Phase 8)**: Can proceed in parallel with user stories
- **Polish (Phase 9)**: Depends on all desired user stories being complete
- **Release (Phase 10)**: Depends on Polish phase completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Enhances US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Extends US1 pattern but independent
- **User Story 4 (P4)**: Can start after US1 complete (enhances error messages from US1)

### Within Each User Story

- Tests (TDD) MUST be written and FAIL before implementation
- Models/utilities before services
- Core implementation before error handling enhancements
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (Phase 1)
- All Foundational tasks marked [P] can run in parallel within their execution order (Phase 2)
- Once Foundational phase completes, User Stories 1, 2, 3 can start in parallel (Phase 3-5)
- User Story 4 should wait for US1 implementation to complete
- All tests for a user story marked [P] can be written in parallel
- Edge case tests (Phase 8) can be written in parallel with user story implementation
- Polish tasks (Phase 9) marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# After Foundational phase complete, launch all US1 tests together (TDD):
T023: Contract test for assert_semantically_similar signature
T024: Integration test for pass case
T025: Integration test for fail case
T026-T030: E2E tests for all acceptance scenarios
# (All marked [P] can run in parallel)

# After tests written and failing, launch parallel implementation:
T031: Implement core function
T032-T035: Add features in dependency order
T036-T037: Documentation and exports
T038-T040: Edge case tests in parallel
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (1-2 days)
2. Complete Phase 2: Foundational (2-3 days)
3. Complete Phase 3: User Story 1 (3-5 days)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Demo/validate with stakeholders

**Total MVP Timeline**: ~7-10 days

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (3-5 days)
2. Add User Story 1 → Test independently → MVP complete (3-5 days)
3. Add User Story 2 → Test independently → Config support added (2-3 days)
4. Add User Story 3 → Test independently → Multi-value support added (2-3 days)
5. Add User Story 4 → Test independently → Polished errors (1-2 days)
6. Polish + Release → Production ready (3-5 days)

**Total Full Implementation**: ~15-25 days (3-5 weeks)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (3-5 days)
2. Once Foundational is done:
   - Developer A: User Story 1 (P1)
   - Developer B: User Story 2 (P2) in parallel
   - Developer C: User Story 3 (P3) in parallel
   - Developer D: Edge cases (Phase 8) in parallel
3. User Story 4 (P4) after US1 complete (enhances US1 errors)
4. Team converges on Polish + Release

**Total with Parallelization**: ~12-20 days (2.5-4 weeks)

---

## Notes

- [P] tasks = different files, no dependencies (safe to parallelize)
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD CRITICAL**: Tests MUST be written first and verified to fail
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Performance targets (<50ms cached, <200ms uncached) verified in Phase 9
- Contract tests ensure API stability across versions

---

## Task Count Summary

- **Total Tasks**: 120
- **Phase 1 (Setup)**: 10 tasks
- **Phase 2 (Foundational)**: 12 tasks
- **Phase 3 (User Story 1)**: 18 tasks (9 tests + 9 implementation)
- **Phase 4 (User Story 2)**: 18 tasks (10 tests + 8 implementation)
- **Phase 5 (User Story 3)**: 14 tasks (7 tests + 7 implementation)
- **Phase 6 (User Story 4)**: 11 tasks (6 tests + 6 implementation)
- **Phase 7 (Parallel Execution)**: 5 tasks
- **Phase 8 (Edge Cases)**: 8 tasks
- **Phase 9 (Polish)**: 11 tasks
- **Phase 10 (Release)**: 13 tasks

**Parallel Opportunities**: 45+ tasks marked [P] can run concurrently

**Independent Test Criteria**:
- **US1**: Install plugin, write basic assertion test, verify pass/fail behavior
- **US2**: Create pytest.ini, verify configured defaults used without explicit params
- **US3**: Write test with list of expected values, verify matching behavior
- **US4**: Create failing tests, verify contextual suggestions in error messages

**Suggested MVP Scope**: Phase 1-3 (User Story 1 only) = ~31 tasks, deliverable in 7-10 days

