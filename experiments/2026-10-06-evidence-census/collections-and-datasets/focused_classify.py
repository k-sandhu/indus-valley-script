"""Reclassify captured portal witnesses without changing the first extraction."""
import collections, json, re
from focused_fetch import RAW

def norm(value):
    return ''.join(str(int(x)) if x.isdigit() else x.upper() for x in re.findall(r'[A-Za-z]+|\d+', value))

def classify(row):
    f=row['fields']; desc=f.get('Brief Description',''); text=' '.join(f.values())
    # General copper-tablet background is not an observation of the particular object.
    if 'There are also several' in desc.replace('\n',' '):
        starts=list(re.finditer(r'This (?:rectangular copper|copper) tablet',desc,re.I))
        if starts: desc=desc[starts[-1].start():]
    if re.search(r'Brahmi|Persian language',desc,re.I) or row['record_identifier'].startswith('ngma_'):
        return 'other_period_or_script', 'Description identifies another script or a modern drawing'
    if not re.search(r'harapp|mohenjo|chanhu|lothal|indus|banawali|dholavira',text,re.I):
        return 'outside_query_topic','No Indus attribution in inspected fields'
    if re.search(r'plaster|replica|reproduc',f.get('Main Material','')+' '+desc,re.I):
        return 'modern_copy','Material or description identifies plaster or reproduction'
    if re.search(r'devoid of script|perhaps intended for script|inscribed\s*\?|possibly inscribed|writing\?',desc,re.I):
        return 'unconfirmed_inscription','Description denies or questions an inscription'
    if re.search(r'inscri|pictogra|script|character|graff|\bsigns\b',desc,re.I):
        return 'confirmed_description','Inscription, pictograph, character, sign or graffiti explicitly described'
    return 'unconfirmed_inscription','Inscription not established by the description'

def object_type(row):
    f=row['fields']; t=f.get('Title','')+' '+f.get('Brief Description','')
    if re.search(r'copper tablet|writing tablet',t,re.I):return 'tablet'
    if re.search(r'pot sherd|pot\s*\(disc\)|pottery|red pot sherd',t,re.I):return 'inscribed pottery'
    if re.search(r'sealing',f.get('Title','')+' '+f.get('Brief Description','')[:90],re.I):return 'sealing'
    if re.search(r'seal',t,re.I):return 'seal'
    return 'other inscribed object'

def run():
    rows=json.loads((RAW/'portal-record-review.json').read_text(encoding='utf8'))
    for r in rows:
        r['status'],r['decision_basis']=classify(r);r['object_type_review']=object_type(r)
        r['object_key']=r['fields'].get('Museum Name','')+'|'+norm(r['fields'].get('Accession Number',r['record_identifier']))
    (RAW/'portal-record-review-v2.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    groups=collections.defaultdict(list)
    for r in rows:groups[r['object_key']].append(r)
    priority=['confirmed_description','modern_copy','unconfirmed_inscription','other_period_or_script','outside_query_topic']
    unique=[]
    for key,items in sorted(groups.items()):
        best=min(items,key=lambda x:priority.index(x['status']))
        best=dict(best, duplicate_record_identifiers=[x['record_identifier'] for x in items], duplicate_page_count=len(items))
        unique.append(best)
    (RAW/'portal-unique-review.json').write_text(json.dumps(unique,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    for museum in sorted({r['fields'].get('Museum Name') for r in rows}):
        subset=[r for r in unique if r['fields'].get('Museum Name')==museum]
        print(museum,len(subset),dict(collections.Counter(r['status'] for r in subset)),dict(collections.Counter(r['object_type_review'] for r in subset if r['status']=='confirmed_description')))

if __name__=='__main__':run()
