#!/usr/bin/env python3

import sys
import os
import random
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grplist as gl

CLOSE = lambda a, b: abs(a - b) <= 3


def norm(groups):
    """Normalize group output for order-independent comparison."""
    return sorted(sorted(g) for g in groups)


# ---------------------------------------------------------------------------
# groupList / groupList2 / groupList3 — empty and single-element edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_empty_array(self, fn):
        assert fn([], CLOSE) == []
        assert fn([], CLOSE, True) == []

    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_single_keys(self, fn):
        assert fn([99], CLOSE, False) == [[0]]

    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_single_vals(self, fn):
        # bug fix: vals=True should return the value, not the index 0
        assert fn([99], CLOSE, True) == [[99]]
        assert fn(['hello'], lambda a, b: True, True) == [['hello']]

    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_single_negative_value(self, fn):
        assert fn([-7], CLOSE, True) == [[-7]]


# ---------------------------------------------------------------------------
# Two-element cases
# ---------------------------------------------------------------------------

class TestTwoElements:
    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_two_that_group(self, fn):
        assert norm(fn([1, 2], CLOSE, True)) == [[1, 2]]

    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_two_that_dont_group(self, fn):
        assert norm(fn([1, 100], CLOSE, True)) == [[1], [100]]

    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_two_boundary_exactly_3_apart(self, fn):
        assert norm(fn([1, 4], CLOSE, True)) == [[1, 4]]

    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_two_boundary_4_apart(self, fn):
        assert norm(fn([1, 5], CLOSE, True)) == [[1], [5]]


# ---------------------------------------------------------------------------
# Canonical docstring example
# ---------------------------------------------------------------------------

class TestCanonical:
    CANONICAL = [1, 3, 6, 10, 12, 14, 21, 35]
    EXPECTED_VALS = norm([[1, 3, 6], [10, 12, 14], [21], [35]])
    EXPECTED_KEYS = norm([[0, 1, 2], [3, 4, 5], [6], [7]])

    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_canonical_vals(self, fn):
        assert norm(fn(self.CANONICAL, CLOSE, True)) == self.EXPECTED_VALS

    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_canonical_keys(self, fn):
        assert norm(fn(self.CANONICAL, CLOSE, False)) == self.EXPECTED_KEYS


# ---------------------------------------------------------------------------
# All-same and no-groups extremes
# ---------------------------------------------------------------------------

class TestExtremes:
    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_all_same_value(self, fn):
        t = [5] * 10
        r = fn(t, CLOSE, True)
        assert len(r) == 1
        assert sorted(r[0]) == t

    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_no_elements_group(self, fn):
        t = [1, 10, 20, 30]
        r = fn(t, CLOSE, True)
        assert norm(r) == [[1], [10], [20], [30]]

    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_all_elements_one_group_via_chain(self, fn):
        t = list(range(1, 19))  # 1..18, each within 3 of its neighbours
        r = fn(t, CLOSE, True)
        assert len(r) == 1
        assert sorted(r[0]) == t


# ---------------------------------------------------------------------------
# Transitive / merge tests
# ---------------------------------------------------------------------------

