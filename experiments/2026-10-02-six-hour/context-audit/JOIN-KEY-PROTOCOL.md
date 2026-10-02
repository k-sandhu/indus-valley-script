# HARP registration keys and excavation-unit links

This descriptive extension follows inspection of the HARP identifier convention on printed p. xlvi, footnote 4. The source gives a registration number and a separate excavation-unit/item pair. The latter is the useful join to the excavated context.

Inspect the `excavation-idno` strings for Harappa families. Count strings with a recognizable HARP year/registration prefix, and count those also carrying the documented slash or space followed by a four-digit excavation-unit and item pair. Retain the distinction between a registration number and a context key. The parser records recognizable syntax, with a list of small illustrative cases; it does not resolve the fieldbooks or assert that unrecognized strings lack every possible contextual identifier.

Keep one string per family where all faces agree. Record any within-family variations. Save results and a code snapshot to a new `join-keys/` endpoint. This addresses a source-driven joining question separately from the frozen availability counts.
