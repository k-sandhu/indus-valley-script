# Writing rules

We adopted plain writing throughout the repository on 2 October 2026. These rules apply to new manuscripts, methods, notes and future edits. Historical evidence is preserved unchanged; its original wording remains part of the record.

## What the recent sources actually support

Tom Babb's March 2026 critique identifies repeated sentence openings, stock oppositions, inflated headings and claims without concrete details. It is a writer's account of patterns he dislikes, rather than a controlled comparison of models. [Article](https://www.linkedin.com/pulse/removing-em-dash-did-fix-your-ai-writing-tom-babb-9txac).

August 2026 discussion extends the complaint to sentence fragments, decorative metaphors, forced three-item lists and closing recaps. The [source summary](https://notes.nicolasdeville.com/nicai/ai-writing-tells/) discloses that it was drafted by an AI assistant; it points to [Ruben Hassid's original post](https://x.com/rubenhassid/status/2087856703773508025). We use these as editorial suggestions, with that provenance visible. We do not accept their claims about model training or automatic authorship detection as established facts.

There is also empirical evidence of shifts in scholarly vocabulary after LLM adoption. Kobak and colleagues analyzed more than 15 million biomedical abstracts; this supports checking habitual style words in aggregate, without treating any word as proof of authorship. [Science Advances paper and author version](https://arxiv.org/abs/2406.07016v5). A January 2026 study examines writing complexity and scientific production; its conclusions concern a defined observational analysis. [Author preprint](https://arxiv.org/abs/2601.13187).

This search did not establish a controlled comparison of the writing habits of every newest model release. The changes below follow the project's preference and identified editorial problems; they do not depend on an AI detector.

## Editing decisions

Write the finding early. Give the observation, result or action, followed by the evidence needed to understand it. A sentence should name its subject and say what happened.

Replace claims of quality with details. State the split rule, measured gain, null design or source check instead of calling the work rigorous, powerful, robust or groundbreaking. Use technical terms when they distinguish an actual method. A bootstrap confidence interval, an inverse problem and minimum-cost flow are legitimate terms.

Cut stock openings, promotional verbs and statements about importance. Avoid "delve", "leverage", "foster", "unlock", "game changer", "seamless", "tapestry", "it's worth noting", "the key takeaway", "here's the thing" and "in conclusion". The research does not need to praise itself.

Explain the result directly. Avoid rhetorical constructions that dismiss an alternative merely to make the preferred description sound stronger. Where a comparison matters, name both measurements or assumptions and explain the difference.

Use paragraphs with connected sentences. Avoid a series of short dramatic fragments, repeated openings or one-sentence paragraphs written for emphasis. Do not manufacture three parallel items when the evidence supplies a different number.

Use tables for real comparisons and lists for steps or parallel observations. Paper sections and methods headings should help navigation. Do not add headings to make a short answer look substantial.

Keep punctuation ordinary. Prefer periods and commas to repeated em dashes. Do not introduce errors, awkward phrasing or needless synonyms to imitate a human author.

State uncertainty where it changes the claim. Keep the source, scope and unresolved premise close to the relevant result. Remove repeated generic caveats that add no new information. Preserve genuine statistical intervals, measured ranges and archaeological dating uncertainty.

We also avoid repeated corrective comparisons, a problem first noticed in the archaeology memo. Assume an attentive reader. Develop the observation, hypothesis and test; collect shared assumptions in one methods block. Repeated reminders that an idea is not a translation, not a discovery, or not automatically evidence interrupt the argument. State publication priority in related work and evidential scope in the appropriate methods section.

Since 12 October we have stated claims more boldly. Conjectures and the working model are written in the indicative, as if true: "Sign 740 closes a title", not "sign 740 may possibly be associated with". The uncertainty is carried by one credence number and by the predictions, so the claim itself needs no qualifying phrases. A report states what was measured and then the boldest reading the measurement supports, with the test that would decide it; it does not stop at what was not established.

Write about the project in its own voice. Say "we" or "the project", and state a rule or priority directly: "Our first priority is a complete record of every object", "The project has no CI/CD, and none should be added". Phrases such as "the owner's priority", "the user wants" or "the user said" read as private notes passed between assistants, and they leave a newcomer unsure who is speaking. Name a person only where the record needs it, such as an author, a reviewer or the maintainer who approved a purchase or a release.

Keep source titles and direct quotations accurate even when their wording breaks these preferences. A bibliographic title is evidence, not prose we are free to rewrite.

## Problems in AI-assisted academic prose

On 13 October 2026 we reviewed recent research on how model-written academic text differs from human writing and checked our published prose against it. The surface habits from the October 2 rules were nearly gone: in about 99,000 words of papers, cards and knowledge pages we found no em dashes, no "utilize" or "leverage" and 29 stock adjectives in total. What remained were the deeper problems below. They are the ones a first-time reader of the README tripped over, and Wikipedia's guide to signs of AI writing makes the same point: the surface patterns are symptoms, and the fix is to repair the clarity and accuracy beneath them ([Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)).

### Dense, noun-heavy sentences

Reinhart and colleagues (2025, *PNAS* 122(8)) found that instruction-tuned models write more nominalisations and participial clauses than human writers in the same genre, producing informationally dense prose ([summary of the literature](https://www.refsmmat.com/notebooks/llm-style.html)). In our papers this takes the form of slash compounds and stacked modifiers: "shuffles exact length/slot columns within site/type strata". Unpack such phrases into a subject, a verb and an object, give each sentence one new idea, and replace slashes with words.

### Private vocabulary

Labels coined during a working session reach published text without a definition: "known-slot masks", "crossing windows", "held export", "table laws", "domain failures", "witness", "endpoint". Users of recent coding models report the same habit of shorthand, nicknames and jargon in their explanations ([OpenAI community thread](https://community.openai.com/t/chatgpt-5-is-worse-at-coding-overly-complicates-rewrites-code-takes-too-long-does-what-it-was-not-asked/1340535)). Define a technical term in plain words the first time it appears in each document, or replace it with the description. Keep a coined label only when the text uses it repeatedly, and define it where it is introduced.

### No guidance for the reader

Jiang and Hyland (2025, *English for Specific Purposes* 79) found ChatGPT essays well organised but much poorer in hedges, boosters, attitude markers and other ways of addressing the reader, which gives an impersonal, expository tone ([abstract](https://ueaeprints.uea.ac.uk/id/eprint/99123)). In our papers a paragraph often lists results without saying what they show. Open a paragraph with the point it makes, say what a number means for the question, and use "we" for the authors' actions and judgements.

### Formal words and a shared template

Miletić and Falk (2026) measured how LLM editing changed NLP papers: formal or specialised words replaced plain ones ("utilize" for "use", "subsequently" for "then"), words grew longer, vocabulary narrowed, and negations and dashes increased ([arXiv:2605.19936](https://arxiv.org/abs/2605.19936)). Several of our introductions share one template, a paragraph beginning "X are established methods" and ending "The present contribution is". Choose plain verbs, and let each paper's structure follow its own argument.

### Defining by negation

Negative parallelisms ("not X but Y", "Y rather than X") and closing "challenges" paragraphs are listed in the Wikipedia guide. Our papers repeat sentences about what a result does not establish. Say once, in the methods or scope paragraph, what was measured and where it applies; elsewhere state what was found.

### Inflated significance

Trailing "-ing" clauses that assign importance ("highlighting…", "reflecting…"), "serves as" in place of "is", lists of three made up for rhythm, title-case headings and bold run-in headings are rare here; keep checking for them.

### Citation errors

Ansari (2026) classified 100 fabricated citations in 53 papers accepted at NeurIPS 2025: 66% invented outright and 27% real-looking entries with a wrong author, title or year ([arXiv:2602.05930](https://arxiv.org/abs/2602.05930)). Every work we cite must exist, and its authors, title, year and link must match. A link label should name the work, "Phipson and Smyth (2010)", not describe it, "primary rank source".

## Examples from this project

| Avoid | Prefer |
|---|---|
| "Our rigorous framework unlocks robust insights into the script." | "The model's exact top-one accuracy was 33.8%, compared with 17.0% for the baseline." |
| "This isn't just prediction. It's a revolution in understanding." | "The result measures graphic prediction. Its relation to lexical meaning remains untested." |
| "Importantly, the rich tapestry of contextual evidence warrants further exploration." | "The catalogue gives a site and object type, but does not identify the find layer for this object." |
| "The results highlight the need to leverage innovative methods." | "The gap-count estimator scored 46.3%; always guessing one scored 51.1%. A retry needs a new predictor or additional physical gap evidence." |
| "Its main reference shuffles exact length/slot columns within site/type strata and rebuilds physical/text groups, folds and model selection for every proposal." | "For the chance comparison we moved signs between inscriptions of the same length, site and object type, keeping each sign at its position in the text. For every shuffled corpus we rebuilt the groups of related records and the cross-validation folds, and repeated model selection." |
| "Missing-count prediction fails its comparator." | "Our estimate of how many signs are lost in a gap was right less often than always guessing one sign." |

Run [the manual prose scan](../../tools/review_prose.py) to flag likely stock phrases, then inspect each passage. The script does not detect authorship and cannot judge scientific clarity. Editing must preserve numbers, estimands, citations and source uncertainty.
