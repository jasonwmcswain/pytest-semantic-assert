<!--
Sync Impact Report - Constitution v1.0.0 (Initial Ratification)
================================================================================
Version Change: [TEMPLATE] → 1.0.0
Rationale: Initial constitution for pytest-semantic-assert PyPI package

Principles Defined:
  1. PyPI Package Excellence - Quality standards for public package distribution
  2. Pytest Integration First - Plugin architecture and pytest compatibility
  3. Test-Driven Development (TDD) - Non-negotiable testing discipline
  4. Semantic Versioning & Backwards Compatibility - API stability guarantees
  5. Developer Experience (DX) - Ease of use and helpful error messages
  6. Performance & Efficiency - Speed and resource optimization for CI/CD
  7. Documentation as Code - Comprehensive, tested, versioned documentation

Additional Sections:
  - PyPI Distribution Standards
  - Development Workflow
  - Quality Gates

Templates Requiring Updates:
  ✅ plan-template.md - Updated with PyPI-specific constitution checks
  ✅ spec-template.md - Aligned with pytest plugin requirements
  ✅ tasks-template.md - Updated with package development task categories

Deferred Items: None

Last Updated: 2025-12-06
================================================================================
-->

# pytest-semantic-assert Constitution

## Core Principles

### I. PyPI Package Excellence

Every component MUST meet public package distribution standards:

- **Package Quality**: Type hints for all public APIs; comprehensive docstrings following Google/NumPy style; zero linter errors (ruff, mypy) before release
- **Distribution Standards**: Valid `pyproject.toml` with complete metadata (description, keywords, classifiers, license); semantic versioning strictly enforced; changelog maintained for every release
- **Dependency Management**: Minimal dependencies in core package; optional dependencies properly declared (`pip install pytest-semantic-assert[llm]`); pinned versions for reproducibility in dev/test
- **Security**: No hardcoded secrets or API keys; secure credential handling via environment variables; vulnerability scanning in CI pipeline

**Rationale**: Public packages represent the project professionally and must instill confidence in production use.

### II. Pytest Integration First

All features MUST integrate naturally with pytest's ecosystem:

- **Plugin Architecture**: Standard pytest plugin hooks (`pytest_configure`, `pytest_addoption`, etc.); discoverable via entry points (`[pytest11]` in `pyproject.toml`)
- **Native Pytest Feel**: Assertion helpers follow pytest conventions (`assert_*` naming); failure messages use pytest's assertion introspection format; configuration via `pytest.ini`/`pyproject.toml`
- **Fixture Support**: Core functionality exposed as fixtures (e.g., `semantic_snapshot`); fixtures properly scoped (function/class/module/session); cleanup handled via fixture teardown
- **Compatibility**: Support pytest 7.0+ and Python 3.9+; test against multiple pytest/Python version combinations in CI; no breaking changes to pytest's internal APIs

**Rationale**: Users expect pytest plugins to feel native, not bolted-on. Seamless integration reduces friction and adoption barriers.

### III. Test-Driven Development (TDD) - NON-NEGOTIABLE

Every feature MUST be test-driven:

- **Red-Green-Refactor Cycle**: Tests written FIRST → User/stakeholder approval → Tests FAIL → Implementation → Tests PASS → Refactor
- **Test Coverage Requirements**: Minimum 90% coverage for core assertion logic; 100% coverage for public API surfaces; edge cases and error paths explicitly tested
- **Test Categories**:
  - **Unit Tests**: Fast, isolated tests for individual functions/classes
  - **Integration Tests**: Plugin integration with pytest runtime
  - **Contract Tests**: Public API stability (detect breaking changes)
  - **End-to-End Tests**: Real-world usage scenarios (embedding models, LLM calls)
- **Test Documentation**: Each test file includes docstring explaining what is tested and why; complex test scenarios documented with rationale

**Rationale**: TDD ensures correctness, prevents regressions, and serves as living documentation. Non-negotiable for library code used in production testing.

### IV. Semantic Versioning & Backwards Compatibility

