"""Unit tests for cosine similarity computation."""

import numpy as np
import pytest
from pytest_semantic_assert.similarity import cosine_similarity


class TestCosineSimilarity:
    """Test cosine similarity function."""

    def test_identical_vectors(self) -> None:
        """Test that identical vectors have similarity 1.0."""
        vec = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        assert abs(cosine_similarity(vec, vec) - 1.0) < 1e-6  # Allow for floating point errors

    def test_orthogonal_vectors(self) -> None:
        """Test that orthogonal vectors have similarity 0.0."""
        vec_a = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        vec_b = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        assert cosine_similarity(vec_a, vec_b) == 0.0

    def test_opposite_vectors(self) -> None:
        """Test that opposite vectors have similarity close to 0.0."""
        vec_a = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        vec_b = np.array([-1.0, 0.0, 0.0], dtype=np.float32)
        # Cosine of opposite vectors is -1.0, but we clamp to [0.0, 1.0]
        similarity = cosine_similarity(vec_a, vec_b)
        assert 0.0 <= similarity <= 1.0

    def test_similar_vectors(self) -> None:
        """Test that similar vectors have high similarity."""
        vec_a = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        vec_b = np.array([1.1, 2.1, 3.1], dtype=np.float32)
        similarity = cosine_similarity(vec_a, vec_b)
        assert similarity > 0.99  # Very similar

    def test_different_dimensions_raises_error(self) -> None:
        """Test that vectors with different dimensions raise ValueError."""
        vec_a = np.array([1.0, 2.0], dtype=np.float32)
        vec_b = np.array([1.0, 2.0, 3.0], dtype=np.float32)

        with pytest.raises(ValueError, match="same dimensions"):
            cosine_similarity(vec_a, vec_b)

    def test_zero_vector_raises_error(self) -> None:
        """Test that zero vectors raise ValueError."""
        vec_a = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        vec_b = np.array([1.0, 2.0, 3.0], dtype=np.float32)

        with pytest.raises(ValueError, match="zero vectors"):
            cosine_similarity(vec_a, vec_b)

    def test_normalized_vectors(self) -> None:
        """Test similarity with pre-normalized vectors."""
        # Unit vectors along different axes
        vec_a = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        vec_b = np.array([0.707, 0.707, 0.0], dtype=np.float32)  # 45 degrees

        similarity = cosine_similarity(vec_a, vec_b)
        assert 0.7 < similarity < 0.72  # cos(45°) ≈ 0.707

    def test_high_dimensional_vectors(self) -> None:
        """Test similarity with high-dimensional vectors (like embeddings)."""
        # Simulate 384-dimensional embeddings
        np.random.seed(42)
        vec_a = np.random.rand(384).astype(np.float32)
        vec_b = vec_a + np.random.rand(384).astype(np.float32) * 0.1  # Add noise

        similarity = cosine_similarity(vec_a, vec_b)
        assert 0.8 < similarity < 1.0  # Should be quite similar

    def test_return_type(self) -> None:
        """Test that function returns float."""
        vec_a = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        vec_b = np.array([4.0, 5.0, 6.0], dtype=np.float32)

        result = cosine_similarity(vec_a, vec_b)
        assert isinstance(result, float)

    def test_clamping_to_valid_range(self) -> None:
        """Test that result is always in [0.0, 1.0] range."""
        # Test various vector combinations
        test_cases = [
            (np.array([1.0, 0.0], dtype=np.float32), np.array([1.0, 0.0], dtype=np.float32)),
            (np.array([1.0, 1.0], dtype=np.float32), np.array([1.0, -1.0], dtype=np.float32)),
            (np.array([3.0, 4.0], dtype=np.float32), np.array([4.0, 3.0], dtype=np.float32)),
        ]

        for vec_a, vec_b in test_cases:
            similarity = cosine_similarity(vec_a, vec_b)
            assert 0.0 <= similarity <= 1.0, f"Similarity {similarity} out of range [0.0, 1.0]"
