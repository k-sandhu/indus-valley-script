# Proposed data inventory update

Add a candidate-review layer for the fixed 358-row queue. It verifies 24 existing links to provisional Lipi families, retains 306 candidate-only rows and 28 unlinked rows, and supplies reviewed identity and exposure fields for all 358. The underlying 4,695-family register population is unchanged.

The local layer contains 1,018 historical exposure documentation records, 2,139 candidate-to-event associations and 13 unresolved duplicate relations. The latter comprise the 11 original possible-duplicate flags and two additional shared-registration pairs with distinct catalogue entries. Candidate locators have 313 explicit PDF-page matches and 45 derived-page matches whose original PDF version remains unverified. All confirmation-eligibility values are false.

The final data directory is `data/raw/2026-10-22-candidate-identity-exposure/run-v3/`. Add its six files to the manifest using the hashes in `run-v3/validation.json`. The companion `source-and-replay-verification.json` records input-byte checks and exact reproduction. No new third-party source was acquired. Candidate details, aliases and source-derived access records remain local; code, aggregate coverage and source hashes may be tracked.

The closed gap is the absence of a complete, row-level identity and exposure review. The remaining gaps are identity evidence for unresolved relations, the original PDF binding for 45 source rows, exact historical display content, the proposed participants' exposure history, and physical and textual dependence closure. Missing logs remain unknown. Maintainers can import the assertion proposals into a new register version while preserving the earlier inventories and registers.
