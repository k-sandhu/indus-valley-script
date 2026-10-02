"""Export a concise machine-readable overview, with experimental scopes intact."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text())


def main():
    restoration = load('results/restoration/benchmark.json')
    independent = load('results/independent_annotator/candidate_event_test.json')
    structural = load('research/methods/results/nested_primary/nested_results.json')
    frozen = load('research/visual_digitization/font_fresh20/evaluation_frozen_endpoint.json')
    geometry = load('research/methods/results/font_geometry_sensitivity/evaluation_post_reference.json')
    result = {
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'report_build': load('output/report_build.json'),
        'decipherment_status': {
            'authenticated_translations': [], 'established_phonetic_values': [],
            'language_identified': None,
            'contribution': 'Reproducible structural constraints, prediction tools and original-source audits; no authenticated semantic decipherment.',
        },
        'structural_prediction': structural['observed'],
        'unique_conditioned_null': load('research/methods/results/joint_nested_unique_conditioned_1000/completion_audit.json'),
        'independent_annotator_candidate_events': independent['all_clear_weighting'],
        'known_one_slot_graphic_restoration': {
            'local_model': restoration['models']['local'],
            'baseline': restoration['models']['baseline'],
            'scope': 'Cross-validated artificial single-glyph masks; not authenticated restoration of damaged inscriptions.',
        },
        'image_acquisition': {
            'frozen_twenty_rows': frozen['summary']['all20_prespecified'],
            'post_reference_geometry_diagnostic': geometry['summary_all20'],
            'scope': 'Printed modern drawn units and candidate-set compatibility; source geometry, editorial auxiliaries and unknown physical boundaries are explicit.',
        },
        'conditional_numerical_result': {
            'premises': ['v=2S-L', 'vL+1=7S+5', 'Positive integer L,S,v'],
            'complete_solutions_L_S_v': [[4, 20, 36], [6, 8, 10], [10, 8, 6], [36, 20, 4]],
            'additional_assumed_range_8_to_13_or_18_selects': [10, 8, 6],
            'scope': 'Exact conditional algebra; external range, referents, units and equal-quantity premises remain unverified.',
        },
        'source_chart': {'cells': 687, 'numeric_ambiguities': 16, 'path': 'output/chart_atlas/index.html',
                         'scope': 'AI manual numeric reference with original-source image provenance, not expert sign gold.'},
        'independent_reviews': ['research/corpus/primary/chart_complete/consolidated_atlas_audit.json',
                                'research/methods/results/font_fresh20_audit/audit.json',
                                'research/root_geometry_audit.json',
                                'research/literature/report_source_review_final.md'],
        'verification': load('output/verification.json'),
    }
    result['report_pdf_sha256'] = hashlib.sha256((ROOT / 'output/pdf/indus_script_research_report.pdf').read_bytes()).hexdigest()
    (ROOT / 'output/research_summary.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'path': 'output/research_summary.json', 'edition': result['report_build']['edition']}))


if __name__ == '__main__':
    main()
