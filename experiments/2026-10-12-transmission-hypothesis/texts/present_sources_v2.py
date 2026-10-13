"""Separate standard rights status from observations; preserve source v1."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    target=HERE/'SOURCES-v2.json'
    if target.exists():raise FileExistsError(target)
    old=HERE/'SOURCES.json';d=json.loads(old.read_text('utf8'))
    for row in d['sources']:
        prior=row['rights_status']
        row['rights_status']='mixed-assets' if prior.startswith('mixed-assets') else 'rights-unverified' if prior.startswith('rights-unverified') else prior
        row['rights_observation']=prior
    d['sources'][0]['title']='Rgveda, Mandala 9; Rgveda, Mandala 10'
    d['metadata_amendment']=dict(prior_path=old.name,prior_sha256=sha(old),script_sha256=sha(Path(__file__)),
        change='Standardized rights_status values and separated descriptive notice; corrected title spacing. Witnesses, reading scopes, IDs and chronology unchanged.')
    target.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Source metadata v2 saved; original v1 retained')


if __name__=='__main__':main()
