import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import eda  # noqa: E402

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
