"""Build the Indus research map page from the experiment registry.

Usage: python -X utf8 -I build_map.py <repo_root> <output_html>
"""
import collections
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
OUT = Path(sys.argv[2])
REG = json.loads((ROOT / "knowledge/experiments/registry.json").read_text(encoding="utf-8"))
E = REG["experiments"]

# ---------------------------------------------------------------- lanes
LANES = [
    ("corpus", "Corpus, transcription and evidence census",
     "Pinned three GitHub exports (Lipi: 5,680 faces in ICIT/Wells codes; Mayig: 179 Mohenjo-daro seals), "
     "acquired the Helsinki 1979/1980/1982 volumes and CISI 1, built and corrected a 687-cell chart reference, "
     "and censused where Indus evidence is indexed. Automatic digitization of the 1979 corpus failed its frozen "
     "criteria; two-reader row verification failed its control screen. Nearly every sequence analysis still rests "
     "on one maintainer's transcription and its sign list. On 12 October two sign codings showed that graphic families improve prediction of rare signs, mostly through information already in the Wells order."),
    ("sequence", "Sequence statistics and restoration",
     "Local order beats position and metadata baselines (0.890 bits per sign nested; 0.848 on unique texts). "
     "Known-slot restoration rose from 33.8% to 41.2% top-one with Kneser-Ney plus GRU. Unknown gap counts failed "
     "against always-one, the learned class grammar lost to Markov, and the invented office-routing control shows "
     "the same gains, so these statistics do not separate language from nonlinguistic codes. On 12 October catalogued line divisions were found to fall between recurring units."),
    ("nulls", "Reference laws for copying and selection",
     "Exact enumerations of shuffling, copying, deduplication and recording-quality laws on small invented tables. "
     "Object-level references stay near nominal (5.4%) where record shuffles reject 15.9% of literal-copy "
     "populations. Useful for test design; no entry touches Indus inscriptions directly."),
    ("mapping", "Synthetic decipherment and symbol mapping",
     "Invented transition and administrative systems with known keys; graph, slot and mixture mappers, anchors, "
     "audits and active measurement. Structural scores alone leave mappings unidentified (720 equal relabellings); "
     "a known reference recovers 309 of 384 generated maps. No real script was used as the test bed."),
    ("numerals", "Numerals, quantities and metrology",
     "Fuls's 10/8/6 equations have four integer solutions; capacity fits trade unit against count; khipu controls "
     "replicate a published alignment. Dholavira 5-100 g weights give a 13.716 g unit. Susa, Oxus and South Indian "
     "sources were recovered and found to disagree. No Indus numeral value is tied to a counted object. On 12 October stroke values proved more tied to neighbouring signs than Ur III counts are."),
    ("objects", "Objects, context and physical use",
     "Source frames for 22 Harappa tablets (66 faces), 93 Lothal sealings and Kanmer pendants; a stamp-contact "
     "simulation; period, site-size and motif tests; whole-object carrier bundles. Copying and face roles explain "
     "the cross-face signal. Contact geometry and counts stay unresolved from available plates. On 12 October Harappa tablet texts were found to pair with their images within genre, with no detectable transfer from copper to seals."),
    ("meaning", "Meaning proposals and sign readings",
     "Review of Bonta's Indo-Aryan proposal (ordering facts reproduce; lexical-survival claims withdrawn), then a "
     "project catalogue assigning working meanings to all 713 codes from Sanskrit senses and pictures, adversarial "
     "pruning to seven families on nine codes, and an expansion to the 567 unreviewed codes now in progress. The published-claim tests of 12 October found that Yajnadevam's key scores 1.2 to 2.4 standard deviations above rearrangements of its own values, where a correct key on synthetic Indus-shaped corpora stands 27 to 72 clear."),
    ("known", "Comparisons with known record systems",
     "Totem poles, weather records, a Puruchuco khipu, and Sumerian, Akkadian, Egyptian and Linear B records. All "
     "eleven testable Bronze Age cohorts show ordering like IVS, and equality-pattern word fits cover 91-97% of IVS "
     "faces in every language. The comparisons calibrate how weak those tests are. On 12 October unsupervised segmentation and alternation were shown to be weak on readable scripts at Indus scale, and the closing asymmetry to change sign with unit and genre."),
    ("contact", "External contact and bilingual anchors",
     "Searched inspected contact objects for an Indus text paired with legible cuneiform; none found. Shu-ilishu's "
     "seal names a Meluhha interpreter without an Indus spelling. The Tell Jokha object was traced to a 2017 report "
     "figure; its registration and context remain unverified. The published-claim tests of 12 October found that West Asian and round Gulf-type seals use unusual orders of common signs."),
    ("continuity", "Later continuity and transmission",
     "Backward chronology from early historic scripts (no empty century in the broad record; a 400-1,600-year gap "
     "among well-dated rows), a resemblance baseline (an unrelated script matches Tamil Nadu graffiti about as often "
     "as Indus signs), early Indian institutions and memory, and a transmission study in progress."),
    ("settlement", "Settlement and landscape",
     "Paper 005 on survey gaps (72-record source register, 21 regions of interest), then Sentinel-2 and terrain "
     "screening of four blocks with eight review targets. No new site or national find total is claimed."),
    ("society", "Societal persistence",
     "A theory of minimum functions for long persistence, invented-law models of renewal and skill replacement, "
     "and 34 source-qualified Harappan observations of maintenance and changed use."),
    ("programme", "Programme, reviews and release",
     "Readiness and priority reviews, the field-recommendation survey, contribution inventories, multi-model "
     "coordination, the 18-page report, and the GitHub and Hugging Face release work."),
]
LANE_IDS = [l[0] for l in LANES]

