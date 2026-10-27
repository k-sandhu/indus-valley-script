# Fields for independent layout review

Each reviewer records one object face against a named image witness. They first confirm the object and side, then describe the layout before seeing a model boundary or another reader's decision. Keep the original entries when adjudication adds a third decision. A reviewer may inspect the historically examined held-image queue immediately. Candidate new objects first require the agreed exposure and cohort procedure.

| Field group | Required entries |
|---|---|
| Identity | Provisional object ID, source face ID, catalogue and accession identifiers, identity relation, conflict status, source supporting the join |
| Image witness | File or source URL, SHA-256, source page and plate coordinates, object photograph or impression, displayed resolution, crop bounds |
| Display transform | Original orientation, horizontal reflection if applied, rotation in degrees, transformation record; retain the original image |
| Observation | Surface and line identifiers, countable graphic groups, bounding boxes in original image pixels, group positions, visible spacing, damage polygons, uncertain sign counts |
| Order | Physical top-to-bottom or side-by-side arrangement, proposed traversal with its observation basis, alternatives, certainty and reason; keep physical arrangement separate from an inferred reading order |
| Division labels | Required physical divisions, unresolved positions, whether a grouping is wrapped text, detached field, strokes, or other; label completeness is partial for Indus |
| Reader record | Reviewer ID, timestamp, what source text and catalogue codes the reviewer saw, source access log, whether prior model predictions were visible |
| Adjudication | Two original decisions, agreement fields, adjudicator, source coordinates resolving disagreement, unresolved alternatives, revision history |

Store sign bounding boxes and counts locally with the source witnesses. Track aggregate agreement and missingness, source hashes and the resulting eligibility rule. Use the common register IDs for joins and preserve the source's raw labels alongside normalized fields. Missing geometry or uncertain source identity keeps a face in the queue.

For readable controls, add editorial word boundaries, the edition's tokenization conventions, source word references, physical object or composite status, and aliases. Complete boundaries describe that edition's annotation. Their independence and transfer to the Indus graphic task are separate questions addressed by the staged protocol.
