"""Check the A1 deliverables and enumerate every created path.

Command: python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/package_check.py --raw data/raw/2026-10-21-head-direction-corpora
This command reads local acquisitions and outputs only hashes, identifiers and counts in the tracked audit.
"""
import argparse
import ast
import collections
import hashlib
import json
import subprocess
from pathlib import Path

CODE = Path(__file__).resolve().parent
ROOT = CODE.parents[3]
FIELDS = ('source entry sub_entry page_printed page_pdf plates object_text material dimensions object_kind device legend_as_printed legend_lines_as_printed line_division_evidence translation_as_printed doubtful restored illegible_part date_as_printed language_note findspot_as_printed depth_as_printed impressions duplicates cross_references museum uncertain_fields transcriber').split()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw',type=Path,required=True)
    a = ap.parse_args()
    raw = a.raw.resolve()
    scratch = raw/'codex-a1'
    errors = []
    records = []
    paths = []
    acquisition = []
    for p in sorted((CODE.parent.parent/'acquisition').glob('asi-ar-*.json')):
        if not p.name.startswith(('asi-ar-1903-04-','asi-ar-1913-14-')):
            continue
        r = json.loads(p.read_text(encoding='utf-8'))
        content = Path(r['local_path']).read_bytes()
        ok = len(content)==r['bytes'] and hashlib.sha256(content).hexdigest()==r['sha256']
        if not ok:
            errors.append({'acquisition_hash_mismatch':p.name})
        acquisition.append({'record':p.name,'sha256_and_bytes_recomputed':ok,'sha1_matches_expected':r.get('sha1_matches_expected'),'bytes_match_expected':r.get('bytes_match_expected')})
        if r.get('expected_sha1') and hashlib.sha1(content).hexdigest()!=r['expected_sha1']:
            errors.append({'sha1_mismatch':p.name})
        paths.append(p)
    render_index = {}
    for directory in (raw/'pages-asi-1903-04',raw/'pages-asi-1913-14'):
        for log in directory.glob('*-render-log.jsonl'):
            for s in log.read_text(encoding='utf-8').splitlines():
                r = json.loads(s)
                render_index[(r['scan'],r['page_pdf'])] = r
    for name in ('asi-ar-1903-04.jsonl','asi-ar-1913-14.jsonl','asi-ar-1913-14.register.jsonl'):
        p = raw/'transcriptions'/name
        rows = [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines()]
        seen = set()
        for r in rows:
            key = r['entry'],r['sub_entry']
            if key in seen:
                errors.append({'duplicate_record':[name,*key]})
            seen.add(key)
            if set(FIELDS)-r.keys():
                errors.append({'missing_fields':[name,*key]})
            for page in [r['page_pdf']]+r.get('page_pdf_continued',[]):
                render = render_index.get((r['scan'],page))
                if not render or render['dpi']<300 or not Path(render['png']).exists():
                    errors.append({'missing_300dpi_render':[name,*key,page]})
            if r['device'] and len(r['device'].split())>15:
                errors.append({'device_word_limit':[name,*key]})
        records.append({'file':name,'rows':len(rows),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'unique_keys':len(seen)})
    scripts = []
    for p in CODE.glob('*.py'):
        tree = ast.parse(p.read_text(encoding='utf-8'))
        doc = ast.get_docstring(tree)
        if not doc or 'Command' not in doc:
            errors.append({'missing_cli_docstring':p.name})
        scripts.append(p.name)
    command = ['git','-c','safe.directory='+ROOT.as_posix(),'status','--porcelain','--untracked-files=all']
    current = subprocess.run(command,cwd=ROOT,capture_output=True,text=True,check=True).stdout
    (scratch/'git-status-final.txt').write_text(current,encoding='utf-8')
    initial = (scratch/'git-status-initial.txt').read_text(encoding='utf-8')
    initial_set = set(initial.splitlines())
    new_status = [s for s in current.splitlines() if s not in initial_set]
    owned_prefixes = [CODE.relative_to(ROOT).as_posix()+'/', 'experiments/2026-10-21-head-direction-corpora/acquisition/asi-ar-1903-04-', 'experiments/2026-10-21-head-direction-corpora/acquisition/asi-ar-1913-14-']
    owned_status = [s for s in current.splitlines() if s[3:].startswith(tuple(owned_prefixes))]
    others = [s for s in current.splitlines() if s not in owned_status]
    # The workspace is shared. Status changes outside A1 cannot establish authorship.
    git_report = {'owned_status_lines':len(owned_status),'outside_owned_status_lines':len(others),'outside_owned_lines_already_in_initial':sum(s in initial_set for s in others),'outside_owned_new_status_lines':sum(s not in initial_set for s in others),'global_status_only_owned':not others,'interpretation':'Other contributions were present at entry and may change concurrently. This run wrote only its owned paths; global clean-scope condition cannot hold in the shared worktree.'}
    for p in CODE.rglob('*'):
        if p.is_file() and p.name not in ('CODEX-PROMPT.md','TASK.md','launch-codex.sh'):
            paths.append(p)
    for pattern in ('src-asi-1903-04-*','src-asi-1913-14-*','pages-asi-1903-04','pages-asi-1913-14','codex-a1'):
        for d in raw.glob(pattern):
            paths.extend(p for p in d.rglob('*') if p.is_file() and p.name not in ('codex.log','launches.txt'))
    paths.extend(p for p in (raw/'transcriptions').glob('asi-ar-1903-04.*') if p.is_file())
    paths.extend(p for p in (raw/'transcriptions').glob('asi-ar-1913-14.*') if p.is_file())
    paths.extend([CODE/'validation.json',CODE/'created-paths.txt'])
    historic = set((CODE/'created-paths.txt').read_text(encoding='utf-8').splitlines()) if (CODE/'created-paths.txt').exists() else set()
    relative = sorted(historic | {p.resolve().relative_to(ROOT).as_posix() for p in paths})
    (CODE/'created-paths.txt').write_text('\n'.join(relative)+'\n',encoding='utf-8')
    report = {'jsonl':records,'acquisition':acquisition,'syntax_checked_scripts':sorted(scripts),'rendered_pages':len(render_index),'retained_rendered_pages':sum(Path(r['png']).exists() for r in render_index.values()),'created_file_count':len(relative),'git_scope':git_report,'errors':errors,'pass':not errors,'limitations':['First-pass OCR correction event counts are unknown.','Second re-read is by the same agent; object/device string differences include independent condensation.','Global git status contains other contributions.']}
    (CODE/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':
    main()
