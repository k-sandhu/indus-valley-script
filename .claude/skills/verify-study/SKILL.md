---
name: verify-study
description: "Use when independently reproducing an outcome or recording an adversarial review."
---

# Verify study

Read [REPRODUCING.md](../../../REPRODUCING.md), the study’s protocol, input hashes and exact outputs. Reproduce or review in your own new dated package, stating which code and sources were reused. Follow the verification tiers in [CONTRIBUTING.md](../../../CONTRIBUTING.md); report discrepancies and required local inputs. Another contributor’s review remains a separate contribution.

Recompute the relevant bench output from its recorded input, code hashes and seed, preserving the submitted endpoint. Check population identity and source access as well as scores; catalogue line divisions provide positive boundary labels, while readable-script word references provide complete labels. Changes to `bench/` also run `python -m bench selftest` and reproduce a source number for every affected scorer.
