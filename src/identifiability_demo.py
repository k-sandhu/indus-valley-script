"""A label-symmetry witness, not an impossibility theorem for decipherment.

Unanchored statistical objectives assign likelihoods to graphic sequences.
Renaming their labels along with model parameters leaves these unchanged.
Archaeological/linguistic constraints external to this objective can break
the symmetry; this example does not assert that every reading is plausible.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from methods.conditional_structure import Model,load_records
from restoration import Restorer

ROOT=Path(__file__).resolve().parents[1]


def witness(rows):
    codes=sorted({s for r in rows for s in r['seq']})
    rename={code:f'UNANCHORED_LABEL_{len(codes)-i:04d}' for i,code in enumerate(codes)}
    renamed=[dict(r,seq=tuple(rename[s] for s in r['seq'])) for r in rows]
    original=Model(rows,20);alternate=Model(renamed,20)
    deviations=[]
    for a,b in zip(rows,renamed):
        sa,_=original.score(a);sb,_=alternate.score(b)
        deviations.extend(abs(x-y) for k in sa for x,y in zip(sa[k],sb[k]))
    first=rows[0];changed=renamed[0]
    ra=Restorer(rows,20).distribution(first,1,True)
    rb=Restorer(renamed,20).distribution(changed,1,True)
    restoration_difference=max(abs(ra[original.index[k]]-rb[alternate.index[rename[k]]]) for k in codes)
    return {'graphic_codes':len(codes),'texts':len(rows),
            'maximum_likelihood_difference_bits':max(deviations),
            'maximum_restoration_mass_difference':float(restoration_difference),
            'renaming_example':list(rename.items())[:8],
            'interpretation':'Likelihood and restoration cannot choose a sound or meaning from arbitrary unanchored labels.',
            'limit':'An externally fixed writing/language model, physical anchor, or independently tested semantic prediction may break this symmetry. It does not make decipherment impossible.'}


if __name__=='__main__':
    rows,_=load_records(ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl',unique=True)
    result=witness(rows)
    out=ROOT/'results/identifiability';out.mkdir(parents=True,exist_ok=True)
    (out/'label_symmetry.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
