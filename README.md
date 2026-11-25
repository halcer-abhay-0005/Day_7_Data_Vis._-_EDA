# Day 07 – Data Visualization & EDA (ticket dataset)

Exploratory analysis of the support-ticket CSV: data profile, 6 charts, findings with caveats.

## Structure
```
data/sample_tickets.csv   input (copy of Day 5 data, 20 rows)
src/eda.py                analysis script (profile, stats, plots)
tests/test_eda.py         pytest tests
outputs/                  profile.txt, stats.json, plots/*.png (generated)
evidence/                 saved run + pytest output
EDA_REPORT.md             findings and caveats
DAILY_REPORT.md           daily report
```

## Setup and reproduce
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/eda.py              # regenerates outputs/
.venv/bin/python src/eda.py --data other.csv --out outputs_other   # optional
.venv/bin/python -m pytest -q            # 8 tests
```
Required CSV columns: ticket_id, priority, category, resolution_time_hours, created_at, status.

## Assumptions
- Blank `resolution_time_hours` means the ticket is unresolved (true for both in this data).
- Priority is ordinal: Critical > High > Medium > Low.

## Limitations
Only 20 rows over 10 days; group sizes 4–8; results are exploratory, not causal. See `EDA_REPORT.md`.
