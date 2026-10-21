# Integration retrospective

The shared checkout contained two unrelated local commits, active source-ledger changes and unfinished studies. We used an isolated branch from remote main and copied only the completed contributions after checking their recorded hashes. A full checkout was slow, so we stopped that checkout and materialized unchanged base files from the local copy. Mutable shared files were copied separately; base differences were restored from Git. A differing calibration fixture was restored only in the disposable checkout.

The base registry pointed to an ignored project-generated check log that was absent from Git. We copied its existing original bytes into the branch and explicitly staged that one log. We did not regenerate an old result. The integrated data manifest now lists 104 sources, and DATA.md uses the corresponding status counts. Overlapping source subsets are kept separate from the physical-object census.

The default Git whitespace check interpreted Windows carriage returns as trailing whitespace because the repository preserves raw bytes. The `cr-at-eol` setting passed without changing frozen files. A copied Markdown card snapshot had four relative links whose origins moved with the file. We retained its original text and hash inside JSON, where its original path is explicit. The second public-checkout check has zero study errors and retains 58 existing repository-wide issues.

The merged contribution states the standard four-unit Fish record as a post-outcome conjecture. The decisive next evidence remains an individually registered physical correspondence that distinguishes contents, account and recipient roles; a new different numeral in the exact construction defeats the fixed-four prediction.
