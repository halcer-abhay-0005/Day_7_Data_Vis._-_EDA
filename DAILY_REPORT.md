# Day 07 Daily Report
- **Topics learned:** Matplotlib figure/axes, seaborn count/hist/box/heatmap, univariate/bivariate EDA, missingness, chart integrity.
- **What I can explain without notes:** when to use box plots, why correlation misleads, why missing resolution time is informative, how to describe an outlier simply.
- **Implementation completed:** `src/eda.py` (profile, stats, 6 plots), tests, `EDA_REPORT.md` with 7 findings and caveats, README.
- **Tests/experiment results:** 8 passed (`evidence/pytest_output.txt`); run log in `evidence/run_output.txt`. Spearman rho priority vs time = 0.958 (n=18).
- **One bug or challenge and its root cause:** the system Python had no matplotlib → ModuleNotFoundError; fixed with a project venv and `requirements.txt`. Also a seaborn/matplotlib 3.11 deprecation warning (`vert`) comes from seaborn internals, harmless.
- **One design decision and why:** used the Day 5 dataset (has missing values, 3 categories) rather than the Day 4 one, which is a perfectly repeating synthetic pattern and shows nothing about missingness.
- **Blocker and what I tried:** none blocking; the sample is small (20 rows), so conclusions are limited to exploratory.
- **Tomorrow's plan:** (fill in from Day 8 plan).
