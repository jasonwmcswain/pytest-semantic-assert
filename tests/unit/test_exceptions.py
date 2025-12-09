"""Unit tests for custom exceptions."""

import pytest
from pytest_semantic_assert.exceptions import (
    ModelLoadError,
    TextTooLongError,
    TextTooShortError,
)


class TestTextTooShortError:
    """Test TextTooShortError exception."""

    def test_init_with_defaults(self) -> None:
        """Test TextTooShortError initialization with default min_length."""
        error = TextTooShortError(text_length=2)

        assert error.text_length == 2
        assert error.min_length == 3
        assert "minimum 3 characters required" in str(error)
        assert "got 2" in str(error)

    def test_init_with_custom_min_length(self) -> None:
        """Test TextTooShortError initialization with custom min_length."""
        error = TextTooShortError(text_length=5, min_length=10)

        assert error.text_length == 5
        assert error.min_length == 10
        assert "minimum 10 characters required" in str(error)
        assert "got 5" in str(error)

    def test_is_value_error(self) -> None:
        """Test that TextTooShortError is a ValueError subclass."""
        error = TextTooShortError(text_length=1)
        assert isinstance(error, ValueError)

    def test_raise_and_catch(self) -> None:
        """Test raising and catching TextTooShortError."""
        with pytest.raises(TextTooShortError) as exc_info:
            raise TextTooShortError(text_length=0, min_length=3)

        assert exc_info.value.text_length == 0
        assert exc_info.value.min_length == 3

    def test_error_message_format(self) -> None:
        """Test error message format is user-friendly."""
        error = TextTooShortError(text_length=2, min_length=3)
        message = str(error)

        assert "Cannot compute semantic similarity" in message
        assert "empty or very short text" in message
        assert "minimum 3 characters required" in message
        assert "(got 2)" in message


class TestTextTooLongError:
    """Test TextTooLongError exception."""

    def test_init(self) -> None:
        """Test TextTooLongError initialization."""
        error = TextTooLongError(text_length=15000, max_length=10000)

        assert error.text_length == 15000
        assert error.max_length == 10000
        assert "15000 characters" in str(error)
        assert "limit: 10000" in str(error)

    def test_is_value_error(self) -> None:
        """Test that TextTooLongError is a ValueError subclass."""
        error = TextTooLongError(text_length=20000, max_length=10000)
        assert isinstance(error, ValueError)

    def test_raise_and_catch(self) -> None:
        """Test raising and catching TextTooLongError."""
        with pytest.raises(TextTooLongError) as exc_info:
            raise TextTooLongError(text_length=50000, max_length=10000)

        assert exc_info.value.text_length == 50000
        assert exc_info.value.max_length == 10000

    def test_error_message_format(self) -> None:
        """Test error message format is user-friendly."""
        error = TextTooLongError(text_length=12345, max_length=10000)
        message = str(error)

        assert "Text exceeds maximum length" in message
        assert "12345 characters" in message
        assert "limit: 10000" in message

    def test_with_large_numbers(self) -> None:
        """Test with very large text lengths."""
        error = TextTooLongError(text_length=1000000, max_length=500000)

        assert error.text_length == 1000000
        assert error.max_length == 500000
        assert "1000000" in str(error)


class TestModelLoadError:
    """Test ModelLoadError exception."""

    def test_init_with_defaults(self) -> None:
        """Test ModelLoadError initialization with default attempts."""
        error = ModelLoadError(model_name="test-model")

        assert error.model_name == "test-model"
        assert error.attempts == 3
        assert "test-model" in str(error)
        assert "after 3 attempts" in str(error)

    def test_init_with_custom_attempts(self) -> None:
        """Test ModelLoadError initialization with custom attempts."""
        error = ModelLoadError(model_name="custom-model", attempts=5)

        assert error.model_name == "custom-model"
        assert error.attempts == 5
        assert "custom-model" in str(error)
        assert "after 5 attempts" in str(error)

    def test_is_runtime_error(self) -> None:
        """Test that ModelLoadError is a RuntimeError subclass."""
        error = ModelLoadError(model_name="test-model")
        assert isinstance(error, RuntimeError)

    def test_raise_and_catch(self) -> None:
        """Test raising and catching ModelLoadError."""
        with pytest.raises(ModelLoadError) as exc_info:
            raise ModelLoadError(model_name="failing-model", attempts=3)

        assert exc_info.value.model_name == "failing-model"
        assert exc_info.value.attempts == 3

    def test_error_message_contains_troubleshooting(self) -> None:
        """Test error message includes troubleshooting steps."""
        error = ModelLoadError(model_name="all-MiniLM-L6-v2", attempts=3)
        message = str(error)

        # Check main error message
        assert "Failed to load embedding model" in message
        assert "all-MiniLM-L6-v2" in message
        assert "after 3 attempts" in message

        # Check troubleshooting section
        assert "Troubleshooting:" in message
        assert "Check network connectivity" in message
        assert "Verify model name in pytest.ini" in message
        assert "Check disk space" in message
        assert "huggingface-cli download" in message

    def test_with_different_model_names(self) -> None:
        """Test with various model name formats."""
        models = [
            "all-MiniLM-L6-v2",
            "sentence-transformers/all-mpnet-base-v2",
            "custom/model-name",
        ]

        for model_name in models:
            error = ModelLoadError(model_name=model_name, attempts=2)
            assert error.model_name == model_name
            assert model_name in str(error)

    def test_error_message_format(self) -> None:
        """Test complete error message format."""
        error = ModelLoadError(model_name="test-model", attempts=3)
        message = str(error)

        # Verify structure
        lines = message.split("\n")
        assert len(lines) >= 5  # Main message + troubleshooting steps
        assert "Failed to load" in lines[0]
        assert "Troubleshooting:" in message
