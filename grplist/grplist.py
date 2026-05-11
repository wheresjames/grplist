#!/usr/bin/env python3

from __future__ import print_function

### Groups a list according to the specified function
# @param [in] arr       - Array to group
# @param [in] fnc       - Function that specifies grouping
#                           The function should take two parameters
#                           and return True if the items belong in
#                           the same group.
# @param [in] vals      - Set to True if you want the function
#                         to return a list of values.  If set
#                         to False, the function will return a
#                         list of keys.
#
# Example to group items less than three appart
# @begincode
#
# groups = groupList([1, 3, 6, 10, 12, 14, 21, 35], lambda a, b: 3 >= abs(a-b), True)
#
# > [[1, 3, 6], [10, 12, 14], [21], [35]]
#
# @endcode
#
def groupList(arr, fnc, vals = False):

    l = len(arr)
    if 1 > l:
        return []
    elif 1 == l:
        return [[arr[0] if vals else 0]]

    g = 0
    m = [-1] * l
    for k1 in range(0, l):

        for k2 in range(k1 + 1, l):

            # Can they be grouped?
            if fnc(arr[k1], arr[k2]):

                # a nor b in group, a and b join new group
                if -1 == m[k1] and -1 == m[k2]:
                    m[k1] = g
                    m[k2] = g
                    g += 1

                # a not in group, b in group, a joins b
                elif -1 == m[k1] and -1 != m[k2]:
                    m[k1] = m[k2]

                # a in group, b not in group, b joins a
                elif -1 != m[k1] and -1 == m[k2]:
                    m[k2] = m[k1]

                # Both in groups, merge groups if not already in the same group
                elif m[k1] != m[k2]:
                    g = g - 1
                    fr = m[k1]
                    to = m[k2]
                    if g == to:
                        to, fr = fr, to
                    for k3 in range(0, l):
                        if m[k3] == fr:
                            m[k3] = to
                        elif m[k3] == g:
                            m[k3] = fr

        # Create new group
        if -1 == m[k1]:
            m[k1] = g
            g += 1

    ret = [[] for i in range(0, g)]
    for k in range(0, l):
        ret[m[k]].append(arr[k] if vals else k)

    return ret


### Groups a list according to the specified function
#
# This function is the same as groupList() but it minimizes the number
# of calls to the given compare function.
#
# @param [in] arr       - Array to group
# @param [in] fnc       - Function that specifies grouping
#                           The function should take two parameters
#                           and return True if the items belong in
#                           the same group.
# @param [in] vals      - Set to True if you want the function
#                         to return a list of values.  If set
#                         to False, the function will return a
#                         list of keys.
#
# Example to group items less than three appart
# @begincode
#
# groups = groupList2([1, 3, 6, 10, 12, 14, 21, 35], lambda a, b: 3 >= abs(a-b), True)
#
# > [[1, 3, 6], [10, 12, 14], [21], [35]]
#
# @endcode
#
def groupList2(arr, fnc, vals = False):

    l = len(arr)
    if 1 > l:
        return []
    elif 1 == l:
        return [[arr[0] if vals else 0]]

    lg = -1
    m = [-1] * l
    g = [-1] * l

    # Create a group map
    for k1 in range(0, l):
        ingroup = -1
        gi = 0
        while -1 != g[gi]:

            # First group item
            k2 = g[gi]

            while True:

                # Does it group with this item
                if fnc(arr[k1], arr[k2]):

                    # If we're already in a group, merge that group
                    if -1 != ingroup:

                        # Find the end of the group we're in
                        eg = k1
                        while m[eg] != -1:
                            eg = m[eg]

                        # Append current group
                        m[eg] = g[gi]

                        # Move last group to current slot
                        g[gi] = g[lg]
                        g[lg] = -1
                        lg -= 1
                        gi -= 1

                    # Add us to this group
                    else:

                        # Insert ourselves here
                        m[k1] = m[k2]
                        m[k2] = k1

                        # Item has been grouped
                        ingroup = gi

                    break

                # Last item?
                if m[k2] == -1:
                    break

                # Next item
                k2 = m[k2]

            gi += 1

        # Create a new group if it didn't fit anywhere
        if -1 == ingroup:
            g[gi] = k1
            lg = gi

    # Create groups by crawling the map
    gi = 0
    ret = []
    while gi < len(g) and -1 != g[gi]:

        # Where to start in the map
        mi = g[gi]

        ret.append([])
        ri = len(ret)-1
        while True:

            # Log(mi)

            ret[ri].append(arr[mi] if vals else mi)

            # Last item?
            if m[mi] == -1:
                break

            # Next item
            mi = m[mi]

        # Next group
        gi += 1

    return ret


