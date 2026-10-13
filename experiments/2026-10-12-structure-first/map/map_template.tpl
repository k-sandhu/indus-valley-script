<title>Indus Research Map</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Serif:wght@500;600&display=swap">
<style>
/* Layout: a registry ledger. One reading column for argument, a wider frame for the effort chart and path lanes. */
:root {
  --bg: #f3f5f3;
  --surface: #ffffff;
  --sunk: #e8ece9;
  --ink: #1b2320;
  --muted: #56625d;
  --line: #d4dbd7;
  --accent: #0e6b5b;
  --accent-ink: #ffffff;

  --c-measured: #137a62;
  --c-negative: #b5442a;
  --c-synthetic: #6a5db0;
  --c-known: #2e6db2;
  --c-source: #94700f;
  --c-hypothesis: #a23d7b;
  --c-infra: #7c8580;

  --hi: #0e6b5b;
  --mid: #94700f;
  --lo: #7c8580;

  --f-display: "IBM Plex Serif", Georgia, "Times New Roman", serif;
  --f-body: "IBM Plex Sans", "Segoe UI", system-ui, -apple-system, sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;

  --measure: 68ch;
  --wide: 1120px;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #111614; --surface: #192019; --sunk: #202824; --ink: #e3e9e5; --muted: #9aa7a1; --line: #2d3732;
    --accent: #54c4a9; --accent-ink: #0b1210;
    --c-measured: #4fc39f; --c-negative: #ef7c5d; --c-synthetic: #a99df0; --c-known: #6eaaf0;
    --c-source: #d8b04c; --c-hypothesis: #e486bf; --c-infra: #a2aba6;
    --hi: #54c4a9; --mid: #d8b04c; --lo: #a2aba6;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #111614; --surface: #192019; --sunk: #202824; --ink: #e3e9e5; --muted: #9aa7a1; --line: #2d3732;
  --accent: #54c4a9; --accent-ink: #0b1210;
  --c-measured: #4fc39f; --c-negative: #ef7c5d; --c-synthetic: #a99df0; --c-known: #6eaaf0;
  --c-source: #d8b04c; --c-hypothesis: #e486bf; --c-infra: #a2aba6;
  --hi: #54c4a9; --mid: #d8b04c; --lo: #a2aba6;
  color-scheme: dark;
}

* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font-family: var(--f-body); font-size: 15.5px; line-height: 1.55; }
.wrap { max-width: var(--wide); margin: 0 auto; padding-inline: 20px; padding-block: 28px 64px; }
h1, h2, h3 { text-wrap: balance; }
h1 { font-family: var(--f-display); font-weight: 600; font-size: clamp(2rem, 4.6vw, 2.9rem); line-height: 1.1; margin: 6px 0 14px; letter-spacing: -0.01em; }
h2 { font-family: var(--f-display); font-weight: 600; font-size: 1.6rem; line-height: 1.2; margin: 0 0 8px; }
h3 { font-size: 1.04rem; font-weight: 600; margin: 0; line-height: 1.35; }
p { margin: 0; }
code { font-family: var(--f-mono); font-size: 0.82em; }
a { color: var(--accent); }
.eyebrow { font-family: var(--f-mono); font-size: 0.76rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); }
.lead { max-width: var(--measure); font-size: 1.06rem; color: var(--ink); }
.prose { max-width: var(--measure); display: grid; gap: 10px; color: var(--muted); }

nav.toc { display: flex; flex-wrap: wrap; gap: 6px 8px; margin: 22px 0 6px; }
nav.toc a { font-size: 0.86rem; text-decoration: none; color: var(--ink); border: 1px solid var(--line); background: var(--surface); padding: 5px 11px; border-radius: 999px; }
nav.toc a:hover, nav.toc a:focus-visible { border-color: var(--accent); color: var(--accent); }

section.block { margin-top: 56px; display: grid; gap: 18px; scroll-margin-top: 16px; }
.sechead { display: grid; gap: 6px; max-width: var(--measure); }
.sechead p { color: var(--muted); }

/* diagnosis */
.diag { display: grid; gap: 0; border-top: 1px solid var(--line); }
.dx { display: grid; grid-template-columns: 3.2rem minmax(0, 1fr); gap: 4px 14px; padding: 20px 0; border-bottom: 1px solid var(--line); }
.dx .rank { font-family: var(--f-display); font-size: 1.7rem; font-weight: 600; color: var(--accent); line-height: 1; padding-top: 2px; font-variant-numeric: tabular-nums; }
.dx h3 { font-family: var(--f-display); font-size: 1.22rem; font-weight: 600; margin-bottom: 6px; }
.dx p { max-width: var(--measure); }
.dx .ev { margin-top: 8px; font-size: 0.84rem; color: var(--muted); }
.dx .ev code { color: var(--muted); }

