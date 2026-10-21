# Harappa vessel stamps belong to the manufacture of the vessel

We recovered two identified primary drawings and their individual excavation keys from a block of 47 Harappa sealings and stamped vessels. H-1745 was recovered from the fill of a Period 3C sump pit. H-1734 came from fill in Trench 10W, and its caption restores the missing registration H95-2526. Both objects are stamped goblet fragments. The excavators identify the larger 40-object vessel group as marked before firing. Their labels therefore entered the vessel's history during manufacture; the deposits where the fragments were recovered record a later event.

The [complete disposition](run-v1/target-dispositions.csv), [source observations](source-observations.json) and [aggregate output](run-v1/summary.json) retain all targets, including nine absent from the export. This is a source audit. We do not give a new sign a sound or a lexical meaning.

## What was added

The starting block is the gap left by [ARCH-01](../2026-10-02-six-hour/harappa-object-frame/README.md): sealings and stopper H-1719–H-1725, and stamped vessels H-1727–H-1766. Of the 47 targets, 38 occur in the export on 40 face records. The new source links provide the following coverage within this block.

| Field | Starting ledger | This run |
|---|---:|---:|
| Explicit published source for the marking operation | 0 | 47 |
| Identified primary drawing | 0 | 2 |
| Individual published lot, item and locus | 0 | 2 |
| Restored registration omitted from the export string | 0 | 1 |
| Direct observation of contents | 0 | 0 |
| Identified reverse attachment view | 0 | 0 |

These are changes to the bounded source ledger. They do not measure how many of the facts were absent from every earlier project document. We add no direct calendar date; the source's Period 3C interval is a group assignment based on vessel and seal type.

The two joins come from Meadow and Kenoyer's 1997 *Excavations at Harappa 1994-1995: New Perspectives on the Indus Script, Craft Activities, and City Organization*, printed p. 161, Figure 12, PDF p. 23. We inspected the complete page and caption after rendering it with Poppler.

| Target | Caption specimen | Registration | Lot and item | Published recovery setting |
|---|---|---|---|---|
| H-1745 | 12.04 | H95-2407 | 5080-500 | Mughal sarai, fill of Period 3C sump pit |
| H-1734 | 12.08 | H95-2526 | 4450-31 | Trench 10W, fill |

H-1745 has a unique exact registration match. H-1734 has a unique year, lot and item match: the export writes H95-4450-31 and omits registration 2526. We retain both forms. The displayed rim, shoulder or wall profile and impressed panel support the caption's vessel identification. Fine sign identities were not coded.

Figure 12 also shows three stamped goblet fragments with unique excavation keys, H94/5356-82, H94/5307-15 and H95/4724-51. No export excavation string matches those keys. They are unjoined source records, with no new CISI number assigned.

## The physical comparison

Kenoyer and Meadow's 2010 [*Inscribed Objects from Harappa Excavations 1986–2007*](https://www.harappa.com/sites/default/files/pdf/KenoyerMeadow%202010%20Inscribed%20Objects%20from%20Harappa.pdf), author-manuscript p. 7, explicitly separates the seven sealing objects from the 40 vessel stamps. We inspected the complete page.

| Objects | Operation reported by the excavators | What the recovery evidence establishes |
|---|---|---|
| H-1719–H-1724 | Impressions on separate clay tags; all were partly hardened by low firing | Their contexts are secondary. Deliberate preservation and later heating remain alternatives. |
| H-1725 | Impression on an unbaked sub-conical jar stopper | Prompt conservation prevented disintegration as salts crystallized. |
| H-1727–H-1766 | Impressions in vessel walls before firing, associated with pointed-base goblets | The mark was selected during manufacture. Two individual captions now identify later fill or disposal deposits. |

This sequence constrains function. A newly incised mark on a used pot could record a recent owner or contents. A fired impression must have been chosen earlier. It can designate a producer, an intended owner, a commissioning institution, an intended commodity or a ritual use. Subsequent filling does not change the inscription. A commodity interpretation would therefore concern an assigned class of use, unless independent evidence shows a different sequence of operations.

The [source observations](source-observations.json) preserve a conflict: the export calls H-1741 a TAG, while the excavators' explicit H-1727–H-1766 range includes it among vessel stamps. We retain the conflict for a plate check rather than silently recode it.

The acquired [Three clay sealings](https://www.harappa.com/slide/three-clay-sealings) photograph shows three separate fragments, but its caption has no object numbers. The [Unicorn sealing](https://www.harappa.com/slide/unicorn-sealing) photograph has registration H2000-4453/2174-192 and a Trench 54 attribution. That registration has no export match. We do not assign it to the missing H-1724 by elimination. The displayed faces do not show a reverse matched to a cord or container, so they supply no identified attachment outcome for this frame.

## Why no classifier was fitted

The [protocol](PROTOCOL.md) required at least ten independent object and text groups in each operation class before prediction. The entire sealing class has only seven objects. It fails that bound before duplicate texts or aliases are joined. There are also no direct contents labels and no securely registered pair linking an extant seal to one of the vessel impressions. A prediction score would answer a weaker question than the one we specified.

The [shared shots synthetic run](shots-synthetic-v1.json) passed its loader, freeze, closure and spending guards. It tests generated data and contributes no archaeological evidence. No real confirmation half was opened, no new seed was used to claim fresh evidence, and no shared spending-ledger entry was changed. The [ledger audit](SPENT-AUDIT.json) records that decision.

## What would decide the next reading

The most informative next witness is a stamped goblet waster from an identified pottery-production deposit, together with a source registration, adjoining wall profile and a legible impression. It would directly connect a legend to a production batch. Clay fabric, tool marks and compositional measurements would then define manufacturing groups independently of the inscription. Residues or deposits associated with use would provide a second, separate set of labels.

A producer designation predicts that its exact stamp or legend remains concentrated in a manufacturing group after vessel form and period are controlled, including vessels distributed to different settlements. A commodity designation predicts recurrence with independently identified contents across manufacturing groups. A commissioning institution can order from several producers, so evidence for mixed fabrics would distinguish that explanation from a single producer. A ritual designation needs a repeatable use-context association established independently of the signs.

We would construct those candidates on a discovery group and freeze the mapping, physical identity rules and chance comparison before a fresh production or use group is opened. A credible test requires enough independently identified groups; the present material cannot supply a useful power calculation for measurements that have not yet been collected.

The boldest supported reading is that the Harappa goblet stamps are persistent designations chosen during vessel manufacture. The decisive next test is whether the same designation follows an independently established manufacturing group or an independently established content or use class across manufacturing groups.
