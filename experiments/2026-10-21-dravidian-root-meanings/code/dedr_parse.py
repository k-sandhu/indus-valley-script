"""Parse local HTML: python -I code/dedr_parse.py. Dictionary text is written only locally."""
from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from html.parser import HTMLParser
from html import unescape
from urllib.parse import urlparse, parse_qs
import re
import unicodedata
from common import LOCAL, RUN, ENTRY, write, sha

LANGUAGES = ['Ta.','Ma.','Ir.','PāKu.','PālKu.','ĀlKu.','AlKu.','Kurub.','Ko.','To.','Ka.','Koḍ.',
             'Tu.','Bel.','Kor.','Te.','Kol.','Nk.','Pa.','Ga.','Go.','Konḍa','Pe.','Manḍ.','Kui','Kuwi','Kur.','Malt.','Br.']
GRAMMAR = r'(?:n\.|adj\.|adv\.|vb\.|v\.i\.|v\.t\.|intr\.|tr\.|caus\.|pl\.|obl\.)'
DROP = re.compile(r'\b(?:DED(?:R|S)?|Turner|CDIAL)\b|[\d<=]')

class Page(HTMLParser):
    """Retain bold/italic runs within each dictionary span, with source order."""
    def __init__(self):
        super().__init__(convert_charrefs=True); self.stack=[]; self.blocks=[]; self.current=None
    def handle_starttag(self,tag,attrs):
        self.stack.append(tag)
        if tag=='span' and dict(attrs).get('class')=='new_p': self.current=[]
    def handle_endtag(self,tag):
        if tag=='span' and self.current is not None:
            self.blocks.append(self.current); self.current=None
        if tag in self.stack:
            j=len(self.stack)-1-self.stack[::-1].index(tag); self.stack=self.stack[:j]
    def handle_data(self,text):
        if self.current is None: return
        style='number' if 'number' in self.stack else ('italic_form' if 'i' in self.stack and 'b' in self.stack else ('italic' if 'i' in self.stack else ('form' if 'b' in self.stack else 'text')))
        if self.current and self.current[-1][0]==style: self.current[-1][1]+=text
        else: self.current.append([style,text])

def no_parentheses(text):
    out=[]; depth=0
    for c in text:
        if c=='(': depth+=1
        elif c==')': depth=max(0,depth-1)
        elif not depth: out.append(c)
    return ''.join(out)

def parenthesis_depth(text,depth=0):
    for c in text:
        if c=='(': depth+=1
        elif c==')': depth=max(0,depth-1)
    return depth

def parenthesis_end(text,depth):
    """Return the end of a parenthesised prefix, including nested parentheses."""
    for i,c in enumerate(text):
        if c=='(': depth+=1
        elif c==')': depth=max(0,depth-1)
        if depth==0: return i+1
    return len(text)

def normalise(text):
    s=unicodedata.normalize('NFC',text).lower().strip(' \t\n.;:')
    while re.match(r'^'+GRAMMAR+r'\s*',s): s=re.sub(r'^'+GRAMMAR+r'\s*','',s,count=1)
    s=re.sub(r'^(?:a|an|the|to)\s+','',s)
    return re.sub(r'\s+',' ',s).strip()

def head(segment):
    s=re.sub(r'^(?:(?:a|an|the)\s+)?(?:kind|sort|species|variety|type) of\s+','',segment)
    s=s.split(' of ',1)[0]
    words=re.findall(r"[^\W_]+(?:[-'][^\W_]+)*",s,re.UNICODE)
    h=words[-1] if words else ''
    return h[:-1] if len(h)>3 and h.endswith('s') and not h.endswith('ss') else h

def segments(gloss):
    out=[]
    for raw in re.split('[,;]',no_parentheses(gloss)):
        n=normalise(raw)
        direct_reference=bool(re.search(r'\b(?:DED(?:R|S)?|Turner|CDIAL)\b|[<=]',n,re.I))
        out.append(dict(text=raw.strip(),normalised=n,head=head(n),
                        reference_dropped='cross_reference' if DROP.search(n) else ('grammatical_or_empty' if not head(n) else None),
                        dropped='cross_reference' if direct_reference else ('grammatical_or_empty' if not head(n) else None)))
    return out

