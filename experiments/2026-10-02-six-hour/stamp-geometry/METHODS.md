# Contact and observation model

This is a displacement-controlled geometric model. It places a rigid rectangular carved face against a cylindrical clay surface, then applies a declared relief-transfer and visibility rule. The primary graphics are four equally probable invented shapes, chosen independently at each slot. They have the same central placement and reversal symmetry. Input configurations have equal prior weight. These assumptions allow the calculation to isolate curvature, pressing angle and preservation. Actual seal layouts, clay flow, pressing force and archaeological sampling weights require measured inputs.

## Geometry and relief

All lengths are in millimetres. Stamp coordinates `(u,v)` run along and across the graphic row. Its angle to the cylinder's circumferential direction is `alpha`, so the cylinder coordinate is `x = u cos(alpha) - v sin(alpha)`. For radius `R`, the surface drops below its tangent by

`sag(x) = R - sqrt(R² - x²)`.

The implementation uses the algebraically identical `x²/(R + sqrt(R² - x²))` to avoid cancellation at large radius. At infinite radius, sag is zero. The stamp moves by `d` into the tangent plane and has slopes `tu = tan(beta_u)` and `tv = tan(beta_v)`. Local land penetration is

`delta(u,v) = d - sag(x) - tu*u - tv*v`.

Positive penetration defines contact. A rectangular groove of depth `h` receives retained relief `eta * min(h, max(delta,0))`, where `eta` is a declared retention factor. A line of width `w` blurred by a Gaussian of standard deviation `sigma` has peak attenuation `A = erf(w/(2 sqrt(2) sigma))`; `A=1` when blur is zero. A stroke point survives when the attenuated relief reaches 0.08 mm and lies inside the retained damage half-plane. A graphic is visible when at least 80% of its total straight-stroke length survives.

The relief law treats columns independently. Lateral flow, groove filling, adhesion, withdrawal and firing can change the actual relief, so these enter the acquisition experiment as measurements. The blur formula is a local straight-line approximation. Its independent raster-convolution check reaches a maximum error of 4.74×10⁻⁷ for the checked widths and blur values. A separate triangular-groove sensitivity averages relief across seven transverse samples before applying the same blur factor. That sensitivity changed visibility in 14 of 72 comparisons and shows that groove profile matters near the threshold.

Damage retains the entire face or removes its leftmost or rightmost quarter. These are geometric sides in the stamp frame. Matrix polarity, impression mirroring and physical reading direction are separate observation fields.

## Exact surviving stroke length

For a straight stroke parameterized by `s` from zero to one, write `u=u0+du*s`, `v=v0+dv*s`, and `x=x0+dx*s`. If `eta*h*A` reaches the visibility height, define `q = 0.08/(eta*A)`. The contact condition at that height is

`sqrt(R² - x²) >= R - d + q + tu*u + tv*v`.

Throughout this grid the right side is positive. Let it be `k0+dk*s`. Squaring gives the interval inequality

`a*s² + 2*b*s - c <= 0`,

where `a=dx²+dk²`, `b=x0*dx+k0*dk`, and `c=R²-x0²-k0²`. Its roots bound the surviving part of the stroke. Intersect that interval with `[0,1]` and the damage half-plane, then multiply its length by the stroke length. Degenerate constant and flat-wall cases are handled separately. Weighted sums across a graphic's strokes give its exact surviving fraction. The initial endpoint instead used 256 midpoint samples per stroke; both remain preserved.

With zero tilt and an aligned face, land-contact half-width is `sqrt(2*R*d-d²)`, capped at the stamp edge. For the visibility-height boundary, replace `d` by `d-q`. The code checks contact roots against scalar bisection in 27 cases and area against independent grids at four rotations. It also checks zero displacement, complete flat contact, a groove below threshold and reflected configurations.

## Endpoint probabilities and selection

Let `V[i,k]` indicate whether class `k` is visible at slot `i`. With four equiprobable classes, slot survival probability is `p[i]=sum_k V[i,k]/4`. The probability that class `k` is the first visible graphic at slot `i` is

`V[i,k]/4 * product_(j<i)(1-p[j])`.

Sum across slots and divide by the probability of at least one surviving graphic. The last-visible formula runs from the opposite end. The minimum-three extension multiplies each first-visible term by the probability that at least two later graphics survive. A polynomial product `product_i[(1-p[i])+p[i]*z]` gives the full visible-length distribution. The code checks these probabilities against exhaustive enumeration of all 64 three-slot rows and two selected eight-slot cases of 65,536 rows each.

For pooled results, sum unconditional endpoint masses across configurations before dividing by pooled retained-row mass. A configuration that loses every graphic contributes to the denominator of mean retention and contributes no observed endpoint. Pools with zero chance of meeting the selection threshold have undefined endpoint distributions, recorded as `null` in the reviewed endpoint.

The map `(u,v) -> (-u,-v)` preserves the invented graphic shapes and reverses the slots. It changes the signs of both tilt slopes and exchanges break sides. The cylinder sag is unchanged because it depends on `x²`. Reversal therefore exchanges first and last probabilities. Equal weights for each configuration and its reflected partner give equal pooled endpoints, including after selection by visible length. Class visibility can remain unequal even when this symmetry holds.

## Run record

The [frozen protocol](PROTOCOL.md) contains the complete primary and nuisance grids. The primary run predates [the length-selection protocol](LENGTH-SELECTION-PROTOCOL.md), [the exact-integration refinement](ANALYTIC-REFINEMENT.md) and [the statistics-field review](reviewed/record.json). The current overview uses exact primary geometry with the reviewed representation of empty pools. The nuisance and triangular-profile results retain the original numerical method and are labelled accordingly. The maxima in the original grid are descriptive selected cases, with their full parameters retained in [main/extreme-examples.json](main/extreme-examples.json).
