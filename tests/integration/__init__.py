"""Integration tests for pytest-semantic-assert.

Integration tests verify that multiple components work correctly together.
They test real interactions between:
- Assertion functions
- Embedding manager with real models
- Similarity calculations
- Configuration system
- Pytest plugin hooks

Unlike unit tests (which mock dependencies) or E2E tests (which test complete
user workflows), integration tests focus on component interactions with real
implementations but in a controlled test environment.
"""
