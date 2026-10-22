"""SVG figures drawn only from saved outputs (project-authored)."""
import json

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import common as C
import roles as R

GRAY = '#8a8985'      # rearrangements of the same assignments
BLUE = '#2a78d6'      # the published assignment
AQUA = '#1baf7a'      # fitted assignments and bounds
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
FIG = C.HERE / 'figures'


def load(path):
    return json.loads((C.HERE / path).read_text(encoding='utf-8'))


def style(ax, xlabel):
    for side in ['top', 'right', 'left']:
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color(INK2)
    ax.tick_params(axis='x', colors=INK2, labelsize=8)
    ax.set_yticks([])
    ax.set_xlabel(xlabel, color=INK2, fontsize=8)
    ax.grid(axis='x', color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def strip(ax, draws, published, bound, title, xlabel, fitted=None, fitted_label=None, rng=None):
    rng = rng or np.random.default_rng(0)
    y = rng.uniform(-0.28, 0.28, len(draws))
    ax.scatter(draws, y, s=5, color=GRAY, alpha=0.45, linewidths=0, label='Rearranged within strata (1,000)',
               rasterized=True)
    ax.scatter([published], [0], s=70, color=BLUE, edgecolors='white', linewidths=1.5, zorder=3, label='Published')
    if fitted is not None:
        ax.scatter([fitted], [0], s=70, marker='s', color=AQUA, edgecolors='white', linewidths=1.5, zorder=3,
                   label=fitted_label)
    if bound is not None:
        ax.scatter([bound], [0], s=70, marker='D', color=AQUA, edgecolors='white', linewidths=1.5, zorder=3,
                   label='Best found under the same freedom')
    ax.set_ylim(-0.6, 0.6)
    ax.set_title(title, loc='left', fontsize=9, color=INK)
    style(ax, xlabel)


def role_figure():
    s = load('roles/summary.json')
    T = R.Tables()
    saved = np.load(C.LOCAL / 'roles/null-draws.npz')
    evs = [R.evaluate(T, lab, frames=('all', 'discovery', 'transfer', 'H2')) for lab in saved['labels']]
    t = next(x for x in s['transfer'] if x['fit_half'] == 'H1' and x['variant'].startswith('membership'))
    st = s['statistics']
    rows = [
        ('Families meeting the two-split rule (published 21 of 53)', [e['R1'] for e in evs], st['R1'], 'families', None),
        ('Member codes meeting the rule individually (published 62 of 539)', [e['R2'] for e in evs], st['R2'], 'codes', None),
        ('Total excess of matching tokens over expectation, all strings', [e['R3_all'] for e in evs], st['R3_all'], 'tokens', None),
        ('Strings whose every constrained token matches its role', [e['R5_compatible'] for e in evs], st['R5_compatible'], 'strings', None),
        ('Total excess on half H2: published map and a fit to half H1', [e['R3_H2'] for e in evs],
         {'published': t['published_map']['H2']['R3_published']['published'], 'bound': None}, 'tokens',
         t['H2']['R3_fit']['published']),
    ]
    fig, axes = plt.subplots(len(rows), 1, figsize=(7.2, 1.25 * len(rows) + 0.6))
    for ax, (title, draws, stat, xlabel, fitted) in zip(axes, rows):
        strip(ax, draws, stat['published'], stat.get('bound'), title, xlabel, fitted,
              'Fitted on H1 by exact assignment' if fitted is not None else None)
    handles, labels = [], []
    for ax in axes:
        for h, l in zip(*ax.get_legend_handles_labels()):
            if l not in labels:
                handles.append(h); labels.append(l)
    fig.legend(handles, labels, loc='lower center', ncol=2, frameon=False, fontsize=8)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / 'role-calibration.svg', dpi=200)
    plt.close(fig)


def lexical_figure():
    s = load('lexical/summary.json')
    draws = json.loads((C.LOCAL / 'lexical/null-draws.json').read_text(encoding='utf-8'))['draws']
    rows = [
        ('L1', 'nonempty_full_intersections_preferred', 'Codes with a nonempty full intersection, values rearranged (published 164)', 'codes'),
        ('L1', 'codes_with_repeated_exact_residual_both_scenarios', 'Codes with a repeated exact residual in both scenarios, values rearranged', 'codes'),
        ('L2', 'distinct_new_anchor_windows', 'Windows opened by the 17 new anchors, anchors moved to matched codes (published 256)', 'windows'),
        ('L2', 'nonempty_full_intersections_preferred', 'Codes with a nonempty full intersection, anchors moved to matched codes', 'codes'),
    ]
    fig, axes = plt.subplots(len(rows), 1, figsize=(7.2, 1.25 * len(rows) + 0.6))
    for ax, (kind, key, title, xlabel) in zip(axes, rows):
        vals = [d[key] for d in draws if d['kind'] == kind]
        stat = s['statistics'][kind][key]
        strip(ax, vals, stat['published'], stat.get('bound'), title, xlabel)
    handles, labels = [], []
    for ax in axes:
        for h, l in zip(*ax.get_legend_handles_labels()):
            if l not in labels:
                handles.append(h); labels.append(l)
    fig.legend(handles, labels, loc='lower center', ncol=2, frameon=False, fontsize=8)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(FIG / 'lexical-calibration.svg', dpi=200)
    plt.close(fig)


if __name__ == '__main__':
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'none'})
    role_figure()
    if (C.HERE / 'lexical/summary.json').exists():
        lexical_figure()
