"""Build the local, self-contained HTML explanation of the preserved findings.

No research is rerun. Photographs remain local because their rights are unresolved.
Run from any directory with Python 3.13.
"""
from pathlib import Path
import base64
import csv
import hashlib
import html
import json
import mimetypes

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
OUT = ROOT / "output/indus-findings-2026-10-22.html"
ASSETS = ROOT / "output/indus-findings-assets"
PHOTO = ROOT / "data/lipi/public/seal_images"
ASSETS.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "audit": ("Literature and publication audit, 22 October 2026", "experiments/2026-10-22-field-novelty-review/REPORT.md"),
    "data": ("Object inventory and data gaps", "knowledge/DATA.md"),
    "cisi": ("CISI basic-data extraction and coverage", "experiments/2026-10-13-cisi-basic-data-full/README.md"),
    "images": ("Face–image index and unit audit", "experiments/2026-10-13-image-index-and-units/README.md"),
    "later": ("Later published finds: source inventory", "experiments/2026-10-21-post-catalogue-finds/README.md"),
    "units": ("Seal-legend units: report and frozen outputs", "experiments/2026-10-20-seal-legend-units/REPORT.md"),
    "replay": ("Segmentation bench replay, 22 October", "experiments/2026-10-22-field-novelty-review/segmentation-replay.json"),
    "identity": ("Seal-text identity and circulation", "experiments/2026-10-12-seal-text-identity/REPORT.md"),
    "time": ("Harappa legend periods", "experiments/2026-10-20-harappa-legend-periods/REPORT.md"),
    "fish": ("Fish contexts: program report", "experiments/2026-10-20-fish-context/PROGRAM-REPORT.md"),
    "birth": ("Birth-star names: discovery and frozen predictions", "experiments/2026-10-21-birth-star-names/REPORT.md"),
    "birthfreeze": ("Birth-star bench freeze v1", "experiments/2026-10-21-birth-star-names/freeze-v1.json"),
    "key": ("Paper 006: Sanskrit-key calibration", "papers/006-sanskrit-key-calibration/manuscript.md"),
    "rebus": ("Unselected rebus-pair tests", "experiments/2026-10-22-rebus-blind-templates/REPORT.md"),
    "winslow": ("Cross-dictionary rebus test", "experiments/2026-10-22-rebus-winslow/REPORT.md"),
    "restore": ("Modern restoration: report and limitations", "experiments/2026-10-06-modern-restoration/REPORT.md"),
    "copies": ("Paper 002: conditional reference laws", "papers/002-conditional-reference-laws/manuscript.md"),
    "numbers": ("Paper 003: physical observations", "papers/003-physical-observations/manuscript.md"),
    "models": ("Paper 004: reference-model selection", "papers/004-reference-model-selection/manuscript.md"),
    "towns": ("Independent town-orientation verification", "experiments/2026-10-21-town-orientations-verification/REPORT.md"),
    "rights": ("Redistribution and source rights", "knowledge/provenance/REDISTRIBUTION.md"),
}

