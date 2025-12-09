"""Example: Testing a chatbot with semantic assertions.

This example demonstrates how to test LLM outputs using semantic assertions
instead of exact string matching.
"""

import pytest

from pytest_semantic_assert import assert_semantically_similar, assert_semantically_similar_to_any


# Simulated chatbot for demonstration
class SimpleChatbot:
    """A simple chatbot that returns varied responses."""

    def ask(self, question: str) -> str:
        """Simulate chatbot response (varies each time in reality)."""
        if "hello" in question.lower() or "hi" in question.lower():
            return "Hello! How may I assist you today?"
        elif "goodbye" in question.lower() or "bye" in question.lower():
            return "Farewell! Have a wonderful day!"
        elif "weather" in question.lower():
            return "The weather is pleasant today."
        elif "help" in question.lower():
            return "I'm here to help! What do you need assistance with?"
        else:
            return "I'm not sure I understand. Could you rephrase that?"


@pytest.fixture
def chatbot() -> SimpleChatbot:
    """Provide a chatbot instance for testing."""
    return SimpleChatbot()


class TestChatbotGreeting:
    """Test chatbot greeting responses."""

    def test_greeting_response(self, chatbot: SimpleChatbot) -> None:
        """Test that chatbot responds with a greeting."""
        response = chatbot.ask("Hello")

        # Semantic assertion - passes even if wording varies
        assert_semantically_similar(response, "Hi there! How can I help you?", threshold=0.60)

    def test_greeting_multiple_variants(self, chatbot: SimpleChatbot) -> None:
        """Test greeting against multiple acceptable responses."""
        response = chatbot.ask("Hi there!")

        # Passes if response matches ANY of these semantically
        assert_semantically_similar_to_any(
            response, ["Hello!", "Hi! How can I help?", "Greetings!", "Hey there!"], threshold=0.55
        )


class TestChatbotFarewell:
    """Test chatbot farewell responses."""

    def test_farewell_response(self, chatbot: SimpleChatbot) -> None:
        """Test that chatbot responds with a farewell."""
        response = chatbot.ask("Goodbye")

        assert_semantically_similar(response, "Goodbye! Have a great day!", threshold=0.70)

    def test_farewell_variations(self, chatbot: SimpleChatbot) -> None:
        """Test various farewell phrasings."""
        response = chatbot.ask("Bye!")

        assert_semantically_similar_to_any(
            response,
            ["Goodbye!", "See you later!", "Take care!", "Have a nice day!"],
            threshold=0.60,
        )


class TestChatbotQuestions:
    """Test chatbot question handling."""

    def test_weather_question(self, chatbot: SimpleChatbot) -> None:
        """Test weather-related question."""
        response = chatbot.ask("What's the weather like?")

        assert_semantically_similar(response, "It's nice today", threshold=0.55)

    def test_help_request(self, chatbot: SimpleChatbot) -> None:
        """Test help request handling."""
        response = chatbot.ask("I need help")

        assert_semantically_similar_to_any(
            response,
            [
                "How can I assist you?",
                "What do you need help with?",
                "I'm here to help!",
                "Let me know what you need",
            ],
            threshold=0.60,
        )


class TestSemanticAssertionBehavior:
    """Demonstrate semantic assertion behavior."""

    def test_exact_match_passes(self) -> None:
        """Exact matches pass with any threshold."""
        assert_semantically_similar("Hello world", "Hello world", threshold=0.99)

    def test_similar_meaning_passes(self) -> None:
        """Similar meanings pass with appropriate threshold."""
        assert_semantically_similar(
            "The cat sat on the mat", "A cat was sitting on the rug", threshold=0.65
        )

    def test_different_meaning_fails(self) -> None:
        """Different meanings fail the assertion."""
        with pytest.raises(AssertionError, match="Semantic similarity too low"):
            assert_semantically_similar("Hello", "Goodbye", threshold=0.85)

    def test_detailed_error_message(self) -> None:
        """Failed assertions show helpful error messages."""
        with pytest.raises(AssertionError) as exc_info:
            assert_semantically_similar("I love programming", "I hate bugs", threshold=0.80)

        error_msg = str(exc_info.value)
        # Check that error contains all required information
        assert "Semantic similarity too low" in error_msg
        assert "I love programming" in error_msg
        assert "I hate bugs" in error_msg
        assert "Similarity Score:" in error_msg
        assert "threshold: 0.8" in error_msg
        assert "Suggestion:" in error_msg

    def test_threshold_customization(self) -> None:
        """Demonstrate threshold customization."""
        # Strict threshold (high similarity required)
        with pytest.raises(AssertionError):
            assert_semantically_similar(
                "Good morning", "Good evening", threshold=0.95  # Very strict
            )

        # Lenient threshold (low similarity accepted)
        assert_semantically_similar("Good morning", "Good evening", threshold=0.50)  # More lenient
