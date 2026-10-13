# Source-format corrections after the first census

The successfully written `normalized-v2` census exposed source-format errors before any statistical scoring. Its records, manifest and exact parser/runner are preserved. The successor `normalized-v3` implements four source-checked corrections.

AES `hiero_unicode` usually contains numeric HTML entities such as `&#x132b5;`, not literal Unicode characters. Decode entities before extracting glyphs. The earlier census's single complete glyph sentence is a parser artifact. Egyptian addition markers `〈〉` and related corner/angle markers also join the declared damage/restoration exclusion.

ORACC stores seal inscriptions as surfaces named `seal 1`, not only as object nodes named `seal`. Start a distinct seal module at those surface markers and retain its parent document/physical aliases. Otherwise an account and its impressed seal are concatenated into a fictitious reading sequence.

ORACC `nonx` nodes describe blank space and rulings in their `state` field. These are not missing inscriptions. Ignore states blank/ruling/space when assigning textual incompleteness; retain missing/other unresolved states as exclusions. The original predicate inspected `subtype` and therefore excluded legible objects at many ordinary rulings.

XML `tla` identifier prefixes, source JSON entries with invalid payloads, and Egyptian tokens without source IDs were addressed before the successful census. Missing IDs remain an exclusion. No source word, image, prior project output or frozen dataset was edited. These changes correct the representation of observed source formats; they were informed by census failures and remain part of the exploratory history.
