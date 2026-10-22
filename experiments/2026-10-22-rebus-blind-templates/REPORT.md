# REBUS-BLIND-TEMPLATES-2026-10-22: Parpola's word assignments on sign pairs he did not choose

Status class: `frozen-evaluation`. The protocol, predictions, identifications and code were frozen through `bench.shots` before the confirmation half was read (protocol SHA-256 `2c022902…7389`, predictions `849ec375…d314`), and the template list was frozen before any Tamil compound was looked up for it ([FREEZE.json](FREEZE.json); `templates-v1.json` SHA-256 `8ddc7d2a…2553`). Verification tier: submitted.

Date and contributors: 22 October 2026. Claude (Opus 5.5, `claude-opus-5-5`, Claude Code desktop harness), in a session started from the session that ran REBUS-BASE-RATE-2026-10-21. Five subagents of the same model extracted the identifications from Parpola's papers.

## Results

On 38 Indus sign pairs that Parpola never published, his Dravidian words form an attested *Tamil Lexicon* compound for 9 pairs (23.7%, Wilson interval 13.0–39.2%). Random words matched on compounding productivity and Sangam frequency do so for 4.97 pairs on average (13.1%). The ratio of hit rates is 1.81, with a 95% bootstrap interval over templates of 0.93–2.72, and it stays between 1.64 and 1.98 when any one pair is removed ([templates.json](results-v1/templates.json) `#/results/primary`). The frozen rule for prediction P1 of [C-0014](../../knowledge/conjectures/C-0014-parpola-interlocks-measure-the-lexicon.md) asks for a ratio below 2 that stays below 3 without any one template, so P1 passes. The kill condition, a ratio of at least 3 with the lower bound above 1.5, is far away. Of 10,000 random keys that replace every word at once, 6.7% reach nine successes.

Parpola's own twelve published pairs, scored with the same code, succeed seven times against 1.15 expected, a ratio of 6.1 (2.8–11.7; `#/results/published_shape_C`). His published pairs thus succeed at 58% and the pairs he did not choose at 24% (one-sided Fisher test p = 0.032; post-outcome, [exploratory.json](exploratory-v1/exploratory.json) `#/E1_published_vs_blind`). At the blind rate, seven successes in twelve attempts has a probability of 0.010, while seven successes become more likely than not after about 28 attempts (`#/E3_templates_needed`). The published network therefore looks like the survivors of roughly thirty tried sign pairs, which is the selection the base-rate study could only infer.

The hidden-member search that produced *veḷ* in 2010 is uninformative on blind pairs: compounds W1-X and X-W2 share a member for 22 of 24 gapped pairs with Parpola's words and for 82% of random replacements (ratio 1.11; `#/results/gapped_shape_S`).

## What the hits are

The nine blind successes (local detail file, glosses read after the outcome) are mostly the same homophone coincidences that random words enjoy. The 'bull's head' word *āṉ* 'cow' succeeds through *veḷ-ḷ-āṉai* 'white elephant' and *āṉai-k-kā*, a Śiva shrine, because *āṉai* 'elephant' shares the stem of *āṉ*; *āvu* 'cow' succeeds through *nīr-āvi* 'steam' and *kaṇ-ṇ-āvi* 'evil eye', where *āvi* is 'vapour'; *veḷ* succeeds through *oru-vēḷai* 'once' and *nīr-veḷḷai*, a paddy variety. One success reads as the pictures say: 'two' + 'eye' is *iru-kaṇ*, glossed 'eye of the body and eye of the mind'. 'Fish' + 'crab' gives *mīṉ-koḷḷi*, which the Lexicon glosses only by cross-reference. The tolerance that allows these matches is the one Parpola's published readings need (*vaṭa-mīṉ* from *vaṭam*, *veṇ-mīṉ* from *veḷ*), and the random words receive it on equal terms.

## Primary result and sensitivities

| Set | Templates | Parpola's hits | Expected random hits | Ratio (95% interval) |
|---|---|---|---|---|
| Primary: adjacent pairs, stated tolerance T0s, pools of 50 | 38 | 9 | 4.97 | 1.81 (0.93–2.72) |
| Practised tolerance T1s | 38 | 11 | 7.06 | 1.56 (0.95–2.20) |
| Pools of 25 | 38 | 9 | 5.50 | 1.64 (0.83–2.42) |
| Pools of 100 | 38 | 9 | 3.83 | 2.35 (1.26–3.54) |
| Picture word as first member only (the shape of *vaṭa-mīṉ*) | 38 | 8 | 3.30 | 2.42 (1.03–3.88) |
| Without *mīṉ* and *muruku*, whose compounds the base-rate study listed | 26 | 8 | 4.36 | 1.84 (0.94–2.77) |
| Without the 'bull's head' (post-outcome) | 26 | 4 | 2.55 | 1.57 (0.39–2.90) |
| Gapped pairs, shared member (shape S) | 24 | 22 | 19.79 | 1.11 (1.01–1.23) |
| Parpola's published pairs | 12 | 7 | 1.15 | 6.11 (2.84–11.70) |

