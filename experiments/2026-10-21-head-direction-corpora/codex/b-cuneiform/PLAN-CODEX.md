# Cuneiform corpus plan

We will preserve every seal legend from the held Ur III archive and the specified Old Akkadian sources. The output will retain physical objects, edition references, lines, damage, language evidence and tagging decisions. Counts describe coverage; the analysis code will decide eligibility and group related legends.

1. Read the protocol, schema, acquisition script and earlier normaliser. Verify the held archive against its recorded SHA-256. Record the starting Git status so concurrent contributions remain distinguishable.
2. Acquire the Old Akkadian archive and the pinned CDLI catalogue, ATF and README. Each file gets a new directory and a separate acquisition record. Check archive member paths before extraction into directories containing data only.
3. Copy the required ORACC traversal and sign-unit conventions into our own standard-library normaliser. Read all archive entries. Keep seal surfaces separate from accounts, retain damaged legends, and reproduce the earlier clean sample before adding schema fields.
4. Select CDLI Old Akkadian seals and seal sections. Prefer ORACC editions where P-numbers overlap, preserve CDLI aliases and record uncertain identity or language for review. Write a vocabulary lexicon and local tables for inferred tags, unknown sites and unresolved cases.
5. Validate every record, report distinct sequences without grouping records, and compare ten seeded records per corpus against the archived edition text. Record the limits of this check when separate page access is outside the permitted URLs.
6. Write sources, aggregate counts and a retrospective with commands, output paths, repairs and coordinator decisions. Run the prose scan and inspect the final Git status against the starting state.

The contributor is Codex, GPT-6, through the Codex API tool harness. We will write only the owned paths, use Python with `-I` for source data, and make no Git mutations. Raw text, review samples and normalised records stay under the ignored `data/raw/` tree.
