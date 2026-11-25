# Day 07 Daily Report - Data Visualization and EDA

- **Developer:** Abhay Gour
- **Assignment:** Day 07 - Data Visualization and EDA
- **Date:** 2026-11-25
- **Repository URL:** https://github.com/halcer-abhay-0005/Day_7_Data_Vis._-_EDA.git
- **Latest commit hash:** `1d8406b` (input-validation hardening; later commits only edit this report)
- **Pull Request:** N/A — no pull request created

- **Topics learned:** Matplotlib figure/axes, seaborn count/hist/box/heatmap, univariate/bivariate EDA, missingness, chart integrity.
- **What I can explain without notes:** when to use box plots, why correlation misleads, why missing resolution time is informative, how to describe an outlier simply.
- **Implementation completed:** `src/eda.py` (strict CSV loader with rejected-row ledger, profile, stats, 6 plots), 26 tests, `EDA_REPORT.md` with 7 findings and caveats, README.
- **Tests/experiment results:** 26 passed (`evidence/pytest_output.txt`), including regressions for non-finite values, duplicate/blank IDs, duplicate headers, wrong field counts, invalid-vs-missing values, multi-line text and input-overwrite protection; run log in `evidence/run_output.txt`. Spearman rho priority vs time = 0.958 (n=18).
- **One bug or challenge and its root cause:** the system Python had no matplotlib → ModuleNotFoundError; fixed with a project venv and `requirements.txt`. Also, self-review against earlier code-review failures (Days 3, 4, 6) showed my first loader used `pd.read_csv` and silently accepted `inf`, blank IDs, duplicate headers and extra fields; root cause was trusting pandas' parsing. Replaced with a strict `csv` loader plus tests.
- **One design decision and why:** used the Day 5 dataset (has missing values, 3 categories) rather than the Day 4 one, which is a perfectly repeating synthetic pattern and shows nothing about missingness.
- **Blocker and what I tried:** none blocking; the sample is small (20 rows), so conclusions are limited to exploratory.
- **Tomorrow's plan:** (fill in from Day 8 plan).
