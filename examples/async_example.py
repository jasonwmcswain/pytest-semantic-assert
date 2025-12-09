"""Example demonstrating async semantic assertions for agentic LLM testing.

This example shows how to use async assertions with pytest-asyncio for
testing async LLM agents and chatbots.
"""

import asyncio

import pytest
from pytest_semantic_assert import (
    assert_semantically_similar_async,
    assert_semantically_similar_to_any_async,
)


# Simulated async LLM agent for demonstration
class AsyncLLMAgent:
    """Mock async LLM agent for demonstration."""

    async def process(self, user_input: str) -> str:
        """Simulate async LLM processing."""
        await asyncio.sleep(0.01)  # Simulate I/O delay

        # Simple response mapping for demo
        responses = {
            "Hello": "Hi there! How can I help you today?",
            "Goodbye": "Farewell! Have a great day!",
            "Thank you": "You're very welcome!",
            "What's the weather?": "I'll check the weather forecast for you.",
        }
        return responses.get(user_input, "I'm not sure how to respond to that.")


# Example 1: Basic async assertion
@pytest.mark.asyncio
async def test_agent_greeting() -> None:
    """Test agent responds to greeting appropriately."""
    agent = AsyncLLMAgent()
    response = await agent.process("Hello")

    # Async semantic assertion
    await assert_semantically_similar_async(
        response, "Hi! How can I assist you?", threshold=0.70
    )


# Example 2: Multi-value async assertion
@pytest.mark.asyncio
async def test_agent_farewell() -> None:
    """Test agent can say goodbye in various ways."""
    agent = AsyncLLMAgent()
    response = await agent.process("Goodbye")

    # Check against multiple acceptable responses
    await assert_semantically_similar_to_any_async(
        response,
        ["Bye!", "See you later!", "Farewell! Take care!", "Goodbye!"],
        threshold=0.75,
    )


# Example 3: Multi-turn conversation
@pytest.mark.asyncio
async def test_agent_conversation_flow() -> None:
    """Test multi-turn agent conversation."""
    agent = AsyncLLMAgent()

    # Turn 1: Greeting
    response1 = await agent.process("Hello")
    await assert_semantically_similar_async(
        response1, "Hi! How can I help you today?", threshold=0.80
    )

    # Turn 2: Request
    response2 = await agent.process("What's the weather?")
    await assert_semantically_similar_async(
        response2, "I'll check the weather for you", threshold=0.75
    )

    # Turn 3: Gratitude
    response3 = await agent.process("Thank you")
    await assert_semantically_similar_async(
        response3, "You're welcome!", threshold=0.75
    )


# Example 4: Parallel batch assertions
@pytest.mark.asyncio
async def test_parallel_agent_responses() -> None:
    """Test multiple agent responses in parallel."""
    agent = AsyncLLMAgent()

    # Process multiple queries in parallel
    responses = await asyncio.gather(
        agent.process("Hello"), agent.process("Goodbye"), agent.process("Thank you")
    )

    # Verify all responses in parallel using asyncio.gather
    await asyncio.gather(
        assert_semantically_similar_async(
            responses[0], "Hi there! What can I do for you?", threshold=0.65
        ),
        assert_semantically_similar_async(responses[1], "Bye! Take care!", threshold=0.60),
        assert_semantically_similar_async(
            responses[2], "You're welcome!", threshold=0.95
        ),
    )


# Example 5: Error handling
@pytest.mark.asyncio
async def test_agent_with_threshold_adjustment() -> None:
    """Test agent response with threshold adjustment."""
    agent = AsyncLLMAgent()
    response = await agent.process("Hello")

    # Strict threshold - very similar required (exact match)
    await assert_semantically_similar_async(
        response, "Hi there! How can I help you today?", threshold=0.98
    )

    # Lenient threshold - broader semantic match
    await assert_semantically_similar_async(
        response, "Hello! What do you need?", threshold=0.40
    )


if __name__ == "__main__":
    # Run examples with pytest
    print("Run these examples with: pytest examples/async_example.py -v")
    print("\nOr run individually:")
    print("  pytest examples/async_example.py::test_agent_greeting -v")