class TestTransitiveMerge:
    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_bridge_merges_two_groups(self, fn):
        # 7 is within 3 of both 6 (group A) and 10 (group B) → merges them
        t = [1, 3, 6, 10, 12, 14, 21, 35, 7, 23]
        expected = norm([[1, 3, 6, 7, 10, 12, 14], [21, 23], [35]])
        assert norm(fn(t, CLOSE, True)) == expected

    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_two_distinct_clusters(self, fn):
        t = list(range(1, 10)) + list(range(20, 29))
        r = norm(fn(t, CLOSE, True))
        assert r == [sorted(range(1, 10)), sorted(range(20, 29))]

    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_split_cluster_with_gap(self, fn):
        # 1-9 chain together; gap of 10 between 9 and 20; 20-28 chain together
        t = [1, 2, 3, 4, 5, 6, 7, 8, 9, 20, 21, 22, 23, 24, 25, 26, 27, 28]
        r = fn(t, CLOSE, True)
        assert len(r) == 2
        assert sorted(r[0] + r[1]) == sorted(t)

    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_out_of_order_input(self, fn):
        # Same logical groups regardless of input order
        t = [1, 10, 20, 5, 15, 3, 7]
        r = norm(fn(t, CLOSE, True))
        # 1,3,5,7,10 are all within 3 of some chain member → one group
        # 15 is within 3 of 13..18 - 15 and 13: |15-13|=2, but no 13.
        # 10 and 7 are ≤3 apart; 5 and 7 are ≤3; 5 and 3 are ≤3; 3 and 1 are ≤3
        # 10 and 7: |10-7|=3 ✓, so 1,3,5,7,10 in one group
        # 15 and 12: no 12 here. 15 and 20: |15-20|=5 > 3. 15 and 13: no 13.
        # Wait: 15 and 13: not present. 15 and 12: not present.
        # 15 alone? |15-20|=5 > 3; |15-10|=5 > 3. Yes, 15 is alone.
        # 20 alone? |20-15|=5 > 3. Yes.
        assert [1, 3, 5, 7, 10] in [sorted(g) for g in r]

    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_complex_merge_scenario(self, fn):
        t = [1, 10, 20, 30, 40, 35, 32, 5, 11, 2, 3, 16, 17, 12, 33, 34, 35, 33, 3, 42]
        r1 = norm(gl.groupList(t, CLOSE, True))
        r2 = norm(gl.groupList2(t, CLOSE, True))
        assert r1 == r2


# ---------------------------------------------------------------------------
# Keys (index) mode
# ---------------------------------------------------------------------------

class TestKeysMode:
    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_keys_are_indices(self, fn):
        t = [100, 101, 200]
        r = fn(t, CLOSE, False)
        # 100 (idx 0) and 101 (idx 1) group together; 200 (idx 2) alone
        assert norm(r) == [[0, 1], [2]]

    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_single_key_is_zero(self, fn):
        assert fn([999], CLOSE, False) == [[0]]

    @pytest.mark.parametrize("fn", [gl.groupList, gl.groupList2, gl.groupList3, gl.groupList4])
    def test_keys_cover_all_indices(self, fn):
        t = [1, 3, 6, 10, 12, 14, 21, 35]
        r = fn(t, CLOSE, False)
        all_indices = sorted(i for g in r for i in g)
        assert all_indices == list(range(len(t)))


# ---------------------------------------------------------------------------
# String / non-numeric comparison functions
# ---------------------------------------------------------------------------

class TestStringGrouping:
    def _any_letter(self, a, b):
        return any(c in b for c in a)

    def test_shared_letters_grouplist2(self):
        t = ['on', 'tw', 'th', 'fo', 'fi', 'si', 'te', 'zk']
        r = gl.groupList2(t, self._any_letter, True)
        zk_groups = [g for g in r if 'zk' in g]
        assert len(zk_groups) == 1
        assert zk_groups[0] == ['zk']

    def test_all_share_one_letter(self):
        t = ['ab', 'bc', 'cd']
        r = gl.groupList(t, self._any_letter, True)
        assert len(r) == 1  # a-b, b-c, c-d bridge all three


# ---------------------------------------------------------------------------
# Dict-valued grouping (overlapping ranges)
# ---------------------------------------------------------------------------

