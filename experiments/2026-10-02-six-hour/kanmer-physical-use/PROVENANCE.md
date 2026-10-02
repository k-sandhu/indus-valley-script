# Witness handling and transformations

The original acquisitions and detailed object/face records remain in the local project. This branch tracks our protocols, summaries, source coordinates, manifests, aggregates and code. It adds no third-party image or full source text to the repository. The [redistribution record](../../../knowledge/provenance/REDISTRIBUTION.md) governs future packaging.

| Component | Observed rights basis | Current handling |
|---|---|---|
| Our prose, code, aggregates and source manifests | `own-work` | Tracked |
| Publisher Antiquity PDF and figure assets | `rights-unverified` for reuse; publisher copyright | Local-only |
| RIHN report PDFs, author copies and preview atlases | `rights-unverified` for our reuse; source copyright recorded | Local-only |
| Science photo/thumbnail in RIHN brochures | `permission-recorded` within the brochure; AAAS reprint line inspected | Local-only |
| 2023 volume text | `explicit-license`: front matter states CC BY 4.0 unless otherwise specified | Acquired witness local-only pending asset review |
| 2023 figure assets | `mixed-assets`: volume license with unchecked figure exceptions | Local-only |
| Individual registrations, measurements and face annotations | Our source-dependent record, with full reconstruction detail | Local-only; aggregate coverage and source coordinates tracked |

Every acquisition endpoint preserves a target list, code snapshot, `access.json` and summary. Raw assets are under `local-witness/`. HTTP 200 records mean successful transport; source qualification follows inspection. Failed responses, including challenge pages, remain in their original endpoints.

The 2012 author-copy PDF is 49,459,102 bytes with SHA-256 `7f3ea038b2d26322d31f4ecc92f87891ac9c9a5bd16e9338c0e90817ebbcb41e`. It contains 55 pages and no embedded mesh file. The original embedded figure bytes were extracted with PyMuPDF. A first caption mapping failed because it assumed resource order matched printed order; both manifests and their image files remain. The reviewed manifest records xrefs, source page bounds, pixel sizes and image hashes.

The 2023 Figures 3–4 asset is 1,801 × 1,035 pixels, SHA-256 `32a23af13003d8968227b3b4cfb4232fcc0c95fdb7b18e321368905e4bb35293`. Its four-source-object annotations preserve image coordinates. Separate files distinguish first observations from proposed registration joins. The author-hosted full text was preserved as a local web-tool witness, rather than labelled as an acquired original PDF.

The extraction helper preserves original and decoded Occasional Paper 10 text. Its map replaces only U+F0030–U+F0039 with decimal digits. The page 98 original JSONP hash is `69f0fc44f4b5b84f0e2ae377c9894155fbab45dfae0ce4fbb27423ae4f232212`. All 81 character substitutions are documented in the local decoding manifest. The original glyphs remain available for inspection.

The numerical endpoint records SHA-256 values for its protocol, local ledger and annotation inputs. Final verification checks those preserved inputs, source-view counts, corrected figure captions and navigation. New annotations or newly acquired final-volume pages should enter a new endpoint with a source-join comparison, while the current files remain unchanged.
