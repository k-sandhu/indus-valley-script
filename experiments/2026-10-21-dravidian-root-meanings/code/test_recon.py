"""Run synthetic tests and calibration: python -I code/test_recon.py [--simulations 500]."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse
import itertools
import math
import traceback
import platform
from common import RUN,LOCAL,TIPS,code_hashes,write
import numpy as np
import scipy
from scipy.stats import beta
from tree import parse_newick,random_yule,nodes,leaves,initialise,load_mcc,mrca,iter_nexus,match_tips,newick
from recon import likelihood,transition,parsimony,mk1,mk2,simulate
from dedr_parse import normalise,head,segments,Page,tokenise,parse_entry
import coding
import reference

SEED=20261021
TESTS=[]

def check(name,action):
    try:
        detail=action()
        TESTS.append(dict(name=name,passed=True,detail=detail))
    except Exception as exc:
        TESTS.append(dict(name=name,passed=False,error=str(exc),traceback=traceback.format_exc()))

def close(a,b,tol=1e-10):
    assert abs(a-b)<=tol,(a,b)

def brute(root,trait,gain,loss,prior):
    ns=list(nodes(root)); internal=[n for n in ns if n.children]
    pi=np.array([.5,.5]) if prior=='flat' else np.array([loss,gain])/(gain+loss)
    matrices={n:transition(gain,loss,n.length) for n in ns if n.parent}
    weights={n:0. for n in internal}; total=0.
    for assignment in itertools.product((0,1),repeat=len(internal)):
        states=dict(zip(internal,assignment)); weight=float(pi[states[root]])
        for node in ns[1:]:
            parent=states[node.parent]
            if node.children: weight*=matrices[node][parent,states[node]]
            elif trait.get(node.name) is not None: weight*=matrices[node][parent,trait[node.name]]
        total+=weight
        for node in internal: weights[node]+=weight*states[node]
    return math.log(total),{n.id:w/total for n,w in weights.items()}

def brute_parsimony(root,trait):
    ns=list(nodes(root)); unknown=[n for n in ns if n.children or trait.get(n.name) is None]
    fixed={n:trait[n.name] for n in leaves(root) if trait.get(n.name) is not None}
    best=math.inf; sets={n.id:set() for n in ns}
    for assignment in itertools.product((0,1),repeat=len(unknown)):
        states=dict(fixed); states.update(zip(unknown,assignment))
        cost=sum(states[n]!=states[n.parent] for n in ns if n.parent)
        if cost<best: best=cost; sets={n.id:set() for n in ns}
        if cost==best:
            for n in ns: sets[n.id].add(states[n])
    return best,{k:sorted(s) for k,s in sets.items()}

def enumerate_tests():
    rng=np.random.default_rng(SEED)
    for case in range(28):
        n=2+case%6; root=random_yule(rng,n)
        for node in nodes(root):
            if node.parent: node.length=float(rng.uniform(.01,2))
        initialise(root)
        trait={n.name:(None if rng.random()<.3 else int(rng.integers(2))) for n in leaves(root)}
        gain,loss=np.exp(rng.uniform(-4,2,2))
        for model,a,b in [('Mk1',gain,gain),('Mk2',gain,loss)]:
            for prior in ['flat','stationary']:
                def action(root=root,trait=trait,a=a,b=b,prior=prior):
                    exact,ep=brute(root,trait,a,b,prior); actual,ap=likelihood(root,trait,a,b,prior)
                    close(math.exp(exact),math.exp(actual)); close(exact,actual)
                    for k,p in ep.items(): close(p,ap[k])
                    return dict(tips=len(trait),internal_nodes=len(ep),tolerance=1e-10)
                check(f'enumeration {case} {model} {prior}',action)
        def action(root=root,trait=trait):
            score,sets=brute_parsimony(root,trait); actual=parsimony(root,trait)
            assert score==actual['cost']; assert sets==actual['sets']
        check(f'Sankoff enumeration {case}',action)

def closed_tests():
    root=parse_newick('(a:0.4,b:0.4);')
    def cherry():
        q=.7; _,p=likelihood(root,{'a':1,'b':1},q)
        matrix=transition(q,q,.4); expected=matrix[1,1]**2/(matrix[0,1]**2+matrix[1,1]**2)
        close(p[root.id],expected)
        assert parsimony(root,{'a':1,'b':1})['sets'][root.id]==[1]
    check('closed cherry',cherry)
    check('every tip missing',lambda:close(mk1(root,{'a':None,'b':None})['probabilities'][root.id],.5))
    def scale():
        original=parse_newick('((a:0.2,b:0.2):0.8,(c:0.6,d:0.6):0.4);')
        other=parse_newick('((a:2,b:2):8,(c:6,d:6):4);')
        trait={'a':1,'b':1,'c':0,'d':1}
        a=mk1(original,trait); b=mk1(other,trait)
        close(a['probabilities'][original.id],b['probabilities'][other.id])
        close(a['q'],b['q'])
    check('ML branch scale invariance',scale)
    check('few observations flag',lambda: (_ for _ in ()).throw(AssertionError()) if not mk1(root,{'a':1,'b':None})['fewer_than_two_observed'] else None)
    def bounds():
        r=mk1(root,{'a':1,'b':1}); assert r['boundary']=='lower'; assert r['probabilities'][root.id]>.999
    check('constant trait lower bound',bounds)
    def asymmetric():
        for prior in ['flat','stationary']:
            fit=mk2(root,{'a':0,'b':1},prior)
            assert 1e-6*(1-1e-12)<=fit['gain']<=1e3*(1+1e-12)
            ll,_=likelihood(root,{'a':0,'b':1},fit['gain']/root.age,fit['loss']/root.age,prior)
            close(ll,fit['log_likelihood'])
    check('Mk2 fitted model consistency',asymmetric)

def tree_tests():
    def nexus():
        path=LOCAL/'synthetic-guard/test.nex'; path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text("#NEXUS\nBegin trees;\nTranslate 1 'alpha tip', 2 beta, 3 gamma;\ntree STATE_0 = [&R] ((1[&height=0]:0.2,2:0.2)[&height=0.2]:0.8,3:1.0);\nEnd;\n",encoding='utf-8')
        _,text,tr=next(iter_nexus(path)); root=parse_newick(text,tr)
        assert {n.name for n in leaves(root)}=={'alpha tip','beta','gamma'}
        close(root.age,1.)
    check('NEXUS translation annotations and root height',nexus)
    def rooted():
        try: parse_newick('[&U] (a:1,b:1);')
        except ValueError: return
        raise AssertionError('Unrooted input accepted')
    check('unrooted input rejected',rooted)
    def mismatch():
        root=random_yule(np.random.default_rng(SEED+3),20,TIPS); leaves(root)[0].name='unmatched'
        try: match_tips(root)
        except ValueError: return
        raise AssertionError('Tip mismatch accepted')
    check('tree tip mismatch rejected',mismatch)
    def archive():
        import zipfile
        from acquire import extract
        path=LOCAL/'synthetic-guard/unsafe.zip'
        with zipfile.ZipFile(path,'w') as z: z.writestr('../outside','synthetic')
        try: extract(path,LOCAL/'synthetic-guard/unsafe-target')
        except ValueError: return
        raise AssertionError('Unsafe archive accepted')
    check('archive traversal rejected before extraction',archive)

def planted_tests():
    rng=np.random.default_rng(SEED+1)
    trees=[('MCC',load_mcc())]+[(f'Yule {i}',random_yule(rng,20)) for i in range(8)]
    for name,root in trees:
        cherry=min((n for n in nodes(root) if len(leaves(n))==2),key=lambda n:n.age)
        inside={n.name for n in leaves(cherry)}
        for polarity in [0,1]:
            def action(root=root,inside=inside,polarity=polarity):
                trait={n.name:(1-polarity if n.name in inside else polarity) for n in leaves(root)}
                p=mk1(root,trait)['probabilities'][root.id]
                assert p<.2 if polarity==0 else p>.8,p
                return dict(root_probability=p,planted_majority=polarity)
            check(f'planted {name} majority {polarity}',action)

def coding_tests():
    cases=[('STAR','pisces',False),('STAR','constellation of fish',False),('STAR','starfish',False),('STAR','star on a forehead',False),
           ('STAR','miniature star-shaped pebble',False),('STAR','star-anise',False),('STAR','north star',True),
           ('STAR','lunar mansion',True),('STAR','venus',True),('STAR','nakṣatra',True),
           ('STAR','naṭcattiram',True),('STAR','lightning',False),('STAR','stars',True),
           ('FISH','kind of fish',True),('FISH','fish-hook',False),('FISH','fisherman',False),('FISH','river fish',True),
           ('FISH','fish net',False),('SIX','six',True),('SIX','6',True),('SIX','sixth',False),('SIX','sixty',False),
           ('SEVEN','seven',True),('SEVEN','sevenfold',False),('THREE','3',True),('THREE','threefold',False),
           ('BANYAN','banyan',True),('BANYAN','ficus benghalensis',True),('BANYAN','f. indica',True),
           ('NORTH','northwards',True),('NORTH','northeastern',False),('EARRING','ear-ring',True),
           ('EARRING','ornament placed upon helix of ear',False),('EARRING','ring in ear',True),
           ('EARRING','bangle',True),('YOUTH','youthful',True),('YOUTH','young of woodland animals',True),
           ('SQUIRREL','forest squirrel',True),('CHILD','young of woodland animals',True),('CHILD','young ones',True),
           ('CHILD','daughter',True),('SPACE','open ground',True),('SPACE','gap',True),('SPACE','spacious',False),
           ('WHITE','whitish',True),('WHITE','whitewash',True),('VELGOD','kāma',True),('VELGOD','deity',True),
           ('VELGOD','skanda',True),('SPINDLE','spindle',True),('LIGHT','glow brightly',True),('LIGHT','ray',True),
           ('LIGHT','forked lightning fragment',False)]
    for i,(name,text,expected) in enumerate(cases):
        def action(name=name,text=text,expected=expected): assert bool(coding.CLASSES[name](text))==expected
        # Output only identifiers; original synthetic fixtures remain in code.
        check('coding '+name+' '+str(i),action)
    check('normalisation article grammar',lambda:close_string(normalise('adj. the star'),'star'))
    check('head kind and of rule',lambda:close_string(head('kind of blue fish of streams'),'fish'))
    check('parentheses before segmentation',lambda:close_string('|'.join(s['normalised'] for s in segments('a star (red, dim); to glow')),'star|glow'))
    def parse():
        html='<span class="new_p"><number>12</number><b><i>Ta.</i> zafa, zafi</b> a striped balloon; <b>zafu</b> id. <b><i>Ma.</i> zafe</b>. / Cf. Skt. <b>zafx</b> other.</span>'
        page=Page(); page.feed(html); e=parse_entry('12',tokenise(page.blocks[0]))
        assert len(e['forms'])==4,e
        assert all('balloon' in f['gloss'] for f in e['forms']),e
        assert sum(f['inherited'] for f in e['forms'])==2
    check('parser shared and inherited glosses',parse)
    def markup():
        html='<span class="new_p"><number>13</number><b><i>Ta.</i> zolo</b> striped balloon. <b><i>Go.</i></b> (Mu.) <b>zulu (<i>Voc.</i></b> 1234). ? <b><i>Ma.</i> zala</b> id.; <b>zili</b> (<i>&lt; Te.</i>) striped balloon. / Cf. Skt. tail.</span>'
        page=Page(); page.feed(html); e=parse_entry('13',tokenise(page.blocks[0])); fs=e['forms']
        assert len(fs)==4,e
        assert 'balloon' in fs[1]['gloss']; assert fs[1]['inherited']; assert fs[2]['doubtful']; assert fs[3]['loan']
        assert not e['issues']
    check('parser citation across markup and flags',markup)
    def dialect():
        html='<span class="new_p"><number>14</number><b><i>Go.</i> zalu</b> (Ma.) striped balloon, (Ko.) decorated balloon.</span>'
        page=Page(); page.feed(html); e=parse_entry('14',tokenise(page.blocks[0]))
        assert [f['dialect'] for f in e['forms']]==['Ma.','Ko.'],e
    check('parser dialect labels after a form',dialect)
    def embedded_language():
        html='<span class="new_p"><number>15</number><b><i>Ga.</i> zulo</b> three <i>(masc.). Go.</i> (Ko.) <b>zilu</b> three <i>(fem.). Konḍa</i> <b>zolu</b> three.</span>'
        page=Page(); page.feed(html); e=parse_entry('15',tokenise(page.blocks[0]))
        assert [line['label'] for line in e['language_lines']]==['Ga.','Go.','Konḍa'],e
        assert [f['language'] for f in e['forms']]==['Ga.','Go.','Konḍa'],e
    check('parser language embedded after grammatical text',embedded_language)
    def bold_grammar():
        html='<span class="new_p"><number>16</number><b><i>Ta.</i> zulo</b> checkered balloon <b>(masc.); zilu</b> id.</span>'
        page=Page(); page.feed(html); e=parse_entry('16',tokenise(page.blocks[0]))
        assert len(e['forms'])==2,e
        assert all('balloon' in f['gloss'] for f in e['forms']),e
    check('parser grammatical parentheses in bold',bold_grammar)
    def parenthetical_reference():
        html='<span class="new_p"><number>17</number><b><i>Ta.</i> zafa</b> striped balloon. <b><i>Br.</i> zafi</b> checkered balloon (cf. s.v. 4321 <b><i>Ta.</i> zafu</b> id. (see 4322 <i>Ma.</i> <b>zafe</b>)). <b><i>Go.</i></b> (Mu. <i>Ko.</i>) <b>zalo</b> striped balloon.</span>'
        page=Page(); page.feed(html); e=parse_entry('17',tokenise(page.blocks[0]))
        assert [line['label'] for line in e['language_lines']]==['Ta.','Br.','Go.'],e
        assert [f['language'] for f in e['forms']]==['Ta.','Br.','Go.'],e
        assert [f['form'] for f in e['forms']]==['zafa','zafi','zalo'],e
        assert e['forms'][2]['dialect']=='Mu. Ko.',e
        assert all(line['parenthesis_depth']==0 for line in e['language_lines']),e
        assert all('4321' not in f['gloss'] and '4322' not in f['gloss'] for f in e['forms']),e
        assert not e['issues'],e
    check('parser nested cross references and dialect sigla inside parentheses',parenthetical_reference)
    def parenthetical_form():
        html='<span class="new_p"><number>18</number><b><i>Ta.</i> zafa</b> striped balloon (<b>zafi</b>); <b>(see 4321 <i>Ma.</i> zafu) zafe</b> checkered balloon.</span>'
        page=Page(); page.feed(html); e=parse_entry('18',tokenise(page.blocks[0]))
        assert [f['form'] for f in e['forms']]==['zafa','zafe'],e
        assert [line['label'] for line in e['language_lines']]==['Ta.'],e
        assert all(line['parenthesis_depth']==0 for line in e['language_lines']),e
    check('parser parenthetical bold text cannot create a form',parenthetical_form)
    def parenthetical_series():
        html='<span class="new_p"><number>19</number><b><i>Ta.</i> zafa, (zafi), zafu</b> striped balloon.</span>'
        page=Page(); page.feed(html); e=parse_entry('19',tokenise(page.blocks[0]))
        assert [f['form'] for f in e['forms']]==['zafa','zafu'],e
        assert not e['issues'],e
    check('parser parenthetical member cannot create a citation form',parenthetical_series)
    def numeral():
        entry=dict(entry='12',forms=[dict(index=0,language='Ta.',dialect='',tips=['Tamil'],loan=False,doubtful=False,segments=segments('6'))])
        assert coding.code_entry(entry,coding.SIX)['tips']['Tamil']['state']==1
        assert reference.build_pool(entry,['SIX'])[0]=={}
    check('numeric segment coding and reference exclusion',numeral)
    check('S4 length and accent normalisation',lambda:close_string(coding.s4_normalise('mí·nː'),'min'))

def close_string(a,b): assert a==b,(a,b)

def reference_tests():
    def action():
        pools={'STAR':[.1,.8],'CHILD':[.2,.6,.9],'FISH':[.3,.7],'SPACE':[]}
        probabilities={'STAR':.9,'CHILD':.7,'FISH':.2,'SPACE':.1}
        result=reference.draw(probabilities,pools)
        exact=reference.exact_distribution([pools[m] for m in ['STAR','CHILD','FISH']])
        observed=result['all']['reference_distribution']
        for k,p in exact.items(): close(observed.get(str(k),0)/10000,p,.02)
        expected=sum(p for k,p in exact.items() if k>=2)
        close(result['all']['p_value'],expected,.02)
        assert result['excluded_empty_pools']==['SPACE']
        assert result==reference.draw(probabilities,pools)
        return dict(exact_distribution={str(k):v for k,v in exact.items()},draws=10000)
    check('reference exact enumeration and repeatability',action)
    def boundary():
        r=reference.draw({'STAR':.5},{'STAR':[.5,.5]})
        assert r['all']['T']==0; close(r['all']['p_value'],1)
        reference.draw({'STAR':.5},{'STAR':[]})
    check('reference strict threshold and empty pool',boundary)

def intervals(k,n):
    return [float(beta.ppf(.025,k,n-k+1)) if k else 0.,float(beta.ppf(.975,k+1,n-k)) if k<n else 1.]

def calibration(n):
    rng=np.random.default_rng(SEED+2); output={}
    for kind in ['MCC','Yule']:
        base=load_mcc() if kind=='MCC' else None
        storage={mode:[] for mode in ['known_q','estimated_q']}
        for i in range(n):
            root=base if base else random_yule(rng,20)
            q=float(np.exp(rng.uniform(math.log(.001),math.log(30))))
            truth,trait=simulate(root,rng,q,.3)
            _,known=likelihood(root,trait,q,rescale=True)
            estimated=mk1(root,trait)
            storage['known_q'].append((known[root.id],truth)); storage['estimated_q'].append((estimated['probabilities'][root.id],truth))
        output[kind]={}
        for mode,rows in storage.items():
            bins=[]
            for b in range(10):
                selected=[(p,s) for p,s in rows if min(9,int(p*10))==b]
                count=len(selected); k=sum(s for p,s in selected)
                bins.append(dict(bin=[b/10,(b+1)/10],count=count,root_ones=k,frequency=k/count if count else None,
                                 mean_prediction=sum(p for p,s in selected)/count if count else None,
                                 binomial_95=intervals(k,count) if count else None))
            output[kind][mode]=dict(n=n,correct_calls=sum((p>.5)==bool(s) for p,s in rows)/n,bins=bins)
    return dict(seed=SEED+2,q_range=[.001,30],missing_rate=.3,interval='Clopper-Pearson 95%',
                interpretation='Known-rate probabilities integrate the simulated state process. Estimated-rate bins measure plug-in calibration.',trees=output)

def main(n):
    enumerate_tests(); closed_tests(); tree_tests(); planted_tests(); coding_tests(); reference_tests()
    guard_tests()
    cal=calibration(n)
    check('calibration bin accounting',lambda:assert_bins(cal,n))
    result=dict(seed=SEED,synthetic_only=True,code_hashes=code_hashes(),tests=TESTS,
                test_count=len(TESTS),failures=sum(not t['passed'] for t in TESTS),
                coding_test_count=sum(t['name'].startswith(('coding','normalisation','head','parentheses','parser','S4')) for t in TESTS),
                calibration=cal,environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__))
    write(RUN/'selftest.json',result)
    print(str(len(TESTS))+' tests; '+str(result['failures'])+' failures')
    for t in TESTS:
        if not t['passed']: print(t['name']+': '+t['error'])
    if result['failures']: raise SystemExit(1)

def assert_bins(cal,n):
    for tree in cal['trees'].values():
        for mode in tree.values(): assert sum(b['count'] for b in mode['bins'])==n

def guard_tests():
    from compute import freeze_gate,synthetic
    def missing():
        try: freeze_gate(LOCAL/'nonexistent-freeze-test.json')
        except RuntimeError: return
        raise AssertionError('Missing freeze accepted')
    check('missing freeze rejected',missing)
    def mismatch():
        path=LOCAL/'synthetic-guard/freeze-fixture.json'
        write(path,dict(code_hashes={}))
        try: freeze_gate(path)
        except RuntimeError: return
        raise AssertionError('Mismatched freeze accepted')
    check('freeze mismatch rejected',mismatch)
    def identical():
        path=LOCAL/'synthetic-guard/freeze-fixture-valid.json'
        write(path,dict(code_hashes=code_hashes()))
        assert len(freeze_gate(path))==64
    check('matching freeze hashes accepted without computation',identical)
    def existing():
        path=LOCAL/'synthetic-guard'; path.mkdir(exist_ok=True)
        try: synthetic(path)
        except ValueError: return
        raise AssertionError('Existing directory accepted')
    check('existing output directory rejected',existing)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--simulations',type=int,default=500)
    main(ap.parse_args().simulations)
