"""Render standalone scientific figures from the saved follow-up aggregates."""
import argparse
import json
import os
import sys
from pathlib import Path

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[1]
RAW = ROOT / 'data/raw/2026-10-06-sign-context-and-seals'
sys.path.insert(0, str(RAW / 'plot-deps-2026-10-07'))
os.environ['MPLCONFIGDIR'] = str(RAW / 'tmp')
os.environ['TMP'] = str(RAW / 'tmp')
os.environ['TEMP'] = str(RAW / 'tmp')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def run():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default='post-launch-2026-10-07-02')
    ap.add_argument('--output', default='figures-post-launch-2026-10-07-02')
    args = ap.parse_args()
    dest, preview = OWN / args.output, RAW / args.output
    if dest.exists() or preview.exists():
        raise FileExistsError('Choose fresh figure directories.')
    dest.mkdir(); preview.mkdir()
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'svg.fonttype': 'none'})
    load = lambda name: json.loads((OWN / args.input / name).read_text(encoding='utf-8'))
    richness = load('richness.json')
    eligible = richness['comparison']['eligible_sites']
    sites = [s for s in richness['sites'] if s['site'] in eligible]
    fig, axs = plt.subplots(1, 3, figsize=(16, 5), layout='constrained')
    colours = plt.get_cmap('tab10')
    for i, site in enumerate(sites):
        for ax, key in zip(axs[:2], ['token_curve', 'object_curve']):
            points = site[key]['points']
            for extrapolated in [False, True]:
                select = [p for p in points if (p['sample_units'] >= site[key]['units'] if extrapolated
                                                else p['sample_units'] <= site[key]['units'])]
                ax.plot([p['sample_units'] for p in select], [p['expected_richness'] for p in select],
                        color=colours(i), linestyle='--' if extrapolated else '-',
                        label=site['site'] if not extrapolated and key == 'token_curve' else None)
        t = next(t for t in richness['comparison']['tests'] if t['site'] == site['site'])
        lo, hi = t['simultaneous_95_band']
        axs[2].plot([lo, hi], [i, i], color='0.7', lw=6, solid_capstyle='butt')
        axs[2].plot(t['reference_mean'], i, marker='|', color='black', markersize=12)
        axs[2].plot(site['observed_richness'], i, 'o', color=colours(i))
    for ax, key in zip(axs[:2], ['shared_token_curve', 'shared_object_curve']):
        points = richness[key]['points']
        ax.plot([p['sample_units'] for p in points], [p['expected_richness'] for p in points],
                color='black', lw=1.2, alpha=.6, label='Pooled curve' if key == 'shared_token_curve' else None)
        ax.set_xlim(0, max(s['token_curve' if key == 'shared_token_curve' else 'object_curve']['units'] for s in sites) * 2)
        ax.set_ylim(0, 750)
        ax.set_ylabel('Expected readable sign richness')
        ax.grid(alpha=.15)
    axs[0].set_xlabel('Readable tokens'); axs[0].set_title('Token rarefaction and extrapolation')
    axs[1].set_xlabel('Physical objects'); axs[1].set_title('Object-incidence curves')
    axs[2].set_yticks(range(len(sites)), [s['site'] for s in sites]); axs[2].invert_yaxis()
    axs[2].set_xlabel('Observed / reference sign richness')
    axs[2].set_title('Simultaneous 95% reference bands')
    axs[0].legend(fontsize=8, loc='lower right')
    fig.suptitle('Post-launch amendment: solid curves interpolate; dashed curves extrapolate to twice each sample')
    fig.savefig(dest / 'richness-curves.svg')
    fig.savefig(preview / 'richness-curves.png', dpi=130)
    plt.close(fig)
    terminal = load('terminal740.json')
    selected = [r for r in terminal['groups'] if r['included_in_context_correction']]
    fig, ax = plt.subplots(figsize=(10, 7), layout='constrained')
    for i, r in enumerate(selected):
        ci = r['excess_rate_component_bootstrap_95_ci']
        v = r['excess_ending_rate']
        ax.errorbar(100 * v, i, xerr=np.array([[100 * (v - ci[0])], [100 * (ci[1] - v)]]),
                    fmt='o', color='#226b91' if r['level'] == 'site' else '#a6502f', capsize=3)
    ax.set_yticks(range(len(selected)), [r['group'] + ' (n=' + str(r['objects']) + ')' for r in selected])
    ax.invert_yaxis(); ax.axvline(0, color='0.5', lw=1)
    ax.set_xlabel('Ending-text rate minus matched expectation, percentage points')
    ax.set_title('Post-launch amendment: terminal 740 enrichment\n95% whole-object bootstrap intervals, exact-type blocks')
    ax.grid(axis='x', alpha=.15)
    fig.savefig(dest / 'terminal740-excess.svg')
    fig.savefig(preview / 'terminal740-excess.png', dpi=130)
    plt.close(fig)
    (dest / 'figure-metadata.json').write_text(json.dumps({'status': 'Exploratory', 'stage': 'post-launch amendment',
        'input_directory': args.input, 'matplotlib_version': matplotlib.__version__,
        'scope': 'Figures render saved aggregates; pooled curves are descriptive and conditional site bands use type/length references.',
        'preview_directory_local': preview.relative_to(ROOT).as_posix()}, indent=2) + '\n', encoding='utf-8')
    print('Two SVG figures and local PNG previews rendered')


if __name__ == '__main__':
    run()
