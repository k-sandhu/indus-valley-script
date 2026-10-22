# Retrospective: REBUS-BLIND-TEMPLATES-2026-10-22

## Approach

The base-rate study of 21 October left one question open: whether Parpola's rebus interlocks measure the language of the script or the number of sign sequences he examined. We answered it with his own word assignments on sign pairs he did not choose. The work had three parts: a source check that turned his published identifications into a table of signs, ICIT codes and Tamil words; a corpus step, through the shared shots loader, that listed the sign pairs; and a scoring step that reused the base-rate study's compound index, tolerances and matched replacement pools unchanged.

## What happened

**The 1994 book.** Prediction P1 names the identifications of *Deciphering the Indus Script* (1994). The Internet Archive holds the book only as a restricted lending copy, and the other copies there are user uploads with unverified rights, so we did not use them. Four later papers by Parpola were open (journal.fi for *Studia Orientalia* 1997; harappa.com for the 2005, 2008 and 2009 papers) and restate the 1994 readings; with the 2010 paper already held, they gave 16 usable signs. The deviation from the card's wording is recorded in the protocol.

**Extraction.** Five subagents read one paper each and wrote structured records with page numbers and short locators, under an instruction not to open any dictionary or the *Tamil Lexicon* tables. Two papers print Dravidian forms in an ASCII scheme without the Tamil alveolars (*miin*, *aru*); we took each form from the paper that prints it with diacritics (Parpola 1997 prints *mīṉ*, *aṟu-mīṉ*). One extraction flagged that the 2010 picture for the two long strokes was chosen after the compound search had produced *veḷ*; we kept the word as his assignment and excluded every pair that search used.

**From sign names to codes.** Parpola names signs by their pictures and gives list numbers for only four of them, and the project has no crosswalk from his numbers to the ICIT codes of the corpus. We fixed codes by reading, in the corpus file, the 45 objects he cites by CISI number and taking the code at the position he describes (H-669 gives 032 + 220 for 'two long strokes' + 'fish'; H-177 gives 151 for the yoke-carrier). The 'bull's head' needed the page image: the glyph printed in Parpola 1997 is the sign other lists call the 'jar', ICIT 740. The spear and the *kaḷam* sign could not be coded, because Parpola cites them only by Koskenniemi–Parpola text numbers or not at all.

**The split and the freeze.** We created a new split in the spending ledger, counted pairs on the discovery half to confirm that at least 20 recurring blind pairs exist (27 per half), wrote the protocol and predictions, ran the synthetic selftest, registered and froze the shot with 15 artifacts, and read the confirmation half once. The template list (38 primary, 24 gapped, 12 published pairs) was hashed in `FREEZE.json` before the scorer ran. The scorer took 34 seconds.

**A speed change before the freeze.** The first scorer called the base-rate `picture_hits` for every replacement pair, which repeats the same normalisation thousands of times. Before freezing we replaced it in the boolean path with cached sets of normalised members and added a selftest check that the cached search equals `picture_hits` on every pair of 65 words under both tolerances and all directions; `picture_hits` still produces the detail listing.

**The independent check.** `verify.py` rebuilt the compound index, pools and rates from the segmentation of the base-rate study's own verifier. It reproduced every hit and the ratio, and disagreed on one pool boundary word for *kōḷ*. The cause is that the two segmentations treat six rare-diacritic headwords differently (4,128 against 4,134 candidates), which shifts the standard deviations used for matching. The frozen code is the base-rate study's verified `rebus.py`, so we kept the result and recorded the difference.

## What remains unresolved

The frequency proxy of the base-rate study counts Sangam tokens that begin with a word's Tamil stem, and for one-syllable words such as *kā* and *ā* the stem is a single letter, so their frequencies (22,287 and 4,458) count every token with that initial. Their replacement pools are matched to very common words. This affects the bull's-head and yoke-carrier templates, which carry five of the nine hits.

The *Tamil Lexicon* resolved *aṟu* to the headword *aṟṟu* through the length- and gemination-free fallback, because *aṟu* is not a one-word noun headword there. The interval on the primary ratio (0.93–2.72) is wide; 38 templates cannot tell an effect of 1.8 from 1 or from 2.5.