class TestOverlappingRanges:
    TRACKS = [
        {'beg': 2,  'end': 10},
        {'beg': 20, 'end': 25},
        {'beg': 4,  'end': 7},
        {'beg': 30, 'end': 35},
        {'beg': 8,  'end': 17},
        {'beg': 22, 'end': 28},
        {'beg': 33, 'end': 45},
        {'beg': 1,  'end': 4},
    ]
    OVERLAPS = staticmethod(lambda a, b: a['beg'] <= b['end'] and a['end'] >= b['beg'])

    def test_three_groups(self):
        r = gl.groupList2(self.TRACKS, self.OVERLAPS, True)
        assert len(r) == 3

    def test_correct_group_sizes(self):
        r = gl.groupList2(self.TRACKS, self.OVERLAPS, True)
        sizes = sorted(len(g) for g in r)
        assert sizes == [2, 2, 4]

    def test_all_three_agree(self):
        r1 = sorted(len(g) for g in gl.groupList(self.TRACKS, self.OVERLAPS, True))
        r2 = sorted(len(g) for g in gl.groupList2(self.TRACKS, self.OVERLAPS, True))
        r3 = sorted(len(g) for g in gl.groupList3(self.TRACKS, self.OVERLAPS, True))
        assert r1 == r2 == r3


# ---------------------------------------------------------------------------
# groupDict / groupDict2
# ---------------------------------------------------------------------------

class TestGroupDict:
    D = {'k0': 1, 'k1': 3, 'k2': 6, 'k3': 10, 'k4': 12,
         'k5': 14, 'k6': 21, 'k7': 35, 'k8': 7, 'k9': 23}

    @pytest.mark.parametrize("fn", [gl.groupDict, gl.groupDict2, gl.groupDict3, gl.groupDict4])
    def test_vals_mode(self, fn):
        expected = norm([[1, 3, 6, 7, 10, 12, 14], [21, 23], [35]])
        assert norm(fn(self.D, CLOSE, True)) == expected

    @pytest.mark.parametrize("fn", [gl.groupDict, gl.groupDict2, gl.groupDict3, gl.groupDict4])
    def test_keys_mode(self, fn):
        r = fn(self.D, CLOSE, False)
        r_norm = sorted(sorted(g) for g in r)
        assert r_norm == sorted([
            sorted(['k0', 'k1', 'k2', 'k3', 'k4', 'k5', 'k8']),
            sorted(['k6', 'k9']),
            ['k7'],
        ])

    @pytest.mark.parametrize("fn", [gl.groupDict, gl.groupDict2, gl.groupDict3, gl.groupDict4])
    def test_empty_dict(self, fn):
        assert fn({}, CLOSE) == []

    @pytest.mark.parametrize("fn", [gl.groupDict, gl.groupDict2, gl.groupDict3, gl.groupDict4])
    def test_single_key_vals(self, fn):
        assert fn({'a': 42}, CLOSE, True) == [[42]]

    @pytest.mark.parametrize("fn", [gl.groupDict, gl.groupDict2, gl.groupDict3, gl.groupDict4])
    def test_single_key_keys(self, fn):
        assert fn({'a': 42}, CLOSE, False) == [['a']]

    @pytest.mark.parametrize("fn", [gl.groupDict, gl.groupDict2, gl.groupDict3, gl.groupDict4])
    def test_two_keys_group(self, fn):
        assert norm(fn({'a': 1, 'b': 2}, CLOSE, True)) == [[1, 2]]

    @pytest.mark.parametrize("fn", [gl.groupDict, gl.groupDict2, gl.groupDict3, gl.groupDict4])
    def test_two_keys_no_group(self, fn):
        assert norm(fn({'a': 1, 'b': 100}, CLOSE, True)) == [[1], [100]]


# ---------------------------------------------------------------------------
# groupList vs groupList2 agreement (parametrized)
# ---------------------------------------------------------------------------

