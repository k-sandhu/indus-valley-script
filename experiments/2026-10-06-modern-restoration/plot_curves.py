"""Render the declared accuracy curves from saved aggregate numbers."""
import argparse
import json
import platform
from data import OWN, save, digest
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='learning-curves.json')
    parser.add_argument('--prefix', default='learning-curves')
    args = parser.parse_args()
    source = OWN / args.input
    curves = json.loads(source.read_text(encoding='utf-8'))
    directory = OWN / 'figures'
    directory.mkdir(exist_ok=True)
    paths = [directory / f'{args.prefix}.{suffix}' for suffix in ['png', 'svg']]
    for path in paths:
        if path.exists():
            raise FileExistsError(path)
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False,
        'axes.spines.right': False, 'svg.fonttype': 'none'})
    fig, ax = plt.subplots(figsize=(9, 5.5), layout='constrained')
    fractions = [25, 50, 75, 100]
    for family, color, label in [('classical', '#176B91', 'MKN'),
            ('neural', '#AA4E00', 'Selected neural')]:
        for extra in [0, 1]:
            accuracy = [100 * curves['models'][f'{family}/extra{extra}/p{f}']['summary']['top1']
                for f in fractions]
            ax.plot(fractions, accuracy, color=color,
                linestyle='--' if extra else '-', marker='s' if extra else 'o',
                linewidth=2, label=label + (' + extra text' if extra else ''))
    for comparator, style in [('Markov1', ':'), ('Markov2', '-.')]:
        value = 100 * curves['comparators'][comparator]['top1']
        ax.axhline(value, color='#626262', linestyle=style, linewidth=1,
            label=f'Saved {comparator}: {value:.2f}%')
    ax.set(xticks=fractions, xlabel='Fraction of outer-training components (%)',
        ylabel='Exact top-one accuracy (%)',
        title='Restoration accuracy as training data grows')
    ax.grid(axis='y', alpha=.18)
    ax.legend(loc='center left', bbox_to_anchor=(1.01, .5), frameon=False, fontsize=9)
    fig.supxlabel('Exploratory, reused 8,009 masks; fixed selected configurations and neural epochs', fontsize=9)
    for path in paths:
        fig.savefig(path, dpi=180)
    plt.close(fig)
    save(directory / f'{args.prefix}-environment.json', {
        'python': platform.python_version(), 'matplotlib': matplotlib.__version__,
        'numpy': np.__version__, 'aggregate_source': args.input,
        'aggregate_sha256': digest(source),
        'files': [{'name': path.name, 'sha256': digest(path)} for path in paths],
    })
    print(json.dumps({'figures': [str(path.relative_to(OWN)) for path in paths]}))


if __name__ == '__main__':
    main()
