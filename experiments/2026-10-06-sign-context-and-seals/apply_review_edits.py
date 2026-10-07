"""One-time living-document corrections from the second coordinator follow-up."""
import json
from pathlib import Path

OWN = Path(__file__).resolve().parent


def run():
    report = (OWN / 'REPORT.md').read_text(encoding='utf-8')
    if '## Post-review corrections, 7 October' in report:
        raise FileExistsError('Document corrections have already been applied.')
    first = report.split('\n\n')[1]
    report = report.replace(first + '\n\n', '', 1)
    report = report.replace('No sign has a supported site-area association across the original and amended reference laws.',
        'Under the frozen area reference law, sign 520 passes correction (q = 0.044; minimum and maximum compiled areas give q = 0.044 and 0.047), but fails without Harappa and Mohenjo-daro (q = 0.387) and under the amended whole-object law (q = 0.223).')
    report = report.replace('External source sampling by the separate reviewer remains outstanding.',
        'The independent [Sonnet review](REVIEW.md) reproduced the endpoints and sampled their sources. The post-review area expansion remains Exploratory.')
    report = report.replace('This is a site-distribution result; neither the code\'s value nor the contrast establishes a sound or function.',
        'The contrast measures the distribution of a graphic sign across sites.')
    report = report.replace('These export categories are retained without assigning administrative meanings.',
        'The analysis retains the export\'s object categories.')
    report = report.replace('The 3C-2 sample contradicts the strict prediction of minority motifs in every adequately sampled period.',
        'The 3C-2 sample contains 35 unicorns and no recorded minority motif; its label shares the same broad 2200–1900 BCE interval as the other 3C subphases.')
    report = report.replace('with the enclosing **Exploratory** status and the inherited helper-label note in `SOURCE-NOTES.md`.',
        'in the separately saved [corrected-label copy](post-review-2026-10-07-01/results-corrected-label.json). Only its nested status was changed to **Exploratory**; the source file remains untouched.')
    report = report.replace('The inspected preview\'s pp. 186–187 describe roughly 65% unicorns in its reference corpus; our 77.44% is from known square motifs in this export and has a different denominator. Its p. 167 discusses size/style variation and workshops.',
        'The inspected preview, pp. 186–188, attributes an approximate 65% **multi-site average** to Marta Ameri\'s 2013 study. The newly opened chapter, *Regional Diversity in the Harappan World: The Evidence of the Seals*, in **Connections and Complexity: New Approaches to the Archaeology of South Asia**, pp. 355–374, compares six sites (Table 19.1, printed p. 361). Our 77.44% pools known square motifs in this export. The earlier attribution of size/style discussion to Frenez p. 167 is withdrawn because that page was not preserved in the inspected witness. His published persistence discussion spans more than six centuries.')
    report = report.replace('Reviewer priorities are the uncertain site boundaries, the mixed Chanhu-daro function, three unread style/size papers, and the unidentified Rao motif item.',
        'Remaining source gaps concern matched occupation boundaries, full carver/style chapters and the unidentified Rao motif item.')
    report = report.replace('This tests richness, not identical sign frequencies.',
        'The reference tests site inventory richness conditional on sample size and object composition.')
    report = report.replace('These are fitted unseen-code predictions, not observed signs.',
        'These fitted curves estimate additional unseen codes.')
    report = report.replace('the present counts cannot choose between linguistic interpretations proposed in that literature.',
        'the present counts measure the frequency distributions in the selected corpus views.')
    report = report.replace('Figure 2 and the following discussion, compare filtered and unfiltered Mahadevan corpora.',
        'Figure 2 (frequency distribution) and the text accompanying Figure 4 (terminal 10% observation), compare filtered and unfiltered Mahadevan corpora.')
    report = report.replace('Across the 14 eligible site/type comparisons, only `TAB:I` fails enrichment after correction.',
        'Across six eligible site comparisons and eight object-type comparisons, only `TAB:I` fails enrichment after joint correction.')
    report = report.replace('Its effect varies by type and does not assign a grammatical or administrative meaning.',
        'Its effect varies by object type.')
    old = 'The persistence endpoint uses 203 known-motif square-seal components at Harappa with Period 3 labels. Raw label heterogeneity among the five labels with at least ten known motifs gives p = 0.0035, q = **0.007**. The interval-time score gives p = q = **0.0194**. Both move whole motif payloads against recorded period intervals. These results reject identical recorded unicorn shares under the specified reference. The records do not sustain a claim that those shares remained constant.'
    new = 'The persistence endpoint uses 203 known-motif square-seal components at Harappa with Period 3 labels. Raw label heterogeneity among the five labels with at least ten known motifs gives p = 0.0035, q = **0.007**. This contrast arises among 3C subphase labels that all share one **2200–1900 BCE interval**. The reviewer\'s four-label 3C-only test gives **p = 0.0006** on 117 objects ([check3 output](review/check3-post-launch.json), `period_heterogeneity_within_3C_subphases`). Unambiguous broad phases give **3B 6/7** and **3C 112/123** unicorns. These observations do **not contradict the lecture\'s persistence statement**; subphase-label heterogeneity does not establish dated change. The separately fitted interval-time score gives p = q = **0.0194** and depends on the recorded interval assignments, including ambiguous dates and the single early 3A object.'
    assert old in report
    report = report.replace(old, new)
    report = report.replace('The primary date range is **700 years**, with uneven coverage. The package therefore tests recorded Harappa phases and cannot evaluate constancy for nearly a millennium.',
        'The coordinator\'s [caption check](../2026-10-06-research-program/frenez-talk-check.md), at 41:30–43:30, paraphrases the lecture: “the iconographies kept the same frequencies for almost a millennium.” This is a quotation of the caption-based summary, whose wording is explicitly paraphrased, rather than a verbatim speech transcript. The primary data range is **700 years**, with uneven coverage. It covers the published chapter\'s more-than-six-centuries scope, while leaving the lecture\'s almost-a-millennium duration incompletely sampled.')
    # Keep the single shared interpretive scope statement with the common methods.
    report = report.replace('These are conditional exchangeability assumptions about the acquired objects.',
        'These are conditional exchangeability assumptions about the acquired objects. All sign values here are graphic catalogue codes; the tests establish no sound, meaning or owner identity.')
    report += '''

## Post-review corrections, 7 October

The dated amendment appended to [PROTOCOL.md](PROTOCOL.md) preceded the new area computation. [site-extents-review-2026-10-07.json](site-extents-review-2026-10-07.json) supplements the unchanged frozen table with the Treccani site-entry extents and Banawali. The acquired Banawali entry already gave a 400-m side, a 16-ha bounding square; the earlier statement that no numerical source was acquired was incorrect. The source log now records that correction, with its original version archived. Rakhigarhi and Ganweriwala also receive Treccani hierarchy citations.

The added anchors are Harappa about 100 ha, Rakhigarhi over 100 ha, Mohenjo-daro at least 2 × 2 km (400 ha), Lothal over 8 ha and a separate 400 × 300 m mound base (12 ha), Nausharo about 6 ha and Banawali 16 ha. Visible rectangles at Chanu daro (3 ha), Kot diji (2.4 ha) and Surkotada (0.72 ha) complete the source-definition sensitivity. The source-anchor table preserves section names, qualifiers, conversions and the saved text's character offsets. Lowest/highest printed anchors include different footprint definitions; an open lower bound has no established maximum.

[area.json](post-review-2026-10-07-01/area.json), `comparisons[]`, reports all four vectors on three cohorts. The expanded three-object cohort has **18 sites and 4,452 readable objects**; the adequately sampled cohort has **eight sites and 4,383 objects**. Removing the two cities leaves **16 sites and 791 objects**. Every test exchanges whole-component site labels within exact object type; 9,999 shared references and correction across ten signs are used in each comparison.

| Area vector | Minimum q, 18 sites | Minimum q, eight sites | Minimum q, without two cities |
|---|---:|---:|---:|
| Frozen reference anchors plus Banawali | 0.1770 | 0.6307 | 0.4720 |
| Treccani site entries | 0.1460 | 0.5075 | 0.3990 |
| Lowest printed anchors | 0.1560 | 0.3890 | 0.4930 |
| Highest printed anchors | 0.1670 | 0.4975 | 0.3690 |

Sign 520 supplies each minimum. No new comparison passes q < 0.05. These exploratory results retain the amended-law conclusion, while the frozen-law q = 0.044 remains a supported result under its own reference. The supplementary correction across all 120 new sign comparisons is also saved. The compressed reference array remains local-only.

### Precedents and result-specific relations

Gregg M. Jamison's 2018 *Understanding Indus Seal-Carving Traditions: A Stylistic and Metric Approach*, pp. 167–186, and Adam S. Green's 2018 *Operational Sequences and Stamp Seals: A Preliminary Report on an Experimental and Microtopographic Framework for Identifying Groups of Seal Carvers in the Indus Civilization*, pp. 187–203, appear in **Seals and Sealing in the Ancient World**, Cambridge University Press. Their publisher abstracts were opened. Jamison combines style and metrics to assign producer groups. Green describes thirty experimental seals and operational-sequence comparisons of two Chanhu-daro seals. These are direct precedents for adding production assignments to the pooled size/CV and motif–text analyses. Full chapters remain unread. Sources JC2018 and GC2018 in [sources-review-2026-10-07.json](sources-review-2026-10-07.json) give exact titles, URLs, DOI and access states.

Jamison's *The Organization of Indus Unicorn Seal Production. A Multi-faceted Investigation of Technology, Skill, and Style*, **Walking with the Unicorn**, 2018, pp. 272–291, addresses technology, skill and style in unicorn production. Its title and author were checked in publisher contents; chapter text remains unread (JW2018). Ameri 2013 was opened in full: her six-site iconographic comparisons precede the regional concentration result and its Banawali exception, **2/14 unicorn square motifs** here. Eastern Headwaters similarly has **9/27**. Those exceptions accompany the majority found at the six larger square-seal samples.

| Result | Relation to Yadav 2013, Oakes and Frenez |
|---|---|
| Site/object sign frequencies and area | Yadav's pp. 83–84 attribute some Harappa preferences to four heavily repeated texts. The review's one-object-per-site/type/text check retains sign 032 at q = 0.019 ([check1](review/check1-signs-sites.json)). The area amendment answers Frenez's site-context proposal while preserving the reference-sensitive 520 result. Oakes's contextual statistics supply an earlier site/object framework. |
| Inventory and concentration | The conditional richness endpoint adds sample-size matching to those contextual comparisons and tests Frenez's inventory bands. The readable cumulative shares remain close to his lecture's approximate concentration figures. Ameri supplies the multi-site motif comparison used by Frenez. |
| Motif concentration | Oakes Table 9 gives 1,045/1,385 unicorn seal symbols, **75.45%**, close to this export's all-seal **75.54%**. Oakes Table 8's Harappa unicorn deficit (residual −3.37) covers all object types; this package's Harappa **86.36%** is restricted to square seals. Their denominators and object compositions differ. |
| Motif–text and terminal signs | Oakes Table 10 and Yadav's field-symbol discussions precede sign–motif comparisons. Here the rare/unicorn length difference survives grouped and collapsed-text checks, while exact-length conditioning leaves sign-distribution q = 0.20525. Terminal 740 supports the lecture's end-position observation; it measures positional frequency in the selected texts. |
| Size and persistence | Pooled CV = 0.2886 and the area/length slope describe the export; Jamison/Green supply prior methods for production assignments. The period-label q = 0.007 concerns shared-interval subphase labels, and broad-phase shares remain compatible with Frenez's persistence proposal. The export alone cannot select among institutional regulation, dominant workshops and uneven recovery. |

### Motif mapping and the Salūt disagreement

[motif-mapping.json](post-review-2026-10-07-01/motif-mapping.json) records fourteen `Bull1*` codes pooled as unicorn. Their `metadata.cult` values most often include SAN (**693 faces**), RAN (**99**) and SAF (**128**), consistent with the stand association described in the seal literature. Oakes's independent Table 9 gives a close all-seal unicorn proportion. This is corroboration of the operational mapping; a complete image-checked codebook remains unavailable. The separate `Bull:i`, `Bull:i:J` and `Bull:i:S` codes are unpooled: **1, 3 and 1 faces**, respectively, and **three** clean rare-cohort objects.

`Gaur` is the available proxy for the Indian bison described by Frenez: **96/124 Gaur faces** carry `metadata.cult: Trough`. Oakes Table 9 lists **82** short-horned-bull seal symbols (code 04); this export has **85** Gaur square-seal objects. Frenez, Degli Esposti, Méry and Kenoyer 2016, pp. 116–117/Figure 9, identifies **Bos gaurus** at a manger. The export's Salūt ST1 square-seal record has Gaur, Trough and five signs, agreeing with that description. Its second Salūt record is a TAG coded Elep with two signs, while the publication describes a sherd with two bison and three or four signs. Both local rows are preserved for checking; no recoding was applied to a frozen result.

### Labels, files and availability

The registry proposal now uses **Exploratory** for the package's current inferential state and states its original Frozen evaluation and Verified computation checks in text. The corrected-label copy changes only the inherited nested status. The byte-identical duplicate follow-up checks file was removed after confirming its digest matched the retained canonical file; [revision-maintenance-2026-10-07.json](revision-maintenance-2026-10-07.json) records that removal. The current plots remain saved SVG artifacts. Their optional local plotting install became OneDrive online-only and cannot currently be read; it was neither hydrated nor reinstalled. The earlier recovery audit describes its observation at that time, rather than current availability.
'''
    (OWN / 'REPORT.md').write_text(report, encoding='utf-8')
    readme = (OWN / 'README.md').read_text(encoding='utf-8')
    top = readme.split('\n\n')[1]
    readme = readme.replace(top + '\n\n', '', 1)
    readme = readme.replace('The site-area comparison rests on 17 sites and does not retain a corrected association under the amended whole-object reference law.',
        'The frozen 17-site area law gives sign 520 q = 0.044 (minimum/maximum q = 0.044/0.047); it fails without the two cities (q = 0.387) and under the amended law (q = 0.223). The expanded 18-site post-review comparison has minimum q = 0.146 across its area vectors.')
    paragraphs = readme.split('\n\n')
    readme = '\n\n'.join(p for p in paragraphs if not p.startswith('The reviewer should sample ') and not p.startswith('Reviewer priorities are '))
    readme = readme.replace('Source and archaeological validation remain for the reviewer.',
        'The independent [review](REVIEW.md) reproduced these values and sampled sources.')
    readme = readme.replace('Optional `plot_followup.py --input <run> --output <fresh-figure-directory>` uses Matplotlib 3.11.2 and dependencies installed only under the local raw directory, and sets its writable configuration directory there.',
        'Optional `plot_followup.py --input <run> --output <fresh-figure-directory>` requires the local Matplotlib 3.11.2 install. OneDrive made that install online-only; the review received PermissionError and plotting is currently unavailable. Existing SVGs remain available. No plotting package was reinstalled or hydrated.')
    # Historical verifiers pin metadata files which this requested amendment edits.
    readme = '\n'.join(line for line in readme.split('\n') if not line.startswith('python experiments/2026-10-06-sign-context-and-seals/verify.py ') and not line.startswith('python experiments/2026-10-06-sign-context-and-seals/verify_followup.py '))
    readme += '''

## Second follow-up after the Sonnet review

The original [site table](site-table.json) and all frozen numerical endpoints remain unchanged. The dated [protocol amendment](PROTOCOL.md) and [supplementary source table](site-extents-review-2026-10-07.json) add the Treccani site-entry extents and Banawali's 16-ha bounding square. Across four area vectors, the expanded **18-site, 4,452-object** comparison has minimum q values **0.177, 0.146, 0.156 and 0.167**. No sign passes correction. Results and the separately corrected nested label are in [post-review-2026-10-07-01](post-review-2026-10-07-01/summary.json); reference values are compressed locally.

The period q = **0.007** concerns 3C labels sharing **2200–1900 BCE**, with the review's 3C-only p = **0.0006**. Unambiguous 3B **6/7** and 3C **112/123** unicorns do not contradict the lecture's persistence statement. [REPORT.md](REPORT.md) quotes the caption-based summary accurately and retains the broad change envelope. The report also adds four precedents, the Ameri source of the approximate 65% multi-site average, explicit motif-code cross-checks and the second Salūt record's disagreement.

[sources-review-2026-10-07.json](sources-review-2026-10-07.json) distinguishes the opened Ameri chapter, Cambridge abstracts and Archaeopress contents. `sources.json` corrects the Banawali log and withdraws the unverified Frenez p. 167 attribution. Their exact preceding versions are archived in `pre-second-followup-2026-10-07/`. The original verification scripts pin the pre-amendment protocol and source metadata; those historical assertions no longer target the living files. The current checker validates their archived versions, original protocol prefix, frozen endpoints and the new references.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:TMP = Join-Path (Get-Location) 'data/raw/2026-10-06-sign-context-and-seals/tmp'
$env:TEMP = $env:TMP
python experiments/2026-10-06-sign-context-and-seals/second_followup.py --run repeat-post-review-2026-10-07-01
python experiments/2026-10-06-sign-context-and-seals/verify_second_followup.py --run repeat-post-review-2026-10-07-01 --output repeat-post-review-checks-2026-10-07.json
python tools/review_prose.py --path experiments/2026-10-06-sign-context-and-seals --no-write
```

`second_followup.py --prepare` created the supplementary table before the first new area run; it refuses its existing input. The new run takes about 15 seconds, uses only NumPy/SciPy, and refuses existing output directories. No original endpoint needs to be rerun to check this revision. The removed duplicate checks file and its retained canonical digest are recorded in [revision-maintenance-2026-10-07.json](revision-maintenance-2026-10-07.json). All changes from this second follow-up are listed in [revision-manifest-2026-10-07.json](revision-manifest-2026-10-07.json), including unresolved OneDrive availability for the optional plotting install.
'''
    (OWN / 'README.md').write_text(readme, encoding='utf-8')
    notes = (OWN / 'SOURCE-NOTES.md').read_text(encoding='utf-8')
    notes = notes.replace('and the size/style discussion on printed page 167.',
        'and its persistence discussion on printed pages 187–188. The previous size/style attribution to printed page 167 was not verified and is withdrawn.')
    notes = notes.replace('That enclosing status governs this post-outcome comparison. The inherited label does not make it a predeclared endpoint.',
        'The separately saved `post-review-2026-10-07-01/results-corrected-label.json` changes that nested status to Exploratory; every statistic and the original file remain unchanged.')
    (OWN / 'SOURCE-NOTES.md').write_text(notes, encoding='utf-8')
    source = OWN / 'sources-review-2026-10-07.json'
    bibliography = json.loads(source.read_text(encoding='utf-8'))
    bibliography['caption_quote']['words'] = len(bibliography['caption_quote']['quote'].split())
    source.write_text(json.dumps(bibliography, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    registry = json.loads((OWN / 'registry-entry.json').read_text(encoding='utf-8'))
    registry['status'] = 'Exploratory'
    registry['outcome'] = registry['outcome'].replace('No sign\'s area association survives the amended grouped law across 17 sites',
        'Frozen area-law sign 520 q=0.044, minimum/maximum q=0.044/0.047; without the two cities q=0.387; amended-law q=0.223. No sign\'s area association survives the amended grouped law across 17 sites')
    registry['outcome'] += ' Second follow-up: the expanded 18-site area comparisons (4,452 readable objects) have minimum q 0.177/0.146/0.156/0.167 across four vectors. Period q 0.007 concerns 3C labels sharing 2200-1900 BCE; reviewer 3C-only p 0.0006. Unambiguous 3B 6/7 and 3C 112/123 do not contradict persistence. Original endpoints remain Frozen evaluation, amendments Exploratory, and arithmetic/reproduction checks Verified computation.'
    registry['remedy'] += ' Added the dated protocol amendment, separate site extents, four production/iconography precedents, code mapping audit, corrected nested-label copy and archived source metadata; consolidated identical checks and documented OneDrive plotting unavailability.'
    registry['challenge'] = registry['challenge'].replace('and Gaur codes remain unverified against photographs.',
        'and Gaur/Bull1 mappings have corroborating table/cult/publication checks but no complete image-checked codebook. The second Salūt TAG record disagrees with the published sherd.')
    registry['evidence'] += ['experiments/2026-10-06-sign-context-and-seals/' + name for name in [
        'REVIEW.md', 'site-extents-review-2026-10-07.json', 'sources-review-2026-10-07.json',
        'post-review-2026-10-07-01/area.json', 'post-review-2026-10-07-01/motif-mapping.json',
        'post-review-2026-10-07-01/results-corrected-label.json', 'revision-maintenance-2026-10-07.json']]
    (OWN / 'registry-entry.json').write_text(json.dumps(registry, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Living report, README, notes, bibliography and registry proposal corrected.')


if __name__ == '__main__':
    run()
