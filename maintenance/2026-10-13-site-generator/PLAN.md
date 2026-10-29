# Public website generator

Date: 13 October 2026. Contributor: Codex, GPT-6.1-Sol instructions, API harness. Status: tooling implementation and local verification.

The generator will present repository documents and card fields through local HTML templates. Git supplies the eligible file inventory and file contents. A committed build uses HEAD; a preview uses tracked and untracked non-ignored files. The sole exception to the data-directory exclusion is the requested metadata table from `data/MANIFEST.json`, read only when tracked, never copied.

I own `tools/build_site.py`, `site/`, this experiment directory except the supplied prompt and launcher, and one added `/_site/` line in `.gitignore`. Existing contributor changes and research evidence stay in their owners' files. Generated HTML is a local build product or a gh-pages tree.

The implementation will import the parser and item index from `tools/kb.py`, supply them with a Git-backed inventory, render the requested document routes, and rewrite repository links against that inventory. Missing or excluded targets become labelled text. Explore assets retain their relative directory structure and source attribution.

Verification will cover repeated preview builds, internal links and assets, pinned GitHub links, exclusions, external resource loads, accessibility markup and badge contrast. Publish verification will use Git plumbing in a temporary clone, compare its source branch, index and working tree before and after, and verify a second publication's parent. No publication command will run in the real repository.

The record will preserve failed checks, repairs, final command outputs, page sizes, build hashes and a retrospective. The coordinator will review the committed-source build and source eligibility before publishing.