Version numbers MUST follow SemVer (MAJOR.MINOR.PATCH):

- **MAJOR (X.0.0)**: Breaking changes to public API (removed functions, changed signatures, behavior changes)
- **MINOR (0.X.0)**: New features, new public APIs (backwards compatible)
- **PATCH (0.0.X)**: Bug fixes, performance improvements (no API changes)
- **Pre-release**: Use `-alpha`, `-beta`, `-rc` suffixes for unstable releases (e.g., `1.0.0-beta.1`)
- **Deprecation Policy**: Deprecated APIs MUST include version number when removed (e.g., "Deprecated in 2.1, will be removed in 3.0"); minimum one MINOR version notice before removal; deprecation warnings via Python's `warnings` module

**Rationale**: Users depend on stable APIs. Breaking changes without warning erode trust and cause production failures.

### V. Developer Experience (DX)

Every interaction MUST prioritize developer productivity:

- **Error Messages**: Actionable, specific error messages with suggestions (e.g., "Similarity score 0.23 below threshold 0.85. Suggestion: texts have opposite meanings, consider assert_contradicts()")
- **Clear APIs**: Self-documenting function names; type hints for IDE autocomplete; minimal required arguments (sensible defaults)
- **Configuration**: Convention over configuration (zero config for common cases); explicit configuration for advanced use cases; validate configuration at pytest startup (fail fast)
- **Debugging**: Verbose mode showing similarity scores, embeddings used, LLM calls made; `--semantic-assert-debug` flag for troubleshooting; clear failure diffs showing expected vs actual

**Rationale**: Poor DX leads to frustration, support burden, and abandoned adoption. Great DX drives adoption and positive word-of-mouth.

### VI. Performance & Efficiency

Every feature MUST be optimized for CI/CD environments:

- **Speed Targets**: Embedding comparison <50ms for cached embeddings; first-run embedding generation <200ms (local model); configurable timeouts for LLM fallbacks
- **Resource Efficiency**: Embedding models loaded once per pytest session (not per test); disk cache for computed embeddings (avoid re-computation); memory-efficient batch processing for lists/JSON
- **CI/CD Optimization**: Embedding models cacheable in CI (pip cache, docker layers); optional offline mode (no network calls); parallel test execution safe (thread-safe, process-safe)
- **Cost Awareness**: LLM calls opt-in only (default to local embeddings); cost tracking for LLM calls (warn if threshold exceeded); retry logic with exponential backoff

**Rationale**: Slow tests kill productivity. CI/CD environments demand fast, resource-efficient testing.

### VII. Documentation as Code

Documentation MUST be comprehensive, tested, and versioned:

- **README Excellence**: Clear problem statement; 30-second quickstart example; installation instructions; link to full docs
- **API Documentation**: Auto-generated from docstrings (Sphinx/mkdocs); type hints visible in docs; examples for every public function
- **User Guides**: Quickstart tutorial; configuration guide; advanced usage patterns; migration guides for breaking changes
- **Tested Examples**: All code examples in docs MUST be tested (doctest or integration tests); examples tested against current version in CI
- **Changelog**: Keep CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/); entries categorized (Added, Changed, Deprecated, Removed, Fixed, Security)

**Rationale**: Documentation is the first touchpoint for users. Untested docs become stale and erode trust.

## PyPI Distribution Standards

All releases MUST meet these criteria before publication:

- **Package Metadata**: Complete `pyproject.toml` with project description, keywords (pytest, testing, LLM, semantic, assertions), classifiers (Development Status, Intended Audience, License, Python versions), author/maintainer info with email
- **License**: OSI-approved open source license (MIT recommended for libraries); LICENSE file in repository root; license classifier in `pyproject.toml`
- **Build System**: PEP 517/518 compliant build (`build-system` in `pyproject.toml`); use modern build tools (hatch, poetry, or setuptools with pyproject.toml)
- **Testing Before Release**: All tests pass (unit, integration, contract, E2E); tests run on all supported Python versions (3.9, 3.10, 3.11, 3.12); linter/type-checker passes with zero errors
- **Version Tagging**: Git tag matches package version (e.g., `v1.2.3`); tag includes release notes; tag signed with GPG (recommended)

