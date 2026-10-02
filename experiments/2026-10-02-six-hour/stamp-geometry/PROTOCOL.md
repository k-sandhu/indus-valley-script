# Flat-stamp visibility on a curved vessel wall

Freeze this protocol before running the forward model. The acquired Harappa drawing H1714 shows a flat, rectangular, inscribed face with three broad graphic groups. The Beas photograph shows four stamped curved vessel fragments, including footprints cut by fracture edges. These observations motivate a geometry study. They provide no measured vessel radii, groove depths or clay constitutive parameters, so those quantities are declared simulation inputs.

The bounded question is whether curvature and survival can change the frequency of synthetic graphic classes at the first and last visible positions. The primary prediction is that a centred cylindrical wall, a centred stamp and symmetric preservation give equal left and right endpoint distributions. Reversing a tilt or break side should reverse its visibility effect. A consistently signed tilt or a consistently sided break may give unequal distributions. We will report the size of any simulated effect and the physical observation needed to test it.

## Physical model and shared assumptions

Let the rectangular stamp use coordinates `(u,v)`. Its row direction makes angle `alpha` with the vessel's circumferential direction. The cylinder coordinate is `x=u*cos(alpha)-v*sin(alpha)`. The convex wall drops below its tangent by `sag(x)=R-sqrt(R²-x²)`. A flat stamp translated down by `d` and tilted with plane slopes `tu,tv` gives local land penetration

`delta(u,v) = d - sag(x) - tu*u - tv*v`.

The primary model is displacement controlled. It calculates geometric contact and an assumed retained relief; it has no force prediction. Positive `delta` denotes land contact. With a rectangular carved groove of depth `h`, the local imprint relief is `eta * min(h, max(delta,0))`. This independent-column construction gives a declared geometric visibility law. `eta` represents retained relief and is varied because lateral clay flow, sticking, withdrawal and firing are unmeasured. A triangular groove profile is a separate sensitivity. The contact geometry is shared by both.

For image resolution, apply the analytic peak attenuation of a uniform line blurred by a Gaussian: `erf(width/(2*sqrt(2)*sigma))`, with attenuation one at `sigma=0`. This local straight-line approximation is checked against an independently rasterized line and convolution. It does not model intersections or a complete camera pipeline. A stroke element survives when retained height after attenuation is at least 0.08 mm. A graphic is counted visible when at least 80% of its sampled stroke length survives.

Damage is a retained half-plane. Primary cases retain the complete stamp, remove its leftmost quarter or remove its rightmost quarter. A sample outside the retained region contributes zero relief. Physical reading direction and positive-impression mirroring remain separate from these geometric coordinates. The synthetic classes are symmetric invented shapes with no assigned Indus sound or meaning.

## Declared frames and runs

Use two illustrative rectangular faces: 14×8 mm with three equally spaced slots, and 24×8 mm with eight slots. H1714's scale-bearing drawing will receive a separate measurement note using manual face and 30 mm scale-bar bounds, including endpoint uncertainty. The simulation frames are declared examples, not fitted reconstructions of a seal–sherd pair.

Each slot can contain four equiprobable synthetic classes: a narrow vertical line, a broad cross, a rectangular loop and a diagonal cross. All are centred in their slot and symmetric under a half-turn. Their width and height scale with slot pitch. Enumerate conditional visibility for every class in every slot; compute exact expected first/last-visible class probabilities under independent uniform choices. Preserve rows with no visible graphic in the accounting.

The primary geometry grid uses radii `[15,25,50,100,200,infinity]` mm, displacements `[0.05,0.1,0.2,0.4,0.8,1.2]` mm, row-axis tilts `[-4,-2,0,2,4]` degrees and row rotations `[0,30,60,90]` degrees. The orthogonal tilt is zero. With two layouts, this gives 1,440 geometries. Evaluate all three preservation cases with groove depth 0.4 mm, width 0.16 mm, retention one and blur sigma 0.025 mm. Use 256 samples per stroke and seven transverse samples for the main groove-profile check; the primary rectangular-profile length measure uses centreline samples.

A nuisance grid uses the eight-slot frame, radii `[25,100,infinity]`, displacements `[0.1,0.4,0.8]`, tilts `[0,2]`, rotations `[0,90]`, groove depths `[0.1,0.2,0.4]`, widths `[0.08,0.16,0.32]`, retention `[0.25,0.5,1]` and blur sigmas `[0,0.025,0.05]`, again with the three preservation cases. This is 8,748 declared configurations. Compare the rectangular and triangular profiles on a named subset. Report empty observations and depth thresholds explicitly.

## Measurements and checks

For every configuration retain slot/class visibility, expected row retention, visible length, endpoint class probabilities, class-frequency distortion, left–right endpoint total variation and outer-versus-middle visibility. Pool the equal-weight primary geometries by zero tilt, balanced tilt, positive tilt and preservation side. Weight observed endpoint distributions by the probability that a row remains visible. Report descriptive maxima with their input configurations.

For zero tilt and an aligned row, contact half-width has the exact form `sqrt(2*R*d-d²)`, capped at the stamp boundary. The height threshold replaces `d` by `d - threshold/(eta*attenuation)` when groove depth can reach that threshold. For row-axis tilt, solve the quadratic contact-boundary equation and compare its roots with an independently coded scalar bisection of the circle/plane intersection. Check flat-wall, zero-displacement, complete-contact, reflection and rotation limits. Compare contact area against progressively finer numerical grids. Check the line-blur approximation by independent raster convolution and check endpoint probability calculations by exhaustive enumeration in the three-slot frame.

If a numerical implementation fails a declared check, preserve its pilot endpoint and describe the change before running a new endpoint. No parameter will be chosen to fit the Beas graphics. A useful physical test would stamp the same measured matrix at controlled curvature and pressing angle, photograph both the footprint and the fracture boundary, and record the displaced relief. Its purpose is to test the visibility law and its assumptions.

## Sources and deliverables

The primary mechanics references are Ball, Balmforth and Hewitt (2019), *Indentation into a plastic fluid layer*, and Abou-Samra, Ewane and Silvestri (2020), *Physical modeling and arbitrary Lagrangian–Eulerian finite element analysis of indentation of a sensitive clay by a flat-ended axisymmetrical indenter*. Their plastic-flow treatments inform the model's limits and the need for material calibration. Lucchini, Stuart and Cassoni's 2025 experimental ceramic study supplies direct observations on pressure distribution, tool application and clay state. Preserve the source access, rights notices and failed routes in a provenance note.

Track own code, protocol, parameters, results, diagrams, source assertions and retrospective under this dated folder. Bulk downloaded sources, source pixels and extracted text remain under ignored `local-witness/`. Preserve every endpoint. Perform no Git, CI or automation actions.
