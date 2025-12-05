# pytest-semantic-assert

## 🎯 Project Overview

A pytest plugin that enables "fuzzy" semantic assertions for LLM outputs using embeddings or cheap LLM calls, solving the problem that LLM responses vary in wording but not meaning.

## 💡 The Problem

Testing LLMs is impossible with traditional assertions:
```python
# This fails randomly
assert response == "The answer is 5"
# LLM might say: "It is 5" or "The result is 5" or "5 is the answer"
```

Current workarounds are hacky:
- Manual "vibe checks"
- Regex patterns (brittle)
- Substring matching (too loose)
- No standardized approach

## ✨ The Solution

A pytest plugin that allows semantic assertions:
```python
from pytest_semantic_assert import assert_semantically_similar

def test_chatbot_greeting():
    response = my_agent.ask("Hello")
    # Passes if response is semantically similar
    assert_semantically_similar(
        response,
        "Hello, how can I help you?",
        threshold=0.85
    )
```

## 🏗️ Technical Architecture

### Core Components

**Semantic Comparison Engine**
- **Local Embeddings** (default): sentence-transformers (all-MiniLM-L6-v2)
- **LLM-based** (optional): OpenAI/Claude for complex comparisons
- **Hybrid Mode**: Embeddings for speed, LLM for edge cases

**Pytest Integration**
- Custom assertion methods
- Pytest fixtures for configuration
- Detailed failure messages
- Snapshot testing support

**Comparison Modes**

1. **Similarity**: Semantic closeness (0.0 to 1.0)
2. **Entailment**: Does A imply B?
3. **Contradiction**: Are A and B opposite?
4. **Equivalence**: Same meaning, different words?

### Example Assertions

**Basic Similarity**:
```python
assert_semantically_similar(
    "The user is authenticated",
    "User login successful",
    threshold=0.8
)
```

**Entailment**:
```python
assert_entails(
    "All users have been notified",
    "John was notified"  # True: John is a user
)
```

**List Assertions**:
```python
assert_semantically_contains(
    ["apple", "banana", "orange"],
    "fruit similar to banana"  # Matches "banana"
)
```

**JSON Assertions**:
```python
assert_semantic_json(
    {"status": "The operation succeeded"},
    {"status": "Success"},  # Semantically equivalent
    threshold=0.85
)
```

## 🛠️ Tech Stack

- **Core**: Python 3.9+, pytest
- **Embeddings**: sentence-transformers, numpy
- **Optional LLM**: OpenAI API, Anthropic API
- **Similarity**: cosine similarity, scipy
- **Caching**: diskcache (avoid re-computing embeddings)

## 📋 Implementation Roadmap

### Phase 1: MVP (1-2 weeks)
- [ ] Basic `assert_semantically_similar` function
- [ ] Local embedding model integration
- [ ] Pytest plugin structure
- [ ] Simple threshold-based comparison

### Phase 2: Core Features (2-3 weeks)
- [ ] Multiple comparison modes (entailment, contradiction)
- [ ] Detailed failure messages with similarity scores
- [ ] Configuration via pytest.ini
- [ ] Caching for performance

### Phase 3: Advanced Assertions (2 weeks)
- [ ] List/array assertions
- [ ] JSON semantic comparison
- [ ] Snapshot testing integration
- [ ] Custom embedding models

### Phase 4: LLM Integration (1-2 weeks)
- [ ] Optional LLM-based comparison
- [ ] Hybrid mode (embeddings + LLM)
- [ ] Cost tracking for LLM calls
- [ ] Fallback mechanisms

### Phase 5: Production Ready (1 week)
- [ ] Comprehensive test suite
- [ ] Documentation with examples
- [ ] PyPI package setup
- [ ] CI/CD integration guide

## 🎮 Usage Example

**Installation**:
```bash
pip install pytest-semantic-assert
```

