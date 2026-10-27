# Dholavira count clarification

The completion message gave an incorrect explanation of the Dholavira stratum/depth counts. The frozen summary correctly records 211 stratum labels and 201 depth labels under both its including-Nil predicate and its usable-label predicate. Neither column contains a Nil cell, so excluding Nil changes neither count.

The difference comes from **Unst.**, including its final full stop. There are two such stratum cells and one such depth cell. A looser exclusion set that removes empty cells, dashes, question marks and Unst, while retaining Unst., gives 213 and 202. The frozen predicates also exclude Unst., giving 211 and 201. The stratum arithmetic is 225 − 2 empty − 10 dashes − 2 Unst. = 211; the depth arithmetic is 225 − 1 empty − 22 dashes − 1 Unst. = 201.

`CLARIFICATION-01.json` records each exact predicate, marker counts, input hashes and the correction. `clarification_01.py` reproduces the recount and verifies that every source-row dictionary matches the inherited extraction. It also verifies every frozen file hash before and after the recount. The pre-join endpoint remains `e574bfea349db809810cdb8b7fb06f832af41549f79f0b2de5e271fca7faddec`.

These are counts of source labels. A retained word such as Surface or Unstratified, or a compound survey/depth expression, does not become a numeric depth or an operational archaeological context. This clarification changes no source cell, construction/date assessment or C0018/C0019 eligibility result.
