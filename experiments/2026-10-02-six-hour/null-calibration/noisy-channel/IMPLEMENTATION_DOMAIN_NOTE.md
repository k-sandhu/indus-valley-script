# The direct inversion's boundary case

The main source returns an undefined raw frequency inverse when its attenuation is at most 1e−12. It then uses the uniform distribution for the direct estimator's frequency comparison. The protocol states the boundary rate and asks for undefined-inversion counts, but leaves that uniform fallback unspecified. This is an implementation detail that needs an explicit rule in a future protocol.

All 1,000 main populations have a defined raw inverse, and the fallback was never used. The saved results, source and input populations remain unchanged. The exact agreement-count calculation gives outside-domain probability about 3.67e−31 under the declared 60-pair generator. Future use should either abstain on frequency inversion at that boundary or state the chosen default distribution before its outcomes.
