# Identity and exposure review of 358 candidate records

We reviewed every row in the fixed candidate inventory and verified 24 existing links to provisional Lipi families. The remaining 306 rows retain candidate links, and 28 have no supported link in the held register. The audit adds an explicit exposure assessment to every row and preserves the source and page evidence behind it. It establishes no new physical object or confirmation-eligible object.

The population consists of publication inventory rows, which can describe the same physical carrier more than once. We joined these rows to the post-catalogue inventory, source register, matching decisions, duplicate tables, exposure logs and the full object register. The metadata inputs and their hashes are listed in [run-v3/source-manifest.json](run-v3/source-manifest.json). We read identity and access metadata without opening primary-source pages or inscription images. A workflow code search displayed some object-type, material and context literals; the access log preserves that exception to the intended identity-only display.

## Identity results

| Disposition | Rows |
|---|---:|
| Verified identifier link to one provisional family | 24 |
| Candidate relationship retained | 306 |
| No link in the held register | 28 |
| Total reviewed | 358 |

Every supported link passed a site-qualified comparison of complete registration components. Six used the existing whole identifier directly. Sixteen Dholavira links used the documented DHR namespace, and two Kanmer links used the documented project label. Numeric components remain separate. The formerly contained Kanmer match was verified by its complete two-part registration after the project label was accounted for. This rechecks an existing decision; the number of supported families remains 24.

All 11 inventory duplicate flags remain unresolved. The flagged rows lack registrations, and their counterpart metadata supplies no explicit same-object cross-reference sufficient to settle the relationship. We also retained two Dholavira pairs that share registrations but cite distinct catalogue entries. Shared numbering, context and provisional candidate families do not establish that those entries describe one carrier. Each relation has a local evidence record and a named missing identity check. No provisional families were merged.

## Exposure results

We indexed 892 combined-log rows, 84 mechanical-access rows, 40 conservative incident records and two later incident records. The resulting 1,018 records document access methods and reported participants. They contain repeated descriptions of some historical accesses, so their count does not measure unique sessions.

| Most informative page-associated record for a candidate | Rows |
|---|---:|
| Recorded image display on its cited page | 2 |
| Recorded text display on its cited page | 13 |
| Conservative incident set includes its cited page | 172 |
| Reviewed-page set includes it; displayed subset unknown | 30 |
| Identity or bibliographic metadata display recorded | 141 |
| Total reviewed | 358 |

One historical image-viewing record is associated with two candidates on the same cited page. Its crop extent does not identify which candidate image was shown. The other exposure classes likewise retain the distinction between a page locator and the content actually displayed. The conservative incident records identify possible exposure; the broad screening logs identify reviewed pages without recovering the exact subset shown to a model.

Page labels join all 358 candidates to historical events. For 313 candidates an event explicitly names PDF coordinates. For 45, the registered source is an OCR file, HTML page or acquisition record, so the relation to the original PDF version remains unverified. We retain printed-page and PDF-page pairs from the inventory and do not extrapolate a volume-wide offset. Source hashes are inherited from the source register; this audit verifies the bytes of its metadata inputs.

The event records distinguish script extraction and hashing from reported model display. They preserve model labels, named runs and documented harnesses, while leaving unidentified sessions, exact timestamps, statistic families and later participant exposure unresolved. No row is certified for confirmation use. Selecting a future participant set and test family will require its own exposure adjudication together with physical and textual dependence checks.

## Verification and next evidence

The final run passed nine synthetic tests for identifier boundaries, namespace handling, ambiguous links, conflict retention, page parsing, source versions and unknown freshness. [The output verification](source-and-replay-verification.json) passed 2,526 checks, including all 24 supported identifier links and 2,139 candidate-to-event associations. Six local output files reproduced byte for byte. Earlier `run-v1` and `run-v2` outputs are preserved; [the retrospective](RETROSPECTIVE.md) explains their refinements. There was no statistical confirmation read.

The strongest supported statement is that the entire 358-row candidate inventory now has reproducible identity and exposure dispositions, with 24 existing family links independently rechecked by complete identifiers. The deciding next evidence is object-specific catalogue or accession documentation for the unresolved relations, and page-and-participant records precise enough to determine what each proposed confirmation participant actually saw.
