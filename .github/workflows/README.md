# GitHub Workflows

This repository uses GitHub Actions for continuous integration and publishing to PyPI.

## Workflows

### 1. Pull Request Checks ([pr-check.yml](./pr-check.yml))

**Triggered on:** Pull requests to `main` or `develop` branches

**Jobs:**
- **Lint**: Runs Black, Ruff, and MyPy checks
- **Test**: Runs the full test suite on multiple Python versions (3.9-3.12) and operating systems (Ubuntu, Windows, macOS)
- **Build**: Verifies the package can be built and checks it with twine

**Matrix:**
- OS: ubuntu-latest, windows-latest, macos-latest
- Python: 3.9, 3.10, 3.11, 3.12

**Note**: On Ubuntu runners, the workflow frees up disk space before installing dependencies to handle large ML packages like PyTorch and CUDA libraries.

### 2. CI ([ci.yml](./ci.yml))

**Triggered on:** Pushes to `main` branch (non-tag)

**Jobs:**
- Quick health check including linting, type checking, and tests
- Runs on Python 3.11 + Ubuntu only for faster feedback
- Includes disk space cleanup for ML dependencies

### 3. Publish to PyPI ([publish.yml](./publish.yml))

**Triggered on:**
- Pushes to `main` branch
- Tags matching `v*` pattern (e.g., `v0.1.2`)

**Jobs:**
1. **Validate Release**
   - Extracts version from `pyproject.toml`
   - Verifies tag version matches package version
   - Only proceeds to publish if tag matches exactly

2. **Full Test Suite**
   - Runs complete test suite with coverage
   - Enforces 80% coverage threshold
   - Includes disk space cleanup

3. **Build and Publish** (only on matching tags)
   - Builds distribution packages
   - Publishes to PyPI using trusted publishing
   - Requires GitHub environment `pypi` to be configured

4. **Test Installation** (after successful publish)
   - Installs package from PyPI on all supported Python versions and OS
   - Verifies the installation works correctly

## Disk Space Management

This project depends on large ML packages (PyTorch, CUDA libraries, sentence-transformers) that can exceed 3GB. The workflows include automated disk space cleanup on Ubuntu runners to prevent "No space left on device" errors:

- Removes .NET, GHC, Boost libraries (not needed for Python tests)
- Uses `--no-cache-dir` with pip to avoid caching large packages
- Frees up several GB of space before installing dependencies

## Setup Requirements

### 1. Configure PyPI Trusted Publishing

To enable automated publishing, you need to configure trusted publishing in your PyPI account:

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher with these settings:
   - **PyPI Project Name**: `pytest-semantic-assert`
   - **Owner**: `<your-github-username>`
   - **Repository name**: `pytest-semantic-assert`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`

### 2. Create GitHub Environment

1. Go to your repository's Settings → Environments
2. Create a new environment named `pypi`
3. (Optional) Add protection rules like "Required reviewers"

### 3. Configure Secrets (Optional)

The workflows use PyPI's trusted publishing (recommended), which doesn't require API tokens. However, if you need to use API tokens instead:

1. Generate a PyPI API token at https://pypi.org/manage/account/token/
2. Add it to your repository as a secret named `PYPI_API_TOKEN`
3. Modify the `publish.yml` workflow to use `password: ${{ secrets.PYPI_API_TOKEN }}`

## Release Process

### Automated Release (Recommended)

The easiest way to release is using the Makefile:

```bash
# 1. Update version and changelog
make version-bump  # or: make version-bump PART=minor/major
# Edit CHANGELOG.md

# 2. Run full release (validates, commits, tags, and pushes)
make release
```

This single command will:
- ✅ Run all validation checks (ruff, mypy, format, tests)
- ✅ Commit changes to `pyproject.toml` and `CHANGELOG.md`
- ✅ Create an annotated git tag (e.g., `v0.1.4`)
- ✅ Push commit and tag to GitHub
- ✅ Trigger GitHub Actions to build and publish to PyPI

### Manual Release

To release a new version to PyPI manually:

1. Update the version in [`pyproject.toml`](../../pyproject.toml) (line 7)
2. Update the [`CHANGELOG.md`](../../CHANGELOG.md)
3. Commit and push your changes:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to X.Y.Z"
   git push
   ```
4. Create and push a version tag:
   ```bash
   git tag vX.Y.Z
   git push tag vX.Y.Z
   ```
5. The GitHub Actions workflow will automatically:
   - Run full test suite
   - Build the package
   - Publish to PyPI
   - Test the installation from PyPI

## Coverage Requirements

- **Minimum coverage**: 80%
- The PR and CI workflows will warn if coverage falls below this threshold
- The Publish workflow will fail if coverage is below 80%

## Testing Matrix

All workflows test across:
- **Python versions**: 3.9, 3.10, 3.11, 3.12
- **Operating systems**: Ubuntu, Windows, macOS

This ensures compatibility across all supported platforms.

## Badges

You can add these badges to your README.md:

```markdown
[![CI](https://github.com/pytest-semantic-assert/pytest-semantic-assert/actions/workflows/ci.yml/badge.svg)](https://github.com/pytest-semantic-assert/pytest-semantic-assert/actions/workflows/ci.yml)
[![PR Checks](https://github.com/pytest-semantic-assert/pytest-semantic-assert/actions/workflows/pr-check.yml/badge.svg)](https://github.com/pytest-semantic-assert/pytest-semantic-assert/actions/workflows/pr-check.yml)
[![PyPI](https://github.com/pytest-semantic-assert/pytest-semantic-assert/actions/workflows/publish.yml/badge.svg)](https://github.com/pytest-semantic-assert/pytest-semantic-assert/actions/workflows/publish.yml)
```
