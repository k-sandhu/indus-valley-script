"""Keep the eight-direction dispatch and claim records reproducible."""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
TRACKS = [
    (1, 'Q-1030', 3, 'Missing objects and identities', 'object-identity-extension', 'OBJECT-IDENTITY-EXTENSION-2026-10-24'),
    (2, 'Q-0027', 4, 'Inscription units and faces', 'unit-source-extension', 'UNIT-SOURCE-EXTENSION-2026-10-24'),
    (3, 'Q-0030', None, 'Harappa object contexts and chronology', 'harappa-context-extension', 'HARAPPA-CONTEXT-EXTENSION-2026-10-24'),
    (4, 'Q-0014', None, 'Matched seal and sealing die and motif evidence', 'office-seal-evidence', 'OFFICE-SEAL-EVIDENCE-2026-10-24'),
    (5, 'Q-0022', None, 'Numbered tablet deposit and use evidence', 'tablet-use-evidence', 'TABLET-USE-EVIDENCE-2026-10-24'),
    (6, 'Q-0039', 5, 'Source-backed lexical extraction repairs', 'lexical-extraction-extension', 'LEXICAL-EXTRACTION-EXTENSION-2026-10-24'),
    (7, 'Q-0037', None, 'Readable Akkadian and Tamil-Brahmi seal controls', 'readable-seal-controls', 'READABLE-SEAL-CONTROLS-2026-10-24'),
    (8, 'Q-1032', None, 'Town axes linked to building episodes', 'town-phase-links', 'TOWN-PHASE-LINKS-2026-10-24'),
]

def prepare():
    if (PACKAGE / 'dispatch-v1.json').exists():
        raise SystemExit('Initial dispatch already exists; preserve it and write a new version for status changes.')
    claims = PACKAGE / 'claims'
    claims.mkdir(exist_ok=True)
    rows = []
    for number, qid, issue, title, slug, attempt in TRACKS:
        package = f'experiments/2026-10-24-{slug}'
        body = (
            f'Claimed for the coordinated eight-direction continuation on 24 October 2026; expires 31 October 2026 unless updated.\n\n'
            f'Direction {number}: {title}. The worker model is gpt-6.1-sol in the Codex collaboration harness. '
            f'Each direction has its own package; the harness runs three workers concurrently and dispatches the remaining directions as slots open.\n\n'
            f'Owned package: `{package}/`. This first contribution closes a bounded source or implementation gap, preserves earlier results, '
            f'and records exact evidence, remaining cases and validation. No new confirmation cohort is opened in this source-work round. '
            f'Raw inputs and detailed derivatives remain local on D:. The shared knowledge index and existing question card remain unchanged pending integration.\n'
        )
        path = claims / f'{qid}.md'
        path.write_text(body, encoding='utf-8')
        rows.append(dict(direction=number, question=qid, issue=issue, title=title, package=package,
                         physical_raw=f'D:/projects/indus_valley_script/data/raw/2026-10-24-{slug}',
                         attempt=attempt, model='gpt-6.1-sol', status='running' if number <= 3 else 'queued',
                         claim_body=str(path.relative_to(ROOT)).replace('\\','/')))
    (PACKAGE / 'dispatch-v1.json').write_text(json.dumps(rows, indent=2)+'\n', encoding='utf-8')
    return rows

def claim(rows):
    output = PACKAGE / 'claim-results.json'
    if output.exists():
        raise SystemExit('Claim results already exist; inspect them before any retry.')
    results = []
    for row in rows:
        if row['issue']:
            command = ['gh','issue','comment',str(row['issue']),'--repo','k-sandhu/indus-valley-script','--body-file',row['claim_body']]
        else:
            command = ['gh','issue','create','--repo','k-sandhu/indus-valley-script','--title',f"{row['question']}: {row['title']}",'--body-file',row['claim_body']]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        results.append(dict(direction=row['direction'], question=row['question'], returncode=result.returncode,
                            output=result.stdout.strip(), error=result.stderr.strip()))
        output.write_text(json.dumps(results, indent=2)+'\n', encoding='utf-8')
        if result.returncode:
            raise SystemExit('Claim failed; partial results retained.')
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    import sys
    rows = prepare()
    if '--claim' in sys.argv:
        claim(rows)
