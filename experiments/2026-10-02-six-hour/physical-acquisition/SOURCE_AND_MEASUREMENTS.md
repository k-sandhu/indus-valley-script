# Collecting the observations needed by the selector

The official Louvre notice for **SB 1940**, [cl010175973](https://collections.louvre.fr/ark:/53355/cl010175973), supplies a usable inside/outside observation: three round clay pieces and three rods, with three exterior circles and three elongated impressions. It records Susa, 3500–2900 BCE, a diameter of 4.9 cm and five photographic entries. Its bibliography points to *Before Writing. Vol. II. A Catalog of Near Eastern Tokens* (1992), pages 60 and 66, Suse 223–225 and 330–332. Those six catalogue identifiers are the next route to individual token records. The JSON notice's modified date is 11 August 2026; the HTML footer reports 15 January 2025.

The accession-linked [BnF caption](https://essentiels.bnf.fr/fr/image/2a59ae81-76d6-4921-b648-c21a8ae51c7e-bulle-enveloppe-scellee-et-calculi), permanent identifier `ark:/12148/mm106200279v`, gives three lenticular tokens and three small cones, a diameter of 6 cm and a date around 3300 BCE. Keep its terminology and measurement alongside the Louvre's record. The difference can be resolved through the underlying catalogue and conservation records. Both notices describe six enclosed pieces.

The new [acquisition manifest](source-acquisition.json) preserves local source hashes and retrieval routes. The web reader returned HTTP 403 for the BnF page; a direct HTTP retrieval subsequently succeeded. Raw notices remain local, and no photographs were acquired. The earlier [SB 1932 witness and collection plan](../physical-information/ARCHAEOLOGICAL_TARGET.md) remain useful for an envelope whose public notice supplies exterior detail but lacks an itemized contents record.

## What an equal mixture leaves ambiguous

SB 1940 has equal counts in its two reported token classes. Consider four unknown weights in this order: exterior circle, exterior elongated mark, interior round piece, interior rod. Comparing the reported totals yields the row `(3, 3, −3, −3)`. It has rank one. Positive vectors `(1, 2, 1, 2)` and `(1, 2, 2, 1)` both satisfy it. These constructed examples show how equal mixtures can preserve two cross-representation assignments.

A second equally mixed envelope would add a proportional row. A securely joined envelope with unequal class counts could distinguish those assignments. For example, a hypothetical inside/outside observation with one round piece and two rods, alongside one circle and two elongated marks, gives `(1, 2, −1, −2)`. It accepts the first vector and rejects the second. These hypothetical counts guide a catalogue search; they were not observed on another Susa object in this work.

The same object may supply a second kind of evidence. A geometric match between a token and an exterior negative imprint tests which token made which mark. That measurement distinguishes assignments even when class totals are equal. To measure numerical weights in goods units, the collection also needs a quantity observation with a documented unit. An envelope's six enclosed pieces supplies a piece count; the relation between a piece and a goods quantity requires its own record.

## Fields that make an acquisition decision possible

The simulation receives a bounded menu of potential observations and their availability before choosing. For the real collection, first build that menu from records. Each row below connects an observable field to a calculation in the experiment.

| Acquisition | Record before selection | Observation obtained | Calculation |
|---|---|---|---|
| Retrieve a token inventory | Envelope accession, publication location, visible exterior groups, retrieval cost and access status | Individual token identifiers, shape classes and membership basis | Add an inside/outside count row; check whether it increases rank or restricts the positive set. |
| Retrieve an opening or conservation record | Envelope condition and catalogue claims about contents | Whether all original contents were recovered, missing pieces, transfers or repairs | Use an equality for a complete group or an inequality for surviving contents. |
| Inspect a token/imprint contact | Accession, candidate shape classes, accessible views and measurement cost | Dimensions, curvature and deviations of the token and negative imprint | Remove cross-representation assignments inconsistent with measured geometry. |
| Obtain an independent quantity | Named physical object, measurement type, unit, declared precision and access status | Count or measured interval for that same object | Restrict scale and quantity coordinates; retain the measurement interval. |
| Reserve a separate envelope and count | Accession and source chosen before fitting | A complete relation and an independent measured quantity | Test both ratios and absolute scale after acquisition choices are fixed. |

The immediate collection steps are to inspect the six SB 1940 token entries in *Before Writing* II, locate their opening/conservation basis, and reconcile the two notices' shape labels and diameter. Then search the same accessioned collection for a securely documented unequal mixture. Preserve individual identifiers rather than matching envelopes by a similar photograph. Record the number of possible contents classes and the largest plausible contents group before applying the selector's outcome enumeration. Our two-/three-child bound and cost units are constructed simulation inputs; Susa envelopes need their own observed bounds and access costs.

For an Indus application, first locate an inscribed object with a documented physical relation to contents, capacity or assembled parts. The reusable calculation ranks candidate observations once those relations and measurement units are available. It can also preserve a quantity hypothesis set that remains broad after the available observations have been exhausted.
