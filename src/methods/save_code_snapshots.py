"""Recover the pre-artifact-alias annotation version for audit hashes."""
import hashlib
import json
from pathlib import Path

current = Path(__file__).with_name("conditional_structure.py").read_bytes()
old = current.replace(
    b"    # Frame/sign keys deduplicate whole sequences while retaining every artifact\n    # alias for independent metadata auditing. Lists do not enter edge counts.\n",
    b"    # Whole-sequence deduplication prevents repeated impressions from creating edges.\n    seen = set()\n",
).replace(
    b'        seq = row["seq"]\n        for i, sign in enumerate(seq):\n            key = (len(seq), i, seq[:i]',
    b'        seq = row["seq"]\n        if seq in seen:\n            continue\n        seen.add(seq)\n        for i, sign in enumerate(seq):\n            key = (len(seq), i, seq[:i]',
)
out = Path("research/methods/code_snapshots/conditional_structure_initial.py")
out.write_bytes(old)
recovered_hash = hashlib.sha256(old).hexdigest()
print("Recovered conditional snapshot:", recovered_hash)
pilot = json.loads(Path("research/methods/results/pilot/conditional_results.json").read_text(encoding="utf-8"))
print("Pilot original hash:", pilot["source_code_sha256"])
print("Snapshot predates collapse-option addition; pilot mismatch may be expected.")
