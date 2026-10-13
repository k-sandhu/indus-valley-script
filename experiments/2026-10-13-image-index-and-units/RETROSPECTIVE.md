# Retrospective: image index and dimension units, 13 October 2026

**Approach.** The protocol was written and hashed after a profile of file-name shapes and dimension strings and a reading of the CISI 1 conventions, and before any join or count. The image index was built from file names, the dimension audit from the stored strings, and both were then checked against an independent witness: the printed captions inside the crops for the images, and the millimetre field and the older website export for the sizes.

**Problems and fixes.**

The volume/page files carry no key in their names. Viewing them on contact sheets showed that almost every crop still holds its printed caption, so 231 of the 299 were assigned by reading the caption, and enlarged strips or full-resolution views settled the cut or several-object crops.

The same observation turned a planned 50-link sample into a check of every file: tesseract read the caption of each crop and the index compared it with the name. Most of the 182 disagreements were OCR digit errors, but 23 names point at the wrong object, a kind of error a random sample of 60 would probably have missed. A first count of 25 had included two names whose object is right (a prefix typo and a crop that also shows a second object); the amendment and report give the corrected count. The corrections are a table of visual readings, kept apart from the parser (Amendment 1).

Page placement first put L-1 and L-2 on a basic-data page, whose rows look like captions. Restricting placement to plate pages, bounded by the pages whose headings carry the word DATA, fixed it; the PDF-to-printed offsets of 36 and 35 then matched the plate-check package's locators.

The ordinal side rule for objects with several faces failed its targeted check: on some Harappa tablets the export lists the short text first while side A carries the long one, and some seals carry more faces than photographed sides. The rule was withdrawn rather than patched, the sides of those objects are left open, and the faces settled by viewing are recorded in a table (Amendment 2). The run built under the old rule is kept because the samples were drawn from it.

For the sizes, the inventory's assumption that `h`, `v` and `th` hold inches did not survive the first profile: they hold the value as recorded, in inches, millimetres or centimetres. Classifying each value by the factor that maps it to the millimetre field explained 222 of the inventory's 228 mismatches. The 206 cross-export disagreements turned out to be mostly thickness ranges that the inventory's rule did not parse. Pairing a single recorded value with a millimetre range needed one revision: the recorded value matches the lower end of the range about as often as the upper.

Two editing passes failed silently when a Python heredoc's assertion stopped before the file was written; the edits were reapplied with the editor and the output checked.

**Outcome.** A face-level index with 8,444 links, every file parsed or explained, pages for 97% of links, identity precision 60 of 60 in a random sample and 95 of 95 over all samples, and a dimension table with unit, precision, provenance and flags for 17,040 values. Object coverage of any image barely moves (53.4% to 54.6%), while the share of objects with a photograph of the inscribed side rises from 17.6% to 46.0% because the unindexed files are mostly photographs of the seals themselves. What remains is the side of each face on 881 objects with several faces, a viewing task.