Two sensitivities put the ratio above 2: wider pools of 100, whose random words are less productive, and the one-directional search. None comes near the kill. Every estimate sits between 1.5 and 2.5, so Parpola's words on unselected pairs do somewhat better than matched random words, by a factor the data cannot yet separate from 1 or from 2.5. The bull's-head templates carry five of the nine hits; without them the ratio is 1.57.

The power simulation frozen with the protocol ([power.json](power-v1/power.json)) shows what a pass at this sample size is worth. With 40 templates and a random rate of 0.10, close to the observed 38 and 0.13, a key with no lexical advantage passes in 95% of simulations, a key twice as good as chance in 45%, and a key three times as good in 5%, while the kill catches the last in 51%. The pass is therefore strong evidence against an effect of three and says little about effects near two.

## Identifications used

Parpola's 1994 book was not available with clear rights (the Internet Archive copy is lending-only), so the identifications come from five of his papers that restate the 1994 readings: *Studia Orientalia* 82 (1997), the Tokyo lecture of 2005, *Airāvati* (2008), *Scripta* 1 (2009) and the 2010 Chennai paper ([SOURCES.json](SOURCES.json)). Sixteen signs have a Dravidian word and an ICIT code fixed by an object Parpola cites ([identifications-v1.json](identifications-v1.json)): fish *mīṉ*, numerals one, two, six and seven, fig tree *vaṭam*, spindle *katir*, intersecting circles *muruku*, squirrel *piḷḷai* and *aṇil*, two long strokes *veḷ*, crab *kōḷ*, eye *kaṇ*, water *nīr*, hind leg *tāḷ* and *tōḷ*, bull's head *ā*, *āṉ* and *āvu*, and yoke-carrier *kā*, *kāvu* and *kāvaṭi*. The 'bull's head' is the sign other lists call the 'jar' (ICIT 740), as the glyph printed in Parpola 1997 shows. The spear and the *kaḷam* sign are left out because Parpola cites no object by CISI number for them; the scorpion, oval and cart because he finds none of his words satisfactory.

The 38 primary pairs are every ordered adjacent pair of two different identified signs that recurs in at least two distinct texts across both halves of split `d1d1b920…`, after removing Parpola's twelve published pairs and the numeral-and-fish pairs whose outcome the base-rate study reported ([templates-v1.json](templates-v1.json)). The confirmation half was read once through the loader for the pair counts, and the spending ledger records the family `rebus_template_pairs` for this split.

## Protocol before outcome

