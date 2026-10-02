# A collection target with inside and outside observations

The Susa clay-envelope group provides a feasible comparison collection. An envelope can preserve exterior marks and a physically enclosed token group on the same object. This supplies a relation that a sequence export usually discards. Begin with accessioned envelopes whose contents have already been opened or documented, and preserve envelopes lacking a full contents record as incomplete observations.

## Original accessible witnesses

The Louvre's **SB 1932**, *Bulle avec empreinte et jetons*, has the stable identifier [cl010175963](https://collections.louvre.fr/ark:/53355/cl010175963) and a linked [JSON notice](https://collections.louvre.fr/ark:/53355/cl010175963.json). The notice records Susa, a manufacture interval of 3500–2900 BCE, discovery in 1933–1939, clay and a diameter of 5.1 cm. Seven photographic entries are available. Its description distinguishes cylinder-seal imagery and six intentional vertical lines within one image, with their numerical role left open. The public notice lacks an itemized enclosed-token inventory and token-to-envelope joins. Text and JSON were inspected; photographic URLs were recorded without counting pixels.

**SB 1940** appears by accession in Figure 18.8 of Schmandt-Besserat's 2018 chapter, [*Prehistoric Administrative Technologies and the Ancient Near Eastern Redistribution Economy – The case of greater Susiana*](https://sites.utexas.edu/dsb/tokens/prehistoric-administrative-technologies-and-the-ancient-near-eastern-redistribution-economy-the-case-of-greater-susiana/). The chapter discusses envelopes bearing both seal impressions and contents-related exterior marks. It supplies an original author-hosted route and an accession-based second target. The search here did not locate an official Louvre notice for SB 1940, so its catalogue join remains a collection step.

Schmandt-Besserat's [*Tokens: Facts and Interpretation*](https://sites.utexas.edu/dsb/files/2021/10/New-Tokens-FactsandInterpretationVisibleLanguage.pdf), *Visible Language* XX 3 (1986), printed page 256, reports sixteen envelopes with exterior markings and two exceptions to number/shape correspondence. One Susa example reportedly has three circular marks and two enclosed spheres. Another uses a circle, six lines and a small triangular impression for one large sphere, six spheres and a disk. These cases give specific disagreement targets to retain during collection. The available passage supplies site-level examples; assigning either exception to SB 1932 or SB 1940 requires an object-specific source.

The downloaded notices, webpage and author PDF remain local. [Acquisition records](source-acquisition.json) retain URLs, retrieval times, byte counts and hashes. The Louvre JSON's modified field is 11 August 2026; the inspected HTML page reported 30 March 2026. Preserve these as separate source dates. The image metadata carries named Louvre/GrandPalaisRmn copyrights. No photographs are included in this experiment's Git package.

## Relational fields to collect

Use one envelope record, a separate record for every token and explicit membership edges. Observation IDs assigned to unnumbered tokens should include the parent accession, view and location, with their status as annotation IDs recorded.

| Field | Purpose and collection step |
|---|---|
| Museum accession, excavation identifier, source edition and figure | Join pictures, opening records and catalogues to the same envelope. Keep each identifier's namespace. |
| Token-to-envelope membership basis | Record an opening inventory, conservation account or scan establishing the enclosed group. A museum display arrangement can serve as a locator for the necessary record. |
| Contents completeness | Record intact/opened/fragmentary condition, the original reported token total, missing pieces, conservation transfers and later additions. |
| Each token's shape, dimensions and visible components | Preserve count and subtype alternatives before assigning a value. Add photographs and 3D measurements with view provenance. |
| Exterior zone and mark group | Locate each repeated imprint, incision and seal image separately, preserving overlap and order where visible. |
| Tool or token-contact evidence | Record a geometric match between a token and a negative imprint, including deviations and uncertainty. |
| Envelope dimensions, cavity and repairs | Check whether available contents fit the preserved cavity and whether opening or repair could have changed the group. |
| Seal identities and impression coverage | Keep authority-related images separate from contents-related mark hypotheses during model fitting. |
| Find context and dating | Retain the actual layer, room, trench and dating source where available, alongside broader catalogue intervals. |
| Quantity/unit anchor | Record an independently observed count or quantity and what physical entity it measures. Counting enclosed tokens anchors token count; a goods-unit relation requires its own measurement or readable account. |

For the first pilot, obtain the original opening or conservation record for SB 1932 and the accession witness for SB 1940. Then locate each token in the photographic or conservation inventory and map each exterior mark group. A small sample of securely joined envelopes is more useful for this calculation than a larger list with unknown membership. No museum contact was sent during this work.

## Calculation on a collected pilot

Construct an exterior-mark count vector and an enclosed-token count vector for each envelope. First test direct contact: whether a proposed token shape predicts the geometry of an exterior negative imprint on an envelope withheld from matching. Next test number correspondence by shape, keeping the two published exception types as explicit controls.

Where exterior and interior conventions differ, form an equation between their weighted counts. Fit the unknown weights on some envelopes and ask which relative weights remain possible. Record rank, positive solutions, unit choices and completeness bounds. Reserve separately accessioned envelopes for prediction. This extends the simulation from one shared code inventory to two observed representations of the same physical group.

For an Indus application, the corresponding acquisition needs an inscribed container or tag with independently documented contents, capacity, attached object or complete assembled parts. The [simulation](README.md) specifies the benefit such a relationship could provide and the failure caused by silently completing missing contents. A pilot collection can first establish which physical relations survive and which quantities can be measured.
