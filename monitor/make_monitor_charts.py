import json, pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
C1, C2, C3, C4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, SURF, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False})
d = pd.read_csv("backtest_daily.csv", index_col=0, parse_dates=True); R = json.load(open("backtest_results.json"))
def finish(fig, ax, title, sub, path):
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold", color=INK, pad=26)
    ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=10, color=INK2); fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)
# chart 6: backtest on unseen cycle
t = d["2026-06-20":]
fig, ax = plt.subplots(figsize=(9.5, 5.4))
f = t[["q10_14", "q50_14", "q90_14"]].shift(14)          # plot each 14-day forecast at the date it is FOR
f = f[f.index >= pd.Timestamp("2026-07-29")]             # only forecasts issued after the cleaning (needs 14 days of data)
ax.fill_between(f.index, 100 * f.q10_14, 100 * f.q90_14, color=C1, alpha=0.18, lw=0)
ax.plot(f.index, 100 * f.q50_14, color=C1, lw=1.8)
ax.plot(t.index, 100 * t.phi_true, color=INK, lw=1.6, ls="--")
ax.plot(t.index, 100 * t.phi_hat, color=C2, lw=0, marker="o", ms=2.2)
ax.axhline(40, color=INK2, lw=1, ls=":"); ax.text(t.index[2], 41.5, "Cliff: plan cleaning before 40 %", color=INK2, fontsize=9.5)
ax.axvline(pd.Timestamp("2026-07-01"), color=C3, lw=1.2); ax.text(pd.Timestamp("2026-07-02"), 72, "TAR cleaning", color=C3, fontsize=9.5)
a = pd.Timestamp(R["first_alarm"]); ax.annotate(f"Alarm {a:%d %b}\n{R['alarm_lead_days']} days early", (a, 40), (a + pd.Timedelta(days=4), 52),
    fontsize=9.5, color=C4, arrowprops=dict(arrowstyle="->", color=C4))
ax.text(pd.Timestamp("2026-10-01"), 53, "True blockage (dashed)", color=INK, fontsize=9.5)
ax.text(pd.Timestamp("2026-09-22"), 66, "Measured health\nindicator (daily)", color=C2, fontsize=9.5)
ax.text(pd.Timestamp("2026-08-24"), 30, "14-day forecast\n+ 10-90 % band", color=C1, fontsize=9.5)
ax.set_ylabel("Equivalent fin blockage (%)"); ax.set_ylim(0, 80)
finish(fig, ax, "Backtest: the model warns before the cliff", "Unseen Jul-Nov 2026 cycle. Synthetic plant, " + ("real Atyrau weather." if "PLACEHOLDER" not in R["weather"] else "placeholder weather."), "chart6_backtest.png")
# chart 7: error vs baselines
fig, ax = plt.subplots(figsize=(9, 4.8)); H = [7, 14, 30]; x = np.arange(3); w = 0.26
for i, (k, lab, c) in enumerate([("persistence_MAE_pct", "No change (today = future)", INK2), ("linear_trend_MAE_pct", "Straight-line trend", C4), ("model_MAE_pct", "Our forecaster", C1)]):
    v = [R[f"h{h}"][k] for h in H]; ax.bar(x + (i - 1) * w, v, w, color=c, label=lab)
    for xi, vi in zip(x, v): ax.text(xi + (i - 1) * w, vi + 0.2, f"{vi:.1f}", ha="center", fontsize=9, color=INK)
ax.set_xticks(x); ax.set_xticklabels([f"{h} days ahead" for h in H]); ax.set_ylabel("Average error (% blockage)")
ax.grid(axis="x", visible=False); ax.legend(frameon=False, fontsize=9.5, loc="upper left")
finish(fig, ax, "Forecast error on the unseen cycle", "Lower is better. Same health indicator for all three methods.", "chart7_forecast_error.png")
print("ok")
