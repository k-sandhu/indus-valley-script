# Brief for the academic-writing pass of 13 October 2026

This pass rewrites the project's published prose so that an attentive reader from a neighbouring field can follow it: an archaeologist reading the statistics papers, a statistician reading the archaeology, or an interested member of the public reading the knowledge pages. That reader has not followed our working sessions and does not know the labels we coined in them. The content, numbers and claims stay exactly as they are; only the way they are written changes.

Read [knowledge/editorial/WRITING.md](../../knowledge/editorial/WRITING.md) in full before editing, in particular the section "Problems in AI-assisted academic prose", which summarises the research behind this pass. A scan on 13 October found the surface habits (stock words, em dashes) almost gone. The work here is on the deeper problems.

## What to fix, most important first

1. Undefined terms. Coined labels and compressed technical phrases reach the reader without explanation: "known-slot masks", "crossing windows", "held export", "table laws", "domain failures", "witness", "endpoint", "reference", "comparator", "family", "face", "shot". Define each technical term in plain words where it first appears in the document, or replace it with the plain description. Keep a coined label only if the text uses it several times, and then define it once. Check the meaning in the linked methods or protocol before writing a definition; a wrong definition is worse than none.
2. Dense, noun-heavy sentences. Unpack slash compounds ("length/slot", "site/type", "physical/text") and stacked modifiers into ordinary sentences with a subject and a verb. One new idea per sentence. Prefer verbs to nominalisations ("we compared" rather than "the comparison of").
3. No guidance for the reader. Begin each paragraph with the point it makes. After a number, say in plain words what it means for the question when that is not obvious. Use "we" for the authors' actions and judgements.
4. Template paragraphs and formal words. Several paper introductions share a paragraph that begins "X are established methods" and ends "The present contribution is". Rewrite these to fit each paper's argument: say what earlier work provides and what this paper adds, in plain words. Prefer "use", "then", "show" to "utilize", "subsequently", "demonstrate".
5. Defining by negation and repeated scope disclaimers. Where several sentences say what a result does not establish, keep one clear statement of what was measured and where it applies, in the scope or methods paragraph, and state findings positively elsewhere. Do not delete a limitation that changes how a specific result should be read.
6. Voice and process talk. The project speaks as "we". Replace "the owner", "the user", "the coordinator" and similar with the project's voice or with "the maintainers" for decisions such as purchases and releases. In manuscripts, notes about which AI model or "pass" did what belong in one plain disclosure sentence in the status line or methods, not scattered through the argument; keep the disclosure that the work used AI assistance.
7. Citation labels. A link label should name the work: "Phipson and Smyth (2010)", not "primary rank source". Use only author, title and year information already present in the text, reference list or link target. Never invent or guess bibliographic details. If you cannot name a work from what is in front of you, leave the label and list it in your report.
8. Surface habits. Remove any remaining stock phrases, significance-inflating "-ing" clauses, "serves as", made-up lists of three, bold run-in labels and title-case headings.

## What must not change

- Numbers. Every number, interval, p-value, count, percentage and date stays exactly as written: no rounding, no recomputation, no dropping. The one exception is a figure repeated verbatim within the same paragraph, where one occurrence may go.
- Claims. Do not make any claim stronger or weaker. Credences stay. Conjectures and the working model are written in the indicative as project policy; keep that.
- Records. In conjecture cards, the sections "Predictions", "Kill condition" and "Record" (and any changelog or history list) are registered records: leave their wording unchanged. In any file, leave verbatim quotations, exact source titles, registered or frozen predictions, code blocks and inline code unchanged.
- Structure the tools read. Keep every link and its target, every ID (F-, Q-, C-, R-, W- codes), file names, YAML front matter except `title`, and the top-level card headings (`# Finding`, `# Evidence`, `# Scope`, `# Question`, `# Why it matters`, `# What is needed`, `# How to decide`, `# Prior attempts`, `# Claim`, `# Why it might be true`, `# Predictions`, `# Kill condition`, `# Record`). Do not rename a heading that another file links to with `#anchor`; search for the anchor before renaming. Tables keep their values; header labels may be clarified.
- Facts. Add no new results, citations, sources or facts that are not already in the repository. A definition or explanation must be accurate to the linked methods.
- Length. About the same length or shorter. Definitions may add up to roughly 15% to a file that needs many of them.

## How to work

Read each owned file in full, and the methods or protocol it links for any term you need to define, before editing. Edit the files in place. Then run, from the repository root:

```text
python maintenance/2026-10-13-academic-writing-pass/check_invariants.py <your files>
python tools/review_prose.py --no-write --path <file> [--path <file> ...]
```

The checker compares each file with the last commit. A `FAIL` (a lost link, lost inline code or a changed protected front-matter field) must be fixed. Every entry under `numbers_lost` or `numbers_added` must be either undone or explained in your report. Re-read each file once from the top as the target reader before you finish.

Edit only the files assigned to you. If you notice a problem elsewhere, report it instead of fixing it. Do not run `python tools/kb.py build`, do not commit, and do not change Git state.

## Report

Return a report of at most 600 words: for each file, two or three lines on the main changes and the terms you defined; the explanation for every `numbers_lost` or `numbers_added` entry; places where the meaning was unclear and you left the text alone; and any citation problems you noticed. End with the list of changed paths.

Writing requirement for all prose, including the report: maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument.
