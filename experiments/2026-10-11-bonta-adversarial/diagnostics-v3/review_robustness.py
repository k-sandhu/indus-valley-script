"""Apply the statistical review using saved permutations, without new draws."""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib, json
import numpy as np
from analyze import frame_stats

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

def main():
    out = HERE/'diagnostics-v3'
    if out.exists():
        raise SystemExit('Preserve existing diagnostic endpoints')
    source = ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl'
    saved_path = ROOT/'data/raw/2026-10-11-bonta-adversarial/run-v2/position-permutations.npz'
    prior = read(HERE/'run-v2/position-audit.json')
    by = {r['code']:r for r in prior['rows']}
    rows = [json.loads(line) for line in source.read_text(encoding='utf-8').splitlines()]
    unique = defaultdict(list)
    for r in rows:
        unique[tuple(r['signs_reading_rtl'])].append(r)
    saved = np.load(saved_path)
    codes = list(saved['codes'])
    ix = {s:i for i,s in enumerate(codes)}
    counts = saved['counts'].astype(float)
    _, observed, mean = frame_stats(unique, codes)
    variance = np.zeros_like(mean)
    for seq in unique:
        length = len(seq)
        if length < 2:
            continue
        for code, n in Counter(seq).items():
            p = n/length
            v = p*(1-p)
            variance[ix[code]] += [v, 2*(length-2)*v/(length-1), v]
    valid = variance > 0
    assert np.all(observed[~valid] == mean[~valid])
    sd = np.sqrt(variance)
    z = np.where(valid, (counts-mean)/np.maximum(sd,1e-9), -np.inf)
    new = [i for i,c in enumerate(codes) if not by[c]['inherited']]
    maxima = z[:,new,:].max(axis=(1,2))
    old_robust = read(HERE/'run-v2/robustness.json')
    selected = []
    for r in old_robust['selected']:
        c = r['code']; i = ix[c]; positions = {}
        for k,name in enumerate(['initial','medial','final']):
            value = float((observed[i,k]-mean[i,k])/sd[i,k]) if valid[i,k] else None
            positions[name] = dict(z=value, maxT_adjusted_p=float((1+(maxima>=value).sum())/(len(counts)+1)) if value is not None else None)
        selected.append(dict(code=c, positions=positions))
    robust = dict(position_maxT='Fixed analytic null means and variances standardize both observed and saved shuffled counts. The maximum uses all non-deterministic comparisons among the 596 previously new codes.',
        total_declared_comparisons=1788, active_comparisons=int(valid[new].sum()), deterministic_comparisons=int((~valid[new]).sum()),
        permutations=len(counts), new_random_draws=0, selected=selected, variant_contrasts=old_robust['variant_contrasts'],
        variant_scope='Unchanged descriptive contrasts copied from run-v2; not recomputed or upgraded.',
        prior='run-v2/robustness.json', code_sha256=sha(Path(__file__)))
    site_rows = []
    added = []
    for c in codes:
        containing = [(seq,rs) for seq,rs in unique.items() if c in seq]
        sites = sorted({r['site'] for _,rs in containing for r in rs})
        per_site = {}
        for site in sites:
            frame = {seq for seq,rs in containing if any(r['site']==site for r in rs)}
            total,pos,expected = frame_stats(frame,[c])
            per_site[site] = dict(tokens=int(total[0]), final=int(pos[0,2]), expected_final=round(float(expected[0,2]),3))
        previous = by[c]['site_final_sensitivity']
        assert all(per_site[s]==value for s,value in previous.items())
        missing = sorted(set(per_site)-set(previous))
        if missing:
            added.append(dict(code=c, sites=missing))
        site_rows.append(dict(code=c,site_final_sensitivity=per_site,added_sites=missing))
    assert len(added)==24 and sum(len(r['sites']) for r in added)==29
    assert robust['active_comparisons']==1388
    out.mkdir()
    write(out/'robustness.json', robust)
    write(out/'position-site-sensitivity.json',dict(scope='Each site includes every distinct string observed there. Shared strings can enter several site sensitivities; site counts need not sum to the pooled unique-text count.',
        correction='Enumerate sites from all containing faces, preserving the earlier representative-site-count field and pooled diagnostics.',
        affected_codes=24,added_code_site_summaries=29,added=added,rows=site_rows))
    write(out/'input-manifest.json',dict(status='Exploratory post-review correction',new_random_draws=0,
        inputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [source,saved_path,HERE/'run-v2/position-audit.json',HERE/'run-v2/robustness.json',Path(__file__),HERE/'analyze.py']],
        outputs=[dict(path=p.relative_to(out).as_posix(),sha256=sha(p)) for p in out.glob('*.json')]))
    (out/'review_robustness.py').write_bytes(Path(__file__).read_bytes())
    (out/'analyze.py').write_bytes((HERE/'analyze.py').read_bytes())
    print(json.dumps(dict(active_comparisons=robust['active_comparisons'],added_site_summaries=29,W142_medial_p=next(r for r in selected if r['code']=='142')['positions']['medial']['maxT_adjusted_p'])))

if __name__=='__main__':
    main()
