"""Apply source-level 0.3.1 documentation changes, with checked replacements."""
from build_release import HERE

def edit(name, pairs):
    path=HERE/name;text=path.read_text(encoding='utf8')
    for old,new in pairs:
        if old not in text:raise ValueError((name,old))
        text=text.replace(old,new)
    path.write_text(text,encoding='utf8')

def main():
    edit('write_release_docs.py',[
        ('Number and classification may be null.','Number and classification may be null. `printed_inscription_id` is a string preserving the printed number and suffix; `classification_literal` is a five-position string, including spaces. Frozen-format aliases `inscription_number` and `classification_code` are accepted. If both names are supplied, their values must agree.'),
        ('The scorer rejects missing unit confidence and missing/invalid v2/v3 section.','The scorer rejects missing number/classification keys, conflicting aliases, missing unit confidence and missing/invalid v2/v3 section.'),
        ('The chart and benchmark await expert epigraphic certification. ',''),
        ('version 0.3.0. [Dataset]','version 0.3.1. [Dataset]'),
        ('version = {{0.3.0}}','version = {{0.3.1}}'),
        ("'version':'0.3.0'","'version':'0.3.1'"),
        ("'license':['CC0-1.0','CC-BY-4.0','Unlicense'],",''),
        ('Report errors through {ISSUES_URL}.\',\'type\'', 'Per-component licences apply; see LICENSE for CC BY 4.0 edition content, CC0 project additions and Unlicense code. Report errors through {ISSUES_URL}.\',\'type\''),
        ('Source authors have not certified these changes or endorsed the dataset.','Version 0.3.1 adds independent-reading impact annotations and accepts public prediction keys while preserving frozen payloads and scores. Source authors have not certified these changes or endorsed the dataset.'),
        ('Chart and benchmark readings were AI-assisted and await expert certification.','AI-reference provenance is described once in the card\'s benchmark frames section.'),
        ("definition=d.get(f['name'],'Definition missing.')","definition=d.get(f['name'],'Definition missing.').replace('staged PNG bytes','published PNG bytes')"),
        ('Prediction units contain confidence in [0, 1] and ranked alternatives, each with codes.', '''Prediction rows require printed_inscription_id (printed number and optional suffix, string or null) and classification_literal (five-position classification preserving spaces, string or null). The scorer accepts inscription_number and classification_code as frozen-format aliases, respectively; conflicting aliases and absent keys are errors. Required row identifiers are sample_index, occurrence_key and pdf_page; v2/v3 also require section. Prediction units contain confidence in [0, 1] and ranked alternatives, each with codes.'''),
        ('Per-unit correction flags never change frozen codes: corrected_cell identifies a linked changed record;', '''Per-unit correction flags never change frozen codes. corrected_cell joins the union of chart_locations, chart_references and shape_only_chart_locations to changed cells. This broader union yields 20 corrected-cell units and seven class-metadata units for v2 reader B; the chart impact's strict-location counts are 12 and six. Eight units link changed cells only through shape-only locations, including one additional class change. candidate_fields_would_change is populated for independent readings as well as adjudicated references. For each candidate field, use its own chart locations (shape_only_chart_locations for shape-only candidates, otherwise chart_locations or chart_references); intersect each code's locations with its original cell membership, map those cells to reviewed candidate labels, and flag a field if its resulting set differs. Unlocated identities stay unchanged and receive a warning. This is a conditional mapping diagnostic, not a rescoring. corrected_cell identifies a linked changed record;'''),
        ("    public_sources=read(HERE/'sources.json')",'''    from public_provenance import write_public_provenance
    write_public_provenance(release,builder)
    public_sources=read(HERE/'sources.json')'''),
        ("    dump(release/'sources.json',builder.portable.value(public_sources))\n    dump(HERE/'rights-audit.json',read(builder.records/'rights-audit.json'))\n    write_owner_records()",'''    public_sources.pop('reused_project_witnesses_0_3_0',None)
    public_sources['project_evidence']=[
        dict(title='Chart numeric reference 2.1 and change review',authors=['k-sandhu'],year=2026,venue='This dataset',url='docs/CHART-REVIEW.md',opened=True,search_snippet_only=False,exact_location='chart_reference; provenance/chart-changes.json'),
        dict(title='Three frozen row-reading evaluations',authors=['Project AI readers and adjudicators'],year=2026,venue='This dataset',url='README.md#benchmark-frames-and-reference-provenance',opened=True,search_snippet_only=False,exact_location='benchmark_rows_v1/v2/v3; benchmark/expected-metrics.json; benchmark/reader-metadata.json')]
    dump(release/'sources.json',builder.portable.value(public_sources))
    if update_owner:write_owner_records()'''),
        ('The coordinator uploaded version 0.2.0 privately and reports all 19 configurations (2,720 rows) and images loading.','The coordinator uploaded version 0.3.0 privately. REVIEW-0.3.0.md verifies all 23 configurations (3,308 rows), decoded images and 136 local/Hub files at commit 541766d5ea8a4c3b3ec5fcc416ee764af8763afb.'),
        ('Update reference benchmarks to 0.3.0 for private owner review','Update reference benchmarks to 0.3.1 for private owner review'),
        ('The existing private preview holds 0.2.0.','The existing private preview holds verified 0.3.0.'),
        ('Hosted 0.3.0 checks remain for the coordinator after this local handoff.','Repeat these hosted checks for 0.3.1 after the coordinator updates the private preview. The private datasets-server viewer returned HTTP 501 during the 0.3.0 review; check every image-bearing viewer table after public visibility is approved.'),
        ('Synthesis v6 reconciles site labels and counts separately for face records, provisional families, catalogue entries and bounded collection queries.','The census compilation reconciles site labels and counts separately for inscribed-surface records, provisional export groupings, catalogue entries and bounded collection queries. Its sixth consolidation combined the registers after copied source prose/search snippets were removed. CISI means Corpus of Indus Seals and Inscriptions.')
    ])
    edit('build_release.py',[
        ("description=f'{len(rows)} source rows with immutable references and frozen predictions.'","description={'v1':'60 numbered-section targets with context crops, initial reference and original template predictions.','v2':'80 targets across three sections with context/exact crops and the second frozen template pipeline.','v3':'80 fresh targets on previously unused target pages with context/exact crops and the third frozen template pipeline.'}[version]"),
        ("description='Synthesis v6 authored aggregate table; frame and measurement columns define denominators.'","description={'evidence_catalogue_coverage':'Catalogue-to-export key coverage by site and publication, with explicit matched/absent denominators.','evidence_catalogue_sections':'19 inspected Gujarat/north India CISI 1 sections, separating pottery/graffiti from other catalogue keys.','evidence_field_completeness':'Measured and assessed field availability by source register and bounded query frame.'}[config]"),
        ("description='Aggregate metrology results after review; no Ascalone catalogue records included.'","description={'weight_mass_bands':'Four Dholavira mass-band fits with sample sizes, fitted units, signal estimates and intervals.','weight_chance_controls':'Nine western-screen control rows across three frames and three randomization rules, with observed and simulated hit counts.'}[name]"),
        ('115 site/provenance entities from synthesis v6; aggregate counts in distinct source frames.','115 site/provenance entities in the reconciled census compilation; aggregate counts in distinct source frames.')
    ])
    edit('validate_release.py',[
        ('Hosted 0.3.0 loading/viewer awaits coordinator update; coordinator reports 0.2.0 all 19 configs load.','Hosted 0.3.0 is verified by REVIEW-0.3.0.md; hosted 0.3.1 remains a coordinator check after upload. Private viewer returned HTTP 501; public viewer remains unchecked.')
    ])

if __name__=='__main__':main()
