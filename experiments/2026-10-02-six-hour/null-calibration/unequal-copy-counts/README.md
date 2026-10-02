# Sampling blocks with unequal numbers of records

When each artifact supplies the same number of identical copies, object-column shuffling also preserves expanded record counts. Unequal multiplicities require a different sampler. This finite experiment counts that conditional space and supplies a sampler that preserves both object and expanded counts.

Six labeled artifacts have multiplicities `[1,1,1,2,2,3]`. Each binary column has three ones across objects and five across the ten records. There are twenty columns with the object count alone, ten with the record count alone, and six with both counts. Independent categorical object signs are uniform on the six-column space after both counts are fixed. For three independent slots, the full space contains 216 tables.

Unrestricted object shuffling changes the expanded count in fourteen of its twenty distinct columns. For example, `(0,0,1,1,1,0)` expands to five ones, while its permutation `(0,0,0,1,1,1)` expands to seven. Rejection by the weighted count and direct continuation sampling both retain the required record margin.

An integer dynamic program counts the number of legal assignments below each prefix. It chooses the next sign in proportion to the numbers of legal completions. Every complete column has exact probability 1/6, verified by multiplying its rational branch probabilities. Three independent column draws therefore give each table probability 1/216. The independent audit constructs the prefix counts by enumeration and replays all 100,000 saved direct draws.

| Sampler | Tables sampled | Column proposals | Pearson diagnostic, 215 degrees of freedom |
|---|---:|---:|---:|
| Integer continuation counts | 100,000 | 300,000 direct columns | χ²=263.5194; p=.01336 |
| Object-column permutation with weighted-count rejection | 100,000 | 999,391 | χ²=228.7693; p=.24751 |

Every draw preserved both margins. The rejection acceptance rate was .300183; its exact value is .3. The direct draw produced a relatively uneven sample count table at its declared seed. That diagnostic is retained alongside the complete probability calculation and independent stream replay. [The results](results.json) contain every table's count and the seeds.

Permutation within equal-multiplicity classes offers another valid conditional reference. It fixes additional class-specific sign counts and leaves three compatible columns, or 27 three-slot tables. It excludes 189 of the 216 tables permitted by the broader pair of count constraints. That choice changes the conditional question and the available movements.

Fixing only the expanded record count leaves latent object counts of two, three or four among the ten compatible columns. At the known sign probability .2, their total conditional probabilities are respectively 16/29, 12/29 and 1/29. The six columns with three latent ones occupy 12/29 of this record-count-only law. Conditioning also on the latent count removes the unknown categorical probability from their relative weights. This is the additional sufficient-count constraint needed before using a uniform reference over that six-column space.

The example prepares a method for an established literal-copy process with unequal record counts. Applying it to an archaeological population would require the copying relation and eligible metadata cells to be specified from the corpus. The current nested study keeps its declared two-copy design. [Protocol](PROTOCOL.md), [reusable code](run.py), [independent verification](verification.json).
