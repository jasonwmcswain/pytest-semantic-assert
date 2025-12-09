"""Contract tests for public API stability."""

import inspect
from typing import Optional

from pytest_semantic_assert import (
    __version__,
    assert_semantically_similar,
    assert_semantically_similar_to_any,
)


class TestPublicAPIContract:
    """Test that public API signatures remain stable."""

    def test_assert_semantically_similar_signature(self) -> None:
        """Ensure assert_semantically_similar signature remains stable."""
        sig = inspect.signature(assert_semantically_similar)
        params = list(sig.parameters.keys())

        assert params == ["actual", "expected", "threshold"]
        assert sig.parameters["actual"].annotation is str
        assert sig.parameters["expected"].annotation is str
        assert sig.parameters["threshold"].annotation == Optional[float]
        assert sig.return_annotation is None or sig.return_annotation is type(None)

    def test_assert_semantically_similar_to_any_signature(self) -> None:
        """Ensure assert_semantically_similar_to_any signature remains stable."""
        sig = inspect.signature(assert_semantically_similar_to_any)
        params = list(sig.parameters.keys())

        assert params == ["actual", "expected_list", "threshold"]
        assert sig.parameters["actual"].annotation is str
        # Note: list[str] annotation might show differently depending on Python version
        assert sig.parameters["threshold"].annotation == Optional[float]
        assert sig.return_annotation is None or sig.return_annotation is type(None)

    def test_version_exists(self) -> None:
        """Test that __version__ is defined and follows semver."""
        assert isinstance(__version__, str)
        assert __version__ != ""
        # Should match semver pattern (simplified check)
        parts = __version__.split(".")
        assert len(parts) >= 2  # At least MAJOR.MINOR

    def test_function_docstrings_exist(self) -> None:
        """Test that public functions have docstrings."""
        assert assert_semantically_similar.__doc__ is not None
        assert len(assert_semantically_similar.__doc__) > 0

        assert assert_semantically_similar_to_any.__doc__ is not None
        assert len(assert_semantically_similar_to_any.__doc__) > 0

    def test_default_threshold_parameter(self) -> None:
        """Test that threshold parameter has correct default."""
        sig = inspect.signature(assert_semantically_similar)
        threshold_param = sig.parameters["threshold"]

        assert threshold_param.default is None

    def test_public_exports(self) -> None:
        """Test that expected functions are exported from main module."""
        from pytest_semantic_assert import __all__

        expected_exports = [
            "__version__",
            "assert_semantically_similar",
            "assert_semantically_similar_to_any",
        ]

        for export in expected_exports:
            assert export in __all__, f"{export} not in __all__"
