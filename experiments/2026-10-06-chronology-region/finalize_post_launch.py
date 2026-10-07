"""Record final preservation, source, prose and path checks without changing endpoints.

Run from the repository root with -B. Existing audit/inventory names are refused.
This script performs documentation and preservation checks, not new analyses.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWN = Path(__file__).resolve().parent
RAW = ROOT/'data/raw/2026-10-06-chronology-region'
for key in ['TMP','TEMP','MPLCONFIGDIR']: os.environ[key]=str(RAW/'tmp')


def read(path): return json.loads(path.read_text(encoding='utf-8'))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value): path.write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def relative(path): return path.relative_to(ROOT).as_posix()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='final-checks-post-launch-2026-10-07-v1.json')
    parser.add_argument('--inventory',default='FILES_POST_LAUNCH_2026-10-07.json')
    parser.add_argument('--verification',default='verification-post-launch-2026-10-07-v1.json')
    args=parser.parse_args()
    for name in [args.output,args.inventory,args.verification]:
        if Path(name).name!=name: raise ValueError('Use a single file name inside the owned directory.')
    output,inventory=OWN/args.output,OWN/args.inventory
    if output.exists() or inventory.exists(): raise FileExistsError('Existing audits and manifests are preserved.')
    baseline=read(OWN/'post-launch-document-baseline-2026-10-07-v1/preservation.json')['baseline_files']
    verification=read(OWN/args.verification)
    preserved,updated=[],[]
    for entry in baseline:
        path=ROOT/entry['path']
        current=digest(path)
        if entry['authorized_document_update']:
            assert current!=entry['sha256'],entry['path']
            snapshot=OWN/'post-launch-document-baseline-2026-10-07-v1'/path.name
            assert digest(snapshot)==entry['sha256']
            if path.suffix=='.md':
                old=snapshot.read_text(encoding='utf-8')
                retained=old.split('\n',1)[1] if path.name=='README.md' else old
                assert retained in path.read_text(encoding='utf-8'),path.name
            else:
                old,new=read(snapshot),read(path)
                assert set(new)=={'id','theme','status','question','outcome','challenge','remedy','evidence','retry_when'}
                for key in old:
                    if key=='evidence': assert new[key][:len(old[key])]==old[key]
                    else: assert new[key].startswith(old[key]),key
            updated.append({'path':entry['path'],'old_sha256':entry['sha256'],'new_sha256':current})
        else:
            assert current==entry['sha256'],entry['path']
            preserved.append(entry['path'])
    for entry in verification['immutable_assay_files']:
        assert digest(ROOT/entry['path'])==entry['sha256'],entry['path']
    assert digest(OWN/'verify_post_launch.py')==verification['code_sha256']
    source_manifest=read(OWN/'sources-post-launch.json')
    acquisition=read(RAW/'sources-post-launch-2026-10-07-v1/acquisition.json')
    by_id={x['id']:x for x in source_manifest['sources']}
    assert len(by_id)==len(source_manifest['sources'])
    source_checks=[]
    for source in acquisition['sources']:
        path=ROOT/source['path']
        assert digest(path)==source['sha256']==by_id[source['id']]['sha256']
        assert path.stat().st_size==source['bytes'] and source['http_status']==200
        source_checks.append({'id':source['id'],'path':source['path'],'sha256':source['sha256'],'bytes':source['bytes'],'pages':source['pages']})
    rendered=[]
    for path in sorted((RAW/'sources-post-launch-2026-10-07-v1').glob('*-page*.png')):
        source_id,page=path.stem.rsplit('-page',1)
        parent=next(x for x in acquisition['sources'] if x['id']==source_id)
        method='pdftoppm -scale-to 1800 -singlefile -png' if (source_id=='kenoyer2020' or page=='2') else 'pdftoppm -r 145 -singlefile -png'
        rendered.append({'path':relative(path),'sha256':digest(path),'parent_path':parent['path'],'parent_sha256':parent['sha256'],'physical_pdf_page':int(page),'method':method,'visually_inspected':True})
    linked=0
    future={output.resolve(),inventory.resolve()}
    for document in ['README.md','REPORT.md','RETROSPECTIVE.md','POST-LAUNCH-PROTOCOL-2026-10-07.md']:
        path=OWN/document
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#') or target.startswith('mailto:'): continue
            destination=(path.parent/target.split('#',1)[0]).resolve()
            assert destination.exists() or destination in future,(document,target)
            linked+=1
    for evidence in read(OWN/'registry-entry.json')['evidence']:
        path=(ROOT/evidence).resolve()
        assert path.exists() or path in future,evidence
    process=subprocess.run([sys.executable,'-B','tools/review_prose.py','--path',relative(OWN),'--no-write'],cwd=ROOT,text=True,encoding='utf-8',capture_output=True,check=True)
    prose=json.loads(process.stdout)
    assert prose['flags']==[],prose['flags']
    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    write(output,{'origin':'post-launch amendment','status':'Verified computation','generated_utc':timestamp,
        'immutable_prior_files':len(preserved),'authorized_prior_document_updates':updated,
        'immutable_new_assay_files':len(verification['immutable_assay_files']),'verification_script_hash_unchanged':True,
        'new_source_payloads_verified':source_checks,'rendered_source_derivatives':rendered,
        'local_markdown_links_checked':linked,'registry_field_schema_and_prior_evidence_preserved':True,
        'prose_review_no_write':prose,'code_sha256':digest(Path(__file__)),
        'scope':'Preservation and documentation checks. The scientific verification and remaining random-replay/archaeological limitations are in the linked verification record.',
        'scientific_verification':relative(OWN/args.verification)})
    baseline_by_path={x['path']:x for x in baseline}
    entries=[]
    for directory in [OWN,RAW]:
        for path in sorted(directory.rglob('*')):
            if not path.is_file(): continue
            name=relative(path)
            if name not in baseline_by_path: action='created'
            elif digest(path)!=baseline_by_path[name]['sha256']: action='changed'
            else: continue
            entries.append({'path':name,'action':action,'local_only':path.is_relative_to(RAW),'bytes':path.stat().st_size,'sha256':digest(path)})
    entries.append({'path':relative(inventory),'action':'created','local_only':False,'bytes':None,'sha256':None})
    entries.sort(key=lambda x:x['path'])
    write(inventory,{'package':'D1','origin':'post-launch amendment','generated_utc':timestamp,
        'owned_directory':relative(OWN),'local_raw_directory':relative(RAW),
        'write_scope':'Only the two assigned directories; four authorized documents updated; existing endpoints and source manifests preserved.',
        'self_reference':'Own bytes/hash are null to avoid recursive hashing.',
        'created_file_count':sum(x['action']=='created' for x in entries),'changed_file_count':sum(x['action']=='changed' for x in entries),
        'owned_created_file_count':sum(x['action']=='created' and not x['local_only'] for x in entries),
        'local_raw_created_file_count':sum(x['action']=='created' and x['local_only'] for x in entries),
        'created_directories':[relative(path) for path in [OWN/'post-launch-2026-10-07-v1',OWN/'post-launch-coverage-2026-10-07-v1',OWN/'post-launch-document-baseline-2026-10-07-v1',RAW/'post-launch-2026-10-07-v1',RAW/'sources-post-launch-2026-10-07-v1']],
        'files':entries})
    manifest=read(inventory)
    print(json.dumps({k:manifest[k] for k in ['created_file_count','changed_file_count','owned_created_file_count','local_raw_created_file_count']},indent=2))
    print(json.dumps({'immutable_prior_files':len(preserved),'new_assay_files':len(verification['immutable_assay_files']),'source_hashes':len(source_checks),'prose_flags':len(prose['flags']),'local_links':linked},indent=2))


if __name__=='__main__': main()
