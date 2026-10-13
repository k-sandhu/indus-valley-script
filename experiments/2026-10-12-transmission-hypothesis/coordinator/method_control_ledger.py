"""Add method controls in successor ledgers, retaining the population-only ledgers."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
RAW=ROOT/'data/raw/2026-10-12-transmission-hypothesis/coordinator/method-v1'


def record(path):
    return {'path':path.relative_to(ROOT).as_posix(),'bytes':path.stat().st_size,
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'redistribution':'local-only'}


def main():
    outs=[HERE/'sources-v2.json',HERE/'observations-v2.json']
    if any(path.exists() for path in outs):raise SystemExit('Successor ledgers exist; no overwrite.')
    sources=json.loads((HERE/'sources.json').read_text('utf-8'))['sources']
    observations=json.loads((HERE/'observations.json').read_text('utf-8'))['observations']
    acquired=json.loads((RAW/'acquisition-v1.json').read_text('utf-8'))['records']
    derivatives=json.loads((RAW/'derivatives-v2.json').read_text('utf-8'))['derivatives']
    sources.extend([
      {'source_id':'C02','authors':['Aleksandr Diachenko','Ray John Rivers','Iwona Sobkowiak-Tabaka'],
       'year':2023,'title':'Convergent Evolution of Prehistoric Technologies: the Entropy and Diversity of Limited Solutions',
       'citation':'Journal of Archaeological Method and Theory 30:1168–1199. DOI 10.1007/s10816-023-09623-8.',
       'primary_url':acquired[0]['requested_url'],
       'reading_scope':'Publisher introduction and Research Hypothesis through connected-component examples; selected Method discussion of dependent joint variants; author/date metadata and rights notice. No kiln-data reanalysis or validation/adoption of its convergence metric or higher-order equations.',
       'loci':['Introduction','Research Hypothesis','Method, joint variants and dependence','Rights and permissions'],
       'witnesses':[acquired[0],record(RAW/'method-web-v1.json'),record(RAW/'method-controls-web-v1.json')],
       'derivatives':[derivatives[1]],'rights_status':'explicit-license','license':'CC BY 4.0',
       'rights_locus':'Publisher Rights and permissions, primary-web lines617–620 in method-controls-web-v1.json; third-party exclusions apply.',
       'redistribution':'local-only','role':'Methodological rival-control rationale, not South Asian archaeological evidence'},
      {'source_id':'C03','authors':['Stephen Shennan'],'year':2020,'title':'Style, Function and Cultural Transmission',
       'citation':'In H.S. Groucutt (ed.), Culture History and Convergent Evolution: Can We Detect Populations in Prehistory?, pp.291–298. DOI 10.1007/978-3-030-46126-3_15.',
       'primary_url':acquired[1]['requested_url'],'version':'Author accepted manuscript, identified by institutional metadata',
       'reading_scope':'Accepted-manuscript PDF pp.1,6,9,11,13–16 selected discussion and conclusion; metadata page identifies publication year, chapter and version. PDF pages are not final printed chapter page numbers.',
       'witnesses':[acquired[1],acquired[2],record(RAW/'shennan-metadata-web-v1.json')],
       'derivatives':[derivatives[0],derivatives[2]],'rights_status':'rights-unverified',
       'rights_observation':'Institutional metadata refers reuse to publisher terms; open access does not itself establish redistribution permission.',
       'redistribution':'local-only','role':'Direct predecessor for production-variable and functional-constraint controls, not a Harappan lineage'}
    ])
    observations.extend([
      {'observation_id':'C-O05','source_id':'C02','locus':'Publisher Research Hypothesis and Method, connected components and joint variants',
       'source_observation':'The authors argue that connected components constrain the range of technological choices and that component variants can be dependent.',
       'kind':'attributed methodological argument','inference_limit':'Several linked traits need a functional-constraint control; this study supplies no numerical Harappan convergence likelihood.'},
      {'observation_id':'C-O06','source_id':'C03','locus':'Accepted-manuscript PDF pp.6 and16, cultural evolution discussion and conclusion',
       'source_observation':'The chapter distinguishes learned production attributes from assemblage composition shaped by local use, preservation and time averaging.',
       'kind':'attributed archaeological method','inference_limit':'Similar inventories alone cannot supply a specific teaching lineage; the claim concerns assessed production variables.'},
      {'observation_id':'C-O07','source_id':'C03','locus':'Accepted-manuscript PDF pp.1,6 and9',
       'source_observation':'The chapter treats functional adaptation and transmitted traditions as interacting influences and discusses operational learning variables.',
       'kind':'attributed archaeological method','inference_limit':'A useful trait can be transmitted and an elaborate sequence can converge; neither category is fixed by appearance alone.'},
      {'observation_id':'C-O08','source_id':'C03','locus':'Accepted-manuscript PDF pp.11,13–14',
       'source_observation':'The chapter reports distinct pottery and ornament transmission patterns and considers demographic evidence alongside possible horizontal cultural transmission.',
       'kind':'attributed comparative synthesis','inference_limit':'These non-Indian examples justify separate component histories, not a measured Indian channel.'}
    ])
    for path,data in zip(outs,[{'scope':'Three coordinator primary controls, including direct method precedents. Population-control v1 remains preserved.','sources':sources},
                               {'scope':'Selected observations/attributed arguments; no new archaeological or genetic data.','observations':observations}]):
        with path.open('x',encoding='utf-8') as stream:json.dump(data,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'sources':len(sources),'observations':len(observations)}))


if __name__=='__main__':main()
