"""Day 7 - Exploratory data analysis of the ticket dataset.

Usage:  python src/eda.py [--data data/sample_tickets.csv] [--out outputs]
Outputs: outputs/profile.txt, outputs/stats.json, outputs/plots/*.png
"""
import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: render to files only
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PRIORITY_ORDER = ["Critical", "High", "Medium", "Low"]
REQUIRED = ["ticket_id", "priority", "category", "resolution_time_hours", "created_at", "status"]


def load(path):
    df = pd.read_csv(path, parse_dates=["created_at"])
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    df["priority"] = pd.Categorical(df["priority"], PRIORITY_ORDER, ordered=True)
    return df


def profile(df):
    """Task A: rows, schema, missingness, unique values, basic stats."""
    lines = [f"Rows: {len(df)}   Columns: {df.shape[1]}", "", "Schema / missingness / unique"]
    for c in df.columns:
        n_miss = int(df[c].isna().sum())
        lines.append(f"  {c:<24}{str(df[c].dtype):<14}missing={n_miss} ({n_miss / len(df):.0%})  unique={df[c].nunique()}")
    lines += ["", "Numeric summary (resolution_time_hours):", df["resolution_time_hours"].describe().round(2).to_string()]
    for c in ["priority", "category", "status"]:
        lines += ["", f"Counts: {c}", df[c].value_counts(dropna=False).to_string()]
    lines += ["", f"Duplicate ticket_ids: {int(df['ticket_id'].duplicated().sum())}",
              f"Date range: {df['created_at'].min().date()} to {df['created_at'].max().date()}"]
    return "\n".join(lines)


def iqr_outliers(s):
    s = s.dropna()
    q1, q3 = s.quantile([0.25, 0.75])
    lo, hi = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    return s[(s < lo) | (s > hi)], lo, hi


def compute_stats(df):
    from scipy import stats

    t = df["resolution_time_hours"]
    resolved = df.dropna(subset=["resolution_time_hours"])
    out, lo, hi = iqr_outliers(t)
    rho, p = stats.spearmanr(resolved["priority"].cat.codes, resolved["resolution_time_hours"])
    by_pri = resolved.groupby("priority", observed=True)["resolution_time_hours"].agg(["count", "mean", "median", "min", "max"]).round(2)
    by_cat = resolved.groupby("category")["resolution_time_hours"].agg(["count", "mean", "median"]).round(2)
    miss = df[t.isna()]
    return {
        "n_rows": len(df),
        "n_missing_resolution": int(t.isna().sum()),
        "missing_rows_status": miss["status"].value_counts().to_dict(),
        "missing_rows_priority": miss["priority"].astype(str).value_counts().to_dict(),
        "mean_hours": round(float(t.mean()), 2),
        "median_hours": round(float(t.median()), 2),
        "std_hours": round(float(t.std()), 2),
        "iqr_fences": [round(float(lo), 2), round(float(hi), 2)],
        "iqr_outliers": out.tolist(),
        "spearman_priority_vs_time": {"rho": round(float(rho), 3), "p": round(float(p), 4), "n": len(resolved),
                                      "note": "priority coded Critical=0..Low=3; association only, not causation"},
        "by_priority": by_pri.reset_index().astype({"priority": str}).to_dict("records"),
        "by_category": by_cat.reset_index().to_dict("records"),
        "category_share": df["category"].value_counts(normalize=True).round(3).to_dict(),
        "status_share": df["status"].value_counts(normalize=True).round(3).to_dict(),
    }


def _save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def make_plots(df, plots):
    """Task B: five plots, each with title, axis labels and n shown."""
    sns.set_theme(style="whitegrid")
    n = len(df)
    resolved = df.dropna(subset=["resolution_time_hours"])

    fig, ax = plt.subplots(figsize=(6, 4))
    order = df["category"].value_counts().index
    sns.countplot(data=df, x="category", order=order, color="#4C72B0", ax=ax)
    ax.bar_label(ax.containers[0])
    ax.set(title=f"Tickets per category (n={n})", xlabel="Category", ylabel="Ticket count")
    _save(fig, plots / "01_category_counts.png")

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.countplot(data=df, x="priority", order=PRIORITY_ORDER, color="#55A868", ax=ax)
    ax.bar_label(ax.containers[0])
    ax.set(title=f"Tickets per priority (n={n})", xlabel="Priority", ylabel="Ticket count")
    _save(fig, plots / "02_priority_counts.png")

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.histplot(resolved["resolution_time_hours"], bins=8, kde=False, color="#C44E52", ax=ax)
    ax.axvline(resolved["resolution_time_hours"].median(), color="k", ls="--", label="median")
    ax.axvline(resolved["resolution_time_hours"].mean(), color="gray", ls=":", label="mean")
    ax.legend()
    ax.set(title=f"Resolution time distribution (n={len(resolved)}, {n - len(resolved)} missing excluded)",
           xlabel="Resolution time (hours)", ylabel="Ticket count")
    _save(fig, plots / "03_resolution_hist.png")

    fig, ax = plt.subplots(figsize=(6.5, 4))
    sns.boxplot(data=resolved, x="priority", y="resolution_time_hours", order=PRIORITY_ORDER, color="#8172B2", ax=ax)
    sns.stripplot(data=resolved, x="priority", y="resolution_time_hours", order=PRIORITY_ORDER, color="k", size=4, ax=ax)
    ax.set(title=f"Resolution time by priority (n={len(resolved)}; points = tickets)",
           xlabel="Priority", ylabel="Resolution time (hours)")
    _save(fig, plots / "04_resolution_by_priority_box.png")

    fig, ax = plt.subplots(figsize=(6.5, 4))
    sns.boxplot(data=resolved, x="category", y="resolution_time_hours", color="#CCB974", ax=ax)
    sns.stripplot(data=resolved, x="category", y="resolution_time_hours", color="k", size=4, ax=ax)
    ax.set(title=f"Resolution time by category (n={len(resolved)})", xlabel="Category", ylabel="Resolution time (hours)")
    _save(fig, plots / "05_resolution_by_category_box.png")

    fig, ax = plt.subplots(figsize=(6, 4))
    ct = pd.crosstab(df["priority"], df["category"])
    sns.heatmap(ct, annot=True, fmt="d", cmap="Blues", cbar_kws={"label": "Ticket count"}, ax=ax)
    ax.set(title=f"Priority x category counts (n={n})", xlabel="Category", ylabel="Priority")
    _save(fig, plots / "06_priority_category_heatmap.png")


def main():
    root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(root / "data" / "sample_tickets.csv"))
    ap.add_argument("--out", default=str(root / "outputs"))
    a = ap.parse_args()
    out = Path(a.out)
    plots = out / "plots"
    plots.mkdir(parents=True, exist_ok=True)

    df = load(a.data)
    text = profile(df)
    (out / "profile.txt").write_text(text + "\n")
    stats = compute_stats(df)
    (out / "stats.json").write_text(json.dumps(stats, indent=2, default=str))
    make_plots(df, plots)
    print(text)
    print("\nSTATS\n" + json.dumps(stats, indent=2, default=str))
    print(f"\nSaved {len(list(plots.glob('*.png')))} plots to {plots}")


if __name__ == "__main__":
    main()