## Development Workflow

### Feature Development

1. **Specification**: Feature spec created (`/speckit.specify`) with user stories and acceptance criteria
2. **Planning**: Implementation plan created (`/speckit.plan`) with technical approach and constitution check
3. **Test Writing**: Tests written FIRST (TDD), user approves test cases, verify tests FAIL
4. **Implementation**: Code written to pass tests (red-green-refactor cycle)
5. **Review**: Code review checklist: tests pass, coverage met, docs updated, changelog entry added, constitution compliance verified
6. **Merge**: Squash or merge commits to main branch; delete feature branch

### Release Process

1. **Pre-release Checks**: All tests passing on all supported versions; changelog updated with release notes; version bumped in `pyproject.toml` and `__init__.py`
2. **Build**: Clean build (`python -m build`); verify package contents (`tar -tzf dist/*.tar.gz`)
3. **Test Release**: Upload to TestPyPI (`twine upload --repository testpypi dist/*`); install from TestPyPI and smoke test
4. **Production Release**: Upload to PyPI (`twine upload dist/*`); create GitHub release with changelog; announce on relevant channels (pytest-dev, Reddit, Twitter)
5. **Post-Release**: Verify installation (`pip install pytest-semantic-assert`); monitor GitHub issues for immediate feedback

## Quality Gates

### Constitution Compliance Checklist

Every feature MUST pass before merge:

- [ ] **PyPI Package Excellence**: Type hints on public APIs; docstrings present; linters pass; dependencies justified
- [ ] **Pytest Integration First**: Uses pytest hooks/fixtures; follows pytest conventions; tested with pytest 7.0+
- [ ] **Test-Driven Development**: Tests written first; >90% coverage; all test categories covered
- [ ] **Semantic Versioning**: Version bumped correctly; breaking changes documented; deprecation warnings added (if applicable)
- [ ] **Developer Experience**: Error messages actionable; examples included; configuration validated
- [ ] **Performance & Efficiency**: Speed targets met; caching implemented; CI/CD optimized
- [ ] **Documentation as Code**: README updated; docstrings complete; examples tested; changelog entry added

### Pull Request Requirements

Every PR MUST include:

- [ ] Description of change (what, why, how)
- [ ] Tests passing (CI green)
- [ ] Test coverage maintained or improved
- [ ] Documentation updated (if API changes)
- [ ] Changelog entry (if user-facing change)
- [ ] Breaking change notice (if applicable)
- [ ] Constitution compliance (checklist above)

### Complexity Justification

If a feature violates simplicity principles (YAGNI, KISS), PR MUST include:

- **What**: Specific complexity being added (e.g., new dependency, abstraction layer, configuration option)
- **Why Needed**: Problem that simpler approach cannot solve
- **Alternatives Rejected**: Why simpler alternatives were insufficient
- **Mitigation**: How complexity is minimized (clear docs, examples, sensible defaults)

## Governance

### Amendment Process

Constitution changes require:

1. **Proposal**: GitHub issue describing proposed change with rationale
2. **Discussion**: Minimum 7-day comment period for stakeholder feedback
3. **Approval**: Maintainer consensus (simple majority for MINOR version bumps, unanimous for MAJOR)
4. **Documentation**: Constitution version bumped (SemVer rules apply); sync impact report generated; dependent templates updated
5. **Migration**: Migration guide for impacted workflows (if applicable)

### Compliance Reviews

- **Per Feature**: Constitution checklist required in every PR
- **Quarterly**: Audit codebase for drift from constitution principles
- **Pre-Release**: Full compliance review before MAJOR/MINOR version releases

### Enforcement

- Pull requests failing constitution checks will be blocked until compliant
- Maintainers responsible for enforcing standards during code review
- Users can file issues for constitution violations in released code

---

**Version**: 1.0.0 | **Ratified**: 2025-12-06 | **Last Amended**: 2025-12-06
