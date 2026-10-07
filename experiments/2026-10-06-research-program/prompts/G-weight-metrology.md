# Package G: the Indus weight system across sites and regions

Owned directory: `experiments/2026-10-06-weight-metrology/`. Local raw directory: `data/raw/2026-10-06-weight-metrology/`. Use live web search for precedents.

## Question

This package studies the Indus civilization's weight system as archaeology in its own right, apart from the script. The project holds Ascalone's 2022 catalogue, *Bronze Age Weights from Mesopotamia, Iran & Greater Indus Valley*, locally as `data/raw/2026-10-02-connections-and-priority/regional-west/ascalone2022.pdf` and an extracted text file beside it. Its Greater Indus section has 938 entries (Dholavira 870, Bagasra 19, Nagwada 16, Rakhigarhi 15, Farmana 8, Shikarpur 7, Kuntasi 2, Nageshwar 1); the Dholavira chapter (printed pp.135–136) reports 505 objects with archaeological context and 435 classed as certain balance weights. The Mesopotamian and Iranian sections cover the other catalogue entries. Earlier project work on this book is in `experiments/2026-10-02-connections-and-priority/regional-west/` (see `indus-weight-audit.json`, the Susa marked-weight census and `REPORT.md`) and `experiments/2026-10-02-source-recovery/susa/`.

Ask: how precisely do Indus weights realize a common unit and series, and does that precision vary by site, material, shape, preservation and excavation context? Where in Mesopotamia, Iran and the Gulf do weights compatible with the Indus standard occur, and how does their fit compare with local standards?

## Steps

1. Extract every catalogue entry into structured rows: catalogue number, museum or excavation identifiers, site, context and period fields, material, shape, dimensions, mass, preservation or damage notes, marks, and the catalogue's own unit attribution where given. Write the parser and its validation in the owned directory; keep the extracted rows, which reproduce third-party catalogue content, in the local raw directory and track only aggregates. Validate the parser against a random sample of at least 60 entries checked by eye against the rendered PDF pages, and report the error rate.
2. Write `PROTOCOL.md` before any fitting. Specify: Kendall's cosine quantogram with a Monte Carlo significance envelope over a declared quantum range; a likelihood or Bayesian model in which each weight is an integer or declared fractional multiple of a unit with multiplicative error, compared across candidate series (the binary-then-decimal series described by Hemmy 1937 and later authors, a purely binary series, and the competing Near Eastern shekel standards); damage and wear handling (exclude, down-weight or model loss of mass, decided before fitting); and stratified comparisons by site, material (chert and other stones), shape, preservation and the certain versus uncertain balance-weight classes.
3. Estimate the unit and its dispersion for Dholavira overall and by context where the catalogue gives it, for each other Indus site with enough weights, and for western assemblages. Report what fraction of western weights fit the Indus standard better than the local alternatives, with intervals, and list the specific objects driving that result.

## Precedents to check before claiming anything new

Hemmy 1937 on Harappan and Mohenjo-daro weights; Mainkar 1984; Kenoyer 2010, "Measuring the Harappan World"; Miller 2013 on weights and measures; Ascalone and Peyronel's work on Indus and Near Eastern weights, and Ascalone 2022's own analyses in the same book; Højlund on the Dilmun standard; Ialongo, Vacca and Peyronel 2018 and Ialongo and Lago 2021 on frequency-distribution methods for Bronze Age weights; Rahmstorf's work on Bronze Age weight systems; Petruso on Aegean weights. State exactly what each already established and what your analysis adds, if anything.

## Outputs

Parser and validation report, aggregate tables (counts by site and class, unit estimates, dispersion, quantogram peaks, model comparisons), code, and a `REPORT.md` with the findings, their bases and the further measurements (for example reweighing, wear documentation, context recovery) that would sharpen them.
