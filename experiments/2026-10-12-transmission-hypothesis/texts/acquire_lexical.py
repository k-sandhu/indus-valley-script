"""Fetch bounded dictionary entries and preserve publisher search metadata."""
import concurrent.futures
import json
from pathlib import Path
from acquire_sources import RAW,HERE,capture,sha


def main():
    target=RAW/'capture-v4.json'
    if target.exists():raise FileExistsError(target)
    words=[('sira','sIra'),('taksh','takz'),('bhishaj','Bizaj'),('yava','yava'),('bija-postselection','bIja')]
    plan=[(f'mw1899-{ident}',f'https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2020/web/webtc/getword.php?key={key}&filter=roman&transLit=slp1') for ident,key in words]
    plan.append(('witzel-publisher-metadata','https://api.crossref.org/works?query.title=Substrate%20Languages%20in%20Old%20Indo-Aryan&rows=3'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(lambda item:capture(item,'v4'),plan))
    target.write_text(json.dumps(dict(script_sha256=sha(Path(__file__).read_bytes()),scope='Original lemma glosses; bīja explicitly post-selection; Crossref is publisher-deposited bibliographic metadata only',attempts=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    for r in rows:print(r['witness_id'],r.get('status_code'),r.get('format'),r.get('bytes'),r.get('error',''))


if __name__=='__main__':main()
