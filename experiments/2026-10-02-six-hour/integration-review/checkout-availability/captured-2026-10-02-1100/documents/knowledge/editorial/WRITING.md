# Writing rules

The user requested plain writing throughout the repository on October 2, 2026. These rules apply to new manuscripts, methods, notes and future edits. Historical evidence is preserved unchanged; its original wording remains part of the record.

## What the recent sources actually support

Tom Babb's March 2026 critique identifies repeated sentence openings, stock oppositions, inflated headings and claims without concrete details. It is a writer's account of patterns he dislikes, rather than a controlled comparison of models. [Article](https://www.linkedin.com/pulse/removing-em-dash-did-fix-your-ai-writing-tom-babb-9txac).

August 2026 discussion extends the complaint to sentence fragments, decorative metaphors, forced three-item lists and closing recaps. The [source summary](https://notes.nicolasdeville.com/nicai/ai-writing-tells/) discloses that it was drafted by an AI assistant; it points to [Ruben Hassid's original post](https://x.com/rubenhassid/status/2087856703773508025). We use these as editorial suggestions, with that provenance visible. We do not accept their claims about model training or automatic authorship detection as established facts.

There is also empirical evidence of shifts in scholarly vocabulary after LLM adoption. Kobak and colleagues analyzed more than 15 million biomedical abstracts; this supports checking habitual style words in aggregate, without treating any word as proof of authorship. [Science Advances paper and author version](https://arxiv.org/abs/2406.07016v5). A January 2026 study examines writing complexity and scientific production; its conclusions concern a defined observational analysis. [Author preprint](https://arxiv.org/abs/2601.13187).

This search did not establish a controlled comparison of the writing habits of every newest model release. The changes below follow the user's preference and identified editorial problems; they do not depend on an AI detector.

## Editing decisions

Write the finding early. Give the observation, result or action, followed by the evidence needed to understand it. A sentence should name its subject and say what happened.

Replace claims of quality with details. State the split rule, measured gain, null design or source check instead of calling the work rigorous, powerful, robust or groundbreaking. Use technical terms when they distinguish an actual method. A bootstrap confidence interval, an inverse problem and minimum-cost flow are legitimate terms.

Cut stock openings, promotional verbs and statements about importance. Avoid "delve", "leverage", "foster", "unlock", "game changer", "seamless", "tapestry", "it's worth noting", "the key takeaway", "here's the thing" and "in conclusion". The research does not need to praise itself.

Explain the result directly. Avoid rhetorical constructions that dismiss an alternative merely to make the preferred description sound stronger. Where a comparison matters, name both measurements or assumptions and explain the difference.

Use paragraphs with connected sentences. Avoid a series of short dramatic fragments, repeated openings or one-sentence paragraphs written for emphasis. Do not manufacture three parallel items when the evidence supplies a different number.

Use tables for real comparisons and lists for steps or parallel observations. Paper sections and methods headings should help navigation. Do not add headings to make a short answer look substantial.

Keep punctuation ordinary. Prefer periods and commas to repeated em dashes. Do not introduce errors, awkward phrasing or needless synonyms to imitate a human author.

State uncertainty where it changes the claim. Keep the source, scope and unresolved premise close to the relevant result. Remove repeated generic caveats that add no new information. Preserve genuine statistical intervals, measured ranges and archaeological dating uncertainty.

The user also rejected repeated corrective comparisons in the archaeology memo. Assume an attentive reader. Develop the observation, hypothesis and test; collect shared assumptions in one methods block. Repeated reminders that an idea is not a translation, not a discovery, or not automatically evidence interrupt the argument. State publication priority in related work and evidential scope in the appropriate methods section.

Keep source titles and direct quotations accurate even when their wording breaks these preferences. A bibliographic title is evidence, not prose we are free to rewrite.

## Examples from this project

| Avoid | Prefer |
|---|---|
| "Our rigorous framework unlocks robust insights into the script." | "The model's exact top-one accuracy was 33.8%, compared with 17.0% for the baseline." |
| "This isn't just prediction. It's a revolution in understanding." | "The result measures graphic prediction. Its relation to lexical meaning remains untested." |
| "Importantly, the rich tapestry of contextual evidence warrants further exploration." | "The catalogue gives a site and object type, but does not identify the find layer for this object." |
| "The results highlight the need to leverage innovative methods." | "The gap-count estimator scored 46.3%; always guessing one scored 51.1%. A retry needs a new predictor or additional physical gap evidence." |

Run [the manual prose scan](../../tools/review_prose.py) to flag likely stock phrases, then inspect each passage. The script does not detect authorship and cannot judge scientific clarity. Editing must preserve numbers, estimands, citations and source uncertainty.
