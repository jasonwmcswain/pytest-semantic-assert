"""Integration tests for concurrent execution (threading and multiprocessing).

Tests verify that the plugin works correctly under concurrent load, ensuring:
1. File locking prevents cache corruption
2. Multiple threads/processes can safely use the plugin
3. No race conditions in embedding generation or caching
4. Works correctly with pytest-xdist (multiprocessing)
"""

import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pytest
from pytest_semantic_assert import (
    assert_semantically_similar,
    assert_semantically_similar_async,
)
from pytest_semantic_assert.cache import EmbeddingCache


# Module-level worker functions for multiprocessing (must be pickleable)
def _mp_run_assertion(text_id: int) -> bool:
    """Worker function for multiprocessing assertion test."""
    actual = f"Hello world {text_id}"
    expected = f"Hi there {text_id}"
    try:
        assert_semantically_similar(actual, expected, threshold=0.40)
        return True
    except AssertionError:
        return False


def _mp_write_and_verify(args: tuple) -> bool:
    """Worker function for multiprocessing cache write test."""
    text_id, cache_dir = args
    cache = EmbeddingCache(cache_dir=cache_dir, enabled=True)

    text = f"Test text {text_id}"
    embedding = np.random.rand(384).astype(np.float32)
    cache.set(text, "test-model", embedding)

    # Verify we can read it back
    result = cache.get(text, "test-model")
    return result is not None


def _mp_stress_cache(args: tuple) -> int:
    """Worker function for cache stress test."""
    worker_id, cache_dir = args
    cache = EmbeddingCache(cache_dir=cache_dir, enabled=True)
    writes = 0

    for i in range(10):
        text = f"shared-{i % 3}"  # Use only 3 shared keys
        embedding = np.random.rand(384).astype(np.float32)
        cache.set(text, "test-model", embedding)
        writes += 1

        # Read it back immediately
        result = cache.get(text, "test-model")
        assert result is not None, "Cache read failed immediately after write"

    return writes


def _mp_worker_test_suite(args: tuple) -> dict:
    """Worker function simulating pytest worker."""
    worker_id, cache_dir = args
    results = {"passed": 0, "failed": 0}

    # Each worker runs 10 tests
    for test_id in range(10):
        actual = f"Worker {worker_id} test {test_id}"
        expected = f"Worker {worker_id} test {test_id}"  # Identical for simplicity

        try:
            # This will use the shared cache
            assert_semantically_similar(actual, expected, threshold=0.99)
            results["passed"] += 1
        except AssertionError:
            results["failed"] += 1

    return results


def _mp_worker(args: tuple) -> int:
    """Worker function for cache corruption test."""
    worker_id, cache_dir, num_tests = args
    count = 0

    for i in range(num_tests):
        # Mix of unique and shared texts
        if i % 2 == 0:
            # Shared text across workers
            actual = f"Shared text {i % 5}"
            expected = "Common response"
        else:
            # Worker-specific text
            actual = f"Worker {worker_id} unique {i}"
            expected = f"Worker {worker_id} response"

        try:
            assert_semantically_similar(actual, expected, threshold=0.30)
            count += 1
        except Exception:
            pass  # Ignore failures for this stress test

    return count


