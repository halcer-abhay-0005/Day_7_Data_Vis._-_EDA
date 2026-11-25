# Ticket Dataset – Exploratory Analysis Report

Data: `data/sample_tickets.csv` (copied from Day 5). Numbers below come from `outputs/stats.json` and `outputs/profile.txt`.

## 1. Data profile (Task A)
| Item | Value |
|---|---|
| Rows / columns | 20 / 6 |
| Missing values | only `resolution_time_hours`: 2 of 20 (10%) |
| Unique | ticket_id 20 (no duplicates), priority 4, category 3, status 2, 10 distinct dates |
| Date range | 2026-11-01 to 2026-11-10 |
| Resolution time (n=18) | mean 7.97 h, median 7.25 h, std 4.73, min 1.5, max 18.0 |
| Priority counts | High 6, Medium 5, Low 5, Critical 4 |
| Category counts | Technical 9, Billing 6, General 5 |
| Status | Resolved 18, Open 2 |

## 2. Charts (Task B) — `outputs/plots/`
1. `01_category_counts.png` – count plot (categorical)
2. `02_priority_counts.png` – count plot (ordinal)
3. `03_resolution_hist.png` – histogram (numeric distribution, median/mean marked)
4. `04_resolution_by_priority_box.png` – box + points (numeric vs ordinal)
5. `05_resolution_by_category_box.png` – box + points (numeric vs nominal)
6. `06_priority_category_heatmap.png` – heatmap of counts (two categoricals)

Every chart has a title, axis labels, the sample size, and a linear axis starting at zero for counts.

## 3. Findings (Task C)
1. **Technical is the largest category** – 9 of 20 tickets (45%) vs Billing 30% and General 25% (chart 1).
2. **Priority mix is roughly even** – 4–6 tickets per level; no priority dominates (chart 2).
3. **Resolution times are spread out, mildly right-skewed** – mean 7.97 h is above median 7.25 h; range 1.5–18 h (chart 3).
4. **Higher-priority tickets were resolved faster.** Median hours: Critical 2.25, High 6.0, Medium 9.0, Low 14.5. Spearman rho = 0.958 (n=18) (chart 4). The ranges of adjacent priorities barely overlap (e.g. Critical max 3.0 < High min 4.5). This is an *association*: the data cannot tell us whether priority causes faster handling (e.g. staff are assigned first to urgent tickets) or whether priority was set based on how quickly an issue was expected to be fixed.
5. **General tickets look slowest** – median 11.0 h vs 6.25 h for Billing and Technical (chart 5, n=4/6/8). Much of this may be priority mix rather than category (General contains Low tickets with 12–15 h times); the data here is too small to separate the two.
6. **Both missing resolution times belong to Open tickets** (1 Low, 1 High). Missingness is therefore informative: it means "not yet resolved", not a data-entry error. Dropping these rows makes the statistics describe *resolved* tickets only and likely understates how long slow tickets take (survivorship/censoring).
7. **No statistical outliers** by the 1.5×IQR rule (fences −5.12 to 20.88 h). The 18.0 h Low-priority ticket is the longest but is consistent with other Low tickets (12–18 h).

## 4. Caveats and limitations
- **Small sample:** n=20 (18 with times); per-group sizes are 4–8. Group medians can shift a lot with one ticket. No confidence intervals were computed; treat results as exploratory.
- **Very clean pattern** (rho 0.96, almost no overlap) suggests the sample is synthetic or sample-sized by hand; real data is usually noisier.
- **Short window:** 10 days, so no weekly/seasonal pattern can be assessed.
- **Censoring:** open tickets have no time; the average excludes the slowest unresolved work.
- **Outlier rule:** with n=18 the IQR fences are wide; absence of outliers is weak evidence.
- Correlation and group differences here are observations only; no causal claim is made.
- A Day 4 dataset (100 rows) exists but follows a perfectly repeating synthetic pattern, so it was not used.

## 5. Viva answers (short)
1. **Box plot:** to compare a numeric distribution across groups; it shows median, spread and outliers, robust to skew.
2. **Misleading correlation:** confounders, reverse causation, small n, outliers, non-linear relations, or coincidence (e.g. priority vs time above).
3. **Missingness as information:** here missing time means the ticket is still open; the reason for missing can be correlated with the outcome.
4. **Explaining an outlier:** "One ticket took far longer than the rest (X hours vs typical Y). We checked it is real, and it is shown separately so it doesn't distort the average."
