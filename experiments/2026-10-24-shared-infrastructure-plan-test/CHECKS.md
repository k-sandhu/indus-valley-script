# Verification of the local delivery

The final study validation passes 304 checks in `study-validation-v3.json`. It checks frozen inputs and source hashes, previous-study preservation, distinct denominators, the spending ledger, independent arithmetic and grid fits, local storage, all thirty atlas images, the final book and explorer, PowerPoint records, slide renders and package structure. These checks belong to the same collaboration. Archaeological interpretation remains exploratory.

## Final versions

| Product | Final version | Verification |
|---|---|---|
| Illustrated report | `book-v2`, 59 pages and 30 figures | All pages rendered; five contact sheets and selected dense text reviewed; no detected layout issue |
| Figure atlas | `run-v2`, 30 PNGs and 9 SVGs | 407 checks; all figures individually reviewed; original orientation, reading bounds and missing fields retained |
| Offline explorer | `explorer-v2`, 30 embedded display images | Town and evidence filters, search, empty results, modal controls, magnification and console checked in the in-app browser; no remote assets |
| PowerPoint | `v3`, 26 slides, 3 native charts and 8 native tables | All slides rendered; 42 chart values checked; all three charts edited, resized, saved and reopened in a test copy; final file unchanged |
| Complete archive | `delivery-v1` | Every archived entry checked against its recorded SHA-256; ZIP integrity checked by the packaging script |

The complete archive is held at the D: raw root in `delivery-v1/shared-infrastructure-study-2026-10-24.zip`. Its outer checksum is recorded in the checkout's `artifact-manifest-v1.json`; its internal `DELIVERY-MANIFEST.json` lists every included file and checksum.

The actual browser screenshot is held at the D: raw root in `review/explorer-v2-browser.png`. Browser testing used a temporary loopback server. That server was stopped after testing. Self-contained HTML structure and interaction tests establish the recorded scope; other browsers and direct file opening were not separately tested.

## Preserved failures and limits

`study-validation-v1.json` passes the earlier 248 checks before the final PowerPoint was added. Version 2 fails because its chart-path assumption misses valid nested OPC chart parts. Version 3 identifies chart parts by XML type and passes. The presentation did not change to satisfy this check.

The first explorer exceeded a browser-control transport limit. Its failure record and larger HTML remain local. The final explorer uses documented display derivatives while the atlas and PDF retain full-resolution figures. Book and deck layout drafts also remain preserved.

`repository-check-summary-v1.json` records 58 pre-existing errors from the broader repository verifier, all outside this contribution. We do not change those other contributions. The knowledge-base check and current source compilation are recorded separately in `CHECKS-v1.json`; generated map and registry notes remain for maintainers.

No fresh confirmation population was opened. The benchmark uses synthetic objects only, no repair date was invented, and no zero eligibility count was converted into a negative effect estimate. The scientific result is eighteen scoped quantities, positive archaeological joins and a specified comparison that the available source frame cannot yet complete.
