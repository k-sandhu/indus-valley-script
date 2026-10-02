# Identifier parsing refinement

The first join-key output exposed two forms needing their own categories. `H96-6952-33` may encode a year, excavation unit and item using hyphens, while `-Figure 68.02` is a publication locator without an object number. A parser following only the introduction's slash/space examples placed the former among registration prefixes and the latter among other reported identifiers.

Keep `join-keys/` unchanged as a record of that literal-syntax check. The next endpoint adds `hyphenated_year_number_item_syntax` for the first form and `figure_locator_without_object_identifier` for the second. The hyphenated form remains unresolved until checked in the basic-data catalogue: its middle number could be an excavation unit or registration. This distinction avoids asserting a lost context key from punctuation alone.

Apply the refined categories to Harappa families and count figure-only values across all sites. Freeze output in `join-keys-refined/`, preserving the input hash, parser patterns, checks and code snapshot. Use the refined endpoint when describing practical joining feasibility.
