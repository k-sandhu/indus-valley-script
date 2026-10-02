# Main budget after the noisy-face timing pilot

Written before the main outcomes, October 2, 2026. The two-population pilot completed its two observed fits and 36 reference fits in .8328 seconds while the original calibration study was running. This timing supports the budget stated in [the original protocol](PROTOCOL.md): 1,000 populations, 99 draws for each of the two references, 198,000 reference fits and 1,000 observed fits. Allow about 1.3 hours at the pilot rate, with additional room for process contention and verification.

The generator, sampling law, model procedure and thresholds remain as declared. The finite vector-space audit is completed before launching this main run. The pilot's two outcomes do not select any error rate, model, cutoff or analysis endpoint.

A seed-schedule check found that a few finite-sampler seeds could coincide with the original proposed main record-reference namespace. Before any main outcomes, move the main references to bases 20,000,000,000 and 40,000,000,000, still adding 1,000,000i+j. The source changes only these main seed bases; the saved pilot and finite-sampler source/endpoints remain unchanged. Pilot bases 6,000,000,000 and 8,000,000,000 and the original generator rules remain fixed. This separates the main study from all earlier simulation streams as well as its own finite sampler.
