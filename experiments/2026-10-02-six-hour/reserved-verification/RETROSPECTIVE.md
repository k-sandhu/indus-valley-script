# Approach and verification record

The preceding acquisition experiment exposed a practical distinction: entropy queries reached the correct synthetic map with fewer identities, while conditional model mass sometimes stopped the search on a wrong map. This run froze the first confident proposal and tested it with additional identities. The target became a checkable prediction on a new observation.

The protocol preceded the pilot. The two-system-per-family pilot produced twelve conditions and 84 audit records without a serialization failure. The full grid then used 24 new systems per family, 576 conditions and 4,032 records. All seven policies shared each frozen proposal and earlier observation history. The response oracle was accessed only after the selected verification codes were fixed.

The mathematical audit calculation was checked by exhaustive subset enumeration. It also determined the conservative random policy: a wrong bijection has at least two remaining disagreements, so the smallest audit with pass probability at most 0.05 can be chosen without knowing their locations. This elementary sampling result predates the experiment; its role here is to supply a model-independent verification comparison for the simulated mapping task.

The independent verifier recalculated all outcomes and regenerated one condition from every system. Its first review passed all twelve checks. Reading the verifier afterward found an unnecessarily complicated expression for remaining search codes and a replacement-key assertion that added no useful check. The working verifier was simplified to track observed codes explicitly, and the redundant assertion was removed. The original `review` endpoint and code remain intact. `review-clean` repeats the same twelve checks and yields the same summaries, score error and mass error.

The main result showed efficient error detection by posterior-selected verification in several conditions. Rejection does not recover a replacement mapping: the retained candidate simply failed its reserved prediction. The report therefore gives accepted correct proposals, accepted wrong proposals and rejections separately, with the shared reliable-identity assumption in the methods.

A subsequent experiment could continue after a rejection, allow erroneous measurements or compare disagreement between several generative models. Each changes the probability of an eventual acceptance and needs a fresh protocol. The current one-proposal histories and exact audit probabilities provide a baseline for those extensions.