LANE_OF = {}
def put(lane, *ids):
    for i in ids:
        LANE_OF[i] = lane

put("corpus", "ROOT-01", "ROOT-15", "ROOT-16", "ROOT-17", "ROOT-18", "ROOT-19", "DATASET-LANDSCAPE-01",
    "EVIDENCE-CENSUS-SITES-01", "EVIDENCE-CENSUS-SITES-PAK-AFG-01", "EVIDENCE-CENSUS-SITES-GUJARAT-01",
    "EVIDENCE-CENSUS-SITES-NORTH-INDIA-01", "EVIDENCE-CENSUS-SITES-ABROAD-01", "EVIDENCE-CENSUS-COLLECTIONS-01",
    "EVIDENCE-CENSUS-SYNTHESIS-01", "OBJECT-LEDGER-PILOT-01", "HELSINKI1979-DIGITIZATION-01",
    "HELSINKI1979-ROW-VERIFICATION-01", "HELSINKI1979-CHART-REFERENCE-AUDIT-01",
    "METHODS-font_fresh20_audit", "METHODS-font_geometry_sensitivity", "METHODS-font_pilot_audit")
put("sequence", "ROOT-02", "ROOT-03", "ROOT-04", "ROOT-05", "ROOT-06", "ROOT-07", "ROOT-08", "ROOT-11",
    "ROOT-12", "MARKOV-01", "MARKOV-02", "MARKOV-03", "MARKOV-04", "MARKOV-05", "MODERN-RESTORATION-01",
    "TWO-APPROACHES-CLASS-GRAMMAR-2026-10-11")
put("nulls", *[f"NULL-{i:02d}" for i in range(1, 12)])
put("mapping", *[f"CRYPTO-{i:02d}" for i in range(1, 12)], "NUM-02")
put("numerals", "ROOT-13", "ROOT-14", "PHYS-01", "PHYS-02", "KHI-01", "KHI-02", "KHI-03", "KHI-04", "KHI-05",
    "WEIGHT-METROLOGY-01", "REGIONNUM-01", "SUSA-SOURCE-02", "OXUS-SOURCE-02", "TN-STROKE-01", "TN-SOURCE-02",
    "HARP-SHORT-01", "METHODS-numerical_equalities")
