# Record form for the head-direction seal-legend corpora

Written 21 October 2026 (UTC) before any corpus was normalised. Every legend from every comparison corpus is stored in this form, one JSON object per line, UTF-8 in Unicode NFC. The form extends the record of the held Ur III seal legends (`data/raw/2026-10-12-bronze-age-comparison/normalized-v4/records.jsonl`, fields `corpus`, `document`, `aliases`, `source`, `source_url`, `date`, `genre`, `site`, `id`, `kind`, `encoding`, `units`, `words`, `gold`, `word_units`, `source_word_refs`) with explicit object identity, line divisions, tags and provenance. In the held records `genre` is the ORACC genre of the tablet, so the new form calls the ORACC value `text_genre` and reserves `genre` for seal or sealing. Normalised records are local-only; tracked files hold counts, identifiers and hashes.

## Identity and provenance

| Field | Required | Content |
|---|---|---|
| `record_id` | yes | `<corpus>:<source>:<entry>`, unique across all corpora |
| `corpus` | yes | `ia-ganges` (Indo-Aryan seals and sealings from Basarh and Bhita), `ta-brahmi` (Tamil-Brahmi seals, rings and coins), `sux-ur3` (Ur III seal legends in Sumerian), `akk-sargonic` (Old Akkadian period legends in Akkadian), `sux-sargonic` (Old Akkadian period legends in Sumerian) |
| `source` | yes | Source id from the acquisition manifest, for example `asi-ar-1903-04` |
| `source_locator` | yes | Object with whichever apply: `page_printed`, `page_pdf`, `entry`, `plate`, `figure`, `table`, `oracc_text`, `cdli_artifact` |
| `object_id` | yes | The physical object that carries this witness: the editor's number of a seal die, ring or coin; the number of a clay sealing; or the P-number of a sealed tablet, envelope or bulla |
| `object_kind` | yes | `seal-die`, `cylinder-seal`, `stamp-seal`, `ring`, `coin`, `clay-sealing`, `sealed-tablet`, `sealed-envelope`, `bulla`, `other` |
| `genre` | yes | `seal` for a matrix (die, cylinder, stamp, signet ring), `sealing` for an impression, `coin` for a coin legend |
| `die_id` | when known | The seal die whose legend this is, where the edition establishes it: Bloch's variety number, Spooner's type number, a CDLI composite seal number (S-number), a Bhita entry number |
| `impressions` | when given | Number of impressions of this die that the source reports for this entry |
| `aliases` | yes (may be empty) | Other identifiers: other catalogue numbers, duplicate register numbers, museum numbers, Siddham, CDLI or ORACC identifiers |
| `site` | yes, or null with a ledger entry | Normalised site name (`Basarh`, `Bhita`, `Karur`, `Umma`, `Girsu`, …) |
| `site_as_printed`, `findspot`, `depth_as_printed`, `stratum_or_level` | when given | As printed: trench, square, house, room; depth with its reference (below surface, above floor) |
| `date_as_printed`, `period` | when given | The editor's date (usually palaeographic) and a normalised period label (`Mauryan`, `Sunga`, `Kushana`, `Gupta`, `post-Gupta`, `Ur III`, `Old Akkadian`) |
| `material`, `dimensions_as_printed`, `device`, `museum` | when given | As printed; `device` is the emblem in at most fifteen words |
| `language`, `language_basis` | yes | `Sanskrit`, `Prakrit`, `mixed Sanskrit-Prakrit`, `Pali`, `Tamil`, `Sumerian`, `Akkadian`, `mixed`; basis `editor`, `token-language`, `catalogue` |
| `script` | yes | `Brahmi (early)`, `Brahmi (Kushana)`, `Brahmi (Gupta)`, `Brahmi (later)`, `Tamil-Brahmi`, `cuneiform` |
| `rights` | yes | Rights status of the source, from the acquisition manifest |

## Legend

