# What the tablet drawing preserves under alternative orientations

The 19 readable pairs of lower faces in Meadow and Kenoyer's Figure 4 occupy eight displayed arrangements. Allowing the two lower faces to exchange reduces them to four groups. Allowing a common end reversal reduces them to two: 11 tablets place the A and D forms on the same displayed side of their stroke groups, and eight place them on opposite sides. Independently reversing each face merges all arrangements into one group. [Calculated partitions and object identifiers](main/results.json).

The calculation helps specify the next observation. A photographic or 3D record that identifies adjoining faces and a common physical end can preserve distinctions which an independently oriented drawing may erase.

## Observations and assumptions

The source shows three rectangular faces of each of 22 triangular-section tablets. The two lower displayed faces have one angle-like form A and one diamond-like form D where readable. Each appears beside short upright strokes. The [first coding](../harappa-object-frame/figure4-first-observations.json) and [native-raster refinement](../harappa-object-frame/figure4-native-reinspection.json) resolve 19 lower-face pairs; three remain obscured.

The source describes variation in sequence and orientation as a tablet is turned and reports microscopic inspection of cutting direction. The inspected figure and text leave the turning convention, common physical end and drawing-to-prism face map unspecified. Our A/D and left/right labels are display observations. The complex form on the top displayed face has no coded physical orientation anchor. [Source correction and orientation assessment](../harappa-object-frame/corrections/2026-10-02-scale-and-pagination/README.md).

The protocol evaluates four conditional representations of the two lower faces. Face exchange identifies arrangements with the same A and D positions, regardless of which appears in the middle drawing row. A common reversal changes both positions together, retaining whether they agree. Independent reversal changes either position separately; it represents a possible drawing convention. A whole-object reversal would also change the top face, which this calculation omits. The experiment's domain is this two-face projection.

| Representation | Groups | Objects in each group |
|---|---:|---|
| Fixed displayed rows and ends | 8 | 2, 2, 2, 5, 2, 3, 1, 2 |
| Exchangeable lower faces | 4 | 4, 3, 5, 7 |
| Exchangeable faces and common end reversal | 2 | 11 same-side; 8 opposite-side |
| Exchangeable faces and separate end reversals | 1 | 19 |

The three unresolved tablets give a possible total of 11–14 same-side objects and 8–11 opposite-side objects across the complete 22-object frame. These ranges retain their missing observations without imputing an arrangement.

## Computation and check

The main routine forms transformation orbits over all eight binary display states. It checks the partitions, involutions and object totals. The independent review reconstructs the 19 pairs directly from the first source annotations and six native-resolution field changes. It joins their source specimen numbers to the preserved registration ledger, then classifies by explicit A and D positions. This route reproduces every group and target membership without calling the orbit routine. Seven main checks and nine review checks passed. [Protocol](PROTOCOL.md), [main code](../../../src/six_hour/tablet_representation.py), [review checks](review/checks.json), [review code](../../../src/six_hour/review_tablet_representation.py).

The published chapter already describes varied arrangements and three proposed engraver groups. Our result makes the dependence on representation explicit and supplies a source-linked grouping table. It gives acquisition requirements for an object-level comparison: common ends, adjacency, incision orientation, readable stroke counts and damage fields.
