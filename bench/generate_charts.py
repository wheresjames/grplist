#!/usr/bin/env python3
"""
Generate performance comparison charts for the grplist README.

Requires: pip install matplotlib numpy

Usage:    python bench/generate_charts.py
Output:   bench/charts.png   (referenced by README.md)
          bench/charts.svg
"""

import sys
import os
import random
import timeit
import hashlib

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.colors import ListedColormap
    import numpy as np
except ImportError:
    sys.exit("Missing dependencies.  Run: pip install matplotlib numpy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grplist as gl

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

SEED      = 42
THRESHOLD = 3
CLOSE     = lambda a, b: abs(a - b) <= THRESHOLD

FUNCTIONS = {
    'groupList':  gl.groupList,
    'groupList2': gl.groupList2,
    'groupList3': gl.groupList3,
    'groupList4': gl.groupList4,
}
BG       = '#1E1E2E'   # dark blue-grey background
AX_BG    = '#252535'   # slightly lighter axes background
GRID_COL = '#3A3A5A'   # muted grid / spine colour
TEXT_COL = '#CDD6F4'   # soft white text

COLORS = {
    'groupList':  '#89B4FA',   # sky blue
    'groupList2': '#FAB387',   # peach/orange
    'groupList3': '#A6E3A1',   # green
    'groupList4': '#CBA6F7',   # lavender
}
FN_NAMES = list(FUNCTIONS.keys())


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make(n, spread):
    random.seed(SEED)
    return [random.randint(0, spread) for _ in range(n)]

def _connectivity(t):
    n = len(t)
    edges = sum(1 for i in range(n) for j in range(i+1, n) if CLOSE(t[i], t[j]))
    return 100.0 * edges / (n * (n - 1) // 2)

def _count_calls(fn, t):
    c = [0]
    fn(t, lambda a, b: (c.__setitem__(0, c[0] + 1), CLOSE(a, b))[1])
    return c[0]

def _walltime_ms(fn, t, pred, reps):
    return timeit.timeit(lambda: fn(t, pred, True), number=reps) / reps * 1000

def _make_pred(cost_level):
    """Return a predicate with increasing computational cost."""
    if cost_level == 0:
        return CLOSE
    if cost_level == 1:
        def pred(a, b):
            hashlib.md5(f"{a}{b}".encode()).digest()
            return abs(a - b) <= THRESHOLD
        return pred
    def pred(a, b):
        for _ in range(6):
            hashlib.sha256(f"{a}{b}".encode()).digest()
        return abs(a - b) <= THRESHOLD
    return pred


# ─────────────────────────────────────────────────────────────────────────────
# Panel 1 — predicate call counts across connectivity levels
# ─────────────────────────────────────────────────────────────────────────────

print("Panel 1: predicate call counts …")

N1       = 300
SPREADS1 = [4, 6, 8, 12, 18, 28, 45, 75, 130, 250, 500]
all_pairs = N1 * (N1 - 1) // 2

conn_x   = []
calls_pct = {k: [] for k in FN_NAMES}

for sp in SPREADS1:
    t = _make(N1, sp)
    conn_x.append(_connectivity(t))
    for name, fn in FUNCTIONS.items():
        calls_pct[name].append(100.0 * _count_calls(fn, t) / all_pairs)


# ─────────────────────────────────────────────────────────────────────────────
# Panel 2 — wall time for four representative scenarios
# ─────────────────────────────────────────────────────────────────────────────

print("Panel 2: scenario wall times …")

SCENARIOS = [
    # (x-label,         make-fn,                      cost, n,   reps)
    ('Cheap pred\nSparse',    lambda n: _make(n, n * 2),      0, 300, 40),
    ('Cheap pred\nDense',     lambda n: _make(n, max(n//6,4)), 0, 300, 40),
    ('Expensive pred\nSparse',lambda n: _make(n, n * 2),      2, 150, 8),
    ('Expensive pred\nDense', lambda n: _make(n, max(n//6,4)),2, 150, 8),
]

scenario_times = []
for label, make, cost, n_val, reps in SCENARIOS:
    t    = make(n_val)
    pred = _make_pred(cost)
    row  = {name: _walltime_ms(fn, t, pred, reps) for name, fn in FUNCTIONS.items()}
    scenario_times.append((label, row))


# ─────────────────────────────────────────────────────────────────────────────
# Panel 3 — winner heatmap: connectivity × predicate cost
# ─────────────────────────────────────────────────────────────────────────────

print("Panel 3: winner heatmap …")

N3 = 200
# Spreads chosen to yield roughly 5 %, 20 %, 45 %, 70 %, 90 %+ connectivity
HM_SPREADS = [250, 50, 18, 9, 4]
HM_COSTS   = [0, 1, 2]
COST_LABELS = ['Cheap\n(direct λ)', 'Medium\n(1× md5)', 'Expensive\n(6× sha256)']

conn_labels  = []
winner_grid  = np.zeros((len(HM_COSTS), len(HM_SPREADS)), dtype=int)
margin_grid  = np.zeros_like(winner_grid, dtype=float)

for ci, sp in enumerate(HM_SPREADS):
    t = _make(N3, sp)
    conn_labels.append(f'{_connectivity(t):.0f}%')
    for ri, cost in enumerate(HM_COSTS):
        pred = _make_pred(cost)
        reps = 6 if cost == 2 else 25
        times = {name: _walltime_ms(fn, t, pred, reps)
                 for name, fn in FUNCTIONS.items()}
        winner_name          = min(times, key=times.get)
        winner_grid[ri, ci]  = FN_NAMES.index(winner_name)
        second_best          = sorted(times.values())[1]
        margin_grid[ri, ci]  = (second_best - times[winner_name]) / second_best * 100


# ─────────────────────────────────────────────────────────────────────────────
# Draw
# ─────────────────────────────────────────────────────────────────────────────

print("Drawing …")

plt.rcParams.update({
    'font.family':         'sans-serif',
    'font.size':           10,
    'text.color':          TEXT_COL,
    'axes.labelcolor':     TEXT_COL,
    'xtick.color':         TEXT_COL,
    'ytick.color':         TEXT_COL,
    'axes.titlecolor':     TEXT_COL,
    'axes.facecolor':      AX_BG,
    'figure.facecolor':    BG,
    'axes.edgecolor':      GRID_COL,
    'axes.spines.top':     False,
    'axes.spines.right':   False,
    'axes.spines.left':    True,
    'axes.spines.bottom':  True,
    'grid.color':          GRID_COL,
    'legend.facecolor':    AX_BG,
    'legend.edgecolor':    GRID_COL,
    'legend.labelcolor':   TEXT_COL,
})

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(17, 5.2))
fig.suptitle('grplist — Performance Guide', fontsize=14, fontweight='bold',
             y=1.02, color=TEXT_COL)

# ── Panel 1 ──────────────────────────────────────────────────────────────────
# groupList2 and groupList4 make identical predicate calls; draw groupList4
# dashed so both are visible rather than one hiding the other.
DASH = {'groupList4': (4, 2)}

for name in FN_NAMES:
    dash   = DASH.get(name)
    kwargs = dict(marker='o', markersize=3.5, linewidth=2,
                  color=COLORS[name], label=name)
    if dash:
        kwargs['linestyle'] = (0, dash)
    ax1.plot(conn_x, calls_pct[name], **kwargs)

ax1.set_xlabel('Graph connectivity (%)')
ax1.set_ylabel('Predicate calls\n(% of all n·(n−1)/2 pairs)')
ax1.set_title('Predicate calls vs connectivity  (n=300)\ngroupList2 & groupList4 overlap')
ax1.legend(fontsize=8.5)
ax1.set_xlim(-2, 102)
ax1.set_ylim(-3, 108)
ax1.grid(True, alpha=0.4)

mid_idx = len(conn_x) // 2
ax1.annotate(
    'groupList / groupList3\ncheck every pair',
    xy=(conn_x[mid_idx], calls_pct['groupList'][mid_idx]),
    xytext=(30, 78),
    fontsize=8, color=COLORS['groupList'],
    arrowprops=dict(arrowstyle='->', color=COLORS['groupList'], lw=1.2),
)

# ── Panel 2 ──────────────────────────────────────────────────────────────────
n_fns = len(FN_NAMES)
width = 0.19
offsets = np.linspace(-(n_fns - 1) / 2, (n_fns - 1) / 2, n_fns) * width
x = np.arange(len(scenario_times))

for i, name in enumerate(FN_NAMES):
    vals = [row[name] for _, row in scenario_times]
    ax2.bar(x + offsets[i], vals, width,
            label=name, color=COLORS[name], alpha=0.90)

for si, (_, row) in enumerate(scenario_times):
    winner = min(row, key=row.get)
    wi     = FN_NAMES.index(winner)
    ax2.text(si + offsets[wi], row[winner] + max(row.values()) * 0.02,
             '★', ha='center', va='bottom', fontsize=10,
             color=COLORS[winner])

ax2.set_xticks(x)
ax2.set_xticklabels([s[0] for s in scenario_times], fontsize=8.5)
ax2.set_ylabel('Wall time (ms)')
ax2.set_title('Wall time by scenario\n★ = fastest')
ax2.legend(fontsize=8.5)
ax2.grid(True, alpha=0.4, axis='y')

# ── Panel 3 ──────────────────────────────────────────────────────────────────
cmap = ListedColormap([COLORS[n] for n in FN_NAMES])
ax3.imshow(winner_grid, cmap=cmap, vmin=-0.5, vmax=len(FN_NAMES) - 0.5,
           aspect='auto')

ax3.set_xticks(range(len(HM_SPREADS)))
ax3.set_xticklabels(conn_labels, fontsize=9)
ax3.set_yticks(range(len(HM_COSTS)))
ax3.set_yticklabels(COST_LABELS, fontsize=9)
ax3.set_xlabel('Graph connectivity  →  denser')
ax3.set_title('Fastest function\nby connectivity × predicate cost')

for ri in range(len(HM_COSTS)):
    for ci in range(len(HM_SPREADS)):
        name = FN_NAMES[winner_grid[ri, ci]]
        pct  = margin_grid[ri, ci]
        ax3.text(ci, ri,
                 f'{name}\n+{pct:.0f}% faster',
                 ha='center', va='center',
                 fontsize=7.5, color='white', fontweight='bold')

patches = [mpatches.Patch(color=COLORS[n], label=n) for n in FN_NAMES]
ax3.legend(handles=patches, fontsize=8,
           loc='upper center', bbox_to_anchor=(0.5, -0.18), ncol=3)

# ─────────────────────────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────────────────────────

plt.tight_layout()
out_dir = os.path.dirname(os.path.abspath(__file__))

for ext in ('png', 'svg'):
    path = os.path.join(out_dir, f'charts.{ext}')
    plt.savefig(path, bbox_inches='tight',
                dpi=150 if ext == 'png' else None)
    print(f'Saved {path}')