**Basic Usage**:
```python
# test_chatbot.py
from pytest_semantic_assert import assert_semantically_similar

def test_greeting():
    bot_response = chatbot.greet()
    assert_semantically_similar(
        bot_response,
        "Hello! How can I assist you today?",
        threshold=0.85
    )

def test_farewell():
    bot_response = chatbot.goodbye()
    # Multiple acceptable responses
    assert_semantically_similar_to_any(
        bot_response,
        ["Goodbye!", "See you later!", "Have a great day!"],
        threshold=0.80
    )
```

**Configuration** (`pytest.ini`):
```ini
[pytest]
semantic_assert_threshold = 0.85
semantic_assert_model = all-MiniLM-L6-v2
semantic_assert_cache = true
semantic_assert_llm_fallback = false

# Optional: Use LLM for complex cases
semantic_assert_llm_provider = openai
semantic_assert_llm_model = gpt-4o-mini
```

**Advanced Usage**:
```python
# Snapshot testing
def test_agent_response(semantic_snapshot):
    response = agent.process("What is the weather?")
    # First run: saves snapshot
    # Subsequent runs: compares semantically
    semantic_snapshot.assert_match(response, threshold=0.9)

# JSON comparison
def test_api_response():
    response = api.get_user(123)
    assert_semantic_json(
        response,
        {
            "status": "success",
            "message": "User found",
            "user": {"name": "John", "email": "john@example.com"}
        },
        threshold=0.85,
        compare_keys=["status", "message"]  # Only compare these semantically
    )
```

**Failure Messages**:
```
AssertionError: Semantic similarity too low

Expected (semantically): "Hello, how can I help you?"
Actual: "Goodbye!"
Similarity Score: 0.23 (threshold: 0.85)

Suggestion: These texts have opposite meanings (greeting vs farewell).
Consider using assert_contradicts() if testing for opposites.
```

## 📊 Success Metrics

- **PyPI Downloads**: Weekly download count
- **GitHub Stars**: Community interest
- **Issue Resolution**: Response time and fix rate
- **Adoption**: Number of projects using it
- **Performance**: Speed vs accuracy tradeoff

## 🎯 Portfolio Value

**Why This Stands Out**:
- Solves an urgent, universal problem
- First-mover advantage (no standard solution exists)
- Demonstrates deep understanding of LLM testing
- Practical tool with immediate value

**Target Audience**:
- Anyone building LLM applications
- QE teams testing AI features
- AI/ML engineers
- Pytest users

## 🚀 Viral Potential

**GitHub Stars Potential**: 5k-10k

**Why It Could Go Viral**:
- Every LLM developer needs this immediately
- Fills a critical gap in testing ecosystem
- Easy to understand and adopt
- "Why doesn't this exist already?" factor
- Strong word-of-mouth potential

## 🎥 Demo Scenario

**Side-by-side comparison**:

**Before** (Traditional Testing):
```python
# Brittle and fails randomly
assert "hello" in response.lower()
# or
assert response == "Hello, how can I help?"  # Fails if wording changes
```

**After** (Semantic Testing):
```python
# Robust and meaningful
assert_semantically_similar(
    response,
    "Hello, how can I help?",
    threshold=0.85
)
# Passes for: "Hi there!", "Greetings!", "How may I assist you?"
```

## 📚 Related Projects

- Used by: [Self-Healing Test Orchestrator](./self-healing-test-orchestrator.md)
- Complements: [Chaos Monkey for Data Contracts](./chaos-monkey-data-contracts.md)
- Similar domain: All testing-related projects

## 🔗 References

- sentence-transformers Documentation
- Pytest Plugin Development
- Semantic Similarity Metrics
- Embedding Models Comparison

## 💰 Monetization Potential

**Open Core Model**:
- Free: Local embeddings, basic assertions
- Pro: LLM-based comparison, advanced features, priority support
- Enterprise: Custom models, on-premise deployment, SLA

---

**Status**: 🚀 **Recommended First PyPI Library**
**Difficulty**: ⭐⭐ (Intermediate)
**Time Estimate**: 7-10 weeks
**Impact**: 💎 Highest viral potential, fills critical gap