[PROTOCOL.md](PROTOCOL.md) fixed the sources and the extraction rules, the inclusion and coding rules for signs and words, the template shapes, the selection rule with its threshold, the exposure sensitivity, the matched null (the base-rate study's candidates and pools of 50 nearest native nouns), exact or Monte Carlo random rates, random keys, the bootstrap and leave-one-out statistics, the pass and kill rules with influence conditions, the joint credence rule and the power simulation. [PREDICTIONS.json](PREDICTIONS.json) registers P1 and two reported-only sets. The synthetic selftest ([selftest.json](selftest-v1/selftest.json)) checked compound detection in both directions and through sandhi, the shared-member search, the agreement of the cached search with the base-rate `picture_hits` on every pair of 65 words, exact against Monte Carlo rates, a planted key (killed, ratio 60) and an unplanted key (not killed). The shared bench selftest and the shots synthetic mode pass ([bench-selftest-v1.json](bench-selftest-v1.json), [shots-synthetic.json](shots-synthetic.json)).

## Commands and outputs

Run from the repository root with Python 3.13 and NumPy 2.2.6; the *Tamil Lexicon*, DEDR and Sangam tables are those of REBUS-BASE-RATE-2026-10-21, held locally.

```text
python experiments/2026-10-22-rebus-blind-templates/code/acquire.py
python experiments/2026-10-22-rebus-blind-templates/code/power.py experiments/2026-10-22-rebus-blind-templates/power-v1/power.json
python -m bench shots --action create --split experiments/2026-10-22-rebus-blind-templates/round.json --seed 2026-10-22-rebus-blind-templates --out experiments/2026-10-22-rebus-blind-templates/split-summary.json
python experiments/2026-10-22-rebus-blind-templates/code/pairs.py experiments/2026-10-22-rebus-blind-templates/identifications-v1.json discovery experiments/2026-10-22-rebus-blind-templates/discovery-v1/pairs.json
python experiments/2026-10-22-rebus-blind-templates/code/selftest.py experiments/2026-10-22-rebus-blind-templates/selftest-v1
python -m bench selftest --out experiments/2026-10-22-rebus-blind-templates/bench-selftest-v1.json
python -m bench shots --synthetic --directory experiments/2026-10-22-rebus-blind-templates/shot-fixtures --out experiments/2026-10-22-rebus-blind-templates/shots-synthetic.json
python -m bench shots --action register --split experiments/2026-10-22-rebus-blind-templates/round.json --shot rebus-blind --predictions experiments/2026-10-22-rebus-blind-templates/PREDICTIONS.json
python -m bench shots --action freeze --split experiments/2026-10-22-rebus-blind-templates/round.json --shot rebus-blind --artifact ... (15 artifacts, listed in round.json)
python experiments/2026-10-22-rebus-blind-templates/code/pairs.py experiments/2026-10-22-rebus-blind-templates/identifications-v1.json confirmation experiments/2026-10-22-rebus-blind-templates/confirmation-v1/pairs.json --shot rebus-blind
python experiments/2026-10-22-rebus-blind-templates/code/build_templates.py experiments/2026-10-22-rebus-blind-templates/identifications-v1.json experiments/2026-10-22-rebus-blind-templates/discovery-v1/pairs.json experiments/2026-10-22-rebus-blind-templates/confirmation-v1/pairs.json experiments/2026-10-22-rebus-blind-templates/templates-v1.json
python experiments/2026-10-22-rebus-blind-templates/code/freeze.py
python experiments/2026-10-22-rebus-blind-templates/code/run_templates.py experiments/2026-10-22-rebus-blind-templates/templates-v1.json experiments/2026-10-22-rebus-blind-templates/results-v1
python experiments/2026-10-22-rebus-blind-templates/code/verify.py experiments/2026-10-22-rebus-blind-templates/templates-v1.json experiments/2026-10-22-rebus-blind-templates/results-v1 experiments/2026-10-22-rebus-blind-templates/verification-v1.json
python experiments/2026-10-22-rebus-blind-templates/code/exploratory.py experiments/2026-10-22-rebus-blind-templates/results-v1 experiments/2026-10-22-rebus-blind-templates/exploratory-v1
```

Seeds: 20261022 for the scorer and power simulation, 20261023 for the exploratory bootstrap. Output hashes: `results-v1/templates.json` `81075cb2…c91a`, `FREEZE.json` `4f769b1f…84eb5`, `confirmation-v1/pairs.json` `5456f6c7…646c`, `verification-v1.json` `c8e256fc…1005`, `exploratory-v1/exploratory.json` `9c239cb6…6b86`. The compounds behind each hit are in the local detail file whose path and hash `templates.json` records.

## Challenges and repairs

The acquisition, the source decision on the 1994 book, the mapping of Parpola's sign names to ICIT codes and the single disagreement of the independent check are described in the [retrospective](RETROSPECTIVE.md). The independent check reproduces Parpola's nine hits template by template, all but one replacement pool and the ratio (1.79 against 1.81). The exception is the first-slot pool of *kōḷ*, where one boundary word differs (*antu* against *pēy*) because the two implementations segment six rare-diacritic headwords differently (4,128 against 4,134 candidates); two random rates move by less than 0.005. The frozen code is the base-rate study's verified segmentation, and no amendment was needed.

## Decision and next evidence

Within this protocol, P1 of C-0014 passes: on sign pairs Parpola did not choose, his word assignments form attested Tamil compounds 1.8 times as often as matched random words, below the frozen threshold of 2 and far from the kill at 3. His published pairs succeed 3.4 times as often as his blind pairs relative to chance (bootstrap interval 1.4–8.7), which measures the selection behind the 2010 network directly. The hidden-member template is uninformative on any pair, since random words find a shared member 82% of the time.

Do not rerun this test unchanged on the same identifications and dictionary. A revisit is justified by Parpola's full 1994 identifications, which would add signs and pairs and narrow the interval on the ratio, by a second Tamil dictionary with compounds, or by a control language for the same pictures.

## The boldest reading and the test that would decide it

Parpola's Dravidian network is a product of search. On pairs he did not choose, his words do about as well as the words of any reader who brings a large compound dictionary and a tolerance for vowel length, sandhi and stem endings: they succeed on a quarter of pairs, and most successes pair his word with an unrelated homophone, an elephant for a cow and a time of day for whiteness. His published pairs succeed on more than half, a rate he would reach by trying about thirty pairs and publishing the seven that worked. What the blind test leaves standing is a modest excess, about 1.8 times chance, concentrated in basic vocabulary such as *iru-kaṇ* 'two eyes'.

That excess has two explanations, and a cross-language control separates them. If it is Dravidian, it belongs to his words; if it is the procedure, any language's words for the same pictures will show it, because words for eyes, water, numbers and cattle combine with one another in every lexicon. The deciding test gives the same 38 sign pairs the Sanskrit or Prakrit words for Parpola's pictures and scores them against the compounds of a Sanskrit dictionary that lists them (Monier-Williams in the Cologne edition), with random Sanskrit words matched on compounding productivity. A Sanskrit ratio near 1.8 shows the excess comes from the pictures and the procedure, and C-0014 then holds in full; a Sanskrit ratio near 1 while the Tamil ratio stays near 1.8 would be the first evidence from unselected pairs that the script's pictures fit Dravidian better than another candidate language.

## Review and verification

[verification-v1.json](verification-v1.json) recomputes, without importing the measurement code, the compound index, every Parpola hit, every replacement pool, the random rate of every template and the ratio; it agrees except for the one pool and two rates described above. The synthetic selftest, the bench selftest and the shots synthetic mode pass. No other contributor has reproduced or reviewed this package.