put("objects", "ROOT-09", "ROOT-10", "CONTEXT-01", "ARCH-01", "ARCH-02", "ARCH-03", "KANMER-01", "KANMER-02",
    "GEOM-01", "LOTHAL-TRACE-01", "HARP-LOTHAL-SOURCE-02", "CHRONOLOGY-REGION-01", "SIGN-CONTEXT-SEALS-01",
    "ADMINISTRATIVE-BUNDLES-2026-10-11", "TWO-APPROACHES-PROGRAM-2026-10-11")
put("meaning", "BONTA-2025-LECTURES-FIRST-PASS-01", "BONTA-EXPLORATORY-SEMANTIC-EXTENSION-01",
    "BONTA-EXTENSION-ADVERSARIAL-2026-10-11", "PUBLIC-IMAGE-REASONING-SOURCE-AUDIT-01")
put("known", "BRONZE-AGE-DOCUMENTARY-COMPARISON-2026-10-12", "BRONZE-AGE-KNOWN-CATEGORY-CONTROLS-2026-10-12",
    "BRONZE-AGE-LEXICAL-PATTERN-AMBIGUITY-2026-10-12", "METHODS-totem_joint_nested", "METHODS-totem_nested",
    "METHODS-totem_templates")
put("contact", "COMM-02")
put("continuity", "BACKWARD-CHRONOLOGY-01", "RESEMBLANCE-BASELINE-01", "EARLY-INDIAN-INSTITUTIONS-2026-10-11",
    "EARLY-INDIAN-MEMORY-2026-10-11", "EARLY-INDIAN-CONTINUITY-PROGRAM-2026-10-11")
put("settlement", "SETTLEMENT-PROSPECTION-2026-10-11")
put("society", "SOCIETAL-PERSISTENCE-SURVEY-2026-10-11", "SOCIETAL-RENEWAL-MODEL-2026-10-11",
    "HARAPPAN-SERVICE-RENEWAL-2026-10-11", "SOCIETAL-PERSISTENCE-PROGRAM-2026-10-11")
put("programme", "ROOT-20", "READINESS-01", "PRIORITY-01", "FIELD-RECOMMENDATIONS-01", "BYPRODUCT-INVENTORY-01",
    "RESEARCH-PROGRAM-2026-10-06", "HF-PUBLIC-RELEASE-01", "GITHUB-PUBLIC-RELEASE-2026-10-11")
# Entries registered on 12 October after the first version of the map.
put("corpus", "SIGN-FAMILIES-2026-10-12")
put("objects", "IMAGE-TEXT-TABLETS-2026-10-12")
put("sequence", "LINE-BREAKS-SEGMENTATION-2026-10-12")
put("numerals", "NUMERAL-BEHAVIOUR-2026-10-12")
put("known", "REHEARSAL-SEGMENTATION-2026-10-12", "STRUCTURAL-TYPOLOGY-2026-10-12")
put("programme", "STRUCTURE-FIRST-PROGRAM-2026-10-12")
put("meaning", "PUBLISHED-KEY-READABILITY-UNICITY-2026-10-12", "PUBLISHED-KEY-SANSKRIT-LIKELIHOOD-2026-10-12",
    "KEY-ALLOGRAPH-HOMOPHONE-SUBSTITUTION-2026-10-12")
put("mapping", "KEY-CALIBRATION-POWER-SYNTHETIC-2026-10-12")
put("contact", "FOREIGN-FINDS-SEQUENCE-STATISTICS-2026-10-12")
for e in E:
    if e["id"].startswith("METHODS-") and e["id"] not in LANE_OF:
        LANE_OF[e["id"]] = "sequence"
    if e["id"] not in LANE_OF:
        LANE_OF[e["id"]] = "programme"