assets = []
def picture(name, alt, cls=""):
    path = ASSETS / name if name == "seal-use-illustration.png" else PHOTO / name
    raw = path.read_bytes()
    assets.append({"file": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": hashlib.sha256(raw).hexdigest(), "alt": alt})
    data = base64.b64encode(raw).decode()
    return f'<img class="{cls}" src="data:{mimetypes.guess_type(name)[0]};base64,{data}" alt="{html.escape(alt)}">'

def sources(*keys):
    return " · ".join(f'<a href="../{SOURCES[k][1]}" target="_blank" rel="noopener">{SOURCES[k][0]}</a>' for k in keys)

def explain(meaning, society, decoding):
    return f'<div class="explain"><div><h3>In simple words</h3><p>{meaning}</p></div><div><h3>If true, for society</h3><p>{society}</p></div><div class="decoding"><h3>Closer to reading?</h3><p>{decoding}</p></div></div>'

def bar(label, value, maximum=100, shown=None, color="teal"):
    return f'<div class="barrow"><div class="barlabel">{label}<strong>{shown if shown is not None else value}</strong></div><div class="track"><div class="bar {color}" style="width:{value / maximum * 100}%"></div></div></div>'

def note(text):
    return f'<p class="note">{text}</p>'

slides = []
def add(kicker, title, subtitle, body, refs=(), cls="", takeaway=""):
    n = len(slides) + 1
    slides.append({"title": title, "html": f'''<section class="slide {cls}" id="slide-{n}" aria-label="Slide {n}: {html.escape(title.replace('<br>', ' '))}" tabindex="-1">
      <header><div class="eyebrow">{kicker}</div><h1>{title}</h1><p class="subtitle">{subtitle}</p></header>
      <div class="body">{body}</div>
      <footer><div class="source">{sources(*refs)}</div><div class="folio">INDUS RESEARCH · 22 OCT 2026 <b>{n:02}</b></div></footer>
    </section>''', "sources": list(refs)})

cover = picture("seal-use-illustration.png", "AI-generated imagined Indus workshop: a seal is used with a tied bundle. This is an illustration, not archaeological evidence.")
add("A visual guide to our findings", "What are the<br>Indus signs<br>telling us?", "What we have measured, what it could mean,<br>and what still stands between us and a reading.",
    f'<div class="cover-art">{cover}</div><div class="cover-bottom"><p>Plain-language research briefing</p><span>Use ← → or the buttons below</span></div><div class="image-disclosure">Imagined seal-use scene · AI illustration<br>Objects, signs and setting are illustrative.</div>', ("audit",), "cover")

add("Start here", "We can study a message before we can read it.", "Our strongest progress concerns how inscriptions are organized and how to test a proposed reading.",
    '''<div class="reading-grid">
      <div><span class="step-number">01</span><h2>Find the object</h2><p>Which photograph, museum record and excavation entry belong together?</p><strong class="status">Substantial data work</strong></div>
      <div><span class="step-number">02</span><h2>Find the pattern</h2><p>Which signs go together? Where does a group end? What changes across sites or layers?</p><strong class="status">Measurable progress</strong></div>
      <div><span class="step-number">03</span><h2>Find the meaning</h2><p>Does a group name a person, office, commodity, number or something else?</p><strong class="status clay-text">Hypotheses to test</strong></div>
      <div><span class="step-number">04</span><h2>Read new texts</h2><p>Can fixed sound or meaning assignments predict an unseen inscription?</p><strong class="status clay-text">Still to be achieved</strong></div>
    </div><div class="wide-callout">We have no authenticated translation. A useful finding can still tell us where to look, what to compare and which proposed readings lack support.</div>''', ("audit",))

add("Finding 1 · Reconnecting the evidence", "A sign becomes more useful when we know its object.", "We are joining photographs, museum numbers and excavation records into traceable object records.",
    '<div class="columns"><div><div class="metric-pair"><div><b>4,695</b><span>provisional object families</span></div><div><b>8,722</b><span>catalogue photograph crops</span></div></div><h3 class="chart-title">Museum-number coverage in the combined records</h3>'
    + bar("At least one definite museum number", 44.3, shown="44.3%")
    + bar("Including uncertain digits", 52.2, shown="52.2%", color="clay")
    + note("An object family is our current grouping of records, pending a full identity audit. Coverage means a field is present; its accuracy still needs checking. CISI 2 has 2,870 unresolved transcription disagreements.")
    + '</div>' + explain("We can connect a short string of signs to a real object and its history.", "Findspot, material and object type may reveal who used inscriptions and in which activities.", "This creates the evidence needed to test meanings against real contexts. It does not supply a sound value by itself.") + '</div>', ("data", "cisi", "images"))

add("Finding 2 · The corpus is still incomplete", "Published finds can give us fresh tests.", "Our later-find inventory brings scattered excavation publications into one searchable record.",
    '''<div class="columns"><div><div class="hero-number">301</div><h2>definite post-catalogue objects<br>recorded across 21 sites</h2><div class="range-block"><span>Estimated missing from the pinned local corpus</span><b>55–291</b><p>Using strict identity matches. Exploratory context joins narrow the range to 55–224.</p></div>'''
    + note("These are already published finds newly collated by this project. The range is wide because aliases and incomplete descriptions make identity uncertain.")
    + '</div>' + explain("There are still objects to locate and match, even before anyone excavates another site.", "Better coverage may change which regions, periods or kinds of activity seem most prominent.", "Objects never used to build a theory let us test its predictions fairly. A new photograph of an already studied object is not a fresh test.") + '</div>', ("later", "audit"))

add("Finding 3 · Where do sign groups divide?", "Physical line breaks give us places to test a boundary.", "A boundary is a possible end of one recurring group and the start of another.",
    '<div class="columns photo-columns"><figure>' + picture("H-60_imp_a.jpg", "CISI H-60 catalogue impression. Several signs occupy the upper row; two signs sit beneath its right end.")
    + '<figcaption>H-60, Harappa. The photograph shows signs arranged on two levels above the animal. The plate audit identifies 4 + 2 signs.</figcaption></figure><div><div class="inline-stat"><b>27 / 34</b><span>required line divisions found<br>in the primary 33-face test</span></div>'
    + bar("Required line divisions found", 79.4, shown="79.4%")
    + bar("Cuts made at other positions", 7.65, shown="7.65%", color="clay")
    + note("This is a test of visible line divisions. It is not 79% accuracy at finding all words: we do not know every true word boundary.")
    + '<p class="plain">In simple words: the model often puts a break where the writer moved to another line. The next question is whether those breaks separate reusable parts of a message.</p></div></div>', ("units", "replay"))

add("Interpreting finding 3", "Some inscriptions may be assembled from recurring parts.", "This makes a short formula a useful working model for some seal texts.",
    '''<div class="columns"><div class="example-panel"><span class="example-label">Modern analogy only · not an Indus translation</span><div class="word-example"><span>MAYA</span><span>POTTER</span></div><div class="word-example"><span>RAVI</span><span>POTTER</span></div><div class="word-example"><span>MAYA</span><span>TRADER</span></div><p>Repeated positions can reveal “a changing part” and “a shared part” before we know what either means.</p></div>'''
    + explain("A sequence may contain units that recur in other inscriptions, rather like reusable pieces of a label.", "If the units encode a holder and a role, seals could identify people or groups authorized to act in a recognized capacity.", "Finding units reduces the number of ways to split a text. Assigning “name” or “role” still needs evidence from use and context.")
    + '</div><div class="small-callout">Next decisive step: test the frozen unit inventory on 50 unread seals, with the scoring rule fixed in advance.</div>', ("units", "identity"))

add("Finding 4 · Long texts and short repeats", "Long seal texts look individual; some short texts travel across sites.", "We counted repeated inscriptions in 1,430 clean, single-line seals from named sites.",
    '''<div class="columns"><div><div class="number-line"><b>445</b><p>texts with six or more signs<br><strong>None repeated in this selected sample.</strong></p></div><div class="number-line"><b>65</b><p>different texts that recur<br>on 174 seals in total</p></div><div class="number-line"><b>41</b><p>of those 65 recurring texts<br>appear at more than one site</p></div>'''
    + note("The primary test did not find convincing excess local concentration (p = 0.31). A non-repeating text is not, by itself, a personal name.")
    + '</div>' + explain("Long strings distinguish objects well. Some shorter strings belong to a shared stock.", "A plausible model is individual identifiers combined with common roles, institutions or formulas used across settlements.", "This helps choose among functions a text could have. It does not tell us which sign says “person”, “merchant” or any particular name.") + '</div>', ("identity",))

add("A concrete example", "The same text can appear on different physical seals.", "Text matching and object matching answer different questions.",
    '<div class="columns"><div><div class="photo-pair"><figure>' + picture("M-895_A.jpg", "CISI M-895 A, photograph of the seal face.") + '<figcaption>M-895: seal face</figcaption></figure><figure>' + picture("M-895_imp_a.jpg", "CISI M-895 a, catalogue impression showing the reversed sign order.") + '<figcaption>M-895: catalogue impression</figcaption></figure></div><p class="plain">The two images above show one seal and its impression. The study also identifies 10 Lothal sealings with the same text as M-895, but made by distinct seal dies.</p>'
    + note("A sealing is clay or another material carrying a stamp impression. A die is the engraved stamping surface. The Lothal sealings are not pictured here.")
    + '</div>' + explain("Several people or workshops could use the same wording on separately made stamps.", "Shared wording could reflect a common office, entitlement or convention across settlements. It does not establish a single central government.", "Matching text to actual stamping practice narrows its possible job. It also prevents us from mistaking one repeated record for many independent observations.") + '</div>', ("identity", "images"))

add("Finding 5 · Inscriptions changed through time", "Later relative layers contain longer texts in this Harappa sample.", "The study compares seals within excavation trenches at Mound F.",
    '<div class="columns"><div><h3 class="chart-title">Average signs per complete inscription</h3>'
    + bar("Earlier third of relative layers", 4.0, 6, "4.0")
    + bar("Middle third", 4.8, 6, "4.8")
    + bar("Later third", 5.3, 6, "5.3")
    + note("105 complete texts within a study of 173 seals and six trench frames. These are relative layer groups, not securely assigned calendar dates. The layer-to-period mapping needs an archaeological audit.")
    + '</div>' + explain("The average inscription becomes longer as we move through the retained sequence of layers.", "If the sequence is sound, users may have added more information or changed their labeling conventions over generations.", "A reading must fit the period in which its signs were used. Dating can separate an early form from a later one, but length alone cannot prove growing bureaucracy.") + '</div>', ("time", "audit"))

add("Finding 6 · Fish-shaped signs have ordering rules", "Some combinations occur in one order much more often than the reverse.", "“Fish” is a description of the shape. Its meaning remains a separate question.",
    '<div class="columns"><div><figure class="wide-photo">' + picture("M-414_imp_a.jpg", "CISI M-414 catalogue impression with fish-shaped signs and a central sign.")
    + '<figcaption>M-414: a real catalogue example of fish-shaped signs. The chart summarizes the wider study, not this object alone.</figcaption></figure>'
    + '<div class="stacked" aria-label="43 supporting groups, 8 reversed groups, 2 tied groups"><span style="flex:43">43</span><span class="clay" style="flex:8">8</span><span class="neutral" style="flex:2">2</span></div><div class="legend">43 support the proposed order · 8 reverse · 2 tie</div>'
    + '</div>' + explain("The fish family is organized: sign order is constrained in these comparisons.", "A fixed order could reflect names, categories, titles or another conventional sequence. It gives no direct evidence that the texts concern fish, stars or trade.", "An eventual reading must explain the ordering. That is a useful constraint on guesses, even while the sounds remain unknown.") + '</div>', ("fish",))

add("A bold hypothesis · Still awaiting its fresh test", "Could fish groups be names connected with birth stars?", "A birth-star name comes from the star group associated with a person’s birth. We have not confirmed this practice for Indus people.",
    '<div class="columns"><div><h3 class="chart-title">Comparison with a known naming system</h3>'
    + bar("Indus legends with a fish run in the proposed name position", 35.6, 40, "35.6%")
    + bar("Star-derived names among later Brāhmī donors", 7.5, 40, "5.5–7.5%", "clay")
    + note("Brāhmī is a later, readable Indian script. The two samples are about 2,000 years apart. This comparison does not show direct continuity. Puṣya supplies 19 of 42 securely identified star-name occurrences in the later sample.")
    + '</div>' + explain("A small stock of common fish groups could fit a naming system with a limited list of names. Ordinary sign categories can fit it too.", "If a birth-star reading were independently supported, it would connect personal identity with sky-related naming practices.", "Current support is weak: the recorded credence is 3%. The next test rejects the closed-list claim if over 15% of fresh fish runs fall outside the discovery inventory.") + '</div>', ("birth", "birthfreeze"))

add("Finding 7 · Testing a proposed Sanskrit key", "A convincing-looking word can be too easy to find.", "We evaluated one complete proposed key on 1,859 distinct, complete Indus inscriptions.",
    '''<div class="columns"><div class="example-panel"><span class="example-label">English analogy · not the Sanskrit experiment</span><div class="letter-example">C T</div><div class="choice-words">CAT &nbsp; COT &nbsp; CUT</div><p>If we are allowed to supply missing vowels, one consonant pattern can fit several words.</p><div class="stat-banner"><b>92–100%</b><span>of random consonant strings passed the emulated dictionary rule in its tested length range</span></div></div>'''
    + explain("A rule that accepts almost anything cannot tell us whether a specific reading is right.", "This key does not provide strong enough evidence to identify the language or the linguistic identity of Indus people.", "The contribution is a better test: compare the full key with matched alternatives and check that a known correct key would stand out. The result concerns this submitted key and scoring rules.") + '</div>', ("key", "audit"))

add("Finding 8 · Testing picture-to-word puns", "A few attractive word matches need a fair comparison.", "A rebus uses a pictured thing for a similar-sounding word. “Sun” standing for “son” is an English analogy.",
    '<div class="columns"><div><div class="rebus-example"><span>SUN</span><b>sounds like</b><span>SON</span></div><h3 class="chart-title">Unselected adjacent pairs in the current test</h3>'
    + bar("Observed dictionary matches", 9, 10, "9 of 38")
    + bar("Average expected under the comparison", 4.97, 10, "4.97", "clay")
    + note("6.7% of random whole keys reach nine matches. Word-frequency matching and dictionary parsing need repair. Earlier four-link tests gave favorable evidence and remain part of the record.")
    + '</div>' + explain("There are more matches than the current comparison expects, but the margin and the measurement problems do not settle the claim.", "If a fixed rebus key predicted new texts reliably, it could identify a language and the cultural vocabulary encoded by the signs.", "This study gives a way to test that possibility. No proposed fish/star sound value is authenticated by these results.") + '</div>', ("rebus", "winslow", "audit"))

add("Finding 9 · Predicting a missing sign", "The surrounding signs can help us guess what is missing.", "Restoration means proposing a lost sign; it is different from translating the inscription.",
    '''<div class="columns"><div class="example-panel"><span class="example-label">Everyday analogy</span><div class="sentence-example">The cat sat<br>on the <span>___</span>.</div><p>“Mat” is plausible because familiar sequences constrain what comes next. The same idea can rank possible sign shapes.</p><div class="stat-banner"><b>≈ 41%</b><span>reported first-choice success in one held-out masking experiment; model ranking remains provisional</span></div></div>'''
    + explain("Models learn recurring sign sequences and offer candidates when a sign is deliberately hidden.", "Better reconstructions may recover details that let us compare labels, people or activities across damaged objects.", "The immediate gain is recovering text structure. A corrected evaluation must keep related objects together; real damage may also hide how many signs were lost.") + '</div>', ("restore", "audit"))

add("Finding 10 · Counting independent evidence", "Copies can make a weak pattern look convincing.", "A simulation shows why several records of the same object must stay together during a chance test.",
    '<div class="columns"><div><h3 class="chart-title">False alarms in 1,000 simulated populations</h3>'
    + bar("Treat copied records as independent", 15.9, 20, "15.9%", "clay")
    + bar("Keep each object’s copies together", 5.4, 20, "5.4%")
    + bar("Intended false-alarm rate", 5, 20, "5.0%", "neutral")
    + note("These percentages come from a controlled simulation, not from counting false historical claims. A false alarm means a test reports a pattern when its chance model generated the data.")
    + '</div>' + explain("Ten photographs of one seal still give us one physical object. Treating them as ten separate witnesses exaggerates the evidence.", "This protects social interpretations from being driven by repeated publication of a few objects.", "It makes tests of every reading more trustworthy. It is a methods contribution, with no new sound or meaning assigned to a sign.") + '</div>', ("copies", "audit"))

add("Finding 11 · What numerical patterns cannot tell us alone", "Knowing a ratio is not the same as knowing the amount.", "Known-answer experiments help identify which outside observations a decoding needs.",
    '''<div class="columns"><div class="example-panel"><span class="example-label">Invented arithmetic example</span><div class="equation">A = B + B</div><table class="mini-table"><tr><th>Possible values</th><th>A</th><th>B</th></tr><tr><td>Reading 1</td><td>2</td><td>1</td></tr><tr><td>Reading 2</td><td>20</td><td>10</td></tr><tr><td>Reading 3</td><td>200</td><td>100</td></tr></table><p>All three obey the same relationship. An actual counted quantity could fix the scale.</p></div>'''
    + explain("Patterns can show that one value is twice another while leaving the units unknown.", "If inscriptions record quantities, links to contents, weights or repeated transactions could reveal how goods were accounted for.", "The experiments specify the missing evidence to seek. They do not establish numerical values for Indus signs. A real object-to-quantity link is the crucial next step.") + '</div>', ("numbers", "models", "audit"))

add("Related archaeology · A useful unresolved result", "Town layouts have not established a star-based system.", "Independent verification reproduced the astronomical calculations but exposed gaps in orientation and dating evidence.",
    '''<div class="columns"><div><table class="evidence-table"><thead><tr><th>Check</th><th>What happened</th></tr></thead><tbody><tr><td>Astronomical calculations</td><td>Reproduced closely</td></tr><tr><td>Open satellite measurements</td><td>Only two towns usable</td></tr><tr><td>Lothal direction</td><td>Sources disagree by about 2°</td></tr><tr><td>General star-setting claim</td><td>Undecided</td></tr><tr><td>Specific Pleiades version</td><td>Fails the stated test</td></tr></tbody></table></div>'''
    + explain("We can calculate where a star would set, but that does not show why builders chose a street direction.", "If a sky-based planning rule were demonstrated, it could reveal shared surveying knowledge or ritual practice. Present measurements do not establish that rule.", "This offers no direct sign reading. Any link between urban alignment and fish/star interpretations needs independent evidence on both sides.") + '</div>', ("towns",))

add("Putting the observations together", "A society of shared conventions and distinctive identities?", "Our strongest working interpretation is that some seal texts identify a holder within a shared system of roles or formulas.",
    '''<table class="synthesis-table"><thead><tr><th>What we observe</th><th>What it could mean for society</th><th>What would decide it</th></tr></thead><tbody>
    <tr><td>Long strings rarely repeat</td><td>People, households or groups distinguish themselves</td><td>Texts consistently tied to particular holders or contexts</td></tr>
    <tr><td>Short strings recur across sites</td><td>Some roles or conventions are recognized widely</td><td>Repeated wording with matching documented uses</td></tr>
    <tr><td>Recurring groups and endings</td><td>Messages use established formats</td><td>The same units predict new inscriptions</td></tr>
    <tr><td>Length changes across relative layers</td><td>Information practices change over generations</td><td>Secure dating and replication across trenches</td></tr>
    </tbody></table><div class="wide-callout">If this model holds, seals could have helped people recognize identity and authority across settlements. Which people, which roles and which institution remain open questions.</div>''', ("identity", "units", "time"))

add("What is new to the field?", "Our additions are specific measurements, datasets and tests.", "The literature already contains many of the broad ideas. Our publication claims need to name the narrower addition.",
    '''<table class="novelty-table"><thead><tr><th>Already in the literature</th><th>Our defensible addition</th></tr></thead><tbody>
    <tr><td>Recurring groups, endings and structural analysis</td><td>A specified predictor tested against photographed line divisions, with a saved benchmark result</td></tr>
    <tr><td>Names, titles and administrative seal functions</td><td>Reproducible counts of repeats, distribution and particular plate checks</td></tr>
    <tr><td>Statistical prediction of missing signs</td><td>Tests that account for object relationships and compare against contextual baselines</td></tr>
    <tr><td>Integrated databases of Indus objects</td><td>A versioned reconciliation that preserves source conflicts and measures remaining gaps</td></tr>
    <tr><td>Criticism of flexible dictionary fitting</td><td>A complete-key evaluation on real inscriptions with matched alternatives and known-answer checks</td></tr>
    </tbody></table>''', ("audit",))

add("Publication assessment", "Two focused papers have a developed scientific core.", "This is our evidence-based assessment, not a guarantee of journal acceptance.",
    '''<div class="publication-grid"><div><h2>Developed core</h2><p><strong>Full Sanskrit-key evaluation</strong><br>Publish the controlled test of the particular released key.</p><p><strong>Reference-law methods</strong><br>Publish the exact examples and calibration for copying, selection and deduplication.</p><span class="status">Specialist checking and preparation remain</span></div>
    <div><h2>Promising with a defined next step</h2><p><strong>Object resource:</strong> audit accuracy and release rights.<br><strong>Segmentation:</strong> confirm labels and test unread seals.<br><strong>Restoration:</strong> refit with corrected object groups.<br><strong>Chronology:</strong> audit dating and trench influence.<br><strong>Rebus tests:</strong> repair matching and the parser.</p></div>
    <div><h2>Supporting or exploratory</h2><p>Seal individuality and fish ordering strengthen larger arguments. They have narrower standalone novelty.</p><p>Birth-star names and town alignments remain hypotheses. Current results do not support a decipherment paper.</p></div></div>''', ("audit", "birth", "towns"))

add("How we get closer", "The next advance should predict something we have not used.", "A reading becomes stronger when a fixed rule survives new objects and independent archaeological evidence.",
    '''<div class="next-grid"><div><span class="step-number">1</span><h2>Complete object records</h2><p>Resolve aliases and find photographs, dimensions, contexts and dates.</p></div><div><span class="step-number">2</span><h2>Freeze a prediction</h2><p>Write exactly what a proposed reading expects, and what would make it fail.</p></div><div><span class="step-number">3</span><h2>Use fresh objects</h2><p>Test unseen seals without changing the key after seeing the answer.</p></div><div><span class="step-number">4</span><h2>Find an outside anchor</h2><p>Connect a sign group to a known name, counted quantity, documented use or bilingual text.</p></div></div><div class="wide-callout">The boldest supported direction is a testable model of identity and shared roles on some seals. Reading those roles requires a stable mapping from signs to meaning, supported outside the pattern itself.</div>''', ("audit", "units", "identity", "numbers"))

add("Plain-language reference", "The terms used in this deck", "Keep this page open when a research term gets in the way.",
    '''<div class="glossary"><div><h3>Corpus</h3><p>The collection of inscriptions we analyze.</p><h3>Sign / sign group</h3><p>One written mark / several marks considered together.</p><h3>Legend</h3><p>The short inscription on an object.</p><h3>Segmentation</h3><p>Deciding where one group ends and another begins.</p><h3>Restoration</h3><p>Suggesting a missing or damaged sign.</p></div>
    <div><h3>Rebus</h3><p>A picture used for a similar-sounding word.</p><h3>Baseline</h3><p>A comparison showing what a simple rule or chance can achieve.</p><h3>Held-out / fresh</h3><p>Kept aside for testing / not previously examined for that research question.</p><h3>Credence</h3><p>A stated degree of belief in a hypothesis, not a measured fact.</p><h3>p-value</h3><p>How often the stated chance model produces a result at least this extreme; not the probability a claim is false.</p></div></div>''', ("audit",))

add("Sources · Prior research", "The main literature behind the novelty assessment", "Links open the original publications or the exact public project snapshot used in the audit.",
    '''<div class="reference-list">
    <p><a href="https://tuhat.helsinki.fi/ws/portalfiles/portal/207893149/indus_syntactic_1981.pdf" target="_blank">Koskenniemi (1981)</a><span>Segmentation and syntactic classification of Indus texts.</span></p>
    <p><a href="https://homes.cs.washington.edu/~rao/PNASIndus.pdf" target="_blank">Rao et al. (2009)</a><span>Statistical structure and prediction of missing signs.</span></p>
    <p><a href="https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0009506" target="_blank">Yadav et al. (2010)</a><span>Statistical analysis of recurring sign combinations.</span></p>
    <p><a href="https://www.harappa.com/sites/default/files/pdf/MarkersAndAgenciesOfAnisotropy.pdf" target="_blank">Bhaskar (2024)</a><span>Direction and the significance of physical line arrangement.</span></p>
    <p><a href="https://www.harappa.com/sites/default/files/pdf/indus-writing.pdf" target="_blank">Parpola (2008)</a><span>Names, occupations and proposed readings.</span></p>
    <p><a href="https://www.nature.com/articles/s41599-023-02320-7" target="_blank">Mukhopadhyay (2023)</a><span>Administrative functions and inscriptions shared across settlements.</span></p>
    <p><a href="https://www.harappa.com/sites/default/files/pdf/KenoyerMeadow%202010%20Inscribed%20Objects%20from%20Harappa.pdf" target="_blank">Kenoyer and Meadow (2010)</a><span>Chronological change in Harappa inscribed objects.</span></p>
    <p><a href="https://arxiv.org/html/2608.02999v1" target="_blank">Raghavendra (2026), preprint</a><span>Earlier criticism of lexical fit and unicity arguments.</span></p>
    <p><a href="https://github.com/dbourdeau/cyphersolver/blob/1c73645947deba694cb82d42dba967319e8df5a5/docs/indus.html" target="_blank">Bourdeau, public snapshot of 1 October 2026</a><span>Close prior approaches; an unreviewed record, not validation of its results.</span></p>
    </div>''', ("audit",))

photo_index = list(csv.DictReader((ROOT / "experiments/2026-10-13-image-index-and-units/run-2026-10-13/images/face-image-links.csv").open(encoding="utf-8-sig")))
photo_rows = []
for asset in assets:
    fn = Path(asset["file"]).name
    if fn.endswith(".jpg"):
        row = next(x for x in photo_index if x["file"] == fn)
        asset["catalogue"] = {k: row[k] for k in ("cisi", "cisi_volume", "cisi_pdf_page", "page_basis", "sha256")}
        photo_rows.append(f'<tr><td>{fn}</td><td>CISI {row["cisi_volume"]}, PDF page {row["cisi_pdf_page"]}</td></tr>')

add("Sources · Project evidence and image credits", "Every result leads back to a preserved research package.", "The source links at the foot of each slide open the local reports. Keep the deck in the repository’s output folder to retain those links.",
    '<div class="columns credits"><div><h2>Actual catalogue photographs</h2><table class="mini-table"><thead><tr><th>Image</th><th>Indexed source</th></tr></thead><tbody>' + ''.join(photo_rows) + '</tbody></table><p>Photographs are CISI catalogue reproductions held through the pinned Lipi export. PDF-page numbers come from the project image index. The photographs have not been redrawn.</p><p><strong>This image-bearing deck is for local review.</strong> Catalogue-image redistribution rights remain unresolved; review permissions before public release.</p></div><div><h2>Illustration and evidence status</h2><p>The cover was generated with OpenAI ImageGen as an imagined seal-use scene. Its people, setting, objects and signs are illustrative.</p><p>English labels, the sun/son example and the arithmetic table explain methods. They are not proposed Indus translations.</p><p>Charts reproduce preserved project results. No new confirmation experiment was run for this presentation.</p><p>The 22 October literature audit gives the detailed publication judgement, source list and remaining validation work.</p><div class="end-line">Understanding the structure is progress.<br>Reading the language is the next challenge.</div></div></div>', ("audit", "images", "rights"))

CSS = r'''
:root{--paper:#f5f1e8;--ink:#243634;--teal:#246d68;--clay:#af6144;--muted:#65716c;--line:#d9d7ca;--pale:#e5ece5;--cream:#ebe2d3;--scale:1}
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;font-family:Segoe UI,Arial,sans-serif;color:var(--ink);background:#1e2e2c}button,a{-webkit-tap-highlight-color:transparent}button{font:inherit;cursor:pointer}a{color:inherit;text-decoration-color:#a7b3a8;text-underline-offset:3px}a:hover{color:var(--teal)}a:focus-visible,button:focus-visible{outline:3px solid #dcaa70;outline-offset:4px}
#stage{position:fixed;inset:0 0 58px;display:flex;align-items:center;justify-content:center;overflow:hidden}.slide{display:none;position:relative;flex-shrink:0;width:1440px;height:900px;background:var(--paper);padding:60px 72px 65px;transform:scale(var(--scale));overflow:hidden}.slide.active{display:flex;flex-direction:column}header{position:relative;z-index:1;flex-shrink:0}.eyebrow{text-transform:uppercase;letter-spacing:2.4px;font-size:16px;font-weight:650;color:var(--teal);margin-bottom:18px}h1{font-family:Georgia,serif;font-weight:400;letter-spacing:-1.3px;font-size:49px;line-height:1.13;margin:0;max-width:1280px}h2{font-family:Georgia,serif;font-size:31px;line-height:1.2;font-weight:400;margin:0 0 20px}h3{font-size:17px;letter-spacing:.7px;font-weight:700;margin:0 0 8px;color:var(--teal)}p{font-size:23px;line-height:1.45;margin:0 0 16px}.subtitle{font-size:23px;line-height:1.4;color:var(--muted);margin:19px 0 0;max-width:1230px}.body{position:relative;flex:1;min-height:0;padding-top:38px}.columns{display:grid;grid-template-columns:1fr 1fr;gap:64px;height:100%;align-content:start}.columns>*{min-width:0}.explain{border-left:1px solid var(--line);padding-left:44px;display:flex;flex-direction:column;gap:21px}.explain p{font-size:23px;margin:0}.explain h3{text-transform:uppercase;font-size:15px;letter-spacing:1.3px}.explain .decoding{border-top:1px solid var(--line);padding-top:19px}.explain .decoding h3{color:var(--clay)}footer{position:absolute;bottom:24px;left:72px;right:72px;display:flex;justify-content:space-between;align-items:flex-end;gap:24px;border-top:1px solid var(--line);padding-top:13px;min-height:35px;z-index:2}.source{font-size:12px;line-height:1.6;max-width:960px;color:var(--muted)}.folio{font-size:11px;letter-spacing:1.1px;white-space:nowrap}.folio b{margin-left:25px;font-size:15px}.metric-pair{display:flex;gap:45px;margin-bottom:37px}.metric-pair b{display:block;font-family:Georgia,serif;font-weight:400;font-size:65px;color:var(--teal)}.metric-pair span{font-size:19px;display:block;max-width:230px}.barrow{margin:0 0 23px}.barlabel{font-size:20px;line-height:1.35;display:flex;gap:16px;justify-content:space-between;margin-bottom:9px}.barlabel strong{white-space:nowrap;color:var(--teal)}.track{height:19px;background:#e3e4d8}.bar{height:100%;min-width:2px;background:var(--teal)}.clay{background:var(--clay)!important}.neutral{background:#a3aca0!important}.clay-text{color:var(--clay)!important}.chart-title{margin:0 0 25px;font-size:21px;letter-spacing:0}.note{font-size:17px!important;line-height:1.45!important;color:var(--muted);margin:23px 0 0!important}.hero-number{font-family:Georgia,serif;font-size:112px;line-height:1;color:var(--teal);margin-bottom:20px}.range-block{border-top:1px solid var(--line);padding-top:24px;margin-top:25px}.range-block span{font-size:18px}.range-block b{font-size:46px;font-family:Georgia,serif;display:block;font-weight:400;margin:8px 0}.range-block p{font-size:19px}.reading-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:31px;margin-top:12px}.reading-grid>div{border-top:2px solid var(--teal);padding-top:26px}.step-number{display:block;font-family:Georgia,serif;color:var(--clay);font-size:54px;margin-bottom:26px;line-height:1}.reading-grid p{font-size:22px}.reading-grid h2{font-size:30px;min-height:38px}.status{display:block;color:var(--teal);font-size:17px;font-weight:650;line-height:1.4;margin-top:20px}.wide-callout{font-family:Georgia,serif;font-size:28px;line-height:1.4;margin-top:38px;border-left:5px solid var(--teal);padding:15px 25px;background:var(--pale)}figure{margin:0}figure img{max-width:100%;object-fit:contain}.photo-columns{grid-template-columns: .85fr 1.15fr;gap:60px}.photo-columns>figure{text-align:center}.photo-columns>figure img{height:378px;max-width:420px}.photo-columns figcaption{text-align:left}.photo-columns .plain{font-size:23px;margin-top:20px}figcaption{color:var(--muted);font-size:17px;line-height:1.4;margin-top:17px}.inline-stat{display:flex;align-items:center;gap:30px;margin-bottom:35px}.inline-stat b{font-family:Georgia,serif;font-size:65px;color:var(--teal);font-weight:400}.inline-stat span{font-size:21px;line-height:1.35}.example-panel{background:var(--cream);padding:30px 34px;align-self:start}.example-label{font-size:14px;text-transform:uppercase;letter-spacing:1px;display:block;color:var(--clay);margin-bottom:25px}.word-example{display:grid;grid-template-columns:1fr 1fr;gap:14px;font-size:29px;font-weight:600;letter-spacing:2px;margin:14px 0}.word-example span{background:var(--paper);padding:15px;color:var(--teal)}.word-example span+span{color:var(--clay)}.example-panel>p{font-size:22px;margin:26px 0 0}.small-callout{background:var(--pale);font-size:19px;padding:15px 20px;margin-top:26px}.body:has(>.small-callout)>.columns{height:auto}.number-line{display:flex;gap:25px;align-items:center;border-bottom:1px solid var(--line);padding:11px 0 23px;margin-bottom:21px}.number-line b{font-family:Georgia,serif;font-size:70px;color:var(--teal);font-weight:400;min-width:120px}.number-line p{font-size:21px;margin:0}.number-line strong{font-size:18px;font-weight:500;color:var(--muted)}.photo-pair{display:grid;grid-template-columns:1fr 1fr;gap:22px;text-align:center;margin-bottom:30px}.photo-pair img{width:100%;height:245px}.photo-pair figcaption{font-size:16px}.plain{font-size:22px}.wide-photo img{width:100%;height:260px}.wide-photo figcaption{margin-top:10px}.stacked{display:flex;width:100%;height:52px;margin-top:27px;color:white;font-weight:600}.stacked span{display:flex;justify-content:center;align-items:center;background:var(--teal);min-width:29px;border-right:2px solid var(--paper)}.legend{font-size:17px;margin-top:13px}.letter-example{font-family:Georgia,serif;font-size:100px;color:var(--teal);letter-spacing:30px;text-align:center;line-height:1.3}.choice-words{text-align:center;font-size:34px;letter-spacing:3px;color:var(--clay);margin-top:15px}.stat-banner{border-top:1px solid #c6bcab;margin-top:25px;padding-top:20px;display:flex;align-items:center;gap:20px}.stat-banner b{font-family:Georgia,serif;font-size:41px;white-space:nowrap;font-weight:400;color:var(--teal)}.stat-banner span{font-size:18px;line-height:1.4}.rebus-example{display:flex;gap:27px;align-items:center;justify-content:center;background:var(--cream);padding:32px 16px;margin-bottom:34px}.rebus-example span{font-size:44px;font-family:Georgia,serif;color:var(--teal)}.rebus-example b{font-size:18px;font-weight:400;color:var(--muted)}.sentence-example{font-family:Georgia,serif;font-size:56px;line-height:1.32;color:var(--teal)}.sentence-example span{color:var(--clay)}.equation{font-family:Georgia,serif;font-size:55px;color:var(--teal);padding:12px 0 24px}.mini-table{width:100%;border-collapse:collapse;font-size:21px;line-height:1.4}.mini-table th{text-align:left;font-size:16px;font-weight:600;color:var(--teal)}td,th{padding:14px 12px;border-bottom:1px solid var(--line);vertical-align:top}td:first-child,th:first-child{padding-left:0}td:last-child,th:last-child{padding-right:0}.evidence-table,.synthesis-table,.novelty-table{width:100%;border-collapse:collapse;font-size:23px;line-height:1.4}.evidence-table th,.synthesis-table th,.novelty-table th{font-size:17px;text-align:left;color:var(--teal)}.evidence-table td{padding-top:19px;padding-bottom:19px}.synthesis-table td{padding-top:20px;padding-bottom:20px;width:33.333%}.synthesis-table+.wide-callout{font-size:26px;margin-top:30px}.novelty-table td{padding-top:23px;padding-bottom:23px;width:50%;font-size:23px}.publication-grid{display:grid;grid-template-columns:1fr 1.15fr 1fr;gap:39px}.publication-grid>div{border-top:3px solid var(--teal);padding-top:25px}.publication-grid>div+div{border-color:var(--clay)}.publication-grid h2{font-size:30px}.publication-grid p{font-size:23px;line-height:1.6;margin-bottom:24px}.next-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:35px}.next-grid h2{font-size:30px}.next-grid p{font-size:23px}.next-grid .step-number{border-bottom:1px solid var(--line);padding-bottom:23px}.glossary{display:grid;grid-template-columns:1fr 1fr;gap:70px}.glossary h3{font-size:22px;margin:0 0 4px}.glossary p{font-size:22px;margin-bottom:21px}.reference-list{display:grid;grid-template-columns:1fr 1fr;column-gap:65px;row-gap:18px}.reference-list p{font-size:22px;margin:0;border-bottom:1px solid var(--line);padding-bottom:15px}.reference-list a{color:var(--teal)}.reference-list span{display:block;font-size:19px;margin-top:6px;color:var(--muted)}.credits p{font-size:21px}.credits h2{font-size:30px}.credits .mini-table{font-size:18px;margin-bottom:20px}.credits td{padding:10px 12px}.end-line{font-family:Georgia,serif;color:var(--teal);font-size:29px;line-height:1.4;border-top:1px solid var(--line);padding-top:21px;margin-top:23px}
.cover{padding-top:67px}.cover-art{position:absolute;inset:-280px -72px -70px;z-index:0}.cover-art img{position:absolute;width:1440px;height:900px;object-fit:cover;left:0;top:0}.cover header{width:580px}.cover h1{font-size:78px;line-height:1.08;letter-spacing:-2px;margin-top:40px}.cover .eyebrow{font-size:15px}.cover .subtitle{font-size:24px;line-height:1.5;max-width:520px;margin-top:32px}.cover .body{position:static}.cover .cover-art{inset:0}.cover-bottom{position:absolute;left:72px;bottom:157px;z-index:1}.cover-bottom p{font-size:20px;margin:0 0 10px}.cover-bottom span{font-size:16px;color:var(--muted)}.image-disclosure{position:absolute;right:55px;bottom:100px;z-index:1;font-size:13px;line-height:1.5;background:#f5f1e8e6;padding:11px 17px}.cover footer{background:#f5f1e8db;left:0;right:0;bottom:0;padding:18px 72px;min-height:70px}.cover .source{max-width:700px}
nav{position:fixed;bottom:0;left:0;right:0;height:58px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;color:#f5f1e8;background:#1e2e2c;gap:20px;z-index:10}nav button{border:1px solid #69847d;background:transparent;color:#f5f1e8;padding:7px 12px;border-radius:3px;font-size:14px}nav button:hover{background:#3f5d56}nav button:disabled{opacity:.35;cursor:default}.navgroup{display:flex;align-items:center;gap:10px}#counter{min-width:72px;text-align:center;font-variant-numeric:tabular-nums;font-size:14px}.navtitle{font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:48vw;color:#c5d2c9}#progress{position:fixed;bottom:58px;height:3px;left:0;background:#c38b61;z-index:11;transition:width .18s}#overview{position:fixed;inset:0 0 58px;background:var(--paper);color:var(--ink);overflow:auto;padding:38px;z-index:9}#overview[hidden]{display:none}#overview h2{margin:0 0 25px}.overview-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}.overview-grid button{font-size:18px;line-height:1.35;text-align:left;background:transparent;color:var(--ink);border:1px solid var(--line);padding:20px;min-height:112px}.overview-grid button:hover{background:var(--pale)}.overview-grid b{display:block;font-size:13px;color:var(--clay);margin-bottom:9px}#help{font-size:13px;color:#b6c7bd}button[aria-pressed=true]{background:#43665d}.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
@media(max-width:700px){html,body{height:auto;overflow:auto;background:var(--paper)}#stage{position:static;display:block;overflow:visible;padding-bottom:80px}.slide{width:100%;height:auto;min-height:calc(100dvh - 58px);transform:none!important;padding:30px 24px 90px;overflow:visible}.slide.active{display:block}.eyebrow{font-size:12px;margin-bottom:15px}h1{font-size:35px;letter-spacing:-.6px}h2{font-size:27px}.subtitle{font-size:19px;line-height:1.45}.body{padding-top:28px}.columns,.reading-grid,.next-grid,.publication-grid,.glossary,.reference-list{grid-template-columns:1fr;gap:30px;height:auto}p,.explain p,.publication-grid p,.plain{font-size:20px}.explain{padding:25px 0 0;border-left:0;border-top:1px solid var(--line);gap:20px}.metric-pair{gap:25px}.metric-pair b{font-size:49px}.metric-pair span{font-size:16px}.note{font-size:16px!important}.wide-callout{font-size:23px;margin-top:25px}.reading-grid h2{min-height:0}.step-number{font-size:42px;margin-bottom:18px}.photo-columns>figure img{max-width:100%;height:310px}.photo-pair{gap:12px}.photo-pair img{height:180px}.photo-pair figcaption{font-size:14px}.inline-stat b{font-size:50px}.inline-stat span{font-size:18px}.example-panel{padding:24px}.word-example{font-size:21px;letter-spacing:1px}.word-example span{padding:12px}.stat-banner{display:block}.stat-banner span{display:block;margin-top:10px}.letter-example{font-size:78px}.choice-words{font-size:27px}.sentence-example{font-size:43px}.barlabel{font-size:18px}.number-line b{font-size:56px;min-width:95px}.number-line p{font-size:19px}.synthesis-table,.novelty-table{font-size:16px;line-height:1.35}.synthesis-table td,.novelty-table td{font-size:16px;padding:12px 7px}.synthesis-table th,.novelty-table th{font-size:13px}.evidence-table{font-size:20px}.credits p{font-size:18px}.mini-table{font-size:18px}.credits .mini-table{font-size:15px}footer{position:static;margin-top:40px;display:block;padding-top:15px;min-height:0}.source{font-size:11px;line-height:1.6}.folio{margin-top:12px}.cover{min-height:calc(100dvh - 58px);background:#eee3d0;padding-top:37px}.cover header{width:100%}.cover h1{font-size:53px;margin-top:18px;max-width:390px}.cover .eyebrow{font-size:12px}.cover .subtitle{font-size:20px;max-width:340px}.cover .cover-art{inset:0;opacity:.27;overflow:hidden}.cover-art img{left:0;top:0;width:100%;height:100%;object-fit:cover}.cover-bottom{position:relative;left:auto;bottom:auto;margin-top:15px}.image-disclosure{position:relative;right:auto;bottom:auto;margin-top:28px;display:inline-block}.cover footer{position:relative;padding:15px 0 0;background:transparent}.navtitle,#help,#fullBtn,#printBtn{display:none}nav{padding:0 12px;gap:8px}.navgroup{gap:6px}nav button{font-size:13px;padding:7px 10px}#counter{min-width:56px}#overview{padding:25px}.overview-grid{grid-template-columns:1fr}.body:has(>.small-callout)>.columns{height:auto}.cover .body{padding-top:26px}}
@media print{@page{size:1440px 900px;margin:0}html,body{width:1440px;background:white;height:auto}nav,#progress,#overview{display:none!important}#stage{position:static;display:block;overflow:visible;padding:0}.slide,.slide.active{display:flex;transform:none!important;width:1440px;height:900px;break-after:page;page-break-after:always;-webkit-print-color-adjust:exact;print-color-adjust:exact}.slide:last-child{break-after:auto}a{text-decoration:none}footer .source{font-size:12px}}
'''

CSS += '\n@media(min-width:701px){.novelty-table td{padding-top:14px;padding-bottom:14px;font-size:22px}}\n'

JS = r'''
const slides=[...document.querySelectorAll('.slide')];
let current=0;
const titles=__TITLES__;
const overview=document.querySelector('#overview');
function resize(){document.documentElement.style.setProperty('--scale',Math.min(innerWidth/1440,(innerHeight-58)/900));}
function showSlide(n, update=true){
  current=Math.max(0,Math.min(slides.length-1,n));
  slides.forEach((slide,i)=>{slide.classList.toggle('active',i===current);slide.setAttribute('aria-hidden',i!==current);});
  document.querySelector('#counter').textContent=`${current+1} / ${slides.length}`;
  document.querySelector('#prev').disabled=current===0;
  document.querySelector('#next').disabled=current===slides.length-1;
  document.querySelector('#navtitle').textContent=titles[current];
  document.querySelector('#progress').style.width=`${(current+1)/slides.length*100}%`;
  document.title=`${current+1}. ${titles[current]} | Indus findings`;
  if(update)history.replaceState(null,'',`#${current+1}`);
  window.scrollTo(0,0);
}
window.showSlide=showSlide;
function toggleOverview(force){overview.hidden=force===undefined?!overview.hidden:!force;document.querySelector('#overviewBtn').setAttribute('aria-pressed',!overview.hidden);}
document.querySelector('#prev').addEventListener('click',()=>showSlide(current-1));
document.querySelector('#next').addEventListener('click',()=>showSlide(current+1));
document.querySelector('#overviewBtn').addEventListener('click',()=>toggleOverview());
document.querySelector('#printBtn').addEventListener('click',()=>window.print());
document.querySelector('#fullBtn').addEventListener('click',async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch{document.querySelector('#help').textContent='Use your browser’s fullscreen command';}});
document.querySelector('.overview-grid').innerHTML=titles.map((title,i)=>`<button data-slide="${i}"><b>${String(i+1).padStart(2,'0')}</b>${title}</button>`).join('');
document.querySelector('.overview-grid').addEventListener('click',e=>{const b=e.target.closest('button[data-slide]');if(b){showSlide(Number(b.dataset.slide));toggleOverview(false);}});
addEventListener('keydown',e=>{if(e.altKey||e.ctrlKey||e.metaKey)return;if(e.key==='Escape'){toggleOverview(false);return;}if(['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName))return;if(e.key.toLowerCase()==='o'){toggleOverview();return;}if(!overview.hidden)return;if(['ArrowRight','PageDown'].includes(e.key)||(e.code==='Space'&&!e.target.closest('button,a'))){e.preventDefault();showSlide(current+1);}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();showSlide(current-1);}if(e.key==='Home'){e.preventDefault();showSlide(0);}if(e.key==='End'){e.preventDefault();showSlide(slides.length-1);}});
addEventListener('resize',resize);
addEventListener('hashchange',()=>showSlide((parseInt(location.hash.slice(1))||1)-1,false));
resize();showSlide((parseInt(location.hash.slice(1))||1)-1,false);
'''.replace('__TITLES__', json.dumps([s["title"].replace('<br>', ' ') for s in slides]))

doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="A plain-language, illustrated explanation of the Indus project's findings and their limits, 22 October 2026."><title>Indus findings</title><style>{CSS}</style></head><body>
<main id="stage">{''.join(s['html'] for s in slides)}</main><div id="progress"></div>
<aside id="overview" hidden aria-label="Slide overview"><h2>Choose a slide</h2><div class="overview-grid"></div></aside>
<nav aria-label="Presentation controls"><div class="navgroup"><button id="prev" aria-label="Previous slide">← Previous</button><span id="counter" aria-live="polite"></span><button id="next" aria-label="Next slide">Next →</button></div><span id="navtitle" class="navtitle"></span><div class="navgroup"><span id="help">← → keys</span><button id="overviewBtn" aria-pressed="false">Overview</button><button id="fullBtn">Fullscreen</button><button id="printBtn">Print / PDF</button></div></nav>
<script>{JS}</script></body></html>'''
doc = doc.replace('<meta name="description"', '<link rel="icon" href="data:,"><meta name="description"')
OUT.write_text(doc, encoding="utf-8")
manifest = {"date": "2026-10-22", "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"), "format": "self-contained HTML", "slide_count": len(slides), "research_status": "Explanation of existing evidence; no new confirmation experiment", "authors": [{"agent": "Codex", "model": "GPT-6 (runtime identity)", "harness": "Codex desktop tools; Python builder; Playwright CLI QA"}], "slides": [{"number": i+1, "title": s["title"].replace('<br>', ' '), "sources": s["sources"]} for i, s in enumerate(slides)], "sources": {k: {"title": v[0], "path": v[1], "sha256": hashlib.sha256((ROOT / v[1]).read_bytes()).hexdigest()} for k,v in SOURCES.items()}, "assets": assets, "rights": "Local review only: embedded CISI photographs have unresolved redistribution rights.", "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest()}
(PACKAGE / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps({"output": str(OUT), "slides": len(slides), "bytes": OUT.stat().st_size, "assets": len(assets)}))