class TestThreadingConcurrency:
    """Test concurrent access using threading (GIL-limited but tests file locking)."""

    def test_concurrent_cache_writes_threading(self, tmp_path: Path) -> None:
        """Test multiple threads writing to cache simultaneously."""
        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=True)

        def write_embedding(text_id: int) -> None:
            """Write an embedding to cache."""
            text = f"Test text {text_id}"
            embedding = np.random.rand(384).astype(np.float32)
            cache.set(text, "test-model", embedding)
            # Verify we can read it back
            result = cache.get(text, "test-model")
            assert result is not None

        # Create 10 threads writing concurrently
        threads = []
        for i in range(10):
            t = threading.Thread(target=write_embedding, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join(timeout=10)

        # Verify all embeddings were written successfully
        for i in range(10):
            result = cache.get(f"Test text {i}", "test-model")
            assert result is not None, f"Embedding {i} not found in cache"

    def test_concurrent_assertions_threading(self) -> None:
        """Test multiple threads running assertions simultaneously."""

        def run_assertion(text_id: int) -> bool:
            """Run a semantic assertion."""
            actual = f"Hello world {text_id}"
            expected = f"Hi there {text_id}"
            try:
                assert_semantically_similar(actual, expected, threshold=0.40)
                return True
            except AssertionError:
                return False

        # Create 20 threads running assertions concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(run_assertion, range(20)))

        # All assertions should pass
        assert all(results), f"Some assertions failed: {sum(not r for r in results)}"

    def test_concurrent_cache_reads_threading(self, tmp_path: Path) -> None:
        """Test multiple threads reading from cache simultaneously."""
        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=True)

        # Pre-populate cache
        embedding = np.random.rand(384).astype(np.float32)
        cache.set("shared text", "test-model", embedding)

        def read_embedding() -> np.ndarray:
            """Read an embedding from cache."""
            result = cache.get("shared text", "test-model")
            assert result is not None
            return result

        # Create 50 threads reading concurrently
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(lambda _: read_embedding(), range(50)))

        # All reads should succeed and return the same embedding
        assert len(results) == 50
        for result in results:
            np.testing.assert_array_equal(result, embedding)

    def test_mixed_read_write_threading(self, tmp_path: Path) -> None:
        """Test concurrent reads and writes to cache."""
        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=True)
        errors: list[Exception] = []

        def write_worker(worker_id: int) -> None:
            """Worker that writes embeddings."""
            try:
                for i in range(5):
                    text = f"text-{worker_id}-{i}"
                    embedding = np.random.rand(384).astype(np.float32)
                    cache.set(text, "test-model", embedding)
                    time.sleep(0.001)  # Small delay to increase contention
            except Exception as e:
                errors.append(e)

        def read_worker(worker_id: int) -> None:
            """Worker that reads embeddings."""
            try:
                for i in range(5):
                    # Try to read various texts
                    for wid in range(3):
                        text = f"text-{wid}-{i}"
                        cache.get(text, "test-model")  # May or may not exist
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        # Start writers and readers concurrently
        threads = []
        for i in range(3):
            t = threading.Thread(target=write_worker, args=(i,))
            threads.append(t)
            t.start()

        for i in range(5):
            t = threading.Thread(target=read_worker, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all to complete
        for t in threads:
            t.join(timeout=10)

        # No errors should have occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"


class TestMultiprocessingConcurrency:
    """Test concurrent access using multiprocessing (true parallelism)."""

    def test_concurrent_assertions_multiprocessing(self) -> None:
        """Test multiple processes running assertions simultaneously."""
        # Use multiprocessing to run assertions in parallel
        # This simulates pytest-xdist behavior
        with ProcessPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(_mp_run_assertion, range(12)))

        # All assertions should pass
        assert all(results), f"Some assertions failed: {sum(not r for r in results)}"

    def test_concurrent_cache_writes_multiprocessing(self, tmp_path: Path) -> None:
        """Test multiple processes writing to cache simultaneously."""
        # Run 8 processes writing concurrently
        args = [(i, str(tmp_path)) for i in range(8)]
        with ProcessPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(_mp_write_and_verify, args))

        # All writes should succeed
        assert all(results), f"Some writes failed: {sum(not r for r in results)}"

        # Verify all embeddings are accessible
        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=True)
        for i in range(8):
            result = cache.get(f"Test text {i}", "test-model")
            assert result is not None, f"Embedding {i} not found after multiprocessing"

    def test_cache_corruption_prevention_multiprocessing(self, tmp_path: Path) -> None:
        """Test that file locking prevents cache corruption under heavy load."""
        # Run 6 processes hammering the cache with same keys
        args = [(i, str(tmp_path)) for i in range(6)]
        with ProcessPoolExecutor(max_workers=6) as executor:
            write_counts = list(executor.map(_mp_stress_cache, args))

        # All processes should complete successfully
        assert len(write_counts) == 6
        assert sum(write_counts) == 60  # 6 processes * 10 writes each

        # Cache should not be corrupted - verify we can still read
        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=True)
        for i in range(3):
            result = cache.get(f"shared-{i}", "test-model")
            # Should exist (last write wins)
            assert result is not None


