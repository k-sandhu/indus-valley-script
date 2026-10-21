"""Read trees and prepare sample: python -I code/tree.py [--burnin FRACTION]."""
from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import argparse
import gzip
import io
import json
import math
import re
import subprocess
import zipfile
import hashlib
from dataclasses import dataclass, field
from common import TIPS, GROUPS, LOCAL, DOWNLOADS, RUN, folded, sha, write
import numpy as np

@dataclass(eq=False)
class Node:
    name: str = ''
    length: float = 0.0
    children: list = field(default_factory=list)
    parent: object = field(default=None, repr=False)
    age: float = 0.0
    id: str = ''

def nodes(root):
    yield root
    for c in root.children:
        yield from nodes(c)

def leaves(root):
    return [n for n in nodes(root) if not n.children]

def initialise(root):
    counter = 0
    def visit(n):
        nonlocal counter
        for c in n.children:
            c.parent = n
            visit(c)
        n.id = n.name if not n.children else 'node'+str(counter)
        counter += 1
        n.age = max((c.age+c.length for c in n.children),default=0.0)
    visit(root)
    return root

def strip_annotations(text):
    out, depth = [], 0
    for ch in text:
        if ch=='[': depth += 1
        elif ch==']': depth -= 1
        elif depth==0: out.append(ch)
        if depth<0: raise ValueError('Unbalanced annotation')
    if depth: raise ValueError('Unclosed annotation')
    return ''.join(out)

def parse_newick(text, translate=None):
    if re.search(r'\[&U\]',text,re.I): raise ValueError('Unrooted tree supplied')
    tokens = re.findall(r"'(?:[^']|'')*'|[(),:;]|[^\s(),:;]+",strip_annotations(text))
    i = 0
    def rec():
        nonlocal i
        n = Node()
        if tokens[i]=='(':
            i += 1
            n.children.append(rec())
            while tokens[i]==',':
                i += 1
                n.children.append(rec())
            if tokens[i]!=')': raise ValueError('Expected closing parenthesis')
            i += 1
        if i<len(tokens) and tokens[i] not in [':',',',')',';']:
            n.name = tokens[i].strip("'").replace("''", "'")
            if translate and not n.children: n.name = translate.get(n.name,n.name)
            i += 1
        if i<len(tokens) and tokens[i]==':':
            n.length=float(tokens[i+1]); i += 2
            if not math.isfinite(n.length) or n.length<0: raise ValueError('Invalid branch length')
        return n
    root=rec()
    if i<len(tokens) and tokens[i]==';': i += 1
    if i!=len(tokens): raise ValueError('Trailing Newick tokens')
    root.length=0.0
    return initialise(root)

def nexus_translate(text):
    m=re.search(r'\btranslate\s+(.*?);',text,re.I|re.S)
    if not m: return {}
    out={}
    for part in m.group(1).split(','):
        k,v=part.strip().split(None,1)
        out[k]=v.strip().strip("'")
    return out

def nexus_lines(stream):
    # Tree records can span lines. No XML alignment is read here.
    header=''; pending=''; translate={}
    for line in stream:
            if not translate:
                header+=line
                translate=nexus_translate(header)
            if pending or re.match(r'\s*tree\s+',line,re.I):
                pending+=line
                if ';' in pending:
                    m=re.match(r'\s*tree\s+(\S+)\s*=\s*(.*?);',pending,re.I|re.S)
                    if not m: raise ValueError('Malformed NEXUS tree')
                    yield m.group(1),m.group(2)+';',translate
                    pending=''

def posterior_member(archive):
    candidates=[m for m in archive.namelist() if m.endswith('.trees') and '__MACOSX' not in m and not Path(m).name.startswith('._')]
    if len(candidates)!=1: raise ValueError('Expected one posterior tree member')
    return candidates[0]

def iter_nexus(path):
    if str(path).endswith('.zip'):
        with zipfile.ZipFile(path) as archive, archive.open(posterior_member(archive)) as raw, io.TextIOWrapper(raw,encoding='utf-8-sig') as stream:
            yield from nexus_lines(stream)
    else:
        with Path(path).open(encoding='utf-8-sig') as stream: yield from nexus_lines(stream)

def posterior_sha(path):
    if not str(path).endswith('.zip'): return sha(path)
    digest=hashlib.sha256()
    with zipfile.ZipFile(path) as archive, archive.open(posterior_member(archive)) as raw:
        for block in iter(lambda:raw.read(1024*1024),b''): digest.update(block)
    return digest.hexdigest()

def match_tips(root):
    def key(s): return re.sub('[^a-z]','',folded(s))
    aliases={key(t):t for t in TIPS}
    aliases.update({'badga':'Badaga'})
    seen={}
    for tip in leaves(root):
        original=tip.name
        k=key(original)
        if k not in aliases: raise ValueError('Unmatched tree label: '+original)
        tip.name=aliases[k]
        if tip.name in seen.values(): raise ValueError('Duplicate variety')
        seen[original]=tip.name
    if set(seen.values())!=set(TIPS): raise ValueError('Tree tip set mismatch')
    initialise(root)
    return seen

def mrca(root, names):
    wanted=set(names)
    if not wanted.issubset({t.name for t in leaves(root)}): raise ValueError('Missing MRCA tip')
    def rec(n):
        for c in n.children:
            if wanted.issubset({t.name for t in leaves(c)}): return rec(c)
        return n
    return rec(root)

def newick(n, lengths=True):
    text='('+','.join(newick(c,lengths) for c in n.children)+')' if n.children else "'"+n.name+"'"
    if lengths and n.parent is not None: text+=':'+format(n.length,'.16g')
    return text