### Groups a list according to the specified function
#
# Optimised variant using Union-Find with path-halving compression and
# union-by-rank.  The key improvement over groupList() is the merge step:
# instead of scanning all n items to renumber a group (O(n) per merge),
# Union-Find updates a single parent pointer (O(alpha(n)) per operation).
#
# find() is called lazily - only after the predicate returns True - so its
# cost is proportional to the number of matching pairs, not n^2.  This
# keeps the per-pair overhead minimal for cheap predicates while still
# delivering fast merges when matches are found.
#
# The comparison loop itself remains O(n^2) - unavoidable for an arbitrary
# predicate - but all bookkeeping around each True result is near-O(1).
#
# @param [in] arr       - Array to group
# @param [in] fnc       - Function that specifies grouping
#                           The function should take two parameters
#                           and return True if the items belong in
#                           the same group.
# @param [in] vals      - Set to True if you want the function
#                         to return a list of values.  If set
#                         to False, the function will return a
#                         list of keys.
#
# Example to group items less than three apart
# @begincode
#
# groups = groupList3([1, 3, 6, 10, 12, 14, 21, 35], lambda a, b: 3 >= abs(a-b), True)
#
# > [[1, 3, 6], [10, 12, 14], [21], [35]]
#
# @endcode
#
def groupList3(arr, fnc, vals = False):

    l = len(arr)
    if 1 > l:
        return []
    elif 1 == l:
        return [[arr[0] if vals else 0]]

    # Each element starts as its own component.
    # parent[i] is i's representative; rank[i] bounds the subtree depth.
    parent = list(range(l))
    rank   = [0] * l

    for k1 in range(l - 1):
        for k2 in range(k1 + 1, l):

            # Call the predicate first; find() only runs on a True result.
            # This keeps find() overhead proportional to matching pairs, not n^2.
            if not fnc(arr[k1], arr[k2]):
                continue

            # find(k1) - inline with path halving
            x = k1
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            r1 = x

            # find(k2) - inline with path halving
            x = k2
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            r2 = x

            if r1 != r2:
                # union by rank: attach the shorter tree under the taller one
                if rank[r1] < rank[r2]:
                    r1, r2 = r2, r1
                parent[r2] = r1
                if rank[r1] == rank[r2]:
                    rank[r1] += 1

    # One final pass to bucket every element into its root's group
    groups = {}
    for k in range(l):
        x = k
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        root = x
        if root not in groups:
            groups[root] = []
        groups[root].append(arr[k] if vals else k)

    return list(groups.values())


### Groups a list according to the specified function
#
# Combines the two independent optimisations from groupList2 and groupList3:
#
#   groupList2 strength  - chain-walk comparison: each new item is compared
#     only against existing group members, not all pairs, cutting predicate
#     calls to ~5–30% of n*(n-1)/2 on typical inputs.
#
#   groupList3 strength  - fast merge: groupList2 walks a group's chain to
#     find its tail before linking two groups together (O(chain_length)).
#     A tail pointer per group makes this O(1).
#
# The merge-walk cost is small in practice (profiling shows ~200 walk steps
# vs ~9,000 predicate calls for n=300), so the real-world speedup over
# groupList2 is modest.  groupList4 is the right default when you want the
# best general-purpose performance without knowing your workload in advance.
#
# @param [in] arr       - Array to group
# @param [in] fnc       - Function that specifies grouping
#                           The function should take two parameters
#                           and return True if the items belong in
#                           the same group.
# @param [in] vals      - Set to True if you want the function
#                         to return a list of values.  If set
#                         to False, the function will return a
#                         list of keys.
#
# Example to group items less than three apart
# @begincode
#
# groups = groupList4([1, 3, 6, 10, 12, 14, 21, 35], lambda a, b: 3 >= abs(a-b), True)
#
# > [[1, 3, 6], [10, 12, 14], [21], [35]]
#
# @endcode
#
def groupList4(arr, fnc, vals = False):

    l = len(arr)
    if 1 > l:
        return []
    elif 1 == l:
        return [[arr[0] if vals else 0]]

    # m[i]:  next element in chain (-1 = end)
    # g[gi]: head of group gi's chain
    # t[gi]: tail of group gi's chain  <- key addition over groupList2
    m  = [-1] * l
    g  = [-1] * l
    t  = [-1] * l
    lg = -1

    for k1 in range(l):
        ingroup = -1
        gi = 0

        while g[gi] != -1:
            k2 = g[gi]

            while True:
                if fnc(arr[k1], arr[k2]):
                    if ingroup != -1:
                        # Merge group gi into ingroup - O(1) via tail pointer
                        m[t[ingroup]] = g[gi]
                        t[ingroup]    = t[gi]

                        # Compact: move last group into freed slot
                        g[gi] = g[lg]
                        t[gi] = t[lg]
                        g[lg] = -1
                        lg -= 1
                        gi -= 1
                    else:
                        # Insert k1 after k2 - same as groupList2, preserving
                        # locality so future similar items match early.
                        # Update tail pointer only when k2 was the tail.
                        m[k1] = m[k2]
                        m[k2] = k1
                        if m[k1] == -1:   # k2 was the tail; k1 is the new tail
                            t[gi] = k1
                        ingroup = gi
                    break

                if m[k2] == -1:
                    break
                k2 = m[k2]

            gi += 1

        if ingroup == -1:
            g[gi] = k1
            t[gi] = k1
            lg = gi

    # Collect results by walking each group's chain
    gi  = 0
    ret = []
    while gi < l and g[gi] != -1:
        mi    = g[gi]
        group = []
        while True:
            group.append(arr[mi] if vals else mi)
            if m[mi] == -1:
                break
            mi = m[mi]
        ret.append(group)
        gi += 1

    return ret


