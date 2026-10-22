# Reproduction of F-0027: long seal texts do not repeat

Verification tier proposed for [F-0027](../../../knowledge/findings/F-0027-long-seal-texts-do-not-repeat.md): `reproduced`. 15 October 2026. Contributor: Claude Code (Claude Opus 5.5) in the Claude desktop app, not an author of the finding, working as a newcomer for the [route test](../REPORT.md).

## Result

The finding reproduces exactly. Rebuilding the population from the protocol's text and recounting gives 445 eligible seals with six or more signs and no pair among them with the same complete text, the numbers on the card. Every length from 2 to 13 matches the frozen endpoint in both the number of seals and the number of identical pairs, and the 27 identical pairs among texts of four or more signs also match ([recount.json](run-2026-10-15/recount.json)).

An exploratory check, chosen after the match, widens the population to every complete seal face without an unknown sign, including texts written on several lines and second faces. One text of six or more signs then appears on two objects: the square seals C-53 and C-58 from Chanhu-daro, seven signs each on two lines, with separate excavation numbers (CH 3051 and CH 3168) and separate plate references in the excavator's report ([sensitivity.json](run-2026-10-15/sensitivity.json)). The finding's scope sentence already limits it to single-line seals, so the card is accurate. The pair has not been checked against photographs, because the image index has no crop for either seal.

## What was reproduced and how

The claim is the field `/S3_whole_text_reuse/by_length` of [summary.json](../../2026-10-12-seal-text-identity/run-2026-10-12/summary.json) (SHA-256 `4d851087…`, last changed in commit `feacf405`). The population rule is in the package's [PROTOCOL.md](../../2026-10-12-seal-text-identity/PROTOCOL.md), "Population": seal faces of `data/normalized/lipi_observed_faces.jsonl` that are complete, single-line, without unknown signs and at least two signs long, at a named South Asian site, one face per object family (lowest record id), with text identity as the exact reading-order sequence.

[recount.py](recount.py) implements that rule without importing the package's code and writes into a new directory. The package's [analysis.py](../../2026-10-12-seal-text-identity/analysis.py) was not run: it writes to `run-2026-10-12/` under a fixed path (lines 251–252) and would overwrite the frozen endpoint. Its population function had been read while finding that path, so the recount is a re-implementation, not a blind one. Two places where the protocol text leaves a choice were settled independently and both turned out not to matter. The protocol does not list the sites outside South Asia; the recount excludes the export's Persian Gulf, Mesopotamia and Central Asia regions and the Iranian sites Susa and Luristan, and keeps the Balochistan sites the export files under "Iranian Plateau". The analysis code also drops texts containing code `000`, which the protocol does not mention; the recount was run with and without that rule and the counts are identical.

```text
python experiments/2026-10-15-route-test/reproduce-f0027/recount.py --faces <local lipi_observed_faces.jsonl> --out experiments/2026-10-15-route-test/reproduce-f0027/run-2026-10-15
python experiments/2026-10-15-route-test/reproduce-f0027/sensitivity.py --faces <local lipi_observed_faces.jsonl> --out experiments/2026-10-15-route-test/reproduce-f0027/run-2026-10-15/sensitivity.json
```

Input: `lipi_observed_faces.jsonl`, SHA-256 `1220f559…`, equal to the hash DATA.md records for the 12 October inventory; read from the maintainer's local checkout because this worktree has no `data/`. Code: `recount.py` SHA-256 `4da930dc…`, `sensitivity.py` `5696d0b3…`. Python 3.13.5, standard library only. No frozen file was written.

## Boldest reading and the test that decides it

Long seal legends are unique to one seal: a text of six or more signs was cut once, which fits a personal or household name and not a title shared by many office-holders. The one exception found, C-53 and C-58, comes from a single site, which is what a name predicts. The deciding test is prospective: among seals published after the catalogues (Q-1026) or in CISI 3.1 and 3.2 (Q-1008, Q-1009), a long single-line legend that duplicates a held one at another site would refute the reading. A photograph check of C-53 and C-58 against Mackay's 1943 plates would settle whether they are one design cut twice or a misread pair.
