# Lexical query repair

The first local extraction concatenated ORACC guidewords and senses before applying exact-word patterns. An entry headed `fish` therefore failed a `^fish$` query because the concatenated field also contained its sense. German stem alternatives also matched substrings of English words: `Tor` matched `administrator`, and `Rind` matched `grind`.

The second extraction searches the English ORACC fields separately with word boundaries and keeps the Egyptian German queries in their own population. Egyptian matches remain a broad retrieval pool requiring individual sense review. The original code, local extraction and source manifests remain preserved. No first-extraction category count is used as a semantic result. The repaired endpoint is `lexical-observations-v2` with `corpus-observation-manifest-v2.json`.
