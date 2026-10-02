# An exact false-rejection example for copied records

Three identical records per latent object raise the exact rejection probability of an ordinary record-column test to 25% at its 5% threshold in this example. The matched object-column test rejects 2.78%. Both calculations use the same observed tables and the same integer adjacency statistic.

The generating law has four labeled objects with three independent binary signs. Each object-column contains two zeros and two ones, giving 216 equally probable latent tables. Each object is then copied c times. The statistic counts equal neighboring signs over the expanded rows. Ordinary record-column shuffling preserves the expanded sign totals; object-column shuffling also preserves which records are identical copies.

| Copies per object | Records | Record reference at 1% | Record reference at 5% | Record reference at 10% |
|---:|---:|---:|---:|---:|
| 1 | 4 | 0% | 2.78% | 2.78% |
| 2 | 8 | 2.78% | 2.78% | 25% |
| 3 | 12 | 2.78% | 25% | 25% |
| 4 | 16 | 25% | 25% | 25% |
| 5 | 20 | 25% | 25% | 25% |

The matched block reference has rejection probabilities 0%, 2.78% and 2.78% at those thresholds for every copy count. Its tied-tail calculation is conservative because the smallest exact tail occupies six of the 216 tables, or 1/36. Expanding every object multiplies the statistic by the same c, which preserves ranks within the matched space.

The ordinary reference breaks the fixed copy relations and gives the repeated rows more independent movement. Its reference tails consequently shrink as the number of copies grows, although the latent generating law stays the same. At c=3, 54 of the 216 latent tables have a score of at least 18. Their ordinary-reference tail is 18,819/853,776, about .02204, so all 54 reject at .05. Their matched tail is 54/216=.25.

Every probability is an exact fraction. The program enumerates all 216 latent tables and all ordinary tables for one and two copies. It counts the larger ordinary spaces using binomial coefficients and an integer convolution. An independent row-state dynamic program verifies the full ordinary score distribution for every copy count, then rechecks every tail and rejection endpoint. [Results](results.json), [verification](verification.json), [protocol](PROTOCOL.md), [code](run.py).

This example isolates conditional table laws using a simple adjacency count. The main calibration study separately measures the preserved nested fitting statistic on forty-record populations. The copying process is specified here as the known synthetic law; archaeological use requires evidence for the proposed copy blocks.
