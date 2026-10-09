# Agreement of two AI coding rounds

The first reader was Codex. The independent Claude Sonnet 5.5 round used two fresh sessions for separate halves of the 96-target packet. Returns and part hashes are preserved. Both parts report packet-only reading, with file/folder names outside their assignments visible. No specialist has reviewed the drawings. Counts are target-level; repeated drawings and allographs are included.

Overlap includes exact singleton matches. Disjoint counts require two nonempty sets. Missing sets are separate. Kappa uses only paired singleton rows and their empirical marginals; it excludes ambiguous and missing rows. Helsinki identity is a chart cell, with code/rank metadata checked separately.

| Domain | Targets | Exact singleton | Equal nonempty sets | Overlap | Disjoint | Missing | Singleton kappa (paired n) |
|---|---:|---:|---:|---:|---:|---:|---|
| mayig | 96 | 72 | 72 | 78 | 10 | 8 | 0.9217 (78) |
| wells | 96 | 42 | 72 | 78 | 10 | 8 | 0.9109 (46) |
| helsinki | 96 | 6 | 59 | 78 | 10 | 8 | 0.7193 (8) |

Helsinki kappa has only eight paired singleton rows. Many chart differences reflect a narrower set of same-class allographs in the second return. The exact target/candidate list is in [agreement.json](agreement.json).

## first confidence

| Stratum | Domain | Targets | Exact singleton | Overlap | Disjoint | Missing | Kappa (paired n) |
|---|---|---:|---:|---:|---:|---:|---|
| high | mayig | 63 | 57 | 59 | 4 | 0 | 0.9489 (60) |
| high | wells | 63 | 36 | 59 | 4 | 0 | 0.9459 (38) |
| high | helsinki | 63 | 4 | 59 | 4 | 0 | 0.7619 (5) |
| medium | mayig | 27 | 15 | 19 | 6 | 2 | 0.8182 (18) |
| medium | wells | 27 | 6 | 19 | 6 | 2 | 0.7091 (8) |
| medium | helsinki | 27 | 2 | 19 | 6 | 2 | 0.5000 (3) |
| unmapped | mayig | 6 | 0 | 0 | 0 | 6 | undefined (0) |
| unmapped | wells | 6 | 0 | 0 | 0 | 6 | undefined (0) |
| unmapped | helsinki | 6 | 0 | 0 | 0 | 6 | undefined (0) |

## second confidence

| Stratum | Domain | Targets | Exact singleton | Overlap | Disjoint | Missing | Kappa (paired n) |
|---|---|---:|---:|---:|---:|---:|---|
| high | mayig | 66 | 59 | 61 | 2 | 3 | 0.9665 (61) |
| high | wells | 66 | 34 | 61 | 2 | 3 | 0.9706 (35) |
| high | helsinki | 66 | 6 | 61 | 2 | 3 | 0.8372 (7) |
| low | mayig | 7 | 1 | 1 | 5 | 1 | 0.3333 (2) |
| low | wells | 7 | 1 | 1 | 5 | 1 | 0.3333 (2) |
| low | helsinki | 7 | 0 | 1 | 5 | 1 | undefined (1) |
| medium | mayig | 23 | 12 | 16 | 3 | 4 | 0.7857 (15) |
| medium | wells | 23 | 7 | 16 | 3 | 4 | 0.7568 (9) |
| medium | helsinki | 23 | 0 | 16 | 3 | 4 | undefined (0) |

## joint confidence