| Field | Required | Content |
|---|---|---|
| `legend_as_printed` | yes | The editor's transliteration exactly as printed, diacritics and brackets included |
| `lines` | yes | Lines in reading order, each a list of the editor's orthographic words |
| `line_division_basis` | yes | `edition` (the edition marks the line breaks), `atf` (ATF line numbers), `none` (the edition prints the legend as one run, so `lines` holds one line and says nothing about the seal) |
| `words` | yes | The editor's orthographic words in reading order, after the transliteration normalisation below |
| `members` | yes | For each word, its lexical members where the edition marks compound members with hyphens; otherwise the word alone |
| `units` | yes | Sign units in reading order (rules below) |
| `word_units` | yes | For each word, its sign units; their concatenation equals `units` |
| `line_of_word` | yes | For each word, the index of its line |
| `tags`, `tag_source` | yes | For each member, one tag and its basis (below) |
| `gloss` | when given | For each member, the editor's gloss: ORACC guide word, or the corresponding word of the editor's translation |
| `translation_as_printed` | when given | The editor's translation of the whole legend |
| `gold` | cuneiform | ORACC part-of-speech code per word, as in the held records |
| `completeness` | yes | `complete`, `restored` (whole legend given, part restored by the editor from duplicates or in brackets), `damaged-edge` (first or last unit lost or unread), `damaged-internal`, `illegible`, `no-legend` |
| `reading_doubtful` | yes | True when the editor marks the reading as doubtful |
| `transcription` | yes | `method` (`page-image`, `ocr-checked-against-image`, `digital-edition`) and `by` (agent and model) |

## Transliteration normalisation

Indo-Aryan legends are converted from the editors' transliteration to IAST before units are formed, because Bloch (1903–04), Marshall (1911–12) and Spooner (1913–14) use the older Survey convention: `chh` → `ch`, then `ch` → `c`, `sh` → `ṣ`, `ṛi` → `ṛ`, `ṁ` → `ṃ`. Capitals are lowered. The editors' restorations in round or square brackets are kept as letters and recorded in `completeness`; a question mark is removed and recorded in `reading_doubtful`. Tamil-Brahmi legends keep Mahadevan's transliteration (`ṉ`, `ḻ`, `ṟ`, `ḷ`, `ṇ`). Cuneiform keeps ATF.

## Sign units

A Brahmi sign unit is one akṣara, the orthographic syllable the script writes as one sign or ligature. It is an optional consonant cluster followed by one vowel, with any following anusvāra (`ṃ`), visarga (`ḥ`) or candrabindu. A vowel with no consonant before it is its own unit. A consonant with no vowel after it inside its word, which in the script carries a virāma or, in Tamil-Brahmi, a dot (puḷḷi) or the bare consonant sign, is its own unit written with a trailing `·`. Units are formed over each orthographic word with its hyphens removed, so compound members joined by sandhi form ligatures as the script writes them; a space always ends a unit. Cuneiform units are the sign readings of the ATF transliteration, with determinatives as their own units (`{d}` → `d`, `{ki}` → `ki`) and numbers as `NUM:<reading>`, the convention of the held records.

## Word units and tags

The reference word unit is the editor's orthographic word: a space-delimited word in the Brahmi editions, a space-delimited ATF word in cuneiform. A Sanskrit compound printed as one word is one word. Tags are assigned to lexical members:

| Tag | Members |
|---|---|
| `NAME` | Personal names, including theophoric names |
| `DIVINE` | Names of deities |
| `PLACE` | Names of places, districts and peoples |
| `TITLE` | Offices, ranks, occupations, royal epithets and honorifics (`mahārāja`, `śrī`, `kumārāmātya`, `śreṣṭhi`, `kulika`, `lugal`, `ensi₂`, `dub-sar`, `šar`, `kō`) |
| `KIN` | Kinship and dependency relations (`putra`, `dumu`, `arad₂`, `ARAD₂`, `dam`, `makaṉ`) |
| `NUMBER` | Numerals |
| `GRAM` | Prepositions, particles, pronouns, conjunctions |
| `OTHER` | Everything else, including office and institution nouns (`adhikaraṇa`, `nigama`), religious formulae and verbs |

`tag_source` is `editor-pos` when an ORACC part-of-speech code decides the tag (PN → `NAME`, DN → `DIVINE`, GN, SN, TN, WN → `PLACE`, RN → `NAME`, NU → `NUMBER`), `editor-translation` when the editor's translation decides it, and `lexicon` when a rule from the tracked lexicon file decides it. Every lexicon entry is a general vocabulary item with its tag, and the lexicon file is tracked.
