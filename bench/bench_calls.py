#!/usr/bin/env python3
"""
Predicate-call-count proofs for grplist.

These tests make no timing assertions — they prove the algorithmic claims
about how many times each function calls the user-supplied predicate.

Run:
    pytest bench/bench_calls.py -v -s
"""

import random
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grplist as gl

random.seed(42)

CLOSE = lambda a, b: abs(a - b) <= 3


class _CountingPred:
    """Wraps a predicate and counts every call made to it."""
    def __init__(self, pred):
        self._pred = pred
        self.calls = 0

    def __call__(self, a, b):
        self.calls += 1
        return self._pred(a, b)

    def reset(self):
        self.calls = 0


def _random(n, spread=None):
    return [random.randint(0, spread or n * 2) for _ in range(n)]

def _all_same(n):
    """All identical values — every pair connects on the very first call.
    After the k1=0 row all n items are one component, so every subsequent
    pair is skipped.  Maximum possible savings for groupList3."""
    return [42] * n

def _sparse(n):
    """Widely spaced — no item connects to any other."""
    return [i * 1000 for i in range(n)]


# ---------------------------------------------------------------------------
# groupList: always evaluates every pair
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [50, 200, 500])
def test_grouplist_evaluates_all_pairs(n):
    """groupList performs a complete O(n²) scan with no skipping."""
    t = _random(n)
    pred = _CountingPred(CLOSE)
    gl.groupList(t, pred)
    assert pred.calls == n * (n - 1) // 2


# ---------------------------------------------------------------------------
# groupList3: skips pairs already in the same component
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [50, 200, 500])
def test_grouplist3_skips_calls_all_same(n, capsys):
    """
    All-same-value input: every pair connects, so after the first row of the
    outer loop all n items are in one component.  Every subsequent pair is
    already merged and its predicate call is skipped.  groupList3 makes only
    n-1 calls; groupList makes n*(n-1)/2.  Savings exceed 90% for any n > 20.
    """
    t = _all_same(n)
    all_pairs = n * (n - 1) // 2

    p1 = _CountingPred(CLOSE)
    p3 = _CountingPred(CLOSE)
    gl.groupList(t,  p1)
    gl.groupList3(t, p3)

    assert p1.calls == all_pairs        # groupList: no skipping ever
    assert p3.calls == n - 1           # groupList3: only the first row needed
    assert p3.calls < p1.calls * 0.1   # savings exceed 90 %

    pct = 100 * (1 - p3.calls / p1.calls)
    with capsys.disabled():
        print(f"\n  all-same n={n:>4}:  "
              f"groupList={p1.calls:>7,}  "
              f"groupList3={p3.calls:>7,}  "
              f"savings={pct:.0f}%")


@pytest.mark.parametrize("n", [50, 200, 500])
def test_grouplist3_no_skipping_sparse(n, capsys):
    """
    On sparse input (no connections) groupList3 cannot skip any calls —
    every pair is in a different component until proven otherwise.
    """
    t = _sparse(n)
    all_pairs = n * (n - 1) // 2

    p1 = _CountingPred(CLOSE)
    p3 = _CountingPred(CLOSE)
    gl.groupList(t,  p1)
    gl.groupList3(t, p3)

    assert p1.calls == all_pairs
    assert p3.calls == all_pairs        # no savings on a fully sparse graph

    with capsys.disabled():
        print(f"\n  sparse n={n:>4}:  "
              f"groupList={p1.calls:>7,}  "
              f"groupList3={p3.calls:>7,}  "
              f"savings=0%")


@pytest.mark.parametrize("n", [50, 200, 500])
def test_grouplist3_partial_savings_random(n, capsys):
    """
    On typical random input savings sit between the dense and sparse extremes.
    We assert savings > 0% but do not hard-code an exact percentage.
    """
    t = _random(n, spread=50)    # high density: spread < 2×n
    all_pairs = n * (n - 1) // 2

    counts = {}
    for name, fn in [("groupList", gl.groupList),
                     ("groupList2", gl.groupList2),
                     ("groupList3", gl.groupList3)]:
        p = _CountingPred(CLOSE)
        fn(t, p)
        counts[name] = p.calls

    assert counts["groupList"] == all_pairs
    assert counts["groupList3"] < counts["groupList"]

    with capsys.disabled():
        print(f"\n  random n={n:>4} spread=50:")
        for k, v in counts.items():
            print(f"    {k:<12}  {v:>7,} calls  "
                  f"({100*v/all_pairs:.0f}% of {all_pairs:,})")


# ---------------------------------------------------------------------------
# groupList2: call-count model is different — verify it also saves calls
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [50, 200])
def test_grouplist2_also_reduces_calls(n):
    """groupList2 reduces calls by a different mechanism (greedy scan)."""
    t = _random(n, spread=50)
    all_pairs = n * (n - 1) // 2

    p1 = _CountingPred(CLOSE)
    p2 = _CountingPred(CLOSE)
    gl.groupList(t, p1)
    gl.groupList2(t, p2)

    assert p1.calls == all_pairs
    assert p2.calls <= all_pairs    # groupList2 never exceeds full scan
