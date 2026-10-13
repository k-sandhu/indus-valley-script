"""Inventory this run's owned outputs without altering another contributor's files."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'experiments/2026-10-12-repo-restructure'
RAW=ROOT/'data/raw/2026-10-12-repo-restructure'


def owned(name):
    exact={'AGENTS.md','CLAUDE.md','README.md','CONTRIBUTING.md','llms.txt','knowledge/INDEX.md',
           'knowledge/MAP.md','knowledge/TIMELINE.md','knowledge/experiments/registry.json',
           'knowledge/experiments/README.md','tools/kb.py','tools/register_experiment.py',
           'templates/FINDING.md','templates/QUESTION.md','templates/EXPERIMENT.md'}
    prefixes=('knowledge/registry/','knowledge/findings/','.claude/skills/','.github/ISSUE_TEMPLATE/',
              'experiments/2026-10-12-repo-restructure/','data/raw/2026-10-12-repo-restructure/')
    return name in exact or name.startswith(prefixes) or name.startswith('knowledge/questions/Q-0')


def reason(name):
    if name.startswith('knowledge/registry/attempts/'):return 'Preserve one original registry entry and add its reviewed classification and order.'
    if name.startswith('knowledge/findings/'):return 'Restate a measured result with checked numbers and exact evidence paths.'
    if name.startswith('knowledge/questions/Q-0'):return 'Add an actionable research or metadata task with scope and stopping rule.'
    if name.startswith('.claude/skills/'):return 'Route a contributor workflow to repository rules and evidence.'
    if name.startswith('.github/ISSUE_TEMPLATE/'):return 'Provide a structured issue form for parallel contribution.'
    if name.startswith('data/raw/'):return 'Preserve the local working-tree baseline for comparison.'
    if name.startswith('experiments/'):return 'Record restructuring methods, changes or verification for coordinator review.'
    if name.startswith('templates/'):return 'Provide card fields and contribution recording instructions.'
    if name.startswith('tools/'):return 'Implement or adapt collision-free knowledge-base maintenance.'
    return {'AGENTS.md':'Make one agent entry point while retaining every existing rule.',
            'CLAUDE.md':'Route Claude to the common agent entry point.',
            'README.md':'Provide human navigation and measured results linked to cards.',
            'CONTRIBUTING.md':'Retain contributor rules and add owned files, claims and verification tiers.',
            'llms.txt':'Provide a short machine-readable entry document.',
            'knowledge/INDEX.md':'Insert only the requested navigation and vocabulary paragraph.',
            'knowledge/MAP.md':'Generate the grouped inventory from cards and registry entry files.',
            'knowledge/TIMELINE.md':'Preserve all former README sections with adjusted relative links.',
            'knowledge/experiments/registry.json':'Regenerate original entries without changing original fields or order.',
            'knowledge/experiments/README.md':'Describe the per-entry source and superseded root reconstruction tool.',
            'knowledge/registry/metadata.json':'Preserve the original registry top-level schema and scope.',
            'knowledge/registry/STATUS-MAPPING.md':'Explain every original-status and primary-endpoint classification.',
            'knowledge/registry/VOCABULARY.md':'Define controlled card fields and copy the original status definitions.',
            'knowledge/registry/README.md':'Explain current per-entry registration and generation.'}.get(name,'Add repository navigation and contributor records.')


def main():
    baseline=json.loads((RAW/'baseline-hashes.json').read_text(encoding='utf-8'))
    baseline.update(json.loads((RAW/'baseline-untracked-hashes.json').read_text(encoding='utf-8')))
    paths=[]
    for name in ['AGENTS.md','CLAUDE.md','README.md','CONTRIBUTING.md','llms.txt','knowledge/INDEX.md',
                 'knowledge/MAP.md','knowledge/TIMELINE.md','knowledge/experiments/registry.json',
                 'knowledge/experiments/README.md','tools/kb.py','tools/register_experiment.py',
                 'templates/FINDING.md','templates/QUESTION.md','templates/EXPERIMENT.md']:
        if (ROOT/name).is_file():paths.append(ROOT/name)
    for pattern in ['knowledge/registry/**/*','knowledge/findings/*','knowledge/questions/Q-0*.md',
                    '.claude/skills/**/*','.github/ISSUE_TEMPLATE/**/*','experiments/2026-10-12-repo-restructure/*',
                    'data/raw/2026-10-12-repo-restructure/*']:
        paths.extend(p for p in ROOT.glob(pattern) if p.is_file() and '__pycache__' not in p.parts)
    rows=[]
    for path in sorted(set(paths)):
        name=path.relative_to(ROOT).as_posix()
        if name in ('experiments/2026-10-12-repo-restructure/CODEX-PROMPT.md','experiments/2026-10-12-repo-restructure/launch.sh'):
            continue
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if baseline.get(name)==digest:continue
        rows.append(dict(path=name,action='modified' if name in baseline else 'created',reason=reason(name)))
    (RUN/'CHANGES.json').write_text(json.dumps(dict(date='2026-10-12',paths=rows),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('CHANGES.json:',len(rows),'owned paths')


if __name__=='__main__':main()
