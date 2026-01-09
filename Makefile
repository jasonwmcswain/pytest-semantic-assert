# Variables
PYTHON := python3
PIP := pip
VENV := venv
BIN := $(VENV)/bin
PROJECT_NAME := pytest_semantic_assert
TEST_DIR := tests
SRC_DIR := $(PROJECT_NAME)

# Default target
.PHONY: help
help:
	@echo "pytest-semantic-assert 🧪 Makefile"
	@echo "------------------------------------"
	@echo ""
	@echo "Environment:"
	@echo "  make venv          - Create virtual environment and install dev deps"
	@echo "  make clean         - Remove build artifacts, cache, and venv"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format        - Format code using Black"
	@echo "  make ruff-check    - Run Ruff linter (check only)"
	@echo "  make ruff-fix      - Run Ruff linter (auto-fix)"
	@echo "  make mypy-check    - Run MyPy type checker (check only)"
	@echo ""
	@echo "Testing:"
	@echo "  make unittest      - Run all tests with coverage"
	@echo "  make unit-test     - Run only unit tests with coverage"
	@echo "  make integration-test - Run only integration tests with coverage"
	@echo "  make contract-test - Run only contract tests with coverage"
	@echo "  make e2e-test      - Run only E2E tests with coverage"
	@echo "  make coverage-combined - Run all tests with combined coverage"
	@echo "  make validate      - Run all checks (ruff, mypy, format, tests)"
	@echo ""
	@echo "Build & Version:"
	@echo "  make build         - Build the source and wheel distribution"
	@echo "  make version-show  - Show current version"
	@echo "  make version-bump  - Bump patch version (use PART=minor/major to change)"
	@echo "  make package       - Alias for build"
	@echo ""
	@echo "Publishing:"
	@echo "  make publish-test  - Upload to TestPyPI"
	@echo "  make publish       - Upload to PyPI"
	@echo ""
	@echo "Pipeline:"
	@echo "  make all           - Clean, Format, Check, Test, Build"

# --- Environment ---
.PHONY: venv
venv:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e .[dev]

# --- Code Quality ---
.PHONY: format
format:
	$(BIN)/black $(SRC_DIR) $(TEST_DIR)

.PHONY: ruff-check
ruff-check:
	$(BIN)/ruff check $(SRC_DIR) $(TEST_DIR)

.PHONY: ruff-fix
ruff-fix:
	$(BIN)/ruff check --fix $(SRC_DIR) $(TEST_DIR)

.PHONY: mypy-check
mypy-check:
	$(BIN)/mypy --verbose --pretty --junit-xml=.mypy-junit.xml $(SRC_DIR)

# --- Testing ---
.PHONY: unittest
unittest:
	$(BIN)/pytest --cov=$(PROJECT_NAME) --cov-report=term-missing $(TEST_DIR)

.PHONY: unit-test
unit-test:
	$(BIN)/pytest --cov=$(PROJECT_NAME) --cov-report=term-missing $(TEST_DIR)/unit

.PHONY: integration-test
integration-test:
	$(BIN)/pytest --cov=$(PROJECT_NAME) --cov-report=term-missing $(TEST_DIR)/integration

.PHONY: contract-test
contract-test:
	$(BIN)/pytest --cov=$(PROJECT_NAME) --cov-report=term-missing $(TEST_DIR)/contract

.PHONY: e2e-test
e2e-test:
	$(BIN)/pytest --cov=$(PROJECT_NAME) --cov-report=term-missing $(TEST_DIR)/e2e

.PHONY: coverage-combined
coverage-combined:
	@echo "Running unit tests with coverage..."
	$(BIN)/pytest --cov=$(PROJECT_NAME) --cov-report= $(TEST_DIR)/unit
	@echo ""
	@echo "Running integration tests with coverage (appending)..."
	$(BIN)/pytest --cov=$(PROJECT_NAME) --cov-append --cov-report= $(TEST_DIR)/integration
	@echo ""
	@echo "Running contract tests with coverage (appending)..."
	$(BIN)/pytest --cov=$(PROJECT_NAME) --cov-append --cov-report= $(TEST_DIR)/contract
	@echo ""
	@echo "Running E2E tests with coverage (appending)..."
	$(BIN)/pytest --cov=$(PROJECT_NAME) --cov-append --cov-report= $(TEST_DIR)/e2e
	@echo ""
	@echo "Generating combined coverage report..."
	$(BIN)/coverage report -m
	@echo ""
	@echo "Generating HTML coverage report..."
	$(BIN)/coverage html
	@echo "✅ Combined coverage report generated! Open htmlcov/index.html to view."

.PHONY: validate
validate: venv ruff-check mypy-check format coverage-combined version-bump version-show
	@echo "✅ All validation checks passed!"

# --- Build & Versioning ---
.PHONY: clean
clean:
	rm -rf dist build *.egg-info
	rm -rf $(VENV)
	rm -rf .pytest-semantic-cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".mypy-junit.xml" -delete

.PHONY: version-show
version-show:
	@grep 'version = ' pyproject.toml | head -n 1 | cut -d '"' -f 2

.PHONY: version-bump
version-bump:
	@# Defaults to patch. Usage: make version-bump PART=minor
	$(eval PART ?= patch)
	@$(PYTHON) -c "import re; \
	f='pyproject.toml'; \
	c=open(f).read(); \
	v=re.search(r'version = \"(\d+)\.(\d+)\.(\d+)\"', c).groups(); \
	major,minor,patch=[int(x) for x in v]; \
	patch+=1 if '$(PART)'=='patch' else 0; \
	minor+=1 if '$(PART)'=='minor' else 0; \
	patch=0 if '$(PART)'=='minor' else patch; \
	major+=1 if '$(PART)'=='major' else 0; \
	minor=0 if '$(PART)'=='major' else minor; \
	patch=0 if '$(PART)'=='major' else patch; \
	new_v=f'{major}.{minor}.{patch}'; \
	print(f'Bumping version: {v[0]}.{v[1]}.{v[2]} -> {new_v}'); \
	open(f,'w').write(re.sub(r'version = \".*?\"', f'version = \"{new_v}\"', c, count=1))"

.PHONY: build
build: clean
	$(BIN)/python -m build

.PHONY: package
package: build

# --- Publishing ---
.PHONY: publish-test
publish-test: build
	@echo "Uploading to TestPyPI..."
	$(BIN)/twine upload --repository testpypi dist/*

.PHONY: publish
publish: build
	@echo "🚀 Uploading to Production PyPI..."
	$(BIN)/twine upload dist/*

# --- Pipeline ---
.PHONY: all
all: clean venv format ruff-fix unittest build
	@echo "✅ Pipeline complete!"

