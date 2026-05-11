#!/usr/bin/env python3
"""
Timing benchmarks for grplist.

Requires:
    pip install pytest-benchmark

Run:
    pytest bench/bench_timing.py -v
    pytest bench/bench_timing.py -v --benchmark-sort=name
    pytest bench/bench_timing.py -v --benchmark-compare   # compare runs
    pytest bench/bench_timing.py -v --benchmark-save=baseline

What this proves
----------------
cheap_pred / random:   groupList2 wins — its greedy scan has less Python
                        overhead per pair than groupList3's find() loops.
expensive_pred / random: groupList3 wins — skipping 50–70% of predicate
                        calls outweighs the find() overhead when each
                        call is slow.
cheap_pred / dense:    groupList2 dominates — merges early and stops scanning
                        within each group; groupList / groupList3 are similar.
cheap_pred / sparse:   all three are similar — no skipping is possible and
                        every pair must be evaluated.
"""

import random
import hashlib
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grplist as gl

random.seed(42)

CLOSE = lambda a, b: abs(a - b) <= 3


def _expensive(a, b):
    """Simulate a slow predicate (image similarity, edit distance, etc.)."""
    hashlib.sha256(f"{a}:{b}".encode()).digest()
    return abs(a - b) <= 3


def _random(n, spread=None):
    return [random.randint(0, spread or n * 2) for _ in range(n)]

def _dense(n):
    return list(range(n))

def _sparse(n):
    return [i * 1000 for i in range(n)]


ALL = pytest.mark.parametrize(
    "fn",
    [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4],
    ids=["groupList", "groupList2", "groupList3", "groupList4"],
)


# ---------------------------------------------------------------------------
# Cheap predicate — random input
# Expected winner: groupList2
# ---------------------------------------------------------------------------

@ALL
@pytest.mark.parametrize("n", [100, 500, 1000])
def test_cheap_random(benchmark, fn, n):
    t = _random(n)
    benchmark.extra_info["input"] = f"random n={n}"
    benchmark(fn, t, CLOSE, True)


# ---------------------------------------------------------------------------
# Expensive predicate — sparse random input
# With spread=2n, the graph is sparse: groupList3 skips few calls and its
# find() overhead makes it the slowest.  All three are broadly similar.
# ---------------------------------------------------------------------------

@ALL
@pytest.mark.parametrize("n", [100, 300])
def test_expensive_sparse_random(benchmark, fn, n):
    t = _random(n)                      # spread = 2n → ~3 % of pairs connect
    benchmark.extra_info["input"] = f"random n={n} spread={n*2} expensive_pred"
    benchmark(fn, t, _expensive, True)


# ---------------------------------------------------------------------------
# Expensive predicate — high-connectivity random input
# With spread=n//5, ~60 % of pairs are within threshold: groupList3 skips
# the majority of predicate calls and its lower call-count pays off here.
# Expected winner: groupList3
# ---------------------------------------------------------------------------

@ALL
@pytest.mark.parametrize("n", [100, 300])
def test_expensive_dense_random(benchmark, fn, n):
    t = _random(n, spread=max(n // 5, 10))
    benchmark.extra_info["input"] = f"random n={n} spread={max(n//5,10)} expensive_pred"
    benchmark(fn, t, _expensive, True)


# ---------------------------------------------------------------------------
# Cheap predicate — dense input (one big group)
# Expected winner: groupList2 by a large margin
# ---------------------------------------------------------------------------

@ALL
@pytest.mark.parametrize("n", [100, 500])
def test_cheap_dense(benchmark, fn, n):
    t = _dense(n)
    benchmark.extra_info["input"] = f"dense n={n}"
    benchmark(fn, t, CLOSE, True)


# ---------------------------------------------------------------------------
# Cheap predicate — sparse input (no connections)
# Expected result: all three similar — no skipping possible
# ---------------------------------------------------------------------------

@ALL
@pytest.mark.parametrize("n", [100, 500])
def test_cheap_sparse(benchmark, fn, n):
    t = _sparse(n)
    benchmark.extra_info["input"] = f"sparse n={n}"
    benchmark(fn, t, CLOSE, True)