class TestConsistency:
    @pytest.mark.parametrize("t", [
        [1, 6, 3],
        [10, 20, 30, 40, 50],
        [1, 3, 6, 10, 12, 14, 21, 35],
        [1, 3, 6, 10, 12, 14, 21, 35, 7, 23],
        [1, 10, 20, 5, 15, 3, 7],
        [1, 1, 1, 1, 1, 1],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 20, 21, 22, 23, 24, 25, 26, 27, 28],
    ])
    def test_agree_vals(self, t):
        r1 = norm(gl.groupList(t, CLOSE, True))
        r2 = norm(gl.groupList2(t, CLOSE, True))
        r3 = norm(gl.groupList3(t, CLOSE, True))
        r4 = norm(gl.groupList4(t, CLOSE, True))
        assert r1 == r2 == r3 == r4

    @pytest.mark.parametrize("t", [
        [1, 6, 3],
        [10, 20, 30, 40, 50],
        [1, 3, 6, 10, 12, 14, 21, 35],
        [1, 3, 6, 10, 12, 14, 21, 35, 7, 23],
    ])
    def test_agree_keys(self, t):
        r1 = norm(gl.groupList(t, CLOSE, False))
        r2 = norm(gl.groupList2(t, CLOSE, False))
        r3 = norm(gl.groupList3(t, CLOSE, False))
        r4 = norm(gl.groupList4(t, CLOSE, False))
        assert r1 == r2 == r3 == r4


# ---------------------------------------------------------------------------
# groupList3 — Union-Find specific behaviours
# ---------------------------------------------------------------------------

class TestGroupList3:
    """Tests that target the properties specific to the Union-Find implementation."""

    def test_predicate_calls_equal_grouplist(self):
        # groupList3 (lazy find) calls the predicate for every pair, same as
        # groupList.  find() is only invoked on True results so there is no
        # O(n^2) find() overhead — but the call count itself matches groupList.
        n = 20
        count1, count3 = [0], [0]
        def pred1(a, b): count1[0] += 1; return abs(a-b) <= 3
        def pred3(a, b): count3[0] += 1; return abs(a-b) <= 3
        t = list(range(n))
        gl.groupList(t, pred1)
        gl.groupList3(t, pred3)
        assert count3[0] == count1[0] == n * (n - 1) // 2

    def test_same_predicate_calls_as_grouplist_sparse(self):
        # Sparse case: no matches → every pair checked, find() never called.
        t = [1, 100, 200, 300, 400]
        count1, count3 = [0], [0]
        def pred1(a, b): count1[0] += 1; return abs(a-b) <= 3
        def pred3(a, b): count3[0] += 1; return abs(a-b) <= 3
        gl.groupList(t, pred1)
        gl.groupList3(t, pred3)
        assert count3[0] == count1[0]

    def test_union_find_handles_many_merges(self):
        # A long chain that causes many successive merges.  This exercises the
        # path-compression and union-by-rank paths thoroughly.
        t = list(range(100))
        r = gl.groupList3(t, lambda a, b: abs(a-b) <= 3, vals=True)
        assert len(r) == 1
        assert sorted(r[0]) == t

    def test_all_singletons_no_merges(self):
        # Worst case for skipping: nothing connects, every pair is checked,
        # no unions occur.  Result must still be correct.
        t = [0, 100, 200, 300, 500, 700]
        r = gl.groupList3(t, lambda a, b: abs(a-b) <= 3, vals=True)
        assert norm(r) == [[v] for v in sorted(t)]

    def test_star_topology(self):
        # One central item connects to all others, but no two non-central
        # items connect to each other.  Forces many merges through one root.
        center = 50
        spokes = [1, 20, 80, 99]
        t = [center] + spokes  # centre is index 0
        r = gl.groupList3(t, lambda a, b: abs(a-b) >= 30, vals=True)
        # 50 and 1: |50-1|=49 ≥ 30 ✓; 50 and 20: 30 ✓; 50 and 80: 30 ✓;
        # 50 and 99: 49 ✓; 1 and 20: 19 < 30 ✗; 80 and 99: 19 < 30 ✗
        # → all five end up in one group via the centre
        assert len(r) == 1
        assert sorted(r[0]) == sorted(t)

    def test_path_compression_correctness_deep_chain(self):
        # Items that connect strictly left-to-right: 0-1, 1-2, 2-3, ...
        # This creates the deepest possible initial trees before compression.
        # Verify the final result is still one group.
        n = 50
        t = list(range(n))
        r = gl.groupList3(t, lambda a, b: abs(a-b) == 1, vals=True)
        assert len(r) == 1
        assert sorted(r[0]) == t

    def test_exported_from_package(self):
        for name in ('groupList3', 'groupList4', 'groupDict3', 'groupDict4'):
            assert hasattr(gl, name) and callable(getattr(gl, name))