# ---------------------------------------------------------------- evidence classes
CLASSES = [
    ("measured", "New measurement on real Indus material"),
    ("negative", "Failed or inconclusive on real Indus material"),
    ("synthetic", "Invented or simulated data only"),
    ("known", "Other real record systems"),
    ("source", "Source audit, census or literature"),
    ("hypothesis", "Interpretive construction or theory"),
    ("infra", "Packaging, release or coordination"),
]
CLASS_OF = {}
def cls(c, *ids):
    for i in ids:
        CLASS_OF[i] = c

cls("measured", "ROOT-02", "ROOT-04", "ROOT-05", "ROOT-06", "ROOT-07", "MARKOV-01", "MARKOV-02", "MARKOV-03",
    "MODERN-RESTORATION-01", "HARP-SHORT-01", "LOTHAL-TRACE-01", "CHRONOLOGY-REGION-01", "SIGN-CONTEXT-SEALS-01",
    "WEIGHT-METROLOGY-01", "ADMINISTRATIVE-BUNDLES-2026-10-11", "ARCH-03")
cls("negative", "ROOT-03", "ROOT-08", "ROOT-09", "ROOT-10", "ROOT-11", "ROOT-17", "MARKOV-04", "MARKOV-05",
    "TWO-APPROACHES-CLASS-GRAMMAR-2026-10-11", "HELSINKI1979-DIGITIZATION-01", "HELSINKI1979-ROW-VERIFICATION-01",
    "RESEMBLANCE-BASELINE-01", "METHODS-gap_design_matched")
cls("synthetic", "ROOT-12", "ROOT-14", *[f"CRYPTO-{i:02d}" for i in range(1, 12)], "NUM-02",
    *[f"NULL-{i:02d}" for i in range(1, 12)], "PHYS-01", "PHYS-02", "KHI-03", "KHI-04", "KHI-05", "GEOM-01",
    "SOCIETAL-RENEWAL-MODEL-2026-10-11", "METHODS-workflow_templates")
cls("known", "KHI-01", "KHI-02", "BRONZE-AGE-DOCUMENTARY-COMPARISON-2026-10-12",
    "BRONZE-AGE-KNOWN-CATEGORY-CONTROLS-2026-10-12", "BRONZE-AGE-LEXICAL-PATTERN-AMBIGUITY-2026-10-12",
    "METHODS-totem_joint_nested", "METHODS-totem_nested", "METHODS-totem_templates")
cls("source", "ROOT-01", "ROOT-13", "ROOT-15", "ROOT-16", "ROOT-18", "ROOT-19", "CONTEXT-01", "ARCH-01", "ARCH-02",
    "COMM-02", "KANMER-01", "KANMER-02", "REGIONNUM-01", "TN-STROKE-01", "OXUS-SOURCE-02", "SUSA-SOURCE-02",
    "TN-SOURCE-02", "HARP-LOTHAL-SOURCE-02", "DATASET-LANDSCAPE-01", "EVIDENCE-CENSUS-SITES-01",
    "EVIDENCE-CENSUS-SITES-PAK-AFG-01", "EVIDENCE-CENSUS-SITES-GUJARAT-01", "EVIDENCE-CENSUS-SITES-NORTH-INDIA-01",
    "EVIDENCE-CENSUS-SITES-ABROAD-01", "EVIDENCE-CENSUS-COLLECTIONS-01", "EVIDENCE-CENSUS-SYNTHESIS-01",
    "BACKWARD-CHRONOLOGY-01", "FIELD-RECOMMENDATIONS-01", "OBJECT-LEDGER-PILOT-01",
    "HELSINKI1979-CHART-REFERENCE-AUDIT-01", "BONTA-2025-LECTURES-FIRST-PASS-01",
    "PUBLIC-IMAGE-REASONING-SOURCE-AUDIT-01", "SETTLEMENT-PROSPECTION-2026-10-11",
    "SOCIETAL-PERSISTENCE-SURVEY-2026-10-11", "HARAPPAN-SERVICE-RENEWAL-2026-10-11", "READINESS-01",
    "PRIORITY-01", "METHODS-font_fresh20_audit", "METHODS-font_geometry_sensitivity", "METHODS-font_pilot_audit",
    "METHODS-numerical_equalities")
