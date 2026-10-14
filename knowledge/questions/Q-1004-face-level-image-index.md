---
id: Q-1004
title: Build an index linking each inscribed face to the 8,722 local CISI photograph crops
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

The local corpus records each inscribed side or view of an object as a separate row, called a face. For every face, which image files show it, from which volume and page of the *Corpus of Indus Seals and Inscriptions* (CISI), as the seal itself or as an impression, and with which side label? Which faces have no image?

# Why it matters

Images are the field the project most needs for every face, and the local set is larger than its use so far. The Lipi repository, our local transcription corpus, holds 8,722 image files cropped from the CISI plates. Its index maps 3,318 CISI keys (the catalogue numbers under which it files images) to 6,570 files; 2,152 files are outside the index, 297 of them named only by volume and page. Matching on the exact CISI key, 2,509 of 4,695 objects (53.4%) have at least one indexed image, and 2,483 have at least as many side labels in their file names as the export records sides. Dholavira has almost none (0.9%), because its objects lack CISI keys.

# What is needed

Read [DATA.md](../DATA.md). Inputs: `data/lipi/public/seal_images/`, `data/lipi/src/assets/data/seal_id_and_image_mapping.json`, `data/normalized/lipi_observed_faces.jsonl`, and the CISI 1 and 2 scans for checking. Parse each file name into CISI key, side (A, B, C …), impression marker (`imp`, lowercase captions), extra photograph (`bis`, `ter`) and scale suffix, following the conventions in `knowledge/provenance/catalogue-caveats.md`. Hash every file and group byte-identical files. Assign the 297 files named by volume and page to CISI keys by locating them on the scanned plates. The images stay local; the index tracked in Git holds file hashes, parsed fields and the links to faces.

# How to decide

Done when every image file has a parsed record or an explicit parse failure, every face has zero or more linked images with a stated rule for the link, and a coverage table reports faces and objects with any image, with a seal image and with an impression image, by site and object type. Check 50 random links against the plates; any wrong side assignment requires a revised rule before release.

# Prior attempts

The October 2 readiness audit counted the image index and its exact-key matches without linking images to individual faces. The 12 October data inventory repeated the object-level count.

# Outcome

13 October 2026, [image index and units](../../experiments/2026-10-13-image-index-and-units/README.md): every one of the 8,722 crops has a record with hash, parsed name, kind and CISI volume; 3,664 catalogue keys are placed on their plate pages, giving a page for 97% of 8,444 links between faces and images. 23 file names point at the wrong object and are corrected, and 231 of 299 files named by volume and page were assigned by reading their printed caption. Objects with any image rise from 53.4% to 54.6%, and objects with a photograph of the inscribed side from 17.6% (Lipi index files only) to 46.0%; seals from 10.5% to 68.3%. A random sample of 60 links had 60 correct identities and kinds. The sides of faces on 881 objects with several faces remain open: [Q-1031](Q-1031-assign-faces-to-sides.md).
