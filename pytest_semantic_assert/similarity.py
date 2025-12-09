"""Cosine similarity computation for semantic embeddings."""

import numpy as np
import numpy.typing as npt


def cosine_similarity(vec_a: npt.NDArray[np.float32], vec_b: npt.NDArray[np.float32]) -> float:
    """Compute cosine similarity between two vectors.

    Args:
        vec_a: First embedding vector
        vec_b: Second embedding vector

    Returns:
        Cosine similarity score (0.0 to 1.0), where:
        - 1.0 = identical vectors
        - 0.0 = orthogonal (completely different)
        - Values are clamped to [0.0, 1.0] range

    Raises:
        ValueError: If vectors have different dimensions or are zero vectors

    Examples:
        >>> vec1 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        >>> vec2 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        >>> cosine_similarity(vec1, vec2)
        1.0

        >>> vec1 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        >>> vec2 = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        >>> cosine_similarity(vec1, vec2)
        0.0
    """
    # Validate dimensions
    if vec_a.shape != vec_b.shape:
        raise ValueError(f"Vectors must have same dimensions (got {vec_a.shape} and {vec_b.shape})")

    # Compute norms
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    # Check for zero vectors
    if norm_a == 0.0 or norm_b == 0.0:
        raise ValueError("Cannot compute similarity for zero vectors")

    # Compute cosine similarity
    dot_product = np.dot(vec_a, vec_b)
    similarity = float(dot_product / (norm_a * norm_b))

    # Clamp to [0.0, 1.0] range (handle floating point errors)
    return max(0.0, min(1.0, similarity))
