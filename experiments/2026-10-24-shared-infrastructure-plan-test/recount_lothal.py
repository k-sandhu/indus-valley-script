"""Independent visual recount of FT2005 Table 1; row transcription stays on D:."""
import collections
import argparse
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
R = Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main(tag):
    output=P/f'lothal-recount-{tag}.json'
    detail=R/f'review/lothal-independent-recount-{tag}.json'
    if output.exists() or detail.exists():raise FileExistsError('Preserve existing recount; use a new tag.')
    # Root read these category strings from both original rendered table pages.
    # Spaces separate rows; superscripts 1 and 2 remain separate provenance codes.
    a = ('W W W W W W W1 W1 W1 W W1 W1 W W W1 W1 W O W ? W2 O O W ? ? O ? W2 ? W2 ? ? W2 '
         'W W W W W W W W W W W W W').split()
    b = ('W W W O W W2 W2 ? W2 W2 ? ? ? ? ? W1 ? ? W W W1 W1 W W1 W1 W W1 W1 W1 W1 W1 W1 W2 '
         '? O W W O W2 O ? W2 ? ? O O').split()
    assert len(a) == 47 and len(b) == 46
    own = [{'CISI_id': f'L{i}', 'table1_provenance': v} for i, v in enumerate(a+b, 124)]
    original = R/'contexts/lothal-ft2005-table1-provenance-transcription-v1.json'
    submitted = json.loads(original.read_text(encoding='utf8'))['rows']
    differences = [x['CISI_id'] for x,y in zip(own,submitted)
                   if x['CISI_id'] != y['CISI_id'] or x['table1_provenance'] != y['table1_provenance']]
    detail.parent.mkdir(parents=True, exist_ok=True)
    detail.write_text(json.dumps({'method':'Independent root visual reading of original table crops, followed by comparison to module transcription.',
                                 'rows':own}, indent=2)+'\n', encoding='utf8')
    witnesses = [R/f'contexts/lot-row-table-{c}.png' for c in ('a','b')]
    result = {'reviewer':'Root agent, separate from original context coder; prior aggregate discrepancy was known.',
              'source':'Frenez and Tosi 2005, Table 1, printed pp.93–94, PDF indices30–31',
              'source_witnesses':[{'physical_path':str(x),'sha256':sha(x)} for x in witnesses],
              'row_count':len(own),'page_row_counts':[len(a),len(b)],
              'counts':dict(collections.Counter(a+b)),
              'submitted_transcription_sha256':sha(original),
              'independent_detail_path':str(detail),'independent_detail_sha256':sha(detail),
              'differences':differences,'passed':len(submitted)==93 and not differences,
              'interpretation':'Table labels W35/W1=18/W2=11/O10/?19 are independently reproduced. Prose O11/?17 is retained as a source conflict, not corrected silently.',
              'independence_limit':'Separate reader in the same collaboration, not external archaeological verification.'}
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'rows':len(own),'counts':result['counts'],'differences':differences,'passed':result['passed']}))

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--tag',default='v1')
    main(parser.parse_args().tag)
