"""Build current documentation drafts; never mutate prior endpoints or shared files."""
import argparse, json
from pathlib import Path
from build_corrections import OWN, PKG, read, write

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args()
    out=Path(a.output).resolve();out.relative_to(OWN)
    if out.exists():ap.error('Use a fresh draft directory.')
    out.mkdir(parents=True)
    current='amendment-2026-10-07-review-corrections'
    for label,part,prefix in [('original','root',current),('Frenez amendment','frenez','../'+current)]:
        dest=out/part;dest.mkdir()
        def link(name):return f'{prefix}/{name}'
        intro=f'''Status: Exploratory; arithmetic: Verified computation. The current review correction has **65 rows, 50 sources, 17 attributed claims and 30 dated contributing rows** (2 A, 15 B, 13 C). Broad possible coverage has no empty century; A+B at any strength leaves two 100-year empty bins. The high/moderate-calendar A+B longest internal empty run ranges **400–1,600 years** across 80 Pirak/Perumbalai scenarios. Their current low ratings give 1,600 years, 1900–300 BCE; hypothetical moderate Perumbalai gives a 400–1,200-year range. This measures coverage of the assembled inventory. [Summary]({link('run-2026-10-07-04/summary.json')}), `gaps`; [sensitivity]({link('sensitivity-04/gap-sensitivity.json')}), `scenario_ranges`.
'''
        hist='42 rows, 18 sources, 11 claims and 19 dated contributors'if part=='root'else'54 rows, 44 sources, 17 claims and 24 dated contributors'
        readme=f'''# Backward chronology: current record

{intro}
The preserved {label} endpoint contains {hist}. Its 1300–700 BCE result used a pooled Pirak date that does not match the seals' II/IIIA captions, and a moderate Perumbalai rating. Current assessments split the Pirak specimens, keep unresolved absolute dates C/low, rate Perumbalai's conflicting calendar labels low, add omitted contexts and exclude site-wide totals without dated-layer allocation. [Current evidence table]({link('inputs-05/evidence-table.json')}); [CSV]({link('inputs-05/evidence-table.csv')}); [field changes]({link('inputs-05/correction-log.json')}).

Use [the current README]({link('README.md')}) for rerunnable commands, [REPORT]({link('REPORT.md')}) for primary-source/date/count/attribution corrections, [COVERAGE]({link('coverage-02/COVERAGE.md')}) for all 33 centuries, and [TEST-DESIGNS]({link('TEST-DESIGNS.md')}) for seven Proposed tests with sample/effect targets. Exact citations and opened-page scope are in [sources]({link('inputs-05/sources.json')}). Earlier input tables, scripts, computed outputs and raw witnesses remain unchanged. Previous documentation is in [documentation-before]({link('documentation-before/')}), with the current preservation checks in [review-checks]({link('review-checks-02.json')}).

The first amendment's 193 added specimens comprise 191 inscribed sherds/sealing and two motif-bearing objects without surviving script. A causal kiln replacement, a direct circa-2800 hearth/sample join, and an authenticated aligned two-script pair remain unrecovered. Pirak's 1979 chronology, 2010 recalibration chapter and exact later-seal catalogue concordance are the immediate dating targets. [Dating details]({link('inputs-05/dating-details.json')}); [recovery audit]({link('recovery-audit.json')}); [complete created/changed paths]({link('file-manifest.json')}).
'''
        (dest/'README.md').write_text(readme,encoding='utf-8')
        report=f'''# Backward chronology: revised findings, 7 October 2026

{intro}
| Series | Current longest internal empty run | Sensitivity range |
|---|---|---:|
| All selected assessments | None | 0 years |
| A+B, any strength | 800–700 and 400–300 BCE | 100 years |
| A+B, high/moderate strength | 1900–300 BCE | 400–1,600 years |

Pirak and Perumbalai control the third series. Its original 600-year result is preserved as a historical computation, but the primary specimen/date join and Perumbalai calendar rating do not support treating it as an archaeological absence interval. [Endpoint comparison]({link('coverage-02/comparison.json')}); [current century table]({link('coverage-02/COVERAGE.md')}).

The correction adds Daimabad V, Thulukkarpatti I, Sivagalai II and A2-Urn-3, Adichanallur burial/habitation records, Kodumanal MEG-19, Korkai KRK-4 and a non-additive Kongu synthesis; Inamgaon's two cultural ranges are separate. Kodumanal's documented count is 1,955, Sivagalai habitation's is 150, Porunthal retains the one/two ringstand conflict, and Kilnamandi retains 88 narrative sherds against 103/101 table totals. Site-wide unallocated counts do not enter numeric century bounds. [Evidence rows]({link('inputs-05/evidence-table.json')}), `count_basis`, `dating_assessments`; [full findings]({link('REPORT.md')}).

Quivron gives 142 failed-firing jars; Miller gives about 140 and estimates about 200 originally. Quivron p. 279 compares incised marks. Rehman object 54 has IA/IB alternatives; the former Period II reading is removed. Its likely phase-count transposition is explicit: 41−14 equals the 27 difference. The 193-specimen first-amendment addition includes two motif-bearing objects without surviving script. [Dating details]({link('inputs-05/dating-details.json')}), `count_audit`, `rehman_object54`, `specimen_units`.

Frenez's fifth-century era is inferred as BCE. Allchin/Coningham's 450–350 BCE Anuradhapura estimate is second-hand here; the original chapter remains unopened. Opened Volume II reports Porunthal 580–520 and 560–410 BCE, with unstated calibration convention and separate association grades. These overlap the fifth-century comparison without identifying merchant carriers; Ashokan Brahmi is the A/high historical endpoint. The BnF/contact date-image inconsistencies, eight claim records, ten source records and analyst-prose spacing were corrected in new inputs. [Current comparison and citations]({link('REPORT.md')}); [claims]({link('inputs-05/continuity-claims.json')}); [sources]({link('inputs-05/sources.json')}).

The original endpoint contains {hist}. Its tables and computed files remain unchanged; use the linked correction for current conclusions. [Preservation and reproduction checks]({link('review-checks-02.json')}); [retrospective]({link('RETROSPECTIVE.md')}).
'''
        (dest/'REPORT.md').write_text(report,encoding='utf-8')
        historical=OWN/'documentation-before'/('RETROSPECTIVE.md'if part=='root'else'amendment-2026-10-07-frenez/RETROSPECTIVE.md')
        previous=historical.read_text(encoding='utf-8-sig').replace('[run-2026-10-07-02](run-2026-10-07-03/summary.json)','[run-2026-10-07-03](run-2026-10-07-03/summary.json)')
        retro=f'''# Dated review correction, 7 October 2026

{intro}
The primary catalogue was reused; it places Pk-15–17 in IB, so the later-seal date remains unresolved. The 2012 publisher paper was opened, the 2010 preview lacked its chapter and the Coningham full-paper attempt returned 403 HTML. Current source access, small raw additions, text repairs and verification outcomes are described in [the new retrospective]({link('RETROSPECTIVE.md')}) and [recovery audit]({link('recovery-audit.json')}). The earlier report below records the outcome as assessed before this review correction. Its computations remain preserved; current archaeological assessments are in the linked amendment.

## Preserved earlier work account

'''+previous
        (dest/'RETROSPECTIVE.md').write_text(retro,encoding='utf-8')
        designs=f'''# Current Proposed test designs, 7 October 2026

The complete definitions, data availability, nulls and support/rejection rules are in [the seven current designs]({link('TEST-DESIGNS.md')}). Numerical planning assumptions are Synthetic in [power-targets.json]({link('power-targets.json')}), rerunnable with `power_targets.py`. No archaeological test was run.

| Design | Required effective sample | Detectable effect / evaluation requirement |
|---|---|---|
| 1. Rare compounds | 300 route objects over three deposits/two sites; 1,000 controls | 1% to 5%; fixed-rate power 0.9350, joint route simulation at least 80% |
| 2. Matched shape features | 600 per group over independent inventories | 20% to 30%; approximate power 0.8887 |
| 3. Seriation | 12 assemblages × 30 objects, three sites | 0.10 bits/object; 1,000 simulations per model, at least 80% power; power not yet estimated |
| 4. Positional rules | 400 multi-mark objects per group/time slice, three intermediate slices | 10% to 20%; approximate power 0.8836, joint slice simulation required |
| 5. Kiln frequency | Batch-aware target to be simulated from reconstructed denominators | Ten-percentage-point decline; at least 80% power |
| 6. Hearth date | Registered sealing/feature/sample/calibration join | At least 95% calendar probability before or after 2800 BCE |
| 7. Contact conventions / paired blocks | 250 graphic objects per group / 60 held-out independent pairs | 10% to 25%, approximate power 0.9550 / 20% to 50%, exact power 0.9863 |

Design 3 compares contextual independence (`q_context = softmax(beta × covariates)`, hierarchical site effects, Dirichlet-multinomial sampling) with copying/mutation (`q_t = (1−rho) q_context,t + rho M_mu q_previous`) on a declared dated route. Both share complexity, medium, ware, production covariates and dispersion. The planning alternative uses rho 0.70, mutation 0.10 and concentration 50; hold out sites and temporal blocks. Its 360-object target must be power-checked before evaluation. [Full design 3]({link('TEST-DESIGNS.md')}), section 3.

Fixed-rate binomial and approximate two-group powers assume independent effective units and one-sided alpha 0.0025, allowing twenty Bonferroni-controlled tests per design. Clustering, estimated control rates, missingness and joint route constraints require simulation before interpreting a negative result. Only Kot Diji (95), Rangpur (222) and Rehman Dheri (190) are additive exact-count rows with at least thirty objects; the required normalized, dated deposit matrices and paired contact objects are missing. [Current evidence]({link('inputs-05/evidence-table.json')}); [targets]({link('power-targets.json')}).
'''
        (dest/'TEST-DESIGNS.md').write_text(designs,encoding='utf-8')
        reg=read(OWN/'documentation-before'/('registry-entry.json'if part=='root'else'amendment-2026-10-07-frenez/registry-entry.json'))
        reg.update(status='Exploratory',outcome='Current review correction: 65 rows, 50 sources, 17 attributed claims and 30 dated contributing rows (2 A, 15 B, 13 C). Broad possible coverage has no empty century; A+B at any strength leaves two 100-year bins. The high/moderate-calendar A+B longest internal empty run ranges 400–1,600 years across 80 Pirak/Perumbalai assumptions; current C/low Pirak and B/low Perumbalai give 1,600 years, 1900–300 BCE. With hypothetical moderate Perumbalai the range is 400–1,200 years. These measure inventory coverage. The first amendment’s 193 added specimens comprise 191 inscribed sherds/sealing and two motif-bearing objects without surviving script. No diagnostic post-urban transmission chain or aligned paired-script object authenticated. Arithmetic Verified computation; seven tests Proposed; power assumptions Synthetic.',
            challenge='Original Pirak 1979 chronology and 2010 recalibration chapter unopened; exact II/IIIA seal catalogue concordance unresolved. Perumbalai calendar labels conflict and mark depths are unallocated. Site-wide totals, point-only dates, legacy chronology and conflicting source counts limit coverage. Coningham full-paper and Petrie mirror downloads returned HTTP 403; ten current live-search batches are preserved.',
            remedy='Preserve both earlier endpoints and raw witnesses. Correct rows, claims, citations and prose spaces in new dated inputs; separate methods and point/interval observations; exclude unaligned site-wide counts consistently. Show all three coverage series beside Pirak/Perumbalai sensitivity. Add explicit copying/independence models, effect/sample targets and simulation gates; rerun and hash-check computations.',
            retry_when='Recover the primary Pirak period chronology and registered seal concordances; named calibration conventions and mark/sample registers; normalized dated intermediate repertoires; original Anuradhapura sample tables; or authenticated paired contact objects. Recount Rehman phases before replacing 14 by 41. Achieve declared sample/power targets and freeze features/routes/nulls before evaluating transmission.')
        paths=['PROTOCOL.md','README.md','REPORT.md','inputs-05/evidence-table.json','inputs-05/sources.json','inputs-05/continuity-claims.json','inputs-05/correction-log.json','run-2026-10-07-04/summary.json','run-2026-10-07-04/coverage.csv','sensitivity-04/gap-sensitivity.json','coverage-02/comparison.json','TEST-DESIGNS.md','power-targets.json','RETROSPECTIVE.md','review-checks-02.json','file-manifest.json']
        reg['evidence']=['experiments/2026-10-06-backward-chronology/'+current+'/'+x for x in paths]
        write(dest/'registry-entry.json',reg)
        cov=f'''# Current coverage, 7 October 2026

{intro}
The corrected [33-century table]({link('coverage-02/COVERAGE.md')}) and [CSV]({link('run-2026-10-07-04/coverage.csv')}) show every assemblage, grade, image and exact-object bound. The earlier generated coverage page and both historical endpoints remain unchanged. Their 1300–700 BCE output is superseded as a current interpretation by [the sensitivity comparison]({link('coverage-02/comparison.json')}).
'''
        (dest/'COVERAGE.md').write_text(cov,encoding='utf-8')
    newreg=read(out/'root/registry-entry.json');newreg.update(id='BACKWARD-CHRONOLOGY-E-REVIEW-2026-10-07',theme='Review correction of backward chronology, count alignment and transmission test designs')
    write(out/'registry-entry.json',newreg)
    print(json.dumps(dict(draft_files=len(list(out.rglob('*.*'))),output=str(out))))
if __name__=='__main__':main()