/* effort */
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
.stat { background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px; display: grid; gap: 4px; }
.stat .n { font-family: var(--f-display); font-size: 1.7rem; font-weight: 600; line-height: 1; font-variant-numeric: tabular-nums; }
.stat .l { font-size: 0.82rem; color: var(--muted); line-height: 1.3; }
.stat .bar { height: 4px; border-radius: 2px; }
.effort { background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 16px 18px; display: grid; gap: 9px; }
.erow { display: grid; grid-template-columns: minmax(0, 17rem) minmax(0, 1fr) 2.4rem; gap: 12px; align-items: center; }
.elabel { font-size: 0.88rem; }
.etrack { display: flex; height: 14px; background: var(--sunk); border-radius: 3px; overflow: hidden; }
.enum { font-family: var(--f-mono); font-size: 0.85rem; text-align: right; font-variant-numeric: tabular-nums; color: var(--muted); }
.seg { display: block; height: 100%; }
.seg + .seg { box-shadow: inset 1px 0 0 var(--surface); }
.c-measured { --c: var(--c-measured); } .c-negative { --c: var(--c-negative); } .c-synthetic { --c: var(--c-synthetic); }
.c-known { --c: var(--c-known); } .c-source { --c: var(--c-source); } .c-hypothesis { --c: var(--c-hypothesis); } .c-infra { --c: var(--c-infra); }
.seg, .stat .bar { background: var(--c); }
.note { font-size: 0.86rem; color: var(--muted); max-width: var(--measure); }

/* filters */
.controls { display: grid; gap: 12px; position: sticky; top: env(safe-area-inset-top, 0px); z-index: 2; background: var(--bg); padding-block: 10px; border-bottom: 1px solid var(--line); }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { font: inherit; font-size: 0.82rem; display: inline-flex; align-items: center; gap: 7px; padding: 5px 10px; border-radius: 999px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); cursor: pointer; }
.chip .cnt { font-family: var(--f-mono); color: var(--muted); font-size: 0.78rem; }
.chip[aria-pressed="false"] { opacity: 0.45; background: transparent; }
.chip:focus-visible, .btn:focus-visible, input:focus-visible, summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.dot { width: 9px; height: 9px; border-radius: 50%; background: var(--c); flex: none; }
.row2 { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
input[type="search"] { font: inherit; font-size: 0.92rem; flex: 1 1 240px; min-width: 0; padding: 7px 11px; border-radius: 6px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); }
.btn { font: inherit; font-size: 0.85rem; padding: 7px 12px; border-radius: 6px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); cursor: pointer; }
.btn:hover { border-color: var(--accent); }

/* lanes */
.lanes { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 520px), 1fr)); gap: 14px; align-items: start; }
.lane { background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 16px 16px 12px; display: grid; gap: 10px; min-width: 0; }
.lanehead { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; }
.lanecount { font-family: var(--f-mono); font-size: 0.78rem; color: var(--muted); white-space: nowrap; }
.minibar { display: flex; height: 6px; border-radius: 3px; overflow: hidden; background: var(--sunk); }
.lanesum { font-size: 0.9rem; color: var(--muted); }
details summary { cursor: pointer; font-size: 0.86rem; color: var(--accent); padding: 4px 0; }
ul.entries { list-style: none; margin: 8px 0 0; padding: 0; display: grid; gap: 0; }
.entry { padding: 11px 0; border-top: 1px solid var(--line); display: grid; gap: 4px; min-width: 0; }
.emeta { display: flex; flex-wrap: wrap; gap: 6px 10px; align-items: center; font-size: 0.76rem; }
.eid { font-family: var(--f-mono); font-weight: 500; font-size: 0.78rem; overflow-wrap: anywhere; }
.edate { color: var(--muted); font-family: var(--f-mono); }
.tag { display: inline-flex; align-items: center; gap: 5px; color: var(--muted); }
.unreg { font-size: 0.72rem; border: 1px dashed var(--line); padding: 1px 6px; border-radius: 3px; color: var(--muted); }
.eq { font-size: 0.9rem; font-weight: 500; }
.eo { font-size: 0.86rem; color: var(--muted); }
.eev { font-size: 0.74rem; color: var(--muted); overflow-wrap: anywhere; }
.lane.empty { opacity: 0.5; }

/* untried */
.ugroup { display: grid; gap: 10px; }
.ugroup > h3 { font-family: var(--f-display); font-size: 1.15rem; font-weight: 600; }
.ugrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 330px), 1fr)); gap: 10px; }
.idea { background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 13px 14px; display: grid; gap: 7px; align-content: start; min-width: 0; }
.idea h4 { margin: 0; font-size: 0.97rem; font-weight: 600; line-height: 1.35; }
.idea p { font-size: 0.86rem; color: var(--muted); }
.idea .have { font-size: 0.8rem; color: var(--muted); }
.idea .have b { color: var(--ink); font-weight: 500; }
.pills { display: flex; flex-wrap: wrap; gap: 6px; }
.pill { font-size: 0.72rem; font-family: var(--f-mono); letter-spacing: 0.02em; padding: 2px 7px; border-radius: 3px; border: 1px solid var(--line); color: var(--muted); }
.pill.p-hi { background: var(--hi); border-color: var(--hi); color: var(--surface); }
.pill.p-mid { border-color: var(--mid); color: var(--mid); }
.pill.p-lo { border-color: var(--lo); color: var(--lo); }
.pill.s-absent { border-style: solid; }
.pill.s-proposed { border-style: dashed; }

