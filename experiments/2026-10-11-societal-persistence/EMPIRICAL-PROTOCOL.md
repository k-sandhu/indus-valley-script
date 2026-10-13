# A prospective archaeological test of renewal requirements

11 October 2026. This design follows the exploratory source survey and model results. It is a proposed next study, with no fitted archaeological parameters, completed population comparison or inferred ancient policy.

The immediate study should reconstruct one documented service sequence at a time. It should then ask whether replacement operations overlap in a way that constrains the proposed mechanism. A general ranking of civilizations by an invented complexity score would conceal the quantities needed for that inference.

## Phase one: establish the outcome independently

Choose a settlement area, service and occupation interval before coding renewal capacity. Record whether the outcome is occupancy, population within a stated range, operating infrastructure, production technique or network participation. Describe the tolerated interruption and evidence required to identify it. A source reporting consecutive archaeological phases does not supply annual continuity.

Build the sampling frame from all relevant excavated or surveyed cases in the defined region and publication range, including short-lived settlements, interruptions and unresolved outcomes. Retain excavation coverage and preservation. Distinguish right censoring at the latest observed phase, left truncation before the earliest recovered phase, uncertain dates and reoccupation after a gap. The broad comparative studies in [the survey](literature/SURVEY.md) supply useful outcome definitions; they are not already measures of renewal capacity.

## Phase two: code observations before a favored explanation

Use the following fields for every observation. Keep each statement attributable to a particular source and locus.

| Field | Content and reason |
|---|---|
| `observation_id`, `source_id`, `witness_hash`, `locus` | A stable join to the inspected witness and exact page, figure or context |
| `site`, `area`, `context`, `phase`, `date_interval`, `dating_basis` | The unit and resolution at which events can be ordered |
| `outcome_unit`, `boundary`, `service`, `minimum_definition` | What continuation would mean for this test |
| `observation_type` | Separate wear, maintained access, repair, replacement, reuse, rerouting, interruption and the author's interpretation |
| `quantity`, `unit`, `lower_bound`, `upper_bound`, `bound_basis` | Commensurable output or material quantities with independently justified bounds |
| `initial_output_horizon`, `wear_basis`, `baseline_supply_routes` | Output from initial assets through the full interval and all allowed baseline sources |
| `task_window`, `duration_bounds`, `skill_requirement`, `shared_inputs` | Inputs to a joint-schedule test; leave unmeasured quantities unresolved |
| `provider`, `upstream_route`, `dependency_basis` | Whether apparently distinct providers share a prerequisite |
| `participation_evidence`, `resident_access`, `distribution_scope` | Evidence that technically possible work could be performed and whom it served |
| `coverage`, `preservation`, `alternative_explanations` | Whether missing traces could result from the recovered sample or a different mechanism |

Do not infer every field from a completed structure. The Harappa sequence documents drain replacement and a route change. Work duration, responsible actors and total delivered waste-removal capacity remain additional questions. The Dholavira sequence includes renewed use after a reported desertion and changes in housing. Its outcome definition must represent that interruption and selective service retention.

Two coders should independently extract the observation and the author's explanation, compare disagreements and retain a resolution log. For a prospective prediction test, mask later duration during capacity extraction and freeze the resulting records before outcome coding. If the readers already know the later outcome, label the comparison exploratory; freezing cannot erase that exposure. Multiple publications of one excavation, mirrored reports and alternate translations belong to a single observation lineage. A missing value remains missing unless new evidence supplies it.

## Phase three: bound additional delivery

Begin with a commodity or service whose usable delivery can share one unit. Food supply, a specified building material and usable water require different accounts. Estimate a minimum demand from independently supported activity or population intervals. Bound the cumulative output of starting stock and unmaintained assets over the entire horizon, along with delivered imports and other permitted baseline sources.

Apply the bound in [THEORY.md](THEORY.md) only when the proposed supply envelope covers all relevant baseline routes. Report zero or an unresolved result when uncertainties prevent a positive residual. A positive result requests an explanation for additional supply; source observations then discriminate production, prolongation of use, repair, replacement and acquisition. A deficit under a narrowly local boundary may disappear under a regional boundary that includes outside suppliers.

Independent wear experiments or comparative material performance can constrain an asset's output. Its apparent archaeological longevity cannot be used as the assumed lifetime and then cited as proof that longevity required the favored intervention. Population contraction, substitute services and intermittent use must be incorporated before the demand bound is fixed.

## Phase four: test the shared schedule

For at least two dated operations, collect independently bounded task duration, allowable completion windows, worker or skill needs and resource use. Enumerate the schedules consistent with those bounds. A favorable-feasibility test asks whether some allowed timing and resource realization admits a schedule. A robust test asks whether an implementable policy can satisfy the declared variation with its stated information. Feasibility for each operation on its own is a separate endpoint.

First apply the work-window constraint in [THEORY.md](THEORY.md): operations confined to a given interval cannot demand more of a resource than its usable capacity in that interval. Identify shared operations before summing demands, so that repair which also trains an apprentice is counted once. For materials, include usable inventory carried into the interval. This can reject a proposed mechanism with fewer assumptions than a complete schedule. It cannot establish joint feasibility on its own. Keep independently available substitutions and alternative operations in the reconstruction so that the favored task list is not mistaken for the only possible means of renewal.

Compare a model with shared inputs against one permitting independent routes, preserving the same observed tasks. Compare immediate completion against independently justified lead times. Keep provider counts and upstream dependence distinct. If date uncertainty is wider than the work windows being hypothesized, report that the mechanism is unresolved at that resolution.

A continuous service observation combined with infeasibility under every admissible reconstruction rejects that specific task/resource account. It directs attention to omitted delivery, substitute methods, timing errors or incorrect service interpretation. It does not overturn accounting. Conversely, a feasible schedule does not establish that ancient actors selected it. Evidence for access, practical knowledge, contribution rules or coercion is needed to connect opportunity with action.

## Phase five: compare persistence without selecting only survivors

A prospective comparison should use a fixed set of settlements or service sequences with consistent coverage. Define capacity indicators before their subsequent outcome is coded. Include failures and unresolved cases, with date uncertainty and censoring visible. Keep quantities such as documented renewal, upstream input diversity and replacement overlap distinct; do not combine them into an unvalidated numerical index.

An initial analysis can report whether the predefined indicators discriminate later service continuity from interruptions after accounting for documented demand and outside delivery. Geography, population changes, hazards, new technology and political conflict remain rival explanations. An association would motivate a more specific causal design; it would not by itself identify a cause of long settlement duration.

## First pilots and stop rules

The [Harappan evidence study](evidence/APPLICATION.md) and [its tests](evidence/TESTS.md) identify the source-qualified pilots. Start with the replacement drain at Harappa because the observed sequence distinguishes clogging, replacement and rerouting. A second pilot can follow Dholavira's selective maintenance and changed occupation, with the reported break retained. A craft sequence would need evidence for technical transmission and input sourcing in addition to product disappearance.

Stop before numerical fitting if delivered quantities are incommensurable, there is no positive independently supported demand lower bound, initial output or imports cannot be bounded above, or the chronology cannot resolve the proposed task overlap. In that case deliver the completed source-linked observations and the missing-measurement list. The [reviewer's rejection criteria](review/FALSIFIERS.md) state which narrower inference each future result can change.
