# Retrospective: work delegated to Codex

Seven Codex runs did the mechanical work of this package. All used the Codex CLI (`codex exec`) with model `gpt-6.1-sol`, reasoning effort `xhigh`, the `workspace-write` sandbox with network access enabled (`-c sandbox_workspace_write.network_access=true`), and, for the dating run, live web search. Each was launched detached from PowerShell through Git Bash with a launcher in this package, and its prompt hash, start and end times are in `data/raw/2026-10-21-town-orientations-verification/codex/<run>/launches.txt`, with the full log beside it. The coordinating Claude session wrote every prompt, reviewed every output before using it, and kept the design, date judgements, combination, comparison and prose. A short smoke test before the first launch confirmed that the sandbox could reach the open-data hosts.

| Run | Prompt | Time (UTC) | What it delivered |
|---|---|---|---|
| infra | [CODEX-PROMPT-INFRA.md](CODEX-PROMPT-INFRA.md) | 03:34–04:55 | Site coordinates for 33 towns, the measurement tools and their guide, IGRF-14 with three checks, imagery for 11 towns; stopped by the full disk |
| astro | [CODEX-PROMPT-ASTRO.md](CODEX-PROMPT-ASTRO.md) | 03:34–04:19 | Independent astronomy and horizons, all validation gates passed, provisional prediction tables, scoring and comparison scripts with selftests |
| dating | [CODEX-PROMPT-DATING.md](CODEX-PROMPT-DATING.md) | 03:34–05:34 | Phase sequences, layout phases and candidate dates for 33 towns and 53 parts, 238 radiocarbon determinations, bibliography |
| infra-2 | [CODEX-PROMPT-INFRA-2.md](CODEX-PROMPT-INFRA-2.md) | 04:57–06:56 | Truncation check, lossless recompression, imagery for all 33 towns, plan library (26 plans, 18 towns), selftest pass, runway validation |
| measure-A-S, -G, -H | [CODEX-PROMPT-MEASURE-A-S.md](CODEX-PROMPT-MEASURE-A-S.md), [-G](CODEX-PROMPT-MEASURE-A-G.md), [-H](CODEX-PROMPT-MEASURE-A-H.md) | 05:51–06:49, 06:29, 06:39 | Measurer A: 33 town files, 119 lines, one imagery system (Lothal), plan systems for 16 towns |

## How it went

The astronomy run was the most valuable delegation. It implemented the long-term precession from the published coefficients, rigorous space motion, horizons to 250 km, refraction and extinction, and it passed every gate: ERFA test vectors to 10⁻¹⁶, pyerfa within 10⁻¹⁴°, astropy within 0.004°. Its code then reproduced the other package's 83 predicted deviations within 0.026°, and its scorer reproduced that package's statistics digit for digit. Its final-message file came out empty, but the final message was complete in the log.

The infrastructure runs were careful and slow. The first solved real problems (Windows GDAL could not open HTTPS cloud-optimised GeoTIFFs, so it wrote a verified byte-range opener; Wikidata and Earth Search needed rate limiting and smaller pages; a smoothing step was needed to stop edge fits locking to pixel phases) and stopped cleanly when the disk filled, asking for space rather than filling it further. The resumption prompt set explicit free-space rules, and the second run followed them, verified 557 rasters, recompressed 324 without changing a pixel and finished the validation. The runway validation it designed, with segments of 100 to 400 m, gave the most useful single number of the package: what 10 m imagery can and cannot measure.

The dating run applied the three levels of evidence strictly and recorded every number with a locator. That strictness left several major towns without a date, which we handled with a second, liberal table; its search could not obtain Dholavira's individual radiocarbon table, and the full disk interrupted some downloads.

Measurer A worked quickly, 38 to 58 minutes per share, and recorded clear reasons for every town it could not measure. It found imagery architecture only at Lothal. Its plan readings agree with measurer B's on the same figures to a median of 1.3°.

## Problems and disclosures

The runs disclosed their own departures, and we checked each. Early raw-data diagnostics in the first infrastructure run, and early acquisition in the astronomy run, used the system Python instead of the package environment (still with `-I` in the astronomy run); both reran the production steps correctly. One measurer-A crop of a published Shikarpur figure showed a narrow strip of commercial imagery, which was disclosed and not measured. One measurer-A log was written with 22 Windows-1252 quotation marks inside otherwise UTF-8 text; we kept the original and re-encoded a copy (see the main retrospective). The sandbox's automatic approval review blocked a recursive cache cleanup and one plan download, both without consequence for the results. No run committed, changed a branch, wrote outside its owned paths or opened the other package, as far as their logs and our searches of them show.

The prompts worked best when they stated owned paths, invariants, deliverables, verification and the final message in full, and when they kept the measurers blind by saying exactly which files of the package they may open. The one thing we would change is to give the measurement runs different imagery or a different fitting tool from each other, so that their agreement measures accuracy as well as consistency.
