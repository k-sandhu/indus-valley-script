"""Recover metadata after a successful review and local relative-path error.

This reads the retained result; it never invokes Claude or replaces its output.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
out = BASE / 'review' / 'claude-opus55-v1'
result = json.loads((out / 'cli-result.json').read_text(encoding='utf-8'))
packet = BASE / 'review' / 'claude-packet-v1.txt'
metadata = {
    'metadata_recovered_utc': datetime.now(timezone.utc).isoformat(),
    'started_utc': None,
    'finished_utc': None,
    'timing_note': 'Exact invocation timestamps were lost in the local post-processing exception; duration is retained by the CLI result.',
    'cli_version': '2.1.296 (Claude Code)',
    'requested_model': 'claude-opus-5-5',
    'model_usage': result.get('modelUsage'),
    'cli_reported_duration_ms': result.get('duration_ms'),
    'exit_code': None,
    'exit_code_note': 'Wrapper exited 1 after retaining successful JSON and review. The original subprocess return code was not persisted.',
    'is_error': result.get('is_error'),
    'terminal_reason': result.get('terminal_reason'),
    'subtype': result.get('subtype'),
    'packet_path': packet.relative_to(ROOT).as_posix(),
    'packet_sha256': hashlib.sha256(packet.read_bytes()).hexdigest(),
    'tools': 'Disabled: supplied authored packet only; no external source retrieval or code execution.',
    'authentication': 'Existing Claude subscription; external API-key variable omitted only from child environment after an earlier 401.',
    'local_repair': 'Path.relative_to failed on a relative argument after result and review writes. Runner now resolves paths before invocation; no review rerun.',
}
target = out / 'invocation.json'
if target.exists():
    raise FileExistsError(target)
target.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'review_success': result.get('subtype'), 'models': list(result.get('modelUsage', {})), 'metadata_path': str(target)}))