cls("hypothesis", "BONTA-EXPLORATORY-SEMANTIC-EXTENSION-01", "BONTA-EXTENSION-ADVERSARIAL-2026-10-11",
    "TWO-APPROACHES-PROGRAM-2026-10-11", "EARLY-INDIAN-INSTITUTIONS-2026-10-11", "EARLY-INDIAN-MEMORY-2026-10-11",
    "EARLY-INDIAN-CONTINUITY-PROGRAM-2026-10-11", "SOCIETAL-PERSISTENCE-PROGRAM-2026-10-11")
cls("infra", "ROOT-20", "BYPRODUCT-INVENTORY-01", "RESEARCH-PROGRAM-2026-10-06", "HF-PUBLIC-RELEASE-01",
    "GITHUB-PUBLIC-RELEASE-2026-10-11")
cls("measured", "SIGN-FAMILIES-2026-10-12", "IMAGE-TEXT-TABLETS-2026-10-12", "LINE-BREAKS-SEGMENTATION-2026-10-12",
    "NUMERAL-BEHAVIOUR-2026-10-12", "STRUCTURAL-TYPOLOGY-2026-10-12", "FOREIGN-FINDS-SEQUENCE-STATISTICS-2026-10-12",
    "KEY-ALLOGRAPH-HOMOPHONE-SUBSTITUTION-2026-10-12")
cls("known", "REHEARSAL-SEGMENTATION-2026-10-12")
cls("negative", "PUBLISHED-KEY-READABILITY-UNICITY-2026-10-12", "PUBLISHED-KEY-SANSKRIT-LIKELIHOOD-2026-10-12")
cls("synthetic", "KEY-CALIBRATION-POWER-SYNTHETIC-2026-10-12")
cls("infra", "STRUCTURE-FIRST-PROGRAM-2026-10-12")
for e in E:
    if e["id"].startswith("METHODS-") and e["id"] not in CLASS_OF:
        CLASS_OF[e["id"]] = "measured"
    if e["id"] not in CLASS_OF:
        CLASS_OF[e["id"]] = "source"

# ---------------------------------------------------------------- METHODS outcomes (registry text is a pointer)
def methods_outcome(i):
    if any(k in i for k in ("nested", "pilot", "raw_primary", "collapsed_primary")):
        return ("Structural-gain variant. Nested selection gives 0.890 bits per noninitial sign (0.848 on unique "
                "texts); the full refitting null has 0 exceedances in 1,000.")
    if any(k in i for k in ("classaware", "joint_transfer", "adjusted_max")):
        return ("Substitution-family variant. Multi-record disjoint-class transfer 5 versus null mean 5.005 "
                "(p about 0.54); unique population p about 0.003; W176/W904 family-wise p about 0.13.")
    if "workflow" in i:
        return "Invented office-routing codes also give a 0.631-bit Markov-over-template gain."
    if "templates" in i:
        return "Independent-slot templates gain 0.142 bits over the independent baseline; Markov remains 0.748 bits better."
    if "totem" in i:
        return "Totem poles: 180 units, about 43.7% out-of-vocabulary; small fitted gain, unexceptional under the reference."
    if "font" in i:
        return "Audit of the printed-row recognition pilot or the fresh20 endpoint and its geometry repair."
    if "gap" in i:
        return "Design-matched gap-count prior: 46.3% versus 51.1% for always-one."
    if "numerical" in i:
        return "Exact integer solutions to Fuls's equations: four; 10/8/6 needs an extra range restriction."
    return "Variant endpoint; see methods findings."

def date_of(e):
    for p in e["evidence"]:
        m = re.search(r"2026-10-(\d\d)", p)
        if m:
            return f"Oct {int(m.group(1))}"
    if e["id"].startswith(("ROOT", "METHODS")):
        return "Oct 1"
    return "Oct 2"