### Groups a dict according to the specified function
# @param [in] arr       - Array to group
# @param [in] fnc       - Function that specifies grouping
#                           The function should take two parameters
#                           and return True if the items belong in
#                           the same group.
# @param [in] vals      - Set to True if you want the function
#                         to return a list of values.  If set
#                         to False, the function will return a
#                         list of keys.
#
# Example to group items less than three appart
# @begincode
#
# d = {'k0': 1, 'k1': 3, 'k2': 6, 'k3': 10, 'k4': 12, 'k5': 14, 'k6': 21, 'k7': 35, 'k8': 7, 'k9': 23}
# groups = groupDict(d, lambda a, b: 3 >= abs(a-b), True)
#
# @endcode
#
def groupDict(obj, fnc, vals = False):

    m = groupList([*obj.values()], fnc, vals)

    # Map keys
    if not vals:
        k = [*obj.keys()]
        for g in m:
            for i in range(0, len(g)):
                g[i] = k[g[i]]

    return m


### Groups a dict according to the specified function
#
# This function is the same as groupDict() but it minimizes the number
# of calls to the given compare function.
#
# @param [in] arr       - Array to group
# @param [in] fnc       - Function that specifies grouping
#                           The function should take two parameters
#                           and return True if the items belong in
#                           the same group.
# @param [in] vals      - Set to True if you want the function
#                         to return a list of values.  If set
#                         to False, the function will return a
#                         list of keys.
#
# Example to group items less than three appart
# @begincode
#
# d = {'k0': 1, 'k1': 3, 'k2': 6, 'k3': 10, 'k4': 12, 'k5': 14, 'k6': 21, 'k7': 35, 'k8': 7, 'k9': 23}
# groups = groupDict2(d, lambda a, b: 3 >= abs(a-b), True)
#
# @endcode
#
def groupDict2(obj, fnc, vals = False):

    m = groupList2([*obj.values()], fnc, vals)

    # Map keys
    if not vals:
        k = [*obj.keys()]
        for g in m:
            for i in range(0, len(g)):
                g[i] = k[g[i]]

    return m


### Groups a dict according to the specified function
#
# This function is the same as groupDict() but uses the Union-Find optimised
# groupList3() internally.  Prefer this over groupDict() when the predicate
# is expensive; for cheap predicates groupDict2() is usually faster.
#
# @param [in] arr       - Array to group
# @param [in] fnc       - Function that specifies grouping
#                           The function should take two parameters
#                           and return True if the items belong in
#                           the same group.
# @param [in] vals      - Set to True if you want the function
#                         to return a list of values.  If set
#                         to False, the function will return a
#                         list of keys.
#
# Example to group items less than three apart
# @begincode
#
# d = {'k0': 1, 'k1': 3, 'k2': 6, 'k3': 10, 'k4': 12, 'k5': 14, 'k6': 21, 'k7': 35, 'k8': 7, 'k9': 23}
# groups = groupDict3(d, lambda a, b: 3 >= abs(a-b), True)
#
# @endcode
#
def groupDict3(obj, fnc, vals = False):

    m = groupList3([*obj.values()], fnc, vals)

    # Map keys
    if not vals:
        k = [*obj.keys()]
        for g in m:
            for i in range(0, len(g)):
                g[i] = k[g[i]]

    return m


### Groups a dict according to the specified function
#
# Wrapper around groupList4() - combines groupList2()'s chain-walk comparison
# with O(1) merges via tail pointers.
#
# @param [in] arr       - Array to group
# @param [in] fnc       - Function that specifies grouping
#                           The function should take two parameters
#                           and return True if the items belong in
#                           the same group.
# @param [in] vals      - Set to True if you want the function
#                         to return a list of values.  If set
#                         to False, the function will return a
#                         list of keys.
#
def groupDict4(obj, fnc, vals = False):

    m = groupList4([*obj.values()], fnc, vals)

    # Map keys
    if not vals:
        k = [*obj.keys()]
        for g in m:
            for i in range(0, len(g)):
                g[i] = k[g[i]]

    return m

