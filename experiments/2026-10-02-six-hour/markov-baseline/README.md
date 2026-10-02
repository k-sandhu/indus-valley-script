# A conventional Markov comparison on the existing masks

On the same 8,009 deliberately hidden signs, the new first-order Markov comparator reached **34.59% exact top-one** and **58.46% top-five**. The existing bidirectional position/metadata model (PMB) reached 33.81% and 55.34%. All record/slot identities, truths, physical/text groups and outer folds match the preserved benchmark. These measurements favor keeping the simpler Markov model as a baseline for future restoration work.

The [protocol](PROTOCOL.md) was written before fitting. [Results](main/results.json) retain every tuning score, source hash, summary and component interval. [Predictions](main/markov_slot_audit.jsonl) retain top-ten suggestions for each mask. The [independent verification](verification.json) checks all 8,009 queries from a second implementation of the count formulas.

| Metric | Position/metadata PM | First-order Markov | Bidirectional PMB |
|---|---:|---:|---:|
| Exact top-one, all slots | 16.99% | 34.59% | 33.81% |
| Exact top-five, all slots | 35.50% | 58.46% | 55.34% |
| Exact top-ten, all slots | 45.57% | 65.43% | 62.70% |
| Exact top-one, equal text weight | 17.36% | 33.35% | 32.60% |
| Exact top-one, equal true-code weight | 0.63% | 4.80% | 5.13% |
| Exact top-five, equal true-code weight | 3.17% | 12.17% | 10.44% |
| Bucket cross-entropy, bits per slot | 7.135 | 5.119 | 5.748 |
| Five-bin expected calibration error | 2.04% | 2.56% | 8.05% |

The Markov–PM top-one improvement was 17.59 percentage points, with a paired component-bootstrap 95% interval of 16.38–18.83. PMB–Markov was −0.774 points, with interval −1.596 to +0.050; this comparison leaves a small range spanning zero. The corresponding top-five difference was −3.121 points, with interval −3.859 to −2.376. Equal-text top-one difference was −0.754 points, with interval −1.596 to +0.085. The model ranking therefore survives equal text weighting, while its top-one uncertainty is wider than its observed difference.

PMB's equal-code top-one score was slightly higher, by 0.334 points, with interval −0.174 to +0.884. Its equal-code top-five score was lower by 1.731 points, with interval −2.549 to −0.942. These intervals use true-code frequency weights fixed from the complete benchmark, followed by component resampling. The type weighting gives rare codes much more influence than slot weighting does.

## Where the performance comes from

There are 548 true-code types in this benchmark. Of these, 76 occur at least 20 times and account for 6,401 slots, about 80% of the total. Markov top-one accuracy in that common-code group was 42.20%, compared with PMB's 41.07%. For codes occurring 5–19 times, the scores were 6.86% and 7.27%; for codes occurring 2–4 times, 0.24% and 1.70%. All 205 singleton codes were absent from their training folds and received zero exact successes in either model. The 3.13% unseen-target rate is identical across models.

The Markov model's highest confidence bin contained 581 masks. Mean top mass was 89.97% and exact accuracy was 89.85%. PMB placed 851 masks in that bin, with mean top mass 89.60% and exact accuracy 83.78%. Its middle bin, [.4,.6), had mean mass 49.15% and accuracy 38.44%; the Markov values were 48.75% and 48.31%. The complete five-bin curves are saved in `results.json`.

The top-label Brier scores were 0.1241 for PM, 0.1653 for Markov and 0.1728 for PMB. Each score measures the correctness event for that model's own chosen label, so their event frequencies differ. Use the bucket log loss for a shared outcome score and the confidence curves to inspect calibration. PMB's bucket loss exceeded Markov's by 0.628 bits per slot, with paired 95% interval 0.579–0.679.

## Model and scope

The comparator learns one position-independent transition matrix, an initial distribution and end-of-text transitions. It combines predecessor and successor likelihoods for every internal mask. At the boundaries it uses the initial distribution or the end transition. Each outer training set selected smoothing 20 from the prespecified 20/100/500/2000 grid using three grouped inner folds. The existing PM and PMB predictions were reused without refitting.

The [2009 Rao et al. model](https://homes.cs.washington.edu/~rao/PNASIndus.pdf) establishes this conceptual family of sign restoration. Our comparator uses the present fine-code corpus and unigram-prior smoothing; its alphabet and smoothing differ from that paper. The figures here belong to the present artificial one-known-slot benchmark, with intact surviving transcription, known string length and conditional intervals for the saved fits. They do not estimate the accuracy of restoring an eroded archaeological object.

The next model comparison should separate the effect of end-state modeling from the effect of metadata multiplication, and should include a declared Kneser–Ney implementation. The current run provides a fixed baseline and concrete score targets for those experiments. Its predictions and protocol remain available even if a later model improves them.

## Reuse

Run the [script](../../../src/six_hour/markov_baseline.py) from repository root, choosing a fresh directory whose parent contains a copy of the protocol:

```powershell
python src/six_hour/markov_baseline.py --self-test
python src/six_hour/markov_baseline.py --output experiments/NEW-DATE/markov-baseline/main
```

The main run took 10.69 seconds on the recorded environment. [The retrospective](RETROSPECTIVE.md) documents the implementation, verification and comparison choices. The verification command deliberately refuses to replace its existing audit record.