def short(text, n):
    text = " ".join(text.split()).replace("�", "–")
    text = re.sub(r"(\d)\?(\d)", lambda m: m.group(1) + "–" + m.group(2), text)
    if len(text) <= n:
        return text
    cut = text[:n]
    stop = max(cut.rfind(". "), cut.rfind("; "))
    if stop > n * 0.55:
        return cut[:stop + 1]
    return cut[: cut.rfind(" ")] + " ..."

rows = []
for e in E:
    i = e["id"]
    outcome = methods_outcome(i) if i.startswith("METHODS-") else short(e["outcome"], 300)
    rows.append(dict(id=i, lane=LANE_OF[i], cls=CLASS_OF[i], date=date_of(e), status=e["status"],
                     q=short(e["question"], 210), o=outcome, ev=e["evidence"][0] if e["evidence"] else ""))

UNREG = [
    dict(id="PACKAGE-Q-BONTA-REVIEW", lane="meaning", cls="negative", date="Oct 8", status="unregistered; reviewed",
         q="Do Bonta's ordering, fish-adjacency and lexical claims hold under conditional tests?",
         o="Jar final in 70.07% of tokens and fish adjacency well above shuffles reproduce. Lexical mapping-survival "
           "claims were withdrawn because values were derived from the same dictionary search.",
         ev="experiments/2026-10-08-bonta-review/REPORT.md"),
    dict(id="EXTERNAL-ANCHOR-AUDIT", lane="contact", cls="source", date="Oct 1", status="unregistered; literature",
         q="Does any inspected contact object pair an Indus text with legible cuneiform?",
         o="No corresponding Indus and cuneiform texts found. Shu-ilishu's seal identifies an interpreting role without an Indus spelling.",
         ev="research/literature/external_phonetic_anchor_audit.md"),
    dict(id="ANCHOR-EXPANSION-2026-10-12", lane="meaning", cls="hypothesis", date="Oct 12", status="in progress",
         q="Can the reviewed anchors be extended to the 567 unreviewed codes and tested on complete inscriptions?",
         o="Context frame rebuilt (1,859 strings, 577 observed codes); visual-family map and Sanskrit sense records under construction.",
         ev="experiments/2026-10-12-anchor-expansion/PROTOCOL.md"),
    dict(id="SEMANTIC-SIGN-COMPARISON-2026-10-12", lane="meaning", cls="hypothesis", date="Oct 12", status="in progress",
         q="How do signs carrying the proposed meanings compare with signs for the same meanings in Sumerian, Egyptian and Linear B?",
         o="Protocol and acquisition plan written; inputs frozen.",
         ev="experiments/2026-10-12-semantic-sign-comparison/PROTOCOL.md"),
    dict(id="SATELLITE-PROSPECTION-2026-10-12", lane="settlement", cls="measured", date="Oct 12", status="unregistered; two output versions",
         q="Do Sentinel-2, terrain and published former-channel data identify reviewable surface targets in selected blocks?",
         o="Four blocks screened with multi-date scenes; eight review targets with rival explanations. No site confirmed.",
         ev="experiments/2026-10-12-satellite-prospection/PROTOCOL.md"),
    dict(id="TRANSMISSION-HYPOTHESIS-2026-10-12", lane="continuity", cls="hypothesis", date="Oct 12", status="in progress",
         q="Which routes (local, inherited, contact, reinvention, recombination) explain particular early Indian practices?",
         o="Protocol, source and method controls, material and textual studies under way; report not yet written.",
         ev="experiments/2026-10-12-transmission-hypothesis/README.md"),
]
for u in UNREG:
    u["unreg"] = True
rows.extend(UNREG)

counts = collections.Counter(r["cls"] for r in rows)
lane_counts = {l: collections.Counter(r["cls"] for r in rows if r["lane"] == l) for l in LANE_IDS}
max_lane = max(sum(c.values()) for c in lane_counts.values())
n_reg = len(E)
n_all = len(rows)
print("class counts", dict(counts), "registered", n_reg, "all", n_all)
print({l: sum(c.values()) for l, c in lane_counts.items()})

