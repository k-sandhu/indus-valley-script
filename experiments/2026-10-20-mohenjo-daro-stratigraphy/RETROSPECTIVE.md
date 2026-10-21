# Retrospective: Mohenjo-daro stratigraphy shot, 20 October 2026

## Approach

The brief named the claim, the data and the excavator split. We read the conjecture-shot design and its review response, the bench documentation and loader code, the chronology package from Harappa and the 13 October join of the Mackay and Marshall tables, then searched the repository for any earlier use of depth with legends at Mohenjo-daro. The seal-text identity review had used excavation area, never depth, so `stratigraphic_level` was a fresh family. The card was created first with `python tools/kb.py new conjecture` and renamed to a short slug, and a note in the shared session folder recorded the C-0006 number for the sessions working in parallel.

The bench shots loader splits an input at random by component, while the brief's partition was by excavator. We gave the loader the Marshall file alone, so that it guarded and logged every read of the confirmation population, and read both of its halves after the freeze. A dry run in the scratchpad on Mackay's rows relabelled as fake areas checked the whole path first: the loader refused the confirmation read before the freeze, accepted it after, logged both halves, and the scorer and credence rule ran. The loader ran with a ledger inside the package, copied from `bench/spent.json`, so that the shared ledger stayed with the maintainer.

The scoring code was written once ([score.py](score.py)) and used three times: as a rehearsal on Mackay's own seals, inside the power simulation and, frozen by hash, on Marshall's seals. Power was simulated on populations with Marshall's strata and tied depth values, read from the tracked join table and the export's section field without any Marshall legend, and filled with Mackay's legends.

## Problems and fixes

The first discovery run tested variant choice on complete legends only and gave p = 0.47; the earlier quick look over all readable legends had given p = 0.13. A damaged legend still shows which variant was cut, so the frozen test uses all readable legends. The choice was made after seeing both values, and [EXPLORATION.md](EXPLORATION.md) records it; the first run is kept as [discovery-v1/](discovery-v1/).

Per-sign split-half reliabilities for opening signs swung between 0.01 and 0.25 between two runs with different random halvings, because only a handful of opening signs reach four legends in each half. The report quotes the transfer correlation, which is stable, alongside the reliability.

The power simulation took about 20 minutes on 16 processes instead of the few minutes estimated, because the variant statistic rebuilds its class structure on every permutation and the machine was shared with other sessions' jobs. It ran to completion unchanged; a later rerun would gain most from precomputing the class codes.

Resampling Mackay's seals with their own heights overstated power for the omnibus tests (P4 passed in 46% of resamples, although on Mackay itself p = 0.31), since resampling treats the noise in an observed association as part of the effect. The predictions file states these rates as upper bounds and relies on the planted-effect rates.

`bench/spent.json` showed as modified during the session. Its hash matched our copy, and the diff contained only the fish-context package's split from earlier the same evening; this package never wrote to it. The fish-context split arrived after we first read the ledger and before we copied it, so the frozen [PROTOCOL.md](PROTOCOL.md) describes two splits where the copy holds three. The third spends fish-sign, object-type, site, motif and seal-size families, none of them `stratigraphic_level`, and the report gives the corrected description.

## Outcome

The single read happened 18 seconds after the freeze. The closing stock passed all three fixity predictions with the bottom-third share at 0.731, against 0.732 in DK-G, and every drift prediction failed, which kills C-0006 under its frozen rule (0.20 to 0.02). The rectangular-seal rise that was the clearest change in DK-G did not repeat in Marshall's sections, where the bottom and top thirds lie under 4 ft apart at the median, so the drift half is refuted for moderate drifts and untested for small ones in short sections. The report ends with the fixed-pattern reading the results support and the Harappa period test that would decide it.
