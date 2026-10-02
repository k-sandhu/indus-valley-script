# Independent-annotator compatibility-event test

This exploratory design was written after the main derivative-corpus structural/restoration results, but before this test's outcomes. Creation time is in the final manifest.

Use all Mayig faces explicitly marked clear, single-line, and at least three glyphs. Do not select them by agreement with Lipi. P identifiers are the Mayig annotator's own IDs. Map each to its SET of Wells candidates by inverting the published catalogue compatibility table; this is not a transitive equivalence relation or a fine-glyph truth assignment.

Exclude from Lipi training every artifact/text component touched by any source-CISI object in the complete179-object Mayig corpus, including damaged/excluded faces. Never infer object identity from coincident numeric row IDs. Remove all test source objects even if their transcriptions disagree.

Additional conservative rule before fitting: exclude every training component containing ANY fine-code sequence compatible at every position with an eligible Mayig candidate-set text. Otherwise a broad catalogue variant could permit a duplicate whole graphic text into training despite differing fine codes. This may exclude genuinely distinct texts too; report its size. Use M1..M199 as a conservative source range because the179-object source is a subset of that printed series.

Fit independent position/site/type and normalized previous-sign models on the remaining unique complete RTL texts, selecting smoothing by grouped inner folds. For each Mayig glyph, sum over all supported fine-code candidates. Compute the probability of the observed candidate-set event at each slot conditional on earlier observed candidate sets using a forward recursion. The alphabet remains training-only. Do not count the UNKNOWN bucket as a compatible identified glyph. Record unsupported/OOV candidates and exclude texts with no supported path; report every exclusion.

Compare mean log-event probability in bits per noninitial glyph, with a whole-P-text/artifact cluster bootstrap conditional on the fitted models. Candidate events can overlap across different P IDs; this is an event score, not a normalized predictive distribution over Mayig labels. No p-value or population accuracy claim is made. This is an independent annotator check on the same archaeological sources, not independent ancient evidence. The crosswalk itself remains shared catalogue interpretation.

Validate the forward recursion against enumeration of all fine-code paths on small artificial candidate sets, and against exact Model.score for singleton candidates. Report the all-clear eligible population, candidate coverage, source-removal count, and any sign-height discrepancy. This test cannot identify words or sounds.
