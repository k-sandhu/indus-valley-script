"""Complete current inventory and PDF phase delta, restricted to owned/raw roots."""
from pdf_followup import ROOT, OWN, RAW, read, write, sha

def main():
    baseline=read(OWN/'history/2026-10-09-before-pdf/baseline-files.json')
    old={r['path']:r['sha256'] for r in baseline}
    rows=[]
    for directory in [OWN,RAW]:
        for p in sorted(directory.rglob('*')):
            if not p.is_file() or p.name in ['FILES.json','PDF-FILES.json']:continue
            if '.git' in p.parts or '__pycache__' in p.parts:continue
            rel=p.relative_to(ROOT).as_posix();hash_value=sha(p)
            rows.append({'path':rel,'bytes':p.stat().st_size,'sha256':hash_value,
                'phase_action':'Created' if rel not in old else 'Preserved' if old[rel]==hash_value else 'Changed',
                'location':'local raw' if p.is_relative_to(RAW) else 'owned'})
    files={'date':'2026-10-09','inventory_exclusions':['FILES.json','PDF-FILES.json','__pycache__','.git'],
        'rights':'Third-party payloads and record-level derivatives are local raw only.',
        'files':rows}
    write(OWN/'FILES.json',files)
    delta=[r for r in rows if r['phase_action']!='Preserved']
    # The baseline captured the newly created extraction script before its revisions.
    for r in delta:
        if r['path']==(OWN/'pdf_followup.py').relative_to(ROOT).as_posix():
            r['phase_action']='Created';r['basis']='Created during this follow-up before baseline file census; subsequently revised.'
    delta += [{'path':(OWN/'FILES.json').relative_to(ROOT).as_posix(),'phase_action':'Changed',
        'sha256':sha(OWN/'FILES.json'),'location':'owned'},
        {'path':(OWN/'PDF-FILES.json').relative_to(ROOT).as_posix(),'phase_action':'Created',
        'location':'owned','sha256':None,'basis':'Self hash omitted'}]
    write(OWN/'PDF-FILES.json',{'date':'2026-10-09','baseline':'history/2026-10-09-before-pdf/baseline-files.json',
        'created_paths':sum(r['phase_action']=='Created' for r in delta),
        'changed_paths':sum(r['phase_action']=='Changed' for r in delta),
        'preserved_existing_files':sum(r['phase_action']=='Preserved' for r in rows),
        'files':delta})
    print({'current_inventory_files':len(rows),'created_paths':sum(r['phase_action']=='Created' for r in delta),
        'changed_paths':sum(r['phase_action']=='Changed' for r in delta)})

if __name__=='__main__':main()