/* plan */
ol.plan { list-style: none; margin: 0; padding: 0; display: grid; gap: 0; border-top: 1px solid var(--line); counter-reset: step; }
ol.plan > li { counter-increment: step; display: grid; grid-template-columns: 3.2rem minmax(0, 1fr); gap: 4px 14px; padding: 18px 0; border-bottom: 1px solid var(--line); }
ol.plan > li::before { content: counter(step); font-family: var(--f-display); font-size: 1.7rem; font-weight: 600; color: var(--accent); line-height: 1; padding-top: 2px; }
.step { display: grid; gap: 8px; max-width: var(--measure); }
.step h3 { font-family: var(--f-display); font-size: 1.18rem; }
.step dl { display: grid; grid-template-columns: 6.2rem minmax(0, 1fr); gap: 6px 12px; margin: 0; font-size: 0.9rem; }
.step dt { color: var(--muted); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.06em; padding-top: 2px; }
.step dd { margin: 0; }
.pause { background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 16px 18px; display: grid; gap: 8px; max-width: var(--measure); }
.pause ul { margin: 0; padding-left: 1.2em; display: grid; gap: 4px; color: var(--muted); }
.update { margin-top: 10px; font-size: 0.88rem; color: var(--muted); border-left: 3px solid var(--accent); padding: 4px 0 4px 10px; max-width: var(--measure); }
.rgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 340px), 1fr)); gap: 10px; }
.rcard { background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 14px 15px; display: grid; gap: 7px; align-content: start; min-width: 0; }
.rcard h3 { font-size: 1rem; }
.rcard p { font-size: 0.88rem; color: var(--muted); }
.rcard .num { font-family: var(--f-mono); font-size: 0.76rem; color: var(--muted); }
.pill.r-frozen { background: var(--accent); border-color: var(--accent); color: var(--surface); }
.pill.r-desc { border-color: var(--c-source); color: var(--c-source); }
.pill.r-cal { border-color: var(--c-known); color: var(--c-known); }
.pill.s-tested { background: var(--c-measured); border-color: var(--c-measured); color: var(--surface); }
.result-line { font-size: 0.82rem; color: var(--ink); border-top: 1px dashed var(--line); padding-top: 6px; }
.tablewrap { overflow-x: auto; }
table.ledger { border-collapse: collapse; width: 100%; min-width: 640px; font-size: 0.86rem; background: var(--surface); }
table.ledger th, table.ledger td { border: 1px solid var(--line); padding: 8px 10px; text-align: left; vertical-align: top; }
table.ledger th { font-weight: 600; background: var(--sunk); }
footer { margin-top: 56px; padding-top: 16px; border-top: 1px solid var(--line); font-size: 0.82rem; color: var(--muted); display: grid; gap: 8px; max-width: var(--measure); }

@media (max-width: 640px) {
  body { font-size: 15px; }
  .erow { grid-template-columns: minmax(0, 1fr) 2.2rem; }
  .elabel { grid-column: 1 / -1; }
  .dx, ol.plan > li { grid-template-columns: 2.2rem minmax(0, 1fr); }
  .step dl { grid-template-columns: minmax(0, 1fr); gap: 2px; }
  .step dd { margin-bottom: 6px; }
}
@media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth; } }
</style>

