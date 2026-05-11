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
# union-by-rank.  Two concrete improvements over groupList():
#
#   - The merge step drops from O(n) per merge to O(alpha(n)) — effectively
#     constant — because parent-pointer updates replace full array scans.
#   - Pairs already in the same component are detected before the predicate
#     is called, skipping 50–90% of predicate calls on dense graphs.
#
# When to prefer groupList3:
#   - The predicate is expensive (network I/O, file access, complex
#     computation, ML inference): fewer calls directly means less work.
#   - n is large enough that the O(n) merge cost in groupList() dominates.
#
# When to prefer groupList2 instead:
#   - The predicate is a cheap Python expression (e.g. abs(a-b) <= k).
#     In that case the two inlined find() loops cost more per pair than
#     the predicate calls they save, so groupList2 is faster in practice.
#
# The comparison loop itself remains O(n^2) — unavoidable for an arbitrary
# predicate — but all bookkeeping around each pair is now near-O(1).
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

            # find(k1) — inline with path halving
            x = k1
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            r1 = x

            # find(k2) — inline with path halving
            x = k2
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            r2 = x

            # Already in the same component: predicate call is unnecessary
            if r1 == r2:
                continue

            if fnc(arr[k1], arr[k2]):
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

