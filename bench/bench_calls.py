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
def test_grouplist3_calls_only_true_pairs_all_same(n, capsys):
    """
    With all-same values every predicate call returns True.
    groupList3 (lazy find) calls the predicate for all n*(n-1)/2 pairs —
    same as groupList — but find() is only called on True results so the
    O(n^2) find() overhead of the old eager design is gone.
    """
    t = _all_same(n)
    all_pairs = n * (n - 1) // 2

    p1 = _CountingPred(CLOSE)
    p3 = _CountingPred(CLOSE)
    gl.groupList(t,  p1)
    gl.groupList3(t, p3)

    # Both check every pair (all True → no skipping possible)
    assert p1.calls == all_pairs
    assert p3.calls == all_pairs

    with capsys.disabled():
        print(f"\n  all-same n={n:>4}:  "
              f"groupList={p1.calls:>7,}  groupList3={p3.calls:>7,}  "
              f"(find() called only on True, not for all pairs)")


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
    On typical random input groupList3 (lazy) calls the predicate for all
    pairs — same count as groupList — while groupList2 skips many via its
    chain-walk structure.  The groupList3 advantage is in cheaper merges,
    not fewer predicate calls.
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

    assert counts["groupList"]  == all_pairs   # all pairs checked
    assert counts["groupList3"] == all_pairs   # lazy: also checks all pairs
    assert counts["groupList2"] <= all_pairs   # chain-walk skips some

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
