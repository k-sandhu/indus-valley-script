# Review of the coordinator's theory manuscript

The inspected [THEORY.md](../THEORY.md) defines persistence by outcome and horizon, bounds full-horizon usable output and separates technical feasibility from enactment. Those revisions address the principal inference problems identified in [REVIEW.md](REVIEW.md). No numerical correction to the frozen run is required.

Three editorial and operational points were sent to the coordinator:

1. Attach robustness to a policy: a robust policy keeps every supported trajectory within the safe set. A single realized trajectory does not carry that guarantee. The finite examples assume the controller observes the full current state; more restrictive historical information can reduce implementable policies.
2. Use the actual report path `review/REVIEW.md`. The four empirical extensions have close predecessors and should be presented as operational hypotheses with independently measured quantities, rather than new general laws.
3. A supply-envelope violation rejects the particular bounded historical reconstruction. It identifies an omitted source, measurement or law problem rather than falsifying the accounting identity. A positive residual remains compatible with several mechanisms and locations.

The strongest remaining blocker to historical confirmation is missing measurement: cumulative delivered demand and baseline output, dated task durations, overlapping deadlines and access arrangements. The manuscript can be presented as a conditional research proposal with those quantities unresolved. The model establishes no historical origin for concepts in later literature.

The later MODEL-RESULTS.md table and saved primary policy path agree with the independent reconstruction. EMPIRICAL-PROTOCOL.md distinguishes rejection of a task/resource reconstruction from rejection of accounting, includes unresolved intervals and alternative supply, and labels the comparison as prospective. The coordinator accepted corrections for the no-op exception, a positive demand lower bound, outcome exposure and the actual reproduction-command location.

The added work-window inequality is valid when mandatory tasks' resource use is additive after shared operations and co-production have been represented. Independently estimated repair and training effort can otherwise count the same apprentice-assisted repair hour twice. Consumable capacity also needs to include usable inventory carried into the interval. These qualifications and a necessary-condition opening for REPORT.md were sent for final correction before the reviewed files are pinned. Final status and hashes belong to a separate reviewer endpoint.
