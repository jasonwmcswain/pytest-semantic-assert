"""Unit tests for package initialization and imports."""

import importlib
import sys


class TestPackageImports:
    """Test package-level imports and exports."""

    def test_module_initialization_coverage(self) -> None:
        """Force module initialization to be covered by coverage.py."""
        # Remove from cache if present to force fresh import
        if "pytest_semantic_assert" in sys.modules:
            # Save reference
            original_module = sys.modules["pytest_semantic_assert"]

            # Reload to ensure __init__.py is executed
            importlib.reload(original_module)
        else:
            # Fresh import
            import pytest_semantic_assert

        # Now verify all module-level attributes exist
        import pytest_semantic_assert

        # Line 7: __version__
        assert hasattr(pytest_semantic_assert, "__version__")
        assert pytest_semantic_assert.__version__ == "0.1.0"

        # Lines 9-16: imports
        assert hasattr(pytest_semantic_assert, "assert_semantically_similar")
        assert hasattr(pytest_semantic_assert, "assert_semantically_similar_to_any")
        assert hasattr(pytest_semantic_assert, "assert_semantically_similar_async")
        assert hasattr(pytest_semantic_assert, "assert_semantically_similar_to_any_async")

        # Line 18: __all__
        assert hasattr(pytest_semantic_assert, "__all__")
        assert len(pytest_semantic_assert.__all__) == 5

    def test_version_exists(self) -> None:
        """Test that __version__ is defined and accessible."""
        from pytest_semantic_assert import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_version_format(self) -> None:
        """Test that __version__ follows semantic versioning."""
        from pytest_semantic_assert import __version__

        # Should be in format: X.Y.Z or X.Y.Z-suffix
        parts = __version__.split(".")
        assert len(parts) >= 2, "Version should have at least MAJOR.MINOR"

        # First two parts should be integers
        major = parts[0]
        minor = parts[1].split("-")[0]  # Handle pre-release suffixes

        assert major.isdigit(), f"Major version should be numeric, got: {major}"
        assert minor.isdigit(), f"Minor version should be numeric, got: {minor}"

    def test_assert_semantically_similar_import(self) -> None:
        """Test that assert_semantically_similar can be imported."""
        from pytest_semantic_assert import assert_semantically_similar

        assert callable(assert_semantically_similar)
        assert assert_semantically_similar.__name__ == "assert_semantically_similar"

    def test_assert_semantically_similar_to_any_import(self) -> None:
        """Test that assert_semantically_similar_to_any can be imported."""
        from pytest_semantic_assert import assert_semantically_similar_to_any

        assert callable(assert_semantically_similar_to_any)
        assert assert_semantically_similar_to_any.__name__ == "assert_semantically_similar_to_any"

    def test_all_exports(self) -> None:
        """Test that __all__ contains expected exports."""
        from pytest_semantic_assert import __all__

        expected_exports = [
            "__version__",
            "assert_semantically_similar",
            "assert_semantically_similar_to_any",
            "assert_semantically_similar_async",
            "assert_semantically_similar_to_any_async",
        ]

        assert isinstance(__all__, list)
        assert len(__all__) == len(expected_exports)

        for export in expected_exports:
            assert export in __all__, f"{export} not in __all__"

    def test_all_exports_are_importable(self) -> None:
        """Test that all items in __all__ can actually be imported."""
        import pytest_semantic_assert

        for name in pytest_semantic_assert.__all__:
            assert hasattr(pytest_semantic_assert, name), f"{name} in __all__ but not importable"

    def test_import_star(self) -> None:
        """Test that 'from pytest_semantic_assert import *' works correctly."""
        # This simulates: from pytest_semantic_assert import *
        import pytest_semantic_assert

        namespace = {}
        for name in pytest_semantic_assert.__all__:
            namespace[name] = getattr(pytest_semantic_assert, name)

        # Verify all expected items are present
        assert "__version__" in namespace
        assert "assert_semantically_similar" in namespace
        assert "assert_semantically_similar_to_any" in namespace

    def test_module_docstring(self) -> None:
        """Test that module has a docstring."""
        import pytest_semantic_assert

        assert pytest_semantic_assert.__doc__ is not None
        assert len(pytest_semantic_assert.__doc__) > 0
        assert "pytest-semantic-assert" in pytest_semantic_assert.__doc__

    def test_direct_import_from_submodule(self) -> None:
        """Test importing directly from assertions submodule."""
        from pytest_semantic_assert.assertions import (
            assert_semantically_similar,
            assert_semantically_similar_to_any,
        )

        assert callable(assert_semantically_similar)
        assert callable(assert_semantically_similar_to_any)

    def test_no_extra_exports(self) -> None:
        """Test that only intended items are exported."""
        import pytest_semantic_assert

        # Get all public attributes (not starting with _)
        # Exclude submodules that are imported but not re-exported
        public_attrs = [
            name
            for name in dir(pytest_semantic_assert)
            if not name.startswith("_")
            and name
            not in [
                "assertions",
                "async_assertions",
                "cache",
                "config",
                "embeddings",
                "exceptions",
                "plugin",
                "similarity",
            ]
        ]

        # Should only be the items in __all__
        expected = set(pytest_semantic_assert.__all__)
        actual = set(public_attrs)

        # All public attrs should be in __all__
        for attr in actual:
            assert attr in expected, f"Unexpected public attribute: {attr} (not in __all__)"

    def test_function_signatures_accessible(self) -> None:
        """Test that imported functions have accessible signatures."""
        import inspect

        from pytest_semantic_assert import (
            assert_semantically_similar,
            assert_semantically_similar_to_any,
        )

        # assert_semantically_similar signature
        sig1 = inspect.signature(assert_semantically_similar)
        assert "actual" in sig1.parameters
        assert "expected" in sig1.parameters
        assert "threshold" in sig1.parameters

        # assert_semantically_similar_to_any signature
        sig2 = inspect.signature(assert_semantically_similar_to_any)
        assert "actual" in sig2.parameters
        assert "expected_list" in sig2.parameters
        assert "threshold" in sig2.parameters

    def test_function_docstrings_accessible(self) -> None:
        """Test that imported functions have accessible docstrings."""
        from pytest_semantic_assert import (
            assert_semantically_similar,
            assert_semantically_similar_to_any,
        )

        assert assert_semantically_similar.__doc__ is not None
        assert len(assert_semantically_similar.__doc__) > 0

        assert assert_semantically_similar_to_any.__doc__ is not None
        assert len(assert_semantically_similar_to_any.__doc__) > 0