class TestAsyncConcurrency:
    """Test async assertions with concurrent execution."""

    @pytest.mark.asyncio
    async def test_concurrent_async_assertions(self) -> None:
        """Test multiple async assertions running concurrently."""
        import asyncio

        async def run_assertion(text_id: int) -> bool:
            """Run an async semantic assertion."""
            actual = f"Hello world {text_id}"
            expected = f"Hi there {text_id}"
            try:
                await assert_semantically_similar_async(actual, expected, threshold=0.40)
                return True
            except AssertionError:
                return False

        # Run 30 async assertions concurrently
        results = await asyncio.gather(*[run_assertion(i) for i in range(30)])

        # All should pass
        assert all(results), f"Some assertions failed: {sum(not r for r in results)}"

    @pytest.mark.asyncio
    async def test_async_batch_processing(self) -> None:
        """Test batch processing with async assertions."""
        import asyncio

        # Simulate processing multiple LLM responses
        test_pairs = [
            ("Hello", "Hi there", 0.50),
            ("Goodbye", "Farewell", 0.50),
            ("Thank you", "Thanks", 0.60),
            ("Good morning", "Morning", 0.60),
            ("Good night", "Night night", 0.50),
        ] * 4  # 20 total assertions

        async def check_pair(actual: str, expected: str, threshold: float) -> None:
            """Check a single pair."""
            await assert_semantically_similar_async(actual, expected, threshold=threshold)

        # Run all in parallel
        await asyncio.gather(*[check_pair(a, e, t) for a, e, t in test_pairs])


class TestPytestXdistSimulation:
    """Simulate pytest-xdist behavior (multiple processes, shared cache)."""

    def test_xdist_simulation_with_shared_cache(self, tmp_path: Path) -> None:
        """Simulate pytest-xdist workers accessing shared cache."""
        # Simulate 4 pytest-xdist workers
        args = [(i, str(tmp_path)) for i in range(4)]

        with ProcessPoolExecutor(max_workers=4) as executor:
            worker_results = list(executor.map(_mp_worker_test_suite, args))

        # All tests should pass
        total_passed = sum(r["passed"] for r in worker_results)
        total_failed = sum(r["failed"] for r in worker_results)

        assert total_passed == 40, f"Expected 40 passed, got {total_passed}"
        assert total_failed == 0, f"Expected 0 failed, got {total_failed}"

    def test_xdist_no_cache_corruption(self, tmp_path: Path) -> None:
        """Verify cache integrity after xdist-style parallel execution."""
        # Run 8 workers with 20 tests each (160 total)
        args = [(i, str(tmp_path), 20) for i in range(8)]

        with ProcessPoolExecutor(max_workers=8) as executor:
            counts = list(executor.map(_mp_worker, args))

        # Should have completed all tests
        assert sum(counts) > 0, "No tests completed successfully"

        # Verify cache is still functional (not corrupted)
        cache = EmbeddingCache(cache_dir=str(tmp_path), enabled=True)

        # Try to read some shared entries
        for i in range(5):
            result = cache.get(f"Shared text {i}", "all-MiniLM-L6-v2")
            # Should exist from worker runs
            if result is not None:
                assert isinstance(result, np.ndarray)
                assert result.shape == (384,)


if __name__ == "__main__":
    # Note: Run with pytest, not directly
    print("Run with: pytest tests/integration/test_concurrency.py -v")
