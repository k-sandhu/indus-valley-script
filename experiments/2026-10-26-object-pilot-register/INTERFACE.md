# Twenty-target metadata interface

The current projection is `data/raw/2026-10-26-object-pilot-register/pilot-register-v4.json`, physically `D:/projects/indus_valley_script/data/raw/2026-10-26-object-pilot-register/pilot-register-v4.json`. The browsable result is `catalogue-v4.html` beside it. Detailed data are local-only. Versions 1, 2 and 3 remain preserved.

The JSON has an `objects` array with twenty unique `record_id` values and a `source_catalogue` array. The exact Dholavira identifiers include the separator: PCF-DHV-005 through PCF-DHV-014. Each object carries its site, aliases, assertions, image pointers, missing fields, retained conflicts and identity status. An assertion has a field, value, canonical status, source references and a locator. Source references resolve to catalogue entries with actual logical and physical paths and SHA-256 where bytes exist. A retained web caption can have a URL and no downloaded bytes; its linked notes preserve the inspection. Missing printed coordinates remain explicit in inherited export assertions.

The [schema](schema-v1.json) documents the required machine fields. Candidate families are a separate array, never aliases or accepted physical identities. Ten source targets retain 62 families and 274 edges. `accepted_physical_merge=false` records that this contribution adjudicates no physical merge. It does not reject the existence of previously catalogued objects. Canonical assertion statuses are catalogued, inferred, unknown and conflicting. Raw values, uncertainty, original assertion identifiers and source dependence remain available where inherited.

Images distinguish inherited index links, source-target photographs, qualified drawing pages, qualified view pointers, web page pointers and unresolved candidate pages. Whole source pages show neighboring objects. Their panel or figure coordinates identify the target. H-1657 has a caption-qualified web pointer without downloaded photograph bytes. H-2587 and H-1688 have held drawing pages. H-1682 and H-1692 have narrative PDF page pointers without a recovered target image. The disputed Rao CLXI F page remains an unresolved candidate source page for L-164.

`missing-evidence-v4.json` is a rankable local queue with record, field, priority, reason and deciding evidence. Priority zero asks for the Dholavira accession-to-corpus bridge. The [coverage table](coverage-v4.json) uses denominator twenty throughout. Source assertion presence counts any retained qualified assertion, including conflicting or inferred values. Accepted physical identity coverage is zero because this pass performs no identity adjudication. The image table separates seventeen targets with local image files from one with only a web pointer; it claims no complete all-side inventory.

Run from repository root, choosing unused output paths:

```text
python -B -X utf8 experiments/2026-10-26-object-pilot-register/build.py v5
python -B -X utf8 experiments/2026-10-26-object-pilot-register/render_catalogue.py INPUT_JSON D:/projects/indus_valley_script/data/raw/2026-10-26-object-pilot-register/catalogue-v5.html
python -B -X utf8 experiments/2026-10-26-object-pilot-register/validate.py INPUT_JSON OUTPUT_HTML VALIDATION_JSON
```

The builder exclusively creates versioned endpoints. The renderer accepts any compatible twenty-record projection and exclusively creates the requested HTML on D:. It uses inline CSS and JavaScript and local image links, with no remote assets or services. Site selection and search filter the cards. Links open actual files; source-coordinate labels remain beside each assertion. The validator checks structure, hashes, links, image accounting and HTML escaping. Browser layout and source pixels require separate review.
