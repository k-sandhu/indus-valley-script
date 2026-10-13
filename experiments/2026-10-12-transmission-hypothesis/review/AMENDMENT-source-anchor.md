# Source-anchor parser correction

12 October 2026. The first source audit stopped at `O-R04-4`: the PDF splits “alternative” across a line as `alter-` followed by `native`. Whitespace collapse preserved that discretionary hyphen and failed the literal anchor. The selected page had already been read, and its observation is unchanged.

Preserve `audit_sources.py` and `source-checks-v1/failure.json`. A successor parser will join word fragments at a PDF line-ending hyphen before checking the English source anchors and write `source-checks-v2`. It will retain all previous assertions and source inputs. This repairs extraction matching; it does not strengthen the historical comparison.
