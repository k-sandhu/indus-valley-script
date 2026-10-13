---
id: Q-1004
title: Build a face-level image index from the 8,722 local CISI crops
status: open
area: data
kind: metadata
priority: 2
data_access: local-only
compute: hours
difficulty: standard
claimed_by: ""
claim_expires: ""
prior_attempts: [READINESS-01]
related: [Q-0002, Q-0008, Q-1005, Q-1006, Q-1030]
sources: [knowledge/DATA.md, experiments/2026-10-12-data-inventory/run-2026-10-12/summary.json]
---

# Question

For every local face, which image files show it, from which CISI volume and page, as a seal or as an impression, and with which side label? Which faces have no image?

# Why it matters

Images are the field the project most needs for every face, and the local set is larger than its use so far. The Lipi repository holds 8,722 image files. Its index maps 3,318 CISI keys to 6,570 files; 2,152 files are outside the index, 297 of them named only by volume and page. By exact CISI key, 2,509 of 4,695 objects (53.4%) have at least one indexed image, and 2,483 have at least as many side labels in their file names as the export's side count. Dholavira has almost none (0.9%), because its objects lack CISI keys.

# What is needed

Read [DATA.md](../DATA.md). Inputs: `data/lipi/public/seal_images/`, `data/lipi/src/assets/data/seal_id_and_image_mapping.json`, `data/normalized/lipi_observed_faces.jsonl`, and the CISI 1 and 2 scans for checking. Parse each file name into CISI key, side (A, B, C …), impression marker (`imp`, lowercase captions), extra photograph (`bis`, `ter`) and scale suffix, following the conventions in `knowledge/provenance/catalogue-caveats.md`. Hash every file and group byte-identical files. Assign the 297 volume/page files to CISI keys by locating them on the scanned plates. The images stay local; the tracked index holds file hashes, parsed fields and joins.

# How to decide

Done when every image file has a parsed record or an explicit parse failure, every face has zero or more linked images with a stated join rule, and a coverage table reports faces and objects with any image, with a seal image and with an impression image, by site and object type. Check 50 random joins against the plates; any wrong side assignment requires a revised rule before release.

# Prior attempts

The October 2 readiness audit counted the image index and its exact-key matches without building a face-level join. This inventory repeated the object-level count.