def tokenise(block):
    out=[]
    for style,text in block:
        if style=='number': continue
        s=unicodedata.normalize('NFC',text).strip()
        sub=re.match(r'^\(([a-z])\)\s*',s)
        if sub:
            out.append(('sub',sub.group(1))); text=text[text.index(')')+1:]; s=text.strip()
        if s in LANGUAGES:
            out.append(('language',s))
        elif style in {'form','italic','italic_form'} and any(s.startswith(label+' ') for label in LANGUAGES):
            label=next(label for label in LANGUAGES if s.startswith(label+' '))
            rest=s[len(label):]
            out.append(('language',label)); out.append(('text' if rest.lstrip().startswith('(') else 'form',rest))
        elif style=='italic_form' and out and out[-1][0]=='form' and out[-1][1].count('(')>out[-1][1].count(')'):
            out[-1]=('form',out[-1][1]+text)
        elif style=='form':
            grammatical=re.match(r'^\s*(\((?:masc\.|fem\.|neut\.|non-masc\.)[^()]*\)[;,.\s]*)',text)
            if grammatical:
                out.append(('text',grammatical.group(1)))
                text=text[grammatical.end():]
            # A bold run may be only punctuation after a nested language label.
            if text.strip():
                if out and out[-1][0]=='form': out[-1]=('form',out[-1][1]+text)
                else: out.append(('form',text))
        else: out.append(('text',text))
    # A malformed or broad italic run can include the end of a gloss and the
    # next language siglum. Read sigla outside parentheses within text runs.
    result=[]; depth=0
    labels=re.compile(r'(?<!\w)('+ '|'.join(re.escape(s) for s in sorted(LANGUAGES,key=len,reverse=True))+r')(?!\w)')
    for kind,text in out:
        if kind=='sub':
            result.append((kind,text)); continue
        # Markup inside parentheses carries context, never a new language or form.
        # Resume the original markup after the outer closing parenthesis.
        if depth:
            end=parenthesis_end(text,depth)
            result.append(('text',text[:end]))
            depth=parenthesis_depth(text[:end],depth); text=text[end:]
            if not text: continue
        while kind=='form' and text.lstrip().startswith('('):
            start=len(text)-len(text.lstrip())
            end=start+parenthesis_end(text[start:],0)
            result.append(('text',text[:end]))
            depth=parenthesis_depth(text[:end],depth); text=text[end:]
            if not text: break
        if not text: continue
        if kind=='text':
            start=0
            for match in labels.finditer(text):
                prefix=text[:match.start()]
                if parenthesis_depth(prefix,depth)>0: continue
                if match.start()>start: result.append(('text',text[start:match.start()]))
                result.append(('language',match.group(1))); start=match.end()
            if start<len(text): result.append(('text',text[start:]))
        else: result.append((kind,text))
        depth=parenthesis_depth(text,depth)
    return result

def split_forms(text):
    # Inflectional paradigms and optional letters stay attached to their citation form.
    parts=[]; start=0; depth=0
    for i,c in enumerate(text):
        if c=='(': depth+=1
        elif c==')': depth=max(0,depth-1)
        elif c in ',;' and not depth:
            parts.append(text[start:i]); start=i+1
    parts.append(text[start:])
    return [p.strip(' ,;.') for p in parts if re.search(r'[^\W\d_]',no_parentheses(p),re.UNICODE)]

def is_dialect_label(candidate):
    candidate=re.sub(r'\b(?:also|etc\.)\s*','',candidate).strip()
    return bool(re.fullmatch(r'(?:[A-ZĀḌṬ][A-Za-zĀāḌḍṬṭ]*\.?(?:[23])?\s*)+',candidate))

def dialect_glosses(raw):
    parts=[]; start=0; label=None
    for m in re.finditer(r'\(([^()]*)\)',raw):
        candidate=m.group(1).strip()
        if not is_dialect_label(candidate): continue
        if m.start()>start and raw[start:m.start()].strip(' ,;.'):
            parts.append((label,raw[start:m.start()]))
        label=candidate; start=m.end()
    parts.append((label,raw[start:]))
    return parts

