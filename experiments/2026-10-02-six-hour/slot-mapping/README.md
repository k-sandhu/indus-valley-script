# Length/slot mapping control

This branch compares a linear length/slot assignment with the multistart graph decoder on fresh known systems. It improves administrative mapping recovery and loses transition mapping recovery. [Findings](FINDINGS.md), [pre-generation protocol](PROTOCOL.md), [retrospective](RETROSPECTIVE.md).

The [main endpoint](main/results.json) has 384 conditions, 768 method results and saved dual assignment certificates. [Generated records](main/worlds.json) give the known-system inputs. The [independent review](review/verification.json) reconstructs all cell counts and likelihoods, verifies every dual bound, enumerates every eight-symbol linear objective and retains tied alternative maps. It also gives [world-based comparison intervals](review/summary.json).

Run [the model](../../../src/six_hour/slot_mapping.py) and [reviewer](../../../src/six_hour/review_slot_mapping.py) only into fresh endpoints. Code and generator snapshots preserve the exact executed source. The existing output should be read directly before considering a new run.
