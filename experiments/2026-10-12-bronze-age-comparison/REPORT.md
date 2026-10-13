# What the four-language comparison found

12 October 2026 UTC. The study acquired and analyzed Sumerian, Akkadian, Egyptian and Mycenaean Greek source records, then applied the same structural calculation to IVS. The [manuscript](MANUSCRIPT.md), [exact tables](TABLES.md), [methods](METHODS.md) and [claim map](CLAIM-EVIDENCE.json) retain the evidence behind this account.

## The useful parallel is record organization

Understood Bronze Age writing traditions contain short, conventional records. Our sources include Sumerian accounts and seal texts, Egyptian vessel labels, Akkadian letters/accounts and Greek economic documents. Their ordering survives references that shuffle each record while preserving its length and units. All eleven testable cohorts pass the adjusted 5% threshold; the tiny Akkadian seal cohort has no testable frequent type. IVS also has strong ordering under that reference. This supports studying how records organize information, with their different encodings and genres kept visible. [Structural output](run-v2/structural-results.json).

The Egyptian vessel case is especially concrete: its edition identifies a ceramic carrier, gives late third-millennium source dating, and annotates a short text with a commodity, named people and kinship terminology. Such a label can rely on knowledge outside the text. The study therefore makes identity, recipient, goods, amount and authority useful alternatives to test on Indus carriers. [Source observations](observations.json).

## The known-category tests expose what the methods need

| Tradition | Measured result | What the result covers |
|---|---|---|
| Sumerian | Word-category context accuracy 90.41%, identity-only 81.79%, position 69.73% | 759 edited records/modules and 3,806 scored source-tagged tokens. Most targets are named entities or nominal forms. |
| Akkadian | Context and identity both score 50% on 50 whole-record word targets | Eight whole-record groups. The four-group complete sign population cannot support five folds; readable lines supply a separate extension. |
| Egyptian | Vessel word-category context accuracy 97.00%, identity-only 95.09% | 302 complete edited vessel texts, 1,202 scored targets; recurring words explain much of the success. |
| Mycenaean Greek | Corrected word/logogram context accuracy 83.92%, identity-only 69.23% | 25 documents and 143 targets. The key distinguishes syllabic forms, logograms and numerals. |

Source tags train these calibrators; held-out tags, readable identities and glosses do not enter prediction. A harder follow-up hides word boundaries and tests anonymous signs/readings. It retains positive contextual results, strong identity baselines and insufficient-data outcomes. [Word controls](run-v2/category-results.json), [sign controls](sign-control-v2/results.json). Their populations differ, so their accuracies do not measure a causal effect of boundary deletion.

## Simple word patterns fit all four inventories

We tested a restrictive hypothetical rule: one IVS face is one word, with an independently chosen unit correspondence for every candidate. With 200 observed spellings sampled from each source inventory, compatible equality patterns cover 92.02% of IVS targets for the Sumerian cohort, 97.13% for the Akkadian document cohort, 96.93% for Egyptian and 91.16% for Greek on average. Multiple candidates remain common. The test concerns repeated-unit positions and supplies neither sounds nor a consistent reading key. [Compatibility, ambiguity and global cardinality bounds](run-v2/lexical-ambiguity.json).

These observations favor a next study that predicts independently observed record use or quantity and requires a shared interpretation across objects. A high dictionary-fit fraction by itself provides little discrimination. The existing Sanskrit windows have different units and mapping premises, so the current comparison does not combine them into a preferred-language score.

## Source corrections and reusable results

The source review repaired separate seal surfaces, ordinary rulings, Egyptian numeric glyph entities and Greek uncertainty hidden in search links. Initial attempts and numerical runs remain preserved. The corrected Greek cohort is smaller, and every non-Greek numerical outcome is unchanged. Separate arithmetic and decision-replay checks accompany the endpoints. Raw editions and record-level derivatives remain local; our code, protocols, source pointers, tables, manuscript and retrospective are available in this package. [Preservation comparison](source-correction-comparison.json), [next tests](NEXT-TESTS.md).
