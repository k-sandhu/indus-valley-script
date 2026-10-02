# Straight tally diagnostic

This extension tests a fixed mass per repeated mark within the same recorded shape, material and date category. It was requested after the three-weight calculation. Rules were set before calculating aggregate ranges, following inspection of individual source entries.

Collect every Susa entry explicitly described as “with marking” or “with markings” with a coded graphic sequence. Textual cuneiform inscriptions form a separate control. A mass with +x supplies a lower bound and stays in the acquisition census but leaves the ratio analysis. Mixed graphics remain in the derivative without a per-mark division.

Divide published mass by the count of identical strokes, circles or crosses. Preserve recorded shape and material, including the distinction between ovoids and ovoid/discoid pebbles. Join line-wrapped material names. Group unpolished hematite with hematite; preserve uncertain material identifications separately. A missing creation date is a metadata bucket whose members can span periods.

Publish all group members' catalogue IDs, minimum and maximum mass per mark, and the smallest symmetric tolerance covering the range. This measures what the rival requires; it does not estimate manufacturing variation. Full factual extraction stays local-only with a published hash. Parsing failures stop the endpoint.

The first saved endpoint remains `marked-weight-census.json`, with code `census_v1.py`. Version 2 corrects line-wrapped words, a shortened pebble shape, and a material field extending into dimensions. It recovers cat. 207, whose “markings” word was split in the PDF. It excludes cats. 119 and 129, which repeat SB 13514 at different masses, and cat. 120, which repeats SB 13747 assigned to a large duck at cat. 609. All entries stay in the local acquisition census.

Some chipped objects carry a printed mass without +x. They remain in the analysis with their recorded condition. No original mass is reconstructed. Only three graphic entries supply explicit creation-date ranges, in separate groups; the dated subset cannot estimate a shared unit from two contemporary objects. Review source entries furnishing group extremes before citing results.
