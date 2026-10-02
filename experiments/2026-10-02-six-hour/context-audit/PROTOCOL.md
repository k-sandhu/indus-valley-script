# Metadata availability and archaeological joins

Written October 2, 2026, before computing the audit. This run asks which archaeological comparisons the preserved observation tables can support, and which source records would improve them.

## Inputs and units

Read `data/normalized/lipi_observed_faces.jsonl`, `lipi_clean_rtl_singleline.jsonl`, `mayig_faces.jsonl`, their source summaries and the existing primary plate adjudications. Record their SHA256 values and the source pins. The full Lipi table has 5,680 rows and 4,695 numeric families. These families are the export's provisional object identifiers. Field availability is measured separately by row and by family.

The retained metadata is a derivative catalogue export. Existing plate checks concern graphics and layout on selected Mohenjo-daro objects. A metadata value becomes a source-inspected assertion only when a named primary caption, table, object photograph or excavation record is checked for that field. The audit will keep those categories separate.

## Availability rules

Inventory the literal values of site, region, CISI reference, area/section, block/house, room/grid, excavation item, time, period, phase, depth, material, motif, manufacture/type, shape and dimensions. Empty strings, strings containing only whitespace and hyphens, and explicit unknown labels are missing. Record the missing literals, so this rule can be inspected. For motif fields, `None` is a catalogued absence and receives its own count. In millimetre fields, a strictly positive numeric value is informative; zero is a placeholder. A nonnumeric dimension remains reported but unparsed. Retain the `h`, `v` and `th` source strings separately from the millimetre conversion.

For each family, report whether any face has an informative value, whether every face has one, and whether distinct informative values occur across its faces. Some fields describe surfaces, so multiple motif values can reflect the object's actual sides. Call these disagreements or variations without automatically assigning an error.

## Comparisons

Measure joint availability for: site plus manufacture/material; site plus excavation item/area; room or grid plus depth plus phase or period; phase/period plus manufacture/material; and positive horizontal/vertical dimensions plus motif. Tabulate availability by site and by object type. Count label variation within site and within site/type strata, and identify families sharing excavation IDs in their site namespace.

For a sign-based comparison use complete right-to-left single-line rows of length at least three. Form connected components from physical-family membership and identical whole sequences among these eligible rows. Keep every eligible face before computing components. Report repeated-text excess, component sizes, and components containing several sites, object types or metadata values. This shows how dependence changes the sample available to an archaeological test.

Mayig is a separate annotation of a restricted object block. Inventory its descriptions and actual metadata keys. Join it to simple Lipi CISI bases and count unique, ambiguous and absent joins, preserving all matched faces. Assess whether its description categories provide an independent response label or a source-restricted graphical annotation target.

## Primary source follow-up

After the availability results, seek one accessible original object group with an exact source pointer and useful context or manufacture evidence. Inspect the acquired HARP source and, if useful, its full public edition. A small source-coded table will record each assertion, printed/PDF page or figure, identity evidence, uncertainty and reuse status. Keep downloaded witnesses local. A source assertion is described narrowly enough for another reader to find and check it.

Choose one feasible follow-up experiment from the counts and source record. State its response, observation unit, controls, grouping rule and required additional coding. Any proposal chosen after the audit is labelled a post-audit design. This run's endpoint is availability and feasibility, rather than a fitted semantic model.

## Outputs and checks

Save aggregates, source hashes, code hash and a code snapshot in a fresh endpoint directory. Assert the known row/family counts, check family accounting and missingness totals, and test the placeholder rules on explicit examples. Preserve original summaries and witnesses. A short report will explain findings, challenges, corrections to the counting rule, unsuccessful source paths and the resulting experiment design. Raw sequences, full catalogue rows and downloaded source text remain local-only under the repository's redistribution policy.
