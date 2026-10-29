# The teaching relay: animated renewal model

13 October 2026. A presentation package for the renewal model in [2026-10-11-societal-persistence](../../experiments/2026-10-11-societal-persistence/MODEL-RESULTS.md). It adds no new model, data or claim.

The animation replays one trajectory per world from the fresh start (2, 2, 3). It covers 48 worlds: 32 from the baseline run and 16 from the shared-operation run. Two brick-built services lose one course per period. A teacher's skill ring drains one segment per period. Training hands the skill to a new generation, shown in a lineage row. Work units fly from a tray to the tasks they pay for. Each period plays in the model's order: work is assigned while the teacher is alive, assets and skill age, repairs and training reset them, and then a supported shock strikes.

[derive_relay.py](derive_relay.py) imports the transition and action laws from the two frozen implementations, `coordinator/renewal_model.py` and `review/co_production.py`, and reads their frozen results. Play is robust. Inside the infinite kernel the controller follows the saved policy; elsewhere it takes the action with the longest guaranteed horizon. The shock each period is the supported one that most shortens that horizon, with ties going to the larger shock. The script asserts that every trajectory's safe length equals the recorded primary outcome and that no step exceeds its budget. It reproduces the three paths quoted in MODEL-RESULTS.md and CO-PRODUCTION-RESULTS.md. The page re-applies the transition law to each step on load, and all 48 worlds pass with no mismatches.

| File | Contents |
|---|---|
| [derive_relay.py](derive_relay.py) | Derivation and page build; refuses an existing output directory |
| [relay.template.html](relay.template.html) | Animated page; the data is injected at `/*__RELAY_DATA__*/null` |
| [run-v1/relay-data.json](run-v1/relay-data.json) | Trajectories, ranks, generation boundaries and source hashes |
| [run-v1/index.html](run-v1/index.html) | Built page |

Reproduce into a fresh directory:

```powershell
C:\Python313\python.exe presentations/2026-10-13-relay-visualization/derive_relay.py --out presentations/2026-10-13-relay-visualization/run-new
```

The model holds a single skill coordinate, so the page draws each training reset as a new generation of teacher. Quantities are invented, and a period has no historical length.
