# D1 retrospective

Work began under the October 6 package date and continued into October 7 UTC/local midnight. All authored files and generated aggregates stayed in the owned experiment directory. Downloaded witnesses, extraction, memberships and predictions stayed in the local raw directory. Shared indexes, registry, manuscripts, other contributors' files and Git history were left untouched.

## Reused evidence and methods

Read AGENTS.md, the root README and knowledge index, writing and redistribution rules, relevant registry entries, corpus/methods/literature retrospectives, Paper 002's methods/manuscript, the October 6 contribution assessment and the earlier context audit. ROOT-02, ROOT-05, METHODS-nested_unique_preserved_aliases and CONTEXT-01 identified the alias, copied-text and short-record issues. The analysis reused the pinned 5,680-face input and imported `group_records`/`make_folds` from `src/methods/conditional_structure.py`. Physical reference and source-placeholder conventions were taken from the existing metadata and alias-safe transfer code. Earlier experiment endpoints were not rerun.

## Sources and chronology

Live searches recovered the HARP chronology, Yadav's direct site/type precedent, Suga's direct 2024 diachronic study, Oakes's positional study and Rao's earlier external-text likelihood experiment. Suga's issue date is 2024, while the repository became available in 2025. Oakes's online 2017 and issue 2019 dates describe one paper. The opened university record corrected an initial draft's Jamison coauthors/year to Gregg Jamison, Akinori Uesugi and Yuji Yamaguchi, December 2023, volume 36. The author PDF and bibliographic search corrected a guessed Rao DOI to 10.1073/pnas.0906237106 and established eight West Asian rows in Table 2.

Six PDFs and two useful HTML pages downloaded successfully. Wiley and ResearchGate PDF requests returned HTTP 403. Wiley's abstract and the 35-page Fuls excerpt were readable through the web tool. Several publisher/PMC opens failed or showed a browser challenge; the author PDFs supplied the usable witnesses. No challenge was bypassed. All failures are recorded in `sources.json` and the local acquisition manifest. Two extraction-inspection commands initially failed to print Japanese/non-ASCII characters through the Windows console; explicitly setting UTF-8 output resolved the inspection. Downloaded files were unaffected.

The catalogue-join checker later caught a title dash replaced by a question mark in a piped Python command. The authored title was corrected and the equality check repeated; both zero-match counts were unchanged. `check_catalogue_join.py` preserves that check for the reviewer.

The initial metadata inventory showed 3,067 time-labelled faces but only 1,939 at Harappa. The mapping was therefore restricted to Harappa. The single 3A face prevented an early mature-period test. Broad Period 3 and 3B/C labels were preserved as intervals. The numeric 1300 cutoff in the frozen Period 5 JSON mapping is not a closed youngest date; `mapping-notes.json` retains the published <1300 BCE end expression. No numerical calendar dates entered the computations.

## Dependence, support and computation

Full physical/text closure produced a 1,038-face component. Predictive folds retained it, limiting usable training support for copied short-text classes. Families and transitive text components were kept together in splits. Label permutations used homogeneous complete units within exact-type/face-count blocks, with margins asserted on every draw. The main run completed in 375.22 seconds.

The family and text-closure references gave different inferential outcomes. Harappa 3B–3C had Holm .044 with physical families and .068 under text closure. Four of six regional family-reference tests passed Holm .05; only Lower Indus–Eastern Headwaters also passed under text closure. None of 338 individual sign tests passed BH .05. These differences were reported with each reference's selected population rather than selecting the favorable result.

The primary site-stratified bootstrap lost rare site/type cells. Three site-balanced frequency intervals retained only 1–3 of 499 replicates. Sparse divergence bootstrap distributions also shifted above observed effects. An explicitly post-outcome amendment introduced site/type/recording-quality component signatures and saved both percentile and basic centered intervals. The supplemental point estimates were unchanged, and all supported intervals retained 499 draws. The manuscript reports their conditional scope and uncalibrated coverage. The original endpoint and its failed intervals were preserved.

The fold allocator balanced proxy lengths after invalid texts were given unique markers. The original `fold_token_loads` field was recognized as a proxy during verification. Supplemental actual fold tables reconcile all 19,946 slots and 2,930 eligible faces. The original grouping/exclusion checks passed.

## External matching and limits

The external region-field set contains 42 faces, but only 16 meet the ordered-text filters. Nine lack the declared length/type support, leaving seven matched objects. All circular seals are excluded from that endpoint. The seven-object adjusted surprisal interval includes zero. Supplemental unpaired scores document unsupported types without supplying a new matched claim. Parpola and Frenez passages support site/type leads, while individual rows, source codes and non-canonical classifications remain unverified. The Baluchistan/Makran entries in the Iranian Plateau category prevent treating the entire external field set as a West Asian linguistic population.

## Checks and remaining work

Independent code rebuilt three count tables, recomputed 23 divergence effects and replayed 104 regional plus 14 external prediction calculations. It checked match cells, fold/alias exclusions and ten source hashes. The main run asserted 7,485 permutation margins. The supplement checker validated unchanged point estimates, complete support, actual fold counts and 41 sampled type-presence rows.

The reviewer should rerun the random schedules in fresh directories, calibrate divergence intervals in appropriate sparse/copying simulations, and sample original excavation plates. Additional secure 3A records, narrower HARP context assignments, matched circular-seal texts and production-batch links would improve the analysis. Full Laursen/Fuls/Frenez texts and a lecture timestamp were not recovered. The complete file inventory is `FILES_CREATED.json`; reproduction commands are in README.md.
