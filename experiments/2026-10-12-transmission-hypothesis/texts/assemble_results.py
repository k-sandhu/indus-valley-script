"""Freeze the actual documentary comparison and its exact input joins."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=HERE/'run-v1';out.mkdir(exist_ok=True);target=out/'RESULTS.json'
    if target.exists():raise FileExistsError(target)
    obs=json.loads((HERE/'OBSERVATIONS.json').read_text('utf8'))['observations']
    lexobs=json.loads((HERE/'LEXICAL-SOURCE-OBSERVATIONS.json').read_text('utf8'))['observations']
    comp=json.loads((HERE/'COMPARISONS.json').read_text('utf8'))['comparisons']
    joins=json.loads((HERE/'MATERIAL-JOINS.json').read_text('utf8'))['joins']
    lex=json.loads((HERE/'LEXICAL-RESULTS.json').read_text('utf8'))
    result=dict(status='completed-documentary-comparison',
        frame=dict(full_main_stanzas=27,main_hymns=['RV9.112','RV10.71','RV10.101'],main_and_control_observations=len(obs),lexical_source_observations=len(lexobs)),
        measurements='Counts describe this fixed documentary frame; no likelihood, posterior, cause estimate or institutional census.',
        input_hashes={f:sha(HERE/f) for f in ['PROTOCOL.md','selection-v1.json','freeze-v1.json','OBSERVATIONS.json','LEXICAL-RESULTS.json','LEXICAL-SOURCE-OBSERVATIONS.json','COMPARISONS.json','MATERIAL-JOINS.json','SOURCES-v2.json']},
        dependency_hashes={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [ROOT/'experiments/2026-10-12-transmission-hypothesis/material/sources.json',ROOT/'experiments/2026-10-12-transmission-hypothesis/material/observations.json',ROOT/'experiments/2026-10-12-transmission-hypothesis/review/sources-v2.json',ROOT/'experiments/2026-10-12-transmission-hypothesis/review/observations-v2.json']},
        script_sha256=sha(Path(__file__)),component_results=comp,material_join_results=joins,lexical_matches=lex['matches'],
        directly_attested_relations=['RV10.71.2 depicts fashioning speech through a meal-sifting comparison.','RV10.71 depicts affiliation, varying competence, recognition and differentiated ritual actions.','RV9.112 portrays occupational/client and mixed household relations.','RV10.101 deploys practical equipment and operations within a ritual exhortation.','DN1 organizes a represented repertoire through normative livelihood rules.'],
        historical_inference='Specific local routes remain untraced; external inherited explanations support selected components. Organization at a textual stage does not identify an earlier donor or observed redaction event.',
        new_refinements=['bīja lexical comparison is post-selection.','Practical-to-conceptual incorporation is a post-reading refinement within the fixed complete speech hymn.'],
        excluded_endpoint='paired-passages-v1.json Greek translation misalignment; preserved, replaced for analysis by v2. Other paired groups unchanged.')
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(main_stanzas=27,observations=len(obs)+len(lexobs),comparisons=len(comp),material_joins=len(joins))))


if __name__=='__main__':main()
