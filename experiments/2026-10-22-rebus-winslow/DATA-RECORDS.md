# Data records for maintainers

This package adds a second Tamil compound dictionary, Winslow's of 1862. It is not an inscribed-object record, so the object coverage counts in `knowledge/DATA.md` section 2 do not change. Files, hashes, byte counts and retrieval times are in [SOURCES.json](SOURCES.json). Everything below stays local under `data/raw/2026-10-22-rebus-winslow/`.

## Proposed row for DATA.md section 1, comparison corpora

| Kind | Source and size | Rights |
|---|---|---|
| Second Tamil compound dictionary | Winslow, *A comprehensive Tamil and English dictionary of high and low Tamil* (1862), DSAL edition: 978 query pages, 953 with entries, 22,760 principal forms, 46,550 sub-entry forms, 18,426 two-member compounds recovered by our parser ([package](REPORT.md)) | 1862 work out of copyright; no licence statement for the DSAL digital edition, kept local |

## New derived table and its fields

| Table (local) | Built by | Fields |
|---|---|---|
| `derived-v1/winslow-entries.jsonl` (SHA-256 `5697e42a…d1e5`) | `code/parse_winslow.py` | `page`, `kind` (principal or sub), `head` (Tamil script), `translit_plain` (DSAL romanisation for principals, ours for sub-entries), `translit` (members joined by hyphens when split), `members`, `seg` (first, second, ety, phrase or none), `root` (principal of a sub-entry), `root_grammatical`, `star` (asterisk or foreign mark), `asterisk`, `foreign_mark`, `grammatical`, `pos` (n for Winslow's s.), `pos_source`, `verb`, `ety` (Tamil members named in the etymology), `gloss` |
| `derived-v1/parser-validation-v1-detail.json` | `code/validate_parser.py` | transliteration mismatches; Winslow compounds whose members differ from the *Tamil Lexicon*'s hyphenation |

## Coverage notes

Winslow's sub-entries carry no romanisation and no hyphens; members are recovered from the nesting under a root and from Tamil sandhi. Where the same form is a two-member compound in both dictionaries, the members agree with the *Tamil Lexicon* in 98.1% of 11,784 cases, and 75.4% of the Lexicon's compounds among Winslow's sub-entries are recovered ([parser-validation-v1.json](parser-validation-v1.json)). Principals that are compounds without an etymology, compounds of three or more members and junctions with the *-am-* increment are not split. The DSAL text writes every initial *e* as ஏ, so 348 principal forms begin with ē in the romanisation whatever their vowel length.

## Proposed entry for data/MANIFEST.json

[MANIFEST-PROPOSAL.json](MANIFEST-PROPOSAL.json) gives the source entry `rebus-winslow` in the schema of the existing entries, with the digest of the page hashes.
