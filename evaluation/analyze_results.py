#!/usr/bin/env python3
"""Summarize recorded detector timings and save a chart."""
import csv
import statistics
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence/evaluation/detection_times.csv"
OUT = ROOT / "evaluation"
with SOURCE.open(newline="", encoding="utf-8") as stream:
    rows = list(csv.DictReader(stream))
values = [float(row["detection_seconds"]) for row in rows]
runs = [int(row["run"]) for row in rows]
if not values:
    raise SystemExit("No timing rows found.")
summary = ("Project Shadow Route — Detection Time Evaluation\n\n"
           f"Number of recorded runs: {len(values)}\n"
           f"Mean: {statistics.mean(values):.3f} seconds\n"
           f"Median: {statistics.median(values):.3f} seconds\n"
           f"Sample standard deviation: {statistics.stdev(values):.3f} seconds\n"
           f"Range: {min(values):.3f}–{max(values):.3f} seconds\n\n"
           "Measurement: attack configuration reload to detector observation; includes route propagation and one-second polling.\n"
           "Results are specific to this controlled SEED VM lab and are not a production-network claim.\n")
(OUT / "evaluation_summary.txt").write_text(summary, encoding="utf-8")
fig, ax = plt.subplots(figsize=(8, 4.8))
bars = ax.bar(runs, values, color="#3978ce")
ax.axhline(statistics.mean(values), color="#dc5267", linestyle="--", label=f"Mean {statistics.mean(values):.3f} s")
ax.set(title="BGP Hijack Detector — Detection Time", xlabel="Run", ylabel="Seconds")
ax.set_xticks(runs); ax.grid(axis="y", linestyle=":", alpha=.4); ax.legend()
for bar, val in zip(bars, values):
    ax.text(bar.get_x()+bar.get_width()/2, val, f"{val:.3f}", ha="center", va="bottom", fontsize=8)
fig.tight_layout(); fig.savefig(OUT / "detection_time_graph.png", dpi=170); plt.close(fig)
print(summary)