<div class="wrap">
  <header>
    <div class="eyebrow">Indus script project · state of the work, 12 October 2026</div>
    <h1>Indus Research Map</h1>
    <p class="lead">This map covers the {{N_REG}} entries in the experiment registry and {{N_UNREG}} packages not yet registered, from 1 to 12 October 2026. It groups every path by line of thought and by the kind of evidence it produced, gives the diagnosis written before the six-step program, reports that program's results, lists directions not yet tried and sets out the next steps.</p>
    <p class="update">Updated 12 October 2026, after the six-step program ran, was verified and was revised in response to an adversarial review.</p>
    <nav class="toc" aria-label="Sections">
      <a href="#diagnosis">What was holding us back</a>
      <a href="#results">Results of the six steps</a>
      <a href="#effort">Where the effort went</a>
      <a href="#paths">Every path investigated</a>
      <a href="#untried">Untried and since tested</a>
      <a href="#next">What to investigate next</a>
      <a href="#method">How this map was made</a>
    </nav>
  </header>

  <section class="block" id="diagnosis">
    <div class="sechead">
      <h2>What has kept us from a substantive result</h2>
      <p>Eight analytical mistakes, ranked by how much each one had cost, as written before the six-step program. Counts refer to the 152 registry entries present at that time. The first four concern what we chose to measure; the last four concern how the work was organized.</p>
    </div>
    <div class="diag">
      <article class="dx"><div class="rank">1</div><div>
        <h3>We defined success where desk research cannot reach</h3>
        <p>The working definition of a substantive result has been a reading confirmed by an independent physical anchor: a counted collection, an attachment trace, a bilingual object. Those need museum access, new photography or excavation. By a keyword match, 80 of the 152 registry entries make their retry condition depend on new photographs, specimens, registrations, dated contexts or similar observations. Packages therefore end with a protocol for data the project cannot obtain, and the next session opens a different topic. Results that the corpus already in hand can support were never set as targets: a tested sign list, a segmentation into recurring units, a description of how the numerals behave, a function for one class of texts.</p>
        <p class="ev">Evidence: registry <code>retry_when</code> fields; roadmap ranks 1–6; <code>knowledge/directions/decipherment-readiness-2026-10-02.md</code></p>
      </div></article>
      <article class="dx"><div class="rank">2</div><div>
        <h3>Most of our measurements cannot tell the hypotheses apart</h3>
        <p>Restoration accuracy, Markov gain and ordering against shuffles come out high for every system tried: IVS, an invented office-routing code (0.631-bit gain) and all eleven testable Sumerian, Akkadian, Egyptian and Linear B cohorts. ROOT-12 recorded this on 1 October. The sequence lane still grew to 47 entries, and restoration rose from 33.8% to 41.2% top-one without changing anything we believe about the script. Dictionary fitting has the same defect: equality-pattern word matches cover 91–97% of IVS faces in all four languages. A test is worth running when the hypotheses still in play predict different values for it.</p>
        <p class="ev">Evidence: ROOT-12, METHODS-workflow_templates, MODERN-RESTORATION-01, BRONZE-AGE-LEXICAL-PATTERN-AMBIGUITY-2026-10-12</p>
      </div></article>
      <article class="dx"><div class="rank">3</div><div>
        <h3>The sign list was taken as given</h3>
        <p>The corpus uses ICIT/Wells codes. In the clean single-line frame (1,859 distinct texts, 8,535 signs) 577 codes occur. Of these, 214 (37%) occur once and 303 (53%) at most twice, while the 30 commonest codes carry 58% of all signs. Much of that long tail is compounds: a frequent base such as the jar, fish, human figure or U-shape with added strokes, hatching or an attached object. Counting each compound as an unrelated symbol fragments the evidence. Restoration fails on rare codes, substitution families depend on chart classes, and the meaning catalogue gives separate meanings to variants of one sign. Mahadevan's list has 417 signs, Parpola's about 386 and the coding used here about 700. No analysis has measured how our results change with that choice.</p>
        <p class="ev">Evidence: descriptive count on <code>data/normalized/lipi_clean_rtl_singleline.jsonl</code>, 12 October; restoration frequency audit; fish-stroke plate audit (the only feature-level sign study)</p>
      </div></article>
      <article class="dx"><div class="rank">4</div><div>
        <h3>We assigned meanings before establishing structure</h3>
        <p>The project constructed 596 new meanings to cover all 713 codes, pruned them under review to seven families on nine codes, and has started extending them to the 567 unreviewed codes. The fit criterion (a dictionary sense, a pictorial resemblance and compatible positions) admits many candidates per sign, so each new anchor adds freedom faster than it adds evidence. The language was inherited from the sources: the Lipi maintainer's Sanskrit readings and Bonta's Indo-Aryan proposal. It was never compared with Proto-Dravidian, Munda or an unknown language under matched freedom. The earliest attested Sanskrit, the Rigveda, was composed roughly 1500–1200 BCE, after the Mature Harappan period of about 2600–1900 BCE, and a fair comparison has to account for that gap. Decipherments that succeeded went in the opposite order: sign list, numerals, segmentation and inflection (Kober's triplets for Linear B), the content of texts from context (Proskouriakoff's dates and events on Maya monuments), and sound values last, from names or bilinguals.</p>
        <p class="ev">Evidence: BONTA-EXPLORATORY-SEMANTIC-EXTENSION-01, BONTA-EXTENSION-ADVERSARIAL-2026-10-11, <code>experiments/2026-10-12-anchor-expansion/PROTOCOL.md</code></p>
      </div></article>
      <article class="dx"><div class="rank">5</div><div>
        <h3>The most informative Indus material was filtered out</h3>
        <p>The main population is complete single-line texts of at least three signs, read right to left. Only 2 of 69 Harappa tablets, sealings and stamped vessels, and 2 of 355 rows in the catalogue's numerical class, pass that filter. Copper tablets are the clearest loss. The local export holds 190 Mohenjo-daro copper tablets carrying 77 distinct texts. The 12 tablets showing a hare carry one text, the 10 showing an anthropomorphic figure carry one text, and the elephant tablets carry two texts that differ by a single stroke. An image class predicts the text, which makes these objects the closest thing to a bilingual inside the corpus. The 2 October readiness review called the copper association graph "the currently useful task"; no package took it up. Also outside every main analysis: 2,060 bas-relief and incised tablet faces, the line breaks of multi-line texts, and 42 faces from sites outside South Asia.</p>
        <p class="ev">Evidence: CONTEXT-01, READINESS-01, <code>experiments/2026-10-02-decipherment-readiness/physical/REPORT.md</code>; object-type counts on <code>data/normalized/lipi_observed_faces.jsonl</code></p>
      </div></article>
      <article class="dx"><div class="rank">6</div><div>
        <h3>Rigor went where it was cheap</h3>
        <p>33 entries work only on invented or simulated data: 11 null-law enumerations, 12 synthetic mapping studies, khipu and measurement-acquisition simulations, a stamp-contact model and a societal renewal model. Of the 46 entries that measured real Indus material, 29 are variants of two statistics first computed on 1 October. The work is careful and the questions are small. The premises that drive conclusions had less scrutiny. One maintainer's transcription supplies almost every sequence, and its sign list, segmentation and reading-order conventions were adopted without a test. Packaging defects, such as a checker that misread JSON whitespace, received full repair records; the sign list has had no comparable audit.</p>
        <p class="ev">Evidence: NULL-01 to NULL-11, CRYPTO-01 to CRYPTO-11, NUM-02, KHI-03 to KHI-05, PHYS-01, PHYS-02; METHODS-* families</p>
      </div></article>
      <article class="dx"><div class="rank">7</div><div>
        <h3>Breadth replaced accumulation</h3>
        <p>Since 6 October the project has opened about twenty lines, from restoration models and an evidence census to settlement survey, satellite screening, societal persistence and early Indian institutions. Five of the ten programmes started on 11–12 October address questions outside the script. Each carries a protocol, reviews, a retrospective and packaging, and each ends with next tests that later sessions rarely run. The Lothal attachment test and the Harappa short-record table recommended on 2 October each received one bounded pass and were not resumed. Because no line was carried far, no result has had an earlier result to build on.</p>
        <p class="ev">Evidence: experiment directories dated 2026-10-06 to 2026-10-12; LOTHAL-TRACE-01, HARP-SHORT-01</p>
      </div></article>
      <article class="dx"><div class="rank">8</div><div>
        <h3>Reviews check for defects and never ask what a result decides</h3>
        <p>Adversarial review adds controls and caveats until a claim is safe. It does not ask which hypothesis a result moves, or by how much, so the output is a growing set of well-documented statements with little bearing on what the script is. A short hypothesis ledger would change this. Candidate descriptions include a logo-syllabic language, names and titles in a language, a nonlinguistic administrative code and an emblem or identity system. Before a test runs, write down what each predicts. If they all predict the same thing, the test should not run.</p>
        <p class="ev">Evidence: review and response files across the 2026-10-08 to 2026-10-12 packages</p>
      </div></article>
    </div>
  </section>

  <section class="block" id="results">
    <div class="sechead">
      <h2>Results of the six steps</h2>
      <p>The plan below the diagnosis was run on 12 October under a protocol recorded before any outcome, using only material already in the repository. An independent recomputation reproduced the headline numbers, and an adversarial review led to corrected endpoints and narrower conclusions. No sound value, meaning or language is assigned. Files are under <code>experiments/2026-10-12-structure-first/</code>.</p>
    </div>
    <div class="rgrid">
      <article class="rcard"><div class="pills"><span class="pill r-frozen">Frozen test</span></div>
        <h3>1. Sign families</h3>
        <p>Graphic families improve held-out prediction of rare Wells codes beyond 200 random groupings. Random contiguous cuts of the Wells order recover about three quarters of the gain, and the Parpola- and Mahadevan-level groupings predict unseen signs better. Added elements grouped across bases do not predict context.</p>
        <p class="num">gain 0.0219 bits/sign, p = 0.005; contiguous cuts 0.0164; unseen signs 14.60 → 14.19 (P: 13.93)</p></article>
      <article class="rcard"><div class="pills"><span class="pill r-frozen">Frozen test</span></div>
        <h3>2. Images and texts</h3>
        <p>On Harappa bas-relief and incised tablets, recurring texts stay with one image and images are predicted from other text types. On copper, held-out prediction fails, so the frozen conclusion applies only to the Harappa tablets. Copper-specific sign groups do not recur on seals showing the same animal.</p>
        <p class="num">2d: 3 hits against 3.01 expected, p = 0.62; power 0.91 for a fivefold enrichment</p></article>
      <article class="rcard"><div class="pills"><span class="pill r-desc">Descriptive</span></div>
        <h3>3. Line divisions</h3>
        <p>Where the catalogue marks a line division, lines recur elsewhere as units more often than windows crossing the division, and the chosen segmenter puts a boundary at every division. Kober-style alternation decides nothing at this scale.</p>
        <p class="num">23 faces against 4 (42 ties), p = 0.0003; boundary at 76 of 76 divisions against 37% elsewhere</p></article>
      <article class="rcard"><div class="pills"><span class="pill r-frozen">Frozen test</span></div>
        <h3>4. Stroke numerals</h3>
        <p>Stroke values are more tied to neighbouring signs than Ur III counts are to commodities, under every repair tried. The preceding sign is the more informative. Near-fixed pairs include 520 after three tall strokes, 585 after seven, and the opening signs 861, 817 and 820 before two strokes.</p>
        <p class="num">3.61 values per item against 4.53–5.15; top share 0.606 against 0.407–0.450</p></article>
      <article class="rcard"><div class="pills"><span class="pill r-cal">Calibration</span></div>
        <h3>5. Rehearsal on readable scripts</h3>
        <p>At Indus scale, unsupervised segmentation averages only slightly better than cutting everywhere, though branching entropy does well on Ur III seal legends. The alternation statistic does not separate Sumerian, Akkadian and Egyptian even on their true words.</p>
        <p class="num">mean boundary F1 0.531 against 0.485; seal legends 0.692 against 0.557</p></article>
      <article class="rcard"><div class="pills"><span class="pill r-desc">Descriptive</span></div>
        <h3>6. Structural profile</h3>
        <p>Indus texts begin with many different signs and end with few, even without texts ending in the jar sign. In the comparison corpora the same statistic changes sign with unit and genre, so it cannot rank languages, and every candidate remains tied.</p>
        <p class="num">asymmetry +0.260 (shuffle ±0.018); +0.149 without 740-final texts; Ur III seals −0.204 by sign, +0.079 by word</p></article>
    </div>
    <div class="tablewrap">
      <table class="ledger">
        <thead><tr><th>Step</th><th>H-LANG language</th><th>H-NAME names, titles</th><th>H-ADMIN administrative code</th><th>H-EMBLEM identity labels</th></tr></thead>
        <tbody>
          <tr><td>1 Bases and modifiers</td><td>Not met (modifiers)</td><td>No prediction</td><td>Not met (modifiers)</td><td>Modifier part met; base part untested threshold</td></tr>
          <tr><td>2 Pairing and transfer</td><td>Either allowed</td><td>Not met (no transfer)</td><td>Met</td><td>Not met (no transfer)</td></tr>
          <tr><td>4 Numeral values</td><td>Accounting part not met</td><td>Partly met</td><td>Not met</td><td>Partly met</td></tr>
        </tbody>
      </table>
    </div>
    <p class="note">Every description failed at least one frozen prediction. The results describe the corpus more than they choose among the four: graphic families that carry contextual information, genre-specific image–text pairing, recurring units respected by line divisions, a small closing sign class, and stroke groups partly fixed to neighbouring signs.</p>
  </section>

  <section class="block" id="effort">
    <div class="sechead">
      <h2>Where the effort went</h2>
      <p>{{N_ALL}} paths by evidence type, and the same paths by line of thought. Bar length is the number of entries; colour is the kind of evidence each produced.</p>
    </div>
    <div class="stats">
      <div class="stat c-measured"><span class="n">{{N_MEAS}}</span><span class="l">New measurement on real Indus material</span><span class="bar"></span></div>
      <div class="stat c-negative"><span class="n">{{N_NEG}}</span><span class="l">Failed or inconclusive on real Indus material</span><span class="bar"></span></div>
      <div class="stat c-synthetic"><span class="n">{{N_SYN}}</span><span class="l">Invented or simulated data only</span><span class="bar"></span></div>
      <div class="stat c-known"><span class="n">{{N_KNOWN}}</span><span class="l">Other real record systems</span><span class="bar"></span></div>
      <div class="stat c-source"><span class="n">{{N_SRC}}</span><span class="l">Source audit, census or literature</span><span class="bar"></span></div>
      <div class="stat c-hypothesis"><span class="n">{{N_HYP}}</span><span class="l">Interpretive construction or theory</span><span class="bar"></span></div>
      <div class="stat c-infra"><span class="n">{{N_INFRA}}</span><span class="l">Packaging, release or coordination</span><span class="bar"></span></div>
    </div>
    <div class="effort" role="img" aria-label="Number of investigated paths per line of thought, coloured by evidence type">
      {{EFFORT}}
    </div>
    <p class="note">Of the {{N_MEAS}} measured entries, 29 are registered variants of the first day's structural-gain and substitution analyses. The entries added on 12 October by the six-step program and the published-claim tests are included; none of the measured entries assigns a function or value to a sign group.</p>
  </section>

  <section class="block" id="paths">
    <div class="sechead">
      <h2>Every path investigated</h2>
      <p>Each lane summarizes what the line of thought established, then opens to its entries with the registry question, outcome, first evidence file and status. Filter by evidence type or search across IDs, questions and outcomes.</p>
    </div>
    <div class="controls">
      <div class="chips" role="group" aria-label="Evidence types">{{LEGEND}}</div>
      <div class="row2">
        <label for="q" class="eyebrow">Search</label>
        <input type="search" id="q" placeholder="e.g. copper, Lothal, restoration, Sanskrit">
        <button type="button" class="btn" id="toggleAll">Open all lanes</button>
        <button type="button" class="btn" id="resetF">Reset filters</button>
      </div>
    </div>
    <div class="lanes">{{LANES}}</div>
  </section>

  <section class="block" id="untried">
    <div class="sechead">
      <h2>Directions not yet investigated, and those since tested</h2>
      <p>Status shows what the record contains. <b>Absent</b> means no entry addresses the idea. <b>Proposed</b> means a memo or review recommended it and nothing ran. <b>Touched</b> means one bounded pass. <b>Tested 12 Oct</b> marks directions run by the six-step program or the concurrent published-claim tests, with a one-line result. Promise is the judgement made before those tests of how much the result could change our understanding.</p>
    </div>

    <div class="ugroup"><h3>The sign inventory</h3><div class="ugrid">
      <article class="idea"><div class="pills"><span class="pill p-hi">High promise</span><span class="pill p-hi">High promise</span><span class="pill p-mid">Medium</span><span class="pill p-hi">High promise</span><span class="pill p-hi">High promise</span><span class="pill p-hi">High, after segmentation</span><span class="pill p-hi">High promise</span><span class="pill p-hi">High promise</span><span class="pill p-mid">Medium</span><span class="pill p-hi">High promise</span><span class="pill p-mid">Medium</span><span class="pill p-hi">High promise</span><span class="pill p-mid">Medium</span><span class="pill p-mid">Medium</span><span class="pill p-mid">Medium</span><span class="pill p-lo">Low–medium</span><span class="pill p-mid">Medium, after segmentation</span><span class="pill s-tested">Partly tested</span></div>
        <h4>Language comparison with matched freedom</h4>
        <p>Score Proto-Dravidian, Munda, Indo-Aryan and a random lexicon on structural predictions (segment length, suffix order, compounding) under the same freedom, with held-out objects.</p>
        <p class="have"><b>Needed:</b> segments from the steps above; DEDR and comparable lexica.</p>  <p class="result-line"><b>Result:</b> The structural profile is descriptive; with no head-final seal corpus, every candidate stays tied.</p>
      </article>
    </div></div>

    <div class="ugroup"><h3>History and use of the signs</h3><div class="ugrid">
      <article class="idea"><div class="pills"><span class="pill p-mid">Medium</span><span class="pill s-absent">Absent</span></div>
        <h4>Early Harappan marks to mature signs</h4>
        <p>Ravi and Kot Diji phase graffiti at Harappa show which signs and compounds came first, which bears on how the inventory was built.</p>
        <p class="have"><b>Needed:</b> HARP publications.</p></article>
      <article class="idea"><div class="pills"><span class="pill p-mid">Medium</span><span class="pill s-proposed">Touched</span></div>
        <h4>Pottery graffiti as a separate genre</h4>
        <p>About 630 pottery faces in the export, and 75 CISI pottery identifiers missing from it. Pre-firing and post-firing marks may record different things from seals.</p>
        <p class="have"><b>In hand:</b> export; census gaps.</p></article>
      <article class="idea"><div class="pills"><span class="pill p-mid">Medium</span><span class="pill s-proposed">Proposed</span></div>
        <h4>Carver hands and workshops</h4>
        <p>Attributing seals to hands separates production variation from meaningful variants, which the sign-list work needs.</p>
        <p class="have"><b>In hand:</b> CISI 1 photographs.</p></article>
      <article class="idea"><div class="pills"><span class="pill p-lo">Access-dependent</span><span class="pill s-proposed">Proposed</span></div>
        <h4>Physical tests already designed</h4>
        <p>Lothal attachment coding, Kanmer replica handling, the stamp-contact laboratory, a 30-object reviewed observation block and an external quantity anchor. Each needs specimens or new images.</p>
        <p class="have"><b>Needed:</b> museum or excavation access.</p></article>
    </div></div>
  </section>

  <section class="block" id="next">
    <div class="sechead">
      <h2>What to investigate next</h2>
      <p>The six-step plan written with the diagnosis has been carried out; its results are above. These next steps follow from what it found. Each uses material that is held or obtainable from publications, and each states what result would change the following action.</p>
    </div>
    <ol class="plan">
      <li><div class="step"><h3>Recode the sign families without the catalogue order</h3><dl>
        <dt>Do</dt><dd>Code families from glyph sheets in shuffled order and without counts, with a human coder beside the model, and check the low-agreement families and the twelve-stroke grid on CISI 1 photographs.</dd>
        <dt>Decides</dt><dd>Whether visual families carry contextual information beyond the 0.0164 bits per sign that contiguous cuts of the Wells order already give.</dd></dl></div></li>
      <li><div class="step"><h3>Compare seals and sealings from one deposit</h3><dl>
        <dt>Do</dt><dd>Take seals and sealings from a single excavated context, where the same issuer is expected on both object types, and test whether texts and images recur together across them.</dd>
        <dt>Decides</dt><dd>Separates the readings left open by step 2: a text naming something tied to its image, seal texts that never name their emblem, or a production convention.</dd></dl></div></li>
      <li><div class="step"><h3>Score segmentation against line divisions</h3><dl>
        <dt>Do</dt><dd>Enlarge the boundary evidence with multi-line tablets and with sign spacing measured on photographs, then train and test segmenters against it.</dd>
        <dt>Decides</dt><dd>Whether the recurring units can be fixed well enough for any inflection or word-order analysis.</dd></dl></div></li>
      <li><div class="step"><h3>Follow the fixed numeral pairs</h3><dl>
        <dt>Do</dt><dd>Analyse stroke combinations in both directions, stratified by site and period, and test whether the two strokes after the opening signs 861, 817 and 820 behave like a number at all.</dd>
        <dt>Decides</dt><dd>Which stroke groups count something and which belong to fixed expressions.</dd></dl></div></li>
      <li><div class="step"><h3>Build the comparison the language question needs</h3><dl>
        <dt>Do</dt><dd>Measure the closing asymmetry at sign and word level on at least two head-initial and two head-final seal-legend corpora, for example Ur III and Old Akkadian seals against early Tamil-Brahmi and Prakrit seals and sealings.</dd>
        <dt>Decides</dt><dd>Whether this statistic can inform a choice among language families at all. Only if it separates the known corpora consistently should it be applied to the Indus texts.</dd></dl></div></li>
    </ol>
    <div class="pause">
      <h3>Keep paused</h3>
      <ul>
        <li>Unsupervised Kober-style analysis and dictionary fitting, until boundary evidence exists.</li>
        <li>Further restoration models on the same 8,009 masks.</li>
        <li>New null-law enumerations and synthetic mapping worlds.</li>
        <li>New topics outside the script while these steps are open.</li>
      </ul>
    </div>
  </section>

  <footer id="method">
    <h3>How this map was made</h3>
    <p>Each registry entry was assigned to one line of thought and one evidence type from its question and outcome. The 38 METHODS entries are variant endpoints of the first day's analyses, so their outcomes are summarized by family from the methods retrospective. Six packages that the registry does not yet list are included and marked.</p>
    <p>Corpus figures in the diagnosis and the untried list are descriptive counts made on 12 October over the local clean single-line Lipi frame (one record per distinct text, no unknown signs) and the full face export for object types and images. They are exploratory counts and not frozen endpoints. No inscription strings are reproduced here.</p>
    <p>Sources: <code>knowledge/experiments/registry.json</code>, the retrospectives under <code>knowledge/retrospectives/</code>, the direction memos and the 12 October experiment directories.</p>
  </footer>
