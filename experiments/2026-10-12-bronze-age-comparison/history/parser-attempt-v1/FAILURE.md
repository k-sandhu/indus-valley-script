# First normalization attempt

The first normalization process parsed the three cuneiform archives and stopped while reading Egyptian tokens that lack `_id`. It wrote no normalized dataset and ran no statistical models. The local log and empty `normalized-v1` directory are preserved. This directory preserves the exact parser and analysis entry point used by that attempt.

The successor parser retains the missing-ID condition as an exclusion rather than inventing a source locator. XML identifiers beginning with `tla` had already been normalized and blank JSON entries counted during pre-run format checks. The first successfully frozen dataset uses `normalized-v2`; the first statistical endpoint is `run-v1`.
