"""One-off continuation of the active run; no scheduled or recurring work."""
import argparse
import subprocess
import sys
import time
from pathlib import Path

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[1]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run', default='main')
    args = p.parse_args()
    expected = [OWN / args.run / f'{family}-f{fold}-extra{extra}-selection.json'
        for family in ['gru', 'transformer'] for fold in range(5) for extra in [0, 1]]
    while not all(path.exists() for path in expected):
        time.sleep(5)
    def execute(script, *options):
        print('Starting', script, *options, flush=True)
        subprocess.run([sys.executable, '-B', str(OWN / script), *options], cwd=ROOT, check=True)
    for stage in ['metadata', 'ensemble', 'curves']:
        execute('run.py', '--run', args.run, '--stage', stage)
    execute('summarize.py', '--run', args.run, '--output', 'aggregate-results.json')
    execute('summarize.py', '--run', args.run, '--output', 'learning-curves.json', '--curves')
    execute('training_diagnostics.py', '--run', args.run)
    execute('verify.py', '--run', args.run)
    execute('run.py', '--run', args.run, '--stage', 'freeze')
    execute('frozen_register.py')
    print('Completed all fitting and computational checks.', flush=True)

if __name__ == '__main__':
    main()
