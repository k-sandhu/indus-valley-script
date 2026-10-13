# Validator output-field correction

12 October 2026. The coordinator narrowed the gate name and output wording while the review fixture was being prepared. The first validator invocation passed its 21 declaration checks, but the review wrapper then expected the older `declared_local_descent_completeness_gate` key and raised `KeyError`. The fixture and validator output remain in `validator-scope-v1`.

A successor wrapper will read the current `declared_local_descent_record_completeness` key and write a fresh `validator-scope-v2` endpoint. The invented comparison and negative semantic test are unchanged. This correction concerns the review wrapper's output schema; it adds no historical observation and does not make the unsupported teaching claim valid.
