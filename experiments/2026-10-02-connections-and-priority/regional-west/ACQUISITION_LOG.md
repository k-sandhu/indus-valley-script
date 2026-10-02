# Source acquisition log

All third-party witnesses and derivatives are under `data/raw/2026-10-02-connections-and-priority/regional-west/`, with local-only handling and rights-unverified status. Repository-facing outputs contain our short factual notes, code, aggregate results and acquisition metadata.

| Source or route | Outcome | Manifest |
| --- | --- | --- |
| Ascalone 2022 institution PDF | 8,739,382 bytes; 293 pages | source-acquisition-v1.json |
| Kaniuth 2010 author-institution PDF | 1,953,147 bytes; 31 pages | source-acquisition-v1.json |
| RAS Margiana Expedition 2016 volume 6 | 39,751,272 bytes; 580 pages | source-acquisition-v1.json |
| Englund 1998 university URL | HTTP 200 HTML; rejected as PDF | source-acquisition-v1.json |
| Louvre SB 13677 JSON export | 2,551 bytes; exact SB/AS join | source-acquisition-v2.json |
| Capitoline Gonur exhibition labels | 1,002,290 bytes; 3 pages | source-acquisition-v2.json |
| Bonora 2014 Persée page | 96,737 bytes of HTML | source-acquisition-v2.json |
| Englund 2006 www.cdli.earth | TLS hostname mismatch; no certificate override | source-acquisition-v2.json |
| Englund 2006 canonical cdli.earth | 12,241,488 bytes; 23 pages | source-acquisition-v3.json |
| Observed Persée PDF form URL | Did not return a valid PDF | source-acquisition-v3.json |
| Bonora author full-text web view | Read exact pp. 66–67 and original figure citations | URL in evidence-table.json; no local PDF claimed |
| Brill contents | Confirmed title, author and starting page 461 | https://brill.com/edcollchap/book/9789004541436/front-1.pdf |
| Louvre JPEG linked in JSON | Web tool inaccessible | Observed URL and copyright preserved in museum export |
| Chicago ISAC nn215 | Web 404 | Deferred; no alternate retry in this run |

Manifests record original and text hashes. PDF text derivatives use PyMuPDF with one-based page separators. Rendered images use 2× or 3× scale, with source page numbers in filenames. `raw-derivatives.json` records their hashes and the marked-weight extraction hashes.

The Louvre HTML update date is 27 March 2026; the acquired JSON modified field is 27 July 2026. Both give the same identifiers and four-mark description. Neither was treated as an archaeological date.

The web tool rejected the canonical Englund PDF for its content length. Ordinary public HTTPS acquisition succeeded at the valid hostname with certificate verification enabled.

The first mass-census endpoint and local extraction remain saved. The corrected v2 endpoint fixes word wrapping, shape/material parsing and accession exclusions. REPORT.md cites v2. Source URLs, exact routes and byte hashes are machine-readable in the three acquisition manifests.
