from contextlib import contextmanager
import time


@contextmanager
def timed(name):
    start = time.perf_counter()

    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"⏱️ {name}: {elapsed:.3f}s")
