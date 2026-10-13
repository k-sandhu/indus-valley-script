"""Independently check ledger keys, pointers, reuse preservation and links."""
from pathlib import Path
import argparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SLP = {'ā':'A','ī':'I','ū':'U','ṛ':'f','ṝ':'F','ḷ':'x','ṅ':'N','ñ':'Y',
       'ṭ':'w','ḍ':'q','ṇ':'R','ś':'S','ṣ':'z','ṃ':'M','ṁ':'M','ḥ':'H'}
ASP = {'kh':'K','gh':'G','ch':'C','jh':'J','ṭh':'W','ḍh':'Q','th':'T',
       'dh':'D','ph':'P','bh':'B','ai':'E','au':'O'}


def slp(word):
    for a,b in ASP.items():
        word = word.replace(a,b)
    return ''.join(SLP.get(c,c) for c in word)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output',default='verification-independent.json')
    args = p.parse_args()
    output = HERE / args.output
    if output.exists():
        raise RuntimeError('Refusing to overwrite ' + str(output))
    source = ROOT/'data/raw/2026-10-08-bonta-review/acquisition-2026-10-08-v1/mw.txt'
    lines = source.read_text(encoding='utf-8').splitlines()
    ledger = json.loads((HERE/'senses.json').read_text(encoding='utf-8'))
    prior = json.loads((ROOT/'experiments/2026-10-11-bonta-adversarial/run-v6/sanskrit-senses.json').read_text(encoding='utf-8'))['rows']
    old = {r['word']:r for r in prior}
    families = json.loads((HERE/'family-links.json').read_text(encoding='utf-8'))['families']
    checks = []
    by = {r['word']:r for r in ledger['rows']}
    for r in ledger['rows']:
        match = re.search(r'#L(\d+)$',r['source_record_url'])
        assert match,r
        line = lines[int(match[1])-1]
        parsed = re.match(r'<L>(.*?)<pc>(.*?)<k1>(.*?)<k2>',line)
        assert parsed, (r,line)
        assert (parsed[1],parsed[2],parsed[3]) == (r['entry_id'],r['page_column'],r['slp1']), (r,line)
        assert slp(r['comparison_headword']) == r['slp1'],r
        assert r['dictionary_citations'] == re.findall(r'<ls(?: [^>]*)?>(.*?)</ls>', '\n'.join(lines[int(match[1]):next(i for i in range(int(match[1]),len(lines)) if lines[i]=='<LEND>')])),r
        if r['addition_status']=='reused-run-v6':
            for key,value in old[r['word']].items():
                assert r[key] == value, (r['word'],key)
        checks.append({'word':r['word'],'entry_id':r['entry_id'],'source_line_pointer':True,'comparison_headword_slp1':True,'citation_extraction':True})
    for key,r in families.items():
        assert r['sense_ids'] == [by[w]['sense_id'] for w in r['words']], key
        assert r['rivals'],key
    assert len(ledger['rows']) == 96
    assert sum(r['addition_status']=='new-selected-sense-2026-10-12' for r in ledger['rows']) == 40
    assert sum(r['addition_status']=='reused-run-v6' for r in ledger['rows']) == 56
    result={'status':'pass','rows':96,'new_senses':40,'reused_senses':56,'family_links':len(families),
            'checks':checks,'inputs':[{'path':q.relative_to(ROOT).as_posix(),'sha256':digest(q)} for q in [source,HERE/'senses.json',HERE/'family-links.json',Path(__file__).resolve()]],
            'scope':'Independent source-line parsing and transliteration code; all checks use the same pinned dictionary witness.'}
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['checks','inputs']},ensure_ascii=False))


if __name__ == '__main__':
    main()
