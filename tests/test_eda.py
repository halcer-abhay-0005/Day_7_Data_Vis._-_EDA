import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import eda  # noqa: E402

SRC = Path(__file__).resolve().parent.parent / "src"
DATA = Path(__file__).resolve().parent.parent / "data" / "sample_tickets.csv"


@pytest.fixture
def df():
    return eda.load(DATA)


def test_load_shape_and_priority_order(df):
    assert df.shape == (20, 6)
    assert list(df["priority"].cat.categories) == eda.PRIORITY_ORDER


def test_load_rejects_missing_columns(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("ticket_id,priority\nT1,High\n")
    with pytest.raises(ValueError):
        eda.load(p)


def test_missingness_counted(df):
    assert df["resolution_time_hours"].isna().sum() == 2
    assert "missing=2 (10%)" in eda.profile(df)


def test_missing_resolution_are_open_tickets(df):
    assert set(df[df["resolution_time_hours"].isna()]["status"]) == {"Open"}


def test_iqr_outliers_detects_extreme():
    out, _, _ = eda.iqr_outliers(pd.Series([1, 2, 2, 3, 3, 3, 4, 100]))
    assert out.tolist() == [100]


def test_iqr_ignores_nan():
    out, _, _ = eda.iqr_outliers(pd.Series([1.0, 2.0, 3.0, None]))
    assert out.empty


def test_stats_values(df):
    s = eda.compute_stats(df)
    assert s["median_hours"] == 7.25
    assert s["spearman_priority_vs_time"]["rho"] > 0.9


def test_plots_created(df, tmp_path):
    eda.make_plots(df, tmp_path)
    assert len(list(tmp_path.glob("*.png"))) == 6


# ---- Regression tests for defect classes found in the Day 3/4/6 code reviews ----
H = "ticket_id,priority,category,resolution_time_hours,created_at,status\n"


def write(tmp_path, body, name="in.csv"):
    p = tmp_path / name
    p.write_text(body, newline="")
    return p


def reasons(p):
    return eda.load_with_report(p)[1]["reason"].tolist()


@pytest.mark.parametrize("val", ["inf", "-inf", "nan", "1e999"])
def test_non_finite_resolution_rejected(tmp_path, val):  # Day 4 B1
    p = write(tmp_path, H + f"T1,High,IT,{val},2026-11-01,Resolved\nT2,Low,IT,2,2026-11-01,Open\n")
    clean, rej = eda.load_with_report(p)
    assert len(clean) == 1 and len(rej) == 1
    assert rej["reason"].iloc[0].startswith("invalid_resolution_time")
    assert clean["resolution_time_hours"].map(lambda x: x == x and abs(x) != float("inf")).all()


def test_extra_fields_raise(tmp_path):  # Day 4 B2
    p = write(tmp_path, H + "T1,High,IT,3,2026-11-01,Resolved,zz\n")
    with pytest.raises(eda.TicketDataError, match="fields"):
        eda.load(p)


def test_short_row_raises(tmp_path):
    with pytest.raises(eda.TicketDataError, match="fields"):
        eda.load(write(tmp_path, H + "T1,High,IT\n"))


@pytest.mark.parametrize("header", [
    "ticket_id,priority,priority,category,resolution_time_hours,created_at,status",
    "ticket_id,priority, PRIORITY,category,resolution_time_hours,created_at,status",
])
def test_duplicate_headers_raise(tmp_path, header):  # Day 3 / Day 4 B3
    with pytest.raises(eda.TicketDataError, match="Duplicate"):
        eda.load(write(tmp_path, header + "\nT1,High,Low,IT,3,2026-11-01,Resolved\n"))


def test_header_whitespace_case_normalised(tmp_path):
    p = write(tmp_path, " Ticket_ID ,PRIORITY,Category,resolution_time_hours,created_at,status\nT1,high,IT,3,2026-11-01,resolved\n")
    df = eda.load(p)
    assert df["priority"].iloc[0] == "High" and df["status"].iloc[0] == "Resolved"


def test_blank_and_whitespace_ticket_id_rejected(tmp_path):  # Day 6 B1
    p = write(tmp_path, H + ",High,IT,3,2026-11-01,Resolved\n   ,High,IT,3,2026-11-01,Resolved\nT3,High,IT,3,2026-11-01,Resolved\n")
    assert reasons(p) == ["missing_ticket_id", "missing_ticket_id"]


def test_duplicate_ticket_id_rejected(tmp_path):
    p = write(tmp_path, H + "T1,High,IT,3,2026-11-01,Resolved\nT1,Low,IT,4,2026-11-01,Resolved\n")
    assert reasons(p) == ["duplicate_ticket_id"]


def test_invalid_text_distinct_from_missing(tmp_path):  # Day 6 B2
    p = write(tmp_path, H + "T1,High,IT,abc,2026-11-01,Resolved\nT2,High,IT,,2026-11-01,Open\nT3,High,IT,2,2026-11-01,Resolved\n")
    clean, rej = eda.load_with_report(p)
    assert rej["reason"].tolist() == ["invalid_resolution_time_non_numeric"]
    assert clean["resolution_time_hours"].isna().sum() == 1  # blank kept as genuinely missing


def test_negative_priority_date_category_rejected(tmp_path):
    p = write(tmp_path, H + "T1,High,IT,-1,2026-11-01,Resolved\nT2,Urgent,IT,1,2026-11-01,Resolved\n"
              "T3,High,,1,2026-11-01,Resolved\nT4,High,IT,1,not-a-date,Resolved\nT5,High,IT,1,2026-11-01,Resolved\n")
    assert reasons(p) == ["invalid_resolution_time_negative", "invalid_priority", "missing_category", "invalid_created_at"]


def test_multiline_quoted_text_preserved(tmp_path):  # Day 6 B4
    p = write(tmp_path, H + 'T1,High,"IT, ops\nsecond line",3,2026-11-01,Resolved\n')
    assert eda.load(p)["category"].iloc[0] == "IT, ops\nsecond line"


def test_empty_header_only_missing_cols_and_missing_file(tmp_path):
    for body, msg in [("", "empty"), (H, "no data rows"), ("a,b\n1,2\n", "Missing required")]:
        with pytest.raises(eda.TicketDataError, match=msg):
            eda.load(write(tmp_path, body))
    with pytest.raises(eda.TicketDataError, match="not found"):
        eda.load(tmp_path / "nope.csv")


def test_malformed_quote_raises(tmp_path):
    with pytest.raises(eda.TicketDataError):
        eda.load(write(tmp_path, H + 'T1,High,"IT"x,3,2026-11-01,Resolved\n'))


def test_cli_refuses_to_overwrite_input(tmp_path):  # Day 6 B3
    out = tmp_path / "o"
    out.mkdir()
    victim = out / "profile.txt"
    victim.write_text(H + "T1,High,IT,3,2026-11-01,Resolved\n")
    before = victim.read_text()
    r = subprocess.run([sys.executable, str(SRC / "eda.py"), "--data", str(victim), "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "overwrite" in r.stderr
    assert victim.read_text() == before


def test_cli_end_to_end_writes_rejected_ledger(tmp_path):
    rows = "".join(f"T{i},{p},IT,{i + 1},2026-11-01,Resolved\n" for i, p in enumerate(["Critical", "High", "Medium", "Low"] * 2))
    src = write(tmp_path, H + rows + "T99,High,IT,inf,2026-11-01,Resolved\n")
    out = tmp_path / "o"
    r = subprocess.run([sys.executable, str(SRC / "eda.py"), "--data", str(src), "--out", str(out)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "T99" in (out / "rejected_rows.csv").read_text()
    assert len(list((out / "plots").glob("*.png"))) == 6
