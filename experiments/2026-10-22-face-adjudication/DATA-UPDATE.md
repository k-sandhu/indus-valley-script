# Proposed object-register additions

Add the locally held face reviews as versioned source assertions after independent integration. Their identifiers are the existing provisional `LIPI:` object and face keys. Preserve the earlier plate verdicts, image index and register versions.

The contribution supplies actual image hashes and dimensions, approximate original-pixel graphic group bounds, display-transform records, observer and exposure information, 21 accepted spatial layouts, and 12 provisional mappings from source segments to graphic groups. It assigns no historical reading traversal. Eight of the 29 layouts and 17 segment maps remain unresolved.

The source-code dependency is the normalized Lipi face file identified by its full SHA-256 in each detailed review. The local font rendering uses U+E000 plus the decimal code, following the held source application's encoding. Unknown codes remain unknown. The font's hash and the visual-pass freeze are recorded separately.

Three supplemental records propose retaining caption suffixes as distinct image groups, counting byte-identical impression files once, and linking an inscribed edge separately from the main face. These are source assertions for adjudication. No source-wide physical identity merge is proposed.

No new third-party source was acquired. All images, rendered source glyphs and detailed annotations remain local under `data/raw/2026-10-22-face-adjudication/` or their original holdings. Tracked outputs are our code, protocols, aggregates and hashes. Shared data coverage, manifest and spending files are unchanged.
