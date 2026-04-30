#!/usr/bin/env python3
"""Visualiseer de resultaten van check_vestigingen.py."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

ROOT = Path(__file__).parent.parent


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["v_ok"] = (df["v_status"] == 200) & (df["v_valid_turtle"] == True)
    df["o_ok"] = (df["o_status"] == 200) & (df["o_valid_turtle"] == True)
    return df


def categorize(df: pd.DataFrame) -> pd.Series:
    conditions = [
        df["v_ok"] & df["o_ok"],
        df["v_ok"] & ~df["o_ok"],
        ~df["v_ok"],
    ]
    labels = [
        "vestiging OK + onderneming OK",
        "vestiging OK, onderneming niet gevonden",
        "vestiging niet gevonden",
    ]
    return pd.cut(
        df.index,
        bins=[-1] + list(df.index),
        labels=False,
    ).where(False, other=pd.Series(
        [labels[0] if c[0] else labels[1] if c[1] else labels[2]
         for c in zip(*[c.tolist() for c in conditions])],
        index=df.index,
    ))


def main(results_path: Path) -> None:
    df = load(results_path)
    total = len(df)

    counts_v = df["v_status"].value_counts().sort_index()
    counts_o = df[df["o_status"].notna()]["o_status"].astype(int).value_counts().sort_index()

    ok = df["v_ok"] & df["o_ok"]
    v_ok_o_nok = df["v_ok"] & ~df["o_ok"]
    v_nok = ~df["v_ok"]
    categories = {
        "vestiging OK\nonderneming OK": ok.sum(),
        "vestiging OK\nonderneming niet gevonden": v_ok_o_nok.sum(),
        "vestiging niet gevonden": v_nok.sum(),
    }

    COLORS = {
        "ok": "#2ecc71",
        "warn": "#f39c12",
        "error": "#e74c3c",
    }

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(f"VKBO LOD — resultaten ({total} vestigingen)", fontsize=13, fontweight="bold")

    # 1. Samenvatting als horizontale gestapelde balk
    ax = axes[0]
    ax.set_title("Samenvatting")
    colors = [COLORS["ok"], COLORS["warn"], COLORS["error"]]
    left = 0
    for (label, count), color in zip(categories.items(), colors):
        pct = count / total * 100
        ax.barh(0, count, left=left, color=color, edgecolor="white", height=0.4)
        if pct > 3:
            ax.text(left + count / 2, 0, f"{count}\n({pct:.1f}%)",
                    ha="center", va="center", fontsize=8, color="white", fontweight="bold")
        left += count
    patches = [mpatches.Patch(color=c, label=l) for l, c in zip(categories.keys(), colors)]
    ax.legend(handles=patches, loc="lower center", bbox_to_anchor=(0.5, -0.25), fontsize=8)
    ax.set_xlim(0, total)
    ax.set_yticks([])
    ax.set_xlabel("aantal vestigingen")

    # 2. HTTP-statuscodes vestigingen
    ax = axes[1]
    ax.set_title("HTTP-statuscodes vestigingen")
    bar_colors = [COLORS["ok"] if s == 200 else COLORS["error"] for s in counts_v.index]
    bars = ax.bar([str(s) for s in counts_v.index], counts_v.values, color=bar_colors, edgecolor="white")
    for bar, val in zip(bars, counts_v.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
                str(val), ha="center", va="bottom", fontsize=9)
    ax.set_xlabel("HTTP-statuscode")
    ax.set_ylabel("aantal")

    # 3. HTTP-statuscodes ondernemingen (alleen waar vestiging OK was)
    ax = axes[2]
    ax.set_title("HTTP-statuscodes ondernemingen\n(enkel waar vestiging OK)")
    df_v_ok = df[df["v_ok"] & df["o_status"].notna()]
    counts_o2 = df_v_ok["o_status"].astype(int).value_counts().sort_index()
    bar_colors2 = [COLORS["ok"] if s == 200 else COLORS["error"] for s in counts_o2.index]
    bars2 = ax.bar([str(s) for s in counts_o2.index], counts_o2.values, color=bar_colors2, edgecolor="white")
    for bar, val in zip(bars2, counts_o2.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                str(val), ha="center", va="bottom", fontsize=9)
    ax.set_xlabel("HTTP-statuscode")
    ax.set_ylabel("aantal")

    plt.tight_layout()
    out = ROOT / "resultaat.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Plot opgeslagen: {out}")


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "resultaat.csv"
    if not path.exists():
        print(f"Bestand niet gevonden: {path}", file=sys.stderr)
        sys.exit(1)
    main(path)
