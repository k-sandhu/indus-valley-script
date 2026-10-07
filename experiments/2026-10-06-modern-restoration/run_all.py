"""Manual full reproduction. Choose a new run label to preserve endpoints."""
import argparse
import subprocess
import sys
from pathlib import Path

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True)
    parser.add_argument('--freeze', action='store_true', help='Create the single carry-forward record if it does not already exist.')
    args = parser.parse_args()
    for stage in ['checks', 'classical', 'neural', 'metadata', 'ensemble', 'curves']:
        subprocess.run([sys.executable, '-B', str(OWN / 'run.py'), '--run', args.run, '--stage', stage], cwd=ROOT, check=True)
    for is_curve, output in [(False, f'{args.run}-aggregate-results.json'), (True, f'{args.run}-learning-curves.json')]:
        command = [sys.executable, '-B', str(OWN / 'summarize.py'), '--run', args.run, '--output', output]
        if is_curve:
            command.append('--curves')
        subprocess.run(command, cwd=ROOT, check=True)
    subprocess.run([sys.executable, '-B', str(OWN / 'verify.py'), '--run', args.run, '--output', f'{args.run}-verification.json'], cwd=ROOT, check=True)
    if args.freeze:
        subprocess.run([sys.executable, '-B', str(OWN / 'run.py'), '--run', args.run, '--stage', 'freeze'], cwd=ROOT, check=True)

if __name__ == '__main__':
    main()
