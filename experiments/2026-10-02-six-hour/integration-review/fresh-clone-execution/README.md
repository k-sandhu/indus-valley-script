# Execution from a clean local clone

The local clone of commit `f979d5aa35e662cdba060ab969acef82dec0cb55` began and ended with a clean Git working tree. Its excluded 132,193,239-byte mixture result was absent. The tracked gzip chunks reconstructed its recorded SHA-256 without access to the original file. [Results](results.json).

The identification audit also ran from the clone's tracked synthetic inputs. It reconstructed 345,600 exact paired entries, checked 34,560 marginals and 144 positive mixing vectors, certified 288 rational minors and repeated 5,760 grouped-product checks. It passed in 2.49 seconds. Main and collapsed endpoint hashes match the earlier audit.

The original audit has a fixed output path containing a preserved review. A copied helper changes that one line to a fresh ignored `tmp/` directory. [The executed copy](executed-audit-copy.py), original/copy hashes and exact before/after line remain in this endpoint. Its scientific inputs and arithmetic are unchanged. Neither original source nor a frozen review was overwritten.

The [driver snapshot](helper_snapshot.py) records the execution. The current [driver](../../../../tools/check_fresh_clone.py) additionally refuses an existing temporary audit copy or output. Run it with a fresh clone and a new output directory:

```powershell
python tools/check_fresh_clone.py --clone PATH-TO-NEW-CLONE --output experiments/NEW-DATE/fresh-clone-check
```

This check exercises package reconstruction and the exact identification audit. Corpus-dependent restoration and acquired-source replication use the inputs described in the [checkout source routes](../checkout-availability/REPORT.md). The clone stays locally under the project's ignored `tmp/` directory.
