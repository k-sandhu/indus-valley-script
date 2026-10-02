# Resuming the local preservation copy

The first copy commands were interrupted while the new writing instructions arrived. A resumed byte comparison found mismatches in copied seal images. The original source files remained available.

The first detected file was `data/lipi/public/seal_images/M-1475_A.jpg`. Both copies were 47,678 bytes, but their hashes differed:

- Original source: `c2dff4a4c69e5596320576d82b1c2d794f9e44e4112bf4d2c9c3ea2ed6a3ea67`.
- Existing destination: `9ff08805568aac6c6615d449ed30d038698a329c37c6d7cd1188121afa50ef2c`.

The destination variant was preserved locally as `archive/2026-10-01-investigation/interrupted-import/M-1475_A.partial.jpg`, then replaced from the original source. The subsequent run detected another 48 mismatching inputs. Their previous bytes and hashes were preserved in the local quarantine and the [import manifest](../../archive/2026-10-01-investigation/import-manifest.json).

The copier now stages each new file before replacing its destination. It refuses to replace a changed research output. The optional repair mode applies only to imported `data/` paths and preserves the existing bytes first. A detached helper with hidden window and progress/error logs allowed the copy to finish while other work continued.

The completed import contains 16,284 files totaling 1,523,734,911 bytes. A subsequent hash check matched every imported file. Hash differences identify differing bytes; this record leaves their underlying cause unresolved.

The original selected evidence manifest refers to the old root README. Verification remaps that one historical path to `archive/2026-10-01-investigation/README.original.md`; the original file and its hash are preserved. The current root README is the new knowledge index.