</div>

<script>
(function () {
  var chips = Array.prototype.slice.call(document.querySelectorAll('.chip[data-cls]'));
  var q = document.getElementById('q');
  var lanes = Array.prototype.slice.call(document.querySelectorAll('.lane'));
  var toggleAll = document.getElementById('toggleAll');
  var resetF = document.getElementById('resetF');

  function active() {
    var on = {};
    chips.forEach(function (c) { if (c.getAttribute('aria-pressed') === 'true') on[c.dataset.cls] = true; });
    return on;
  }
  function apply() {
    var on = active();
    var term = (q.value || '').trim().toLowerCase();
    lanes.forEach(function (lane) {
      var shown = 0;
      lane.querySelectorAll('.entry').forEach(function (li) {
        var ok = !!on[li.dataset.cls] && (!term || li.dataset.text.indexOf(term) !== -1);
        li.hidden = !ok;
        if (ok) shown++;
      });
      lane.querySelector('.shown').textContent = shown;
      lane.classList.toggle('empty', shown === 0);
      if (term && shown > 0) lane.querySelector('details').open = true;
    });
  }
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      c.setAttribute('aria-pressed', c.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
      apply();
    });
  });
  q.addEventListener('input', apply);
  toggleAll.addEventListener('click', function () {
    var anyClosed = lanes.some(function (l) { return !l.querySelector('details').open; });
    lanes.forEach(function (l) { l.querySelector('details').open = anyClosed; });
    toggleAll.textContent = anyClosed ? 'Close all lanes' : 'Open all lanes';
  });
  resetF.addEventListener('click', function () {
    chips.forEach(function (c) { c.setAttribute('aria-pressed', 'true'); });
    q.value = '';
    apply();
  });
  apply();
})();
</script>