# ---------------------------------------------------------------------------
# groupList4 — tail-pointer merge specific behaviours
# ---------------------------------------------------------------------------

class TestGroupList4:
    """Verify the O(1) tail-pointer merge produces correct results."""

    def test_merge_two_groups(self):
        # 5 bridges [1,3] and [7,9] → all four in one group
        t = [1, 3, 7, 9, 5]
        r = norm(gl.groupList4(t, lambda a, b: abs(a-b) <= 2, True))
        assert r == [[1, 3, 5, 7, 9]]

    def test_three_way_merge(self):
        # item at index 4 (value 5) connects three separate groups
        t = [1, 2, 7, 8, 5]   # 5 is within 2 of both 3 (not present) but...
        # Actually: 1-2 group, 7-8 group, 5 connects to neither with threshold 2
        # Use threshold 3: 5-2=3 ✓, 8-5=3 ✓
        r = norm(gl.groupList4(t, lambda a, b: abs(a-b) <= 3, True))
        assert r == [[1, 2, 5, 7, 8]]

    def test_identical_predicate_calls_to_grouplist2(self):
        # groupList4 uses insert-after-match (same as groupList2), so the two
        # functions make exactly the same predicate calls on every input.
        random.seed(42)
        t = [random.randint(0, 50) for _ in range(200)]
        c2, c4 = [0], [0]
        gl.groupList2(t, lambda a, b: (c2.__setitem__(0, c2[0]+1), abs(a-b)<=3)[1])
        gl.groupList4(t, lambda a, b: (c4.__setitem__(0, c4[0]+1), abs(a-b)<=3)[1])
        assert c4[0] == c2[0]

    def test_merge_eliminates_chain_end_walk(self):
        # Build a scenario that forces many merges (each new item bridges groups).
        # With groupList2 this triggers the O(chain_len) walk; groupList4 avoids it.
        # Both must produce the same result.
        t = list(range(0, 60, 2)) + list(range(1, 60, 2))  # evens then odds
        pred = lambda a, b: abs(a - b) <= 1
        assert norm(gl.groupList4(t, pred, True)) == norm(gl.groupList2(t, pred, True))

    def test_chain_order_preserves_all_members(self):
        # Tail-append changes insertion order vs groupList2 but every member
        # must still appear in the output exactly once.
        random.seed(0)
        t = [random.randint(0, 30) for _ in range(100)]
        r = gl.groupList4(t, lambda a, b: abs(a-b) <= 3, True)
        assert sorted(v for g in r for v in g) == sorted(t)

    def test_keys_mode(self):
        t = [1, 3, 6, 10, 12, 14, 21, 35]
        assert norm(gl.groupList4(t, lambda a, b: abs(a-b) <= 3, False)) == \
               norm(gl.groupList2(t, lambda a, b: abs(a-b) <= 3, False))


# ---------------------------------------------------------------------------
# Package metadata
# ---------------------------------------------------------------------------

class TestPackageMetadata:
    def test_project_dict_exists(self):
        assert hasattr(gl, '_project')
        assert isinstance(gl._project, dict)

    def test_required_keys_present(self):
        for key in ('name', 'version', 'description', 'author'):
            assert key in gl._project, f"_project missing key: {key}"

    def test_version_accessible(self):
        assert hasattr(gl, '__version__')
        assert gl.__version__

    def test_author_accessible(self):
        assert hasattr(gl, '__author__')
        assert gl.__author__
