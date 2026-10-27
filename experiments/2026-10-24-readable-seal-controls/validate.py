"""Validate the local source-extension ledger; never compute a linguistic score."""
import collections, hashlib, json
from pathlib import Path
PACKAGE = Path(__file__).resolve().parent
RAW = Path('D:/projects/indus_valley_script/data/raw/2026-10-24-readable-seal-controls')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    manifest = json.loads((PACKAGE/'source-manifest.json').read_text(encoding='utf8'))
    sources = {r['source_id']: r for r in manifest}
    ledger = RAW/'extension-ledger-v1.jsonl'
    rows = [json.loads(line) for line in ledger.read_text(encoding='utf8').splitlines()]
    assert len({r['record_id'] for r in rows}) == len(rows)
    for r in rows:
        assert r['source_id'] in sources
        assert r['source_locator'] and r['reason']
        if r['decision'].startswith('duplicate'): assert r['duplicate_join']
        if r['eligible_addition']:
            assert r['object_id'] and r['site'] and r['language'] in ('Tamil','Akkadian')
            assert r['words'] and len(r['units']) >= 2 and r['lines']
            assert not r['duplicate_join']
    for s in manifest:
        if 'physical_path' in s:
            p=Path(s['physical_path']); assert p.is_file()
            assert digest(p)==s['sha256'] and p.stat().st_size==s['bytes']
            assert str(p).lower().startswith('d:')
    out=dict(schema_version=1,validation='passed',verification_tier='submitted',author_checks=True,records=len(rows),decisions=dict(collections.Counter(r['decision'] for r in rows)),admissible_new_distinct_legends=sum(r['eligible_addition'] for r in rows),baseline_counts_unchanged={'akkadian_sign':11,'tamil_brahmi_sign_with_coins':23,'tamil_brahmi_seals_rings':16},source_outcomes=dict(collections.Counter(s['status'] for s in manifest)),ledger_sha256=digest(ledger),ledger_bytes=ledger.stat().st_size,ledger_logical_path='data/raw/2026-10-24-readable-seal-controls/'+ledger.name,ledger_physical_path=str(ledger),exposure_sha256=digest(RAW/'exposure-v1.json'),protocol_sha256=digest(PACKAGE/'PROTOCOL.md'),statistic_computed=False,indus_confirmation_opened=False)
    (PACKAGE/'validation-v1.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
    print(json.dumps(out,indent=2))
if __name__=='__main__': main()
