"""Build a semantic-input coverage map from the indexed research entries.

This reads metadata and writes an audit. It runs no fitted model or experiment.
"""
from collections import Counter
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'knowledge').is_dir())
BASE = Path(__file__).resolve().parent

FAMILIES = {
    'graphic_acquisition': ('Source-linked shapes, segmentation and candidate catalogue codes', 'Printed/photographic witnesses and coded transcriptions exist; fresh-font whole-row acquisition remains unsuccessful', 'Independent graphic adjudication, preserved physical boundaries, damage and editorial-unit treatment'),
    'graphic_prediction': ('Conditional graphic distributions, artificial restoration ranks and structural score contrasts', 'Graphic strings, physical aliases and selected metadata are available', 'A source-certified damaged slot for real restoration, or an independent functional/quantity target for semantic prediction'),
    'gap_count': ('Predicted missing-span length under an artificial masking design', 'Transcribed strings exist; the tested count predictor loses to always-one', 'Independent surviving gap geometry, reference counts and a fresh held-out acquisition population'),
    'source_context': ('Object/source correspondence and bounded physical-use or display descriptions', 'Source-defined Harappa/Lothal/Kanmer cohorts exist; particular observation fields and identity joins remain unresolved', 'Object-specific target verification, separate source-derived versus independently observed labels and appropriate short-text units'),
    'substitution_frames': ('Graphic compatibility and transferred shared-frame support', 'Candidate-coded frames and limited original plate checks exist', 'Independent class identity and a reserved semantic prediction that distinguishes proposed roles'),
    'generative_adequacy': ('Predictive adequacy of declared record mechanisms', 'Indus sequences and known/nonphonetic controls exist', 'A mechanism with independently measured functional fields; a fitting gain alone supplies no semantic target'),
    'numerical_proposal': ('An exact feasible parameter set under supplied arithmetic and graphical premises', 'Selected Indus numerical-proposal graphics and four conditional positive solutions exist', 'Historical object joins, independent equal-quantity/addition premises, commensurate units and a held-out count'),
    'metrology_scale': ('Identified products and explicitly rescaled alternative parameterizations', 'Published vessel examples and a scale-symmetry demonstration exist', 'An independently fixed count or goods unit and a securely joined held-out vessel measurement'),
    'relabelling_symmetry': ('A proof of structural-label nonidentification and the residual maps after supplied identities', 'Indus graphic structure is available; no independent identity oracle is supplied', 'An external identity/functional association; one anchor leaves a remaining permutation unless further evidence restricts it'),
    'known_reference_mapping': ('A bijection into an externally supplied reference alphabet, with score/search/tie diagnostics', 'Indus transcriptions exist; an independently justified matching reference population and bijection are missing', 'Known reference semantics/process, compatible inventories, record units and test observations outside mapping selection'),
    'measurement_selection': ('A selected next observation under a supplied action menu and response law', 'Source acquisition targets exist; simulated actions/costs/oracle responses are supplied premises', 'Accessible object-level actions, independent measurement likelihood, availability, cost and calibrated errors'),
    'independent_validation': ('Acceptance/rejection or feasible-set restriction using reserved independent targets', 'Reusable validation calculations exist; no Indus identity/count validation packet is supplied', 'Reliable reserved identities or object-specific quantities chosen to distinguish the remaining alternatives'),
    'physical_quantity': ('Positive relative quantities, conditional absolute quantities or geometric account correspondence', 'Known khipu source records and synthetic whole-part controls exist; the analogous Indus membership/count packet is absent', 'Stable labels, independently observed membership/completeness, additivity, units and nonredundant held-out targets'),
    'conditional_reference': ('Conditional-space laws, calibration, fitting support and observation-channel parameters', 'Corpus dependency metadata exists; synthetic sampling and error laws were supplied', 'Measured copy/face/selection/quality/error law for the actual observation population'),
    'population_identification': ('Mixing weights and form-specific slot distributions identified from the exact population within fixed r=3', 'Stored synthetic generator parameters exist; the same product-model premises and exact probabilities are unavailable for Indus', 'Justified component count/product model, finite-sample estimation and independently grounded functional reference'),
    'production_geometry': ('Predicted contact/preservation effects under a specified material and pressing model', 'Source photos and specimen targets exist; transfer parameters are unmeasured', 'Measured matrix/relief/clay/curvature/pressing conditions and experimental contact controls'),
    'integrity_documentation': ('Preservation, report and historical computation correspondence', 'Source and outcome records are preserved', 'Use the method-specific evidence and semantic target requirements; integrity is not an additional target measurement')}


