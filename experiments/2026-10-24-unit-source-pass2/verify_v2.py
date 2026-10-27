from pathlib import Path
import json,hashlib,fitz
P=Path('experiments/2026-10-24-unit-source-pass2');R=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-unit-source-pass2')
m=json.load(open(P/'SOURCE-MANIFEST-v2.json'));r=json.load(open(P/'results-v2.json'));a=json.load(open(R/'target-dispositions-v1.json'))
checks={'logical_paths_relative':all(not x['logical_path'].startswith('D:') for x in m['local_derivatives']),'seven_unique_targets':len(a)==len({x['face_id'] for x in a})==7,'five_HARP':sum(x['face_id'] not in ['LIPI:126.1','LIPI:130.1'] for x in a)==5,'none_admitted':not any(x['crop_recovered'] for x in a),'queue_conserved':r['missing_divided_faces_before']==r['missing_divided_faces_after']==42,'protocol_hash':hashlib.sha256((P/'PROTOCOL.md').read_bytes()).hexdigest()==r['protocol_sha256'],'all_raw_artifacts_D':all(x['physical_path'].startswith('D:') for x in m['local_derivatives']),'all_hashes':all(Path(x['physical_path']).stat().st_size==x['bytes'] and hashlib.sha256(Path(x['physical_path']).read_bytes()).hexdigest()==x['sha256'] for x in m['inputs']+m['local_derivatives']),'candidate_not_supported_bridge':r['primary_candidate_panels']==1 and r['supported_new_face_bridges']==0,'no_confirmation':r['confirmation_reads']==0}
for name,w,h in [('20781-entry-candidate.png',1545,411),('20781-context-candidate-v3.png',2304,93)]:
 pix=fitz.Pixmap(R/name);checks[name+'-dimensions']=pix.width==w and pix.height==h
out={'validation':'author source and accounting checks','checks':checks,'all_pass':all(checks.values())}
with (P/'verification-v2.json').open('x') as f:json.dump(out,f,indent=2)
print(out)
assert out['all_pass']
