"""Binary reconstruction library. Test with python -I code/test_recon.py; no data CLI."""
from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import math
import common
import numpy as np
from scipy.optimize import minimize, minimize_scalar
from tree import nodes, leaves

LOW, HIGH = math.log(1e-6), math.log(1e3)

def transition(gain,loss,t):
    total=gain+loss
    pi=np.array([loss/total,gain/total])
    change=-math.expm1(-total*t)
    return np.array([[1-pi[1]*change,pi[1]*change],
                     [pi[0]*change,1-pi[0]*change]])

class Engine:
    """Topology compiled once; rates and lengths use the original tree unless scaled."""
    def __init__(self,root,trait,rescale=False):
        self.root=root; self.ns=list(nodes(root)); self.order=self.ns[::-1]
        self.trait=trait
        self.lengths={n:n.length/(root.age if rescale else 1) for n in self.ns}
        if root.age<=0: raise ValueError('Tree must have positive root height')
        unknown=set(trait)-{n.name for n in leaves(root)}
        if unknown: raise ValueError('Trait has unknown tips')
        if any(v not in (0,1,None) for v in trait.values()): raise ValueError('Invalid tip state')
        self.observed=sum(trait.get(n.name) is not None for n in leaves(root))

    def evaluate(self,gain,loss=None,prior='flat',marginals=True):
        loss=gain if loss is None else loss
        if gain<=0 or loss<=0: raise ValueError('Rates must be positive')
        p0=np.array([.5,.5]) if prior=='flat' else np.array([loss,gain])/(gain+loss)
        if prior not in ('flat','stationary'): raise ValueError('Unknown root prior')
        transitions={n:transition(gain,loss,self.lengths[n]) for n in self.ns if n is not self.root}
        down={}; message={}; logscale=0.0
        for n in self.order:
            if not n.children:
                state=self.trait.get(n.name)
                v=np.ones(2) if state is None else np.array([float(state==0),float(state==1)])
            else:
                v=np.ones(2)
                for c in n.children:
                    message[c]=transitions[c]@down[c]
                    v*=message[c]
            scale=float(v.max())
            if scale<=0: return (-math.inf,{}) if marginals else -math.inf
            down[n]=v/scale; logscale+=math.log(scale)
        ll=logscale+math.log(float(p0@down[self.root]))
        if not marginals: return ll
        up={self.root:p0}; probs={}
        for n in self.ns:
            v=up[n]*down[n]; probs[n.id]=float(v[1]/v.sum())
            for c in n.children:
                outside=up[n].copy()
                for sibling in n.children:
                    if sibling is not c: outside*=message[sibling]
                outside/=outside.max()
                u=outside@transitions[c]
                up[c]=u/u.max()
        return ll,probs

def likelihood(root,trait,gain,loss=None,prior='flat',rescale=False):
    return Engine(root,trait,rescale).evaluate(gain,loss,prior)

def parsimony(root,trait):
    ns=list(nodes(root)); down={}; up={root:np.zeros(2)}; cost=np.array([[0.,1.],[1.,0.]])
    for n in ns[::-1]:
        if not n.children:
            v=trait.get(n.name)
            down[n]=np.zeros(2) if v is None else np.array([0. if s==v else np.inf for s in (0,1)])
        else:
            down[n]=sum((np.min(cost+down[c][None,:],axis=1) for c in n.children),start=np.zeros(2))
    optimum=float(down[root].min()); sets={}; scores={}
    for n in ns:
        total=down[n]+up[n]
        allowed=[s for s in (0,1) if abs(total[s]-optimum)<1e-9]
        sets[n.id]=allowed; scores[n.id]=sum(allowed)/len(allowed)
        for c in n.children:
            v=up[n].copy()
            for sibling in n.children:
                if sibling is not c: v+=np.min(cost+down[sibling][None,:],axis=1)
            up[c]=np.min(v[:,None]+cost,axis=0)
    return dict(cost=optimum,sets=sets,scores=scores,
                fewer_than_two_observed=sum(v is not None for v in trait.values())<2)

def result(engine,gain,loss,prior,boundary,optimisation):
    ll,probs=engine.evaluate(gain,loss,prior)
    older=sorted((n for n in engine.ns if probs[n.id]>.5),key=lambda n:(-n.age,n.id))
    oldest=dict(node=older[0].id,age=older[0].age) if older else None
    return dict(gain=gain,loss=loss,q=gain if gain==loss else None,log_likelihood=ll,
                root_prior=prior,boundary=boundary,probabilities=probs,oldest_above_half=oldest,
                observed_tips=engine.observed,fewer_than_two_observed=engine.observed<2,
                optimisation=optimisation)

def mk1(root,trait):
    engine=Engine(root,trait,True)
    def objective(x): return -engine.evaluate(math.exp(float(x)),marginals=False)
    grid=np.linspace(LOW,HIGH,61); vals=np.array([objective(x) for x in grid]); j=int(vals.argmin())
    a=grid[max(j-1,0)]; b=grid[min(j+1,len(grid)-1)]
    fitted=minimize_scalar(objective,bounds=(a,b),method='bounded',options={'xatol':1e-11})
    options=[(float(vals[j]),float(grid[j])),(float(fitted.fun),float(fitted.x))]
    # Endpoint candidates preserve constant traits' bound solution.
    value,x=min(options,key=lambda pair:pair[0])
    boundary='lower' if x-LOW<1e-5 else ('upper' if HIGH-x<1e-5 else None)
    return result(engine,math.exp(x),math.exp(x),'flat',boundary,
                  dict(method='61 log-grid points and bounded refinement',success=bool(fitted.success)))

def mk2(root,trait,prior='flat'):
    engine=Engine(root,trait,True)
    def objective(x): return -engine.evaluate(math.exp(float(x[0])),math.exp(float(x[1])),prior,False)
    symmetric=mk1(root,trait)['gain']
    starts=[(math.log(symmetric),math.log(symmetric))]+[(x,y) for x in (-10.,-2.,4.) for y in (-10.,-2.,4.)]
    fits=[minimize(objective,x,method='L-BFGS-B',bounds=[(LOW,HIGH)]*2,
                   options={'ftol':1e-13,'gtol':1e-8,'maxiter':1000}) for x in starts]
    best=min(fits,key=lambda f:f.fun)
    gain,loss=np.exp(best.x)
    boundary={name:('lower' if x-LOW<1e-5 else ('upper' if HIGH-x<1e-5 else None))
              for name,x in zip(['gain','loss'],best.x)}
    return result(engine,float(gain),float(loss),prior,boundary,
                  dict(method='L-BFGS-B',starts=len(starts),success=bool(best.success),message=str(best.message)))

def simulate(root,rng,q,missing=.3,root_state=None):
    state=int(rng.random()<.5) if root_state is None else int(root_state)
    states={root:state}; trait={}
    for n in nodes(root):
        if n.parent is not None:
            p=transition(q,q,n.length/root.age)
            states[n]=int(rng.random()<p[states[n.parent],1])
        if not n.children: trait[n.name]=None if rng.random()<missing else states[n]
    return state,trait
