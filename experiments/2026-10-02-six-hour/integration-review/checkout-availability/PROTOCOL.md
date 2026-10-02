# Fresh-checkout navigation review

This manual review inventories local Markdown links in README.md, REPRODUCING.md, CONTRIBUTING.md, and every Markdown document under knowledge/ and papers/. The selected payload is the deduplicated output of `git ls-files --cached --others --exclude-standard -z`, captured at execution. It describes the intended file selection at that moment.

An exact selected file target is available in a checkout. A directory target is available when the selection contains at least one descendant file. A target that exists in the local project but has no selected file or descendant is local-only. A target absent from both the selection and the local project is missing. Targets outside the repository receive their own category. Local fragments and network links are counted separately. Links inside fenced code examples are excluded. Inline links, image links and explicit reference definitions are inspected; bare paths in prose and code are outside this navigation count.

The review retains link occurrences, unique targets, document hashes and the selected-file list. It links each local-only core target to selected source, acquisition, transformation or reconstruction records. Source witnesses and detailed corpus derivatives keep their present rights exclusions. A reconstructable authored result receives its package route and retains its local-only raw-file status.

The helper also streams the eight authored latent-result chunks through known credential patterns. It reports only pattern counts and chunk paths, with an overlap window across chunk boundaries. Pattern absence covers that declared check only. The original reconstruction hash is already verified by the latent-form branch.

All outputs go to a new dated endpoint under this folder, with the executed helper snapshot. Other contributors may continue editing their documents; the captured hashes identify the reviewed versions. Any later navigation change requires another endpoint.