def parse_entry(key,tokens):
    forms=[]; lines=[]; issues=[]; language=None; dialect=''; doubtful_line=False
    queue=[]; gloss=''; preceding=None; next_doubt=False; depth=0
    def finish():
        nonlocal queue,gloss,preceding,dialect,next_doubt
        if not queue: gloss=''; return
        raw=gloss.strip(' \n\t;,')
        raw=re.split(r'\bCf\.\s*\d|\bDED(?:R|S)?\s*[\d(]|\s/\s',raw)[0].strip(' ;,')
        for override,unit in dialect_glosses(raw):
            loan=bool(re.search(r'<(?!->)',unit))
            cleaned=no_parentheses(unit)
            inherited=False
            if not cleaned.strip(' .;,?'):
                inherited=True; cleaned=preceding or ''
                if preceding is None: issues.append(dict(kind='no_preceding_gloss',form_index=len(forms)))
            elif re.search(r'\bid\.(?=$|[\s,;])',cleaned):
                inherited=True
                if preceding is None: issues.append(dict(kind='id_without_preceding',form_index=len(forms)))
                cleaned=re.sub(r'\bid\.',preceding or '',cleaned)
            if cleaned.strip(): preceding=cleaned
            for original in queue:
                f=dict(original)
                if override is not None: f['dialect']=override
                f.update(index=len(forms),gloss=cleaned,raw_gloss=unit,inherited=inherited,
                         loan=f['loan'] or loan,segments=segments(cleaned))
                forms.append(f)
        queue=[]; gloss=''; next_doubt=False
    for kind,text in tokens:
        opening_depth=depth
        depth=parenthesis_depth(text,depth)
        if kind=='sub': continue
        if kind=='language':
            question=bool(re.search(r'\?\s*$',gloss))
            if question: gloss=re.sub(r'\?\s*$','',gloss)
            finish(); language=text; dialect=''; doubtful_line=question
            lines.append(dict(index=len(lines),label=language,parenthesis_depth=opening_depth))
            continue
        if language is None: continue
        if kind=='text':
            # A bold citation may close its parentheses in plain markup.
            # Keep that material on the form so citation numbers cannot become glosses.
            if queue and queue[-1]['form'].count('(')>queue[-1]['form'].count(')') and ')' in text:
                j=text.index(')')+1
                queue[-1]['form']+=text[:j]
                text=text[j:]
            # References and non-Dravidian comparison sections end the entry.
            stop=re.search(r'\bCf\.|\bDED(?:R|S)?\s*(?:\(|\d)|(?:^|\s)/\s',text)
            if stop:
                gloss+=text[:stop.start()]; finish(); break
            gloss+=text
            continue
        # Parentheses surrounding citations may contain bold forms. Keep them in gloss text.
        if gloss.count('(')>gloss.count(')'):
            gloss+=text; continue
        # A trailing label before a new form belongs to that form, not to the prior gloss.
        prefix=''
        m=re.search(r'(\([^()]*\)\s*)+[?\s]*$',gloss)
        if m:
            candidate=m.group(0)
            if all(is_dialect_label(p) for p in re.findall(r'\(([^()]*)\)',candidate)):
                prefix=candidate; gloss=gloss[:m.start()]
        doubt=bool(re.search(r'\?\s*$',gloss)) or '?' in prefix
        if doubt: gloss=re.sub(r'\?\s*$','',gloss)
        meaningful=no_parentheses(gloss).strip(' ,;:.?')
        if meaningful: finish()
        # No intervening gloss: all queued forms share the next gloss.
        if prefix: dialect=' '.join(re.findall(r'\(([^()]*)\)',prefix))
        loan=bool(re.search(r'<(?!->)',text+prefix))
        for value in split_forms(text):
            queue.append(dict(language=language,dialect=dialect,form=value,line_index=len(lines)-1,
                              doubtful=doubtful_line or doubt or value.startswith('?'),loan=loan))
        gloss=''
    finish()
    for f in forms:
        if f['form'].count('(')!=f['form'].count(')') or len(f['form'])>200:
            issues.append(dict(kind='malformed_form_markup',form_index=f['index'],line_index=f['line_index']))
    return dict(entry=key,language_lines=lines,forms=forms,issues=issues)

def read_pages(folder):
    entries={}; sources={}; last=None; current_sub=''; previous_page=None
    for path in sorted(Path(folder).glob('*.html')):
        page_number=int(re.search(r'(\d+)\.html$',path.name).group(1))
        if previous_page is not None and page_number!=previous_page+1: last=None; current_sub=''
        previous_page=page_number
        page=Page(); page.feed(path.read_text(encoding='utf-8'))
        for block in page.blocks:
            number=''.join(t for s,t in block if s=='number').strip()
            if number: last=number; current_sub=''
            if last is None: continue
            tokens=tokenise(block)
            sub=next((t for s,t in tokens if s=='sub'),'')
            if sub: current_sub=sub
            key=last+current_sub
            if not number and not sub and key in entries:
                entries[key].extend(tokens)
                sources[key].setdefault('continuations',[]).append(dict(path=str(path),sha256=sha(path)))
                continue
            # DSAL repeats complete entries on adjacent pages and within a page.
            if key not in entries or len(str(tokens))>len(str(entries[key])):
                entries[key]=tokens; sources[key]=dict(path=str(path),sha256=sha(path))
    return {key:dict(parse_entry(key,tokens),source=sources[key],headword=next((t.strip() for s,t in tokens if s=='form'),''))
            for key,tokens in entries.items()}