def family(entry):
    identity = entry['id']
    root = {'ROOT-01':'graphic_acquisition', 'ROOT-02':'graphic_prediction', 'ROOT-03':'graphic_prediction',
            'ROOT-04':'graphic_prediction', 'ROOT-05':'graphic_prediction', 'ROOT-06':'graphic_prediction',
            'ROOT-07':'graphic_prediction', 'ROOT-08':'gap_count', 'ROOT-09':'source_context', 'ROOT-10':'source_context',
            'ROOT-11':'substitution_frames', 'ROOT-12':'generative_adequacy', 'ROOT-13':'numerical_proposal',
            'ROOT-14':'metrology_scale', 'ROOT-15':'graphic_acquisition', 'ROOT-16':'graphic_acquisition',
            'ROOT-17':'graphic_acquisition', 'ROOT-18':'graphic_acquisition', 'ROOT-19':'source_context', 'ROOT-20':'integrity_documentation'}
    if identity in root:
        return root[identity]
    if identity.startswith('METHODS-'):
        name = identity[8:]
        if name.startswith('font_'):
            return 'graphic_acquisition'
        if name == 'gap_design_matched':
            return 'gap_count'
        if name == 'numerical_equalities':
            return 'numerical_proposal'
        if name.startswith(('adjusted_max', 'classaware', 'joint_transfer')):
            return 'substitution_frames'
        if 'templates' in name:
            return 'generative_adequacy'
        return 'graphic_prediction'
    if identity.startswith('MARKOV-'):
        return 'graphic_prediction'
    if identity.startswith(('ARCH-', 'CONTEXT-', 'KANMER-', 'COMM-')):
        return 'source_context'
    if identity.startswith('NULL-'):
        return 'conditional_reference'
    if identity.startswith('KHI-'):
        return 'independent_validation' if identity == 'KHI-05' else 'physical_quantity'
    fixed = {'CRYPTO-01':'relabelling_symmetry', 'CRYPTO-04':'measurement_selection', 'CRYPTO-05':'independent_validation',
             'CRYPTO-11':'population_identification', 'PHYS-01':'physical_quantity', 'PHYS-02':'measurement_selection',
             'GEOM-01':'production_geometry', 'NUM-02':'known_reference_mapping'}
    if identity in fixed:
        return fixed[identity]
    if identity.startswith('CRYPTO-'):
        return 'known_reference_mapping'
    raise ValueError('Unclassified registry entry: '+identity)


def main():
    destination = BASE/'coverage.json'
    if destination.exists():
        raise FileExistsError('Preserve the prior coverage endpoint')
    registry = json.loads((ROOT/'knowledge/experiments/registry.json').read_text(encoding='utf-8'))['experiments']
    identifiers = [e['id'] for e in registry]
    assert len(identifiers) == len(set(identifiers)) == 101
    entries = []
    for entry in registry:
        name = family(entry)
        output, available, missing = FAMILIES[name]
        historical = entry['id'] in ['ROOT-03', 'METHODS-nested_unique', 'METHODS-classaware_unique']
        entries.append({'registry_id': entry['id'], 'family': name, 'indexed_status': entry['status'],
                        'output_identified': output, 'present_indus_input_packet': available, 'required_new_inputs': missing,
                        'current_verified_indus_semantic_value': None, 'retained_historical_or_superseded_population': historical,
                        'review_basis': 'indexed design/outcome and the family methods/result/retrospective cited in AUDIT.md',
                        'indexed_evidence': entry.get('evidence', [])})
    result = {'scope': 'Input-to-output and semantic readiness review; no model runs or frozen-endpoint reruns',
              'registry_path': 'knowledge/experiments/registry.json', 'reviewed_registry_ids': identifiers,
              'reviewed_registry_count': len(identifiers), 'family_counts': dict(Counter(e['family'] for e in entries)),
              'readiness_levels': {'tools_ready': 'Specified solvers, mapping/prediction routines and source tables are reusable within their tested domains',
                                   'actual_semantic_test_packet': 'Bounded physical-category constraints are available; an independently measured Indus quantity/identity packet is absent',
                                   'confirmed_one_indus_value': 'No indexed evidence packet currently confirms an Indus numerical/lexical value',
                                   'later_reading_requirements': 'A functional/count role would supply one anchor; sounds, language and productive readings require additional independently discriminating evidence'},
              'entries': entries}
    destination.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({'reviewed_ids': len(identifiers), 'families': result['family_counts']}, indent=2))


if __name__ == '__main__':
    main()
