# Development Guide

This guide covers local development setup, testing, and contribution workflows for pytest-semantic-assert.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip or poetry
- git

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

## 🧪 Running Tests

```bash
# All tests
make test

# Specific test categories
make unit-test          # Unit tests only
make integration-test   # Integration tests
make contract-test      # API contract tests
make e2e-test          # End-to-end tests

# With coverage
make coverage-combined
open htmlcov/index.html
```

## 🎨 Code Quality

```bash
# Format code
make format

# Lint
make ruff-check
make ruff-fix           # Auto-fix issues

# Type check
mypy src/

# Run all quality checks
make validate
```

## 📦 Building

```bash
# Build package
make build

# Test locally
pip install dist/pytest_semantic_assert-*.whl
```

## 🔧 Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** following TDD:
   - Write tests first
   - Implement functionality
   - Ensure tests pass

3. **Quality checks**
   ```bash
   make validate  # Runs format, lint, type check, and tests
   ```

4. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📊 Project Structure

```
pytest-semantic-assert/
├── pytest_semantic_assert/      # Source code
│   ├── assertions.py            # Core assertion functions
│   ├── cache.py                 # Embedding cache
│   ├── config.py                # Configuration
│   ├── embeddings.py            # Model management
│   ├── exceptions.py            # Custom exceptions
│   ├── plugin.py                # Pytest hooks
│   └── similarity.py            # Similarity computation
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   ├── contract/                # API contract tests
│   └── e2e/                     # End-to-end tests
├── examples/                    # Example usage
├── docs/                        # Documentation
└── specs/                       # Feature specifications
```

## 🎯 Testing Philosophy

### Test-Driven Development (TDD)
- Write tests **before** implementation
- Red → Green → Refactor cycle
- Aim for >90% coverage on new code

### Test Categories
1. **Unit Tests** - Individual functions/classes
2. **Integration Tests** - Multiple components working together
3. **Contract Tests** - Public API stability
4. **E2E Tests** - Complete user scenarios

## 🔍 Debugging

### Enable Debug Mode
```python
# In your test
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Cache Inspection
```bash
# View cache contents
ls -la .pytest-semantic-cache/

# Clear cache
make clean
```

## 📝 Documentation

### Docstrings
All public functions must have:
- Summary line
- Args section
- Returns section
- Raises section
- Examples (if applicable)

### Type Hints
- Use strict type hints for all public APIs
- Follow PEP 484 conventions
- Validate with mypy --strict

## 🐛 Common Issues

### Model Download Fails
```bash
# Pre-download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Import Errors
```bash
# Reinstall in editable mode
pip install -e ".[dev]"
```

### Test Failures
```bash
# Run specific test
pytest tests/unit/test_similarity.py::TestCosineSimilarity::test_identical_vectors -v

# Run with pdb on failure
pytest --pdb
```

## 📦 Release Process

See [RELEASING.md](RELEASING.md) for the complete release checklist.

## 🤝 Contributing

1. Check existing issues or create a new one
2. Fork the repository
3. Create feature branch
4. Make changes following this guide
5. Submit pull request

## 📚 Additional Resources

- [Architecture Overview](ARCHITECTURE.md)
- [API Documentation](../specification/api.md)
- [Testing Guide](TESTING.md)