def distances(root):
    out=[]
    def rec(n,d):
        if not n.children: out.append(d)
        for c in n.children: rec(c,d+c.length)
    rec(root,0)
    return out

def load_mcc():
    path=DOWNLOADS/'kolipakam2018/rsos171504_si_005.trees'
    _,text,tr=next(iter_nexus(path))
    root=parse_newick(text,tr)
    match_tips(root)
    return root

def random_yule(rng,n=20,names=None):
    root=Node(); active=[root]
    while len(active)<n:
        delta=float(rng.exponential(1/len(active)))
        for tip in active: tip.length+=delta
        tip=active.pop(int(rng.integers(len(active))))
        tip.children=[Node(),Node()]; active.extend(tip.children)
    delta=float(rng.exponential(1/n))
    for tip in active: tip.length+=delta
    for tip,name in zip(active,names or ['t'+str(i) for i in range(n)]): tip.name=name
    root.length=0
    return initialise(root)

def prepare(burnin=None):
    source=DOWNLOADS/'kolipakam2018/rsos171504_si_005.trees'
    _,nw,tr=next(iter_nexus(source)); root=parse_newick(nw,tr); mapping=match_tips(root)
    d=distances(root)
    result=dict(sha256=sha(source),tip_labels=mapping,ultrametric=max(d)-min(d)<1e-6*root.age,
                root_height=root.age,units='years before present, inferred from the article and protocol; NEXUS has no explicit unit declaration',
                topology=newick(root,False)+';',groups={})
    for group,tips in GROUPS.items():
        node=mrca(root,tips)
        result['groups'][group]=dict(age=node.age,node=node.id,monophyletic=set(tips)=={x.name for x in leaves(node)})
    write(LOCAL/'mcc.json',dict(newick=newick(root)+';',source_sha256=sha(source)))
    pdf=DOWNLOADS/'kolipakam2018/rsos171504_si_001.pdf'
    textfile=LOCAL/'supplement.txt'; textfile.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(['pdftotext','-enc','UTF-8','-layout',str(pdf),str(textfile)],check=True)
    text=textfile.read_text(encoding='utf-8')
    excerpts=[]
    for m in re.finditer(r'burn[ -]?in',text,re.I): excerpts.append(text[max(0,m.start()-180):m.end()+220])
    write(LOCAL/'burnin-evidence.json',dict(pdf_sha256=sha(pdf),excerpts=excerpts))
    # Explicit burn-in percentages override the default. Other statements require --burnin review.
    found=[]
    for excerpt in excerpts:
        found.extend(float(x)/100 for x in re.findall(r'(\d+(?:\.\d+)?)\s*%[^.\n]{0,90}burn[ -]?in',excerpt,re.I))
        found.extend(float(x)/100 for x in re.findall(r'burn[ -]?in[^.\n]{0,80}?(\d+(?:\.\d+)?)\s*%',excerpt,re.I))
    fraction=burnin if burnin is not None else (found[0] if found else .1)
    if not 0<=fraction<1: raise ValueError('Invalid burn-in fraction')
    xml=DOWNLOADS/'kolipakam2018/rsos171504_si_002.xml'
    # Only opening run/logger tags are inspected; alignment text is never parsed or emitted.
    logger=[]; chain=None
    with xml.open(encoding='utf-8') as stream:
        for line in stream:
            if '<run ' in line:
                m=re.search(r'chainLength="(\d+)"',line)
                if m: chain=int(m.group(1))
            if '<logger ' in line and '.trees' in line:
                m=re.search(r'logEvery="(\d+)"',line)
                if m: logger.append(int(m.group(1)))
    candidates=[p for p in (DOWNLOADS/'kolipakam2018-posterior').rglob('*.trees')
                if '__MACOSX' not in p.parts and not p.name.startswith('._')]
    if len(candidates)>1: raise ValueError('Expected one posterior tree file')
    posterior=candidates[0] if candidates else DOWNLOADS/'kolipakam2018/rsos171504_si_003.zip'
    count=sum(1 for _ in iter_nexus(posterior)); discard=int(count*fraction)
    if count-discard<1000: raise ValueError('Fewer than 1000 post-burn-in trees')
    indices=np.linspace(discard,count-1,1000,dtype=int); selected=set(indices.tolist())
    output=LOCAL/'posterior/sample.jsonl.gz'; output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('wb') as rawstream, gzip.GzipFile(filename='',fileobj=rawstream,mode='wb',mtime=0) as compressed, io.TextIOWrapper(compressed,encoding='utf-8',newline='\n') as stream:
        for i,(label,nw,tr) in enumerate(iter_nexus(posterior)):
            if i in selected:
                r=parse_newick(nw,tr); match_tips(r)
                stream.write(json.dumps(dict(index=i,state=label,newick=newick(r)+';'))+'\n')
    result['posterior']=dict(source_sha256=posterior_sha(posterior),source_container_sha256=sha(posterior),
                             storage='ZIP member' if str(posterior).endswith('.zip') else 'extracted file',total=count,burnin_fraction=fraction,discarded=discard,
                             post_burnin=count-discard,selected=1000,selection='linspace inclusive; integer floor',
                             burnin_decision='explicit command-line review' if burnin is not None else ('supplementary percentage' if found else 'protocol default 10%; no stated percentage found'),
                             burnin_mentions=len(excerpts),chain_length=chain,tree_log_every=logger,
                             sample_sha256=sha(output))
    write(RUN/'tree-summary.json',result)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--burnin',type=float)
    prepare(ap.parse_args().burnin)