| Stratum | Domain | Targets | Exact singleton | Overlap | Disjoint | Missing | Kappa (paired n) |
|---|---|---:|---:|---:|---:|---:|---|
| high/high | mayig | 49 | 48 | 48 | 1 | 0 | 0.9790 (49) |
| high/high | wells | 49 | 28 | 48 | 1 | 0 | 0.9643 (29) |
| high/high | helsinki | 49 | 4 | 48 | 1 | 0 | 0.7619 (5) |
| high/low | mayig | 2 | 1 | 1 | 1 | 0 | undefined (1) |
| high/low | wells | 2 | 1 | 1 | 1 | 0 | undefined (1) |
| high/low | helsinki | 2 | 0 | 1 | 1 | 0 | undefined (0) |
| high/medium | mayig | 12 | 8 | 10 | 2 | 0 | 0.7826 (10) |
| high/medium | wells | 12 | 7 | 10 | 2 | 0 | 0.8596 (8) |
| high/medium | helsinki | 12 | 0 | 10 | 2 | 0 | undefined (0) |
| medium/high | mayig | 14 | 11 | 13 | 1 | 0 | 0.9070 (12) |
| medium/high | wells | 14 | 6 | 13 | 1 | 0 | 1.0000 (6) |
| medium/high | helsinki | 14 | 2 | 13 | 1 | 0 | 1.0000 (2) |
| medium/low | mayig | 4 | 0 | 0 | 4 | 0 | undefined (1) |
| medium/low | wells | 4 | 0 | 0 | 4 | 0 | undefined (1) |
| medium/low | helsinki | 4 | 0 | 0 | 4 | 0 | undefined (1) |
| medium/medium | mayig | 9 | 4 | 6 | 1 | 2 | 0.7368 (5) |
| medium/medium | wells | 9 | 0 | 6 | 1 | 2 | undefined (1) |
| medium/medium | helsinki | 9 | 0 | 6 | 1 | 2 | undefined (0) |
| unmapped/high | mayig | 3 | 0 | 0 | 0 | 3 | undefined (0) |
| unmapped/high | wells | 3 | 0 | 0 | 0 | 3 | undefined (0) |
| unmapped/high | helsinki | 3 | 0 | 0 | 0 | 3 | undefined (0) |
| unmapped/low | mayig | 1 | 0 | 0 | 0 | 1 | undefined (0) |
| unmapped/low | wells | 1 | 0 | 0 | 0 | 1 | undefined (0) |
| unmapped/low | helsinki | 1 | 0 | 0 | 0 | 1 | undefined (0) |
| unmapped/medium | mayig | 2 | 0 | 0 | 0 | 2 | undefined (0) |
| unmapped/medium | wells | 2 | 0 | 0 | 0 | 2 | undefined (0) |
| unmapped/medium | helsinki | 2 | 0 | 0 | 0 | 2 | undefined (0) |

## target type

| Stratum | Domain | Targets | Exact singleton | Overlap | Disjoint | Missing | Kappa (paired n) |
|---|---|---:|---:|---:|---:|---:|---|
| Table 18 drawing | mayig | 65 | 49 | 51 | 8 | 6 | 0.9057 (54) |
| Table 18 drawing | wells | 65 | 31 | 51 | 8 | 6 | 0.9092 (34) |
| Table 18 drawing | helsinki | 65 | 5 | 51 | 8 | 6 | 0.6744 (7) |
| caption form | mayig | 17 | 13 | 16 | 1 | 0 | 0.9218 (14) |
| caption form | wells | 17 | 5 | 16 | 1 | 0 | 0.8065 (6) |
| caption form | helsinki | 17 | 1 | 16 | 1 | 0 | undefined (1) |
| field or anchor target | mayig | 14 | 10 | 11 | 1 | 2 | 1.0000 (10) |
| field or anchor target | wells | 14 | 6 | 11 | 1 | 2 | 1.0000 (6) |
| field or anchor target | helsinki | 14 | 0 | 11 | 1 | 2 | undefined (0) |

## Reference and instruction checks

All returned Helsinki class/code payloads match chart v2.1. The `class` field means its printed `rank`; both coding rounds used that meaning. The 96-row v2 template is the operative template. The original instructions remain preserved, with a new local clarification.

There are 658 ordinary direct Mayig/Parpola-code joins: 624 have Mayig number equal to chart rank and 34 have Mayig number two higher. P373 and P374 list codes 804/805 absent from this chart. The special damage marker P000/V599 joins chart rank 396 and supplies the sole numeric-offset exception. Code 369 prints class 43 but is absent from direct Mayig code lists; Mayig P043 instead lists code 288. Explicit cell/code joins therefore remain necessary. [Reference check](reference-check.json).

There are 38 targets with a candidate-set or component difference, including 24 with different Mayig sets. [DISAGREEMENTS.md](DISAGREEMENTS.md) gives both codings and short source-image notes. [target-attribution.json](target-attribution.json) identifies outcome-sensitive cases without adjudication.