def main():
    from tips import map_form
    entries=read_pages(LOCAL/'dedr/pages')
    summary={}
    for key in sorted(set(ENTRY.values())):
        if key not in entries: raise ValueError('Missing entry '+key)
        entry=entries[key]
        for f in entry['forms']: f['tips']=map_form(f['language'],f['dialect'])[0]
        write(LOCAL/'parsed'/(key+'.json'),entry)
        fs=entry['forms']
        summary[key]=dict(language_lines=len(entry['language_lines']),forms=len(fs),
                          doubtful_forms=sum(f['doubtful'] for f in fs),loan_marked_forms=sum(f['loan'] for f in fs),
                          inherited_glosses=sum(f['inherited'] for f in fs),segments=sum(len(f['segments']) for f in fs),
                          tips_with_forms=len({t for f in fs for t in f['tips']}),
                          unread_issues=len(entry['issues']))
    searches=list((LOCAL/'dedr/s4').glob('search-*.html'))
    cards=[]
    for path in searches:
        html=path.read_text(encoding='utf-8')
        query=path.stem.removeprefix('search-')
        for hw,p in re.findall(r'\d+\)\s*<a href="([^"]*)"[^>]*>.*?burrow_query\.py\?page=(\d+)',html,re.S):
            cards.append(dict(query=query,headword=parse_qs(urlparse(unescape(hw)).query).get('qs',[''])[0],page=int(p)))
    s4=read_pages(LOCAL/'dedr/s4/pages')
    selected={}; unresolved=[]; recovered=[]; pagecache={}
    def compact(s): return re.sub(r'\s+',' ',unicodedata.normalize('NFC',s)).strip(' .')
    for card in cards:
        pagepath=LOCAL/'dedr/s4/pages'/f"page-{card['page']:05d}.html"
        if card['page'] not in pagecache: pagecache[card['page']]=read_pages_one(pagepath)
        local=pagecache[card['page']]
        matches=[k for k,v in local.items() if card['headword'] and (compact(v['headword'])==compact(card['headword']) or
                 (not card['headword'].endswith(')') and '(' in card['headword'] and compact(v['headword']).startswith(compact(card['headword']))))]
        if not matches:
            # Empty DSAL headword cards still identify a page and the queried definition.
            # Recover only entries on that page whose text contains the search term.
            matches=[k for k,v in local.items() if card['query'] in v['raw_text'].lower()]
            if matches: recovered.append(dict(card,entries=matches))
            else: unresolved.append(card)
        for key in matches:
            if key in s4: selected[key]=s4[key]
    for key,entry in selected.items():
        for f in entry['forms']: f['tips']=map_form(f['language'],f['dialect'])[0]
        write(LOCAL/'parsed/s4'/(key+'.json'),entry)
    write(LOCAL/'s4-result-resolution.json',dict(cards=cards,recovered=recovered,unresolved=unresolved))
    write(LOCAL/'s4-entries.json',sorted(selected))
    write(RUN/'parse-summary.json',dict(entries=summary,s4_entries=len(selected),s4_result_cards=len(cards),
                                      s4_recovered_cards=len(recovered),s4_ambiguous_recovered_cards=sum(len(r['entries'])>1 for r in recovered),
                                      s4_unresolved_cards=len(unresolved),s4_parse_issues={key:entry['issues'] for key,entry in selected.items() if entry['issues']}))

def read_pages_one(path):
    page=Page(); page.feed(path.read_text(encoding='utf-8'))
    last=None; entries={}
    for block in page.blocks:
        number=''.join(t for s,t in block if s=='number').strip()
        if number: last=number
        if not last: continue
        tokens=tokenise(block); sub=next((t for s,t in tokens if s=='sub'),'')
        entries[last+sub]=dict(parse_entry(last+sub,tokens),raw_text=''.join(t for s,t in tokens),headword=next((t.strip() for s,t in tokens if s=='form'),''))
    return entries

if __name__=='__main__': main()
