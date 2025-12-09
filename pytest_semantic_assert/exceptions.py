"""Custom exceptions for pytest-semantic-assert."""


class TextTooShortError(ValueError):
    """Raised when text is too short for semantic comparison."""

    def __init__(self, text_length: int, min_length: int = 3) -> None:
        """Initialize TextTooShortError.

        Args:
            text_length: Actual length of the text
            min_length: Minimum required length (default: 3)
        """
        super().__init__(
            f"Cannot compute semantic similarity for empty or very short text - "
            f"minimum {min_length} characters required (got {text_length})"
        )
        self.text_length = text_length
        self.min_length = min_length


class TextTooLongError(ValueError):
    """Raised when text exceeds maximum length."""

    def __init__(self, text_length: int, max_length: int) -> None:
        """Initialize TextTooLongError.

        Args:
            text_length: Actual length of the text
            max_length: Maximum allowed length
        """
        super().__init__(
            f"Text exceeds maximum length: {text_length} characters (limit: {max_length})"
        )
        self.text_length = text_length
        self.max_length = max_length


class ModelLoadError(RuntimeError):
    """Raised when embedding model fails to load after retries."""

    def __init__(self, model_name: str, attempts: int = 3) -> None:
        """Initialize ModelLoadError.

        Args:
            model_name: Name of the model that failed to load
            attempts: Number of attempts made (default: 3)
        """
        super().__init__(
            f"Failed to load embedding model '{model_name}' after {attempts} attempts.\n\n"
            f"Troubleshooting:\n"
            f"- Check network connectivity\n"
            f"- Verify model name in pytest.ini\n"
            f"- Check disk space (~100MB required)\n"
            f"- Try manual download: huggingface-cli download sentence-transformers/{model_name}"
        )
        self.model_name = model_name
        self.attempts = attempts
