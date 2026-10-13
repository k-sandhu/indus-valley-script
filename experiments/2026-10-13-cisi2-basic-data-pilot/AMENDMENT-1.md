# Amendment 1: a full second reading of the pilot block

13 October 2026, 02:01 (UTC-4), written after the first pass was frozen (01:49) and the sampled second reading had been started, and before its results were seen.

The targeted comparison of the first pass with the Lipi `excavation-idno` field (run at 01:50 to test the join code) found about 30 cells where the scan cannot separate two digits, and several first-pass misreadings of the FC number. The protocol's sampled check measures the error rate but leaves the other 294 rows read once, and the protocol already requires double reading of every row if the error rate for columns 3 or 4 exceeds 2%. To keep the pilot within its time, a full second reading of all 327 entries (M-621 to M-947) is started now by another separate Claude instance, working from copies of the page renders in `data/raw/2026-10-13-cisi2-basic-data-pilot/pass2b/` with the same isolation rules: no access to the first pass, the sampled second pass, Lipi, the older export or the text layer.

Use of the readings:

1. The accuracy measure of the protocol is unchanged. It uses the first pass and the sampled second pass (`pass2/pass2.txt`), adjudicated against the page.
2. The full second reading (`pass2b/pass2b.txt`) is compared with the first pass on all rows and every disagreement is adjudicated against the page. On the 33 sampled rows it is a third reading, reported separately as a check on the adjudication.
3. The final local table applies, in this order of precedence: the sample adjudication, the full-reading adjudication, then the Lipi-prompted recheck (which may only resolve or bracket cells).
4. The agreement between the first pass and the full second reading over all rows is reported as a second, larger estimate of single-reader agreement, labelled as an amendment result.