# ---------------------------------------------------------------- HTML helpers
esc = lambda s: html.escape(str(s), quote=True)

def stacked(counter, total_scale):
    segs = []
    for c, _ in CLASSES:
        n = counter.get(c, 0)
        if n:
            w = 100 * n / total_scale
            segs.append(f'<span class="seg c-{c}" style="width:{w:.3f}%" title="{esc(dict(CLASSES)[c])}: {n}"></span>')
    return "".join(segs)

effort_rows = []
for lid, name, _ in LANES:
    c = lane_counts[lid]
    effort_rows.append(
        f'<div class="erow"><span class="elabel">{esc(name)}</span>'
        f'<span class="etrack">{stacked(c, max_lane)}</span><span class="enum">{sum(c.values())}</span></div>')

legend = "".join(
    f'<button type="button" class="chip c-{c}" data-cls="{c}" aria-pressed="true" id="chip-{c}">'
    f'<span class="dot"></span>{esc(label)} <span class="cnt">{counts.get(c, 0)}</span></button>'
    for c, label in CLASSES)

lane_html = []
for lid, name, summary in LANES:
    items = [r for r in rows if r["lane"] == lid]
    items.sort(key=lambda r: (int(r["date"].split()[1]), r["id"]))
    li = []
    for r in items:
        tag = ' <span class="unreg">not in registry</span>' if r.get("unreg") else ""
        li.append(
            f'<li class="entry" data-cls="{r["cls"]}" data-text="{esc((r["id"] + " " + r["q"] + " " + r["o"]).lower())}">'
            f'<div class="emeta"><span class="eid">{esc(r["id"])}</span><span class="edate">{esc(r["date"])}</span>'
            f'<span class="tag c-{r["cls"]}"><span class="dot"></span>{esc(dict(CLASSES)[r["cls"]])}</span>{tag}</div>'
            f'<p class="eq">{esc(r["q"])}</p><p class="eo">{esc(r["o"])}</p>'
            f'<p class="eev"><code>{esc(r["ev"])}</code> · {esc(r["status"])}</p></li>')
    c = lane_counts[lid]
    lane_html.append(
        f'<section class="lane" id="lane-{lid}" data-lane="{lid}"><div class="lanehead"><h3>{esc(name)}</h3>'
        f'<span class="lanecount"><span class="shown">{len(items)}</span> of {len(items)}</span></div>'
        f'<div class="minibar">{stacked(c, sum(c.values()))}</div><p class="lanesum">{esc(summary)}</p>'
        f'<details id="det-{lid}"><summary>Show the {len(items)} entries</summary><ul class="entries">{"".join(li)}</ul></details></section>')

tpl = (Path(__file__).parent / "map_template.tpl").read_text(encoding="utf-8")
page = (tpl.replace("{{EFFORT}}", "".join(effort_rows))
           .replace("{{LEGEND}}", legend)
           .replace("{{LANES}}", "".join(lane_html))
           .replace("{{N_REG}}", str(n_reg))
           .replace("{{N_ALL}}", str(n_all))
           .replace("{{N_SYN}}", str(counts["synthetic"]))
           .replace("{{N_MEAS}}", str(counts["measured"]))
           .replace("{{N_SRC}}", str(counts["source"]))
           .replace("{{N_NEG}}", str(counts["negative"]))
           .replace("{{N_HYP}}", str(counts["hypothesis"]))
           .replace("{{N_INFRA}}", str(counts["infra"]))
           .replace("{{N_KNOWN}}", str(counts["known"]))
           .replace("{{N_UNREG}}", str(len(UNREG))))
OUT.write_text(page, encoding="utf-8")
print("wrote", OUT, len(page))
print("methods measured", sum(1 for r in rows if r["id"].startswith("METHODS-") and r["cls"]=="measured"))
